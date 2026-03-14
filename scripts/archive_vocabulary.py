#!/usr/bin/env python3
"""批量归档 Notion Anki Cards 中的欧路词典卡片（并发版）"""
import os, requests, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from pathlib import Path
from notion_client import Client

load_dotenv(Path(__file__).parent.parent / "notion-kit" / ".env")
TOKEN = os.getenv("NOTION_TOKEN")
DB_ID = os.getenv("ANKI_DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2025-09-03",
}

notion = Client(auth=TOKEN, notion_version="2025-09-03")
db = notion.databases.retrieve(DB_ID)
DS_ID = db.get("data_sources", [{}])[0].get("id", DB_ID)
URL = f"https://api.notion.com/v1/data_sources/{DS_ID}/query"

print(f"Data source: {DS_ID[:12]}...", flush=True)


def archive_page(page_id):
    """归档单个页面（用 requests 直接调用，避免 SDK 锁）"""
    for attempt in range(3):
        try:
            r = requests.patch(
                f"https://api.notion.com/v1/pages/{page_id}",
                headers=HEADERS,
                json={"archived": True},
                timeout=30,
            )
            if r.status_code == 200:
                return True
            if r.status_code == 429:
                time.sleep(1)
                continue
            time.sleep(1)
        except Exception:
            time.sleep(1)
    return False


def query_batch():
    """查询一批未归档的欧路卡片"""
    filter_obj = {"property": "Tags", "multi_select": {"contains": "欧路"}}
    for attempt in range(5):
        try:
            resp = requests.post(
                URL, headers=HEADERS,
                json={"filter": filter_obj, "page_size": 100},
                timeout=300,
            )
            if resp.status_code == 200:
                return resp.json().get("results", [])
            print(f"  query [{resp.status_code}]", end=" ", flush=True)
            time.sleep(10 * (attempt + 1))
        except Exception as e:
            print(f"  query err", end=" ", flush=True)
            time.sleep(10 * (attempt + 1))
    return None


total = 0
batch = 0

while True:
    batch += 1
    print(f"Batch {batch}: querying...", end=" ", flush=True)

    pages = query_batch()
    if pages is None:
        print(f"\nQuery failed. Archived so far: {total}", flush=True)
        break
    if not pages:
        print(f"empty.\nDone! Total archived: {total}", flush=True)
        break

    print(f"got {len(pages)}, archiving...", end=" ", flush=True)

    # 并发归档（10 线程）
    ok = 0
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(archive_page, p["id"]): p["id"] for p in pages}
        for f in as_completed(futures):
            if f.result():
                ok += 1

    total += ok
    print(f"done ({ok}/{len(pages)}, total: {total})", flush=True)
