# Notion to Anki 同步 - 快速入门指南

> 最后更新: 2025-12-22
> 版本: 1.0

欢迎使用 LifeOS Notion-Anki 同步系统！这个指南将帮你在 5 分钟内完成设置。

---

## 📋 功能概览

✨ **自动化学习卡片管理**

- 📝 在 Notion 中管理 Anki 卡片（支持富文本、标签、来源链接）
- 🤖 每天自动生成 .apkg 文件
- 📱 通过 Telegram 接收文件，一键导入手机 Anki
- ☁️ 自动同步到 AnkiWeb

---

## 🚀 快速开始

### 步骤 1: 准备工作（5 分钟）

#### 1.1 创建 Notion Integration

1. 访问 [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. 点击 "+ New integration"
3. 命名为 "LifeOS" 或其他名称
4. 复制 "Internal Integration Token"（ntn_xxx...）
5. 保存到 `notion-kit/.env`:

```bash
NOTION_TOKEN=ntn_你的Token
```

#### 1.2 创建 Telegram Bot

1. 在 Telegram 搜索 `@BotFather`
2. 发送 `/newbot`
3. 设置名称和用户名
4. 复制 Bot Token
5. 搜索 `@userinfobot` 获取你的 Chat ID
6. 添加到 `notion-kit/.env`:

```bash
TELEGRAM_BOT_TOKEN=你的Bot_Token
TELEGRAM_CHAT_ID=你的Chat_ID
```

#### 1.3 创建 Anki Cards 数据库

在项目根目录运行：

```bash
./lifeos setup-anki
```

或指定父页面：

```bash
./lifeos setup-anki YOUR_PAGE_ID
```

✅ 数据库会自动创建，ID 会保存到 `.env` 文件

---

### 步骤 2: 添加测试卡片（2 分钟）

在 Notion "Anki Cards" 数据库中添加 2-3 张测试卡片：

| Front | Back | Deck | Tags | Source |
|-------|------|------|------|--------|
| What is GTD? | Getting Things Done - 提升生产力的方法论 | Concept | Daily | |
| Python list comprehension | `[x**2 for x in range(10)]` | Code | Programming | |
| 明天 | tomorrow | Vocabulary | English | |

**字段说明：**
- **Front** (必填): 卡片正面/问题
- **Back** (必填): 卡片背面/答案
- **Deck**: 牌组（Vocabulary/Concept/Translation/Code/General）
- **Tags**: 标签（English/Quant/Programming/Daily）
- **Source**: 来源链接（可选）
- **Synced**: 自动更新（脚本会自动勾选）
- **Last Synced**: 自动更新（最后同步时间）

---

### 步骤 3: 测试同步（1 分钟）

#### 3.1 试运行

```bash
./lifeos sync-anki --dry-run
```

应该看到：

```
============================================================
  Notion → Anki 同步
  [试运行模式 - 不会实际修改数据]
============================================================

🔍 查询未同步的卡片...
   找到 3 张未同步的卡片
```

#### 3.2 实际同步

```bash
./lifeos sync-anki
```

输出示例：

```
📦 生成 Anki 包...
   ✓ What is GTD?... → LifeOS::Concept
   ✓ Python list comprehension... → LifeOS::Code
   ✓ 明天... → LifeOS::Vocabulary
✅ Anki 包已生成: data/anki_sync_20251222_143052.apkg
   包含 3 个牌组，共 3 张卡片

📤 发送到 Telegram...
✅ 已发送到 Telegram

📝 更新 Notion 同步状态...
✅ 已更新 3 张卡片的同步状态

🎉 同步完成！
```

---

### 步骤 4: 导入到 Anki（1 分钟）

#### 方式 1: 手机（推荐）

1. 打开 Telegram，找到你的 Bot
2. 点击收到的 .apkg 文件
3. 选择"用 Anki 打开"
4. Anki 自动导入
5. 在 Anki 中点击"同步"→ 上传到 AnkiWeb

#### 方式 2: 电脑

1. 找到生成的文件：`data/anki_sync_xxx.apkg`
2. 双击文件，Anki 自动导入
3. 点击"同步"上传到 AnkiWeb

---

## 🤖 自动化设置（可选）

### GitHub Actions 每日自动同步

#### 1. 配置 Secrets

在 GitHub 仓库设置中添加：

1. 进入 **Settings** → **Secrets and variables** → **Actions**
2. 点击 "New repository secret"
3. 添加以下 4 个 secrets:

| Name | Value | 说明 |
|------|-------|------|
| `NOTION_TOKEN` | ntn_xxx... | Notion Integration Token |
| `ANKI_DATABASE_ID` | xxx-xxx-xxx | Anki Cards 数据库 ID |
| `TELEGRAM_BOT_TOKEN` | 123456:xxx | Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | 123456789 | 你的 Telegram Chat ID |

#### 2. 提交代码

```bash
git add .
git commit -m "feat: add Notion-Anki sync system"
git push
```

#### 3. 测试 Workflow

1. 在 GitHub 进入 **Actions** 标签
2. 选择 "Notion to Anki Sync"
3. 点击 "Run workflow"
4. 查看运行日志

✅ 设置完成后，每天北京时间 08:00 自动同步！

---

## 📱 使用指南

### 日常工作流

1. **在 Notion 中添加卡片**
   - 随时在 "Anki Cards" 数据库中添加新卡片
   - 不需要手动标记 Synced

2. **每天早上（自动）**
   - GitHub Actions 自动运行同步
   - 新卡片生成 .apkg 文件
   - Telegram 自动推送文件

3. **导入到 Anki（手机）**
   - 打开 Telegram
   - 点击 .apkg 文件
   - 选择"用 Anki 打开"
   - 在 Anki 中同步到云端

4. **开始复习**
   - 在任何设备打开 Anki
   - 从 AnkiWeb 同步下载
   - 开始复习！

### 手动同步

如果需要立即同步：

```bash
./lifeos sync-anki
```

### 查看帮助

```bash
./lifeos help
```

---

## 🎯 高级用法

### 自定义牌组结构

编辑 `config/anki_sync_config.json`:

```json
{
  "anki": {
    "deck_prefix": "LifeOS",        // 牌组前缀
    "default_deck": "General"       // 默认牌组
  }
}
```

卡片会自动组织为: `LifeOS::Vocabulary`, `LifeOS::Concept` 等

### 批量添加卡片

在 Notion 中使用表格视图：
1. 点击右上角 "Table"
2. 快速填充多行
3. 运行同步

### 更新已有卡片

Anki 使用 Notion Page ID 生成稳定的 GUID，因此：
- ✅ 修改卡片内容会更新 Anki
- ✅ 不会产生重复卡片
- ✅ 保留复习进度

**重要**: 修改后需要将 `Synced` 取消勾选，下次同步才会更新。

---

## 🔧 故障排除

### 问题 1: 查询失败 "Invalid request URL"

**原因**: Python SDK 还在适配新 API

**解决**: 代码已使用直接 HTTP 请求，无需处理

### 问题 2: Telegram 未收到文件

**检查**:
1. Bot Token 和 Chat ID 是否正确？
2. 是否向 Bot 发送过消息（激活对话）？
3. 查看脚本输出是否有错误提示

**测试 Telegram**:
```bash
curl -X POST "https://api.telegram.org/bot你的TOKEN/sendMessage" \
  -d "chat_id=你的CHAT_ID&text=Test"
```

### 问题 3: GitHub Actions 失败

**检查**:
1. 所有 4 个 Secrets 是否正确设置？
2. 查看 Actions 日志的详细错误
3. 手动运行测试: `./lifeos sync-anki --dry-run`

### 问题 4: Anki 显示重复卡片

**原因**: 可能修改了 Notion Page ID

**解决**:
1. 在 Anki 中删除旧卡片
2. 重新同步

---

## 📚 相关资源

- [Notion API 文档](https://developers.notion.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [genanki 文档](https://github.com/kerrickstaley/genanki)
- [Anki Manual](https://docs.ankiweb.net/)

---

## 🤝 需要帮助？

1. 查看 `CLAUDE.md` 了解技术细节
2. 检查 GitHub Issues
3. 运行 `./lifeos help` 查看所有命令

---

## 🎉 完成！

你已经成功设置了 Notion-Anki 同步系统！

**下一步：**
1. 在 Notion 中添加更多卡片
2. 设置 GitHub Actions 自动同步
3. 在手机上愉快地复习

Happy Learning! 📚✨
