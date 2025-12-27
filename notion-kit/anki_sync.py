#!/usr/bin/env python3
"""
Notion to Anki 同步模块 (API 2025-09-03)

功能:
- 从 Notion 数据库查询未同步的卡片
- 使用 genanki 生成 .apkg 文件
- 通过 Telegram Bot 发送文件
- 更新 Notion 同步状态

使用方法:
    from notion_kit.anki_sync import AnkiSyncManager

    manager = AnkiSyncManager()
    manager.run()
"""

import os
import sys
import json
import hashlib
import requests
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# 导入 genanki
try:
    import genanki
except ImportError:
    print("❌ 缺少依赖: genanki")
    print("请运行: pip install genanki")
    sys.exit(1)

# 导入 notion_client
try:
    from notion_client import Client
    from notion_client.errors import APIResponseError
except ImportError:
    print("❌ 缺少依赖: notion-client")
    print("请运行: pip install notion-client")
    sys.exit(1)

# 默认路径配置（相对于本模块）
MODULE_DIR = Path(__file__).parent
DEFAULT_ENV_PATH = MODULE_DIR / ".env"
DEFAULT_CONFIG_PATH = MODULE_DIR / "anki_config.json"
DEFAULT_STATE_PATH = MODULE_DIR / "anki_state.json"
DEFAULT_OUTPUT_DIR = MODULE_DIR / "output"


class AnkiSyncManager:
    """Anki 同步管理器"""

    def __init__(
        self,
        dry_run: bool = False,
        env_path: Optional[Path] = None,
        config_path: Optional[Path] = None,
        state_path: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ):
        """
        初始化同步管理器

        Args:
            dry_run: 试运行模式（不实际更新 Notion 或发送 Telegram）
            env_path: .env 文件路径
            config_path: 配置文件路径
            state_path: 状态文件路径
            output_dir: 输出目录
        """
        self.dry_run = dry_run

        # 路径配置
        self.env_path = env_path or DEFAULT_ENV_PATH
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.state_path = state_path or DEFAULT_STATE_PATH
        self.output_dir = output_dir or DEFAULT_OUTPUT_DIR

        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 加载环境变量
        load_dotenv(self.env_path)

        # 加载配置和状态
        self.config = self._load_config()
        self.state = self._load_state()

        # 初始化 Notion 客户端
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.anki_database_id = os.getenv("ANKI_DATABASE_ID")
        self.cortex_database_id = os.getenv("DATABASE_ID")

        if not self.notion_token:
            raise ValueError("❌ 未找到 NOTION_TOKEN，请在 .env 中设置")

        # 使用 Notion API 2025-09-03
        self.notion = Client(auth=self.notion_token, notion_version="2025-09-03")

        # 获取 data_source_id
        if self.anki_database_id:
            self.anki_data_source_id = self._get_data_source_id(self.anki_database_id)
        else:
            self.anki_data_source_id = None

        if self.cortex_database_id:
            self.cortex_data_source_id = self._get_data_source_id(self.cortex_database_id)
        else:
            self.cortex_data_source_id = None

        # Telegram 配置
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # Anki 模型
        self.anki_model = self._create_anki_model()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        if not self.config_path.exists():
            return self._get_default_config()

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "anki": {
                "deck_prefix": "NotionKit",
                "model_name": "NotionKit Basic",
                "model_id": 1607392319,
                "default_deck": "General"
            },
            "telegram": {
                "enabled": True,
                "send_empty_report": False
            },
            "sync": {
                "update_notion_status": True,
                "generate_full_deck": False
            }
        }

    def _load_state(self) -> Dict:
        """加载同步状态"""
        if not self.state_path.exists():
            return {
                "last_sync": None,
                "synced_cards": {},
                "stats": {
                    "total_synced": 0,
                    "last_batch_count": 0
                }
            }

        with open(self.state_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_state(self):
        """保存同步状态"""
        if self.dry_run:
            print("   [Dry Run] 跳过保存状态")
            return

        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _get_data_source_id(self, database_id: str) -> str:
        """获取数据源 ID (API 2025-09-03)"""
        try:
            database = self.notion.databases.retrieve(database_id)
            data_sources = database.get("data_sources", [])

            if data_sources:
                return data_sources[0]["id"]
            else:
                return database_id
        except Exception as e:
            print(f"⚠️  获取 data_source_id 失败: {e}")
            return database_id

    def _create_anki_model(self) -> genanki.Model:
        """创建 Anki 卡片模型"""
        model_id = self.config["anki"]["model_id"]
        model_name = self.config["anki"]["model_name"]

        return genanki.Model(
            model_id,
            model_name,
            fields=[
                {'name': 'Front'},
                {'name': 'Back'},
                {'name': 'Source'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Front}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Back}}<br><small style="color: #888;">{{Source}}</small>',
                },
            ],
            css='''
            .card {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
                font-size: 20px;
                text-align: center;
                color: #333;
                background-color: #fff;
                padding: 20px;
            }
            .card hr {
                margin: 20px 0;
                border: none;
                border-top: 1px solid #ddd;
            }
            '''
        )

    def query_unsynced_cards(self) -> List[Dict]:
        """查询未同步的卡片"""
        print("🔍 查询未同步的卡片...")

        all_cards = []

        # 1. 查询 Anki Cards 数据库（Synced = false）
        if self.anki_data_source_id:
            anki_filter = {
                "property": "Synced",
                "checkbox": {"equals": False}
            }
            cards = self._query_database(
                self.anki_data_source_id,
                anki_filter,
                "Anki Cards"
            )
            all_cards.extend(cards)

        # 2. 查询 Cortex 数据库（Last Reviewed 为空）
        if self.cortex_data_source_id:
            cortex_filter = {
                "property": "Last Reviewed",
                "date": {"is_empty": True}
            }
            cards = self._query_database(
                self.cortex_data_source_id,
                cortex_filter,
                "Cortex"
            )
            all_cards.extend(cards)

        print(f"   总计找到 {len(all_cards)} 张未同步的卡片")
        return all_cards

    def _query_database(self, data_source_id: str, filter_obj: Dict, db_name: str) -> List[Dict]:
        """查询单个数据库"""
        try:
            url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"
            headers = {
                "Authorization": f"Bearer {self.notion_token}",
                "Content-Type": "application/json",
                "Notion-Version": "2025-09-03"
            }

            response = requests.post(
                url,
                headers=headers,
                json={"filter": filter_obj},
                timeout=30
            )

            if response.status_code != 200:
                print(f"   ⚠️  {db_name} 查询失败: {response.status_code}")
                return []

            data = response.json()
            cards = data.get("results", [])
            print(f"   从 {db_name} 找到 {len(cards)} 张卡片")
            return cards
        except Exception as e:
            print(f"   ⚠️  {db_name} 查询错误: {e}")
            return []

    def _extract_property(self, page: Dict, prop_name: str, prop_type: str) -> Optional[str]:
        """提取页面属性"""
        props = page.get("properties", {})
        prop = props.get(prop_name)

        if not prop:
            return None

        if prop_type == "title":
            titles = prop.get("title", [])
            return titles[0]["plain_text"] if titles else None
        elif prop_type == "rich_text":
            texts = prop.get("rich_text", [])
            return texts[0]["plain_text"] if texts else None
        elif prop_type == "select":
            select = prop.get("select")
            return select["name"] if select else None
        elif prop_type == "multi_select":
            items = prop.get("multi_select", [])
            return [item["name"] for item in items]
        elif prop_type == "url":
            return prop.get("url")
        elif prop_type == "checkbox":
            return prop.get("checkbox", False)

        return None

    def _is_cortex_card(self, page: Dict) -> bool:
        """判断是否为 Cortex 数据库的卡片"""
        props = page.get("properties", {})
        has_name = "Name" in props and props["Name"].get("type") == "title"
        has_type = "Type" in props and props["Type"].get("type") == "select"
        has_status = "Status" in props and props["Status"].get("type") == "select"
        return has_name and has_type and has_status

    def _get_page_content(self, page_id: str) -> str:
        """获取页面正文内容"""
        try:
            blocks = self.notion.blocks.children.list(page_id)
            content_parts = []

            for block in blocks.get("results", []):
                block_type = block.get("type")
                if block_type in ["paragraph", "bulleted_list_item", "numbered_list_item", "heading_1", "heading_2", "heading_3"]:
                    texts = block.get(block_type, {}).get("rich_text", [])
                    for text in texts:
                        content_parts.append(text.get("plain_text", ""))

            return "\n".join(content_parts).strip()
        except Exception as e:
            print(f"   ⚠️  获取页面内容失败 {page_id[:8]}: {e}")
            return ""

    def _convert_cortex_to_anki(self, page: Dict) -> tuple:
        """将 Cortex 条目转换为 Anki 卡片格式"""
        name = self._extract_property(page, "Name", "title")
        source = self._extract_property(page, "Source", "rich_text") or ""
        tags = self._extract_property(page, "Tags", "multi_select") or []
        page_id = page["id"]

        if not name:
            return None, None, None, None, None

        back = self._get_page_content(page_id)
        if not back:
            back = "（无内容）"

        front = name
        deck = "Vocabulary"

        # 处理不同类型的条目
        if name.startswith("翻译："):
            front = name.replace("翻译：", "").strip()
            deck = "Translation"
        elif name.startswith("单词："):
            front = name.replace("单词：", "").strip()
            deck = "Vocabulary"
        elif name.startswith("短语："):
            front = name.replace("短语：", "").strip()
            deck = "Phrases"

        if "Cortex" not in tags:
            tags.append("Cortex")

        return front, back, deck, source, tags

    def generate_anki_guid(self, notion_page_id: str) -> int:
        """从 Notion Page ID 生成稳定的 Anki GUID"""
        hash_hex = hashlib.md5(notion_page_id.encode()).hexdigest()
        return int(hash_hex[:15], 16)

    def create_anki_package(self, cards: List[Dict]) -> Optional[str]:
        """创建 Anki .apkg 文件"""
        if not cards:
            print("⚠️  没有卡片需要同步")
            return None

        print(f"📦 生成 Anki 包...")

        decks = {}
        deck_prefix = self.config["anki"]["deck_prefix"]

        for page in cards:
            if self._is_cortex_card(page):
                front, back, deck_name, source, tags = self._convert_cortex_to_anki(page)
                if not front or not back:
                    print(f"   ⏭️  跳过: Cortex 卡片转换失败")
                    continue
            else:
                front = self._extract_property(page, "Front", "title")
                back = self._extract_property(page, "Back", "rich_text")
                deck_name = self._extract_property(page, "Deck", "select")
                source = self._extract_property(page, "Source", "url") or ""
                tags = self._extract_property(page, "Tags", "multi_select") or []

                if not front or not back:
                    print(f"   ⏭️  跳过: 缺少 Front 或 Back")
                    continue

            full_deck_name = f"{deck_prefix}::{deck_name}" if deck_name else deck_prefix

            if full_deck_name not in decks:
                deck_id = abs(hash(full_deck_name)) % (10 ** 10)
                decks[full_deck_name] = genanki.Deck(deck_id, full_deck_name)

            guid = self.generate_anki_guid(page["id"])

            note = genanki.Note(
                model=self.anki_model,
                fields=[front, back, source],
                guid=guid,
                tags=tags
            )

            decks[full_deck_name].add_note(note)
            print(f"   ✓ {front[:30]}... → {full_deck_name}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"anki_sync_{timestamp}.apkg"

        package = genanki.Package(list(decks.values()))
        package.write_to_file(str(output_file))

        print(f"✅ Anki 包已生成: {output_file}")
        print(f"   包含 {len(decks)} 个牌组，共 {len(cards)} 张卡片")

        return str(output_file)

    def send_to_telegram(self, file_path: str, card_count: int) -> bool:
        """发送 .apkg 文件到 Telegram"""
        if not self.config["telegram"]["enabled"]:
            print("⏭️  Telegram 发送已禁用")
            return False

        if not self.telegram_token or not self.telegram_chat_id:
            print("⚠️  Telegram 未配置，跳过发送")
            return False

        if self.dry_run:
            print(f"   [Dry Run] 跳过发送到 Telegram: {file_path}")
            return True

        print("📤 发送到 Telegram...")

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendDocument"
        caption = f"🎴 Anki 卡片同步\n\n📊 本次同步: {card_count} 张\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    url,
                    files={'document': f},
                    data={'chat_id': self.telegram_chat_id, 'caption': caption},
                    timeout=30
                )

            if response.status_code == 200:
                print("✅ 已发送到 Telegram")
                return True
            else:
                print(f"❌ Telegram 发送失败: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Telegram 发送错误: {e}")
            return False

    def update_notion_sync_status(self, cards: List[Dict]):
        """更新 Notion 中的同步状态"""
        if not self.config["sync"]["update_notion_status"]:
            print("⏭️  跳过更新 Notion 状态")
            return

        if self.dry_run:
            print(f"   [Dry Run] 跳过更新 Notion 状态 ({len(cards)} 张卡片)")
            return

        print(f"📝 更新 Notion 同步状态...")

        today = datetime.now().strftime("%Y-%m-%d")

        for page in cards:
            page_id = page["id"]
            try:
                if self._is_cortex_card(page):
                    self.notion.pages.update(
                        page_id=page_id,
                        properties={
                            "Status": {"select": {"name": "Learning"}},
                            "Last Reviewed": {"date": {"start": today}}
                        }
                    )
                else:
                    self.notion.pages.update(
                        page_id=page_id,
                        properties={
                            "Synced": {"checkbox": True},
                            "Last Synced": {"date": {"start": today}}
                        }
                    )
                print(f"   ✓ 已更新: {page_id[:8]}...")
            except APIResponseError as e:
                print(f"   ❌ 更新失败 {page_id[:8]}: {e}")

        print(f"✅ 已更新 {len(cards)} 张卡片的同步状态")

    def run(self):
        """执行同步流程"""
        print("=" * 60)
        print("  Notion → Anki 同步")
        if self.dry_run:
            print("  [试运行模式 - 不会实际修改数据]")
        print("=" * 60)
        print()

        cards = self.query_unsynced_cards()

        if not cards:
            print("✅ 没有新卡片需要同步")
            return

        print()

        apkg_file = self.create_anki_package(cards)

        if not apkg_file:
            print("❌ Anki 包生成失败")
            return

        print()

        self.send_to_telegram(apkg_file, len(cards))

        print()

        self.update_notion_sync_status(cards)

        self.state["last_sync"] = datetime.now().isoformat()
        self.state["stats"]["total_synced"] += len(cards)
        self.state["stats"]["last_batch_count"] = len(cards)
        self._save_state()

        print()
        print("=" * 60)
        print("🎉 同步完成！")
        print(f"   本次同步: {len(cards)} 张")
        print(f"   总计同步: {self.state['stats']['total_synced']} 张")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Notion to Anki 同步工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m notion_kit.anki_sync
  python -m notion_kit.anki_sync --dry-run
        """
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行模式，不实际修改 Notion 或发送 Telegram'
    )

    args = parser.parse_args()

    try:
        manager = AnkiSyncManager(dry_run=args.dry_run)
        manager.run()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
