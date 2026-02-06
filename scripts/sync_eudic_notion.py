#!/usr/bin/env python3
"""
欧路词典生词本同步到 Notion Anki Cards 脚本

功能:
- 从欧路词典 API 获取生词本
- 将生词添加到 Notion "Anki Cards" 数据库
- 自动标记已同步的单词，避免重复
- 支持批量同步和增量同步
"""

import os
import sys
import json
import hashlib
import requests
import argparse
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# 导入 notion_client
try:
    from notion_client import Client
    from notion_client.errors import APIResponseError
    from httpx import HTTPStatusError
except ImportError:
    print("❌ 缺少依赖: notion-client")
    print("请运行: pip install notion-client")
    sys.exit(1)

# 加载环境变量
env_path = Path(__file__).parent.parent / "notion-kit" / ".env"
load_dotenv(env_path)

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent / "config" / "eudic_config.json"
STATE_FILE = Path(__file__).parent.parent / "data" / "eudic_sync_state.json"

# 确保 data 目录存在
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


def retry_on_502(max_retries=3, delay=2):
    """
    装饰器：在遇到 502 Bad Gateway 错误时自动重试

    Args:
        max_retries: 最大重试次数
        delay: 每次重试间隔（秒）
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (APIResponseError, HTTPStatusError) as e:
                    last_exception = e
                    # 检查是否是 502 错误
                    status_code = None
                    if hasattr(e, 'status'):
                        status_code = e.status
                    elif hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                        status_code = e.response.status_code

                    if status_code == 502 and attempt < max_retries:
                        wait_time = delay * (2 ** attempt)  # 指数退避
                        print(f"   ⚠️  Notion API 502 错误，{wait_time}秒后重试 ({attempt + 1}/{max_retries})...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise
            raise last_exception
        return wrapper
    return decorator


class EudicSyncManager:
    """欧路词典同步管理器"""

    def __init__(self, dry_run=False, limit=None):
        """
        初始化同步管理器

        Args:
            dry_run: 是否为试运行模式（不实际写入 Notion）
            limit: 限制同步单词数量（None 表示不限制）
        """
        self.dry_run = dry_run
        self.limit = limit
        self.config = self._load_config()
        self.state = self._load_state()

        # 欧路词典 API 配置
        self.eudic_token = os.getenv("EUDIC_TOKEN") or self.config.get("api_token")
        self.api_base_url = self.config.get("api_base_url", "https://api.frdic.com/api/open/v1")

        if not self.eudic_token:
            raise ValueError("❌ 未找到欧路词典 API Token，请设置 EUDIC_TOKEN 环境变量或在 config/eudic_config.json 中配置")

        # Notion 配置
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.anki_database_id = os.getenv("ANKI_DATABASE_ID")

        if not self.notion_token:
            raise ValueError("❌ 未找到 NOTION_TOKEN，请在 notion-kit/.env 中设置")
        if not self.anki_database_id:
            raise ValueError("❌ 未找到 ANKI_DATABASE_ID，请运行: ./lifeos setup-anki")

        # 初始化 Notion 客户端 (API 2025-09-03)
        self.notion = Client(auth=self.notion_token, notion_version="2025-09-03")
        self.data_source_id = self._get_data_source_id(self.anki_database_id)

        # 同步配置
        self.sync_settings = self.config.get("sync_settings", {})
        self.notion_mapping = self.config.get("notion_mapping", {})
        self.filters = self.config.get("filters", {})

    def _load_config(self) -> Dict:
        """加载配置文件"""
        if not CONFIG_FILE.exists():
            raise FileNotFoundError(f"❌ 配置文件不存在: {CONFIG_FILE}")

        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_state(self) -> Dict:
        """加载同步状态"""
        if not STATE_FILE.exists():
            return {
                "last_sync": None,
                "synced_words": [],
                "total_synced": 0
            }

        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_state(self):
        """保存同步状态"""
        self.state["last_sync"] = datetime.now().isoformat()

        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

        print(f"✓ 同步状态已保存: {STATE_FILE}")

    def _get_data_source_id(self, database_id: str) -> str:
        """从数据库 ID 获取数据源 ID"""
        try:
            database = self.notion.databases.retrieve(database_id)
            data_sources = database.get("data_sources", [])

            if not data_sources:
                return database_id

            return data_sources[0]["id"]
        except Exception as e:
            print(f"⚠️  获取 data_source_id 失败，使用 database_id: {e}")
            return database_id

    def fetch_vocabulary(self, page=1, page_size=50) -> List[Dict]:
        """
        从欧路词典 API 获取生词本

        Args:
            page: 页码（从 1 开始）
            page_size: 每页数量

        Returns:
            生词列表
        """
        language = self.sync_settings.get("language", "en")
        studylist_id = self.sync_settings.get("studylist_id", "0")

        url = f"{self.api_base_url}/studylist/words/{studylist_id}"
        headers = {
            "Authorization": self.eudic_token,
            "User-Agent": "LifeOS/1.0"
        }
        params = {
            "language": language,
            "page": str(page),
            "page_size": str(page_size)
        }

        try:
            print(f"🔍 正在获取欧路词典生词本 (第 {page} 页)...")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            words = data.get("data", [])

            print(f"✓ 获取到 {len(words)} 个单词")
            return words

        except requests.exceptions.RequestException as e:
            print(f"❌ 获取欧路词典生词失败: {e}")
            if hasattr(e.response, 'text'):
                print(f"   错误详情: {e.response.text}")
            return []

    def fetch_all_vocabulary(self) -> List[Dict]:
        """
        获取所有生词（自动分页）

        Returns:
            完整的生词列表
        """
        all_words = []
        page = 1
        page_size = self.sync_settings.get("page_size", 50)

        while True:
            words = self.fetch_vocabulary(page=page, page_size=page_size)

            if not words:
                break

            all_words.extend(words)

            # 如果返回的单词数少于 page_size，说明已经是最后一页
            if len(words) < page_size:
                break

            page += 1

        print(f"\n✓ 总计获取到 {len(all_words)} 个单词")
        return all_words

    def filter_new_words(self, words: List[Dict]) -> List[Dict]:
        """
        过滤已同步的单词

        Args:
            words: 完整单词列表

        Returns:
            未同步的新单词列表
        """
        synced_words = set(self.state.get("synced_words", []))
        new_words = [w for w in words if w.get("word") not in synced_words]

        print(f"📊 已同步: {len(synced_words)} | 新单词: {len(new_words)}")
        return new_words

    def word_to_notion_card(self, word_data: Dict) -> Dict:
        """
        将欧路词典单词转换为 Notion 卡片格式

        Args:
            word_data: 欧路词典单词数据

        Returns:
            Notion 页面属性
        """
        word = word_data.get("word", "")

        # 提取释义 (exp 字段)
        exp = word_data.get("exp", "")

        # 提取音标
        phonetic = word_data.get("phonetic", "")

        # 构建卡片背面（释义 + 音标）
        back_content = exp
        if phonetic:
            back_content = f"[{phonetic}]\n\n{exp}"

        # 提取标签
        auto_tags = self.notion_mapping.get("auto_add_tags", [])
        deck_name = self.notion_mapping.get("deck_name", "欧路词典")

        # 构建 Notion 属性
        properties = {
            "Front": {
                "title": [{"text": {"content": word}}]
            },
            "Back": {
                "rich_text": [{"text": {"content": back_content}}]
            },
            "Deck": {
                "select": {"name": deck_name}
            },
            "Tags": {
                "multi_select": [{"name": tag} for tag in auto_tags]
            },
            "Synced": {
                "checkbox": False
            }
        }

        return properties

    @retry_on_502(max_retries=3, delay=2)
    def add_to_notion(self, word_data: Dict) -> bool:
        """
        将单词添加到 Notion Anki Cards 数据库

        Args:
            word_data: 欧路词典单词数据

        Returns:
            是否成功
        """
        word = word_data.get("word", "")

        if self.dry_run:
            print(f"   [DRY RUN] 将添加: {word}")
            return True

        try:
            properties = self.word_to_notion_card(word_data)

            # API 2025-09-03: 使用 data_source_id 作为 parent
            page_data = {
                "parent": {"data_source_id": self.data_source_id},
                "properties": properties
            }

            self.notion.pages.create(**page_data)
            print(f"   ✓ 已添加: {word}")
            return True

        except APIResponseError as e:
            print(f"   ❌ 添加失败 ({word}): {e}")
            return False

    def sync(self) -> Dict[str, int]:
        """
        执行完整同步流程

        Returns:
            同步统计信息
        """
        print("=" * 50)
        print("📚 欧路词典 → Notion Anki Cards 同步")
        print("=" * 50)

        if self.dry_run:
            print("⚠️  试运行模式：不会实际写入 Notion\n")

        # 1. 获取所有生词
        all_words = self.fetch_all_vocabulary()

        if not all_words:
            print("⚠️  没有找到生词，退出同步")
            return {"total": 0, "new": 0, "success": 0, "failed": 0}

        # 2. 过滤已同步的单词
        new_words = self.filter_new_words(all_words)

        if not new_words:
            print("\n✓ 所有单词已同步，无需更新")
            return {"total": len(all_words), "new": 0, "success": 0, "failed": 0}

        # 3. 应用限制（如果设置了）
        if self.limit and self.limit > 0:
            original_count = len(new_words)
            new_words = new_words[:self.limit]
            print(f"⚠️  限制模式：只同步前 {self.limit} 个单词（共 {original_count} 个新单词）\n")

        # 4. 同步到 Notion
        print(f"🔄 开始同步 {len(new_words)} 个新单词...\n")

        success_count = 0
        failed_count = 0

        for i, word_data in enumerate(new_words, 1):
            word = word_data.get("word", "")
            print(f"[{i}/{len(new_words)}] {word}")

            try:
                if self.add_to_notion(word_data):
                    success_count += 1
                    # 标记为已同步
                    if "synced_words" not in self.state:
                        self.state["synced_words"] = []
                    self.state["synced_words"].append(word)
                else:
                    failed_count += 1
            except Exception as e:
                print(f"   ❌ 添加失败 ({word}): {e}")
                failed_count += 1
                # 继续处理下一个单词，不中断流程

        # 4. 保存状态
        self.state["total_synced"] = self.state.get("total_synced", 0) + success_count

        if not self.dry_run:
            self._save_state()

        # 5. 打印统计
        print("\n" + "=" * 50)
        print("✅ 同步完成")
        print("=" * 50)
        print(f"总单词数: {len(all_words)}")
        print(f"新单词数: {len(new_words)}")
        print(f"成功: {success_count}")
        print(f"失败: {failed_count}")
        print(f"累计同步: {self.state.get('total_synced', 0)}")
        print("=" * 50)

        return {
            "total": len(all_words),
            "new": len(new_words),
            "success": success_count,
            "failed": failed_count
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="欧路词典生词本同步到 Notion")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="试运行模式（不实际写入 Notion）"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="限制同步单词数量（用于测试）"
    )
    args = parser.parse_args()

    try:
        manager = EudicSyncManager(dry_run=args.dry_run, limit=args.limit)
        manager.sync()

    except Exception as e:
        print(f"\n❌ 同步失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
