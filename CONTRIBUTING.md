# 贡献指南

感谢你对 LifeOS 项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告 Bug
1. 检查 [Issues](https://github.com/your-username/lifeos/issues) 确保问题未被报告
2. 使用 Bug Report 模板创建新 Issue
3. 包含详细的重现步骤和环境信息

### 建议新功能
1. 在 [Discussions](https://github.com/your-username/lifeos/discussions) 中先讨论想法
2. 使用 Feature Request 模板创建 Issue
3. 详细描述功能需求和使用场景

### 提交代码
1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

## 📝 开发指南

### 环境设置
```bash
# 克隆项目
git clone https://github.com/your-username/lifeos.git
cd lifeos

# 安装开发版本
./install.sh
```

### 代码规范
- Python 代码遵循 PEP 8 标准
- AppleScript 使用清晰的命名和注释
- 提交信息使用英文，格式：`type: description`

### 测试
```bash
# 运行基础测试
lifeos status

# 测试同步功能
lifeos sync morning
```

## 🎯 贡献领域

我们特别欢迎以下方面的贡献：

### 🐛 Bug 修复
- 修复已知问题
- 改进错误处理
- 提升系统稳定性

### ✨ 新功能
- 支持更多 GTD 工具（Things、Todoist）
- 支持更多笔记工具（Obsidian、Notion）
- 数据分析和可视化
- Web 管理界面

### 📚 文档改进
- 使用指南优化
- API 文档完善
- 视频教程制作
- 多语言翻译

### 🧪 测试用例
- 单元测试覆盖
- 集成测试场景
- 性能测试基准

## 📋 Pull Request 指南

### 提交前检查
- [ ] 代码遵循项目规范
- [ ] 添加必要的测试
- [ ] 更新相关文档
- [ ] 确保现有测试通过

### PR 描述模板
```markdown
## 概述
简要描述这个 PR 的目的

## 变更内容
- [ ] 修复了 XXX 问题
- [ ] 添加了 XXX 功能
- [ ] 更新了 XXX 文档

## 测试
描述如何测试这些变更

## 截图（如有）
添加相关截图

## 相关 Issue
Fixes #123
```

## 🏷️ 版本管理

我们使用语义化版本控制：
- `MAJOR`：不兼容的 API 变更
- `MINOR`：向后兼容的新功能
- `PATCH`：向后兼容的问题修复

## 📞 联系方式

- **讨论**：[GitHub Discussions](https://github.com/your-username/lifeos/discussions)
- **Issues**：[GitHub Issues](https://github.com/your-username/lifeos/issues)

## 📄 许可证

通过向这个项目贡献代码，你同意你的贡献将在 [MIT License](LICENSE) 下授权。