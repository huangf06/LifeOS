# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Commands

### Personal Assistant System
```bash
# Main entry point - intelligent task planning with natural language
./lifeos 'your task description'

# Email and task management
python3 scripts/email_sender.py setup     # Configure email account
python3 scripts/email_sender.py test      # Test email sending
python3 scripts/email_sender.py fitness   # Send fitness plan

# Life tracking and journaling
python3 scripts/logseq_tracker.py init    # Initialize today's template
python3 scripts/logseq_tracker.py log --category work --content "task description" --rating 8 --duration 2h
python3 scripts/logseq_tracker.py report  # Generate weekly report
python3 scripts/logseq_tracker.py sync    # Git sync Logseq

# AI advisor
python3 scripts/ai_advisor.py analyze     # Analyze life patterns
python3 scripts/ai_advisor.py plan        # Generate optimized plans

# Personal assistant direct access
python3 scripts/personal_assistant.py "task description"
python3 scripts/personal_assistant.py --stats
```

## Repository Architecture

**LifeOS** is a personal digital life management system designed for GTD (Getting Things Done) and comprehensive life tracking. The system integrates with external tools like OmniFocus for task management and Logseq for knowledge management.

### Key Components

1. **Personal Assistant (`scripts/personal_assistant.py`)**
   - Natural language task processing
   - Automatic task categorization and priority assignment
   - Integration with OmniFocus via email gateway
   - Task history tracking and statistics

2. **Email Integration (`scripts/email_sender.py`)**
   - SMTP-based task sending to OmniFocus
   - Template-based email generation
   - Support for fitness plans and task notifications

3. **Logseq Integration (`scripts/logseq_tracker.py`)**
   - Daily journal template creation
   - Activity logging with ratings and duration
   - Data tracking (mood, energy, productivity)
   - Weekly report generation
   - Git synchronization for version control

4. **AI Advisor (`scripts/ai_advisor.py`)**
   - Pattern analysis from Logseq data
   - Life optimization recommendations
   - Planning assistance based on historical data

### Configuration Files

- `config/assistant_profile.json`: Assistant identity and behavior configuration
- `config/email_templates.json`: Email templates for different task types
- `config/logseq_templates.json`: Logseq journal templates

### Directory Structure

- `scripts/`: Core Python scripts for various functionalities
- `config/`: System configuration files
- `data/`: Data storage (if exists)
- `schedule_management/`: Schedule tracking and management
  - `adjustments/`: Schedule adjustment triggers
  - `logs/`: Daily logs and reports
  - `plans/`: Master schedules and printable versions
  - `tracking/`: Daily tracking templates
  - `versions/`: Version control for schedules

## Development Guidelines

### Assistant Behavior
When working with this codebase, Claude should act as defined in `config/assistant_profile.json`:
- Proactively create and track tasks using TodoWrite
- Automatically send tasks to OmniFocus when appropriate
- Prioritize action over explanation
- Use project tools before external solutions

### Python Dependencies
The project uses standard Python libraries:
- smtplib, email.mime for email functionality
- json, os, sys for system operations
- datetime, statistics for data processing
- subprocess for system commands
- argparse for CLI interfaces
- pathlib for file operations

### Integration Points
- **OmniFocus**: Tasks are sent via email to mail drop address
- **Logseq**: Direct file manipulation in `/root/Documents/logseq/`
- **Git**: Automatic version control for Logseq data

### Testing Commands
```bash
# Test email configuration
python3 scripts/email_sender.py test

# Test personal assistant
./lifeos 'test task for tomorrow'

# Check assistant statistics
./lifeos stats
```

## Working with the System

### Task Management Flow
1. User provides natural language task description
2. Personal assistant parses and structures the task
3. Task is sent to OmniFocus via email
4. Task history is logged locally

### Life Tracking Flow
1. Initialize daily template with `logseq_tracker.py init`
2. Log activities throughout the day
3. Update data points (mood, energy, etc.)
4. Generate weekly reports for insights
5. Sync with Git for backup

### Key Permissions
The system has permissions for:
- Python script execution
- Email sending via SMTP
- File operations in project and Logseq directories
- Git operations for version control
- Web searches and fetches for specific domains