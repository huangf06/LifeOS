#!/usr/bin/env python3
"""
快速任务创建工具
支持直接指定时间和项目，无需自然语言解析
"""

import sys
import json
from pathlib import Path
from todoist_api_python.api import TodoistAPI

def quick_task(content, due_string=None, project="life", priority="medium", description=""):
    """快速创建任务"""

    # 自动获取项目根目录（相对于此脚本文件）
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    config_path = project_root / "config" / "todoist_config.json"

    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        return False

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 初始化API
    try:
        api = TodoistAPI(config["api_token"])
    except Exception as e:
        print(f"❌ API初始化失败: {e}")
        return False

    # 获取项目ID
    project_id = None
    if project and project in config["projects"]:
        project_id = config["projects"][project]["project_id"]

    # 优先级映射
    priority_map = {"high": 4, "medium": 2, "low": 1}
    priority_value = priority_map.get(priority, 2)

    # 创建任务
    try:
        task_params = {
            "content": content,
            "priority": priority_value
        }

        if project_id:
            task_params["project_id"] = project_id

        if due_string:
            task_params["due_string"] = due_string

        if description:
            task_params["description"] = description

        task = api.add_task(**task_params)

        print(f"✅ 任务创建成功！")
        print(f"   📝 {task.content}")
        if task.due:
            print(f"   ⏰ {task.due.string}")
        print(f"   📂 项目: {project}")
        print(f"   🔗 ID: {task.id}")

        return True

    except Exception as e:
        print(f"❌ 创建任务失败: {e}")
        return False


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 quick_task.py '任务内容' [时间] [项目] [优先级] [描述]")
        print("")
        print("示例:")
        print("  python3 quick_task.py '取快递' 'today 21:00'")
        print("  python3 quick_task.py '健身' 'every day at 18:00' fitness high")
        print("  python3 quick_task.py '面试' 'tomorrow 10am' career high '准备简历和作品集'")
        print("")
        print("时间格式:")
        print("  - today, tomorrow")
        print("  - today 21:00, tomorrow 9am")
        print("  - every day, every weekday")
        print("  - every monday at 9am")
        print("  - 2025-01-15")
        print("")
        print("项目: fitness, career, english, work, study, life, other")
        print("优先级: high, medium, low")
        return

    content = sys.argv[1]
    due_string = sys.argv[2] if len(sys.argv) > 2 else None
    project = sys.argv[3] if len(sys.argv) > 3 else "life"
    priority = sys.argv[4] if len(sys.argv) > 4 else "medium"
    description = sys.argv[5] if len(sys.argv) > 5 else ""

    quick_task(content, due_string, project, priority, description)


if __name__ == "__main__":
    main()
