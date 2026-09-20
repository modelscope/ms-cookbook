<!-- Generated from ../source-html/chapter-02.html; do not edit independently. -->

# 开源模型还没用上，先卡在下载这一步？

早在 23 年，我就写过一篇文章《大模型下载使我痛苦》，

![正文配图](<../../assets/manuscript-20260914/c02-df1f804f3c3e14.webp>)

那时 HF 需要科学上网才能使用，模型少说十几 G，流量有限，可能有一些镜像网站，但不一定全，也不一定稳定。

<p></p>

<strong>现在，如果问在国内下载开源模型先去哪里，那毋庸置疑是魔搭。</strong>模型下载快，同时基本上所有国内外的开源模型都会第一时间上架，已然成为国内第一大开源模型社区（当然不止模型）。

<p></p>

<a id="c2-s1"></a>

## 教你如何在魔搭上找到你想要的开源模型

模型库是魔搭的基础功能模块，平台按任务类型（如文本生成、图像分类、语音识别等）对模型进行分类组织，支持关键词检索与多维度筛选。

![正文配图](<../../assets/manuscript-20260914/c02-bef2e47d883a7f.webp>)

已经知道模型名字，可以直接搜索。

![正文配图](<../../assets/manuscript-20260914/c02-754309025c1357.webp>)

还没确定用哪个，就先想清楚要让模型做什么。

比如，想把录音转成文字，就从可以语音识别开始找，再结合语言、参数规模、运行框架和许可证，逐步缩小范围，

具体想找到适合你业务的模型，可以看【把业务问题翻译成模型任务】章节内容。

<p></p>

<p></p>

<a id="c2-s2"></a>

## 开源模型的 Model Card，值得多看两眼

找到感兴趣的模型后，点进去看它的模型卡片。以 [Qwen3-ASR-1.7B](<https://modelscope.cn/models/Qwen/Qwen3-ASR-1.7B>) 为例，模型页面会把介绍、使用方法和效果评估放在一起。

<p></p>

先看这是什么模型，能做什么。模型名称、基本介绍和架构说明，可以帮我们确认有没有找错方向。

![正文配图](<../../assets/manuscript-20260914/c02-92f1d898fabc93.webp>)

再看适用范围，支持哪些语言、适合什么输入、有哪些限制，都和自己的任务有关。

![正文配图](<../../assets/manuscript-20260914/c02-b953f3979b2616.webp>)

接着看使用方法，需要什么运行环境，依赖哪些工具，输入应该怎样准备，通常都能在示例中找到。下载之前读一下，可以避免文件下载完了，才发现环境部署不了。

![正文配图](<../../assets/manuscript-20260914/c02-9c68fc359adb01.webp>)

最后看评估结果，这个模型在哪些数据上测过，比较的是什么指标，可以作为选型参考。当然具体效果怎么样，还是要拿自己真实数据试一试才知道，榜单只能作为一个参考。

![正文配图](<../../assets/manuscript-20260914/c02-a53b3b46d7e35d.webp>)

模型页面还提供文件清单、版本和许可证信息，上一章提过，能使用不等于能商用，

<strong>准备商用或者继续微调时，这一步千万别跳过。</strong>

![正文配图](<../../assets/manuscript-20260914/c02-8b4388b364a866.webp>)

部分模型还提供在线体验入口，遇到可以直接试用的模型，也能帮助判断这个模型是否值得下载。

<p></p>

<a id="c2-s3"></a>

## 下载模型方式有很多，选一个喜欢的就行

魔搭提供网页、命令行、Git 和 Python SDK 等下载方式，下面继续用较小的`Qwen/Qwen3-0.6B`演示，方便第一次操作。

<a id="c2-s4"></a>

### 只想在网页上点几下

进入模型的文件页面，找到需要的文件，点击下载按钮即可。网页方式适合查看文件和下载少量内容。

通过模型页面提供的下载按钮获取文件，示例：

![正文配图](<../../assets/manuscript-20260914/c02-7c3ecb6c57038f.webp>)

<a id="c2-s5"></a>

### 在终端里，一条命令下载

先安装最新版的 ModelScope Python 包，

```bash
pip install -U modelscope
```

只下载一个文件，可以把文件名写在模型名称后面，下面这条命令只下载说明文档，适合先检查下载是否正常。

```bash
modelscope download --model Qwen/Qwen3-0.6B README.md --local_dir ./Qwen3-0.6B
```

如果要下载整个模型，去掉文件名即可，

```bash
modelscope download --model Qwen/Qwen3-0.6B --local_dir ./Qwen3-0.6B
```

`--model`后面是模型在魔搭上的名称，`--local_dir`后面是本地保存目录，换一个模型时，把这两个位置改成自己需要的值。

<p></p>

上面的命令在终端中运行，如果放进 Notebook 的 Python 代码单元格，安装时可以使用`%pip install -U modelscope`，执行命令时在`modelscope`前加一个`!`。

结果展示：

![正文配图](<../../assets/manuscript-20260914/c02-6cc41770227681.webp>)

<a id="c2-s6"></a>

### 写进 Python 代码里，就用 SDK

在 Python 程序中，可以直接调用`snapshot_download`下载模型，比如，

```python
from modelscope import snapshot_download

model_dir = snapshot_download(
    'Qwen/Qwen3-0.6B',
    local_dir='./Qwen3-0.6B',
)
print(model_dir)
```

函数返回模型保存的位置，后续代码可以用这个路径加载模型。没有指定`local_dir`时，SDK 会使用默认缓存目录。

![正文配图](<../../assets/manuscript-20260914/c02-70ccc6e14bbd3c.webp>)

<a id="c2-s7"></a>

### 平时习惯用 Git，也可以直接拉取

模型文件通常较大，使用 Git 下载前，需要先安装 Git 和 Git LFS。安装好 Git LFS 后，再执行下面的初始化和克隆命令。

```bash
git lfs install
git clone https://www.modelscope.cn/Qwen/Qwen3-0.6B.git
```

`git lfs install`是在当前环境中初始化 Git LFS，并不负责安装这个工具本身。如果提示没有`lfs`命令，需要先完成工具安装。

![正文配图](<../../assets/manuscript-20260914/c02-973b14a709cdc5.webp>)

<p></p>

四种方式不用全部试一遍，临时拿几个文件就用网页，终端操作用命令行，Python 项目用 SDK，已有 Git 工作习惯就继续用 Git。

模型下载完成后，打开它的使用示例，把模型路径换成本地目录，先跑通一次输入和输出。

真正需要花时间的模型实验，就可以从这里开始了。

<p></p>
