#!/usr/bin/env python3
"""
清理 Notion Anki Cards 数据库中的重复卡片

问题: Eudic sync 在 CI 中每天重复添加全部单词，导致数据库中有大量重复卡片。
策略: 对于同名卡片，保留最早创建的一张，删除（archive）其余重复卡片。
"""

import os
import sys
import time
import requests
import argparse
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / "notion-kit" / ".env"
load_dotenv(env_path)

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
ANKI_DATABASE_ID = os.getenv("ANKI_DATABASE_ID")


def get_data_source_id(token, database_id):
    """获取 data_source_id"""
    from notion_client import Client
    notion = Client(auth=token, notion_version="2025-09-03")
    db = notion.databases.retrieve(database_id)
    sources = db.get("data_sources", [])
    return sources[0]["id"] if sources else database_id


def fetch_all_cards(token, data_source_id, filter_obj=None):
    """获取所有卡片（分页，带重试）"""
    url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2025-09-03"
    }

    all_cards = []
    start_cursor = None
    page = 0

    while True:
        page += 1
        body = {"page_size": 100}
        if filter_obj:
            body["filter"] = filter_obj
        if start_cursor:
            body["start_cursor"] = start_cursor

        resp = None
        for attempt in range(5):
            timeout = 120 * (attempt + 1)  # 120s, 240s, 360s, 480s, 600s
            try:
                resp = requests.post(url, headers=headers, json=body, timeout=timeout)
                if resp.status_code == 200:
                    break
                if resp.status_code in (502, 504) and attempt < 4:
                    wait = 5 * (attempt + 1)
                    print(f"   ⚠️  {resp.status_code} 错误，{wait}秒后重试 ({attempt+1}/5)...")
                    time.sleep(wait)
                    continue
                print(f"   ❌ 查询失败: {resp.status_code}")
                return all_cards
            except requests.exceptions.RequestException as e:
                if attempt < 4:
                    wait = 5 * (attempt + 1)
                    print(f"   ⚠️  请求失败，{wait}秒后重试 ({attempt+1}/5): {e}")
                    time.sleep(wait)
                    continue
                print(f"   ❌ 请求失败: {e}")
                return all_cards

        if not resp or resp.status_code != 200:
            return all_cards

        data = resp.json()
        results = data.get("results", [])
        all_cards.extend(results)
        print(f"   第{page}页: 获取 {len(results)} 张 (累计 {len(all_cards)})")

        if data.get("has_more") and data.get("next_cursor"):
            start_cursor = data["next_cursor"]
        else:
            break

    return all_cards


def find_duplicates(cards):
    """找出重复卡片，按 Front 标题分组"""
    by_title = defaultdict(list)

    for card in cards:
        props = card.get("properties", {})
        front = props.get("Front", {})
        titles = front.get("title", [])
        title = titles[0].get("plain_text", "") if titles else ""

        if title:
            by_title[title].append(card)

    # 找出有重复的
    duplicates_to_delete = []
    for title, group in by_title.items():
        if len(group) > 1:
            # 按创建时间排序，保留最早的
            group.sort(key=lambda c: c.get("created_time", ""))
            keep = group[0]
            to_delete = group[1:]
            duplicates_to_delete.extend(to_delete)

    return duplicates_to_delete, by_title


def archive_pages(token, page_ids, dry_run=False):
    """归档（软删除）页面"""
    from notion_client import Client
    notion = Client(auth=token, notion_version="2025-09-03")

    success = 0
    failed = 0

    for i, page_id in enumerate(page_ids, 1):
        if dry_run:
            if i <= 5:
                print(f"   [DRY RUN] 将删除: {page_id[:8]}...")
            continue

        try:
            notion.pages.update(page_id=page_id, archived=True)
            success += 1
            if i % 50 == 0:
                print(f"   已删除 {i}/{len(page_ids)}...")
                time.sleep(0.5)  # 避免 rate limit
        except Exception as e:
            failed += 1
            if failed <= 3:
                print(f"   ❌ 删除失败 {page_id[:8]}: {e}")

    return success, failed


def main():
    parser = argparse.ArgumentParser(description="清理 Notion Anki Cards 重复卡片")
    parser.add_argument("--dry-run", action="store_true", help="试运行，不实际删除")
    args = parser.parse_args()

    if not NOTION_TOKEN or not ANKI_DATABASE_ID:
        print("❌ 缺少 NOTION_TOKEN 或 ANKI_DATABASE_ID")
        sys.exit(1)

    print("=" * 50)
    print("🧹 清理 Notion Anki Cards 重复卡片")
    if args.dry_run:
        print("   [试运行模式]")
    print("=" * 50)

    # 1. 获取 data_source_id
    ds_id = get_data_source_id(NOTION_TOKEN, ANKI_DATABASE_ID)
    print(f"\n📦 Data Source ID: {ds_id[:8]}...")

    # 2. 获取欧路标签的卡片（重复的主要来源）
    print("\n🔍 获取「欧路」标签的卡片...")
    eudic_filter = {
        "property": "Tags",
        "multi_select": {"contains": "欧路"}
    }
    cards = fetch_all_cards(NOTION_TOKEN, ds_id, filter_obj=eudic_filter)
    print(f"\n   总计: {len(cards)} 张「欧路」卡片")

    # 3. 找出重复
    print("\n🔎 分析重复...")
    to_delete, by_title = find_duplicates(cards)
    unique_count = len(by_title)
    dup_groups = sum(1 for g in by_title.values() if len(g) > 1)

    print(f"   唯一标题: {unique_count}")
    print(f"   有重复的标题: {dup_groups}")
    print(f"   需要删除的重复卡片: {len(to_delete)}")

    if not to_delete:
        print("\n✅ 没有重复卡片，无需清理")
        return

    # 4. 删除重复
    print(f"\n🗑️  {'[DRY RUN] ' if args.dry_run else ''}删除 {len(to_delete)} 张重复卡片...")
    ids = [c["id"] for c in to_delete]
    success, failed = archive_pages(NOTION_TOKEN, ids, dry_run=args.dry_run)

    if args.dry_run:
        print(f"\n   [DRY RUN] 将删除 {len(to_delete)} 张重复卡片")
    else:
        print(f"\n✅ 清理完成: 成功 {success}, 失败 {failed}")

    print("=" * 50)


if __name__ == "__main__":
    main()
