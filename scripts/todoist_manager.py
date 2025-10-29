#!/usr/bin/env python3
"""
LifeOS Todoist 集成管理器
替代原email_sender.py，使用Todoist API直接管理任务
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import getpass

try:
    from todoist_api_python.api import TodoistAPI
    from todoist_api_python.models import Task, Project, Label
except ImportError:
    print("❌ Todoist API Python库未安装")
    print("请运行: pip3 install todoist-api-python")
    sys.exit(1)


class TodoistManager:
    def __init__(self, config_path=None):
        # 自动获取项目根目录（相对于此脚本文件）
        if config_path is None:
            script_dir = Path(__file__).parent
            project_root = script_dir.parent
            self.config_path = project_root / "config" / "todoist_config.json"
        else:
            self.config_path = Path(config_path).expanduser()
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self.load_config()

        # 初始化API客户端
        if self.config.get("api_token"):
            try:
                self.api = TodoistAPI(self.config["api_token"])
            except Exception as e:
                print(f"⚠️  API初始化失败: {e}")
                self.api = None
        else:
            self.api = None

    def _flatten_paginator(self, paginator):
        """将分页结果扁平化为列表"""
        results = []
        for page in paginator:
            results.extend(page)
        return results

    def load_config(self):
        """加载Todoist配置"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"❌ 配置文件不存在: {self.config_path}")
            return {}

    def save_config(self):
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def setup_todoist(self):
        """首次设置Todoist API Token"""
        print("🔧 Todoist API 设置")
        print("")
        print("请按照以下步骤获取API Token:")
        print("1. 打开 https://todoist.com/")
        print("2. 登录你的账户")
        print("3. 进入 Settings > Integrations > Developer")
        print("4. 复制 'API Token'")
        print("")

        api_token = getpass.getpass("请输入你的Todoist API Token: ").strip()

        if not api_token:
            print("❌ Token不能为空")
            return False

        # 测试连接
        try:
            test_api = TodoistAPI(api_token)
            projects = []
            for page in test_api.get_projects():
                projects.extend(page)

            print(f"✅ 连接成功！找到 {len(projects)} 个项目")

            # 保存配置
            self.config["api_token"] = api_token
            self.config["setup_date"] = datetime.now().isoformat()
            self.save_config()

            # 重新初始化API
            self.api = test_api

            print("✅ Todoist配置保存成功！")

            # 询问是否创建默认项目
            create_projects = input("是否创建默认项目（健身/求职/英语等）？(y/n): ").strip().lower()
            if create_projects in ['y', 'yes', '是', '好']:
                self.initialize_projects()

            return True

        except Exception as e:
            print(f"❌ 连接失败: {e}")
            print("请检查Token是否正确")
            return False

    def initialize_projects(self):
        """初始化默认项目和标签"""
        if not self.api:
            print("❌ 请先设置API Token")
            return False

        print("📁 创建默认项目...")

        created_count = 0
        for key, project_config in self.config["projects"].items():
            try:
                # 检查项目是否已存在
                existing_projects = self._flatten_paginator(self.api.get_projects())
                existing_project = next(
                    (p for p in existing_projects if p.name == project_config["name"]),
                    None
                )

                if existing_project:
                    print(f"  ℹ️  项目已存在: {project_config['name']}")
                    project_config["project_id"] = existing_project.id
                else:
                    # 创建新项目
                    project = self.api.add_project(
                        name=project_config["name"],
                        color=project_config.get("color", "grey"),
                        is_favorite=project_config.get("is_favorite", False)
                    )
                    project_config["project_id"] = project.id
                    print(f"  ✅ 创建项目: {project_config['name']}")
                    created_count += 1

            except Exception as e:
                print(f"  ❌ 创建项目 {project_config['name']} 失败: {e}")

        # 创建标签
        print("\n🏷️  创建默认标签...")
        for key, label_config in self.config["labels"].items():
            try:
                # 检查标签是否已存在
                existing_labels = self._flatten_paginator(self.api.get_labels())
                existing_label = next(
                    (l for l in existing_labels if l.name == label_config["name"]),
                    None
                )

                if existing_label:
                    print(f"  ℹ️  标签已存在: {label_config['name']}")
                    label_config["label_id"] = existing_label.id
                else:
                    # 创建新标签
                    label = self.api.add_label(
                        name=label_config["name"],
                        color=label_config.get("color", "grey")
                    )
                    label_config["label_id"] = label.id
                    print(f"  ✅ 创建标签: {label_config['name']}")

            except Exception as e:
                print(f"  ❌ 创建标签 {label_config['name']} 失败: {e}")

        # 保存更新后的配置
        self.save_config()

        print(f"\n✅ 初始化完成！创建了 {created_count} 个新项目")
        return True

    def create_task(
        self,
        content: str,
        project: str = None,
        priority: str = "medium",
        due_days: int = 0,
        labels: List[str] = None,
        description: str = "",
        parent_id: str = None
    ) -> Optional[Task]:
        """创建单个任务"""
        if not self.api:
            print("❌ Todoist API未初始化，请先运行setup")
            return None

        try:
            # 映射优先级
            priority_map = self.config["default_settings"]["priority_mapping"]
            priority_value = priority_map.get(priority, 2)

            # 获取项目ID
            project_id = None
            if project:
                project_config = self.config["projects"].get(project)
                if project_config:
                    project_id = project_config.get("project_id")

            # 设置截止日期
            due_string = None
            if due_days == 0:
                due_string = "today"
            elif due_days == 1:
                due_string = "tomorrow"
            elif due_days > 1:
                due_date = datetime.now() + timedelta(days=due_days)
                due_string = due_date.strftime("%Y-%m-%d")

            # 处理标签
            label_names = []
            if labels:
                for label_key in labels:
                    label_config = self.config["labels"].get(label_key)
                    if label_config:
                        label_names.append(label_config["name"])

            # 创建任务
            task_params = {
                "content": content,
                "description": description,
                "project_id": project_id,
                "due_string": due_string,
                "priority": priority_value,
                "labels": label_names
            }

            # 添加父任务ID（用于创建子任务）
            if parent_id:
                task_params["parent_id"] = parent_id

            task = self.api.add_task(**task_params)

            return task

        except Exception as e:
            print(f"❌ 创建任务失败: {e}")
            return None

    def create_tasks_batch(self, tasks: List[Dict]) -> Dict:
        """批量创建任务"""
        if not self.api:
            print("❌ Todoist API未初始化")
            return {"success": 0, "failed": 0, "tasks": []}

        results = {
            "success": 0,
            "failed": 0,
            "tasks": []
        }

        print(f"📝 开始创建 {len(tasks)} 个任务...")

        for i, task_data in enumerate(tasks, 1):
            task_name = task_data.get('name', task_data.get('content', f'任务 {i}'))
            print(f"  {i}/{len(tasks)}: {task_name[:40]}...")

            task = self.create_task(
                content=task_name,
                project=task_data.get('project', 'other'),
                priority=task_data.get('priority', 'medium'),
                due_days=task_data.get('due_days', 1),
                labels=task_data.get('labels', []),
                description=task_data.get('body', task_data.get('note', ''))
            )

            if task:
                results["success"] += 1
                results["tasks"].append(task)
            else:
                results["failed"] += 1

        print(f"\n✅ 成功创建 {results['success']}/{len(tasks)} 个任务")
        if results["failed"] > 0:
            print(f"⚠️  失败 {results['failed']} 个")

        return results

    def send_fitness_plan(self):
        """发送健身计划到Todoist"""
        fitness_tasks = [
            {
                "name": "动态热身：关节活动",
                "body": "手腕、肩膀、腰部、膝盖各方向转动热身，准备身体进入运动状态。预计3分钟。",
                "project": "fitness",
                "priority": "medium",
                "due_days": 0,
                "labels": ["routine"]
            },
            {
                "name": "轻松跑步热身 7分钟",
                "body": "楼下健身房跑步机或户外慢跑，心率控制在120-130bpm，为力量训练做准备。",
                "project": "fitness",
                "priority": "medium",
                "due_days": 0,
                "labels": ["routine"]
            },
            {
                "name": "🔥俯卧撑测试 3组×8-12个",
                "body": "重要任务！测试现有水平，动作标准比数量重要。记录每组完成个数，为后续训练制定基准。",
                "project": "fitness",
                "priority": "high",
                "due_days": 0,
                "labels": ["important"]
            },
            {
                "name": "哑铃推举 3组×8-10个",
                "body": "从5-10kg轻重量开始，感受肌肉发力。组间休息60-90秒，注意呼吸节奏。",
                "project": "fitness",
                "priority": "medium",
                "due_days": 0,
                "labels": ["routine"]
            },
            {
                "name": "哑铃划船 3组×8-10个",
                "body": "背部训练，注意挺胸收肩胛骨，拉起时想象挤压背部肌肉。重量同样从轻开始。",
                "project": "fitness",
                "priority": "medium",
                "due_days": 0,
                "labels": ["routine"]
            },
            {
                "name": "🔥引体向上水平测试",
                "body": "重要任务！2组，能做几个做几个，记录准确数据。这是衡量上肢力量的重要指标。",
                "project": "fitness",
                "priority": "high",
                "due_days": 0,
                "labels": ["important"]
            },
            {
                "name": "上肢拉伸放松 10分钟",
                "body": "胸部、肩部、手臂各部位充分拉伸，预防肌肉僵硬，促进恢复。",
                "project": "fitness",
                "priority": "medium",
                "due_days": 0,
                "labels": ["routine"]
            },
            {
                "name": "记录今日训练数据",
                "body": "记录俯卧撑和引体向上的准确数字，以及训练感受，为明天的下肢训练做参考。",
                "project": "fitness",
                "priority": "medium",
                "due_days": 0,
                "labels": ["routine"]
            }
        ]

        print("🏋️  发送健身计划到 Todoist...")
        results = self.create_tasks_batch(fitness_tasks)

        return results["success"] == len(fitness_tasks)

    def get_all_tasks(self, project: str = None, label: str = None) -> List[Task]:
        """获取所有任务（用于数据导出和分析）"""
        if not self.api:
            print("❌ Todoist API未初始化")
            return []

        try:
            filters = {}

            if project:
                project_config = self.config["projects"].get(project)
                if project_config and project_config.get("project_id"):
                    filters["project_id"] = project_config["project_id"]

            if label:
                label_config = self.config["labels"].get(label)
                if label_config:
                    filters["label"] = label_config["name"]

            tasks_paginator = self.api.get_tasks(**filters)
            tasks = self._flatten_paginator(tasks_paginator)
            return tasks

        except Exception as e:
            print(f"❌ 获取任务失败: {e}")
            return []

    def export_tasks_to_json(self, output_file: str = None):
        """导出所有任务为JSON（用于数据分析）"""
        if not output_file:
            # 使用相对路径
            script_dir = Path(__file__).parent
            project_root = script_dir.parent
            data_dir = project_root / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            output_file = data_dir / f"todoist_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        else:
            output_file = Path(output_file)

        output_path = Path(output_file).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print("📊 导出Todoist任务数据...")

        tasks = self.get_all_tasks()

        if not tasks:
            print("⚠️  没有找到任务")
            return None

        # 转换为可序列化的字典
        tasks_data = []
        for task in tasks:
            # 处理due date
            due_date = None
            if task.due:
                if hasattr(task.due, 'date'):
                    due_date = str(task.due.date) if task.due.date else None
                else:
                    due_date = str(task.due)

            tasks_data.append({
                "id": task.id,
                "content": task.content,
                "description": task.description,
                "project_id": task.project_id,
                "priority": task.priority,
                "due": due_date,
                "labels": task.labels,
                "created_at": task.created_at.isoformat() if hasattr(task.created_at, 'isoformat') else str(task.created_at),
                "is_completed": task.is_completed
            })

        export_data = {
            "export_time": datetime.now().isoformat(),
            "total_tasks": len(tasks_data),
            "tasks": tasks_data
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 成功导出 {len(tasks_data)} 个任务到: {output_path}")
        return str(output_path)

    def test_connection(self):
        """测试Todoist连接"""
        if not self.api:
            print("❌ API未初始化，请先运行setup")
            return False

        try:
            print("🔌 测试Todoist连接...")
            projects = self._flatten_paginator(self.api.get_projects())
            labels = self._flatten_paginator(self.api.get_labels())
            tasks = self._flatten_paginator(self.api.get_tasks())

            print(f"✅ 连接成功！")
            print(f"   项目数: {len(projects)}")
            print(f"   标签数: {len(labels)}")
            print(f"   任务数: {len(tasks)}")

            return True

        except Exception as e:
            print(f"❌ 连接测试失败: {e}")
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description='LifeOS Todoist 管理器')
    parser.add_argument('action', nargs='?',
                       choices=['setup', 'test', 'fitness', 'init-projects', 'export', 'list'],
                       default='help',
                       help='执行的操作')
    parser.add_argument('--project', help='指定项目')
    parser.add_argument('--label', help='指定标签')
    parser.add_argument('--output', help='导出文件路径')

    args = parser.parse_args()

    manager = TodoistManager()

    if args.action == 'setup':
        manager.setup_todoist()

    elif args.action == 'test':
        manager.test_connection()

    elif args.action == 'init-projects':
        manager.initialize_projects()

    elif args.action == 'fitness':
        manager.send_fitness_plan()

    elif args.action == 'export':
        manager.export_tasks_to_json(args.output)

    elif args.action == 'list':
        tasks = manager.get_all_tasks(project=args.project, label=args.label)
        print(f"\n📋 找到 {len(tasks)} 个任务:")
        for i, task in enumerate(tasks, 1):
            status = "✓" if task.is_completed else "○"
            priority_icons = ["", "!", "!!", "!!!"]
            priority_icon = priority_icons[task.priority - 1] if task.priority > 0 else ""
            print(f"  {status} {i}. {priority_icon} {task.content}")

    else:
        print("🤖 LifeOS Todoist 管理器")
        print("")
        print("用法:")
        print("  python todoist_manager.py setup          # 首次设置API Token")
        print("  python todoist_manager.py test           # 测试连接")
        print("  python todoist_manager.py init-projects  # 初始化默认项目和标签")
        print("  python todoist_manager.py fitness        # 发送健身计划")
        print("  python todoist_manager.py export         # 导出所有任务数据")
        print("  python todoist_manager.py list           # 列出所有任务")
        print("  python todoist_manager.py list --project fitness  # 列出特定项目任务")


if __name__ == "__main__":
    main()
