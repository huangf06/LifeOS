# 量化金融求职管理系统

一个完整的求职管理工具，帮助你高效管理简历版本、追踪申请进度、收集职位信息。

## 🚀 快速开始

### 基本设置
```bash
cd /Users/huangfei/lifeos/job_search
```

### 生成第一份简历
```bash
# 为IMC Trading生成定制化简历
python scripts/resume_generator.py --company "IMC Trading" --position "Quantitative Researcher" --pdf

# 为Optiver生成简历
python scripts/resume_generator.py --company "Optiver" --position "Quantitative Trader" --pdf
```

### 开始追踪申请
```bash
# 添加新申请
python scripts/application_tracker.py add \\
    --company "IMC Trading" \\
    --position "Graduate Quantitative Researcher" \\
    --status "draft" \\
    --priority "high" \\
    --salary "€80,000 - €120,000"

# 查看所有申请
python scripts/application_tracker.py list

# 更新申请状态
python scripts/application_tracker.py update --id [APP_ID] --status "submitted"

# 查看统计信息
python scripts/application_tracker.py summary
```

### 收集职位信息
```bash
# 手动添加职位信息
python scripts/job_scraper.py add \\
    --company "IMC Trading" \\
    --title "Graduate Quantitative Researcher" \\
    --location "Amsterdam" \\
    --salary "€80,000 - €120,000" \\
    --url "https://imc.com/careers/job/123"

# 搜索职位
python scripts/job_scraper.py search --keyword "quantitative"

# 分析职位市场
python scripts/job_scraper.py analyze
```

## 📁 系统结构

```
job_search/
├── config/
│   └── settings.json          # 个人信息和系统配置
├── resumes/
│   ├── templates/             # 简历模板
│   ├── versions/              # 各公司定制版本
│   └── output/                # 生成的PDF文件
├── applications/
│   ├── tracker.json           # 申请追踪数据
│   ├── interviews/            # 面试记录
│   └── feedback/              # 反馈记录
├── job_data/
│   └── scraped_jobs.json      # 收集的职位信息
└── scripts/
    ├── resume_generator.py    # 简历生成工具
    ├── application_tracker.py # 申请追踪工具
    └── job_scraper.py         # 职位收集工具
```

## 🎯 核心功能

### 1. 智能简历生成
- **基于模板系统**: 维护一个基础模板，针对不同公司生成定制版本
- **自动格式转换**: Markdown → PDF 自动转换
- **版本管理**: 追踪每个版本的表现和回复率

**使用示例**:
```bash
# 生成简历并转换为PDF
python scripts/resume_generator.py --company "IMC Trading" --position "Quantitative Researcher" --pdf

# 生成的文件位置:
# resumes/versions/IMC_Trading_Quantitative_Researcher_v1.md
# resumes/output/IMC_Trading_Quantitative_Researcher_v1.pdf
```

### 2. 申请状态追踪
- **完整生命周期管理**: 从draft到offer的每个阶段
- **时间线追踪**: 申请日期、预期回复时间、面试安排
- **数据分析**: 回复率、面试邀请率等关键指标

**状态流程**:
```
draft → submitted → screening → interview_scheduled → 
interview_completed → offer_received/rejected
```

### 3. 职位信息管理
- **目标公司监控**: 定期检查目标公司的新职位
- **关键词匹配**: 自动识别相关的量化金融职位
- **市场分析**: 分析职位分布、薪资范围、技能要求

## 📊 数据分析功能

### 查看申请统计
```bash
python scripts/application_tracker.py summary
```

输出示例:
```
📊 Application Summary:
Total Applications: 15
Active Applications: 8
Response Rate: 60.0%
Interview Rate: 33.3%

Status Breakdown:
  submitted: 5
  interview_scheduled: 2
  rejected: 3
  offer_received: 1
```

### 分析职位市场
```bash
python scripts/job_scraper.py analyze
```

输出示例:
```
📈 Job Market Analysis:
Total Jobs: 25
Company Distribution:
  IMC Trading: 3
  Optiver: 4
  Flow Traders: 2
Position Types:
  researcher: 8
  analyst: 6
  developer: 4
```

## 🛠 自定义配置

### 修改个人信息
编辑 `config/settings.json`:
```json
{
  "personal_info": {
    "name": "你的姓名",
    "email": "your.email@example.com",
    "phone": "+31 XXX XXX XXX",
    "location": "Amsterdam, Netherlands"
  }
}
```

### 添加新的简历模板
1. 在 `resumes/templates/` 创建新模板文件
2. 在 `resume_generator.py` 中添加公司特定的定制逻辑

### 扩展申请追踪字段
修改 `applications/tracker.json` 中的模板结构，添加你需要的字段。

## 📅 建议工作流程

### 日常使用
1. **每周一**: 运行职位搜索，更新目标职位列表
2. **申请前**: 为目标公司生成定制简历
3. **申请后**: 立即记录到追踪系统
4. **面试后**: 更新状态并记录反馈

### 批量操作
```bash
# 为多个公司生成简历
companies=("IMC Trading" "Optiver" "Flow Traders")
for company in "${companies[@]}"; do
    python scripts/resume_generator.py --company "$company" --position "Quantitative Researcher" --pdf
done

# 批量更新申请状态
python scripts/application_tracker.py list --status submitted | while read line; do
    # 根据需要更新状态
    echo "Check status for: $line"
done
```

## 🎯 求职策略建议

### 简历优化
- 为每个公司生成专门版本，突出相关技能
- 追踪不同版本的回复率，优化表现不佳的版本
- 定期更新基础模板，纳入新的技能和经验

### 申请管理
- 设置合理的申请节奏，避免同时处理过多面试
- 记录每次面试的问题和反馈，为后续面试做准备
- 定期review拒绝原因，识别需要改进的地方

### 数据驱动决策
- 分析回复率最高的简历版本特征
- 识别面试表现最好的公司类型
- 根据市场分析调整申请策略

## 🔧 故障排除

### 常见问题
1. **PDF生成失败**: 确保安装了pandoc和相关依赖
2. **权限问题**: 确保脚本有执行权限 `chmod +x scripts/*.py`
3. **配置文件错误**: 检查JSON格式是否正确

### 备份和恢复
```bash
# 备份所有数据
cp -r applications/ job_data/ backups/$(date +%Y%m%d)/

# 恢复数据
cp -r backups/20240106/* ./
```

## 📈 后续扩展

系统设计为可扩展的，你可以添加:
- 更复杂的职位爬虫 (LinkedIn API, Indeed等)
- Web界面仪表盘
- 邮件自动提醒功能
- 面试准备助手
- 薪资谈判分析工具

---

**开始你的求职之旅吧！** 🚀

记住：这个系统的目标是让你的求职过程更加科学化和数据驱动，但最终的成功还是取决于你的能力展示和面试表现。