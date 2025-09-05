#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edge-TTS 专用配置
简化的Edge-TTS配置和测试工具
"""

import asyncio
import tempfile
import os
import sys
import subprocess
import time

# Edge-TTS 声音配置
EDGE_TTS_VOICES = {
    "zh-CN": [
        {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓 (女声)", "gender": "female"},
        {"id": "zh-CN-YunxiNeural", "name": "云希 (男声)", "gender": "male"},
        {"id": "zh-CN-YunyangNeural", "name": "云扬 (男声)", "gender": "male"},
        {"id": "zh-CN-XiaoyiNeural", "name": "晓伊 (女声)", "gender": "female"},
        {"id": "zh-CN-YunjianNeural", "name": "云健 (男声)", "gender": "male"},
        {"id": "zh-CN-XiaochenNeural", "name": "晓辰 (女声)", "gender": "female"},
    ],
    "en-US": [
        {"id": "en-US-AriaNeural", "name": "Aria (女声)", "gender": "female"},
        {"id": "en-US-DavisNeural", "name": "Davis (男声)", "gender": "male"},
        {"id": "en-US-JennyNeural", "name": "Jenny (女声)", "gender": "female"},
        {"id": "en-US-GuyNeural", "name": "Guy (男声)", "gender": "male"},
    ]
}

class EdgeTTSConfig:
    """Edge-TTS配置类"""
    
    def __init__(self):
        self.current_voice = "zh-CN-XiaoxiaoNeural"
        self.rate = "+0%"  # 语速
        self.pitch = "+0Hz"  # 音调
        self.volume = "+0%"  # 音量
    
    def set_voice(self, voice_id: str) -> bool:
        """设置声音"""
        for lang_voices in EDGE_TTS_VOICES.values():
            for voice in lang_voices:
                if voice["id"] == voice_id:
                    self.current_voice = voice_id
                    return True
        return False
    
    def get_voice_info(self, voice_id: str = None) -> dict:
        """获取声音信息"""
        voice_id = voice_id or self.current_voice
        for lang_voices in EDGE_TTS_VOICES.values():
            for voice in lang_voices:
                if voice["id"] == voice_id:
                    return voice
        return {}
    
    def list_voices(self, language: str = None) -> list:
        """列出可用声音"""
        if language:
            return EDGE_TTS_VOICES.get(language, [])
        else:
            all_voices = []
            for lang_voices in EDGE_TTS_VOICES.values():
                all_voices.extend(lang_voices)
            return all_voices

# 全局配置实例
edge_tts_config = EdgeTTSConfig()

async def generate_speech_async(text: str, voice_id: str = None, output_file: str = None) -> str:
    """异步生成语音文件"""
    try:
        import edge_tts
        
        voice_id = voice_id or edge_tts_config.current_voice
        config = edge_tts_config
        
        # 创建临时文件
        if not output_file:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                output_file = tmp_file.name
        
        # 生成语音（直接文本，避免SSML被朗读）
        communicate = edge_tts.Communicate(
            text,
            voice=voice_id,
            rate=config.rate,
            volume=config.volume,
            pitch=config.pitch,
        )
        await communicate.save(output_file)
        
        return output_file
        
    except Exception as e:
        print(f"❌ Edge-TTS生成失败: {e}")
        return None

def play_audio_file(audio_file: str) -> bool:
    """播放音频文件"""
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["afplay", audio_file], check=True)
            return True
        elif sys.platform == "linux":
            subprocess.run(["mpg123", audio_file], check=True)
            return True
        elif sys.platform == "win32":
            subprocess.run(["start", audio_file], shell=True, check=True)
            return True
        else:
            print("❌ 不支持的操作系统")
            return False
    except Exception as e:
        print(f"❌ 播放音频失败: {e}")
        return False

def speak_text(text: str, voice_id: str = None) -> bool:
    """语音合成并播放"""
    try:
        print(f"🔊 Edge-TTS播放: {text}")
        
        # 异步生成语音
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_file = loop.run_until_complete(generate_speech_async(text, voice_id))
        loop.close()
        
        if audio_file and os.path.exists(audio_file):
            # 播放音频
            success = play_audio_file(audio_file)
            
            # 清理临时文件
            try:
                os.unlink(audio_file)
            except:
                pass
            
            return success
        else:
            print("❌ 语音生成失败")
            return False
            
    except Exception as e:
        print(f"❌ Edge-TTS播放失败: {e}")
        return False

def test_edge_tts():
    """测试Edge-TTS功能"""
    print("🧪 测试Edge-TTS功能...")
    
    # 测试中文语音
    print("\n🇨🇳 测试中文语音:")
    chinese_voices = edge_tts_config.list_voices("zh-CN")
    for voice in chinese_voices[:2]:  # 只测试前两个
        print(f"  - 测试声音: {voice['name']}")
        if speak_text("你好，我是" + voice['name'] + "，很高兴为您服务。", voice['id']):
            print("    ✅ 测试成功")
        else:
            print("    ❌ 测试失败")
        time.sleep(1)
    
    # 测试英文语音
    print("\n🇺🇸 测试英文语音:")
    english_voices = edge_tts_config.list_voices("en-US")
    for voice in english_voices[:2]:  # 只测试前两个
        print(f"  - 测试声音: {voice['name']}")
        if speak_text("Hello, I am " + voice['name'] + ", nice to meet you.", voice['id']):
            print("    ✅ 测试成功")
        else:
            print("    ❌ 测试失败")
        time.sleep(1)

def interactive_voice_selection():
    """交互式声音选择"""
    print("\n🎵 Edge-TTS声音选择")
    print("=" * 30)
    
    while True:
        print("\n选项:")
        print("1. 查看所有声音")
        print("2. 查看中文声音")
        print("3. 查看英文声音")
        print("4. 测试声音")
        print("5. 设置当前声音")
        print("0. 退出")
        
        choice = input("\n请选择 (0-5): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            voices = edge_tts_config.list_voices()
            print(f"\n🎤 所有声音 (共{len(voices)}个):")
            for i, voice in enumerate(voices, 1):
                current = " (当前)" if voice['id'] == edge_tts_config.current_voice else ""
                print(f"  {i:2d}. {voice['name']} ({voice['gender']}){current}")
        elif choice == "2":
            voices = edge_tts_config.list_voices("zh-CN")
            print(f"\n🇨🇳 中文声音 (共{len(voices)}个):")
            for i, voice in enumerate(voices, 1):
                current = " (当前)" if voice['id'] == edge_tts_config.current_voice else ""
                print(f"  {i:2d}. {voice['name']} ({voice['gender']}){current}")
        elif choice == "3":
            voices = edge_tts_config.list_voices("en-US")
            print(f"\n🇺🇸 英文声音 (共{len(voices)}个):")
            for i, voice in enumerate(voices, 1):
                current = " (当前)" if voice['id'] == edge_tts_config.current_voice else ""
                print(f"  {i:2d}. {voice['name']} ({voice['gender']}){current}")
        elif choice == "4":
            test_text = input("请输入测试文本 (回车使用默认): ").strip()
            if not test_text:
                test_text = "这是一个Edge-TTS测试。"
            speak_text(test_text)
        elif choice == "5":
            voices = edge_tts_config.list_voices()
            print(f"\n🎤 选择声音 (1-{len(voices)}):")
            for i, voice in enumerate(voices, 1):
                current = " (当前)" if voice['id'] == edge_tts_config.current_voice else ""
                print(f"  {i:2d}. {voice['name']} ({voice['gender']}){current}")
            
            try:
                voice_num = int(input("请选择声音编号: "))
                if 1 <= voice_num <= len(voices):
                    voice_id = voices[voice_num-1]['id']
                    if edge_tts_config.set_voice(voice_id):
                        print(f"✅ 已设置声音: {voices[voice_num-1]['name']}")
                    else:
                        print("❌ 设置失败")
                else:
                    print("❌ 无效编号")
            except ValueError:
                print("❌ 请输入有效数字")
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    print("🎤 Edge-TTS 配置和测试工具")
    print("=" * 40)
    
    # 检查Edge-TTS是否可用
    try:
        import edge_tts
        print("✅ Edge-TTS 已安装")
    except ImportError:
        print("❌ Edge-TTS 未安装，请运行: pip install edge-tts")
        sys.exit(1)
    
    # 显示当前配置
    current_voice = edge_tts_config.get_voice_info()
    print(f"当前声音: {current_voice.get('name', 'Unknown')} ({current_voice.get('gender', 'Unknown')})")
    
    # 测试功能
    test_edge_tts()
    
    # 交互式配置
    interactive_voice_selection()
    
    print("\n👋 再见！")
