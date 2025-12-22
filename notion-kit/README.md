# Notion Kit

快速集成 Notion 笔记功能到任何 Python 项目。

## 使用方法

1. 复制整个 `notion-kit` 文件夹到目标项目
2. 安装依赖：`pip install -r requirements.txt`
3. 导入使用：

```python
from notion_wrap import NotionWrapper

notion = NotionWrapper()

# 添加笔记
notion.add_task(
    name="学到的知识点",
    task_type="Note",  # Note/Vocabulary/Concept/Code Snippet/Example
    note="详细内容...",
    tags=["Python", "AI"],
    priority="High"  # High/Medium/Low
)

# 查询本周笔记
results = notion.query_current_week()
```

## 配置

`.env` 文件已包含 Notion 配置，无需修改。
