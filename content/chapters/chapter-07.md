<!-- Generated from ../source-html/chapter-07.html; do not edit independently. -->

# 30 分钟带你快速看到第一个结果

开源模型下载下来，可以在自己的笔记本上跑，也可以租一台云服务器，按需要配置 CPU、GPU 和运行环境。设备不同，准备工作也不一样。

<p></p>

如果只是想先试一下模型能做什么，魔搭 Notebook 提供了一个免费的入口。打开浏览器，选择运行实例，就能在网页里写代码、下载模型并查看结果。

<p></p>

这一篇从创建 Notebook、检查环境到加载模型，跟着做完，就能看到第一个结果。

<a id="c7-s1"></a>

## 打开 Notebook，先连上运行实例

进入模型库，找到 Qwen/Qwen3-ASR-1.7B 模型，点击右侧的“Notebook 快速开发”即可创建魔搭 Notebook。

模型链接：https://www.modelscope.cn/models/Qwen/Qwen3-ASR-1.7B

![正文配图](<../../assets/manuscript-20260914/c07-24e3ac0b44038a.webp>)

点击右上角的“连接运行时”选择实例，这里我们选择 GPU 进行演示，可以根据模型依赖选择合适的预装镜像。

![正文配图](<../../assets/manuscript-20260914/c07-842702a8d17940.webp>)

<a id="c7-s2"></a>

## 检查一下环境准备好了没有

加载实例后，首先需要检查当前环境，可以在 notebook 执行以下命令：

1.查看 python 版本

```text
!python3 --version
```

结果展示：

![正文配图](<../../assets/manuscript-20260914/c07-0c22d724d88227.webp>)

2.查看相关依赖

不同模型的依赖不同，需要查看模型卡片了解信息，根据 Qwen3-ASR-1.7B 模型的模型卡片，了解到其推理依赖`qwen3-asr`。如果环境缺失 qwen3-asr，需要自行安装

```text
# 查询依赖
!pip3 show qwen-asr
# 安装qwen-asr(如缺失)
!pip3 install -U qwen-asr
```

结果展示：

![正文配图](<../../assets/manuscript-20260914/c07-d57a19908cfa63.webp>)

安装成功的查询结果：

![正文配图](<../../assets/manuscript-20260914/c07-bb1099aa862cef.webp>)

3.查看 CPU 配置

```text
!lscpu
```

结果展示：

![正文配图](<../../assets/manuscript-20260914/c07-cea051219a074d.webp>)

4.查看 GPU 及显存

```text
!nvidia-smi
```

结果展示：

![正文配图](<../../assets/manuscript-20260914/c07-cbdbb23a46f508.webp>)

5.查看内存

```text
!free -h
```

结果展示：

![正文配图](<../../assets/manuscript-20260914/c07-eae28c100f0724.webp>)

6.查看磁盘

```text
!df -h
```

结果展示：

![正文配图](<../../assets/manuscript-20260914/c07-65859c8cb5ee99.webp>)

<a id="c7-s3"></a>

####

<a id="c7-s4"></a>

## 直接按模型名称加载模型

参考模型卡片示例代码进行模型加载，这里会自动下载需要的模型文件。

```python
import torch
from qwen_asr import Qwen3ASRModel
 
model = Qwen3ASRModel.from_pretrained(
    "Qwen/Qwen3-ASR-1.7B",
    dtype=torch.bfloat16,
    device_map="cuda:0",
    # attn_implementation="flash_attention_2",
    max_inference_batch_size=32, # Batch size limit for inference. -1 means unlimited. Smaller values can help avoid OOM.
    max_new_tokens=256, # Maximum number of tokens to generate. Set a larger value for long audio input.
)
print("模型加载完成！")
```

结果展示：

![正文配图](<../../assets/manuscript-20260914/c07-654f63dcc5e91f.webp>)

如果想要自己单独下载模型，可参考本书 2.5 节的模型下载方法。如将模型下载到目录：`/mnt/workspace/Qwen3-ASR-1.7B`，以命令行下载方式为例，在终端执行以下命令：

```text
# 安装 ModelScope（如未安装）
!pip3 install modelscope
# 下载完整模型库
!modelscope download --model Qwen/Qwen3-ASR-1.7B --local_dir /mnt/workspace/Qwen3-ASR-1.7B
```

结果展示：

![正文配图](<../../assets/manuscript-20260914/c07-559068ac157a75.webp>)

有下载好的模型文件，就可将`Qwen/Qwen3-ASR-1.7B`替换成你的模型路径。

```python
import torch
from qwen_asr import Qwen3ASRModel

model = Qwen3ASRModel.from_pretrained(
    "/mnt/workspace/Qwen3-ASR-1.7B",
    dtype=torch.bfloat16,
    device_map="cuda:0",
    # attn_implementation="flash_attention_2",
    max_inference_batch_size=32, # Batch size limit for inference. -1 means unlimited. Smaller values can help avoid OOM.
    max_new_tokens=256, # Maximum number of tokens to generate. Set a larger value for long audio input.
)
print("模型加载完成！")
```

结果展示：

![正文配图](<../../assets/manuscript-20260914/c07-f77df5d805f7ba.webp>)

<a id="c7-s5"></a>

## 传入一段音频，看看识别出了什么

模型加载后，即可传入音频文件进行模型推理。可将 audio 的值替换成你的音频文件路径。

```sql
results = model.transcribe(
    audio="https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3-ASR-Repo/asr_en.wav",
    language=None, # set "English" to force the language
)
 
print(results[0].language)
print(results[0].text)
print("模型推理完成！")
```

结果展示：

![正文配图](<../../assets/manuscript-20260914/c07-eb17ac93b1fd85.webp>)

可将 audio 的值替换成你的音频文件路径，进行模型推理。右击左侧工作区的“DSW-GPU”文件夹，点击“上传”，选择本地的音频文件，即可上传到 Notebook 环境的“DSW-GPU”文件夹下。

![正文配图](<../../assets/manuscript-20260914/c07-3bebb1610065d9.webp>)

然后修改代码如下：

```sql
results = model.transcribe(
    audio="/mnt/workspace/asr_en.wav",
    language=None, # set "English" to force the language
)
 
print(results[0].language)
print(results[0].text)
print("模型推理完成！")
```

结果展示：

![正文配图](<../../assets/manuscript-20260914/c07-df433592f8b1fb.webp>)

<p></p>

本章代码及相关文件见：https://www.modelscope.cn/gallery/liucong/54c2ca38-b797-43d1-97ab-4b9f569aaa95

<p></p>
