#!/bin/bash

# LifeOS 一键安装脚本
# 自动设置 OmniFocus + Logseq 同步系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 图标定义
SUCCESS="✅"
ERROR="❌"
WARNING="⚠️"
INFO="ℹ️"
ROCKET="🚀"

# 配置变量
LIFEOS_DIR="$HOME/LifeOS"
LOGSEQ_DIR="$HOME/logseq"
INSTALL_DIR="$(pwd)"

# 日志函数
log_info() {
    echo -e "${BLUE}${INFO} $1${NC}"
}

log_success() {
    echo -e "${GREEN}${SUCCESS} $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}${WARNING} $1${NC}"
}

log_error() {
    echo -e "${RED}${ERROR} $1${NC}"
}

# 显示欢迎信息
show_welcome() {
    clear
    echo -e "${BLUE}"
    cat << "EOF"
    ╦  ┬┌─┐┌─┐╔═╗╔═╗
    ║  │├┤ ├┤ ║ ║╚═╗
    ╩═╝┴└  └─┘╚═╝╚═╝
    Personal Life Operating System
EOF
    echo -e "${NC}"
    echo -e "${GREEN}欢迎使用 LifeOS 安装程序！${NC}"
    echo
    echo "这个脚本将帮你设置 OmniFocus + Logseq 自动同步系统"
    echo "预计安装时间：3-5分钟"
    echo
    read -p "按回车键继续安装..."
}

# 检查系统要求
check_requirements() {
    log_info "检查系统要求..."
    
    # 检查 macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "此系统仅支持 macOS"
        exit 1
    fi
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "未找到 Python 3，请先安装 Python"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
    log_success "Python $PYTHON_VERSION 已安装"
    
    # 检查 OmniFocus
    if ! pgrep -f "OmniFocus" > /dev/null; then
        log_warning "OmniFocus 3 未运行，请确保已安装并打开"
    else
        log_success "检测到 OmniFocus 3 正在运行"
    fi
    
    # 检查 Logseq
    LOGSEQ_APP="/Applications/Logseq.app"
    if [[ ! -d "$LOGSEQ_APP" ]]; then
        log_warning "未检测到 Logseq 应用，请确保已安装"
        log_info "可从 https://logseq.com 下载安装"
    else
        log_success "检测到 Logseq 应用"
    fi
}

# 创建目录结构
setup_directories() {
    log_info "创建目录结构..."
    
    # 创建 LifeOS 目录
    mkdir -p "$LIFEOS_DIR"/{scripts,data,logs,config}
    
    # 创建 Logseq 目录
    mkdir -p "$LOGSEQ_DIR/journals"
    
    log_success "目录结构创建完成"
    echo "  LifeOS: $LIFEOS_DIR"
    echo "  Logseq: $LOGSEQ_DIR"
}

# 安装核心脚本
install_scripts() {
    log_info "安装核心脚本..."
    
    # 复制脚本文件
    if [[ -f "$INSTALL_DIR/scripts/lifeos_sync.py" ]]; then
        cp "$INSTALL_DIR/scripts/lifeos_sync.py" "$LIFEOS_DIR/scripts/"
        chmod +x "$LIFEOS_DIR/scripts/lifeos_sync.py"
        log_success "Python 同步引擎安装完成"
    else
        log_error "未找到 lifeos_sync.py 脚本文件"
        exit 1
    fi
    
    if [[ -f "$INSTALL_DIR/scripts/omnifocus_export.scpt" ]]; then
        cp "$INSTALL_DIR/scripts/omnifocus_export.scpt" "$LIFEOS_DIR/scripts/"
        log_success "OmniFocus 导出脚本安装完成"
    else
        log_error "未找到 omnifocus_export.scpt 脚本文件"
        exit 1
    fi
}

# 创建快捷脚本
create_shortcuts() {
    log_info "创建快捷脚本..."
    
    # 晨间同步脚本
    cat > "$LIFEOS_DIR/scripts/morning.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🌅 开始 LifeOS 晨间同步..."
python3 lifeos_sync.py morning 2>&1 | tee "../logs/morning_$(date +%Y%m%d).log"
echo "🚀 打开 Logseq..."
open -a "Logseq"
EOF
    
    # 晚间同步脚本
    cat > "$LIFEOS_DIR/scripts/evening.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🌙 开始 LifeOS 晚间同步..."
python3 lifeos_sync.py evening 2>&1 | tee "../logs/evening_$(date +%Y%m%d).log"
EOF
    
    # 状态检查脚本
    cat > "$LIFEOS_DIR/scripts/status.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 lifeos_sync.py status
EOF
    
    # 设置权限
    chmod +x "$LIFEOS_DIR/scripts"/{morning.sh,evening.sh,status.sh}
    
    log_success "快捷脚本创建完成"
}

# 创建命令行工具
create_cli_tool() {
    log_info "创建命令行工具..."
    
    # 创建全局命令脚本
    cat > "/usr/local/bin/lifeos" << EOF
#!/bin/bash
LIFEOS_DIR="$LIFEOS_DIR"
case "\$1" in
    sync)
        if [[ "\$2" == "morning" ]]; then
            "\$LIFEOS_DIR/scripts/morning.sh"
        elif [[ "\$2" == "evening" ]]; then
            "\$LIFEOS_DIR/scripts/evening.sh"
        else
            echo "用法: lifeos sync [morning|evening]"
        fi
        ;;
    status)
        "\$LIFEOS_DIR/scripts/status.sh"
        ;;
    *)
        echo "LifeOS - Personal Life Operating System"
        echo
        echo "用法:"
        echo "  lifeos sync morning    # 晨间同步"
        echo "  lifeos sync evening    # 晚间同步"
        echo "  lifeos status          # 查看状态"
        echo
        echo "详细文档: https://github.com/your-username/lifeos"
        ;;
esac
EOF
    
    # 设置权限
    sudo chmod +x "/usr/local/bin/lifeos" 2>/dev/null || {
        log_warning "无法创建全局命令，需要管理员权限"
        log_info "你可以手动运行: $LIFEOS_DIR/scripts/morning.sh"
        return 1
    }
    
    log_success "命令行工具 'lifeos' 安装完成"
}

# 设置自动化任务
setup_automation() {
    log_info "设置自动化任务..."
    
    LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
    mkdir -p "$LAUNCH_AGENTS_DIR"
    
    # 晨间自动化
    cat > "$LAUNCH_AGENTS_DIR/com.lifeos.morning.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lifeos.morning</string>
    <key>ProgramArguments</key>
    <array>
        <string>$LIFEOS_DIR/scripts/morning.sh</string>
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
    <string>$LIFEOS_DIR/logs/morning_auto.log</string>
    <key>StandardErrorPath</key>
    <string>$LIFEOS_DIR/logs/morning_auto_error.log</string>
</dict>
</plist>
EOF
    
    # 晚间自动化
    cat > "$LAUNCH_AGENTS_DIR/com.lifeos.evening.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lifeos.evening</string>
    <key>ProgramArguments</key>
    <array>
        <string>$LIFEOS_DIR/scripts/evening.sh</string>
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
    <string>$LIFEOS_DIR/logs/evening_auto.log</string>
    <key>StandardErrorPath</key>
    <string>$LIFEOS_DIR/logs/evening_auto_error.log</string>
</dict>
</plist>
EOF
    
    # 加载自动化任务
    launchctl load "$LAUNCH_AGENTS_DIR/com.lifeos.morning.plist" 2>/dev/null
    launchctl load "$LAUNCH_AGENTS_DIR/com.lifeos.evening.plist" 2>/dev/null
    
    log_success "自动化任务设置完成"
    echo "  每天 08:00 - 自动晨间同步"
    echo "  每天 21:00 - 自动晚间同步"
}

# 测试安装
test_installation() {
    log_info "测试安装..."
    
    # 测试脚本存在
    if [[ -f "$LIFEOS_DIR/scripts/lifeos_sync.py" ]]; then
        log_success "核心脚本安装正确"
    else
        log_error "核心脚本安装失败"
        return 1
    fi
    
    # 测试 Python 脚本
    cd "$LIFEOS_DIR/scripts"
    if python3 lifeos_sync.py status &>/dev/null; then
        log_success "Python 脚本运行正常"
    else
        log_warning "Python 脚本测试失败，可能需要权限设置"
    fi
    
    # 测试快捷脚本
    if [[ -x "$LIFEOS_DIR/scripts/morning.sh" ]]; then
        log_success "快捷脚本权限设置正确"
    else
        log_error "快捷脚本权限设置失败"
        return 1
    fi
}

# 显示权限设置指导
show_permission_guide() {
    echo
    log_warning "重要：需要设置系统权限"
    echo
    echo "请按以下步骤设置权限："
    echo
    echo "1. 打开 系统偏好设置 > 安全性与隐私 > 隐私"
    echo
    echo "2. 左侧选择 '自动化'"
    echo "   - 找到 '终端' 或 'Terminal'"
    echo "   - 勾选 'OmniFocus 3'"
    echo
    echo "3. 左侧选择 '完全磁盘访问'"
    echo "   - 点击 '+' 添加 '终端' 应用"
    echo "   - 确保已勾选"
    echo
    echo "4. 如果看不到相关选项，请先运行一次同步："
    echo "   lifeos sync morning"
    echo
    read -p "权限设置完成后按回车键继续..."
}

# 首次运行测试
first_run_test() {
    log_info "进行首次运行测试..."
    
    echo "即将运行第一次晨间同步，这将："
    echo "1. 从 OmniFocus 导出今日任务"
    echo "2. 在 Logseq 中创建今日日志页面"
    echo "3. 自动打开 Logseq 查看结果"
    echo
    read -p "确认继续？(y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "运行首次同步..."
        cd "$LIFEOS_DIR/scripts"
        
        if ./morning.sh; then
            log_success "首次同步成功！"
            echo
            echo "请检查 Logseq 是否自动打开并显示了今日页面"
            echo "如果看到任务列表，说明安装成功！"
        else
            log_error "首次同步失败"
            echo "请检查权限设置或查看错误日志："
            echo "  tail -f $LIFEOS_DIR/logs/morning_$(date +%Y%m%d).log"
        fi
    else
        log_info "跳过首次测试"
    fi
}

# 显示完成信息
show_completion() {
    clear
    echo -e "${GREEN}"
    cat << "EOF"
    🎉 安装完成！
    
    ╦  ┬┌─┐┌─┐╔═╗╔═╗
    ║  │├┤ ├┤ ║ ║╚═╗
    ╩═╝┴└  └─┘╚═╝╚═╝
EOF
    echo -e "${NC}"
    
    log_success "LifeOS 安装成功！"
    echo
    echo "🚀 使用方法："
    echo "  lifeos sync morning    # 晨间同步"
    echo "  lifeos sync evening    # 晚间同步"
    echo "  lifeos status          # 查看状态"
    echo
    echo "📁 安装位置："
    echo "  核心文件: $LIFEOS_DIR"
    echo "  日志文件: $LIFEOS_DIR/logs"
    echo "  Logseq: $LOGSEQ_DIR"
    echo
    echo "⏰ 自动化："
    echo "  每天 08:00 AM - 自动晨间同步"
    echo "  每天 09:00 PM - 自动晚间同步"
    echo
    echo "📚 更多帮助："
    echo "  文档: https://github.com/your-username/lifeos"
    echo "  问题: https://github.com/your-username/lifeos/issues"
    echo
    echo "💡 建议："
    echo "  1. 在 OmniFocus 中添加一些测试任务"
    echo "  2. 运行 'lifeos sync morning' 体验同步"
    echo "  3. 在 Logseq 中记录工作过程"
    echo "  4. 晚上运行 'lifeos sync evening' 同步状态"
    echo
    echo "🌟 如果觉得有用，请给项目点个 Star！"
}

# 主安装流程
main() {
    show_welcome
    check_requirements
    setup_directories
    install_scripts
    create_shortcuts
    create_cli_tool
    setup_automation
    test_installation
    show_permission_guide
    first_run_test
    show_completion
}

# 错误处理
trap 'log_error "安装过程中发生错误，请查看错误信息并重试"; exit 1' ERR

# 运行主程序
main "$@"