#!/usr/bin/env python3
"""
LifeOS Personal Assistant MVP
Claude Code 集成版本 - 直接对话式任务规划和执行
Todoist集成版
"""

import json
import subprocess
import urllib.parse
from datetime import datetime, date, timedelta
from pathlib import Path
import re
import sys

class PersonalAssistant:
    def __init__(self, lifeos_path="~/LifeOS"):
        self.lifeos_path = Path(lifeos_path).expanduser()
        self.data_path = self.lifeos_path / "data"
        self.config_path = self.lifeos_path / "config"

        # 确保目录存在
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.config_path.mkdir(parents=True, exist_ok=True)

        # 初始化Todoist管理器
        try:
            sys.path.insert(0, str(self.lifeos_path / "scripts"))
            from todoist_manager import TodoistManager
            self.todoist = TodoistManager()
        except ImportError as e:
            print(f"⚠️  Todoist管理器加载失败: {e}")
            self.todoist = None
        
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
    
    def send_to_todoist(self, tasks):
        """发送任务到Todoist"""
        if not self.todoist or not self.todoist.api:
            print("❌ Todoist未配置，请先运行: python todoist_manager.py setup")
            return "❌ Todoist未配置"

        try:
            # 转换任务格式为Todoist格式
            todoist_tasks = []
            for task in tasks:
                todoist_task = {
                    'name': task['name'],
                    'body': f"预计时间: {task['estimated_time']}分钟\n优先级: {task['priority']}",
                    'project': task['project'].lower() if task['project'] in ['工作', '学习', '生活', '沟通'] else 'other',
                    'priority': task['priority'],
                    'due_days': task.get('due_days', 1),
                    'labels': []
                }

                # 添加标签
                if task['priority'] == 'high':
                    todoist_task['labels'].append('important')

                todoist_tasks.append(todoist_task)

            # 批量创建任务
            results = self.todoist.create_tasks_batch(todoist_tasks)

            if results['success'] > 0:
                return f"✅ 成功创建 {results['success']}/{len(tasks)} 个任务到 Todoist"
            else:
                return f"❌ 任务创建失败"

        except Exception as e:
            return f"❌ 发送失败: {e}"
    
    
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
        print("选项: --stats 查看统计, --auto-send 自动发送")
        return

    # 检查特殊命令
    if '--stats' in sys.argv:
        print(assistant.get_task_stats())
        return

    # 检查是否自动发送
    auto_send = '--auto-send' in sys.argv

    # 移除选项参数
    args = [arg for arg in sys.argv[1:] if not arg.startswith('--')]
    user_input = ' '.join(args)

    print(f"🤖 正在分析: {user_input}")

    # 解析任务
    tasks = assistant.parse_user_input(user_input)

    if not tasks:
        print("❌ 没有识别到具体任务，请描述得更清楚一些")
        return

    # 生成计划
    plan, tasks = assistant.generate_task_plan(tasks)
    print(plan)

    # 用户确认或自动发送
    if auto_send:
        confirm = 'y'
    else:
        confirm = input("要发送到Todoist吗？(y/n): ").strip().lower()

    if confirm in ['y', 'yes', '是', '好']:
        result = assistant.send_to_todoist(tasks)
        print(result)

        # 保存历史
        assistant.save_task_history(tasks, user_input)
        print("📝 已保存到任务历史")
    else:
        print("❌ 已取消")


if __name__ == "__main__":
    main()