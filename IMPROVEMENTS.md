# LifeOS 改进记录

## 2025-10-29 更新

### 🎯 主要改进

#### 1. **跨平台路径支持**
- ✅ 所有脚本改用相对路径，自动检测项目根目录
- ✅ 不再硬编码 `~/LifeOS` 或 `~/Downloads/LifeOS`
- ✅ 支持 Windows、Mac、Linux 跨平台使用

**修改的文件：**
- `scripts/personal_assistant.py`
- `scripts/todoist_manager.py`
- `scripts/logseq_tracker.py`
- `scripts/ai_advisor.py`
- `scripts/quick_task.py`

#### 2. **增强自然语言解析**

**扩展任务动词识别：**
```python
# 新增支持的动词
"去", "取", "拿", "送", "接", "订", "预约", "报名",
"提交", "发送", "回复", "打电话", "查看", "检查",
"修改", "更新", "删除", "测试", "上传", "下载",
"阅读", "研究", "分析", "总结", "汇报", "沟通"
```

**改进项目分类：**
- `fitness`: 健身、运动、锻炼、跑步、力量、瑜伽、游泳、训练
- `career`: 面试、简历、求职、招聘、投递、笔试、作品集
- `english`: 英语、学习、口语、听力、阅读、写作、单词、语法
- `work`: 项目、会议、报告、代码、开发、测试、上线、文档、汇报
- `study`: 复习、研究、课程、论文、资料、笔记
- `life`: 买、购、取、送、医院、体检、快递、缴费、预约

#### 3. **新增快速任务命令**

创建了 `scripts/quick_task.py`，支持精确控制任务创建：

```bash
# 基本用法
./lifeos quick '任务内容' '时间'

# 完整用法
./lifeos quick '任务' '时间' [项目] [优先级] [描述]
```

**示例：**
```bash
# 简单任务
./lifeos quick '取快递' 'today 21:00'

# 重复任务
./lifeos quick '健身' 'every day at 18:00' fitness high

# 带描述的任务
./lifeos quick '面试' 'tomorrow 10am' career high '准备简历和作品集'
```

**支持的时间格式：**
- `today`, `tomorrow`
- `today 21:00`, `tomorrow 9am`
- `every day`, `every weekday`
- `every monday at 9am`
- `2025-01-15`

#### 4. **更新 Skill 文档**

在 `.claude/skills/lifeos-helper/SKILL.md` 中新增：
- 高级用法示例
- 直接使用 Python API 的方法
- 常见场景解决方案
- 时间格式支持说明

---

### 📊 测试结果

**测试 1: 自然语言解析（已改进）**
```bash
./lifeos '我晚上9点要去取我的TooGoodToGo' --auto-send
```
✅ 成功识别"取"动词
✅ 正确分类到 life 项目
✅ 自动创建任务

**测试 2: 快速任务命令**
```bash
./lifeos quick '明天早上跑步' 'tomorrow 7am' fitness high '5公里晨跑'
```
✅ 任务创建成功
✅ 时间格式正确
✅ 项目和优先级正确

---

### 🚀 新功能

#### 快速任务创建流程

**方法 1: 自然语言（适合简单任务）**
```bash
./lifeos '明天要开会'
```

**方法 2: 快速命令（适合精确控制）**
```bash
./lifeos quick '开会' 'tomorrow 10am' work high '准备PPT'
```

**方法 3: 直接 Python API（复杂场景）**
```python
from todoist_api_python.api import TodoistAPI
task = api.add_task(
    content="任务",
    due_string="every monday at 9am",
    project_id=project_id
)
```

---

### 📝 使用建议

1. **日常任务**: 使用自然语言 `./lifeos '任务描述'`
2. **带时间的任务**: 使用快速命令 `./lifeos quick`
3. **重复任务**: 使用快速命令指定 `every day`
4. **复杂任务**: 直接用 Python API

---

### 🔧 技术改进

**相对路径实现：**
```python
# 自动获取项目根目录
script_dir = Path(__file__).parent
project_root = script_dir.parent
config_path = project_root / "config" / "todoist_config.json"
```

**优势：**
- 无需配置路径
- 支持任意位置运行
- 跨平台兼容
- Git 克隆即可使用

---

### 📖 下一步计划

#### 待实现功能：

1. **任务管理**
   - [ ] 完成任务: `./lifeos done <task_id>`
   - [ ] 搜索任务: `./lifeos search "关键词"`
   - [ ] 修改任务: `./lifeos edit <task_id>`
   - [ ] 删除任务: `./lifeos delete <task_id>`

2. **时间解析增强**
   - [ ] 支持中文时间: "晚上9点"、"下午3点"
   - [ ] 支持相对时间: "1小时后"、"30分钟后"
   - [ ] 支持日期范围: "本周"、"下个月"

3. **智能提醒**
   - [ ] 任务到期提醒
   - [ ] 习惯打卡提醒
   - [ ] 每日总结提醒

4. **数据分析**
   - [ ] 任务完成率统计
   - [ ] 时间分配分析
   - [ ] 项目进度追踪
   - [ ] 生成周报/月报

5. **集成功能**
   - [ ] 日历同步
   - [ ] Notion 集成
   - [ ] Obsidian 集成
   - [ ] Slack 通知

---

### 🐛 已修复问题

- ✅ 路径硬编码导致跨平台问题
- ✅ 任务动词识别不全（"去"、"取"等）
- ✅ 时间解析不支持具体时间点
- ✅ 项目分类关键词不够丰富
- ✅ 缺少快速创建任务的方法

---

### 💡 使用技巧

**1. 批量创建任务**
```bash
./lifeos '明天要开会，准备PPT，发送邮件'
```

**2. 创建重复习惯**
```bash
./lifeos quick '早起' 'every day at 6am' life medium '养成早起习惯'
./lifeos quick '阅读' 'every weekday at 20:00' study medium '每天阅读30分钟'
```

**3. 设置项目目标**
```bash
./lifeos setup-goals  # 一次性设置三大目标
./lifeos setup-goal fitness  # 单独设置健身目标
```

**4. 导出数据分析**
```bash
./lifeos export-tasks  # 导出所有任务到 JSON
./lifeos report        # 生成周报
./lifeos analyze       # AI 分析生活模式
```

---

**更新时间**: 2025-10-29
**版本**: v1.1.0
**贡献者**: Claude Code + User
