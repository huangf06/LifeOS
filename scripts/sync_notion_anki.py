#!/usr/bin/env python3
"""
Notion to Anki 同步脚本 (API 2025-09-03)

功能:
- 从 Notion "Anki Cards" 数据库查询未同步的卡片
- 使用 genanki 生成 .apkg 文件
- 通过 Telegram Bot 发送文件
- 更新 Notion 同步状态
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

# 加载环境变量
env_path = Path(__file__).parent.parent / "notion-kit" / ".env"
load_dotenv(env_path)

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent / "config" / "anki_sync_config.json"
STATE_FILE = Path(__file__).parent.parent / "data" / "anki_sync_state.json"
OUTPUT_DIR = Path(__file__).parent.parent / "data"

# 确保输出目录存在
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class AnkiSyncManager:
    """Anki 同步管理器"""

    def __init__(self, dry_run=False):
        """
        初始化同步管理器

        Args:
            dry_run: 是否为试运行模式（不实际更新 Notion 或发送 Telegram）
        """
        self.dry_run = dry_run
        self.config = self._load_config()
        self.state = self._load_state()

        # 初始化 Notion 客户端
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.anki_database_id = os.getenv("ANKI_DATABASE_ID")

        if not self.notion_token:
            raise ValueError("❌ 未找到 NOTION_TOKEN，请在 notion-kit/.env 中设置")
        if not self.anki_database_id:
            raise ValueError("❌ 未找到 ANKI_DATABASE_ID，请运行: python3 scripts/setup_anki_database.py")

        # 使用 Notion API 2025-09-03
        self.notion = Client(auth=self.notion_token, notion_version="2025-09-03")

        # 获取 data_source_id
        self.data_source_id = self._get_data_source_id()

        # Telegram 配置
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # Anki 模型
        self.anki_model = self._create_anki_model()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        if not CONFIG_FILE.exists():
            print(f"⚠️  配置文件不存在: {CONFIG_FILE}")
            return self._get_default_config()

        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "anki": {
                "deck_prefix": "LifeOS",
                "model_name": "LifeOS Basic",
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
        if not STATE_FILE.exists():
            return {
                "last_sync": None,
                "synced_cards": {},
                "stats": {
                    "total_synced": 0,
                    "last_batch_count": 0
                }
            }

        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_state(self):
        """保存同步状态"""
        if self.dry_run:
            print("   [Dry Run] 跳过保存状态")
            return

        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _get_data_source_id(self) -> str:
        """获取数据源 ID (API 2025-09-03)"""
        try:
            database = self.notion.databases.retrieve(self.anki_database_id)
            data_sources = database.get("data_sources", [])

            if data_sources:
                return data_sources[0]["id"]
            else:
                # 如果没有 data_sources，直接使用 database_id
                return self.anki_database_id
        except Exception as e:
            print(f"⚠️  获取 data_source_id 失败: {e}")
            return self.anki_database_id

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

        # 简化过滤器：只查询 Synced = false 或未设置（默认为 false）
        filter_obj = {
            "property": "Synced",
            "checkbox": {
                "equals": False
            }
        }

        try:
            # API 2025-09-03: 使用 data_sources 端点
            url = f"https://api.notion.com/v1/data_sources/{self.data_source_id}/query"
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

            # 打印详细错误信息（如果有）
            if response.status_code != 200:
                print(f"   API 响应: {response.status_code}")
                print(f"   错误详情: {response.text}")

            response.raise_for_status()

            data = response.json()
            cards = data.get("results", [])
            print(f"   找到 {len(cards)} 张未同步的卡片")
            return cards
        except requests.exceptions.RequestException as e:
            print(f"❌ 查询失败: {e}")
            return []
        except Exception as e:
            print(f"❌ 查询错误: {e}")
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

    def generate_anki_guid(self, notion_page_id: str) -> str:
        """从 Notion Page ID 生成稳定的 Anki GUID"""
        hash_hex = hashlib.md5(notion_page_id.encode()).hexdigest()
        # genanki 要求 GUID 是整数
        return int(hash_hex[:15], 16)

    def create_anki_package(self, cards: List[Dict]) -> Optional[str]:
        """创建 Anki .apkg 文件"""
        if not cards:
            print("⚠️  没有卡片需要同步")
            return None

        print(f"📦 生成 Anki 包...")

        # 按 Deck 分组
        decks = {}
        deck_prefix = self.config["anki"]["deck_prefix"]

        for page in cards:
            # 提取卡片信息
            front = self._extract_property(page, "Front", "title")
            back = self._extract_property(page, "Back", "rich_text")
            deck_name = self._extract_property(page, "Deck", "select")
            source = self._extract_property(page, "Source", "url") or ""
            tags = self._extract_property(page, "Tags", "multi_select") or []

            # 验证必填字段
            if not front or not back:
                print(f"   ⏭️  跳过: 缺少 Front 或 Back")
                continue

            # 构建完整 Deck 名称
            full_deck_name = f"{deck_prefix}::{deck_name}" if deck_name else deck_prefix

            # 创建 Deck（如果不存在）
            if full_deck_name not in decks:
                deck_id = abs(hash(full_deck_name)) % (10 ** 10)
                decks[full_deck_name] = genanki.Deck(deck_id, full_deck_name)

            # 生成 Note GUID
            guid = self.generate_anki_guid(page["id"])

            # 创建 Note
            note = genanki.Note(
                model=self.anki_model,
                fields=[front, back, source],
                guid=guid,
                tags=tags
            )

            decks[full_deck_name].add_note(note)
            print(f"   ✓ {front[:30]}... → {full_deck_name}")

        # 生成 .apkg 文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = OUTPUT_DIR / f"anki_sync_{timestamp}.apkg"

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
            print("   设置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID 环境变量")
            return False

        if self.dry_run:
            print(f"   [Dry Run] 跳过发送到 Telegram: {file_path}")
            return True

        print("📤 发送到 Telegram...")

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendDocument"

        caption = f"🎴 Anki 卡片同步\n\n📊 本次同步: {card_count} 张\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        try:
            with open(file_path, 'rb') as f:
                files = {'document': f}
                data = {
                    'chat_id': self.telegram_chat_id,
                    'caption': caption
                }
                response = requests.post(url, files=files, data=data, timeout=30)

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

        # 1. 查询未同步的卡片
        cards = self.query_unsynced_cards()

        if not cards:
            if self.config["telegram"]["send_empty_report"]:
                print("📭 没有新卡片，发送空报告")
                # TODO: 发送空报告
            else:
                print("✅ 没有新卡片需要同步")
            return

        print()

        # 2. 生成 Anki 包
        apkg_file = self.create_anki_package(cards)

        if not apkg_file:
            print("❌ Anki 包生成失败")
            return

        print()

        # 3. 发送到 Telegram
        self.send_to_telegram(apkg_file, len(cards))

        print()

        # 4. 更新 Notion 状态
        self.update_notion_sync_status(cards)

        # 5. 更新本地状态
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
  # 正常同步
  python3 scripts/sync_notion_anki.py

  # 试运行（不修改数据）
  python3 scripts/sync_notion_anki.py --dry-run

  # 或通过 lifeos 命令
  ./lifeos sync-anki
  ./lifeos sync-anki --dry-run
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
