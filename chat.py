import sounddevice as sd
import numpy as np
import wave
import sys
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import subprocess
import warnings

# 屏蔽pydub关于ffmpeg的无害告警
warnings.filterwarnings(
    "ignore",
    message="Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work",
    category=RuntimeWarning,
    module="pydub.utils",
)

# 添加模型路径到系统路径
sys.path.append('./models/pyAudioAnalysis')

# ---------------- 配置 ----------------
ASR_MODEL_PATH = "./models/SenseVoiceSmall"   # SenseVoice 模型路径
SAMPLE_RATE = 16000
RECORD_SECONDS = 5

# 对话历史管理
conversation_history = []
# --------------------------------------

def record_audio(filename="input.wav"):
    print("🎙️ 录音中...")
    print("💡 请清晰地说出你的话，保持适中的音量...")
    
    # 增加录音时长，给用户更多时间
    record_duration = RECORD_SECONDS + 1  # 6秒
    
    audio = sd.rec(int(record_duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()
    
    # 检查录音音量
    max_volume = np.max(np.abs(audio))
    if max_volume < 1000:  # 音量太低
        print("⚠️ 录音音量较低，可能影响识别效果")
    elif max_volume > 30000:  # 音量太高
        print("⚠️ 录音音量较高，可能影响识别效果")
    else:
        print("✅ 录音音量正常")
    
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(audio.tobytes())
    wf.close()
    print("✅ 录音完成:", filename)

def vad_trim(input_file="input.wav"):
    print("🔍 VAD 检测语音段落...")
    try:
        # 检查音频文件是否存在
        if not os.path.exists(input_file):
            print(f"⚠️ 音频文件不存在: {input_file}")
            return input_file
        
        # 尝试使用pyAudioAnalysis进行VAD
        try:
            from pyAudioAnalysis.audioSegmentation import silence_removal
            from pyAudioAnalysis.audioBasicIO import read_audio_file
            
            # 正确的方式：先读取音频数据，再传递给silence_removal
            [Fs, x] = read_audio_file(input_file)
            segments = silence_removal(x, Fs, 0.020, 0.020, smooth_window=1.0, weight=0.3)
            
            if len(segments) == 0:
                print("🔍 未检测到语音段落，使用原始音频")
                return input_file
                
            # 取第一个语音段落
            start_time, end_time = segments[0]
            start_sample = int(start_time * SAMPLE_RATE)
            end_sample = int(end_time * SAMPLE_RATE)
            
            # 读取音频数据
            wf = wave.open(input_file, 'rb')
            frames = wf.readframes(wf.getnframes())
            audio = np.frombuffer(frames, dtype=np.int16)
            wf.close()
            
            # 截取语音段落
            trimmed = audio[start_sample:end_sample]
            
            # 保存截取后的音频
            out_file = "trimmed.wav"
            with wave.open(out_file, 'wb') as wf_out:
                wf_out.setnchannels(1)
                wf_out.setsampwidth(2)
                wf_out.setframerate(SAMPLE_RATE)
                wf_out.writeframes(trimmed.tobytes())
                
            print(f"✅ VAD处理完成，语音段落: {start_time:.2f}s - {end_time:.2f}s")
            return out_file
            
        except Exception as vad_error:
            print(f"⚠️ pyAudioAnalysis VAD失败: {vad_error}")
            print("🔄 使用简单VAD处理")
            return simple_vad_trim(input_file)
        
    except Exception as e:
        print(f"⚠️ VAD处理出错: {e}")
        print("🔄 使用原始音频文件")
        return input_file

def simple_vad_trim(input_file="input.wav"):
    """简单的VAD处理，基于音量阈值"""
    try:
        # 读取音频数据
        wf = wave.open(input_file, 'rb')
        frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16)
        wf.close()
        
        # 计算音量阈值
        rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
        threshold = rms * 0.3  # 30%的RMS作为阈值
        
        # 找到非静音段落
        frame_size = int(0.02 * SAMPLE_RATE)  # 20ms帧
        non_silent_frames = []
        
        for i in range(0, len(audio) - frame_size, frame_size):
            frame = audio[i:i + frame_size]
            frame_rms = np.sqrt(np.mean(frame.astype(np.float32) ** 2))
            if frame_rms > threshold:
                non_silent_frames.append(i)
        
        if not non_silent_frames:
            print("🔍 未检测到语音段落，使用原始音频")
            return input_file
        
        # 找到语音段落的开始和结束
        start_frame = min(non_silent_frames)
        end_frame = max(non_silent_frames) + frame_size
        
        # 截取语音段落
        trimmed = audio[start_frame:end_frame]
        
        # 保存截取后的音频
        out_file = "trimmed.wav"
        with wave.open(out_file, 'wb') as wf_out:
            wf_out.setnchannels(1)
            wf_out.setsampwidth(2)
            wf_out.setframerate(SAMPLE_RATE)
            wf_out.writeframes(trimmed.tobytes())
        
        start_time = start_frame / SAMPLE_RATE
        end_time = end_frame / SAMPLE_RATE
        print(f"✅ 简单VAD处理完成，语音段落: {start_time:.2f}s - {end_time:.2f}s")
        return out_file
        
    except Exception as e:
        print(f"⚠️ 简单VAD处理失败: {e}")
        return input_file

def asr_transcribe(file="trimmed.wav"):
    print("📝 语音识别...")
    
    try:
        # 使用简化的ASR模块
        from simple_asr import simple_asr_transcribe
        return simple_asr_transcribe(file)
        
    except Exception as e:
        print(f"⚠️ ASR识别失败: {e}")
        print("🔄 使用模拟语音识别结果")
        text = "你好，这是一个测试语音识别结果"
        print("👤 你说:", text)
        return text

def llm_reply(text):
    """调用LLM生成回复"""
    print("🤖 调用 LLM...")
    
    # 1. 尝试本地LLM
    try:
        from local_llm import ensure_loaded, generate_reply
        if ensure_loaded("./models/llm/model.gguf"):
            print("🧠 使用本地LLM (GGUF)...")
            reply = generate_reply(text)
            if reply and reply.strip():
                print("🤖 回复:", reply)
                conversation_history.append({"role": "user", "content": text})
                conversation_history.append({"role": "assistant", "content": reply})
                return reply
            else:
                print("⚠️ 本地LLM回复为空，使用模拟回复")
        else:
            print("⚠️ 本地LLM模型未加载或不可用，使用模拟回复")
    except Exception as e:
        print(f"⚠️ 本地LLM调用失败: {e}")
        print("🔄 使用模拟回复")

    # 2. 模拟回复
    reply = f"我收到了你的消息：'{text}'。这是一个测试回复。"
    print("🤖 回复:", reply)
    conversation_history.append({"role": "user", "content": text})
    conversation_history.append({"role": "assistant", "content": reply})
    return reply

def show_conversation_history():
    """显示对话历史"""
    if not conversation_history:
        print("📚 暂无对话历史")
        return
    
    print(f"\n📚 对话历史 (共 {len(conversation_history)} 条消息):")
    print("=" * 50)
    
    for i, msg in enumerate(conversation_history):
        role = "👤 用户" if msg["role"] == "user" else "🤖 助手"
        content = msg["content"]
        print(f"{i+1}. {role}: {content}")
        print("-" * 30)

def clear_conversation_history():
    """清空对话历史"""
    global conversation_history
    conversation_history = []
    print("✅ 对话历史已清空")

def tts_settings():
    """TTS设置菜单"""
    try:
        from edge_tts_config import edge_tts_config, speak_text
        
        print("\n🎤 Edge-TTS设置")
        print("=" * 30)
        
        # 显示当前声音
        current_voice = edge_tts_config.get_voice_info()
        print(f"当前声音: {current_voice.get('name', 'Unknown')} ({current_voice.get('gender', 'Unknown')})")
        
        # 列出可用声音
        voices = edge_tts_config.list_voices()
        print(f"\n🎵 可用声音 (共{len(voices)}个):")
        for i, voice in enumerate(voices):
            current = " (当前)" if voice['id'] == edge_tts_config.current_voice else ""
            print(f"  {i+1:2d}. {voice['name']} ({voice['gender']}){current}")
        
        print("\n选项:")
        print("  's' - 切换声音")
        print("  'c' - 查看中文声音")
        print("  'e' - 查看英文声音")
        print("  't' - 测试TTS")
        print("  'b' - 返回主菜单")
        
        while True:
            choice = input("\n请选择操作 (s/c/e/t/b): ").strip().lower()
            
            if choice == 'b':
                break
            elif choice == 's':
                try:
                    voice_num = int(input(f"请选择声音 (1-{len(voices)}): "))
                    if 1 <= voice_num <= len(voices):
                        voice_id = voices[voice_num-1]['id']
                        if edge_tts_config.set_voice(voice_id):
                            print(f"✅ 已切换到声音: {voices[voice_num-1]['name']}")
                        else:
                            print("❌ 声音切换失败")
                    else:
                        print("❌ 无效的声音编号")
                except ValueError:
                    print("❌ 请输入有效的数字")
            elif choice == 'c':
                chinese_voices = edge_tts_config.list_voices("zh-CN")
                print(f"\n🇨🇳 中文声音 (共{len(chinese_voices)}个):")
                for i, voice in enumerate(chinese_voices, 1):
                    current = " (当前)" if voice['id'] == edge_tts_config.current_voice else ""
                    print(f"  {i:2d}. {voice['name']} ({voice['gender']}){current}")
            elif choice == 'e':
                english_voices = edge_tts_config.list_voices("en-US")
                print(f"\n🇺🇸 英文声音 (共{len(english_voices)}个):")
                for i, voice in enumerate(english_voices, 1):
                    current = " (当前)" if voice['id'] == edge_tts_config.current_voice else ""
                    print(f"  {i:2d}. {voice['name']} ({voice['gender']}){current}")
            elif choice == 't':
                test_text = input("请输入测试文本 (回车使用默认): ").strip()
                if not test_text:
                    test_text = "这是一个Edge-TTS测试。"
                print("🔊 测试TTS...")
                tts_speak(test_text)
            else:
                print("❌ 无效选择")
                
    except Exception as e:
        print(f"⚠️ TTS设置失败: {e}")

def analyze_audio_basic(audio_file):
    """对音频进行基础分析，只输出音频统计信息。"""
    duration_sec = None
    rms = None
    silence_ratio = None
    try:
        with wave.open(audio_file, 'rb') as wf_in:
            frames = wf_in.readframes(wf_in.getnframes())
            audio_np = np.frombuffer(frames, dtype=np.int16)
            duration_sec = wf_in.getnframes() / float(wf_in.getframerate())
            if audio_np.size > 0:
                rms = float(np.sqrt(np.mean((audio_np.astype(np.float32) / 32768.0) ** 2)))
                frame_len = int(0.02 * wf_in.getframerate()) or 1
                if frame_len > 0:
                    frames_view = audio_np[: len(audio_np) - (len(audio_np) % frame_len)].reshape(-1, frame_len)
                    frame_rms = np.sqrt(np.mean((frames_view.astype(np.float32) / 32768.0) ** 2, axis=1))
                    thr = max(0.01, np.median(frame_rms) * 0.5)
                    silence_ratio = float(np.mean(frame_rms < thr))
    except Exception as e:
        print(f"⚠️ 音频分析失败: {e}")

    print("\n📊 音频分析：")
    if duration_sec is not None:
        print(f"- 音频时长: {duration_sec:.2f}s  | RMS: {rms:.4f}  | 静音占比: {silence_ratio if silence_ratio is None else round(silence_ratio, 2)}")
    print()

    return {"duration_sec": duration_sec, "rms": rms, "silence_ratio": silence_ratio}

def visualize_audio(audio_file: str, output_prefix: str = "audio_analysis"):
    """使用pyAudioAnalysis和matplotlib生成音频可视化图像。"""
    try:
        with wave.open(audio_file, 'rb') as wf_in:
            fr = wf_in.getframerate()
            n = wf_in.getnframes()
            raw = wf_in.readframes(n)
            y = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        t = np.arange(len(y)) / float(fr)

        fig, axes = plt.subplots(3, 1, figsize=(12, 9))
        fig.suptitle('Audio Analysis Report', fontsize=16, fontweight='bold')

        # 波形
        axes[0].plot(t, y, linewidth=0.7, color='blue')
        axes[0].set_title('Waveform', fontweight='bold')
        axes[0].set_xlabel('Time (s)')
        axes[0].set_ylabel('Amplitude')
        axes[0].grid(True, alpha=0.3)

        # 频谱图（忽略log10除零等RuntimeWarning）
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            axes[1].specgram(y, NFFT=512, Fs=fr, noverlap=256, cmap='magma')
        axes[1].set_title('Spectrogram', fontweight='bold')
        axes[1].set_xlabel('Time (s)')
        axes[1].set_ylabel('Frequency (Hz)')

        # 短时特征
        from pyAudioAnalysis import ShortTermFeatures as stf
        win = int(0.05 * fr) or 1
        step = int(0.025 * fr) or 1
        feats, feat_names = stf.feature_extraction(y, fr, win, step)
        zcr_idx = feat_names.index('zcr') if 'zcr' in feat_names else 0
        energy_idx = feat_names.index('energy') if 'energy' in feat_names else 1
        x_frames = np.arange(feats.shape[1]) * (step / fr)

        axes[2].plot(x_frames, feats[zcr_idx, :], label='ZCR', color='red', linewidth=1)
        axes[2].plot(x_frames, feats[energy_idx, :], label='Energy', color='green', linewidth=1)
        axes[2].set_title('Short-Term Features (ZCR & Energy)', fontweight='bold')
        axes[2].set_xlabel('Time (s)')
        axes[2].set_ylabel('Value')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        combined_path = f"{output_prefix}_combined.png"
        plt.savefig(combined_path, dpi=150, bbox_inches='tight')
        plt.close()

        print("🖼️ 综合音频分析图已生成:")
        print(f"- {combined_path}")
    except Exception as e:
        print(f"⚠️ 音频可视化失败: {e}")

def tts_speak(text):
    print("🔊 开始语音合成...")
    
    try:
        # 使用Edge-TTS
        from edge_tts_config import speak_text
        
        if speak_text(text):
            print("🔊 语音播放完成")
        else:
            print("⚠️ Edge-TTS播放失败，显示文本回复")
            print("📝 文本回复:", text)
        
    except Exception as e:
        print(f"⚠️ Edge-TTS加载失败: {e}")
        # 降级到系统TTS
        try:
            subprocess.run(["say", text], check=True)
            print("🔊 系统语音播放完成")
        except Exception as e2:
            print(f"⚠️ 系统TTS也失败: {e2}")
            print("📝 文本回复:", text)

def interactive_mode():
    """交互式对话模式"""
    print("\n🎙️ 欢迎使用智能语音聊天系统！")
    print("=" * 50)
    print("命令说明:")
    print("  'r' 或 'record' - 开始录音对话")
    print("  'h' 或 'history' - 查看对话历史")
    print("  'c' 或 'clear' - 清空对话历史")
    print("  't' 或 'tts' - TTS设置")
    print("  'q' 或 'quit' - 退出程序")
    print("=" * 50)
    
    while True:
        try:
            command = input("\n请输入命令 (r/h/c/t/q): ").strip().lower()
            
            if command in ['q', 'quit', 'exit']:
                print("👋 再见！")
                break
            elif command in ['r', 'record']:
                print("\n🎙️ 开始录音对话...")
                record_audio()
                speech_file = vad_trim()
                user_text = asr_transcribe(speech_file)
                
                # 音频基础分析
                _ = analyze_audio_basic(speech_file)
                # 生成音频可视化
                visualize_audio(speech_file, output_prefix="audio_analysis")
                
                reply_text = llm_reply(user_text)
                tts_speak(reply_text)
                
            elif command in ['h', 'history']:
                show_conversation_history()
            elif command in ['c', 'clear']:
                clear_conversation_history()
            elif command in ['t', 'tts']:
                tts_settings()
            else:
                print("❌ 无效命令，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n👋 程序被用户中断，再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    # 检查是否以交互模式运行
    if len(sys.argv) > 1 and sys.argv[1] in ['-i', '--interactive']:
        interactive_mode()
    else:
        # 默认单次运行模式
        print("🎙️ 单次录音模式 (使用 -i 参数进入交互模式)")
        record_audio()
        speech_file = vad_trim()
        user_text = asr_transcribe(speech_file)
        # 音频基础分析
        _ = analyze_audio_basic(speech_file)
        # 生成音频可视化
        visualize_audio(speech_file, output_prefix="audio_analysis")
        reply_text = llm_reply(user_text)
        tts_speak(reply_text)