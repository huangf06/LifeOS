#!/usr/bin/env python3
"""
LifeOS Logseq生活追踪模块
本地Logseq + Git同步的生活记录系统
"""

import json
import os
from datetime import datetime, date, timedelta
from pathlib import Path
import subprocess
import re
import statistics
from collections import defaultdict

class LogseqTracker:
    def __init__(self, logseq_path="~/Documents/logseq", lifeos_path="~/LifeOS"):
        self.logseq_path = Path(logseq_path).expanduser()
        self.lifeos_path = Path(lifeos_path).expanduser()
        self.pages_path = self.logseq_path / "pages"
        self.journals_path = self.logseq_path / "journals"
        
        # 确保目录存在
        self.pages_path.mkdir(parents=True, exist_ok=True)
        self.journals_path.mkdir(parents=True, exist_ok=True)
        
        # 数据存储路径
        self.data_path = self.lifeos_path / "data"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # 加载模板配置
        self.load_templates()
        
    def get_today_journal_path(self, target_date=None):
        """获取今日journal文件路径"""
        if target_date is None:
            target_date = date.today()
        
        # Logseq journal文件名格式: 2024_01_15.md
        filename = target_date.strftime("%Y_%m_%d.md")
        return self.journals_path / filename
    
    def ensure_daily_template(self, target_date=None):
        """确保今日journal有基础模板"""
        journal_path = self.get_today_journal_path(target_date)
        
        if not journal_path.exists():
            if target_date is None:
                target_date = date.today()
                
            template = self._generate_daily_template(target_date)
            
            with open(journal_path, 'w', encoding='utf-8') as f:
                f.write(template)
            
            print(f"✅ 创建今日记录模板: {journal_path.name}")
        
        return journal_path
    
    def load_templates(self):
        """加载模板配置"""
        templates_path = self.lifeos_path / "config" / "logseq_templates.json"
        if templates_path.exists():
            with open(templates_path, 'r', encoding='utf-8') as f:
                self.templates = json.load(f)
        else:
            self.templates = {}
    
    def _generate_daily_template(self, target_date):
        """生成每日记录模板"""
        weekday_cn = {
            'Monday': '周一', 'Tuesday': '周二', 'Wednesday': '周三', 
            'Thursday': '周四', 'Friday': '周五', 'Saturday': '周六', 'Sunday': '周日'
        }
        
        weekday_en = target_date.strftime("%A")
        weekday = weekday_cn.get(weekday_en, weekday_en)
        date_str = target_date.strftime("%Y-%m-%d")
        
        # 使用配置的模板或默认模板
        if 'daily_journal' in self.templates:
            template_str = self.templates['daily_journal']['template']
            template = template_str.format(date=date_str, weekday=weekday)
        else:
            # 默认模板
            template = f"""- ## 📅 {date_str} {weekday}
- ### 🌅 晨间记录
  - 起床时间: 
  - 今日心情: /10 😊
  - 能量水平: /10 ⚡
  - 天气状况: 
  - 今日主要目标:
    - 
- ### ✅ 任务跟踪
  - 🏢 **工作任务**:
    - TODO 
  - 📚 **学习任务**:
    - TODO 
  - 🏠 **生活任务**:
    - TODO 
  - 💪 **健康任务**:
    - TODO 
- ### 🌙 晚间反思
  - 今日最有成就感: 
  - 遇到的挑战: 
  - 学到的新知识: 
  - 明日需要改进: 
  - 今日评分: /10
- ### 📊 数据记录
  - 睡眠时长: 小时
  - 运动时长: 分钟
  - 学习时长: 小时
  - 工作效率: /10
- ### 🤖 AI洞察
  - *等待分析...*
"""
        return template
    
    def create_project_page(self, project_name):
        """创建项目管理页面"""
        page_name = f"项目：{project_name}"
        page_path = self.pages_path / f"{page_name}.md"
        
        if 'project_template' in self.templates:
            template_str = self.templates['project_template']['template']
            content = template_str.format(project_name=project_name)
        else:
            content = f"""- ## 🎯 项目: {project_name}
- ### 📋 项目信息
  - 开始日期: {date.today()}
  - 预期完成: 
  - 优先级: 
  - 状态: 进行中
- ### 🎯 项目目标
  - 最终目标: 
  - 成功标准: 
- ### ✅ 任务分解
  - TODO 任务1
  - TODO 任务2
- ### 📊 进度追踪
  - 整体进度: 0%
  - 下一步行动: 
"""
        
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 创建项目页面: {page_name}")
        return page_path
    
    def create_weekly_review(self, week_start_date=None):
        """创建周回顾页面"""
        if week_start_date is None:
            week_start_date = date.today() - timedelta(days=date.today().weekday())
        
        week_end_date = week_start_date + timedelta(days=6)
        week_num = week_start_date.isocalendar()[1]
        
        page_name = f"第{week_num}周回顾"
        page_path = self.pages_path / f"{page_name}.md"
        
        if 'weekly_review' in self.templates:
            template_str = self.templates['weekly_review']['template']
            content = template_str.format(
                week_num=week_num,
                week_start=week_start_date.strftime('%m-%d'),
                week_end=week_end_date.strftime('%m-%d')
            )
        else:
            content = f"""- ## 📅 第{week_num}周回顾 ({week_start_date.strftime('%m-%d')} - {week_end_date.strftime('%m-%d')})
- ### ✅ 本周成就
  - 
- ### 🤔 问题与挑战
  - 
- ### 🎯 下周规划
  - 
"""
        
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 创建周回顾: {page_name}")
        return page_path
    
    def create_book_note(self, book_title, author=""):
        """创建读书笔记页面"""
        page_name = f"《{book_title}》"
        page_path = self.pages_path / f"{page_name}.md"
        
        if 'book_review' in self.templates:
            template_str = self.templates['book_review']['template']
            content = template_str.format(
                book_title=book_title,
                date=date.today().strftime('%Y-%m-%d')
            )
            if author:
                content = content.replace("作者: ", f"作者: {author}")
        else:
            content = f"""- ## 📖 读书笔记: {book_title}
- ### 📋 图书信息
  - 作者: {author}
  - 开始阅读: {date.today()}
  - 评分: ⭐⭐⭐⭐⭐
- ### 📝 核心观点
  - 
- ### 💡 金句摘录
  - 
- ### 🤔 个人思考
  - 
"""
        
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 创建读书笔记: {book_title}")
        return page_path
    
    def log_activity(self, category, content, rating=None, duration=None):
        """记录活动到今日journal"""
        journal_path = self.ensure_daily_template()
        
        # 读取现有内容
        with open(journal_path, 'r', encoding='utf-8') as f:
            content_lines = f.readlines()
        
        # 查找对应分类并添加记录
        timestamp = datetime.now().strftime("%H:%M")
        
        if duration:
            log_entry = f"    - {timestamp} {content} ({duration}) "
        else:
            log_entry = f"    - {timestamp} {content} "
            
        if rating:
            log_entry += f"[评分: {rating}/10]"
        
        log_entry += "\n"
        
        # 插入到对应类别下
        category_mapping = {
            'work': '工作任务:',
            'study': '学习任务:', 
            'life': '生活任务:',
            'health': '健康任务:',
            'mood': '心情指数:',
            'energy': '能量水平:',
            'sleep': '睡眠质量:'
        }
        
        target_line = category_mapping.get(category, '工作任务:')
        
        # 找到目标行并在其后插入
        for i, line in enumerate(content_lines):
            if target_line in line:
                content_lines.insert(i + 1, log_entry)
                break
        
        # 写回文件
        with open(journal_path, 'w', encoding='utf-8') as f:
            f.writelines(content_lines)
        
        print(f"✅ 已记录 [{category}]: {content}")
        return True
    
    def quick_log(self, text):
        """快速记录文本到今日journal"""
        journal_path = self.ensure_daily_template()
        timestamp = datetime.now().strftime("%H:%M")
        
        # 添加到文件末尾
        with open(journal_path, 'a', encoding='utf-8') as f:
            f.write(f"- {timestamp} {text}\n")
        
        print(f"✅ 快速记录: {text}")
        return True
    
    def update_daily_data(self, data_type, value):
        """更新今日基础数据"""
        journal_path = self.ensure_daily_template()
        
        # 读取文件内容
        with open(journal_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 数据类型映射
        patterns = {
            'wakeup': r'起床时间: .*',
            'bedtime': r'就寝时间: .*',
            'mood': r'心情指数: .*/10',
            'energy': r'能量水平: .*/10',
            'sleep_quality': r'睡眠质量: .*',
            'weather': r'天气: .*'
        }
        
        replacements = {
            'wakeup': f'起床时间: {value}',
            'bedtime': f'就寝时间: {value}',
            'mood': f'心情指数: {value}/10',
            'energy': f'能量水平: {value}/10',
            'sleep_quality': f'睡眠质量: {value}',
            'weather': f'天气: {value}'
        }
        
        if data_type in patterns:
            pattern = patterns[data_type]
            replacement = replacements[data_type]
            
            new_content = re.sub(pattern, replacement, content)
            
            with open(journal_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 更新 {data_type}: {value}")
            return True
        
        return False
    
    def extract_daily_data(self, target_date=None):
        """提取指定日期的结构化数据"""
        journal_path = self.get_today_journal_path(target_date)
        
        if not journal_path.exists():
            return None
        
        with open(journal_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析结构化数据
        data = {
            'date': target_date or date.today(),
            'wakeup': self._extract_field(content, r'起床时间: (.+)'),
            'bedtime': self._extract_field(content, r'就寝时间: (.+)'),
            'mood': self._extract_rating(content, r'心情指数: (\d+)/10'),
            'energy': self._extract_rating(content, r'能量水平: (\d+)/10'),
            'sleep_quality': self._extract_field(content, r'睡眠质量: (.+)'),
            'weather': self._extract_field(content, r'天气: (.+)'),
            'tasks': self._extract_tasks(content),
            'reflections': self._extract_reflections(content)
        }
        
        return data
    
    def _extract_field(self, content, pattern):
        """从内容中提取字段"""
        match = re.search(pattern, content)
        return match.group(1).strip() if match else None
    
    def _extract_rating(self, content, pattern):
        """提取评分数据"""
        match = re.search(pattern, content)
        return int(match.group(1)) if match else None
    
    def _extract_tasks(self, content):
        """提取任务列表"""
        tasks = {}
        categories = ['工作任务:', '学习任务:', '生活任务:', '健康任务:']
        
        for category in categories:
            tasks[category] = []
            # 查找任务列表
            # 这里可以根据实际格式调整正则表达式
        
        return tasks
    
    def _extract_reflections(self, content):
        """提取反思内容"""
        reflections = {}
        reflection_fields = [
            '最有成就感的事:', '遇到的挑战:', 
            '学到的东西:', '明日改进点:'
        ]
        
        for field in reflection_fields:
            reflections[field] = self._extract_field(content, f'{field} (.+)')
        
        return reflections
    
    def generate_weekly_report(self, weeks_back=0):
        """生成周报"""
        today = date.today()
        start_date = today - timedelta(days=today.weekday() + weeks_back * 7)
        
        weekly_data = []
        for i in range(7):
            day_date = start_date + timedelta(days=i)
            day_data = self.extract_daily_data(day_date)
            if day_data:
                weekly_data.append(day_data)
        
        # 生成报告
        report = self._analyze_weekly_data(weekly_data)
        return report
    
    def _analyze_weekly_data(self, weekly_data):
        """分析周数据"""
        if not weekly_data:
            return "本周暂无数据"
        
        # 计算平均值
        moods = [d['mood'] for d in weekly_data if d['mood']]
        energies = [d['energy'] for d in weekly_data if d['energy']]
        
        avg_mood = sum(moods) / len(moods) if moods else 0
        avg_energy = sum(energies) / len(energies) if energies else 0
        
        report = f"""📊 本周生活分析报告

🎯 核心数据:
- 平均心情: {avg_mood:.1f}/10
- 平均能量: {avg_energy:.1f}/10
- 记录天数: {len(weekly_data)}/7

📈 趋势分析:
- 心情趋势: {'上升' if len(moods) > 1 and moods[-1] > moods[0] else '稳定'}
- 能量趋势: {'上升' if len(energies) > 1 and energies[-1] > energies[0] else '稳定'}

🎯 改进建议:
- [AI分析建议将在这里显示]
"""
        return report
    
    def sync_with_git(self):
        """与Git同步"""
        try:
            os.chdir(self.logseq_path)
            
            # Git add
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Git commit
            commit_msg = f"Auto sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            result = subprocess.run(['git', 'commit', '-m', commit_msg], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # Git push
                subprocess.run(['git', 'push'], check=True)
                print("✅ Git同步成功")
                return True
            else:
                print("ℹ️ 没有新的更改需要提交")
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Git同步失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 同步出错: {e}")
            return False


def main():
    """命令行入口"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='LifeOS Logseq生活追踪')
    parser.add_argument('action', choices=['log', 'data', 'report', 'sync', 'init'])
    parser.add_argument('--category', '-c', help='记录类别')
    parser.add_argument('--content', help='记录内容')
    parser.add_argument('--rating', '-r', type=int, help='评分 1-10')
    parser.add_argument('--duration', '-d', help='持续时间')
    parser.add_argument('--type', help='数据类型')
    parser.add_argument('--value', help='数据值')
    
    args = parser.parse_args()
    
    tracker = LogseqTracker()
    
    if args.action == 'init':
        tracker.ensure_daily_template()
        print("✅ 今日模板已就绪")
    
    elif args.action == 'log':
        if args.category and args.content:
            tracker.log_activity(args.category, args.content, args.rating, args.duration)
        else:
            print("❌ 需要指定类别和内容")
    
    elif args.action == 'data':
        if args.type and args.value:
            tracker.update_daily_data(args.type, args.value)
        else:
            print("❌ 需要指定数据类型和值")
    
    elif args.action == 'report':
        report = tracker.generate_weekly_report()
        print(report)
    
    elif args.action == 'sync':
        tracker.sync_with_git()


if __name__ == "__main__":
    main()