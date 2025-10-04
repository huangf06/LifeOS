#!/bin/bash
# ElevenLabs配置脚本

# 设置API Key
export ELEVENLABS_API_KEY="sk_90254ef2456928d089bd66ce71d8fff2ab0370bf15bcef07"

# 设置默认语音ID (可以选择以下任一)
# Eric - 中年美国男性，平滑专业的声音（默认）
export OBAMA_VOICE_ID="cjVigY5qzO86Huf0OWal"

# 其他推荐的声音选项：
# Clyde - 中年美国男性，适合角色扮演
# export OBAMA_VOICE_ID="2EiwWnXFnvU5JabPnv8n"

# Roger - 中年美国男性，轻松随意
# export OBAMA_VOICE_ID="CwhRBWXzGAHq8TQ4Fs17"

# Brian - 中年美国男性，共鸣温暖
# export OBAMA_VOICE_ID="nPczCjzI2devNBz1zQrb"

# Bill - 老年美国男性，友好舒适
# export OBAMA_VOICE_ID="pqHfZKP75CvOlQylNhV4"

# 设置默认提供商
export VOICE_PROVIDER="elevenlabs"

echo "✅ ElevenLabs 配置已加载"
echo "📌 当前使用声音: Eric (ID: $OBAMA_VOICE_ID)"
echo ""
echo "可用命令："
echo "  ./lifeos obama speak '文本' [语气]  # 生成语音"
echo "  ./lifeos obama practice file.txt    # 练习会话"
echo "  ./lifeos obama progress             # 查看进度"
echo "  ./lifeos obama tones                # 查看语气模式"