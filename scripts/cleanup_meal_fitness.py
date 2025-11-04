#!/usr/bin/env python3
"""
清理所有训练和膳食相关的Todoist任务
"""

import sys
import argparse
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from todoist_manager import TodoistManager


def cleanup_all_meal_and_fitness_tasks(auto_confirm=False):
    """清理所有训练和膳食相关任务"""
    print("🧹 清理所有训练和膳食相关任务")
    print("=" * 50)

    manager = TodoistManager()

    if not manager.api:
        print("❌ Todoist API未初始化")
        print("请先运行: ./lifeos setup")
        return False

    # 获取fitness项目的所有任务
    print("\n📥 获取所有任务...")
    all_tasks = manager.get_all_tasks()

    if not all_tasks:
        print("❌ 无法获取任务列表")
        return False

    print(f"找到 {len(all_tasks)} 个任务")

    # 定义需要删除的任务关键词
    keywords_to_delete = [
        # 膳食相关
        "早餐", "午餐", "晚餐", "加餐", "营养液", "饮水", "蛋白粉",
        "🥚", "🥜", "🍗", "🍌", "🥤", "🥩", "💧", "🏺",
        # 训练相关
        "训练", "健身", "跑步", "力量", "俯卧撑", "引体", "哑铃",
        "拉伸", "泡沫轴", "核心", "卧推", "划船", "肩推", "二头",
        "💪", "🏃", "🧘", "📝 记录今日训练",
        # 晨间例行
        "起床", "晨间例行", "🌅"
    ]

    # 筛选需要删除的任务
    tasks_to_delete = []
    for task in all_tasks:
        content = task.content
        # 检查是否包含任何关键词
        if any(keyword in content for keyword in keywords_to_delete):
            tasks_to_delete.append(task)

    if not tasks_to_delete:
        print("\n✅ 没有找到需要清理的任务")
        return True

    print(f"\n📋 找到 {len(tasks_to_delete)} 个需要清理的任务:")
    print("-" * 50)
    for i, task in enumerate(tasks_to_delete, 1):
        print(f"{i:2d}. {task.content}")

    # 确认删除
    print("\n" + "=" * 50)
    if not auto_confirm:
        print("⚠️  警告: 这将永久删除以上所有任务!")
        confirm = input("确认删除? (输入 'yes' 或 'y' 确认): ").strip().lower()

        if confirm not in ['yes', 'y', '是']:
            print("\n❌ 已取消删除操作")
            return False
    else:
        print("⚠️  自动确认模式: 将删除以上所有任务")

    # 执行删除
    print("\n🗑️  开始删除任务...")
    deleted_count = 0
    failed_count = 0

    for task in tasks_to_delete:
        try:
            manager.api.delete_task(task.id)
            print(f"  ✅ 已删除: {task.content}")
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ 删除失败: {task.content} - {e}")
            failed_count += 1

    print("\n" + "=" * 50)
    print(f"✅ 清理完成!")
    print(f"   成功删除: {deleted_count} 个任务")
    if failed_count > 0:
        print(f"   删除失败: {failed_count} 个任务")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='清理所有训练和膳食相关的Todoist任务')
    parser.add_argument('-y', '--yes', action='store_true',
                        help='自动确认删除，不需要交互式确认')
    args = parser.parse_args()

    cleanup_all_meal_and_fitness_tasks(auto_confirm=args.yes)
