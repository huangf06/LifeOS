# LifeOS - 个人生活操作系统

费煌的个人数字化生活管理平台

## 🎯 当前重点：量化金融求职

### 求职管理系统
位置：`./job_search/`

**核心功能：**
- 🎯 智能简历生成和版本管理
- 📋 申请状态全程追踪  
- 💼 职位信息收集和分析
- 📊 数据可视化仪表盘

**快速开始：**
```bash
cd job_search
python job_manager.py help
```

详细文档：[job_search/README.md](./job_search/README.md)

---

## 📁 系统架构

```
lifeos/
├── job_search/           # 🎯 求职管理系统 (当前重点)
│   ├── job_manager.py    # 统一管理入口
│   ├── resumes/          # 简历版本管理
│   ├── applications/     # 申请追踪
│   ├── job_data/        # 职位信息
│   └── dashboard/       # 数据仪表盘
├── config/              # 系统配置
├── scripts/             # 自动化脚本
├── projects/            # 项目管理
├── data/               # 数据存储
└── logs/               # 系统日志
```

## 🚀 核心命令

### 求职管理
```bash
# 生成简历
python job_search/job_manager.py resume --company "IMC Trading" --position "Quantitative Researcher" --pdf

# 追踪申请
python job_search/job_manager.py apply add --company "IMC Trading" --position "Quant Researcher"

# 查看进展
python job_search/job_manager.py apply summary
python job_search/job_manager.py dashboard
```

### 系统管理  
```bash
# 个人助手
python scripts/personal_assistant.py

# 日程管理
python scripts/logseq_tracker.py
```

## 📈 当前状态

**求职进展：**
- ✅ 求职管理系统已搭建完成
- ✅ 简历模板和版本管理系统就绪
- 🔄 正在准备IMC Trading量化研究员申请
- 📋 目标：2025年8月开始全职工作

**技能栈：**
- 🎓 VU Amsterdam AI硕士 (GPA: 8.2/10)
- 🏛️ 清华大学工业工程学士 (0.01%录取率)
- 💹 中国A股交易经验 + 金融从业资格  
- 🤖 Python, ML/DL, 统计分析, 时间序列分析

## 🎯 目标与愿景

**短期目标 (2025 Q1-Q2):**
- 成功申请量化金融相关职位
- 完成VU Amsterdam AI硕士学位
- 建立欧洲职业网络

**长期愿景:**
- 成为顶级量化研究专家
- 在AI+金融交叉领域建立影响力
- 实现财务自由和个人成长

---

## 🔧 系统维护

### 备份策略
- 自动git版本控制
- 重要数据云端同步
- 定期系统状态检查

### 持续改进
- 基于使用反馈优化工具
- 集成新的自动化功能
- 扩展数据分析能力

---

*"The best time to plant a tree was 20 years ago. The second best time is now."* - 37岁，正是厚积薄发的时候。

**最后更新：** 2025年1月6日  
**当前版本：** v2.0 - 求职管理系统完整版