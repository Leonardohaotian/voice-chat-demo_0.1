#!/bin/bash
# 模型下载脚本

echo "🚀 开始下载模型文件..."

# 创建模型目录
mkdir -p models/llm
mkdir -p models/SenseVoiceSmall

echo "📥 下载 SenseVoice 模型..."
# 使用 ModelScope 下载 SenseVoice
python3 -c "
from modelscope import snapshot_download
import os
print('开始下载 SenseVoice 模型...')
model_dir = snapshot_download('iic/SenseVoiceSmall')
print(f'模型下载到: {model_dir}')

# 复制到项目目录
import shutil
src_dir = model_dir
dst_dir = './models/SenseVoiceSmall'
for item in os.listdir(src_dir):
    src = os.path.join(src_dir, item)
    dst = os.path.join(dst_dir, item)
    if os.path.isfile(src):
        shutil.copy2(src, dst)
        print(f'复制: {item}')
print('SenseVoice 模型下载完成!')
"

echo "📥 下载 LLM 模型 (Qwen2.5-1.5B-Instruct-Q4_K_M)..."
# 下载 Qwen2.5 模型
curl -L --retry 3 --retry-delay 3 -o models/llm/model.gguf \
"https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf?download=true"

echo "✅ 所有模型下载完成!"
echo ""
echo "📁 模型文件位置:"
echo "  - SenseVoice: models/SenseVoiceSmall/"
echo "  - LLM: models/llm/model.gguf"
echo ""
echo "🎉 现在可以运行 python chat.py -i 开始使用!"
