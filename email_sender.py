#!/usr/bin/env python3
"""
LifeOS 邮件发送工具
支持多种邮件服务，自动发送任务到OmniFocus
"""

import json
import subprocess
import smtplib
import email.mime.text as mime_text
import email.mime.multipart as mime_multipart
from datetime import datetime
from pathlib import Path
import argparse
import getpass
import sys

class EmailSender:
    def __init__(self, config_path="~/LifeOS/config/email_config.json"):
        self.config_path = Path(config_path).expanduser()
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self.load_config()
        
    def load_config(self):
        """加载邮件配置"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    
    def save_config(self, config):
        """保存邮件配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        self.config = config
    
    def setup_email_account(self):
        """首次设置邮件账户"""
        print("🔧 邮件账户设置")
        print("支持的邮件服务商：")
        print("1. Gmail")
        print("2. 163邮箱")
        print("3. QQ邮箱")
        print("4. 自定义SMTP")
        
        choice = input("选择邮件服务商 (1-4): ").strip()
        
        smtp_configs = {
            "1": {"host": "smtp.gmail.com", "port": 587, "name": "Gmail"},
            "2": {"host": "smtp.163.com", "port": 25, "name": "163邮箱"}, 
            "3": {"host": "smtp.qq.com", "port": 587, "name": "QQ邮箱"},
        }
        
        if choice in smtp_configs:
            config = smtp_configs[choice]
            email = input(f"输入你的{config['name']}邮箱: ")
            password = getpass.getpass(f"输入邮箱密码或应用专用密码: ")
            
        elif choice == "4":
            config = {}
            config["host"] = input("SMTP服务器地址: ")
            config["port"] = int(input("SMTP端口 (通常587或25): "))
            config["name"] = "自定义"
            email = input("输入邮箱地址: ")
            password = getpass.getpass("输入密码: ")
        else:
            print("❌ 无效选择")
            return False
        
        # OmniFocus邮件地址
        omnifocus_email = input("输入你的OmniFocus邮件地址: ") or "huangf06.d96py@sync.omnigroup.com"
        
        email_config = {
            "smtp_host": config["host"],
            "smtp_port": config["port"],
            "service_name": config["name"],
            "sender_email": email,
            "sender_password": password,
            "omnifocus_email": omnifocus_email,
            "setup_date": datetime.now().isoformat()
        }
        
        # 测试连接
        if self.test_connection(email_config):
            self.save_config(email_config)
            print("✅ 邮件配置保存成功！")
            return True
        else:
            print("❌ 连接测试失败，请检查配置")
            return False
    
    def test_connection(self, config):
        """测试邮件连接"""
        try:
            print("🔌 测试邮件连接...")
            
            server = smtplib.SMTP(config["smtp_host"], config["smtp_port"])
            server.starttls()
            server.login(config["sender_email"], config["sender_password"])
            server.quit()
            
            print("✅ 连接成功！")
            return True
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def send_single_email(self, subject, body, to_email=None):
        """发送单封邮件"""
        if not self.config:
            print("❌ 未配置邮件账户，请先运行: python email_sender.py setup")
            return False
        
        to_email = to_email or self.config.get("omnifocus_email")
        
        try:
            # 创建邮件
            msg = mime_multipart.MIMEMultipart()
            msg['From'] = self.config["sender_email"]
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(mime_text.MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            server = smtplib.SMTP(self.config["smtp_host"], self.config["smtp_port"])
            server.starttls()
            server.login(self.config["sender_email"], self.config["sender_password"])
            
            text = msg.as_string()
            server.sendmail(self.config["sender_email"], to_email, text.encode('utf-8'))
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"❌ 发送失败: {e}")
            return False
    
    def send_task_list(self, tasks, batch_mode=True):
        """发送任务列表到OmniFocus"""
        if not self.config:
            print("❌ 未配置邮件账户，请先运行设置")
            return False
        
        if batch_mode:
            # 批量模式：一封邮件包含所有任务
            subject = f"LifeOS任务计划 - {datetime.now().strftime('%Y-%m-%d')}"
            body = "今日任务计划：\n\n"
            
            for i, task in enumerate(tasks, 1):
                if isinstance(task, dict):
                    body += f"- {task.get('name', task.get('subject', ''))}\n"
                    if task.get('body') or task.get('note'):
                        body += f"  备注: {task.get('body', task.get('note', ''))}\n"
                else:
                    body += f"- {task}\n"
                body += "\n"
            
            body += f"\n总计 {len(tasks)} 项任务\n"
            body += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            if self.send_single_email(subject, body):
                print(f"✅ 成功发送 {len(tasks)} 个任务到 OmniFocus")
                return True
            else:
                return False
        
        else:
            # 单独模式：每个任务一封邮件
            success_count = 0
            total_count = len(tasks)
            
            print(f"📧 开始发送 {total_count} 封邮件...")
            
            for i, task in enumerate(tasks, 1):
                if isinstance(task, dict):
                    subject = task.get('name', task.get('subject', f'任务 {i}'))
                    body = task.get('body', task.get('note', ''))
                else:
                    subject = task
                    body = f"任务详情：{task}"
                
                print(f"发送 {i}/{total_count}: {subject[:30]}...")
                
                if self.send_single_email(subject, body):
                    success_count += 1
                else:
                    print(f"❌ 任务 {i} 发送失败")
            
            print(f"✅ 成功发送 {success_count}/{total_count} 个任务")
            return success_count == total_count
    
    def send_fitness_plan(self):
        """发送今天的健身计划"""
        fitness_tasks = [
            {
                "name": "动态热身：关节活动",
                "body": "手腕、肩膀、腰部、膝盖各方向转动热身，准备身体进入运动状态。预计3分钟。"
            },
            {
                "name": "轻松跑步热身 7分钟",
                "body": "楼下健身房跑步机或户外慢跑，心率控制在120-130bpm，为力量训练做准备。"
            },
            {
                "name": "🔥俯卧撑测试 3组×8-12个",
                "body": "重要任务！测试现有水平，动作标准比数量重要。记录每组完成个数，为后续训练制定基准。"
            },
            {
                "name": "哑铃推举 3组×8-10个",
                "body": "从5-10kg轻重量开始，感受肌肉发力。组间休息60-90秒，注意呼吸节奏。"
            },
            {
                "name": "哑铃划船 3组×8-10个",
                "body": "背部训练，注意挺胸收肩胛骨，拉起时想象挤压背部肌肉。重量同样从轻开始。"
            },
            {
                "name": "🔥引体向上水平测试",
                "body": "重要任务！2组，能做几个做几个，记录准确数据。这是衡量上肢力量的重要指标。"
            },
            {
                "name": "上肢拉伸放松 10分钟",
                "body": "胸部、肩部、手臂各部位充分拉伸，预防肌肉僵硬，促进恢复。"
            },
            {
                "name": "记录今日训练数据",
                "body": "记录俯卧撑和引体向上的准确数字，以及训练感受，为明天的下肢训练做参考。"
            }
        ]
        
        print("🏋️ 发送健身计划到 OmniFocus...")
        
        # 创建主任务邮件
        subject = "健身计划第一天"
        body = "今日健身训练流程（按顺序执行）：\n\n"
        
        for i, task in enumerate(fitness_tasks, 1):
            body += f"{i}. {task['name']}\n"
            body += f"   说明：{task['body']}\n\n"
        
        body += "总训练时间：约60分钟\n"
        body += "重要提醒：严格按照1-8的顺序执行，注意安全！"
        
        if self.send_single_email(subject, body):
            print(f"✅ 成功发送健身主任务到 OmniFocus")
            return True
        else:
            print("❌ 健身计划发送失败")
            return False


def main():
    parser = argparse.ArgumentParser(description='LifeOS 邮件发送工具')
    parser.add_argument('action', nargs='?', choices=['setup', 'test', 'fitness', 'send'], 
                       default='help', help='执行的操作')
    parser.add_argument('--subject', help='邮件主题')
    parser.add_argument('--body', help='邮件内容')
    parser.add_argument('--tasks', nargs='+', help='任务列表')
    parser.add_argument('--batch', action='store_true', help='批量模式发送')
    
    args = parser.parse_args()
    
    sender = EmailSender()
    
    if args.action == 'setup':
        sender.setup_email_account()
    
    elif args.action == 'test':
        if sender.config:
            result = sender.send_single_email("LifeOS测试邮件", "这是一封测试邮件，验证邮件发送功能正常。")
            if result:
                print("✅ 测试邮件发送成功！")
            else:
                print("❌ 测试邮件发送失败")
        else:
            print("❌ 请先运行 setup 配置邮件账户")
    
    elif args.action == 'fitness':
        sender.send_fitness_plan()
    
    elif args.action == 'send':
        if args.subject and args.body:
            result = sender.send_single_email(args.subject, args.body)
            print("✅ 发送成功" if result else "❌ 发送失败")
        elif args.tasks:
            sender.send_task_list(args.tasks, batch_mode=args.batch)
        else:
            print("❌ 请提供邮件主题和内容，或任务列表")
    
    else:
        print("🤖 LifeOS 邮件发送工具")
        print("")
        print("用法:")
        print("  python email_sender.py setup     # 首次设置邮件账户")
        print("  python email_sender.py test      # 测试邮件发送")
        print("  python email_sender.py fitness   # 发送健身计划")
        print("  python email_sender.py send --subject '任务' --body '内容'")
        print("  python email_sender.py send --tasks '任务1' '任务2' --batch")


if __name__ == "__main__":
    main()