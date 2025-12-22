#!/usr/bin/env python3
"""
创建 Anki Cards 数据库
自动在 Notion 中创建符合规范的 Anki 卡片数据库

用法:
  python3 scripts/setup_anki_database.py [PARENT_PAGE_ID]

如果不提供 PARENT_PAGE_ID，将在工作区根目录创建
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError

# 加载环境变量
env_path = Path(__file__).parent.parent / "notion-kit" / ".env"
load_dotenv(env_path)

def create_anki_database(parent_page_id=None):
    """创建 Anki Cards 数据库

    Args:
        parent_page_id: 父页面 ID（可选）
    """

    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        print("❌ 未找到 NOTION_TOKEN")
        print("请在 notion-kit/.env 中设置 NOTION_TOKEN")
        sys.exit(1)

    # 使用 Notion API 2025-09-03 (最新版本)
    notion = Client(auth=notion_token, notion_version="2025-09-03")

    print("🔨 正在创建 Anki Cards 数据库...")
    print()

    # 数据库结构
    database_schema = {
        "parent": {},
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "Anki Cards"
                }
            }
        ],
        "properties": {
            "Front": {
                "title": {}
            },
            "Back": {
                "rich_text": {}
            },
            "Deck": {
                "select": {
                    "options": [
                        {"name": "Vocabulary", "color": "blue"},
                        {"name": "Concept", "color": "purple"},
                        {"name": "Translation", "color": "green"},
                        {"name": "Code", "color": "orange"},
                        {"name": "General", "color": "gray"}
                    ]
                }
            },
            "Tags": {
                "multi_select": {
                    "options": [
                        {"name": "English", "color": "blue"},
                        {"name": "Quant", "color": "red"},
                        {"name": "Programming", "color": "orange"},
                        {"name": "Daily", "color": "green"}
                    ]
                }
            },
            "Source": {
                "url": {}
            },
            "Synced": {
                "checkbox": {}
            },
            "Last Synced": {
                "date": {}
            }
        }
    }

    # 询问用户父页面 ID（如果没有提供）
    if parent_page_id:
        # 移除可能的连字符
        parent_page_id = parent_page_id.replace("-", "")
        database_schema["parent"] = {
            "type": "page_id",
            "page_id": parent_page_id
        }
        print(f"📍 使用父页面 ID: {parent_page_id}")
    else:
        # 使用工作区根目录
        print("📍 将在工作区根目录创建数据库")
        print("   (如需指定父页面，运行: python3 scripts/setup_anki_database.py <PAGE_ID>)")
        database_schema["parent"] = {"type": "workspace", "workspace": True}

    print()

    try:
        response = notion.databases.create(**database_schema)
        database_id = response["id"]
        database_url = response["url"]

        print()
        print("✅ 数据库创建成功!")
        print()
        print("=" * 60)
        print(f"数据库名称: Anki Cards")
        print(f"数据库 ID: {database_id}")
        print(f"数据库 URL: {database_url}")
        print("=" * 60)
        print()

        # 自动保存到 .env
        try:
            with open(env_path, 'r') as f:
                content = f.read()

            # 添加 ANKI_DATABASE_ID
            if "ANKI_DATABASE_ID" not in content:
                content += f"\n# Anki Cards 数据库 ID\nANKI_DATABASE_ID={database_id}\n"

                with open(env_path, 'w') as f:
                    f.write(content)

                print("✅ 已自动保存到 notion-kit/.env")
            else:
                print("⚠️  .env 中已存在 ANKI_DATABASE_ID，请手动更新")
        except Exception as e:
            print(f"⚠️  无法保存到 .env: {e}")

        print()
        print("🎯 下一步:")
        print("1. 访问数据库 URL，确认字段结构正确")
        print("2. 手动添加 2-3 张测试卡片")
        print("3. 运行同步脚本测试: ./lifeos sync-anki")
        print()

        return database_id

    except APIResponseError as e:
        print(f"❌ 创建失败: {e}")
        print()
        print("可能的原因:")
        print("- Parent Page ID 不正确")
        print("- Notion Integration 没有权限访问该页面")
        print("- 需要在 Notion 中将 Integration 添加到父页面")
        print()
        print("解决方案:")
        print("1. 打开父页面")
        print("2. 点击右上角 '...' → 'Add connections'")
        print("3. 选择你的 Integration")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="创建 Notion Anki Cards 数据库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 在工作区根目录创建
  python3 scripts/setup_anki_database.py

  # 在指定页面下创建
  python3 scripts/setup_anki_database.py 1234567890abcdef1234567890abcdef

获取 Parent Page ID:
  1. 在 Notion 中打开想要放置数据库的页面
  2. 点击 '...' → 'Copy link'
  3. 从 URL 提取: https://www.notion.so/xxx/{PAGE_ID}?v=...
        """
    )
    parser.add_argument(
        'parent_page_id',
        nargs='?',
        default=None,
        help='父页面 ID (可选，不提供则在工作区根目录创建)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  Anki Cards 数据库创建工具")
    print("=" * 60)
    print()

    create_anki_database(args.parent_page_id)
