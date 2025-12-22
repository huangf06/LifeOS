# Notion to Anki 自动同步系统 - 施工方案

> 最后更新: 2024-12-22
> 状态: 待实施

---

## 一、系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                         用户工作流                                   │
│                                                                     │
│   1. 在 Notion "Anki Cards" 数据库中添加卡片                         │
│   2. 每天收到 Telegram 推送的 .apkg 文件                             │
│   3. 点击文件，选择"用 Anki 打开"                                    │
│   4. 手机 Anki 自动同步到 AnkiWeb                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         技术架构                                     │
│                                                                     │
│   ┌──────────────┐                                                  │
│   │   Notion     │                                                  │
│   │  Database    │                                                  │
│   │ "Anki Cards" │                                                  │
│   └──────┬───────┘                                                  │
│          │ Notion API                                               │
│          ▼                                                          │
│   ┌──────────────────────────────────────┐                          │
│   │       GitHub Actions                  │                          │
│   │  (每天 UTC 00:00 = 北京 08:00)        │                          │
│   │                                      │                          │
│   │  1. 拉取 Notion 数据库               │                          │
│   │  2. 对比上次同步状态                 │                          │
│   │  3. 生成增量 .apkg 文件              │                          │
│   │  4. 通过 Telegram Bot 发送           │                          │
│   │  5. 更新同步状态记录                 │                          │
│   └──────────────────────────────────────┘                          │
│          │                                                          │
│          │ Telegram Bot API                                         │
│          ▼                                                          │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐       │
│   │  Telegram    │     │    Anki      │     │   AnkiWeb    │       │
│   │   手机端     │ ──▶ │   手机端     │ ──▶ │   云同步     │       │
│   │  接收文件    │     │   导入卡片   │     │              │       │
│   └──────────────┘     └──────────────┘     └──────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 二、组件清单

### 2.1 Notion 数据库

**数据库名称**: `Anki Cards`

**字段结构**:

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `Front` | Title | ✅ | 卡片正面（问题） |
| `Back` | Text | ✅ | 卡片背面（答案） |
| `Deck` | Select | ✅ | 牌组名称 |
| `Tags` | Multi-select | ❌ | 标签 |
| `Source` | URL | ❌ | 来源链接（可链接到 Cortex/知识库） |
| `Synced` | Checkbox | ❌ | 是否已同步（脚本自动更新） |
| `Last Synced` | Date | ❌ | 最后同步时间（脚本自动更新） |

**Deck 选项**:
- `Vocabulary` - 词汇
- `Concept` - 概念
- `Translation` - 翻译
- `Code` - 代码片段
- `General` - 通用

**Tags 选项**:
- `English`
- `Quant`
- `Programming`
- `Daily`
- （可自行扩展）

---

### 2.2 Python 同步脚本

**文件路径**: `scripts/sync_notion_anki.py`（重构现有文件）

**依赖**:
```
notion-client>=2.0.0
genanki>=0.13.0
requests>=2.28.0
python-telegram-bot>=20.0
python-dotenv>=1.0.0
```

**核心功能**:
1. 查询 Notion 数据库（筛选未同步或已修改的卡片）
2. 使用 `genanki` 生成 .apkg 文件
3. 使用 Notion Page ID 作为 Anki Note GUID（防止重复）
4. 通过 Telegram Bot API 发送文件
5. 更新 Notion 中的 `Synced` 和 `Last Synced` 字段

---

### 2.3 Telegram Bot

**创建步骤**:
1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot`
3. 按提示设置名称和用户名
4. 获取 Bot Token
5. 获取你的 Chat ID（通过 `@userinfobot` 或 `@getidsbot`）

**配置项**:
- `TELEGRAM_BOT_TOKEN`: Bot Token
- `TELEGRAM_CHAT_ID`: 你的 Chat ID

---

### 2.4 GitHub Actions

**工作流文件**: `.github/workflows/sync-anki.yml`

**触发条件**:
- 每天 UTC 00:00（北京时间 08:00）自动运行
- 手动触发（workflow_dispatch）

**Secrets 配置**:
- `NOTION_TOKEN`: Notion Integration Token
- `NOTION_DATABASE_ID`: Anki Cards 数据库 ID
- `TELEGRAM_BOT_TOKEN`: Telegram Bot Token
- `TELEGRAM_CHAT_ID`: 你的 Telegram Chat ID

---

### 2.5 配置文件

**文件路径**: `config/anki_sync_config.json`

```json
{
  "notion": {
    "database_id": "YOUR_DATABASE_ID",
    "filter": {
      "or": [
        { "property": "Synced", "checkbox": { "equals": false } },
        { "property": "Synced", "checkbox": { "is_empty": true } }
      ]
    }
  },
  "anki": {
    "deck_prefix": "LifeOS",
    "model_name": "LifeOS Basic",
    "default_deck": "General"
  },
  "telegram": {
    "enabled": true,
    "send_empty_report": false
  },
  "sync": {
    "update_notion_status": true,
    "generate_full_deck": false
  }
}
```

---

### 2.6 同步状态管理

**本地状态文件**: `data/anki_sync_state.json`

```json
{
  "last_sync": "2024-12-22T08:00:00Z",
  "synced_cards": {
    "notion_page_id_1": {
      "anki_guid": "generated_guid_1",
      "last_modified": "2024-12-21T10:00:00Z",
      "front_hash": "abc123"
    }
  },
  "stats": {
    "total_synced": 150,
    "last_batch_count": 5
  }
}
```

---

## 三、实施步骤

### Phase 1: 基础设施准备

| 步骤 | 任务 | 预计时间 |
|------|------|----------|
| 1.1 | 创建 Notion "Anki Cards" 数据库 | 5 分钟 |
| 1.2 | 创建 Telegram Bot，获取 Token 和 Chat ID | 5 分钟 |
| 1.3 | 更新 LifeOS 配置文件 | 5 分钟 |
| 1.4 | 安装 Python 依赖 | 2 分钟 |

### Phase 2: 核心脚本开发

| 步骤 | 任务 | 预计时间 |
|------|------|----------|
| 2.1 | 重构 `sync_notion_anki.py` - Notion 查询模块 | 15 分钟 |
| 2.2 | 实现 genanki 卡片生成模块 | 15 分钟 |
| 2.3 | 实现 Telegram 发送模块 | 10 分钟 |
| 2.4 | 实现状态管理模块 | 10 分钟 |
| 2.5 | 整合并添加 CLI 入口 | 10 分钟 |

### Phase 3: 本地测试

| 步骤 | 任务 | 预计时间 |
|------|------|----------|
| 3.1 | 在 Notion 添加 3 张测试卡片 | 2 分钟 |
| 3.2 | 运行 `./lifeos sync-anki --dry-run` 验证 | 5 分钟 |
| 3.3 | 运行 `./lifeos sync-anki` 实际同步 | 5 分钟 |
| 3.4 | 检查 Telegram 是否收到文件 | 2 分钟 |
| 3.5 | 导入 Anki 并验证卡片内容 | 5 分钟 |

### Phase 4: GitHub Actions 配置

| 步骤 | 任务 | 预计时间 |
|------|------|----------|
| 4.1 | 创建 `.github/workflows/sync-anki.yml` | 10 分钟 |
| 4.2 | 在 GitHub 配置 Secrets | 5 分钟 |
| 4.3 | 手动触发 workflow 测试 | 5 分钟 |
| 4.4 | 验证定时任务配置 | 2 分钟 |

### Phase 5: 集成与文档

| 步骤 | 任务 | 预计时间 |
|------|------|----------|
| 5.1 | 更新 `lifeos` 入口脚本 | 5 分钟 |
| 5.2 | 更新 `CLAUDE.md` 文档 | 5 分钟 |
| 5.3 | 创建用户快速指南 | 10 分钟 |

---

## 四、文件结构

```
LifeOS/
├── .github/
│   └── workflows/
│       └── sync-anki.yml          # [新建] GitHub Actions 工作流
│
├── config/
│   ├── anki_sync_config.json      # [新建] 同步配置
│   └── anki_config.json           # [现有] 保留兼容
│
├── data/
│   └── anki_sync_state.json       # [新建] 同步状态记录
│
├── scripts/
│   └── sync_notion_anki.py        # [重构] 同步脚本
│
├── docs/
│   ├── NOTION_ANKI_SYNC_PLAN.md   # [本文件] 施工方案
│   └── ANKI_SYNC_QUICKSTART.md    # [新建] 用户快速指南
│
├── notion-kit/
│   └── notion_wrap.py             # [现有] 复用 Notion API 封装
│
├── lifeos                          # [更新] 添加 sync-anki 命令
└── CLAUDE.md                       # [更新] 添加 Anki 同步说明
```

---

## 五、关键技术细节

### 5.1 防止重复卡片

使用 Notion Page ID 生成稳定的 GUID：

```python
import hashlib

def generate_anki_guid(notion_page_id: str) -> str:
    """从 Notion Page ID 生成稳定的 Anki GUID"""
    # genanki 要求 GUID 是 10 位数字
    hash_hex = hashlib.md5(notion_page_id.encode()).hexdigest()
    return str(int(hash_hex[:16], 16) % (10**10))
```

### 5.2 增量同步逻辑

```python
def get_cards_to_sync(notion, config, state):
    """获取需要同步的卡片"""
    # 查询条件：Synced = false OR Synced 为空
    filter_obj = {
        "or": [
            {"property": "Synced", "checkbox": {"equals": False}},
            {"property": "Synced", "checkbox": {"is_empty": True}}
        ]
    }

    pages = notion.databases.query(
        database_id=config["database_id"],
        filter=filter_obj
    )

    return pages["results"]
```

### 5.3 Anki 卡片模型

```python
import genanki

LIFEOS_MODEL = genanki.Model(
    1607392319,  # 固定 ID，确保模型一致
    'LifeOS Basic',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},
        {'name': 'Source'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Front}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Back}}<br><small>{{Source}}</small>',
        },
    ],
    css='''
    .card {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 18px;
        text-align: center;
        color: #333;
        background-color: #fff;
    }
    '''
)
```

### 5.4 Telegram 发送文件

```python
import requests

def send_apkg_to_telegram(file_path: str, bot_token: str, chat_id: str, caption: str = ""):
    """发送 .apkg 文件到 Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {
            'chat_id': chat_id,
            'caption': caption or f"Anki 卡片同步 - {datetime.now().strftime('%Y-%m-%d')}"
        }
        response = requests.post(url, files=files, data=data)

    return response.json()
```

---

## 六、配置清单

### 6.1 需要获取的凭证

| 凭证 | 来源 | 用途 |
|------|------|------|
| `NOTION_TOKEN` | [Notion Integrations](https://www.notion.so/my-integrations) | 访问 Notion API |
| `NOTION_DATABASE_ID` | 创建数据库后从 URL 提取 | 指定同步的数据库 |
| `TELEGRAM_BOT_TOKEN` | @BotFather | 发送消息 |
| `TELEGRAM_CHAT_ID` | @userinfobot | 指定接收者 |

### 6.2 GitHub Secrets 配置

在仓库 Settings → Secrets and variables → Actions 中添加：

- `NOTION_TOKEN`
- `NOTION_DATABASE_ID`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

---

## 七、验收标准

### 7.1 功能验收

- [ ] 在 Notion 添加卡片后，运行脚本能生成 .apkg
- [ ] .apkg 文件能通过 Telegram 发送到手机
- [ ] 导入 Anki 后卡片内容正确
- [ ] 重复运行脚本不会产生重复卡片
- [ ] 修改 Notion 卡片后，Anki 中能更新
- [ ] GitHub Actions 能定时自动运行

### 7.2 性能验收

- [ ] 100 张卡片的同步时间 < 30 秒
- [ ] 生成的 .apkg 文件大小合理（< 5MB for 1000 cards）

---

## 八、风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| Notion API 限流 | 低 | 同步失败 | 添加重试逻辑，已在 notion_wrap.py 实现 |
| Telegram 发送失败 | 低 | 收不到文件 | 添加错误通知，保留本地 .apkg 备份 |
| GitHub Actions 额度用尽 | 极低 | 无法自动运行 | 每月 2000 分钟足够，每次运行约 1-2 分钟 |
| Anki 导入覆盖复习进度 | 低 | 复习进度丢失 | 使用稳定 GUID，测试验证 |

---

## 九、后续优化（可选）

1. **支持图片**: 下载 Notion 中的图片并嵌入 .apkg
2. **支持 LaTeX**: 转换数学公式为 Anki MathJax 格式
3. **双向同步**: 将 Anki 复习数据回写到 Notion（高级）
4. **多数据库支持**: 同时从 Cortex 等数据库同步
5. **智能提取**: 从知识库 Toggle List 自动提取卡片

---

## 十、执行确认

- [ ] 已阅读并理解本方案
- [ ] 已准备好 Notion 账户
- [ ] 已准备好 Telegram 账户
- [ ] 已确认 GitHub 仓库权限
- [ ] 准备开始 Phase 1

---

**准备好后，回复"开始"，我们将按照 Phase 1 逐步执行。**
