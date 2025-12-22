#!/usr/bin/env python3
"""
LifeOS Knowledge Gardener (知识园丁)
Deep Work & Spaced Repetition System

Philosophy:
    - Knowledge is a stream, not a static pond.
    - We don't "memorize"; we "resurface" to strengthen neural pathways.
    - Friction must be zero. The prompt comes to you (Todoist).
    - Reviewing > Collecting.

Mechanism:
    - Scans `knowledge/` folder for Markdown files.
    - Implements Fibonacci Spaced Repetition (1, 2, 3, 5, 8, 13...). 
    - Pushes "Review Tasks" to Todoist.
    - Tracks completion by monitoring Todoist task disappearance (Snapshot Diff).
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Ensure we can import from the same directory
script_dir = Path(__file__).parent
sys.path.append(str(script_dir))

from todoist_manager import TodoistManager

# --- Configuration ---
BASE_DIR = script_dir.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
DATA_DIR = BASE_DIR / "data"
STATE_FILE = DATA_DIR / "review_state.json"
ACTIVE_TASKS_FILE = DATA_DIR / "active_reviews.json"

# Fibonacci intervals (Days)
INTERVALS = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
MAX_DAILY_REVIEWS = 3  # Cap to prevent burnout

class KnowledgeGardener:
    def __init__(self):
        self.tm = TodoistManager()
        self.state = self._load_json(STATE_FILE)
        self.active_map = self._load_json(ACTIVE_TASKS_FILE)
        
        # Ensure directories exist
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path: Path) -> Dict:
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_json(self, path: Path, data: Dict):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _get_file_content_preview(self, file_path: Path) -> str:
        """Extracts a preview of the file for the task description."""
        try:
            lines = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for _ in range(10):
                    line = f.readline()
                    if not line: break
                    line = line.strip()
                    if line and not line.startswith('#'): # Skip headers in preview if possible, or keep them
                        lines.append(line)
            return "\n".join(lines[:3]) + "..." if lines else "No content preview."
        except Exception:
            return "Unable to read file."

    def _get_all_knowledge_files(self) -> List[Path]:
        """Recursively finds all .md files in knowledge dir."""
        return list(KNOWLEDGE_DIR.rglob("*.md"))

    def sync(self):
        """Main execution logic."""
        print("🌱 Knowledge Gardener: Syncing...")
        
        # 1. Update status of currently active reviews
        self._check_completions()
        
        # 2. Scan for new files and clean up deleted ones
        self._scan_library()
        
        # 3. Schedule new reviews
        self._schedule_reviews()
        
        # 4. Save state
        self._save_json(STATE_FILE, self.state)
        self._save_json(ACTIVE_TASKS_FILE, self.active_map)
        print("✅ Sync Complete.")

    def _check_completions(self):
        """Checks if active tasks in Todoist are completed (gone)."""
        if not self.active_map:
            return

        print("🔍 Checking active tasks...")
        # Fetch current tasks from Todoist
        # We assume if a task ID was in active_map but is NOT in current tasks, it's done.
        current_tasks = self.tm.get_all_tasks()
        current_ids = set(t.id for t in current_tasks)
        
        completed_files = []
        
        # Iterate over a copy of keys
        for file_path_str, task_id in list(self.active_map.items()):
            if task_id not in current_ids:
                # Task is gone -> Completed!
                print(f"🎉 Review Completed: {Path(file_path_str).name}")
                self._promote_item(file_path_str)
                completed_files.append(file_path_str)
            else:
                # Task still active -> Skip
                pass
                
        # Remove completed from active map
        for f in completed_files:
            del self.active_map[f]

    def _promote_item(self, file_path_str: str):
        """Moves an item to the next spaced repetition stage."""
        if file_path_str not in self.state:
            self.state[file_path_str] = {"stage": 0, "last_review": None}
            
        item = self.state[file_path_str]
        current_stage = item.get("stage", 0)
        
        # Update last review date
        item["last_review"] = datetime.now().strftime("%Y-%m-%d")
        
        # Increment stage
        new_stage = current_stage + 1
        item["stage"] = new_stage
        
        # Calculate next review date
        interval = INTERVALS[min(new_stage, len(INTERVALS) - 1)]
        next_date = datetime.now() + timedelta(days=interval)
        item["next_review"] = next_date.strftime("%Y-%m-%d")
        
        print(f"   📈 Promoted to Stage {new_stage} (Next review: +{interval} days)")

    def _scan_library(self):
        """Registers new files and cleans up deleted ones."""
        files = self._get_all_knowledge_files()
        file_paths_str = set(str(f) for f in files)
        
        # Add new files
        for f_str in file_paths_str:
            if f_str not in self.state:
                print(f"🆕 Found new knowledge: {Path(f_str).name}")
                # Initialize at stage -1 so first review is scheduled for today/tomorrow
                self.state[f_str] = {
                    "stage": 0, 
                    "last_review": None,
                    "next_review": datetime.now().strftime("%Y-%m-%d") # Due immediately
                }
                
        # Remove deleted files
        for f_str in list(self.state.keys()):
            if f_str not in file_paths_str:
                print(f"🗑️  File removed, cleaning state: {Path(f_str).name}")
                del self.state[f_str]
                if f_str in self.active_map:
                    # Note: We don't delete the Todoist task here, we just forget about it.
                    del self.active_map[f_str]

    def _schedule_reviews(self):
        """Pushes tasks to Todoist for items due for review."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Find candidates
        candidates = []
        for f_str, data in self.state.items():
            # Skip if already active
            if f_str in self.active_map:
                continue
                
            next_review = data.get("next_review", "1970-01-01")
            if next_review <= today_str:
                candidates.append(f_str)
                
        # Sort by "overdue amount" (lexicographical comparison of YYYY-MM-DD works)
        candidates.sort(key=lambda x: self.state[x]["next_review"])
        
        # Limit daily volume
        to_schedule = candidates[:MAX_DAILY_REVIEWS]
        
        if not to_schedule:
            print("💤 No reviews due today.")
            return

        print(f"🚀 Scheduling {len(to_schedule)} reviews...")
        
        for f_str in to_schedule:
            path = Path(f_str)
            preview = self._get_file_content_preview(path)
            
            # Construct meaningful content
            # Try to get H1 from file, else filename
            title = path.stem.replace("_", " ").replace("-", " ").title()
            
            # Create Task
            print(f"   Posting: {title}")
            task = self.tm.create_task(
                content=f"🧠 Review: {title}",
                description=f"{preview}\n\nPath: `{path.name}`",
                project="fitness", # Using 'fitness' or 'default' project for now, ideally 'Knowledge'
                labels=["review"],
                priority="high" # P2
            )
            
            if task:
                self.active_map[f_str] = task.id

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(__doc__)
        return

    gardener = KnowledgeGardener()
    gardener.sync()

if __name__ == "__main__":
    main()
