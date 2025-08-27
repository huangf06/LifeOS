#!/usr/bin/env python3
"""
LifeOS 自动同步引擎
OmniFocus ↔ Logseq 双向同步
"""

import json
import subprocess
import re
from datetime import datetime, date, timedelta
from pathlib import Path
import uuid
import sys
import argparse

class LifeOSSync:
    def __init__(self, logseq_graph_path="~/logseq", lifeos_path="~/LifeOS"):
        self.logseq_path = Path(logseq_graph_path).expanduser()
        self.lifeos_path = Path(lifeos_path).expanduser()
        self.journals_path = self.logseq_path / "journals"
        self.data_path = self.lifeos_path / "data"
        self.scripts_path = self.lifeos_path / "scripts"
        
        # 确保目录存在
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.journals_path.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Logseq路径: {self.logseq_path}")
        print(f"📁 数据路径: {self.data_path}")
    
    def morning_sync(self):
        """晨间同步：OmniFocus → Logseq"""
        print("🌅 开始晨间同步...")
        
        try:
            # 1. 从 OmniFocus 导出任务
            tasks = self.export_omnifocus_tasks()
            print(f"📱 从 OmniFocus 导出了 {len(tasks)} 个任务")
            
            # 2. 生成 Logseq 日志内容
            today = date.today()
            journal_content = self.generate_logseq_journal(tasks, today)
            
            # 3. 更新 Logseq 日志页面
            self.update_logseq_journal(journal_content, today)
            
            # 4. 保存同步记录
            self.save_sync_record("morning", len(tasks))
            
            print("✅ 晨间同步完成！")
            self.send_notification("晨间同步完成", f"已导入 {len(tasks)} 个任务")
            
        except Exception as e:
            print(f"❌ 晨间同步失败: {e}")
            self.send_notification("同步失败", str(e))
    
    def export_omnifocus_tasks(self):
        """从 OmniFocus 导出任务"""
        script_path = self.scripts_path / "omnifocus_export.scpt"
        
        if not script_path.exists():
            raise FileNotFoundError(f"OmniFocus导出脚本不存在: {script_path}")
        
        # 运行 AppleScript
        result = subprocess.run(
            ['osascript', str(script_path)], 
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise Exception(f"OmniFocus导出失败: {result.stderr}")
        
        # 读取导出的JSON文件
        export_file = self.data_path / "omnifocus_export.json"
        
        if not export_file.exists():
            raise FileNotFoundError("OmniFocus导出文件不存在")
        
        with open(export_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        return tasks
    
    def generate_logseq_journal(self, tasks, target_date):
        """生成 Logseq 日志内容"""
        weekday_name = target_date.strftime('%A')
        date_str = target_date.strftime('%Y-%m-%d')
        
        # 按优先级排序任务
        high_priority_tasks = [t for t in tasks if t.get('flagged', False)]
        regular_tasks = [t for t in tasks if not t.get('flagged', False)]
        
        # 生成任务列表
        task_list = ""
        
        if high_priority_tasks:
            task_list += "\n### 🔥 高优先级任务\n"
            for task in high_priority_tasks:
                task_list += self.format_task_for_logseq(task) + "\n"
        
        if regular_tasks:
            task_list += "\n### 📋 常规任务\n" 
            for task in regular_tasks:
                task_list += self.format_task_for_logseq(task) + "\n"
        
        # 生成时间规划表格
        time_blocks = self.generate_time_blocks(tasks)
        
        template = f"""# {date_str} | {weekday_name} | %energy: /10

## 🎯 今日意图
*我今天要成为什么样的人，做什么最重要的事？*



## 📋 任务列表 (从OmniFocus同步 - {len(tasks)}项)
{task_list}

## ⏰ 时间规划
{time_blocks}

---

## 📝 执行记录

### {datetime.now().strftime('%H:%M')} - 开始工作
@focus: /10 @energy: /10
> 关键想法：


---

## 🧠 学习捕获
**学到什么新东西：**

**练习了什么技能：**

**有什么认知更新：**

---

## 🌙 晚间反思 (%satisfaction: /10)

### 今日成就
✅ 
✅ 
✅ 

### 主要挑战
❗ 

### 明日重点
🎯 
🎯 
🎯 

### 最有价值的收获
> 

---

## 📊 任务同步状态
%morning_sync: {datetime.now().strftime('%H:%M')}
%evening_sync: pending
%total_tasks: {len(tasks)}
%completed_tasks: 0

---
%writing_time: min | %word_count: words
"""
        return template
    
    def format_task_for_logseq(self, task):
        """格式化单个任务为 Logseq 格式"""
        # 基础信息
        name = task.get('name', 'Untitled')
        project = task.get('project', 'Inbox')
        context = task.get('context', '')
        estimated = task.get('estimatedMinutes', 0)
        
        # 构建标记
        project_tag = f"`[{project}]`" if project != 'Inbox' else ""
        context_tag = f"@{context}" if context else ""
        time_tag = f"⏱️{estimated}min" if estimated > 0 else ""
        
        # 优先级图标
        priority_icon = "🔥 " if task.get('flagged', False) else ""
        
        # 任务ID（用于同步）
        task_id = task.get('id', str(uuid.uuid4())[:8])
        
        # 组合格式
        parts = [priority_icon + name, project_tag, context_tag, time_tag, f"&of:{task_id}"]
        formatted_parts = [part for part in parts if part]
        
        return f"- [ ] {' '.join(formatted_parts)}"
    
    def generate_time_blocks(self, tasks):
        """生成时间块分配表格"""
        total_estimated = sum(task.get('estimatedMinutes', 30) for task in tasks)
        high_priority_tasks = [t for t in tasks if t.get('flagged', False)]
        
        if total_estimated == 0:
            return """| 时间 | 任务 | 预计时间 |
|------|------|----------|
| 09:00-12:00 | 深度工作 | 3h |
| 13:30-15:30 | 常规任务 | 2h |
| 16:00-17:30 | 沟通协调 | 1.5h |"""
        
        time_blocks = "| 时间 | 任务 | 预计时间 |\n|------|------|----------|\n"
        
        # 为高优先级任务安排上午时间
        morning_start = 9
        for i, task in enumerate(high_priority_tasks[:3]):  # 最多3个高优先级任务
            duration = task.get('estimatedMinutes', 60)
            hours = duration // 60
            minutes = duration % 60
            time_str = f"{hours}h{minutes}min" if minutes > 0 else f"{hours}h"
            
            start_time = morning_start + i * 2
            end_time = start_time + max(1, duration // 60)
            
            time_blocks += f"| {start_time:02d}:00-{end_time:02d}:00 | {task['name'][:20]}... | {time_str} |\n"
        
        # 下午时间块
        time_blocks += "| 13:30-15:30 | 其他重要任务 | 2h |\n"
        time_blocks += "| 16:00-17:30 | 沟通协调 | 1.5h |\n"
        
        return time_blocks
    
    def update_logseq_journal(self, content, target_date):
        """更新 Logseq 日志页面"""
        journal_file = self.journals_path / f"{target_date.strftime('%Y_%m_%d')}.md"
        
        if journal_file.exists():
            # 如果文件已存在，只更新任务部分
            existing_content = journal_file.read_text(encoding='utf-8')
            
            # 查找任务列表部分并替换
            pattern = r'(## 📋 任务列表.*?)(## ⏰ 时间规划)'
            new_task_section = re.search(r'(## 📋 任务列表.*?)(## ⏰ 时间规划)', content, re.DOTALL)
            
            if new_task_section and re.search(pattern, existing_content, re.DOTALL):
                updated_content = re.sub(
                    pattern, 
                    new_task_section.group(0), 
                    existing_content, 
                    flags=re.DOTALL
                )
                journal_file.write_text(updated_content, encoding='utf-8')
                print(f"📝 已更新现有日志: {journal_file}")
            else:
                # 如果找不到模式，直接覆盖
                journal_file.write_text(content, encoding='utf-8')
                print(f"📝 已覆盖日志文件: {journal_file}")
        else:
            # 创建新文件
            journal_file.write_text(content, encoding='utf-8')
            print(f"📝 已创建新日志: {journal_file}")
    
    def evening_sync(self):
        """晚间同步：Logseq → OmniFocus"""
        print("🌙 开始晚间同步...")
        
        try:
            # 1. 从 Logseq 提取任务状态更新
            today = date.today()
            task_updates = self.extract_task_updates_from_logseq(today)
            
            if not task_updates:
                print("📝 没有找到任务状态更新")
                return
            
            print(f"📝 提取了 {len(task_updates)} 个任务状态更新")
            
            # 2. 同步状态到 OmniFocus
            success_count = 0
            for task_id, status, notes in task_updates:
                if self.update_omnifocus_task(task_id, status, notes):
                    success_count += 1
            
            print(f"✅ 成功同步 {success_count}/{len(task_updates)} 个任务")
            
            # 3. 保存同步记录
            self.save_sync_record("evening", success_count)
            
            self.send_notification("晚间同步完成", f"已同步 {success_count} 个任务状态")
            
        except Exception as e:
            print(f"❌ 晚间同步失败: {e}")
            self.send_notification("同步失败", str(e))
    
    def extract_task_updates_from_logseq(self, target_date):
        """从 Logseq 日志中提取任务状态更新"""
        journal_file = self.journals_path / f"{target_date.strftime('%Y_%m_%d')}.md"
        
        if not journal_file.exists():
            print(f"❌ 日志文件不存在: {journal_file}")
            return []
        
        content = journal_file.read_text(encoding='utf-8')
        updates = []
        
        # 匹配不同状态的任务
        patterns = {
            'completed': r'- \[x\] .+?&of:(\w+).*',
            'cancelled': r'- \[-\] .+?&of:(\w+).*',
            'deferred': r'- \[>\] .+?&of:(\w+).*'
        }
        
        for status, pattern in patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE)
            for task_id in matches:
                # 提取相关备注
                task_line_pattern = rf'- \[.\] .+?&of:{re.escape(task_id)}.*'
                task_match = re.search(task_line_pattern, content)
                notes = ""
                
                if task_match:
                    task_line = task_match.group(0)
                    # 提取质量评分等信息
                    quality_match = re.search(r'✨.*?(\d+/10)', task_line)
                    if quality_match:
                        notes += f"质量评分: {quality_match.group(1)}\n"
                    
                    # 提取其他备注
                    note_match = re.search(r'✨(.+?)(?=\s|$)', task_line)
                    if note_match:
                        notes += f"执行备注: {note_match.group(1)}\n"
                
                updates.append((task_id, status, notes.strip()))
        
        return updates
    
    def update_omnifocus_task(self, task_id, status, notes=""):
        """更新 OmniFocus 任务状态"""
        try:
            if status == 'completed':
                script = f'''
                tell application "OmniFocus 3"
                    set theTask to (first flattened task of default document whose id is "{task_id}")
                    set completed of theTask to true
                    if "{notes}" is not "" then
                        set note of theTask to (note of theTask) & "\\n\\nLogseq sync: {notes}"
                    end if
                end tell
                '''
            elif status == 'cancelled':
                script = f'''
                tell application "OmniFocus 3"
                    set theTask to (first flattened task of default document whose id is "{task_id}")
                    set completed of theTask to true
                    set note of theTask to (note of theTask) & "\\n\\n[CANCELLED] " & "{notes}"
                end tell
                '''
            elif status == 'deferred':
                tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
                script = f'''
                tell application "OmniFocus 3"
                    set theTask to (first flattened task of default document whose id is "{task_id}")
                    set defer date of theTask to date "{tomorrow}"
                    set note of theTask to (note of theTask) & "\\n\\nDeferred from Logseq: " & "{notes}"
                end tell
                '''
            else:
                return False
            
            result = subprocess.run(
                ['osascript', '-e', script], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ 任务 {task_id} 状态更新为 {status}")
                return True
            else:
                print(f"❌ 更新任务 {task_id} 失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 更新任务 {task_id} 时出错: {e}")
            return False
    
    def save_sync_record(self, sync_type, count):
        """保存同步记录"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "type": sync_type,
            "count": count,
            "date": date.today().isoformat()
        }
        
        log_file = self.data_path / "sync_log.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + "\n")
    
    def send_notification(self, title, message):
        """发送系统通知"""
        script = f'''
        display notification "{message}" with title "LifeOS - {title}" sound name "Glass"
        '''
        
        try:
            subprocess.run(['osascript', '-e', script], timeout=5)
        except:
            pass  # 忽略通知失败
    
    def status(self):
        """显示同步状态"""
        print("📊 LifeOS 同步状态")
        print("-" * 30)
        
        # 检查文件路径
        print(f"Logseq Graph: {self.logseq_path}")
        print(f"数据目录: {self.data_path}")
        
        # 检查最近的同步记录
        log_file = self.data_path / "sync_log.jsonl"
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_record = json.loads(lines[-1])
                    print(f"最后同步: {last_record['timestamp']}")
                    print(f"同步类型: {last_record['type']}")
                    print(f"处理任务: {last_record['count']} 个")


def main():
    parser = argparse.ArgumentParser(description='LifeOS 自动同步工具')
    parser.add_argument('action', choices=['morning', 'evening', 'status'], 
                       help='执行的操作')
    parser.add_argument('--logseq-path', default='~/logseq',
                       help='Logseq Graph 路径')
    parser.add_argument('--lifeos-path', default='~/LifeOS',
                       help='LifeOS 数据路径')
    
    args = parser.parse_args()
    
    sync = LifeOSSync(args.logseq_path, args.lifeos_path)
    
    if args.action == 'morning':
        sync.morning_sync()
    elif args.action == 'evening':
        sync.evening_sync()
    elif args.action == 'status':
        sync.status()


if __name__ == "__main__":
    main()