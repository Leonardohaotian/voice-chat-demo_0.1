# SenseVoice 模型文件

## 下载说明

请将 SenseVoice 模型文件放置在此目录下。

### 必需文件

- `model.pt` - 主模型权重文件 (~893MB)
- `config.yaml` - 模型配置文件
- `configuration.json` - ModelScope配置文件
- `tokens.json` - 词汇表文件
- `chn_jpn_yue_eng_ko_spectok.bpe.model` - 分词器模型
- `am.mvn` - 音频归一化文件

### 快速下载

运行项目根目录下的下载脚本：

```bash
./download_models.sh
```

### 手动下载

使用 ModelScope 下载：

```python
from modelscope import snapshot_download

# 下载 SenseVoice 模型
model_dir = snapshot_download('iic/SenseVoiceSmall')

# 将文件复制到当前目录
import shutil
import os
for item in os.listdir(model_dir):
    if os.path.isfile(os.path.join(model_dir, item)):
        shutil.copy2(os.path.join(model_dir, item), f'./{item}')
```

### 模型信息

- **模型名称**: SenseVoice-Small
- **支持语言**: 中文、英文、粤语、日语、韩语
- **模型大小**: ~893MB
- **框架**: PyTorch
- **许可证**: Apache 2.0

### 注意事项

- 确保所有必需文件都在此目录下
- 不要删除任何配置文件
- 模型文件较大，下载需要时间
