# LifeOS - AI Personal Assistant

> 通过自然语言对话生成任务，自动发送到OmniFocus的个人助理系统

## 🤖 Claude Code Assistant 身份定义
> **重要**：作为此项目的智能助理，我的核心职责是：
> - 🎯 **主动GTD任务管理** - 用户提到任何任务时立即使用TodoWrite跟踪并发送到OmniFocus
> - 📧 **无缝工具整合** - 优先使用项目内的email_sender.py等工具，而不是询问用户
> - 🚀 **先行动后解释** - 直接执行用户需求，减少确认步骤
> - 📋 **个人生活助理** - 专注于提升用户的个人效率和生活质量
> 
> 配置文件：`config/assistant_profile.json`

## 🎯 核心功能

- 🤖 **自然语言任务规划** - 描述你的想法，AI理解并生成结构化任务
- 📧 **自动发送到OmniFocus** - 一键发送任务到你的GTD系统  
- 🏋️ **专业健身计划** - 内置完整的健身训练流程
- 📊 **任务历史追踪** - 记录所有规划历史和使用统计

## 🚀 快速开始

### 1. 设置邮件账户
```bash
./lifeos setup
```
配置Gmail等邮箱，用于发送任务到OmniFocus

### 2. 发送健身计划
```bash
./lifeos fitness  
```
自动发送8步完整健身流程到OmniFocus

### 3. 智能任务规划
```bash
./lifeos "明天要开会，需要准备PPT和相关资料"
```
AI理解后生成有序任务列表

## 💡 使用示例

**健身规划：**
```bash
./lifeos fitness
# → 创建"健身计划第一天"任务，包含8个有序步骤
```

**工作规划：**
```bash
./lifeos "下周出差北京，要预订机票酒店，准备工作文件"
# → 创建"LifeOS任务计划"，包含多个优先级排序的子任务
```

**学习规划：**
```bash  
./lifeos "这个月要完成Python课程，每天学习2小时，做项目练习"
# → 自动拆分学习计划和时间安排
```

## 🏗️ 任务结构设计

**主任务 + 有序子任务模式**：
- 一个邮件 = 一个完整工作流
- 子任务按1、2、3...编号排序  
- 每步有详细说明和时间估算
- 优先级分组和总时间统计

示例输出：
```
健身计划第一天

1. 动态热身：关节活动
   说明：手腕、肩膀、腰部、膝盖各方向转动热身...

2. 轻松跑步热身 7分钟  
   说明：心率控制在120-130bpm，为力量训练做准备...

...
总训练时间：约60分钟
```

## 📋 完整命令列表

```bash
./lifeos "task description"  # 智能任务规划
./lifeos setup              # 设置邮件账户  
./lifeos test-email         # 测试邮件发送
./lifeos fitness            # 发送健身计划
./lifeos stats              # 查看使用统计
./lifeos help               # 显示帮助信息
```

## ⚙️ 系统要求

- **Python 3.7+** - 运行核心逻辑
- **邮箱账户** - Gmail/163/QQ等，需要应用专用密码  
- **OmniFocus 3** - 任务管理目标系统
- **macOS/Linux** - 命令行环境

## 🔧 核心文件

- `lifeos` - 主命令入口脚本
- `personal_assistant.py` - AI任务规划引擎
- `email_sender.py` - 邮件发送核心模块
- `config/email_config.json` - 邮件账户配置（自动生成）
- `data/task_history.jsonl` - 任务历史记录（自动生成）

## 🎉 开始使用

1. **克隆项目**：`git clone <repo-url>`
2. **进入目录**：`cd LifeOS`  
3. **设置邮箱**：`./lifeos setup`
4. **开始规划**：`./lifeos "你的任务描述"`

让AI成为你的个人生产力助理！💪