# LifeOS - 个人生活操作系统

黄飞的个人数字化生活管理平台，基于 GTD 方法论与 Todoist、Logseq 深度集成。

## ✨ 核心特性

- 🎯 **Todoist 集成** - 跨平台任务管理（Windows/Mac/iPhone/Android/Web）
- 🧠 **自然语言处理** - 智能解析任务描述，自动分类和优先级分配
- 📊 **Logseq 生活追踪** - 日志记录、数据追踪、周报生成
- 🤖 **AI 顾问** - 基于历史数据的生活模式分析和建议
- 📈 **数据导出分析** - 完整的任务数据导出和可视化支持

## 🚀 快速开始

### 一键安装

```bash
# 安装依赖
pip3 install todoist-api-python

# 首次配置
./lifeos setup

# 初始化项目和标签
./lifeos init-todoist

# 设置三大核心目标（健身/求职/英语）
./lifeos setup-goals
```

📖 **详细文档**: 查看 [TODOIST_QUICKSTART.md](TODOIST_QUICKSTART.md) 获取完整设置指南

### 常用命令

```bash
# 智能任务规划（自然语言）
./lifeos '明天要开会讨论新项目，需要提前准备PPT和资料'

# 快速发送健身计划
./lifeos fitness

# 查看所有任务
./lifeos list-tasks

# 导出任务数据
./lifeos export-tasks

# 生活追踪
./lifeos today              # 初始化今日记录
./lifeos log work '编程2小时' 8 '2h'
./lifeos report             # 生成周报

# AI 顾问
./lifeos analyze            # 分析生活模式
./lifeos plan               # 生成优化计划

# 查看完整帮助
./lifeos help
```

## 📁 系统架构

```
LifeOS/
├── config/                      # 系统配置
│   ├── todoist_config.json     # Todoist API 配置和项目映射
│   ├── assistant_profile.json  # AI 助手配置
│   └── logseq_templates.json   # Logseq 模板
├── scripts/                     # 核心脚本
│   ├── todoist_manager.py      # Todoist API 管理器
│   ├── personal_assistant.py   # 自然语言任务处理
│   ├── setup_goals.py          # 快速目标设置
│   ├── logseq_tracker.py       # 生活追踪系统
│   └── ai_advisor.py           # AI 顾问分析
├── data/                        # 本地数据存储（不同步）
├── archive/                     # 历史存档（不同步）
├── lifeos                       # 主入口脚本
├── CLAUDE.md                    # Claude Code AI 助手指南
├── TODOIST_QUICKSTART.md        # Todoist 快速入门
└── README.md                    # 本文档
```

## 🎯 三大核心目标

本系统围绕三个核心生活目标设计：

| 目标 | Todoist 项目 | 说明 |
|------|-------------|------|
| 💪 **健身计划** | work-out | 力量训练、有氧运动、体能测试 |
| 💼 **求职目标** | job-hunt | 简历优化、面试准备、岗位申请 |
| 🗣️ **英语学习** | speak-up | 听说读写、词汇扩展、面试英语 |

## 🛠️ 技术栈

- **任务管理**: Todoist REST API v2 (todoist-api-python)
- **笔记系统**: Logseq (Markdown + Git)
- **自动化**: Python 3.x + Bash
- **AI 集成**: Claude Code (Anthropic)
- **版本控制**: Git

## 📈 工作流示例

### 日常任务规划

```bash
# 早上：规划今天任务
./lifeos '今天要完成项目报告，下午3点开会，晚上复习英语听力'

# 系统自动：
# 1. 解析出3个任务
# 2. 分配到对应项目（工作/沟通/英语）
# 3. 设置优先级和截止时间
# 4. 同步到 Todoist
# 5. 所有设备实时更新
```

### 生活数据追踪

```bash
# 初始化今天的日志
./lifeos today

# 记录工作活动
./lifeos log work '完成算法题3道' 8 '2h'

# 更新心情数据
./lifeos data mood 7

# 周末生成报告
./lifeos report
```

## 📊 数据分析

所有任务数据可导出为 JSON 格式，支持：

- 完成率统计
- 时间分配分析
- 项目进展追踪
- 习惯养成监控
- 可视化图表生成

```bash
# 导出所有任务
./lifeos export-tasks

# 输出: ~/LifeOS/data/todoist_export_20251014_*.json
```

## 🔧 系统维护

### 备份策略
- Git 版本控制（代码和配置）
- Todoist 云端同步（任务数据）
- Logseq 本地+Git（笔记和追踪）
- 定期数据导出（JSON 备份）

### 持续改进
- 基于使用数据优化任务分类
- AI 顾问学习个人习惯
- 自动化工作流扩展
- 跨平台同步优化

## 📝 开发者指南

查看 [CLAUDE.md](CLAUDE.md) 了解：
- 项目架构设计
- API 集成方式
- 开发规范
- 测试流程

## 🆘 常见问题

**Q: 如何获取 Todoist API Token?**
A: 访问 https://todoist.com → Settings → Integrations → Developer

**Q: 任务没有同步怎么办?**
A: 运行 `./lifeos test` 检查连接状态

**Q: 如何备份数据?**
A: 定期运行 `./lifeos export-tasks` 导出 JSON 数据

**Q: 支持哪些平台?**
A: Windows、Mac、Linux（WSL）、iPhone、Android 全平台同步

---

*"The best time to plant a tree was 10 years ago. The second best time is now."*

**最后更新:** 2025-10-14
**当前版本:** v3.0 - Todoist 集成完整版