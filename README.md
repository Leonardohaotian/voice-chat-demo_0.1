# 🎙️ 智能语音聊天系统（本地 ASR + 本地 LLM + TTS）

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Development-orange.svg)](https://github.com/Leonardohaotian/voice-chat-demo_0.1 )

**基于多模态AI的实时语音对话系统**

</div>

## 📖 项目简介

本项目集成了“ASR → LLM → TTS”链路，面向本地运行：支持语音识别、智能回复与语音播放，并提供音频分析与可视化功能。

## ✨ 核心特性

- 🎤 实时语音录制（sounddevice）
- 🔍 智能语音检测（pyAudioAnalysis，失败回退简易VAD）
- 📝 多语言语音识别（SenseVoice，本地）
- 🧠 智能对话（本地 GGUF + llama-cpp-python，无需 API）
- 🔊 语音合成（Edge‑TTS，高质量）
- 📊 音频分析与可视化（matplotlib）
- 🎯 模块化架构，易扩展

## 🏗️ 技术架构

### 系统组件

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

### 技术栈

- 语音处理: `sounddevice`, `numpy`, `wave`
- 语音分析: `pyAudioAnalysis`（VAD/特征）
- 语音识别: `SenseVoice`（本地）
- 自然语言处理: `llama-cpp-python`（GGUF，本地）
- 语音合成: `Edge‑TTS`
- 数据可视化: `matplotlib`

## 🚀 快速开始

### 环境要求

- Python 3.8+
- macOS/Linux/Windows
- 音频设备（麦克风）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/Leonardohaotian/voice-chat-demo_0.1.git
cd voice-chat-demo_0.1
```

2. **安装依赖**
```bash
# 安装Python依赖
pip install -r requirements.txt

# （可选）就地安装 pyAudioAnalysis：本项目已内置源码，一般无需额外安装
# cd models/pyAudioAnalysis && pip install -e . && cd ../..
```

3. **下载模型文件**
```bash
# 自动下载所有模型（推荐）
./download_models.sh

# 或手动下载：
# - SenseVoice: 运行 python -c "from modelscope import snapshot_download; snapshot_download('iic/SenseVoiceSmall')"
# - LLM: 下载 Qwen2.5-1.5B-Instruct-Q4_K_M.gguf 到 models/llm/model.gguf
```

4. **运行程序**
```bash
python chat.py      # 单轮
python chat.py -i   # 交互
```

### 使用说明

1. 运行程序后，系统会自动开始录音（6秒）
2. 录音完成后，系统会进行语音检测和识别
3. 识别结果会显示在控制台
4. 系统会生成智能回复并播放语音
5. 同时生成音频分析图表

### 交互式模式

使用 `python chat.py -i` 启动交互式模式，支持以下命令：
- `r` - 开始录音对话
- `h` - 查看对话历史
- `c` - 清空对话历史
- `t` - TTS设置
- `q` - 退出程序

## 📁 项目结构（精简版）

```
voice-chat-demo_0.1/
├── .gitignore                 # 忽略大文件
├── download_models.sh         # 模型下载脚本
├── chat.py                    # 主程序
├── simple_asr.py             # ASR模块
├── local_llm.py              # LLM模块
├── edge_tts_config.py        # TTS模块
├── requirements.txt           # 依赖列表
├── README.md                 # 项目说明
├── USAGE.md                  # 使用指南
└── models/
    ├── llm/
    │   └── README.md         # LLM下载说明
    ├── SenseVoiceSmall/
    │   ├── README.md         # SenseVoice下载说明
    │   ├── config.yaml       # 配置文件
    │   ├── configuration.json # 配置文件
    │   ├── tokens.json       # 词汇表
    │   ├── chn_jpn_yue_eng_ko_spectok.bpe.model # 分词器
    │   └── am.mvn            # 音频归一化
    └── pyAudioAnalysis/      # 音频分析库
```

## 🔧 配置说明

### 主要配置参数

```python
# 音频配置
SAMPLE_RATE = 16000          # 采样率
RECORD_SECONDS = 5           # 基础录音时长（实际录音6秒）

# 模型路径
ASR_MODEL_PATH = "./models/SenseVoiceSmall"
```

### 自定义配置

- 修改 `SAMPLE_RATE` 调整音频质量
- 修改 `RECORD_SECONDS` 调整录音时长
- 在 `models/` 目录下添加自定义模型

## 📊 功能演示

### 音频分析示例

系统会自动生成包含以下内容的音频分析图：
- 音频波形图
- 频谱图
- 短时特征分析

### 语音识别示例

```
🎙️ 录音中...
✅ 录音完成: input.wav
🔍 VAD 检测语音段落...
✅ VAD处理完成，语音段落: 0.50s - 4.20s
📝 语音识别 (SenseVoice)...
👤 你说: 你好，这是一个测试语音识别结果
```

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 如何贡献

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范

- 遵循 PEP 8 代码风格
- 添加适当的注释和文档
- 确保代码通过测试
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

本项目基于以下开源项目构建，感谢所有贡献者：

### 核心依赖

- **[pyAudioAnalysis](https://github.com/tyiannak/pyAudioAnalysis)** - 音频特征提取和分析库
  - 作者: Theodoros Giannakopoulos
  - 许可证: Apache License 2.0

- **[SenseVoice](https://github.com/FunAudioLLM/SenseVoice)** - 多语言语音识别模型
  - 作者: FunAudioLLM团队
  - 许可证: Apache License 2.0

- **[llama-cpp-python](https://github.com/abetlen/llama-cpp-python)** - Python绑定，用于运行GGUF格式的本地LLM
  - 作者: abetlen
  - 许可证: MIT License

### 其他依赖

- **[Edge-TTS](https://github.com/rany2/edge-tts)** - 微软Edge浏览器的TTS引擎Python接口
  - 作者: rany2
  - 许可证: MIT License
- **[sounddevice](https://github.com/spatialaudio/python-sounddevice)** - 音频录制库
- **[matplotlib](https://matplotlib.org/)** - 数据可视化库

## 📞 联系我们

- 项目主页: [GitHub Repository](https://github.com/Leonardohaotian/voice-chat-demo_0.1)
- 问题反馈: [Issues](https://github.com/Leonardohaotian/voice-chat-demo_0.1/issues)
- 邮箱: 2944718988@qq.com

## 🔮 未来规划

- [ ] 支持更多语音识别模型
- [ ] 添加情感识别功能
- [ ] 支持更完善的多轮对话与记忆
- [ ] 添加Web界面
- [ ] 支持实时流式处理
- [ ] 添加语音克隆功能

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个 Star！**

## 📜 版权与致谢（Attribution）

- 本项目代码以 MIT 许可证开源（见 `LICENSE`）。
- 模型与第三方库分别遵循其各自许可证：
  - SenseVoice（Apache-2.0）
  - llama-cpp-python（MIT），GGUF 模型版权归其原作者/发布者所有
  - pyAudioAnalysis（Apache-2.0）
  - Edge-TTS（MIT）
  - sounddevice（MIT）
  - matplotlib（PSF）
- 请在发布或分发时遵守各模型与依赖的使用条款与许可证要求。

Made with ❤️ by [KisYuu](https://github.com/Leonardohaotian)

</div>
