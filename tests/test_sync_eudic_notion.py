import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.sync_eudic_notion import EudicSyncManager


def test_filter_new_words_excludes_state_and_existing_notion_titles():
    manager = EudicSyncManager.__new__(EudicSyncManager)
    manager.state = {"synced_words": ["alpha", "beta"]}
    manager._fetch_existing_notion_titles = lambda: {"gamma"}

    words = [
        {"word": "alpha"},
        {"word": "beta"},
        {"word": "gamma"},
        {"word": "delta"},
    ]

    new_words = manager.filter_new_words(words)

    assert new_words == [{"word": "delta"}]
