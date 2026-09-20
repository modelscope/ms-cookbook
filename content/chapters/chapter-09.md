<!-- Generated from ../source-html/chapter-09.html; do not edit independently. -->

# 笔记本也能跑开源模型，先从 Ollama 开始

模型在本地或者云端部署，比如，本地设备包括笔记本、台式机，以及其他端侧设备等等，

同时本地运行也有不同的工具选择，Ollama、以及 vLLM、SGLang 等框架。

<p></p>

本章，我们先把 Ollama 的基本用法讲清楚。<strong>其他端侧设备的适配，以及 vLLM、SGLang 等框架的使用，会在后续补充。</strong>

<p></p>

<a id="c9-s1"></a>

## 为什么想把模型放在自己的电脑上？

通过 API 调用大模型是最省心的做法：请求发过去，模型计算好把结果回传，用户不需要采购 GPU，也不用维护底层环境。

但 API 模式也有绕不开的限制，主要表现在以下几个方面，

- 数据安全，核心文档、客户隐私和内部业务数据，无法直接传给第三方公有云。
- 离线可用，内网专线等生产环境根本无法连接外网。
- 成本控制：当调用量大且稳定时，自己搭服务器的综合成本通常会比一直按 Token 付费更划算。

所以，如果业务涉及数据敏感、要求纯离线运行、调用量较大，本地部署就是更合适的选择。

<p></p>

<a id="c9-s2"></a>

## 先看看笔记本的系统和硬件

Ollama 是目前用起来比较顺手的工具之一，把模型下载、本地管理和接口服务都打包好了。用户不需要自己写代码去加载模型，只需几行命令就能直接启动模型。

模型能否在本地顺利运行，很大程度上取决于计算机的硬件资源。Ollama 对常见的硬件平台提供了较好的支持，支持 Windows、Linux 和 macOS 等常见操作系统。无论是普通 CPU、GPU，还是搭载 Apple Silicon 的 Mac 电脑，都可以用来运行模型。

<strong>CPU 运行，</strong>即使电脑没有独立显卡，也可以通过 CPU 运行模型。由于大模型推理需要进行大量计算，使用 CPU 时生成速度通常比较慢，因此更适合参数规模较小的模型，或者对响应速度要求不高的场景。

<strong>GPU 运行，</strong>这是目前比较常见的大模型运行方式。GPU 具有较强的并行计算能力，可以明显提升模型的生成速度。模型越大，需要的显存通常也越多，因此选择模型时需要考虑显卡是否有足够的显存。

<strong>Apple Silicon 运行，</strong>苹果 M 系列芯片采用统一内存设计，CPU 和 GPU 可以使用同一块内存。对于 Mac 用户来说，如果设备具有 32GB、64GB 或者更大的统一内存，就可以尝试运行一些参数规模较大的量化模型。

<a id="c9-s3"></a>

## 选自己的操作系统，安装 Ollama

<a id="c9-s4"></a>

### Windows 下安装 Ollama

1）首先在在 Ollama 官网，[Download Ollama](<https://ollama.com/download>) 下载对应的 windows 版本

![正文配图](<../../assets/manuscript-20260914/c09-562fed6f376b07.webp>)

2)下载完成后，直接点击安装，点击 continue

![正文配图](<../../assets/manuscript-20260914/c09-84fbbdb032e197.webp>)

3\) 安装完成后，显示，此时 Ollama 服务已经启动

![正文配图](<../../assets/manuscript-20260914/c09-4a2c1cee33adac.webp>)

4）在 cmd 中，启动想要加载的模型，比如：qwen3.5:2b，直接在终端中输入命令

```text
ollama run qwen3.5:2b
```

页面输出如下，说明模型启动成功，此时可以直接在客户端中对话，也可以直接调用接口测试模型

![正文配图](<../../assets/manuscript-20260914/c09-3ec90eccd2e903.webp>)

测试接代码如下：

```json
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:11434/v1",
    api_key="ollama",  
)

response = client.chat.completions.create(
    model="qwen3.5:2b", 
    messages=[
        {
            "role": "system",
            "content": "你是一个有帮助的中文助手。",
        },
        {
            "role": "user",
            "content": "你是谁？",
        },
    ],
    temperature=0,
    max_tokens=512,
)

print(response.choices[0].message.content)
```

结果显示如下：

![正文配图](<../../assets/manuscript-20260914/c09-b655606fa9a68a.webp>)

<a id="c9-s5"></a>

### ModelScope Notebook 安装 Ollama

1）在 Notebook 中安装 Ollama，首先下载安装包，执行下面命令

```text
!modelscope download --model=modelscope/ollama-linux --local_dir ./ollama-linux  
```

![正文配图](<../../assets/manuscript-20260914/c09-dc92f54670f6c7.webp>)

2）安装包下载后，进入 `ollama-linux` 文件夹，执行下面命令进行安装 

```text
%cd ollama-linux
```

![正文配图](<../../assets/manuscript-20260914/c09-0876f501356221.webp>)

<p></p>

```text
sudo chmod 777 ./ollama-modelscope-install.sh
./ollama-modelscope-install.sh
```

安装完成会显示 API 接口信息，默认 127.0.0.1:11434，如果显示如下信息，说明安装完成。

![正文配图](<../../assets/manuscript-20260914/c09-63cd320bae0306.webp>)

<a id="c9-s6"></a>

### Linux 下安装 Ollama

linux 下的安装步骤和以上在 ModelScope Notebook 中安装 Ollama 的方式一样。

<a id="c9-s7"></a>

### MAC 下安装 Ollama

1）首先在在 Ollama 官网，[Download Ollama](<https://ollama.com/download>) 下载对应的 macOS 版本

![正文配图](<../../assets/manuscript-20260914/c09-41a856385d9791.webp>)

2)下载完成后，双击下载文件，将 ollama 拖入到 applications 中

![正文配图](<../../assets/manuscript-20260914/c09-94e39bfe8d6df6.webp>)

3\) 安装完成后，显示，此时 Ollama 服务已经启动

![正文配图](<../../assets/manuscript-20260914/c09-8f8ec60e9899c4.webp>)

4）在 cmd 中，启动想要加载的模型，比如：qwen3.5:2b，直接在终端中输入命令

```text
ollama run qwen3.5:2b
```

页面输出如下，说明模型启动成功，此时可以直接在客户端中对话，也可以直接调用接口测试模型

![正文配图](<../../assets/manuscript-20260914/c09-60177d3b2d5627.webp>)

在客户端也可以进行 chat

![正文配图](<../../assets/manuscript-20260914/c09-9c52eab89512b0.webp>)

<p></p>

<a id="c9-s8"></a>

## 也可以从魔搭下载模型，用 Ollama 启动

Ollama 提供了很多模型库，我们可以在 ModelScope 中查找我们需要的模型，通过 Ollama 启动。

1）启动 Ollama 服务

这种常驻服务，Jupyter 的单个内核一次只能执行一个单元，所以导致后面的单元不太好执行，所以此部分在终端中执行，打开 Notebook 之后，直接进入工作区，下面有终端字样，点击即可。

![正文配图](<../../assets/manuscript-20260914/c09-79e4a22935cf09.webp>)

在终端中输入：

```text
ollama serve
```

![正文配图](<../../assets/manuscript-20260914/c09-7cafe12d23d148.webp>)

2）接下来运行我们想要启动的模型，比如：`Qwen3-4B-GGUF`，模型第一次运行时，需要先从模型仓库下载对应文件。这个命令也需要在终端执行，可以打开一个新的终端，执行命令如下：

![正文配图](<../../assets/manuscript-20260914/c09-ffba51d8bbbcc6.webp>)

```text
 ollama run modelscope.cn/unsloth/Qwen3-4B-GGUF
```

![正文配图](<../../assets/manuscript-20260914/c09-9d3696215d29ff.webp>)

此时模型已经启动好，可以调用接口测试模型接口是否连通，代码如下：

```json
import requests
url = "http://127.0.0.1:11434/v1/chat/completions"
data = {
    "model": "modelscope.cn/unsloth/Qwen3-4B-GGUF",
    "messages": [
        {
            "role": "user",
            "content": "你好，请介绍一下自己"
        }
    ],
    "max_tokens": 100
}

response = requests.post(url, json=data)

print("状态码:", response.status_code)
print(response.text)
```

模型调用成功，会输出对应的模型结果。

![正文配图](<../../assets/manuscript-20260914/c09-07612cad9b3680.webp>)

<p></p>

此章节所涉及的全部实验过程，具体可参照：https://modelscope.cn/gallery/liucong/b1ef397b-fe80-4fb9-812f-969fa25ea44c

<p></p>
