#!/usr/bin/env python3
"""
Clean up Movement Flow tasks from Todoist
Removes all Movement Flow related tasks
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.todoist_manager import TodoistManager

def cleanup_movement_flow_tasks():
    """Delete all Movement Flow related tasks"""

    manager = TodoistManager()
    print("🧹 Cleaning up Movement Flow tasks from Todoist...\n")

    # Get all tasks - handle paginator
    tasks = []
    for page in manager.api.get_tasks():
        tasks.extend(page)

    # Keywords to identify Movement Flow tasks
    keywords = [
        "Movement Flow",
        "Ground Connection",
        "Expanding Range",
        "Dynamic Movement Patterns",
        "Building Complexity",
        "Inversions & Kicks",
        "Mastery Integration",
        "Pattern Internalization",
        "Ultimate Freedom",
        "Checkpoint",
        "Weekly Reflection",
        "Monthly Deep Review",
        "Slide Up",
        "Hip Roll",
        "Sliding Split",
        "Official Flow"
    ]

    deleted_count = 0

    for task in tasks:
        # Handle both dict and object types
        if isinstance(task, dict):
            content = task.get('content', '')
            description = task.get('description', '')
            task_id = task.get('id')
        else:
            content = task.content
            description = task.description if hasattr(task, 'description') else ""
            task_id = task.id

        # Check if task contains any Movement Flow keywords
        if any(keyword in content or keyword in description for keyword in keywords):
            try:
                manager.api.delete_task(task_id)
                print(f"  ✓ Deleted: {content[:70]}...")
                deleted_count += 1
            except Exception as e:
                print(f"  ✗ Error deleting task: {e}")

    print(f"\n✅ Cleanup complete! Deleted {deleted_count} Movement Flow tasks.")
    return deleted_count

if __name__ == "__main__":
    try:
        cleanup_movement_flow_tasks()
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        sys.exit(1)
