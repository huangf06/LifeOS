# 故障排除指南

## 🔧 常见问题

### 权限相关问题

#### Q: "Not authorized to send Apple events"
**症状：** 运行同步时出现权限错误
**解决方案：**
1. 系统偏好设置 → 安全性与隐私 → 隐私
2. 左侧选择 "自动化"
3. 找到 "终端" 或 "Terminal"
4. 勾选 "OmniFocus 3"

#### Q: 无法写入 Logseq 文件
**症状：** 提示文件权限错误
**解决方案：**
1. 系统偏好设置 → 安全性与隐私 → 隐私
2. 左侧选择 "完全磁盘访问"
3. 点击 "+" 添加 "终端" 应用
4. 确保已勾选

### 同步相关问题

#### Q: 导出了 0 个任务
**可能原因：**
- OmniFocus 中没有未完成任务
- 任务没有设置截止日期或开始日期
- OmniFocus 没有运行

**解决方案：**
1. 打开 OmniFocus 3
2. 添加几个测试任务
3. 设置截止日期为今天或明天
4. 重新运行 `lifeos sync morning`

#### Q: Logseq 页面没有生成
**检查清单：**
- [ ] Logseq 目录是否存在：`ls ~/logseq/journals`
- [ ] Python 脚本是否有错误：`lifeos status`
- [ ] 权限是否正确设置

### 脚本运行问题

#### Q: "command not found: lifeos"
**解决方案：**
```bash
# 检查全局命令是否安装
ls -la /usr/local/bin/lifeos

# 如果不存在，直接使用脚本路径
~/LifeOS/scripts/morning.sh
~/LifeOS/scripts/evening.sh
```

#### Q: Python 脚本报错
**调试步骤：**
```bash
# 检查 Python 版本
python3 --version

# 检查脚本路径
ls -la ~/LifeOS/scripts/

# 手动运行并查看详细错误
cd ~/LifeOS/scripts
python3 lifeos_sync.py morning
```

## 📊 诊断工具

### 检查系统状态
```bash
# 查看 LifeOS 状态
lifeos status

# 查看最近的同步日志
tail -f ~/LifeOS/logs/morning_$(date +%Y%m%d).log
```

### 验证环境
```bash
# 检查必需软件
python3 --version
osascript -e 'tell application "OmniFocus 3" to get version'
ls /Applications/Logseq.app

# 检查目录结构
tree ~/LifeOS 2>/dev/null || find ~/LifeOS -type d
```

### 测试权限
```bash
# 测试 OmniFocus 访问
osascript -e 'tell application "OmniFocus 3" to get name of every project'

# 测试文件写入
echo "test" > ~/logseq/journals/test.md && rm ~/logseq/journals/test.md
```

## 🔄 重置系统

如果遇到严重问题，可以重置系统：

```bash
# 停止自动化任务
launchctl unload ~/Library/LaunchAgents/com.lifeos.*.plist

# 清理配置文件
rm ~/Library/LaunchAgents/com.lifeos.*.plist

# 清理数据（可选，会丢失历史记录）
rm -rf ~/LifeOS/data/*
rm -rf ~/LifeOS/logs/*

# 重新安装
cd lifeos
./install.sh
```

## 📞 获取帮助

### 自助诊断
1. 查看日志文件：`~/LifeOS/logs/`
2. 运行状态检查：`lifeos status`
3. 查看错误代码：运行命令时的输出

### 社区支持
- **GitHub Issues**: 报告bug和功能请求
- **GitHub Discussions**: 使用问题和经验分享
- **Wiki**: 查看详细文档和FAQ

### 提交Bug报告时请包含：
1. 操作系统版本
2. Python 版本
3. OmniFocus 和 Logseq 版本
4. 错误日志内容
5. 重现步骤