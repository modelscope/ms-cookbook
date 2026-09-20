<!-- Generated from ../source-html/chapter-04.html; do not edit independently. -->

# 没有资源也能玩开源模型，因为这里资源免费

模型找到了，数据也准备好了，结果卡在了最后一个问题上，没有资源跑，

自己的电脑没有显卡，或者显存不够，甚至连内存都不够，这太让人心痛了～

<p></p>

没关系，可以先用魔搭提供的免费资源，

<strong>魔搭 Notebook 把开发环境放在了云端，打开浏览器，就能写代码、处理数据，也能在免费 GPU 额度内尝试模型推理和小规模微调。</strong>

刚开始学习开源模型，不必先买一台新电脑，先把一个小实验跑起来，看看自己究竟需要多少资源。

<p></p>

<a id="c4-s1"></a>

## 免费资源有多少，先看清楚再用

魔搭提供免费 CPU 环境，也提供有时长限制的 GPU 环境，免费资源包括下面这些，

<table><tbody><tr><td><p>资源</p></td><td><p>配置与额度</p></td><td><p>可以先用来做什么</p></td></tr><tr><td><p>CPU 环境</p></td><td><p>8 核 CPU、32GB 内存，免费使用时长不限</p></td><td><p>下载文件、处理数据、调试代码</p></td></tr><tr><td><p>GPU 环境</p></td><td><p>NVIDIA A10、24GB 显存，36 小时免费时长</p></td><td><p>适合该显存规模的模型推理和小规模微调</p></td></tr><tr><td><p>存储空间</p></td><td><p>100GB 持久化存储</p></td><td><p>保存代码、模型、数据和实验结果</p></td></tr></tbody></table>

<p></p>

<a id="c4-s2"></a>

## 打开浏览器，先把 Notebook 启动起来

登录魔搭，进入[我的 Notebook](<https://modelscope.cn/my/mynotebook>)，如果页面提示需要完成账号绑定或认证，按页面指引操作，再选择 CPU 或 GPU 环境。选好后，点击“启动”，等待实例创建。

![正文配图](<../../assets/manuscript-20260914/c04-8e54a4319c83d2.webp>)

<p></p>

实例就绪后，点击查看 Notebook 进入开发页面，下方截图里会出现体验新版的提示，按提示进入即可；界面更新后，以当前入口为准。

![正文配图](<../../assets/manuscript-20260914/c04-cb10124282fbf0.webp>)

<p></p>

<a id="c4-s3"></a>

## 文件存在哪里，这件事要记住

进入环境后，可以在左侧文件区上传自己的代码和数据，也可以把需要的结果下载回本地。

![正文配图](<../../assets/manuscript-20260914/c04-fb60b44eab2e14.webp>)

<strong>需要保留的文件，放在</strong><strong>`/mnt/workspace`</strong><strong>目录下，</strong> 魔搭提供的 100GB 持久化存储挂载在这里，其他路径中的文件默认会在实例关闭后不会继续保留。

可以在这个目录下分别建立模型、数据和输出文件夹，后面找东西会方便一些。在终端执行下面的命令即可。

```bash
mkdir -p /mnt/workspace/models /mnt/workspace/data /mnt/workspace/outputs
```

下载模型时，也可以直接指定保存位置。

```python
from modelscope import snapshot_download

model_dir = snapshot_download(
    'Qwen/Qwen3-0.6B',
    local_dir='/mnt/workspace/models/Qwen3-0.6B',
)
print(model_dir)
```

如果想看看已经用了多少存储，在终端执行下面这条命令。

```bash
du -sh /mnt/workspace
```

模型文件容易占空间，不再需要的版本可以及时清理。重要代码和实验结果也可以定期下载一份到本地。

<p></p>

<a id="c4-s4"></a>

## 先运行一行代码，后面就好办了

在文件区新建一个`test.ipynb`文件，打开后添加代码单元格。第一次可以先写一行简单的 Python。

```python
print('你好，魔搭Notebook！')
```

点击代码单元格左侧的运行按钮，输出会显示在下方。看到这句话，就说明你已经成功在云端执行了代码。

![正文配图](<../../assets/manuscript-20260914/c04-813ceec84fa022.webp>)

需要安装 ModelScope 时，可以在代码单元格里运行下面的命令。

```python
%pip install -U modelscope
```

然后新建一个单元格，粘贴前面的模型下载代码。需要读取数据时，也可以继续添加`MsDataset.load`示例。

Notebook 的方便之处就在于，代码、说明和运行结果可以放在同一个文件里，改一段、跑一段，哪里报错就回到哪里检查。

<p></p>

<a id="c4-s5"></a>

## 实验结束，别让 GPU 一直开着

免费 GPU 有时长限制，任务跑完后记得停止实例。只是离开页面或者关闭浏览器，不要当成已经停止了云端机器。返回 Notebook 页面可以查看剩余额度。

<p></p>

长任务要提前安排保存进度，训练得到的文件写到`/mnt/workspace`里。GPU 额度用完后，还可以继续使用免费 CPU 环境处理数据和调试代码；需要更多算力时，再按需求选择活动资源或付费服务。

<p></p>

第一次不用把任务安排得太满，打开环境，建一个 Notebook，下载一个小模型，把示例跑起来，

可以参考【30 分钟看到第一个结果】章节。
