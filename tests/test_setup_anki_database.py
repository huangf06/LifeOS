import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.setup_anki_database import build_database_schema


def test_build_database_schema_uses_initial_data_source_properties():
    schema = build_database_schema("parent-page-id")

    assert schema["parent"] == {"type": "page_id", "page_id": "parentpageid"}
    assert "properties" not in schema
    assert schema["initial_data_source"]["name"] == "Anki Cards"

    properties = schema["initial_data_source"]["properties"]
    assert properties["Front"] == {"title": {}}
    assert properties["Back"] == {"rich_text": {}}
    assert properties["Deck"]["select"]["options"][0]["name"] == "Vocabulary"
    assert properties["Tags"]["multi_select"]["options"][0]["name"] == "English"
    assert properties["Source"] == {"url": {}}
    assert properties["Synced"] == {"checkbox": {}}
    assert properties["Last Synced"] == {"date": {}}
