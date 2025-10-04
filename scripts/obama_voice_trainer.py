#!/usr/bin/env python3
"""
Obama Voice Training System - 奥巴马语音模仿训练系统
用于英语口语训练，通过模仿奥巴马的语音特征提升口语能力
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib
import sys

# 添加语音API支持
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from voice_api import VoiceManager

class ObamaVoiceTrainer:
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / "config"
        self.data_dir = Path(__file__).parent.parent / "data" / "voice_training"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 初始化语音管理器
        self.voice_manager = VoiceManager()
        self.preferred_provider = os.environ.get('VOICE_PROVIDER', 'elevenlabs')

        # 语气模式配置
        self.tone_modes = {
            "inspiring": {
                "name": "激励演讲",
                "speed": 0.95,
                "pitch": 1.05,
                "emphasis": "strong",
                "description": "适合练习演讲和激励性表达"
            },
            "conversational": {
                "name": "日常对话",
                "speed": 1.0,
                "pitch": 1.0,
                "emphasis": "moderate",
                "description": "适合练习日常交流"
            },
            "serious": {
                "name": "严肃正式",
                "speed": 0.9,
                "pitch": 0.95,
                "emphasis": "measured",
                "description": "适合练习正式场合发言"
            },
            "storytelling": {
                "name": "叙事风格",
                "speed": 0.95,
                "pitch": 1.02,
                "emphasis": "varied",
                "description": "适合练习讲故事和叙述"
            }
        }

        # 训练记录
        self.training_log_file = self.data_dir / "training_history.json"
        self.load_training_history()

    def load_training_history(self):
        """加载训练历史"""
        if self.training_log_file.exists():
            with open(self.training_log_file, 'r', encoding='utf-8') as f:
                self.training_history = json.load(f)
        else:
            self.training_history = []

    def save_training_history(self):
        """保存训练历史"""
        with open(self.training_log_file, 'w', encoding='utf-8') as f:
            json.dump(self.training_history, f, ensure_ascii=False, indent=2)

    def generate_voice(self, text: str, tone: str = "conversational",
                      output_file: Optional[str] = None) -> Dict:
        """
        生成奥巴马风格的语音

        Args:
            text: 要朗读的文本
            tone: 语气模式
            output_file: 输出文件路径

        Returns:
            生成结果信息
        """
        if tone not in self.tone_modes:
            raise ValueError(f"不支持的语气模式: {tone}")

        # 生成唯一的文件名
        if not output_file:
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.data_dir / f"obama_voice_{timestamp}_{text_hash}.mp3"
        else:
            output_file = Path(output_file)

        tone_config = self.tone_modes[tone]

        # 获取语音提供商
        provider = self.voice_manager.get_provider(self.preferred_provider)
        if not provider:
            print("⚠️ 没有可用的语音提供商")
            print("请参考以下步骤设置:")
            print("1. 设置 ELEVENLABS_API_KEY 环境变量")
            print("2. 或设置 OPENAI_API_KEY 环境变量")
            print("3. 或安装 Coqui TTS: pip install TTS")
            return {"status": "error", "message": "No voice provider available"}

        try:
            print(f"🎙️ 正在生成语音 (使用 {provider.__class__.__name__})...")

            # 调用API生成音频
            audio_data = provider.generate(text, tone_config)

            # 保存音频文件
            with open(output_file, 'wb') as f:
                f.write(audio_data)

            print(f"✅ 语音生成成功！")

        except Exception as e:
            print(f"❌ 生成失败: {e}")
            return {"status": "error", "message": str(e)}

        result = {
            "status": "success",
            "text": text,
            "tone": tone,
            "tone_config": tone_config,
            "output_file": str(output_file),
            "timestamp": datetime.now().isoformat(),
            "duration_estimate": len(text.split()) * 0.4,  # 估算时长
            "provider": provider.__class__.__name__
        }

        # 记录训练历史
        self.training_history.append({
            "timestamp": result["timestamp"],
            "text": text[:100] + "..." if len(text) > 100 else text,
            "tone": tone,
            "file": str(output_file)
        })
        self.save_training_history()

        print(f"📝 文本: {text[:50]}...")
        print(f"🎭 语气: {tone_config['name']}")
        print(f"📁 输出: {output_file}")

        return result

    def practice_session(self, text_file: str, tone: str = "conversational"):
        """
        创建练习会话

        Args:
            text_file: 包含练习文本的文件
            tone: 语气模式
        """
        with open(text_file, 'r', encoding='utf-8') as f:
            texts = f.read().strip().split('\n\n')

        session_dir = self.data_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n🎯 开始练习会话")
        print(f"📚 共 {len(texts)} 段文本")
        print(f"🎭 语气模式: {self.tone_modes[tone]['name']}\n")

        session_results = []
        for i, text in enumerate(texts, 1):
            if not text.strip():
                continue

            print(f"\n--- 第 {i}/{len(texts)} 段 ---")
            output_file = session_dir / f"segment_{i:02d}.mp3"
            result = self.generate_voice(text, tone, output_file)
            session_results.append(result)

        # 保存会话摘要
        summary_file = session_dir / "session_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "tone": tone,
                "total_segments": len(session_results),
                "segments": session_results
            }, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 练习会话完成！")
        print(f"📁 会话文件保存在: {session_dir}")

        return session_results

    def analyze_progress(self):
        """分析训练进度"""
        if not self.training_history:
            print("还没有训练记录")
            return

        print("\n📊 训练进度分析")
        print("-" * 50)

        # 统计各种语气的使用
        tone_counts = {}
        for record in self.training_history:
            tone = record.get('tone', 'unknown')
            tone_counts[tone] = tone_counts.get(tone, 0) + 1

        print("\n语气模式使用统计:")
        for tone, count in sorted(tone_counts.items(), key=lambda x: x[1], reverse=True):
            if tone in self.tone_modes:
                print(f"  {self.tone_modes[tone]['name']}: {count} 次")

        # 最近的训练
        print("\n最近5次训练:")
        for record in self.training_history[-5:]:
            timestamp = datetime.fromisoformat(record['timestamp'])
            print(f"  {timestamp.strftime('%Y-%m-%d %H:%M')} - {record['tone']} - {record['text'][:30]}...")

        print(f"\n总训练次数: {len(self.training_history)}")

        # 计算今日训练次数
        today = datetime.now().date()
        today_count = sum(1 for r in self.training_history
                         if datetime.fromisoformat(r['timestamp']).date() == today)
        print(f"今日训练: {today_count} 次")

def main():
    parser = argparse.ArgumentParser(description="Obama Voice Training System")
    parser.add_argument('action', choices=['generate', 'practice', 'progress', 'list-tones'],
                       help="执行的操作")
    parser.add_argument('--text', '-t', help="要朗读的文本")
    parser.add_argument('--file', '-f', help="文本文件路径")
    parser.add_argument('--tone', default='conversational',
                       help="语气模式 (inspiring/conversational/serious/storytelling)")
    parser.add_argument('--output', '-o', help="输出文件路径")

    args = parser.parse_args()
    trainer = ObamaVoiceTrainer()

    if args.action == 'generate':
        if not args.text and not args.file:
            print("❌ 请提供文本 (--text) 或文件 (--file)")
            return

        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            text = args.text

        trainer.generate_voice(text, args.tone, args.output)

    elif args.action == 'practice':
        if not args.file:
            print("❌ 请提供练习文本文件 (--file)")
            return
        trainer.practice_session(args.file, args.tone)

    elif args.action == 'progress':
        trainer.analyze_progress()

    elif args.action == 'list-tones':
        print("\n🎭 可用的语气模式:\n")
        for key, config in trainer.tone_modes.items():
            print(f"  {key}: {config['name']}")
            print(f"    {config['description']}\n")

if __name__ == "__main__":
    main()