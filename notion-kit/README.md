# Notion Kit

Portable Notion API wrapper for Python projects. Ready to copy & paste.

## Quick Start

```bash
# 1. Copy this folder to your project
cp -r notion-kit /path/to/your-project/

# 2. Install dependencies
pip install -r notion-kit/requirements.txt

# 3. Configure environment
cp notion-kit/.env.example notion-kit/.env
# Edit .env with your credentials
```

## Usage

### Basic Operations

```python
from notion_kit.notion_wrap import NotionWrapper

notion = NotionWrapper()

# Add a note
notion.add_task(
    name="Key concept learned",
    task_type="Note",       # Note/Vocabulary/Concept/Code Snippet/Example
    note="Detailed content...",
    tags=["Python", "AI"],
    priority="High"         # High/Medium/Low
)

# Query this week's entries
results = notion.query_current_week()

# Update task status
notion.update_task(
    page_id="page-id-here",
    status="Learning",
    last_reviewed=True
)

# Get page content
content = notion.get_page_content("page-id-here")
```

### Property Extraction

```python
# Extract values from Notion page objects
for page in notion.query_database():
    name = notion.extract_property_value(page, "Name")
    tags = notion.extract_property_value(page, "Tags")
    status = notion.extract_property_value(page, "Status")
```

## Configuration

### Environment Variables (.env)

```bash
# Required
NOTION_TOKEN=ntn_xxx           # From: https://www.notion.so/my-integrations
DATABASE_ID=xxx                # Main database ID

# Optional (for Anki sync)
ANKI_DATABASE_ID=xxx           # Anki Cards database ID

# Optional (for Telegram notifications)
TELEGRAM_BOT_TOKEN=xxx         # From @BotFather
TELEGRAM_CHAT_ID=xxx           # From @userinfobot
```

### Getting Database ID

From Notion URL:
```
https://www.notion.so/workspace/DATABASE_ID?v=...
                        ^^^^^^^^^^^^
                        Copy this part
```

## API Version

Uses **Notion API 2025-09-03** (latest) with:
- `data_source_id` support for multi-source databases
- Rate limiting with exponential backoff
- Automatic retry on failures

## Dependencies

- `notion-client` - Official Notion SDK
- `python-dotenv` - Environment variable management
- `requests` - HTTP requests (for Telegram)
- `genanki` - Anki package generation (optional)

## License

MIT
