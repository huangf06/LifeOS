#!/bin/bash
# LifeOS Assistant 自动设置脚本

LIFEOS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🤖 设置 LifeOS Assistant 自动启动..."

# 检测shell类型
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    echo "❌ 不支持的shell类型"
    exit 1
fi

# 创建别名和自动加载
ASSISTANT_SETUP="
# LifeOS Assistant 自动设置
export LIFEOS_PATH='$LIFEOS_DIR'
alias lifeos='cd \$LIFEOS_PATH && ./lifeos'
alias assistant='cd \$LIFEOS_PATH && python3 recall_identity.py'

# Claude Code 启动时自动加载助理身份
if [ \"\$CLAUDE_CODE_SESSION\" = \"true\" ]; then
    cd \$LIFEOS_PATH && python3 recall_identity.py
    echo \"\"
    echo \"✅ 你的个人助理已就绪！直接说出任何需求即可。\"
    echo \"\"
fi
"

# 检查是否已经设置
if grep -q "LifeOS Assistant 自动设置" "$SHELL_RC" 2>/dev/null; then
    echo "⚠️  LifeOS Assistant 已经设置过了"
else
    echo "$ASSISTANT_SETUP" >> "$SHELL_RC"
    echo "✅ 已添加到 $SHELL_RC"
fi

echo ""
echo "🎯 现在你有三种方式激活助理："
echo ""
echo "1. 🚀 自动方式（推荐）："
echo "   export CLAUDE_CODE_SESSION=true"
echo "   然后重启终端，助理会自动加载"
echo ""
echo "2. ⚡ 快捷方式："
echo "   在任何位置输入: assistant"
echo ""
echo "3. 📍 手动方式："
echo "   cd $LIFEOS_DIR && python3 recall_identity.py"
echo ""
echo "推荐使用方式1，每次打开Claude Code都会自动激活助理身份！"