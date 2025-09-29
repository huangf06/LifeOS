#!/bin/bash

# English Speaking Practice Tracker
# 用于跟踪每日英语口语练习的简单脚本

# 配置
PRACTICE_DIR="$HOME/lifeos/career/english-practice"
LOG_FILE="$PRACTICE_DIR/practice-log.md"
RECORDINGS_DIR="$PRACTICE_DIR/recordings"
TODAY=$(date +%Y-%m-%d)

# 创建必要的目录
mkdir -p "$PRACTICE_DIR"
mkdir -p "$RECORDINGS_DIR"

# 初始化日志文件
if [ ! -f "$LOG_FILE" ]; then
    cat > "$LOG_FILE" << 'EOF'
# 英语口语练习记录

## 练习原则
1. 每天开口，哪怕只有1分钟
2. 录音对比，发现进步
3. 不求完美，但求表达

---

EOF
fi

# 功能函数
practice_start() {
    echo "🎯 开始今日英语练习 ($TODAY)"
    echo ""
    echo "选择练习类型："
    echo "1) 英语自言自语（描述所见所想）"
    echo "2) 技术概念解释（选一个技术话题）"
    echo "3) 模拟面试问答（回答一个面试问题）"
    echo "4) 自由录音（任意话题）"
    echo ""
    read -p "请选择 (1-4): " choice
    
    case $choice in
        1)
            practice_type="自言自语"
            prompt="请用英语描述你现在看到的东西，或者正在做的事情。"
            ;;
        2)
            practice_type="技术解释"
            prompt="请选择一个技术概念（如：REST API, Docker, React等），用英语解释给初学者听。"
            ;;
        3)
            practice_type="面试问答"
            prompt="问题：Tell me about yourself / Why do you want this job / Describe a challenging project"
            ;;
        4)
            practice_type="自由练习"
            prompt="任意话题，开始说英语吧！"
            ;;
        *)
            echo "无效选择"
            exit 1
            ;;
    esac
    
    echo ""
    echo "📝 练习类型: $practice_type"
    echo "💡 提示: $prompt"
    echo ""
    echo "准备好后按Enter开始录音（再次按Enter结束录音）..."
    read
    
    # 录音文件名
    recording_file="$RECORDINGS_DIR/${TODAY}_${practice_type// /_}.m4a"
    
    echo "🔴 录音中... (按Ctrl+C结束)"
    
    # macOS录音命令
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # 使用macOS的rec命令（需要先安装sox: brew install sox）
        if command -v rec &> /dev/null; then
            rec -q "$recording_file"
        else
            echo "请先安装sox: brew install sox"
            echo "或使用QuickTime Player录音，保存到: $recording_file"
        fi
    else
        # Linux使用arecord
        arecord -f cd -t wav "$recording_file"
    fi
    
    echo ""
    echo "✅ 录音完成！"
    echo ""
    
    # 自我评估
    echo "请自我评估（1-5分）："
    read -p "流畅度 (1-5): " fluency
    read -p "清晰度 (1-5): " clarity
    read -p "自信度 (1-5): " confidence
    
    echo ""
    read -p "今日突破或感悟（可选）: " breakthrough
    read -p "明日改进重点（可选）: " improvement
    
    # 写入日志
    cat >> "$LOG_FILE" << EOF

## $TODAY

**练习类型**: $practice_type  
**录音文件**: $recording_file  
**练习时长**: 待统计  

**自我评分**:
- 流畅度: $fluency/5
- 清晰度: $clarity/5  
- 自信度: $confidence/5

**今日突破**: $breakthrough  
**明日重点**: $improvement

---
EOF
    
    echo ""
    echo "✨ 太棒了！今天的练习已完成并记录。"
    echo "📊 查看练习记录: $LOG_FILE"
    echo ""
    echo "💪 记住：每天进步0.1%，一年后就是44%的提升！"
}

# 查看进度
show_progress() {
    echo "📈 练习进度统计"
    echo ""
    
    if [ -f "$LOG_FILE" ]; then
        # 统计练习天数
        practice_days=$(grep -c "^## 2" "$LOG_FILE")
        echo "总练习天数: $practice_days 天"
        
        # 显示最近5次练习
        echo ""
        echo "最近练习记录:"
        tail -n 30 "$LOG_FILE" | head -n 20
    else
        echo "还没有练习记录，今天开始第一次吧！"
    fi
}

# 主菜单
echo "======================================"
echo "   英语口语练习助手 🗣️"
echo "======================================"
echo ""
echo "1) 开始今日练习"
echo "2) 查看练习进度"
echo "3) 退出"
echo ""
read -p "请选择: " main_choice

case $main_choice in
    1)
        practice_start
        ;;
    2)
        show_progress
        ;;
    3)
        echo "Goodbye! Keep practicing! 👋"
        exit 0
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac