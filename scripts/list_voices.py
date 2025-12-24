#!/usr/bin/env python3
"""
列出ElevenLabs可用的声音
"""

import os
import requests
import json

headers = {
    "xi-api-key": api_key
}

# 获取可用的声音列表
response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers)

if response.status_code == 200:
    voices = response.json()['voices']

    print("\n🎙️ ElevenLabs 可用声音列表:\n")
    print("-" * 60)

    # 寻找类似奥巴马或男性深沉声音的
    recommended_voices = []

    for voice in voices:
        voice_id = voice['voice_id']
        name = voice['name']
        category = voice.get('category', 'unknown')
        labels = voice.get('labels', {})
        description = voice.get('description', '')

        print(f"\n📌 {name}")
        print(f"   ID: {voice_id}")
        print(f"   类别: {category}")

        if labels:
            gender = labels.get('gender', 'unknown')
            age = labels.get('age', 'unknown')
            accent = labels.get('accent', 'unknown')
            print(f"   性别: {gender}, 年龄: {age}, 口音: {accent}")

        if description:
            print(f"   描述: {description[:100]}...")

        # 推荐男性深沉声音
        if labels.get('gender') == 'male':
            if any(word in name.lower() for word in ['deep', 'mature', 'authoritative', 'professional']):
                recommended_voices.append((name, voice_id))
            elif labels.get('age') in ['middle_aged', 'old']:
                recommended_voices.append((name, voice_id))

    print("\n" + "=" * 60)
    print("\n🎯 推荐的声音（适合模仿奥巴马）:\n")

    if recommended_voices:
        for name, voice_id in recommended_voices[:5]:  # 显示前5个推荐
            print(f"  • {name}")
            print(f"    export OBAMA_VOICE_ID=\"{voice_id}\"")
    else:
        # 如果没有特别推荐的，选择前几个男声
        male_voices = [v for v in voices if v.get('labels', {}).get('gender') == 'male']
        if male_voices:
            print("  建议选择以下男声之一：")
            for voice in male_voices[:3]:
                print(f"  • {voice['name']}")
                print(f"    export OBAMA_VOICE_ID=\"{voice['voice_id']}\"")

    # 保存完整的声音列表
    output_file = "/mnt/e/LifeOS/data/voice_training/available_voices.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(voices, f, ensure_ascii=False, indent=2)

    print(f"\n💾 完整声音列表已保存到: {output_file}")

else:
    print(f"❌ 获取声音列表失败: {response.status_code}")
    print(response.text)