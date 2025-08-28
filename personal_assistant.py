#!/usr/bin/env python3
"""
LifeOS Personal Assistant MVP
Claude Code 集成版本 - 直接对话式任务规划和执行
"""

import json
import subprocess
import urllib.parse
from datetime import datetime, date, timedelta
from pathlib import Path
import re

class PersonalAssistant:
    def __init__(self, lifeos_path="~/LifeOS"):
        self.lifeos_path = Path(lifeos_path).expanduser()
        self.data_path = self.lifeos_path / "data"
        self.config_path = self.lifeos_path / "config"
        
        # 确保目录存在
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        # 加载邮件模板
        self.email_templates = self.load_email_templates()
        
    def load_email_templates(self):
        """加载邮件模板配置"""
        template_file = self.config_path / "email_templates.json"
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认模板
            return {
                "templates": {
                    "default": {
                        "subject": {
                            "single_task": "{task_name}",
                            "multiple_tasks_same_project": "{project}任务 ({task_count}项)",
                            "multiple_tasks_mixed": "今日计划 ({task_count}项任务)"
                        },
                        "body": {
                            "header": "任务清单：\n\n",
                            "high_priority_section": "🔥 高优先级任务：\n",
                            "medium_priority_section": "📋 常规任务：\n",
                            "task_format": "{number}. {name}\n   项目：{project} | 预计：{time}分钟\n\n",
                            "footer": "总预计时间：{total_hours}小时{total_minutes}分钟\n生成时间：{timestamp}"
                        }
                    }
                },
                "default_template": "default"
            }
        
    def parse_user_input(self, user_input):
        """
        解析用户的自然语言输入，提取任务意图
        这里是简化版，实际使用时你直接和Claude对话更准确
        """
        tasks = []
        
        # 简单的关键词识别（实际使用中Claude会更智能地理解）
        task_indicators = [
            "要做", "需要", "完成", "准备", "处理", "写", "开会", "联系", 
            "买", "约", "学习", "复习", "整理", "安排"
        ]
        
        # 时间关键词
        time_patterns = {
            "今天": 0,
            "明天": 1,
            "后天": 2,
            "这周": 7,
            "下周": 14
        }
        
        # 分句处理
        sentences = re.split(r'[，。；,;]', user_input)
        
        for sentence in sentences:
            if any(indicator in sentence for indicator in task_indicators):
                # 提取任务
                task = {
                    'name': sentence.strip(),
                    'priority': self._extract_priority(sentence),
                    'due_days': self._extract_timeline(sentence, time_patterns),
                    'project': self._extract_project(sentence),
                    'estimated_time': self._extract_duration(sentence)
                }
                tasks.append(task)
        
        return tasks
    
    def _extract_priority(self, text):
        """提取优先级"""
        high_priority_words = ["重要", "紧急", "急", "马上", "立即", "必须"]
        if any(word in text for word in high_priority_words):
            return "high"
        return "medium"
    
    def _extract_timeline(self, text, time_patterns):
        """提取时间线"""
        for time_word, days in time_patterns.items():
            if time_word in text:
                return days
        return 1  # 默认明天
    
    def _extract_project(self, text):
        """提取项目分类"""
        project_keywords = {
            "工作": ["项目", "会议", "报告", "代码", "开发", "测试"],
            "学习": ["学习", "复习", "阅读", "研究", "课程"],
            "生活": ["买", "购", "医院", "体检", "健身", "运动"],
            "沟通": ["联系", "电话", "邮件", "微信", "约"]
        }
        
        for project, keywords in project_keywords.items():
            if any(keyword in text for keyword in keywords):
                return project
        
        return "其他"
    
    def _extract_duration(self, text):
        """提取预估时间"""
        # 查找数字+时间单位
        time_match = re.search(r'(\d+)\s*(小时|分钟|h|min)', text)
        if time_match:
            value = int(time_match.group(1))
            unit = time_match.group(2)
            if unit in ['小时', 'h']:
                return value * 60
            else:  # 分钟
                return value
        
        # 根据任务复杂度估算
        if any(word in text for word in ["完成", "写", "准备"]):
            return 60  # 1小时
        elif any(word in text for word in ["联系", "约", "买"]):
            return 20  # 20分钟
        else:
            return 30  # 默认30分钟
    
    def generate_task_plan(self, tasks):
        """生成结构化的任务计划"""
        if not tasks:
            return "没有识别到具体任务。"
        
        # 按优先级和时间排序
        high_priority = [t for t in tasks if t['priority'] == 'high']
        medium_priority = [t for t in tasks if t['priority'] == 'medium']
        
        plan = f"📋 为你生成了 {len(tasks)} 项任务:\n\n"
        
        if high_priority:
            plan += "🔥 高优先级任务:\n"
            for i, task in enumerate(high_priority, 1):
                due_date = (date.today() + timedelta(days=task['due_days'])).strftime('%m-%d')
                plan += f"  {i}. {task['name']} [{task['project']}]\n"
                plan += f"     ⏰ {due_date} | ⏱️ {task['estimated_time']}min\n\n"
        
        if medium_priority:
            plan += "📋 常规任务:\n"
            for i, task in enumerate(medium_priority, 1):
                due_date = (date.today() + timedelta(days=task['due_days'])).strftime('%m-%d')
                plan += f"  {i}. {task['name']} [{task['project']}]\n"
                plan += f"     ⏰ {due_date} | ⏱️ {task['estimated_time']}min\n\n"
        
        total_time = sum(task['estimated_time'] for task in tasks)
        plan += f"⏱️ 预计总时间: {total_time//60}h {total_time%60}min\n"
        
        return plan, tasks
    
    def send_to_omnifocus(self, tasks, method="email", create_subtasks=False, template="default"):
        """发送任务到OmniFocus"""
        if method == "applescript":
            return self._send_via_applescript(tasks)
        elif method == "url":
            return self._send_via_url_scheme(tasks)
        elif method == "email":
            return self._send_via_email(tasks, create_subtasks=create_subtasks, template=template)
        else:
            return self._generate_email_format(tasks)
    
    def _send_via_applescript(self, tasks):
        """通过AppleScript发送任务"""
        script_lines = ['tell application "OmniFocus 3"']
        
        for task in tasks:
            due_date = (date.today() + timedelta(days=task['due_days'])).strftime('%Y-%m-%d')
            
            # 清理任务名称中的特殊字符
            clean_name = task['name'].replace('"', '\\"')
            note = f"AI生成任务\\n预计时间: {task['estimated_time']}分钟\\n优先级: {task['priority']}"
            
            script_lines.extend([
                f'\tset newTask to make new inbox task with properties {{name:"{clean_name}", note:"{note}"}}',
                f'\ttry',
                f'\t\tset containing project of newTask to (first project whose name is "{task["project"]}")',
                f'\ton error',
                f'\t\t-- 如果项目不存在，保持在Inbox',
                f'\tend try',
                f'\tset due date of newTask to date "{due_date}"'
            ])
            
            if task['priority'] == 'high':
                script_lines.append('\tset flagged of newTask to true')
        
        script_lines.extend([
            'end tell',
            f'display notification "已创建 {len(tasks)} 个任务" with title "LifeOS Assistant" sound name "Glass"'
        ])
        
        script = '\n'.join(script_lines)
        
        try:
            result = subprocess.run(
                ['osascript', '-e', script], 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return f"✅ 成功创建 {len(tasks)} 个任务到 OmniFocus"
            else:
                return f"❌ 创建失败: {result.stderr}"
        
        except Exception as e:
            return f"❌ 执行失败: {e}"
    
    def _send_via_email(self, tasks, create_subtasks=False, template="default"):
        """通过邮件发送任务"""
        try:
            # 导入邮件发送模块
            from email_sender import EmailSender
            
            sender = EmailSender()
            
            if create_subtasks and len(tasks) > 1:
                return self._send_project_with_subtasks(sender, tasks)
            else:
                return self._send_simple_task_list(sender, tasks, template)
            
        except ImportError:
            return "❌ 邮件模块未找到，请检查 email_sender.py"
        except Exception as e:
            return f"❌ 邮件发送出错: {e}"
    
    def _send_project_with_subtasks(self, sender, tasks):
        """发送带子任务的项目（多封邮件方式）"""
        from datetime import datetime
        
        # 获取主要项目分类
        main_project = max(set([t['project'] for t in tasks]), key=[t['project'] for t in tasks].count)
        
        # 创建主任务
        main_subject = f"🎯 {main_project}项目"
        main_body = f"这是一个包含 {len(tasks)} 个子任务的项目：\n\n"
        
        for i, task in enumerate(tasks, 1):
            main_body += f"  {i}. {task['name']}\n"
            main_body += f"     ⏰ 预计 {task['estimated_time']} 分钟\n\n"
        
        total_time = sum(task['estimated_time'] for task in tasks)
        main_body += f"总计用时：{total_time//60}小时{total_time%60}分钟\n"
        main_body += f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        main_body += "📋 各子任务将单独发送，请在OmniFocus中将它们移到此项目下"
        
        # 发送主任务
        if not sender.send_single_email(main_subject, main_body):
            return "❌ 主任务发送失败"
        
        # 发送子任务
        success_count = 1  # 主任务已成功
        for i, task in enumerate(tasks, 1):
            sub_subject = f"├─ {task['name']}"
            sub_body = f"【{main_project}项目 - 子任务 {i}】\n\n"
            sub_body += f"项目：{task['project']}\n"
            sub_body += f"预计时间：{task['estimated_time']}分钟\n"
            sub_body += f"优先级：{task['priority']}\n\n"
            sub_body += f"请将此任务移动到「{main_subject}」项目下"
            
            if sender.send_single_email(sub_subject, sub_body):
                success_count += 1
        
        return f"✅ 成功发送项目和 {success_count-1}/{len(tasks)} 个子任务到 OmniFocus"
    
    def _send_simple_task_list(self, sender, tasks, template_name=None):
        """发送简单任务列表（使用模板）"""
        from datetime import datetime
        
        # 获取模板
        template_name = template_name or self.email_templates.get("default_template", "default")
        template = self.email_templates["templates"][template_name]
        
        # 生成标题
        subject = self._generate_subject(tasks, template["subject"])
        
        # 生成邮件正文
        body = self._generate_body(tasks, template["body"])
        
        # 发送邮件
        if sender.send_single_email(subject, body):
            return f"✅ 成功发送任务计划到 OmniFocus（包含 {len(tasks)} 项任务）"
        else:
            return f"❌ 邮件发送失败，请检查邮件配置"
    
    def _generate_subject(self, tasks, subject_template):
        """生成邮件标题"""
        if len(tasks) == 1:
            return subject_template["single_task"].format(task_name=tasks[0]['name'])
        else:
            projects = list(set([t['project'] for t in tasks]))
            if len(projects) == 1:
                return subject_template["multiple_tasks_same_project"].format(
                    project=projects[0], task_count=len(tasks)
                )
            else:
                return subject_template["multiple_tasks_mixed"].format(task_count=len(tasks))
    
    def _generate_body(self, tasks, body_template):
        """生成邮件正文"""
        from datetime import datetime
        
        # 开始构建邮件正文
        body = body_template["header"]
        
        # 按优先级分组
        high_tasks = [t for t in tasks if t['priority'] == 'high']
        medium_tasks = [t for t in tasks if t['priority'] == 'medium']
        
        task_number = 1
        
        # 高优先级任务
        if high_tasks:
            body += body_template["high_priority_section"]
            for task in high_tasks:
                body += body_template["task_format"].format(
                    number=task_number,
                    name=task['name'],
                    project=task['project'],
                    time=task['estimated_time'],
                    priority=task['priority']
                )
                task_number += 1
        
        # 中等优先级任务
        if medium_tasks:
            body += body_template["medium_priority_section"]
            for task in medium_tasks:
                body += body_template["task_format"].format(
                    number=task_number,
                    name=task['name'],
                    project=task['project'],
                    time=task['estimated_time'],
                    priority=task['priority']
                )
                task_number += 1
        
        # 添加底部信息
        total_time = sum(task['estimated_time'] for task in tasks)
        suggested_time = datetime.now().replace(hour=datetime.now().hour + total_time//60).strftime('%H:%M')
        
        body += body_template["footer"].format(
            total_hours=total_time//60,
            total_minutes=total_time%60,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M'),
            date=datetime.now().strftime('%m-%d'),
            suggested_time=suggested_time
        )
        
        return body

    def _send_via_url_scheme(self, tasks):
        """生成URL Scheme链接"""
        urls = []
        for task in tasks:
            name = urllib.parse.quote(task['name'])
            project = urllib.parse.quote(task['project'])
            note = urllib.parse.quote(f"预计时间: {task['estimated_time']}分钟")
            
            url = f"omnifocus:///add?name={name}&project={project}&note={note}"
            urls.append(f"open '{url}'")
        
        commands = '\n'.join(urls)
        return f"🔗 执行以下命令创建任务:\n\n{commands}"
    
    def save_task_history(self, tasks, user_input):
        """保存任务历史"""
        history = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'generated_tasks': tasks,
            'total_tasks': len(tasks)
        }
        
        history_file = self.data_path / "task_history.jsonl"
        with open(history_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(history, ensure_ascii=False) + '\n')
    
    def get_task_stats(self):
        """获取任务统计"""
        history_file = self.data_path / "task_history.jsonl"
        if not history_file.exists():
            return "还没有任务历史记录"
        
        total_sessions = 0
        total_tasks = 0
        
        with open(history_file, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                total_sessions += 1
                total_tasks += record.get('total_tasks', 0)
        
        return f"📊 已处理 {total_sessions} 次对话，生成 {total_tasks} 个任务"


def main():
    """命令行入口"""
    import sys
    
    assistant = PersonalAssistant()
    
    if len(sys.argv) < 2:
        print("用法: python personal_assistant.py '你的任务描述'")
        print("示例: python personal_assistant.py '明天要开会讨论新项目，需要提前准备资料'")
        return
    
    user_input = ' '.join(sys.argv[1:])
    
    print(f"🤖 正在分析: {user_input}")
    
    # 解析任务
    tasks = assistant.parse_user_input(user_input)
    
    if not tasks:
        print("❌ 没有识别到具体任务，请描述得更清楚一些")
        return
    
    # 生成计划
    plan, tasks = assistant.generate_task_plan(tasks)
    print(plan)
    
    # 用户确认
    confirm = input("要发送到OmniFocus吗？(y/n): ").strip().lower()
    
    if confirm in ['y', 'yes', '是', '好']:
        result = assistant.send_to_omnifocus(tasks)
        print(result)
        
        # 保存历史
        assistant.save_task_history(tasks, user_input)
        print("📝 已保存到任务历史")
    else:
        print("❌ 已取消")


if __name__ == "__main__":
    main()