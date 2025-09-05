# LLM 模型文件

## 下载说明

请将 GGUF 格式的 LLM 模型文件放置在此目录下，文件名为 `model.gguf`。

### 推荐模型

- **Qwen2.5-1.5B-Instruct-Q4_K_M.gguf** (约 1GB)
  - 下载地址: https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF
  - 文件大小: ~1GB
  - 性能: 平衡速度和质量

### 快速下载

运行项目根目录下的下载脚本：

```bash
./download_models.sh
```

### 手动下载

1. 访问 https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF
2. 下载 `Qwen2.5-1.5B-Instruct-Q4_K_M.gguf` 文件
3. 将文件重命名为 `model.gguf` 并放置在此目录

### 其他可选模型

- Qwen2.5-0.5B-Instruct (更小，更快)
- Qwen2.5-3B-Instruct (更大，更好)
- Llama-2-7B-Chat (经典选择)

确保模型文件格式为 GGUF，并且与 llama-cpp-python 兼容。
