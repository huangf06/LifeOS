#!/usr/bin/env python3
"""
LifeOS CLI Flashcards (The "Terminal Anki")
Deep Work & Spaced Repetition System

Features:
    - Parses Markdown files for "Q:" and "A:" blocks.
    - Implements the SuperMemo-2 (SM-2) Algorithm.
    - Stores progress in a clean JSON file.
    - Interactive CLI interface.
"""

import os
import sys
import json
import re
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# --- Configuration ---
BASE_DIR = Path(__file__).parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
DATA_DIR = BASE_DIR / "data"
PROGRESS_FILE = DATA_DIR / "flashcard_progress.json"

class Flashcard:
    def __init__(self, question: str, answer: str, source_file: str, context: str = ""):
        self.question = question
        self.answer = answer
        self.source_file = source_file
        self.context = context
        # Unique ID based on question content (simple hash for persistence)
        self.id = hex(hash(f"{source_file}:{question}"))[2:]

class SM2:
    """
    SuperMemo-2 Algorithm Implementation
    """
    @staticmethod
    def calculate(quality: int, repetitions: int, ease_factor: float, interval: int):
        """
        Args:
            quality: 0-5 (User rating)
            repetitions: consecutive successful reviews
            ease_factor: difficulty multiplier (starts at 2.5)
            interval: days until next review
        Returns:
            (new_repetitions, new_ease_factor, new_interval)
        """
        if quality >= 3:
            if repetitions == 0:
                interval = 1
            elif repetitions == 1:
                interval = 6
            else:
                interval = int(interval * ease_factor)
            
            repetitions += 1
        else:
            repetitions = 0
            interval = 1
        
        # EF calculation
        new_ef = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if new_ef < 1.3:
            new_ef = 1.3
            
        return repetitions, new_ef, interval

class CardManager:
    def __init__(self):
        self.progress = self._load_progress()
        self.cards = []
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _load_progress(self) -> Dict:
        if PROGRESS_FILE.exists():
            try:
                with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_progress(self):
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)

    def scan_cards(self):
        """Scans all MD files for Q/A pairs."""
        self.cards = []
        files = list(KNOWLEDGE_DIR.rglob("*.md"))
        
        qa_pattern = re.compile(r'^Q:\s*(.*?)\nA:\s*(.*?)(?=\n\n|\nQ:|$)', re.DOTALL | re.MULTILINE)
        
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
                # Find current H1 or H2 for context
                # Simple context: Filename
                context = file_path.stem.replace('_', ' ').title()
                
                matches = qa_pattern.findall(content)
                for q, a in matches:
                    self.cards.append(Flashcard(
                        question=q.strip(),
                        answer=a.strip(),
                        source_file=str(file_path),
                        context=context
                    ))
            except Exception as e:
                print(f"⚠️  Error reading {file_path.name}: {e}")

    def get_due_cards(self) -> List[Flashcard]:
        due = []
        today = datetime.now().date()
        
        for card in self.cards:
            if card.id not in self.progress:
                # New card
                due.append(card)
            else:
                data = self.progress[card.id]
                next_review = datetime.strptime(data['next_review'], "%Y-%m-%d").date()
                if next_review <= today:
                    due.append(card)
        
        # Sort: New cards mixed with review cards
        random.shuffle(due)
        return due

    def review_loop(self):
        self.scan_cards()
        due_cards = self.get_due_cards()
        
        if not due_cards:
            print("\n🎉 All caught up! No cards due for review today.\n")
            return

        print(f"\n📚 Session Started: {len(due_cards)} cards due.\n")
        
        for i, card in enumerate(due_cards, 1):
            print(f"--- Card {i}/{len(due_cards)} ---")
            print(f"📍 Context: {card.context}")
            print(f"\n❓ Q: {card.question}\n")
            
            input("Press [Enter] to show answer...")
            
            print(f"\n💡 A: {card.answer}\n")
            
            while True:
                print("Rating: [1] Again (Fail)  [2] Hard  [3] Good  [4] Easy")
                try:
                    choice = input("Select > ").strip()
                    if choice in ['1', '2', '3', '4']:
                        rating = int(choice)
                        # Map 1-4 to SM-2's 0-5 scale roughly
                        # 1 (Fail) -> 0
                        # 2 (Hard) -> 3
                        # 3 (Good) -> 4
                        # 4 (Easy) -> 5
                        quality_map = {1: 0, 2: 3, 3: 4, 4: 5}
                        quality = quality_map[rating]
                        self._update_card(card.id, quality)
                        break
                except KeyboardInterrupt:
                    print("\nSession paused.")
                    return

    def _update_card(self, card_id: str, quality: int):
        data = self.progress.get(card_id, {
            "repetitions": 0,
            "ease_factor": 2.5,
            "interval": 0,
            "next_review": datetime.now().strftime("%Y-%m-%d")
        })
        
        reps, ef, interval = SM2.calculate(
            quality, 
            data["repetitions"], 
            data["ease_factor"], 
            data["interval"]
        )
        
        next_date = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d")
        
        self.progress[card_id] = {
            "repetitions": reps,
            "ease_factor": ef,
            "interval": interval,
            "next_review": next_date,
            "last_review": datetime.now().strftime("%Y-%m-%d")
        }
        self._save_progress()
        print(f"   [Next review in {interval} days]")

if __name__ == "__main__":
    app = CardManager()
    try:
        app.review_loop()
    except KeyboardInterrupt:
        print("\nExiting...")
