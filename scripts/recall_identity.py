#!/usr/bin/env python3
"""
LifeOS Assistant Identity Recall
用于快速提醒AI助理的身份和职责
"""

import json
from pathlib import Path

def show_identity():
    """显示助理身份信息"""
    config_path = Path("config/assistant_profile.json")
    
    if not config_path.exists():
        print("❌ 助理配置文件不存在")
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)
    
    identity = profile["assistant_identity"]
    
    print("🤖 LifeOS Assistant Identity")
    print("=" * 30)
    print(f"角色: {identity['role']}")
    print(f"名称: {identity['name']}")
    print()
    
    print("🎯 核心职责:")
    for func in identity['primary_functions']:
        print(f"  • {func}")
    print()
    
    print("🚀 关键行为:")
    for behavior in profile['context_reminders'][:3]:  # 显示前3个最重要的
        print(f"  • {behavior}")
    print()
    
    print("⚡ 默认行为模式:")
    for key, value in identity['default_behaviors'].items():
        print(f"  • {key.replace('_', ' ').title()}: {value}")

if __name__ == "__main__":
    show_identity()