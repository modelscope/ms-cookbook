<!-- Generated from ../source-html/chapter-03.html; do not edit independently. -->

# 数据，是你要做开源模型微调的基石

你是否遇到过这种情况，一个模型可以在写代码、做数学题表现的十分优秀，但你问一个日常的问题，却给你瞎回答。

<p></p>

我们都知道模型在训练的过程中，想要那个部分的能力提高，就针对性的找那类的数据，

但很多数据，你直接互联网检索，很难找到，有一个数据的统一下载入口，对于模型训练者来说，会节省很大的精力。

比如，我们当时开源的中文基于满血 DeepSeek-R1 蒸馏数据集，其中很多原始数据都是从魔搭上直接下载的，

![正文配图](<../../assets/manuscript-20260914/c03-4de63a06f1d781.webp>)

我们模型的微调，可以从一份现成的开源数据集开始，这样可以快速跑通整个流程。

<p></p>

<a id="c3-s1"></a>

## 找数据，也要先知道自己准备做什么

魔搭整合了超过 4 万个开源数据集，平台支持数据集搜索和预览，提供字段说明及数据集版本。

魔搭支持根据关键词标签及任务类别搜索数据集，如，检索语言中文的二分类文本分类数据，

![正文配图](<../../assets/manuscript-20260914/c03-d1a6f009d63cac.webp>)

<p></p>

<a id="c3-s2"></a>

## 下载之前，先翻几条数据看看

筛选出数据集后，选择感兴趣的数据集，点击“数据预览”可以在线查看样本内容与字段说明，辅助数据选型决策，如 [simpleai/HC3-Chinese](<https://modelscope.cn/datasets/simpleai/HC3-Chinese>)。

![正文配图](<../../assets/manuscript-20260914/c03-5e43d34eec8f6c.webp>)

问题放在哪一列，答案放在哪一列，有没有标签，一条数据里是一段文字还是一组对话，这些都可以先看清楚。后面写处理代码时，就不用对着字段名猜了。

以问答数据为例，人类回答和模型回答可能分别保存在不同字段里，准备拿它做什么任务，就要决定读取哪些字段、怎样整理，不能只看到问答两个字就直接开始训练。

<p></p>

再到数据集文件里看看文件和版本，同一份数据集会更新，训练样本、字段或者划分也可能变化。做实验时记下用的是哪个版本，后面才容易复现。

![正文配图](<../../assets/manuscript-20260914/c03-c33f6d404ef93d.webp>)

数据集的说明和许可证也值得一起看。能下载的数据，用于研究、训练或者商业产品时，可能有不同要求。

<p></p>

<a id="c3-s3"></a>

## 先把数据读进来，再决定用哪一部分

魔搭提供了`MsDataset.load`接口，可以在 Python 里加载数据集。安装 ModelScope 后，就可以按数据集页面的使用说明操作。

<p></p>

<a id="c3-s4"></a>

### 先加载一份完整的数据

以 [DAMO&#95;NLP/jd](<https://modelscope.cn/datasets/DAMO_NLP/jd>) 为例，可以这样读取默认配置下的数据，

```python
from modelscope.msdatasets import MsDataset

ds = MsDataset.load(
    'DAMO_NLP/jd',
    trust_remote_code=True,
)
print(ds)
```

![正文配图](<../../assets/manuscript-20260914/c03-be7695c08c686f.webp>)

<p></p>

<a id="c3-s5"></a>

### 只需要其中一个子集，就把名字写清楚

有些数据集会把不同来源、领域或用途的数据分开保存。如果只关心其中一部分，就用`subset_name`指定子集。

<p></p>

例如，读取 HC3-Chinese 里的`baike`子集。

```python
from modelscope.msdatasets import MsDataset

ds = MsDataset.load(
    'simpleai/HC3-Chinese',
    subset_name='baike',
    trust_remote_code=True,
)
print(ds)
```

![正文配图](<../../assets/manuscript-20260914/c03-1e8bcc0c71e19b.webp>)

换一份数据集时，要先查它有哪些子集。`baike`是这里的具体名称，不能原样套到其他数据集上。

<p></p>

<a id="c3-s6"></a>

### 训练集和测试集，也可以分开取

子集选的是哪一类数据，`split`选的是数据的哪一个划分。常见的有训练集`train`、验证集`validation`和测试集`test`。

<p></p>

只读取`baike`子集里的训练集，可以再加一个参数。

```python
from modelscope.msdatasets import MsDataset

ds = MsDataset.load(
    'simpleai/HC3-Chinese',
    subset_name='baike',
    split='train',
    trust_remote_code=True,
)
print(ds[0])
```

![正文配图](<../../assets/manuscript-20260914/c03-5bd2b9c5f8a03f.webp>)

并不是每份数据都同时提供这三种划分，具体名称要看数据集说明。拿到训练集后，先打印一条样本，确认字段和内容都符合预期，再接后面的处理代码。

<p></p>

<a id="c3-s7"></a>

### 想复现实验，记得把版本一起记下来

数据更新以后，同一段代码可能读取到不同内容。以 HC3-Chinese 的`v1`版本为例，可以通过`version`明确指定。

```python
from modelscope.msdatasets import MsDataset

ds = MsDataset.load(
    'simpleai/HC3-Chinese',
    subset_name='baike',
    version='v1',
    trust_remote_code=True,
)
print(ds)
```

![正文配图](<../../assets/manuscript-20260914/c03-1217bdcfbfd54f.webp>)

<p></p>

实际操作时，到数据集页面确认可用版本。如果某个版本会持续更新，还要保留当时使用的数据文件或校验信息，方便之后对照。

<p></p>

<a id="c3-s8"></a>

## 数据下载好了，先别急着全交给模型

先抽几条样本看看有没有空值、乱码或者明显错误，再确认字段是不是符合训练代码要求。同一批问题的答案格式，如果前后差别很大，也需要先整理。

<p></p>

训练数据和测试数据还要分开。准备用来检查模型效果的样本，别提前混进训练集，否则分数看着不错，却很难判断模型遇到新问题时怎么样。

<p></p>

<p></p>

<p></p>
