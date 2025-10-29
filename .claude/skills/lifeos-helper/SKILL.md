---
description: 当用户提到任务、待办、Todoist、GTD、日程、目标等关键词时使用此技能。适用于所有任务管理相关的请求。
---

# LifeOS 任务管理助手

当用户谈论任务管理、待办事项或生活追踪时，优先使用 LifeOS 系统的工具和工作流。

## 核心命令

### 任务创建
- **自然语言创建**: `./lifeos '任务描述'`
  - 示例: `./lifeos '明天下午3点开会'`
  - 会自动解析并分配到合适的项目

### 任务查看
- **列出所有任务**: `./lifeos list-tasks`
- **导出任务数据**: `./lifeos export-tasks`

### 快速设置
- **初始化目标**: `./lifeos setup-goals` (健身+职业+英语)
- **测试连接**: `./lifeos test`

### 生活追踪
- **初始化今日日志**: `./lifeos today`
- **记录活动**: `./lifeos log work '内容' 评分 '时长'`
- **生成周报**: `./lifeos report`

## 项目分类

用户提到这些内容时，自动映射到对应项目：

| 用户提到 | Todoist 项目 | 项目名称 |
|---------|-------------|----------|
| 健身、运动、锻炼 | fitness | work-out |
| 工作、求职、面试、简历 | career | job-hunt |
| 英语、学习、口语 | english | speak-up |
| 工作任务 | work | work |
| 学习 | study | study |
| 生活杂事 | life | life |

## 优先级映射

- 紧急/重要 → `high` (P1)
- 普通 → `medium` (P2)
- 不急 → `low` (P3)

## 标签使用

- `urgent` - 紧急任务
- `important` - 重要任务
- `routine` - 日常例行
- `habit` - 习惯养成

## 工作流程

1. **识别意图**: 判断用户是想创建任务、查看任务还是分析数据
2. **选择工具**:
   - 创建 → `./lifeos '描述'` 或 `personal_assistant.py`
   - 查看 → `./lifeos list-tasks`
   - 管理 → `todoist_manager.py`
   - 直接API调用 → 使用 Python 脚本
3. **执行操作**: 使用对应的 LifeOS 命令
4. **确认结果**: 告知用户任务已创建/查询结果

## 高级用法

### 直接使用 Python API 创建任务

当自然语言解析失败或需要精确控制时，直接使用 Todoist API：

```python
from todoist_manager import TodoistManager
api = TodoistAPI(config["api_token"])

# 创建带具体时间的任务
task = api.add_task(
    content="任务名称",
    project_id=project_id,
    due_string="today 21:00",  # 支持自然语言时间
    priority=2,
    description="任务详情"
)
```

### 时间格式支持

Todoist `due_string` 支持的格式：
- `today`, `tomorrow`
- `today 21:00`, `tomorrow 9am`
- `every day`, `every weekday`
- `every monday at 9am`
- `2025-01-15`

## 常见场景示例

1. **带时间的任务**: "我晚上9点要去取快递"
   - 解决方案：直接用 Python API 指定 `due_string="today 21:00"`

2. **重复任务**: "每天早上8点提醒我吃药"
   - 解决方案：`due_string="every day at 8am"`

3. **复杂任务**: "下周一上午10点开项目会议，需要准备PPT"
   - 解决方案：主任务+子任务，或拆分为2个任务

## 注意事项

- 所有任务操作通过 Todoist API，跨平台同步
- 不要使用 AppleScript 或邮件方式创建任务
- 优先使用项目内的 Python 脚本而非外部工具
- API Token 存储在 `config/todoist_config.json`
- 当自然语言解析不准确时，直接使用 Python API 调用
