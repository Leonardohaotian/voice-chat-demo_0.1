#!/bin/bash

echo "🚀 开始安装语音聊天演示的依赖..."

# 安装Python依赖
echo "📦 安装Python依赖包..."
pip install -r requirements.txt

# 安装pyAudioAnalysis
echo "🔊 安装pyAudioAnalysis..."
cd models/pyAudioAnalysis
pip install -e .
cd ../..

# 安装YuXi-Know
echo "🤖 安装YuXi-Know..."
cd models/Yuxi-Know
pip install -e .
cd ../..

# 检查piper是否安装
echo "🎵 检查Piper TTS..."
if ! command -v piper &> /dev/null; then
    echo "⚠️  Piper TTS 未安装，请手动安装："
    echo "   1. 访问: https://github.com/rhasspy/piper"
    echo "   2. 下载适合你系统的版本"
    echo "   3. 或者使用: pip install piper-tts"
fi

# 检查sox是否安装（用于音频播放）
echo "🔊 检查SoX音频工具..."
if ! command -v play &> /dev/null; then
    echo "⚠️  SoX 未安装，请安装："
    echo "   macOS: brew install sox"
    echo "   Ubuntu: sudo apt-get install sox"
    echo "   Windows: 下载并安装 SoX"
fi

echo "✅ 依赖安装完成！"
echo ""
echo "📝 使用说明："
echo "1. 确保所有依赖都已正确安装"
echo "2. 运行: python chat.py"
echo "3. 按提示进行语音交互"
