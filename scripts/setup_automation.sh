#!/bin/bash
# LifeOS 自动化设置脚本

set -e

LIFEOS_DIR="$HOME/LifeOS"
SCRIPT_DIR="$LIFEOS_DIR/scripts"
DATA_DIR="$LIFEOS_DIR/data"
LOGSEQ_DIR="$HOME/logseq"

echo "🚀 设置 LifeOS 自动化环境..."

# 创建必要的目录
echo "📁 创建目录结构..."
mkdir -p "$LIFEOS_DIR"/{scripts,data,logs}
mkdir -p "$LOGSEQ_DIR/journals"

# 设置脚本权限
echo "🔑 设置脚本权限..."
chmod +x "$SCRIPT_DIR/lifeos_sync.py"
chmod +x "$SCRIPT_DIR/setup_automation.sh"

# 创建快捷启动脚本
echo "⚡ 创建快捷启动脚本..."

# 晨间同步脚本
cat > "$SCRIPT_DIR/morning_sync.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🌅 开始 LifeOS 晨间同步..."
python3 lifeos_sync.py morning 2>&1 | tee ../logs/morning_$(date +%Y%m%d).log

# 打开应用
echo "🚀 打开应用..."
open -a "Logseq" 
# open -a "OmniFocus 3"  # 可选
EOF

# 晚间同步脚本
cat > "$SCRIPT_DIR/evening_sync.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🌙 开始 LifeOS 晚间同步..."
python3 lifeos_sync.py evening 2>&1 | tee ../logs/evening_$(date +%Y%m%d).log
EOF

# 状态检查脚本
cat > "$SCRIPT_DIR/check_status.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 lifeos_sync.py status
EOF

# 设置新脚本权限
chmod +x "$SCRIPT_DIR"/{morning_sync.sh,evening_sync.sh,check_status.sh}

# 创建 LaunchAgent 配置文件（macOS 自动化）
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$LAUNCH_AGENTS_DIR"

echo "⏰ 配置定时任务..."

# 晨间同步 LaunchAgent
cat > "$LAUNCH_AGENTS_DIR/com.lifeos.morning.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lifeos.morning</string>
    <key>ProgramArguments</key>
    <array>
        <string>$SCRIPT_DIR/morning_sync.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>$LIFEOS_DIR/logs/morning_launchd.log</string>
    <key>StandardErrorPath</key>
    <string>$LIFEOS_DIR/logs/morning_launchd_error.log</string>
</dict>
</plist>
EOF

# 晚间同步 LaunchAgent
cat > "$LAUNCH_AGENTS_DIR/com.lifeos.evening.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lifeos.evening</string>
    <key>ProgramArguments</key>
    <array>
        <string>$SCRIPT_DIR/evening_sync.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>21</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>$LIFEOS_DIR/logs/evening_launchd.log</string>
    <key>StandardErrorPath</key>
    <string>$LIFEOS_DIR/logs/evening_launchd_error.log</string>
</dict>
</plist>
EOF

# 加载 LaunchAgent
echo "🔄 加载自动化任务..."
launchctl load "$LAUNCH_AGENTS_DIR/com.lifeos.morning.plist"
launchctl load "$LAUNCH_AGENTS_DIR/com.lifeos.evening.plist"

# 创建手动触发的快捷命令
echo "📱 创建快捷命令..."

# 添加到 .zshrc 或 .bashrc
SHELL_RC=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    echo "" >> "$SHELL_RC"
    echo "# LifeOS 快捷命令" >> "$SHELL_RC"
    echo "alias lifeos-morning='$SCRIPT_DIR/morning_sync.sh'" >> "$SHELL_RC"
    echo "alias lifeos-evening='$SCRIPT_DIR/evening_sync.sh'" >> "$SHELL_RC"
    echo "alias lifeos-status='$SCRIPT_DIR/check_status.sh'" >> "$SHELL_RC"
    echo "" >> "$SHELL_RC"
    
    echo "✅ 已添加快捷命令到 $SHELL_RC"
fi

# 创建桌面快捷方式（可选）
DESKTOP_DIR="$HOME/Desktop"
if [ -d "$DESKTOP_DIR" ]; then
    cat > "$DESKTOP_DIR/LifeOS Morning.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/../LifeOS/scripts"
./morning_sync.sh
read -p "按回车键关闭..."
EOF
    
    cat > "$DESKTOP_DIR/LifeOS Evening.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/../LifeOS/scripts"  
./evening_sync.sh
read -p "按回车键关闭..."
EOF
    
    chmod +x "$DESKTOP_DIR/LifeOS Morning.command"
    chmod +x "$DESKTOP_DIR/LifeOS Evening.command"
    
    echo "🖥️ 已创建桌面快捷方式"
fi

# 测试安装
echo "🧪 测试安装..."
echo "检查 Python 环境..."
python3 --version

echo "检查脚本权限..."
ls -la "$SCRIPT_DIR/"

echo "检查目录结构..."
tree "$LIFEOS_DIR" 2>/dev/null || find "$LIFEOS_DIR" -type d

echo ""
echo "✅ LifeOS 自动化设置完成！"
echo ""
echo "📋 使用方法："
echo "  手动执行："
echo "    晨间同步: $SCRIPT_DIR/morning_sync.sh"
echo "    晚间同步: $SCRIPT_DIR/evening_sync.sh"
echo "    查看状态: $SCRIPT_DIR/check_status.sh"
echo ""
echo "  终端快捷命令（重启终端后生效）："
echo "    lifeos-morning"
echo "    lifeos-evening" 
echo "    lifeos-status"
echo ""
echo "  自动执行："
echo "    每天 08:00 - 自动晨间同步"
echo "    每天 21:00 - 自动晚间同步"
echo ""
echo "🎯 现在可以运行第一次同步："
echo "   $SCRIPT_DIR/morning_sync.sh"
echo ""
echo "⚠️ 首次运行前请确保："
echo "   1. OmniFocus 3 已安装且有任务"
echo "   2. Logseq 已安装并设置了 Graph 路径"
echo "   3. 已授予必要的权限（自动化、文件访问）"