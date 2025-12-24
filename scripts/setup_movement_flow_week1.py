#!/usr/bin/env python3
"""
Setup Movement Flow Week 1 training schedule in Todoist
Only creates tasks for the first week of training
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.todoist_manager import TodoistManager

def setup_week1_schedule():
    """Create Week 1 Movement Flow training tasks in Todoist"""

    manager = TodoistManager()
    print("🎯 Setting up Movement Flow Week 1 training schedule...\n")

    tasks_created = []

    # ============================================
    # WEEK 1: Ground Connection & Mobility
    # ============================================
    print("📋 Week 1: Ground Connection & Mobility (Days 1-7)")

    week1_tasks = [
        # Daily practice task (recurring)
        {
            "content": "🌅 Movement Flow 每日练习 (20-30分钟)",
            "project": "fitness",
            "priority": "high",
            "due_days": 0,
            "labels": ["routine"],
            "description": """📖 参考: /mnt/e/LifeOS/plans/movement_flow_mastery_path.md

**热身序列** (p.17):
• Arm snaps: 20次
• Squat snaps: 20次
• Downdog leg lifts: 每腿20次
• Sissy squat: 10次
• Puppy pose: 30秒保持
• Wheel push ups: 10秒保持
• 手腕和肩膀准备: 10次

**核心动作** (慢速控制):
1. Slide Ups - Straddle Up (p.48-49)
   • 每侧5次，专注掌心旋转
2. Hip Rolls - Side Hip Roll (p.114-115)
   • 每侧3次，专注臀部控制
3. Basic Rolls - Forward Roll前半部分 (p.74-75)
   • 5次，专注脊柱屈曲

**恢复拉伸** (各30秒):
• Straddle pancake (劈叉前屈)
• Two knee twist (双膝扭转)
• Side stretch (侧伸展)

💡 原则: 慢速移动，深呼吸，专注"吸收"原则（安静、受控的动作）"""
        },

        # Mid-week check-in
        {
            "content": "📝 Week 1 中期检查：动作质量自查",
            "project": "fitness",
            "priority": "medium",
            "due_days": 3,
            "description": """检查清单:
✓ Slide Ups 是否能保持手臂伸直？
✓ Hip Rolls 是否能安静无声地完成？
✓ Forward Roll 是否能流畅过渡？
✓ 身体感觉如何？（能量、疼痛、灵活性）

记录发现的问题，下次练习重点改进。"""
        },

        # Weekend review
        {
            "content": "📊 Week 1 周末总结：回顾本周进展",
            "project": "fitness",
            "priority": "high",
            "due_days": 6,
            "description": """Week 1 反思问题:
1. 哪些动作感觉最自然？
2. 哪些动作需要更多注意？
3. 能否流畅地从一个动作过渡到另一个？
4. 身体感觉如何？（能量、疼痛、自由度）
5. 发现了哪些创意变化？

✓ 如果能够以控制和安静的方式执行每个动作，准备进入 Week 2
✗ 如果还有困难，继续本周训练，不要急于进入下一周"""
        },

        # Week 2 decision point
        {
            "content": "🔄 Week 2 准备评估：是否准备好扩展训练范围？",
            "project": "fitness",
            "priority": "high",
            "due_days": 7,
            "description": """Week 1 完成检查点:
□ 可以控制地完成 Slide Ups（每侧5次）
□ 可以安静地完成 Hip Rolls（每侧3次）
□ 可以流畅地完成 Forward Roll 前半部分（5次）
□ 每日热身序列已经熟练掌握
□ 身体感觉更加灵活和有意识
□ 可以连接 2-3 个动作而不停顿

✅ 全部打勾：准备进入 Week 2（添加 Sliding Splits + Matrix Foundation）
⚠️ 还有未勾选项：继续 Week 1 训练，等身体准备好再进入下一周

💡 记住：质量重于数量！精通一个动作胜过匆忙完成许多动作。"""
        }
    ]

    for task in week1_tasks:
        try:
            manager.create_task(**task)
            tasks_created.append(task["content"][:50])
            print(f"  ✓ {task['content'][:60]}...")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # ============================================
    # SUMMARY
    # ============================================
    print(f"\n✅ Week 1 设置完成!")
    print(f"📊 创建了 {len(tasks_created)} 个任务")
    print(f"\n🎯 第一周训练重点：")
    print(f"   • 每日练习 20-30 分钟")
    print(f"   • 掌握 3 个核心动作（Slide Ups, Hip Rolls, Basic Rolls）")
    print(f"   • 专注质量和控制，而非速度")
    print(f"   • Week 1 结束时评估是否准备好进入 Week 2")
    print(f"\n📖 完整训练计划: /mnt/e/LifeOS/plans/movement_flow_mastery_path.md")
    print(f"📚 动作手册: Movement-Flow-Manual-Co-Edit.pdf")
    print(f"\n💡 原则: 慢速练习建立更快的精通。动作要安静、受控、流畅。")

    return tasks_created

if __name__ == "__main__":
    try:
        tasks = setup_week1_schedule()
    except Exception as e:
        print(f"\n❌ 设置过程中出错: {e}")
        sys.exit(1)
