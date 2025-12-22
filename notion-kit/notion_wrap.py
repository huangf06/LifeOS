#!/usr/bin/env python3
"""Notion API 封装模块 - 用于 Cortex 知识管理系统"""

import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError

# 加载环境变量
load_dotenv()

class NotionWrapper:
    """Notion API 封装类 - 使用 Notion API 2025-09-03"""

    def __init__(self, api_version="2025-09-03"):
        """
        初始化 Notion 客户端

        Args:
            api_version: Notion API 版本 (默认 2025-09-03，最新版本)
        """
        self.notion = Client(
            auth=os.getenv("NOTION_TOKEN"),
            notion_version=api_version
        )
        self.database_id = os.getenv("DATABASE_ID")

        if not self.database_id:
            raise ValueError("DATABASE_ID 未在 .env 中设置")

        # API 2025-09-03: 使用 data_source_id 替代 database_id
        # 自动获取第一个数据源 ID
        self.data_source_id = self._get_data_source_id(self.database_id)

    def _get_data_source_id(self, database_id: str) -> str:
        """
        从数据库 ID 获取数据源 ID

        Args:
            database_id: 数据库 ID

        Returns:
            数据源 ID（单数据源数据库返回第一个）
        """
        try:
            database = self.notion.databases.retrieve(database_id)
            data_sources = database.get("data_sources", [])

            if not data_sources:
                # 如果没有 data_sources 字段，可能是旧版本，直接返回 database_id
                return database_id

            # 返回第一个数据源 ID
            return data_sources[0]["id"]
        except Exception as e:
            print(f"⚠️  获取 data_source_id 失败，使用 database_id: {e}")
            return database_id

    def _retry_on_rate_limit(self, func, *args, max_retries=3, **kwargs):
        """处理速率限制，自动重试"""
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except APIResponseError as e:
                if e.code == "rate_limited" and attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"⚠️  速率限制，等待 {wait_time}s 后重试...")
                    time.sleep(wait_time)
                else:
                    raise

    def query_database(self,
                      filter_obj: Optional[Dict] = None,
                      sorts: Optional[List[Dict]] = None) -> List[Dict]:
        """
        查询数据库 (API 2025-09-03)

        Args:
            filter_obj: Notion 过滤器对象
            sorts: 排序规则列表

        Returns:
            查询结果列表
        """
        try:
            params = {"database_id": self.data_source_id}
            if filter_obj:
                params["filter"] = filter_obj
            if sorts:
                params["sorts"] = sorts

            response = self._retry_on_rate_limit(
                self.notion.databases.query,
                **params
            )
            return response.get("results", [])
        except APIResponseError as e:
            print(f"❌ 查询失败: {e}")
            return []

    def add_task(self,
                 name: str,
                 task_type: str = "Note",
                 status: str = "New",
                 tags: Optional[List[str]] = None,
                 priority: Optional[str] = None,
                 source: Optional[str] = None,
                 note: Optional[str] = None,
                 auto_created: bool = False) -> Optional[Dict]:
        """
        添加任务到数据库 (API 2025-09-03)

        Args:
            name: 任务名称
            task_type: 类型 (Note/Vocabulary/Concept/Code Snippet/Example/Daily Summary)
            status: 状态 (New/Learning/Mastered/Archived)
            tags: 标签列表
            priority: 优先级 (High/Medium/Low)
            source: 来源
            note: 笔记内容
            auto_created: 是否自动创建

        Returns:
            创建的页面对象，失败返回 None
        """
        try:
            # 计算当前周次
            now = datetime.now()
            week = now.strftime("%Y-W%V")

            # 构建属性
            properties = {
                "Name": {"title": [{"text": {"content": name}}]},
            }

            # 添加可选属性
            if task_type:
                properties["Type"] = {"select": {"name": task_type}}

            if status:
                properties["Status"] = {"select": {"name": status}}

            if tags:
                properties["Tags"] = {"multi_select": [{"name": tag} for tag in tags]}

            if priority:
                properties["Priority"] = {"select": {"name": priority}}

            if source:
                properties["Source"] = {"rich_text": [{"text": {"content": source}}]}

            properties["Week"] = {"rich_text": [{"text": {"content": week}}]}
            properties["Auto Created"] = {"checkbox": auto_created}

            # 构建页面内容
            children = []
            if note:
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": note}}]
                    }
                })

            # API 2025-09-03: 使用 data_source_id 作为 parent
            page_data = {
                "parent": {"data_source_id": self.data_source_id},
                "properties": properties,
            }

            if children:
                page_data["children"] = children

            response = self._retry_on_rate_limit(
                self.notion.pages.create,
                **page_data
            )

            print(f"✓ 已添加: {name}")
            return response

        except APIResponseError as e:
            print(f"❌ 添加任务失败: {e}")
            return None

    def update_task(self,
                   page_id: str,
                   status: Optional[str] = None,
                   tags: Optional[List[str]] = None,
                   priority: Optional[str] = None,
                   last_reviewed: bool = False) -> Optional[Dict]:
        """
        更新任务属性

        Args:
            page_id: 页面 ID
            status: 新状态
            tags: 新标签列表
            priority: 新优先级
            last_reviewed: 是否更新 Last Reviewed 为今天

        Returns:
            更新后的页面对象，失败返回 None
        """
        try:
            properties = {}

            if status:
                properties["Status"] = {"select": {"name": status}}

            if tags:
                properties["Tags"] = {"multi_select": [{"name": tag} for tag in tags]}

            if priority:
                properties["Priority"] = {"select": {"name": priority}}

            if last_reviewed:
                today = datetime.now().strftime("%Y-%m-%d")
                properties["Last Reviewed"] = {"date": {"start": today}}

            response = self._retry_on_rate_limit(
                self.notion.pages.update,
                page_id=page_id,
                properties=properties
            )

            print(f"✓ 已更新页面: {page_id[:8]}...")
            return response

        except APIResponseError as e:
            print(f"❌ 更新任务失败: {e}")
            return None

    def append_note(self, page_id: str, text: str) -> bool:
        """
        向页面追加段落

        Args:
            page_id: 页面 ID
            text: 要追加的文本

        Returns:
            成功返回 True，失败返回 False
        """
        try:
            self._retry_on_rate_limit(
                self.notion.blocks.children.append,
                block_id=page_id,
                children=[{
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": text}}]
                    }
                }]
            )
            print(f"✓ 已追加内容到页面: {page_id[:8]}...")
            return True

        except APIResponseError as e:
            print(f"❌ 追加内容失败: {e}")
            return False

    def get_page_content(self, page_id: str) -> str:
        """
        获取页面的文本内容

        Args:
            page_id: 页面 ID

        Returns:
            页面文本内容
        """
        try:
            blocks = self._retry_on_rate_limit(
                self.notion.blocks.children.list,
                block_id=page_id
            )

            content = []
            for block in blocks.get("results", []):
                if block["type"] == "paragraph":
                    texts = block["paragraph"]["rich_text"]
                    content.append("".join([t["plain_text"] for t in texts]))

            return "\n".join(content)

        except APIResponseError as e:
            print(f"❌ 获取页面内容失败: {e}")
            return ""

    def query_yesterday(self) -> List[Dict]:
        """查询昨天创建的所有条目"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")

        filter_obj = {
            "and": [
                {
                    "property": "Created",
                    "created_time": {
                        "on_or_after": yesterday
                    }
                },
                {
                    "property": "Created",
                    "created_time": {
                        "before": today
                    }
                },
                {
                    "property": "Auto Created",
                    "checkbox": {
                        "equals": False
                    }
                }
            ]
        }

        return self.query_database(filter_obj=filter_obj)

    def query_current_week(self) -> List[Dict]:
        """查询本周创建的所有条目（不含自动创建）"""
        week = datetime.now().strftime("%Y-W%V")

        filter_obj = {
            "and": [
                {
                    "property": "Week",
                    "rich_text": {
                        "equals": week
                    }
                },
                {
                    "property": "Auto Created",
                    "checkbox": {
                        "equals": False
                    }
                }
            ]
        }

        return self.query_database(filter_obj=filter_obj)

    def extract_property_value(self, page: Dict, property_name: str) -> Any:
        """
        从页面对象中提取属性值

        Args:
            page: 页面对象
            property_name: 属性名称

        Returns:
            属性值（类型根据属性类型而定）
        """
        props = page.get("properties", {})
        prop = props.get(property_name)

        if not prop:
            return None

        prop_type = prop.get("type")

        if prop_type == "title":
            titles = prop.get("title", [])
            return titles[0]["plain_text"] if titles else ""

        elif prop_type == "rich_text":
            texts = prop.get("rich_text", [])
            return texts[0]["plain_text"] if texts else ""

        elif prop_type == "select":
            select = prop.get("select")
            return select["name"] if select else None

        elif prop_type == "multi_select":
            return [item["name"] for item in prop.get("multi_select", [])]

        elif prop_type == "date":
            date = prop.get("date")
            return date["start"] if date else None

        elif prop_type == "checkbox":
            return prop.get("checkbox", False)

        elif prop_type == "number":
            return prop.get("number")

        elif prop_type == "created_time":
            return prop.get("created_time")

        return None
