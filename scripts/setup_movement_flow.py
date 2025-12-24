#!/usr/bin/env python3
"""
Setup Movement Flow training schedule in Todoist
Creates structured tasks for the 16-week mastery path
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.todoist_manager import TodoistManager

def setup_movement_flow_schedule():
    """Create Movement Flow training tasks in Todoist"""

    manager = TodoistManager()
    print("🎯 Setting up Movement Flow training schedule...\n")

    # Get today's date for scheduling
    today = datetime.now()

    tasks_created = []

    # ============================================
    # PHASE 1: FOUNDATION (Weeks 1-4)
    # ============================================
    print("📋 Phase 1: Foundation (Weeks 1-4)")

    phase1_tasks = [
        {
            "content": "🌅 Week 1-2: Ground Connection & Mobility - Daily practice (20-30 min): Warm-up + Slide Ups + Hip Rolls + Basic Rolls",
            "project": "fitness",
            "priority": "high",
            "due_days": 0,
            "labels": ["routine"],
            "description": "Focus: Straddle Up, Side Hip Roll, Forward Roll (first half). Move slowly, breathe deeply. Mobility: straddle pancake, two knee twist, side stretch (30s each)"
        },
        {
            "content": "📊 Week 2 Checkpoint: Can you perform each movement with control and silence?",
            "project": "fitness",
            "priority": "medium",
            "due_days": 14,
            "description": "Review movements learned: Slide Ups, Hip Rolls, Basic Rolls. Check for absorption principle and silent movement."
        },
        {
            "content": "🌅 Week 3-4: Expanding Range - Add Sliding Splits + Matrix Foundation + Basic Transitions",
            "project": "fitness",
            "priority": "high",
            "due_days": 14,
            "labels": ["routine"],
            "description": "Add: Forward Fold Sliding Split, Canoe, and linking Slide Up → Hip Roll → Slide Up (3 rounds). Continue daily mobility work."
        },
        {
            "content": "📊 Phase 1 Complete Checkpoint: Can you link 3-4 movements smoothly?",
            "project": "fitness",
            "priority": "high",
            "due_days": 28,
            "description": "Review 10 basic movements. Body should feel more mobile and aware. Confirm transitions are smooth before moving to Phase 2."
        }
    ]

    for task in phase1_tasks:
        try:
            manager.create_task(**task)
            tasks_created.append(task["content"][:50])
            print(f"  ✓ {task['content'][:60]}...")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # ============================================
    # PHASE 2: INTEGRATION (Weeks 5-8)
    # ============================================
    print("\n📋 Phase 2: Integration (Weeks 5-8)")

    phase2_tasks = [
        {
            "content": "🔄 Week 5-6: Dynamic Movement Patterns - Add Sweeps + QDR + Open Door (30-40 min daily)",
            "project": "fitness",
            "priority": "high",
            "due_days": 35,
            "labels": ["routine"],
            "description": "First Flow: Low Sweep → Slide Up → Forward Fold Sliding Split → Canoe → Stand (5 rounds daily). Focus on 'Cutting & Splicing' smooth transitions."
        },
        {
            "content": "🎬 Week 6 Video: Record your first flow sequence for self-review",
            "project": "fitness",
            "priority": "medium",
            "due_days": 42,
            "description": "Film your Low Sweep → Slide Up → Sliding Split → Canoe flow. Watch without judgment, notice smoothness and creativity."
        },
        {
            "content": "🔄 Week 7-8: Building Complexity - Add Around The World + Monkey Flow + Cartwheels",
            "project": "fitness",
            "priority": "high",
            "due_days": 49,
            "labels": ["routine"],
            "description": "Create 2-3 different sequences using 5-6 movements each. Practice each sequence 3 times. Record yourself to analyze flow quality."
        },
        {
            "content": "📊 Phase 2 Complete Checkpoint: Can you transition between movements without pausing?",
            "project": "fitness",
            "priority": "high",
            "due_days": 56,
            "description": "Review 20 movements confidently. Should be able to create mini-flows (5-6 movements). Transitions feel natural."
        }
    ]

    for task in phase2_tasks:
        try:
            manager.create_task(**task)
            tasks_created.append(task["content"][:50])
            print(f"  ✓ {task['content'][:60]}...")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # ============================================
    # PHASE 3: ELEVATION (Weeks 9-12)
    # ============================================
    print("\n📋 Phase 3: Elevation (Weeks 9-12)")

    phase3_tasks = [
        {
            "content": "🚀 Week 9-10: Inversions & Kicks - Add Handstands + Bridge Roll + Spinning Kick + Matrix",
            "project": "fitness",
            "priority": "high",
            "due_days": 63,
            "labels": ["routine"],
            "description": "Practice 'Official Flow' from manual: Falling Tree → Forward Fold Sliding Splits → Monkey Flow → Open Door → Bridge Roll (3-5 rounds daily). Use wall support for handstands."
        },
        {
            "content": "🎬 Week 10 Video: Record 'Official Flow' performance",
            "project": "fitness",
            "priority": "medium",
            "due_days": 70,
            "description": "Film your Official Flow sequence. Review for smoothness, creativity, and joy. Notice improvement from Week 6."
        },
        {
            "content": "🚀 Week 11-12: Mastery Integration - Add Windmill + QDR Side Flip + Double Pidgeon + Compass",
            "project": "fitness",
            "priority": "high",
            "due_days": 77,
            "labels": ["routine"],
            "description": "Spontaneous Flow Practice: Put on music, start anywhere, flow 5 min without planning. Focus on feeling, not thinking. Repeat 3-4 times daily (20 min total)."
        },
        {
            "content": "📊 Phase 3 Complete Checkpoint: Can you create unique flows spontaneously?",
            "project": "fitness",
            "priority": "high",
            "due_days": 84,
            "description": "Review all 30 Level 1 movements. Can invert safely. Can flow for 5+ minutes continuously. Ready for spontaneous creation phase."
        }
    ]

    for task in phase3_tasks:
        try:
            manager.create_task(**task)
            tasks_created.append(task["content"][:50])
            print(f"  ✓ {task['content'][:60]}...")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # ============================================
    # PHASE 4: CREATION (Weeks 13-16)
    # ============================================
    print("\n📋 Phase 4: Creation (Weeks 13-16)")

    phase4_tasks = [
        {
            "content": "🎨 Week 13-14: Pattern Internalization - Morning (15m) + Focused (30m) + Creative (20m) structure",
            "project": "fitness",
            "priority": "high",
            "due_days": 91,
            "labels": ["routine"],
            "description": "Morning: warm-up + 3 favorite movements + 5m spontaneous flow. Focused: drill 2-3 weak movements (10 reps each). Creative: create 3 new flows daily, film weekly."
        },
        {
            "content": "🎬 Week 14 Video: Film creative flow in new environment (outdoor/different surface)",
            "project": "fitness",
            "priority": "medium",
            "due_days": 98,
            "description": "Practice flow challenges: different locations, music tempos, eyes closed (carefully), reverse familiar flows."
        },
        {
            "content": "🎨 Week 15-16: Ultimate Freedom - Create signature flows (Morning/Restoration/Power/Freestyle)",
            "project": "fitness",
            "priority": "high",
            "due_days": 105,
            "labels": ["routine"],
            "description": "Mastery Test: Create Morning Flow (5m energizing), Restoration Flow (10m slow meditative), Power Flow (8m dynamic), Freestyle (spontaneous). Reduce structure, move when called."
        },
        {
            "content": "🎬 Final Week 16 Video: Record all 4 signature flows for completion milestone",
            "project": "fitness",
            "priority": "high",
            "due_days": 112,
            "description": "Film your Morning, Restoration, Power, and Freestyle flows. Celebrate your journey from foundation to spontaneous mastery!"
        },
        {
            "content": "🏆 Movement Flow Mastery Complete - Phase 4 Final Checkpoint",
            "project": "fitness",
            "priority": "high",
            "due_days": 112,
            "description": "✓ Can flow 10+ min continuously without thinking\n✓ Can create unique sequences spontaneously\n✓ Can adapt to any space/surface\n✓ Movement feels natural and effortless\n✓ Can express emotions through movement\n✓ Body feels restored, awakened, alive"
        }
    ]

    for task in phase4_tasks:
        try:
            manager.create_task(**task)
            tasks_created.append(task["content"][:50])
            print(f"  ✓ {task['content'][:60]}...")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # ============================================
    # WEEKLY REVIEW TASKS
    # ============================================
    print("\n📋 Weekly Review Tasks")

    weekly_reviews = [
        {
            "content": "📝 Weekly Reflection: Movement Flow progress check (Week 1)",
            "project": "fitness",
            "priority": "medium",
            "due_days": 7,
            "labels": ["routine"],
            "description": "Questions: 1) Which movements feel most natural? 2) Which need more attention? 3) Can I transition smoothly? 4) How does my body feel? 5) What variations did I discover?"
        },
        {
            "content": "📝 Monthly Deep Review: Record 5-min flow + analyze (Month 1)",
            "project": "fitness",
            "priority": "medium",
            "due_days": 28,
            "description": "Watch video without judgment. Notice: smoothness, creativity, joy. Celebrate progress! Schedule deep restoration: massage/foam rolling, extended stretching (30m), bath, rest day."
        }
    ]

    for task in weekly_reviews:
        try:
            manager.create_task(**task)
            tasks_created.append(task["content"][:50])
            print(f"  ✓ {task['content'][:60]}...")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # ============================================
    # SUMMARY
    # ============================================
    print(f"\n✅ Setup complete!")
    print(f"📊 Created {len(tasks_created)} tasks across 4 phases (16 weeks)")
    print(f"\n🎯 Your Movement Flow journey begins today!")
    print(f"📖 Reference document: /mnt/e/LifeOS/movement_flow_mastery_path.md")
    print(f"📚 Manual pages: Movement-Flow-Manual-Co-Edit.pdf")
    print(f"\n💡 Remember: Quality over quantity. Move with intention. Flow with joy. Restore with wisdom.")

    return tasks_created

if __name__ == "__main__":
    try:
        tasks = setup_movement_flow_schedule()
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)
