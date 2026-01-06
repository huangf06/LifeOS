# Vibe Coding 环境配置指南

**给妹妹的傻瓜操作手册** - 一步一步照做就行

---

## 第一步：打开 PowerShell（管理员模式）

1. 按键盘上的 **Windows 键**（左下角那个田字格）
2. 输入 `powershell`
3. 看到"Windows PowerShell"，**右键点击**
4. 选择 **"以管理员身份运行"**
5. 弹出窗口问你"是否允许"，点 **"是"**

✅ 现在你面前有一个蓝色/黑色的命令窗口

---

## 第二步：安装必要工具

把下面这段代码**全部复制**，粘贴到命令窗口里，按回车：

```powershell
winget install --id OpenJS.NodeJS.LTS --silent --accept-source-agreements --accept-package-agreements
winget install --id Microsoft.VisualStudioCode --silent --accept-source-agreements --accept-package-agreements
winget install --id Git.Git --silent --accept-source-agreements --accept-package-agreements
winget install --id Microsoft.WindowsTerminal --silent --accept-source-agreements --accept-package-agreements
```

⏳ 等待安装完成（大约 3-5 分钟），看到命令行不再滚动就是装好了

✅ 完成后，**关闭这个窗口**

---

## 第三步：重新打开命令窗口

1. 按 **Windows 键**
2. 输入 `terminal`
3. 点击 **"终端"**（或 Windows Terminal）

这次不用管理员模式了，直接点开就行

---

## 第四步：安装 AI 编程助手

把下面这行代码复制粘贴，按回车：

```powershell
npm install -g @anthropic-ai/claude-code
```

⏳ 等待安装完成（大约 1-2 分钟）

---

## 第五步：创建你的工作文件夹

把下面这段代码复制粘贴，按回车：

```powershell
mkdir "$HOME\Documents\my-websites"
cd "$HOME\Documents\my-websites"
```

---

## 第六步：登录 AI 助手

输入下面这个命令，按回车：

```powershell
claude
```

🌐 **会自动打开浏览器**，让你登录 Anthropic 账号

1. 如果没有账号，点 **"Sign up"** 注册一个（用邮箱就行）
2. 如果有账号，直接登录
3. 登录成功后，浏览器会显示"授权成功"之类的提示
4. **回到命令窗口**，你会看到 Claude 已经准备好了

✅ 看到 `>` 或者 Claude 的提示符，说明登录成功

---

## 第七步：开始用 AI 写网页！

现在你可以用中文告诉 AI 你想要什么网页了，比如：

```
帮我做一个个人介绍网页，要有我的名字、照片位置、还有自我介绍
```

或者：

```
帮我做一个生日倒计时网页，倒计时到2025年3月15日
```

AI 会帮你写代码，写完后会告诉你文件在哪里。

---

## 怎么看做出来的网页？

1. 打开 **文件资源管理器**（就是那个黄色文件夹图标）
2. 进入 `文档` → `my-websites`
3. 找到 `.html` 结尾的文件
4. **双击打开**，就能在浏览器里看到你的网页啦！

---

## 常用命令速查

| 你想做什么 | 输入什么 |
|-----------|---------|
| 启动 AI 助手 | `claude` |
| 退出 AI 助手 | 输入 `/exit` 或按 `Ctrl + C` |
| 进入工作文件夹 | `cd "$HOME\Documents\my-websites"` |

---

## 遇到问题？

### 问题1：winget 命令不认识
说明 Windows 版本太旧，需要更新 Windows 或者手动下载安装：
- Node.js: https://nodejs.org （点 LTS 版本下载）
- VS Code: https://code.visualstudio.com
- Git: https://git-scm.com

### 问题2：npm 命令不认识
关闭命令窗口，重新打开再试

### 问题3：登录页面打不开
检查网络，或者用手机热点试试

---

## 附加：让命令窗口更好看

1. 打开 **终端**（Windows Terminal）
2. 按 `Ctrl + ,`（逗号键）打开设置
3. 左边选 **"默认值"** → **"外观"**
4. 把 **"配色方案"** 改成 `One Half Dark`
5. 把 **"字号"** 改成 `14`
6. 点右下角 **"保存"**

这样看起来就舒服多了！

---

## 第八步：(进阶) 在 VS Code 里直接用 AI

如果你不想一直切换窗口，可以直接在编辑器里用 AI：

1. 打开 **Visual Studio Code**
2. 点击左侧最下面的 **方块图标** (扩展)
3. 搜索 `Roo Code` 并点击安装
4. 安装好后，左侧会出现一个 **小火箭** 图标
5. 点击火箭，它会让你输入 API Key
   - 去 [console.anthropic.com](https://console.anthropic.com) 申请一个 Key
   - 粘贴进去，模型选 `Claude 3.5 Sonnet`

这样你就可以在写代码的时候直接问 AI 啦！

---

**搞定！现在你可以用中文指挥 AI 帮你写网页了** 🎉
