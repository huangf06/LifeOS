# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

**LifeOS** is a personal GTD (Getting Things Done) system with Todoist integration. The system enables natural language task creation, automated project management, and comprehensive life tracking.

---

## Quick Commands

```bash
# Todoist Task Management
./lifeos 'your task description'    # Natural language task creation
./lifeos setup                       # Setup Todoist API Token
./lifeos test                        # Test Todoist connection
./lifeos setup-goals                 # Quick setup for fitness/career/English goals
./lifeos fitness                     # Send workout plan
./lifeos export-tasks                # Export all tasks to JSON
./lifeos list-tasks                  # List all tasks

# Life Tracking (Logseq Integration)
./lifeos today                       # Initialize today's journal
./lifeos log work 'content' 8 '2h'  # Log activity
./lifeos report                      # Generate weekly report
./lifeos sync                        # Git sync Logseq

# AI Advisor
./lifeos analyze                     # Analyze life patterns
./lifeos plan                        # Generate optimized plans
```

---

## Core Components

### 1. Todoist Manager (`scripts/todoist_manager.py`)
Full-featured Todoist API integration:
- Create/manage tasks, projects, and labels
- Batch task operations
- Data export for analysis
- Pre-configured fitness/career/English templates

**Key Features:**
- Direct REST API integration (no email required)
- Cross-platform sync (Windows, Mac, iPhone, Android)
- Full programmatic control via Python
- Habit tracking and recurring tasks

### 2. Personal Assistant (`scripts/personal_assistant.py`)
Natural language task processing:
- Parse user input into structured tasks
- Auto-categorize by project and priority
- Estimate task duration
- Send to Todoist via API

### 3. Goals Setup (`scripts/setup_goals.py`)
Quick initialization for three major goals:
- **Fitness (work-out)**: 6 workout tasks
- **Career (job-hunt)**: 8 job search tasks
- **English (speak-up)**: 10 learning tasks

### 4. Logseq Tracker (`scripts/logseq_tracker.py`)
Daily journaling and life tracking:
- Template-based journal initialization
- Activity logging with ratings
- Weekly report generation
- Git synchronization

### 5. AI Advisor (`scripts/ai_advisor.py`)
Pattern analysis and recommendations:
- Analyze historical data from Logseq
- Generate optimization suggestions
- Create personalized plans

---

## Configuration Files

- `config/todoist_config.json` - Todoist API settings and project mappings
- `config/assistant_profile.json` - Assistant behavior configuration
- `config/logseq_templates.json` - Logseq journal templates

### Todoist Project Mapping

```json
{
  "fitness": "work-out",    // Workout and fitness
  "career": "job-hunt",     // Job searching
  "english": "speak-up",    // English learning
  "work": "work",           // General work
  "study": "study",         // Study tasks
  "life": "life",           // Life tasks
  "other": "other"          // Miscellaneous
}
```

### Labels

- `urgent` - Urgent tasks (red)
- `important` - Important tasks (orange)
- `routine` - Daily routines (grey)
- `habit` - Habit formation (green)

---

## Project Structure

```
LifeOS/
├── lifeos                        # Main entry point
├── CLAUDE.md                     # This file
├── TODOIST_QUICKSTART.md         # User quickstart guide
├── README.md                     # Project readme
│
├── scripts/
│   ├── todoist_manager.py        # Todoist API core
│   ├── personal_assistant.py     # NLP task parser
│   ├── setup_goals.py            # Goal templates
│   ├── logseq_tracker.py         # Life tracking
│   └── ai_advisor.py             # AI recommendations
│
├── config/
│   ├── todoist_config.json       # Todoist settings
│   ├── assistant_profile.json    # Assistant config
│   └── logseq_templates.json     # Journal templates
│
├── data/                         # Local data storage
├── schedule_management/          # Schedule tracking
└── career/                       # Career documents

```

---

## Python Dependencies

```bash
pip install todoist-api-python    # Official Todoist SDK
```

**Standard libraries used:**
- `json`, `os`, `sys`, `pathlib` - System operations
- `datetime`, `statistics` - Data processing
- `subprocess`, `argparse` - CLI operations

---

## Integration Points

### Todoist API
- **Authentication**: Bearer token in `config/todoist_config.json`
- **API Version**: REST API v2
- **Endpoint**: `https://api.todoist.com/rest/v2`
- **Features**: Projects, labels, priorities, due dates, recurring tasks

### Logseq
- **Path**: `/root/Documents/logseq/`
- **Format**: Markdown-based daily journals
- **Sync**: Git version control

---

## Workflow Examples

### Creating Tasks

**Natural language:**
```bash
./lifeos '明天要准备面试资料和更新简历'
# Parses into 2 tasks, assigns to job-hunt project
```

**Python API:**
```python
from scripts.todoist_manager import TodoistManager

manager = TodoistManager()
manager.create_task(
    content="Morning workout",
    project="fitness",    # Maps to "work-out"
    priority="high",      # P1 in Todoist
    due_days=0,           # Today
    labels=["habit"]      # Add habit label
)
```

### Batch Task Creation

```python
tasks = [
    {"name": "Task 1", "project": "career", "priority": "high"},
    {"name": "Task 2", "project": "english", "priority": "medium"}
]
manager.create_tasks_batch(tasks)
```

### Goal Setup

```bash
# All three goals at once
python3 scripts/setup_goals.py --all

# Individual goals
python3 scripts/setup_goals.py --goal fitness
python3 scripts/setup_goals.py --goal career
python3 scripts/setup_goals.py --goal english
```

### Data Export

```bash
# Export to JSON
./lifeos export-tasks

# File location: ~/LifeOS/data/todoist_export_YYYYMMDD_HHMMSS.json
```

---

## Testing

```bash
# Test Todoist connection
./lifeos test

# Should output:
# ✅ 连接成功！
#    项目数: 4
#    标签数: 4
#    任务数: X
```

---

## Development Guidelines

### For Claude Code

1. **Task Management**:
   - Use TodoWrite to track multi-step tasks
   - Proactively send tasks to Todoist when appropriate
   - Prioritize action over explanation

2. **Project Tools First**:
   - Use `todoist_manager.py` for task operations
   - Use `personal_assistant.py` for NLP parsing
   - Avoid external tools when project tools exist

3. **Todoist Integration**:
   - All task operations go through Todoist API
   - No email/AppleScript methods
   - Cross-platform compatibility is key

4. **Data Privacy**:
   - API tokens stored in `config/todoist_config.json`
   - Never commit tokens to git
   - Use `.gitignore` for sensitive data

---

## Priority Mapping

```
high   → 4 (P1 - Urgent)
medium → 2 (P2 - Normal)
low    → 1 (P3 - Low)
```

---

## Key Permissions

The system has permissions for:
- Python script execution
- Todoist API access (requires API Token)
- File operations in project and Logseq directories
- Git operations for version control
- Web searches for specific domains

---

## Important Features

- **Cross-Platform**: Works on Windows, Mac, iPhone, Android, Web
- **API Integration**: Full programmatic control via Python
- **Data Export**: Export tasks to JSON for analysis
- **Goal Templates**: Pre-configured for fitness, career, English
- **Habit Tracking**: Built-in support for recurring tasks
- **Natural Language**: Parse user descriptions into structured tasks
- **Life Tracking**: Integrate with Logseq for journaling

---

## Support

- **Documentation**: `./lifeos help`
- **Quickstart**: See `TODOIST_QUICKSTART.md`
- **API Docs**: https://developer.todoist.com/rest/v2/
- **Todoist SDK**: https://github.com/Doist/todoist-api-python

---

**Last Updated**: 2025-01-14
