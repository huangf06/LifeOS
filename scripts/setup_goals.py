#!/usr/bin/env python3
"""
LifeOS 三大目标快速设置脚本
自动创建健身、求职、英语学习三个核心目标的项目和任务模板
"""

import sys
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from todoist_manager import TodoistManager
from datetime import datetime

class GoalsSetup:
    def __init__(self):
        self.manager = TodoistManager()

        if not self.manager.api:
            print("❌ Todoist未配置，请先运行: lifeos setup")
            sys.exit(1)

    def setup_all_goals(self):
        """设置所有三大目标"""
        print("🎯 开始设置三大核心目标...")
        print("")

        # 确保项目已创建
        print("📁 检查项目...")
        self.manager.initialize_projects()
        print("")

        # 设置健身目标
        self.setup_fitness_goal()
        print("")

        # 设置求职目标
        self.setup_career_goal()
        print("")

        # 设置英语目标
        self.setup_english_goal()
        print("")

        print("✅ 三大目标设置完成！")
        print("💡 提示：访问 Todoist 查看你的新项目和任务")

    def setup_fitness_goal(self):
        """设置健身目标"""
        print("🏋️  设置健身目标...")

        fitness_tasks = [
            {
                "name": "制定健身计划",
                "body": "根据当前体能水平，制定为期3个月的健身计划。包括：力量训练、有氧运动、柔韧性练习。",
                "project": "fitness",
                "priority": "high",
                "due_days": 0,
                "labels": ["important"]
            },
            {
                "name": "购买健身装备",
                "body": "购买必要的健身装备：运动鞋、运动服、哑铃、瑜伽垫等。",
                "project": "fitness",
                "priority": "medium",
                "due_days": 1,
                "labels": ["routine"]
            },
            {
                "name": "俯卧撑能力测试",
                "body": "测试当前俯卧撑水平（标准动作），记录完成数量，作为基准数据。",
                "project": "fitness",
                "priority": "high",
                "due_days": 0,
                "labels": ["important"]
            },
            {
                "name": "引体向上能力测试",
                "body": "测试当前引体向上水平，记录完成数量，作为基准数据。",
                "project": "fitness",
                "priority": "high",
                "due_days": 0,
                "labels": ["important"]
            },
            {
                "name": "设置每周训练提醒",
                "body": "在日历中设置固定的训练时间，每周至少4次，每次60分钟。",
                "project": "fitness",
                "priority": "medium",
                "due_days": 0,
                "labels": ["habit"]
            },
            {
                "name": "记录第一周训练日志",
                "body": "每次训练后记录：完成的动作、组数、感受、进步点。",
                "project": "fitness",
                "priority": "medium",
                "due_days": 7,
                "labels": ["habit"]
            }
        ]

        results = self.manager.create_tasks_batch(fitness_tasks)
        print(f"  ✅ 健身目标：创建了 {results['success']} 个任务")

    def setup_career_goal(self):
        """设置求职目标"""
        print("💼 设置求职目标...")

        career_tasks = [
            {
                "name": "更新简历",
                "body": "更新简历内容，突出最新的项目经验和技能。准备中英文两个版本。",
                "project": "career",
                "priority": "high",
                "due_days": 1,
                "labels": ["important"]
            },
            {
                "name": "优化LinkedIn个人资料",
                "body": "完善LinkedIn个人资料，添加项目经验、技能标签、专业头像。",
                "project": "career",
                "priority": "high",
                "due_days": 2,
                "labels": ["important"]
            },
            {
                "name": "列出目标公司清单",
                "body": "列出20-30家目标公司，研究公司文化、产品、技术栈、招聘需求。",
                "project": "career",
                "priority": "high",
                "due_days": 3,
                "labels": ["important"]
            },
            {
                "name": "准备自我介绍（中英文）",
                "body": "准备1分钟和3分钟的自我介绍，练习到流利。包括：背景、经验、优势、目标。",
                "project": "career",
                "priority": "high",
                "due_days": 3,
                "labels": ["important"]
            },
            {
                "name": "整理项目案例",
                "body": "整理3-5个代表性项目，准备STAR法则的描述（情境、任务、行动、结果）。",
                "project": "career",
                "priority": "medium",
                "due_days": 5,
                "labels": ["routine"]
            },
            {
                "name": "复习常见面试题",
                "body": "复习技术面试常见问题，准备答案。涵盖：技术栈、算法、系统设计、行为面试。",
                "project": "career",
                "priority": "medium",
                "due_days": 7,
                "labels": ["routine"]
            },
            {
                "name": "每周投递10个职位",
                "body": "每周筛选并投递10个匹配的职位，记录投递情况和跟进状态。",
                "project": "career",
                "priority": "high",
                "due_days": 7,
                "labels": ["habit", "important"]
            },
            {
                "name": "准备作品集网站",
                "body": "创建或更新个人作品集网站，展示项目、技能、博客文章。",
                "project": "career",
                "priority": "medium",
                "due_days": 14,
                "labels": ["routine"]
            }
        ]

        results = self.manager.create_tasks_batch(career_tasks)
        print(f"  ✅ 求职目标：创建了 {results['success']} 个任务")

    def setup_english_goal(self):
        """设置英语学习目标"""
        print("🗣️  设置英语学习目标...")

        english_tasks = [
            {
                "name": "英语水平评估",
                "body": "进行英语水平自测，明确当前听说读写能力，找出薄弱环节。",
                "project": "english",
                "priority": "high",
                "due_days": 0,
                "labels": ["important"]
            },
            {
                "name": "设定具体学习目标",
                "body": "设定3个月的具体目标，例如：词汇量、口语流利度、能看懂技术文档、能进行面试对话。",
                "project": "english",
                "priority": "high",
                "due_days": 1,
                "labels": ["important"]
            },
            {
                "name": "选择学习资源",
                "body": "选择适合的学习资源：APP（多邻国/扇贝）、播客、YouTube频道、技术文档、英文书籍。",
                "project": "english",
                "priority": "medium",
                "due_days": 1,
                "labels": ["routine"]
            },
            {
                "name": "每日单词学习30个",
                "body": "每天学习30个新单词，重点是技术词汇和职场常用词汇。使用间隔重复记忆法。",
                "project": "english",
                "priority": "high",
                "due_days": 0,
                "labels": ["habit", "important"]
            },
            {
                "name": "每日听力练习20分钟",
                "body": "每天听英语材料20分钟：技术播客、TED演讲、技术会议视频等。",
                "project": "english",
                "priority": "high",
                "due_days": 0,
                "labels": ["habit", "important"]
            },
            {
                "name": "每周口语练习3次",
                "body": "每周进行3次口语练习：跟读、模仿、自我对话、在线语言交换等。",
                "project": "english",
                "priority": "high",
                "due_days": 2,
                "labels": ["habit", "important"]
            },
            {
                "name": "阅读英文技术文档",
                "body": "每周阅读2-3篇英文技术文档或博客，提高专业英语阅读能力。",
                "project": "english",
                "priority": "medium",
                "due_days": 3,
                "labels": ["routine"]
            },
            {
                "name": "观看英文技术视频",
                "body": "每周观看2个英文技术教学视频（关闭字幕或只看英文字幕），提高听力和专业词汇。",
                "project": "english",
                "priority": "medium",
                "due_days": 3,
                "labels": ["routine"]
            },
            {
                "name": "准备英文面试常见问题",
                "body": "准备10-15个英文面试常见问题的回答，录音练习直到流利。",
                "project": "english",
                "priority": "high",
                "due_days": 7,
                "labels": ["important"]
            },
            {
                "name": "第一周学习总结",
                "body": "总结第一周学习情况：完成的任务、遇到的困难、需要调整的地方、下周计划。",
                "project": "english",
                "priority": "medium",
                "due_days": 7,
                "labels": ["routine"]
            }
        ]

        results = self.manager.create_tasks_batch(english_tasks)
        print(f"  ✅ 英语学习目标：创建了 {results['success']} 个任务")

    def setup_single_goal(self, goal_name):
        """设置单个目标"""
        if goal_name.lower() in ['fitness', '健身']:
            self.setup_fitness_goal()
        elif goal_name.lower() in ['career', '求职', 'job']:
            self.setup_career_goal()
        elif goal_name.lower() in ['english', '英语']:
            self.setup_english_goal()
        else:
            print(f"❌ 未知目标: {goal_name}")
            print("可用目标: fitness/健身, career/求职, english/英语")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='LifeOS 三大目标快速设置')
    parser.add_argument('--goal', help='设置单个目标 (fitness/career/english)')
    parser.add_argument('--all', action='store_true', help='设置所有目标')

    args = parser.parse_args()

    setup = GoalsSetup()

    if args.all:
        setup.setup_all_goals()
    elif args.goal:
        setup.setup_single_goal(args.goal)
    else:
        # 默认设置所有目标
        print("用法:")
        print("  python setup_goals.py --all              # 设置所有三大目标")
        print("  python setup_goals.py --goal fitness     # 只设置健身目标")
        print("  python setup_goals.py --goal career      # 只设置求职目标")
        print("  python setup_goals.py --goal english     # 只设置英语目标")
        print("")

        confirm = input("是否现在设置所有三大目标？(y/n): ").strip().lower()
        if confirm in ['y', 'yes', '是', '好']:
            setup.setup_all_goals()
        else:
            print("已取消")


if __name__ == "__main__":
    main()
