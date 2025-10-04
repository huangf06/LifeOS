#!/usr/bin/env python3
"""
Voice API Implementations - 语音合成API实现
支持多种TTS服务的集成
"""

import os
import requests
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict
import base64
import time

class VoiceProvider(ABC):
    """语音提供商基类"""

    @abstractmethod
    def generate(self, text: str, voice_config: Dict) -> bytes:
        """生成语音"""
        pass

    @abstractmethod
    def check_availability(self) -> bool:
        """检查服务可用性"""
        pass

class ElevenLabsProvider(VoiceProvider):
    """ElevenLabs API实现"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('ELEVENLABS_API_KEY')
        self.base_url = "https://api.elevenlabs.io/v1"
        # 奥巴马声音模型ID（使用Eric作为默认，或自定义）
        self.obama_voice_id = os.environ.get('OBAMA_VOICE_ID', 'cjVigY5qzO86Huf0OWal')

    def generate(self, text: str, voice_config: Dict) -> bytes:
        """使用ElevenLabs生成语音"""
        if not self.api_key:
            raise ValueError("需要设置 ELEVENLABS_API_KEY 环境变量")

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        # 根据语气调整参数
        stability = 0.5  # 稳定性
        similarity_boost = 0.75  # 相似度增强

        if voice_config.get('emphasis') == 'strong':
            stability = 0.3
            similarity_boost = 0.85
        elif voice_config.get('emphasis') == 'measured':
            stability = 0.7
            similarity_boost = 0.65

        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": voice_config.get('style', 0),
                "use_speaker_boost": True
            }
        }

        response = requests.post(
            f"{self.base_url}/text-to-speech/{self.obama_voice_id}",
            json=data,
            headers=headers
        )

        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"ElevenLabs API错误: {response.status_code} - {response.text}")

    def check_availability(self) -> bool:
        """检查API可用性"""
        if not self.api_key:
            return False

        try:
            response = requests.get(
                f"{self.base_url}/user",
                headers={"xi-api-key": self.api_key}
            )
            return response.status_code == 200
        except:
            return False

    def clone_voice(self, audio_files: list, voice_name: str = "Obama Clone"):
        """克隆声音（需要付费订阅）"""
        if not self.api_key:
            raise ValueError("需要设置 ELEVENLABS_API_KEY 环境变量")

        # 准备文件上传
        files = []
        for audio_file in audio_files:
            files.append(('files', open(audio_file, 'rb')))

        data = {
            'name': voice_name,
            'description': 'Obama voice clone for language learning'
        }

        headers = {"xi-api-key": self.api_key}

        response = requests.post(
            f"{self.base_url}/voices/add",
            headers=headers,
            data=data,
            files=files
        )

        if response.status_code == 200:
            voice_data = response.json()
            print(f"✅ 声音克隆成功！Voice ID: {voice_data['voice_id']}")
            return voice_data['voice_id']
        else:
            raise Exception(f"声音克隆失败: {response.status_code} - {response.text}")

class OpenAIWhisperProvider(VoiceProvider):
    """OpenAI TTS实现（备选方案）"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1"

    def generate(self, text: str, voice_config: Dict) -> bytes:
        """使用OpenAI TTS生成语音"""
        if not self.api_key:
            raise ValueError("需要设置 OPENAI_API_KEY 环境变量")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # OpenAI TTS参数调整
        speed = voice_config.get('speed', 1.0)

        data = {
            "model": "tts-1-hd",  # 高质量模型
            "input": text,
            "voice": "onyx",  # 最接近男性深沉声音的选项
            "speed": speed
        }

        response = requests.post(
            f"{self.base_url}/audio/speech",
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"OpenAI API错误: {response.status_code} - {response.text}")

    def check_availability(self) -> bool:
        """检查API可用性"""
        if not self.api_key:
            return False

        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(f"{self.base_url}/models", headers=headers)
            return response.status_code == 200
        except:
            return False

class LocalCoquiProvider(VoiceProvider):
    """本地Coqui TTS实现（开源方案）"""

    def __init__(self):
        self.model_name = "tts_models/en/vctk/vits"
        self.speaker = None  # 将选择最接近的speaker
        self.tts = None

    def _init_model(self):
        """延迟加载模型"""
        if self.tts is None:
            try:
                from TTS.api import TTS
                self.tts = TTS(model_name=self.model_name)
                print("✅ Coqui TTS模型加载成功")
            except ImportError:
                raise Exception("请安装Coqui TTS: pip install TTS")

    def generate(self, text: str, voice_config: Dict) -> bytes:
        """使用Coqui TTS生成语音"""
        self._init_model()

        # 生成临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            output_path = tmp_file.name

        # 生成语音
        self.tts.tts_to_file(
            text=text,
            file_path=output_path,
            speaker=self.speaker,
            language="en",
            speed=voice_config.get('speed', 1.0)
        )

        # 读取生成的音频
        with open(output_path, 'rb') as f:
            audio_data = f.read()

        # 清理临时文件
        os.unlink(output_path)

        return audio_data

    def check_availability(self) -> bool:
        """检查是否可用"""
        try:
            import TTS
            return True
        except ImportError:
            return False

class VoiceManager:
    """语音管理器 - 管理多个提供商"""

    def __init__(self):
        self.providers = {}
        self._init_providers()

    def _init_providers(self):
        """初始化可用的提供商"""
        # 尝试初始化ElevenLabs
        if os.environ.get('ELEVENLABS_API_KEY'):
            self.providers['elevenlabs'] = ElevenLabsProvider()
            print("✅ ElevenLabs provider已启用")

        # 尝试初始化OpenAI
        if os.environ.get('OPENAI_API_KEY'):
            self.providers['openai'] = OpenAIWhisperProvider()
            print("✅ OpenAI TTS provider已启用")

        # 检查本地Coqui
        local_provider = LocalCoquiProvider()
        if local_provider.check_availability():
            self.providers['coqui'] = local_provider
            print("✅ Coqui TTS provider已启用")

        if not self.providers:
            print("⚠️ 警告: 没有可用的语音提供商")
            print("请设置以下环境变量之一:")
            print("  - ELEVENLABS_API_KEY (推荐)")
            print("  - OPENAI_API_KEY")
            print("或安装Coqui TTS: pip install TTS")

    def get_provider(self, preferred: Optional[str] = None) -> Optional[VoiceProvider]:
        """获取语音提供商"""
        if preferred and preferred in self.providers:
            return self.providers[preferred]

        # 优先级: ElevenLabs > OpenAI > Coqui
        for provider_name in ['elevenlabs', 'openai', 'coqui']:
            if provider_name in self.providers:
                return self.providers[provider_name]

        return None

    def list_providers(self) -> list:
        """列出可用的提供商"""
        return list(self.providers.keys())

# 工具函数
def setup_voice_cloning():
    """设置声音克隆的辅助函数"""
    print("\n🎯 声音克隆设置向导\n")
    print("需要准备:")
    print("1. 3-5个奥巴马演讲音频片段（每个30秒-2分钟）")
    print("2. ElevenLabs付费账户（Starter以上）")
    print("3. 设置ELEVENLABS_API_KEY环境变量\n")

    api_key = input("请输入ElevenLabs API Key (或按Enter跳过): ").strip()
    if api_key:
        os.environ['ELEVENLABS_API_KEY'] = api_key

    audio_files = []
    print("\n请输入音频文件路径（输入空行结束）:")
    while True:
        file_path = input("音频文件: ").strip()
        if not file_path:
            break
        if os.path.exists(file_path):
            audio_files.append(file_path)
        else:
            print(f"文件不存在: {file_path}")

    if audio_files and api_key:
        provider = ElevenLabsProvider(api_key)
        try:
            voice_id = provider.clone_voice(audio_files, "Obama Training Voice")
            print(f"\n请将以下内容添加到环境变量:")
            print(f"export OBAMA_VOICE_ID={voice_id}")
            print(f"export ELEVENLABS_API_KEY={api_key}")
            return voice_id
        except Exception as e:
            print(f"❌ 克隆失败: {e}")
            return None
    else:
        print("⚠️ 跳过声音克隆设置")
        return None

if __name__ == "__main__":
    # 测试代码
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_voice_cloning()
    else:
        manager = VoiceManager()
        print(f"\n可用的语音提供商: {manager.list_providers()}")

        # 测试生成
        provider = manager.get_provider()
        if provider:
            test_text = "Yes we can. Together, we can build a better future."
            print(f"\n测试文本: {test_text}")
            print("正在生成语音...")
            try:
                audio = provider.generate(test_text, {"speed": 1.0, "emphasis": "strong"})
                print(f"✅ 生成成功！音频大小: {len(audio)} bytes")
            except Exception as e:
                print(f"❌ 生成失败: {e}")