# 🎙️ 智能语音聊天系统使用指南

## 📋 系统概述

本系统实现"ASR → LLM → TTS"的本地语音对话链路，并提供音频分析与可视化：

- **ASR（语音识别）**: SenseVoice（本地，已做管道缓存与加速）
- **LLM（大语言模型）**: 本地 GGUF 模型（llama-cpp-python，无需 API）
- **TTS（语音合成）**: Edge‑TTS（高质量，跨平台）
- **VAD（语音检测）**: pyAudioAnalysis（失败自动回退到简易 VAD）

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# （可选）就地安装 pyAudioAnalysis：本项目已内置源码，一般无需额外安装
# cd models/pyAudioAnalysis && pip install -e . && cd ../..
```

### 2. 下载模型文件

**自动下载（推荐）**：
```bash
./download_models.sh
```

**手动下载**：
- **SenseVoice**: 运行 `python -c "from modelscope import snapshot_download; snapshot_download('iic/SenseVoiceSmall')"`
- **LLM**: 下载 Qwen2.5-1.5B-Instruct-Q4_K_M.gguf 到 `models/llm/model.gguf`

完成后，系统会自动优先使用本地模型。

### 3. 运行语音聊天系统

```bash
# 交互式模式（推荐）
python chat.py -i

# 单次录音模式
python chat.py
```

## 🎮 交互式模式使用

启动交互式模式后，你可以使用以下命令：

- `r` 或 `record` - 开始录音对话
- `h` 或 `history` - 查看对话历史
- `c` 或 `clear` - 清空对话历史
- `t` 或 `tts` - TTS 设置（切换 Edge‑TTS 声音、测试播放）
- `q` 或 `quit` - 退出程序

### 使用流程

1. 运行 `python chat.py -i` 启动交互式模式
2. 输入 `r` 开始录音
3. 系统会录音 6 秒，然后进行 VAD 裁剪与语音识别（SenseVoice）
4. 识别结果会由本地 LLM（GGUF）生成回复
5. 回复通过 Edge‑TTS 播放

## 🔧 配置说明

### 音频配置（`chat.py`）

```python
SAMPLE_RATE = 16000      # 采样率
RECORD_SECONDS = 5       # 基础录音时长（实际录音6秒）
```

### 本地 LLM 配置（`local_llm.py`）

- 模型路径：`./models/llm/model.gguf`
- 引擎：`llama-cpp-python`（可在 `ensure_loaded` 中调整 `n_ctx`、`n_threads`、`n_gpu_layers`）

### TTS 配置（`edge_tts_config.py`）

- 默认使用 Edge‑TTS 播放；可在交互菜单中（`t`）切换中文/英文多种声音。

### 模型路径

```python
ASR_MODEL_PATH = "./models/SenseVoiceSmall"   # SenseVoice 模型
LLM_GGUF_PATH  = "./models/llm/model.gguf"     # 本地 LLM 模型
```

## 🛠️ 故障排除

### 1. 本地 LLM 未生效

现象：控制台提示连接外部服务器或回复为模拟文本。

解决：
- 确认 `./models/llm/model.gguf` 文件已放置
- 重新运行 `python3 chat.py -i` 进行一次对话

### 2. 语音识别失败/很慢

- 确认 `models/SenseVoiceSmall` 目录存在且完整
- 尽量在同一进程内多轮识别（已缓存管道，避免重复初始化）
- 录音时尽量减少静音段，VAD 截取得更短更快
- 如需更进一步加速，可将录音时长降到 2–3 秒

### 3. TTS 播放异常

- 再次运行一次，或在交互菜单（`t`）中切换声音测试
- macOS 使用 `afplay` 播放；如需改为其它播放器，可在 `play_audio_file` 中调整

## 📊 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   音频录制模块   │    │   语音处理模块   │    │   智能对话模块   │
│  sounddevice    │───▶│ pyAudioAnalysis │───▶│  Llama (GGUF)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   语音识别模块   │    │   音频分析模块   │    │   语音合成模块   │
│  SenseVoice     │    │   可视化分析     │    │   Edge‑TTS      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔮 功能特性

### 已实现功能

- ✅ 实时语音录制
- ✅ 智能语音检测（VAD，失败回退简易 VAD）
- ✅ 多语言语音识别（SenseVoice，本地）
- ✅ 本地 LLM 对话（GGUF + llama-cpp-python）
- ✅ 高质量语音合成（Edge‑TTS）
- ✅ 对话历史管理、音频分析与可视化、命令行交互

### 计划功能

- 🔄 流式实时（边录边识/边播）
- 🔄 本地离线 TTS 替代方案（如 Piper/XTTS v2）

## 📝 开发说明

### 项目结构（简化后）

```
voice_chat_demo_0.1/
├── chat.py                    # 主程序
├── local_llm.py               # 本地 LLM（GGUF）
├── simple_asr.py              # SenseVoice ASR + 兜底
├── edge_tts_config.py         # Edge‑TTS 播放
├── requirements.txt           # 依赖
├── USAGE.md                   # 使用说明
└── models/
    ├── pyAudioAnalysis/       # VAD/特征
    ├── SenseVoiceSmall/       # ASR 模型
    └── llm/
        └── model.gguf         # LLM 模型
```

## 📜 版权与致谢（Attribution）

- 本项目代码以 MIT 许可证开源（见 `LICENSE`）。
- 模型与第三方库分别遵循其各自许可证：
  - SenseVoice（Apache-2.0）
  - llama-cpp-python（MIT），GGUF 模型版权归其原作者/发布者所有
  - pyAudioAnalysis（Apache-2.0）
  - Edge‑TTS（MIT）
- 请在发布或分发时遵守各模型与依赖的使用条款与许可证要求。

---

**🎉 享受你的智能语音聊天体验！**
