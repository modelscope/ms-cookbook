<!-- Generated from ../source-html/chapter-36.html; do not edit independently. -->

# 把三个生图服务打包成 MCP：让 AI 助手随口一句话就能画图的实践

> 一句话摘要：用 Python + FastMCP 把柏拉图AI、BizyAir、魔搭三个生图服务统一封装成 MCP 服务器，AI 助手连接后一句话就能调用生图，全程踩坑记录 + 可复制配置。

<a id="c36-s1"></a>

## <strong>写在前面</strong>

我平时写文章、做项目经常需要生成配图，手里攒了三个生图渠道：柏拉图AI（apilio.ai）、BizyAir、还有魔搭社区的免费推理 API。以前的做法是每换一个渠道就翻出对应的 CLI 脚本手动跑一遍，复制图片 URL，再粘给 AI 继续处理——来回切换特别烦。

后来接触了 MCP（Model Context Protocol，你可以理解为给 AI 插上的"万能转接头"，插上之后 AI 就能直接调用你本地封装好的工具），我就想把这三个生图服务全部封装成 MCP 服务器，这样我跟 AI 说"帮我画一张赛博朋克风格的城市夜景"，它自己就知道该调哪个工具、参数怎么填。

这篇教程就带大家从零把这件事做一遍。三个服务的封装思路各不相同（一个直连 API、一个套壳 CLI、一个社区开源项目本地跑），正好覆盖了 MCP 开发最常见的三种场景。文中所有 API Key 都已脱敏，大家替换成自己的就行。

<a id="c36-s2"></a>

## <strong>效果先看</strong>

AI 助手连接配置后，在客户端里开启 MCP 服务器，就能看到三个服务提供的全部工具：

![Agent 中开启 MCP 服务器，工具列表已出现](<https://modelscope.cn/models/bozoyan/dsh-bizyair-i2-assets/resolve/master/mcp-tutorial/01-open-mcp.png>)

下面是我实测的几张出图效果，按渠道依次展示。

<strong>BizyAir-MCP</strong>——对 AI 说"用 bizyair 画一张赛博朋克风格的城市夜景，16:9"，它自动调用 `generate_image` 工具，一两分钟后返回 4k 图片 URL：

![Agent 中使用 BizyAir-MCP 生成图片](<https://modelscope.cn/models/bozoyan/dsh-bizyair-i2-assets/resolve/master/mcp-tutorial/02-bizyair-result.png>)

<strong>BLTCY-MCP</strong>——柏拉图AI 渠道出图，同样一句话搞定：

![Agent 中使用 BLTCY-MCP 生成图片](<https://modelscope.cn/models/bozoyan/dsh-bizyair-i2-assets/resolve/master/mcp-tutorial/03-bltcy-result.png>)

<strong>魔搭-MCP（卡通风格）</strong>——魔搭渠道免费额度，速度快，卡通风格表现不错：

![Agent 中使用魔搭 MCP 生成卡通图片](<https://modelscope.cn/models/bozoyan/dsh-bizyair-i2-assets/resolve/master/mcp-tutorial/04-ms-cartoon.png>)

<strong>魔搭-MCP（真人 Lora 模型）</strong>——加载社区真人 Lora 模型出写实人像。这里有个关键点：<strong>用真人 Lora 模型时，提示词里必须带人物描述</strong>（人种、年龄、发型、五官、表情、服装等），只写场景不写人，模型就不知道该把 Lora 的人物特征往谁身上套，出图会跑偏甚至崩脸。具体怎么写人物提示词，见下文「提示词小课堂」：

![Agent 中使用魔搭 MCP 真人 Lora 模型生成图片](<https://modelscope.cn/models/bozoyan/dsh-bizyair-i2-assets/resolve/master/mcp-tutorial/05-ms-lora.png>)

<a id="c36-s3"></a>

## <strong>本篇大纲</strong>

- 准备工作
- 实践流程总览
- 第一步：准备统一的 Python 环境
- 第二步：封装柏拉图AI 服务（bltcy）
- 第三步：封装 BizyAir 服务（bizyair-i2）
- 第四步：本地跑通魔搭官方示例（ms-image-gen-mcp）
- 第五步：写一份统一的 MCP 配置文件
- 提示词小课堂：人物类提示词怎么写
- 踩坑记录 / 常见问题
- 小结
- 模型信息

<a id="c36-s4"></a>

## <strong>准备工作</strong>

开始前需要准备这几样，每样都给获取方式：

<table><thead><tr><th>准备项</th><th>获取方式</th><th>用途</th></tr></thead><tbody><tr><td>macOS / Linux 电脑</td><td>——</td><td>本文以 macOS 为例</td></tr><tr><td>Miniconda</td><td>官网下载安装包</td><td>管理独立的 Python 环境</td></tr><tr><td>三个平台的 API Key</td><td>见下文各步骤</td><td>调用生图 API 的凭证</td></tr><tr><td>一个支持 MCP 的 AI 客户端</td><td>比如 Claude Code、Cherry Studio 等</td><td>连接并调用 MCP 工具</td></tr></tbody></table>

三个 Key 分别在哪拿：

- <strong>柏拉图AI（BLTCY&#95;API&#95;KEY）</strong>：apilio.ai 注册后在个人中心获取，形如 `sk-xxxxxxxx...`
- <strong>BizyAir（BIZYAIR&#95;API&#95;KEY）</strong>：BizyAir 平台控制台生成，形如 `sk-xxxxxxxx...`
- <strong>魔搭（MODELSCOPE&#95;API&#95;KEY）</strong>：modelscope.cn 个人中心 → 访问令牌页面，形如 `ms-xxxxxxxx-xxxx-...`

> 🔒 安全提醒：API Key 不要写进代码里提交到公开仓库，统一放在环境变量或本地的 `.env` 文件里，代码里只读环境变量。

<a id="c36-s5"></a>

## <strong>实践流程总览</strong>

1. 用 conda 建一个统一的 Python 环境，装好 MCP 相关依赖
2. 写第一个 MCP 服务器：直连 API 的 bltcy（柏拉图AI）
3. 写第二个 MCP 服务器：子进程封装 CLI 的 bizyair-i2（BizyAir）
4. 本地跑通第三个：社区现成的 ms-image-gen-mcp（魔搭）
5. 写一份统一的 `mcp-servers.json` 配置文件，三个服务一次接入
6. 插入 AI 客户端验证工具列表，实测生图

<a id="c36-s6"></a>

## <strong>第一步：准备统一的 Python 环境</strong>

<strong>做什么</strong>：建一个 conda 环境，三个 MCP 服务共用它，以后缺什么包装一次就够。

<strong>怎么做</strong>：

```bash
# 创建名为 modelscope 的环境（Python 3.10 够用）
conda create -n modelscope python=3.10 -y
conda activate modelscope

# 安装 MCP SDK —— 注意必须装 1.x 版本！原因见"踩坑记录"第 1 条
pip install "mcp<2"

# 三个服务各自需要的其他依赖
pip install requests python-dotenv pillow httpx
```

<strong>预期看到什么</strong>：执行 `pip list | grep mcp` 能看到 `mcp 1.x.x`（我这里装到的是 1.30.0），说明环境就绪。整个安装一两分钟。

记住这个环境的 python 绝对路径，后面配置文件里要用（我的是 `/Users/yons/miniconda3/envs/modelscope/bin/python`，你的用户名不一样路径会不同）。

<a id="c36-s7"></a>

## <strong>第二步：封装柏拉图AI 服务（bltcy）</strong>

<strong>做什么</strong>：写一个 `server.py`，用 httpx 异步直连 apilio.ai 的生图 API，提供文生图、图生图两个工具。

<strong>怎么做</strong>：核心骨架长这样（完整代码约 300 行，这里只讲关键结构）：

```python
from mcp.server.fastmcp import FastMCP

# 1. 初始化 MCP 服务，起个名字
mcp = FastMCP(
    name="bltcy",
    instructions="柏拉图AI GPT-image-2 绘图服务 — 文生图/图生图"
)

# 2. 用装饰器把普通函数注册成 MCP 工具
@mcp.tool()
async def text_to_image(prompt: str, size: str = "1008x1792",
                        aspect_ratio: str = "") -> list[dict]:
    """文生图 — 根据文字描述生成图片"""
    client, base_url = _get_client()          # 从环境变量读 API Key
    payload = {"model": "gpt-image-2", "prompt": prompt, "size": size}
    resp = await client.post("/images/generations", json=payload)
    resp.raise_for_status()
    # ...解析返回的图片 URL 列表...

# 3. stdio 模式启动：MCP 客户端会以子进程方式拉起本脚本
if __name__ == "__main__":
    mcp.run()
```

写完先自测一下导入没问题：

```bash
python -c "import server; print('OK')"
```

<strong>预期看到什么</strong>：打印 `OK` 就说明服务代码本身没问题，可以进入后面的配置接入环节。

<a id="c36-s8"></a>

## <strong>第三步：封装 BizyAir 服务（bizyair-i2）</strong>

<strong>做什么</strong>：我手上已经有一个写好的 BizyAir 命令行脚本 `bizyair-i2.py`（带智能解析、任务轮询、本地图片自动上传 OSS、网络重试等一堆逻辑）。这次封装我<strong>没有重写这些逻辑</strong>，而是让 MCP 服务器用子进程方式调用这个 CLI——这是"已有脚本快速 MCP 化"的通用套路。

<strong>怎么做</strong>：思路是用 `subprocess.run` 拉起 CLI，再从输出里解析结果：

```python
import subprocess, sys, re
from pathlib import Path

CLI_PATH = Path(__file__).resolve().parent / "bizyair-i2.py"

def _run_cli(args: list[str]) -> str:
    """子进程运行 CLI，任何报错都不会把 MCP 服务带崩"""
    proc = subprocess.run(
        [sys.executable, str(CLI_PATH)] + args,
        capture_output=True, text=True, timeout=900,
    )
    if proc.returncode != 0:
        err_lines = [l for l in proc.stderr.splitlines() if l.strip()]
        raise RuntimeError(f"生成失败: {err_lines[-1] if err_lines else '未知错误'}")
    return proc.stdout

@mcp.tool()
def generate_image(prompt: str, aspect_ratio: str = "16:9",
                   resolution: str = "4k", images: list[str] | None = None) -> dict:
    """BizyAir 文生图/图生图，images 传入参考图即为图生图模式"""
    args = ["--prompt", prompt, "--ar", aspect_ratio, "--resolution", resolution]
    if images:
        args += ["--images"] + images
    output = _run_cli(args)
    # 从 CLI 输出中解析图片 URL 和本地保存路径
    urls = re.findall(r'\[\d+\]\s*URL:\s*(\S+)', output)
    return {"urls": urls}
```

两个封装细节值得说：

- <strong>为什么用子进程而不是直接 import？</strong> CLI 脚本里有很多 `sys.exit(1)`（比如图片不存在时直接退出），如果直接 import 进 MCP 进程，一次报错就把整个服务干掉了。子进程方式等于加了一层隔离舱，崩溃了只是那一次调用失败，服务还活着。
- <strong>为什么默认 4k 分辨率、解析 stdout？</strong> 因为复用 CLI 的现有行为，CLI 打印什么格式我就解析什么格式，零改动。

<strong>预期看到什么</strong>：同样的自测命令 `python -c "import server; print('OK')"`，以及 `python -c "import server; print(server.check_api_key())"` 应该返回 `{'configured': True, 'key': 'sk-xxxx...xxxx'}`（Key 自动脱敏显示）。

<a id="c36-s9"></a>

## <strong>第四步：本地跑通魔搭官方示例（ms-image-gen-mcp）</strong>

<strong>做什么</strong>：魔搭官方提供了开源的 `ms-image-gen-mcp` 项目，把代码 clone 到本地后直接用我们第一步建好的环境运行，不需要额外安装。

<strong>怎么做</strong>：这个项目本身就是标准 MCP 结构，入口是包内的 `server.py`，直接验证：

```bash
# 用统一环境直接跑（注意路径换成你自己的克隆位置）
/Users/yons/miniconda3/envs/modelscope/bin/python \
    ms_image_gen_mcp/server.py
```

它提供三个工具：`search_models`（搜魔搭社区的生图模型）、`text_to_image`（文生图）、`text_image_to_image`（图生图，支持本地图片路径自动转 base64，超过 2048px 还会自动缩放——这个细节官方处理得很贴心）。

<strong>预期看到什么</strong>：命令执行后终端"卡住"不动是正常的——stdio 模式的 MCP 服务就是在等客户端发指令，没有报错退出就说明启动成功，`Ctrl+C` 退出即可。

<a id="c36-s10"></a>

## <strong>第五步：写一份统一的 MCP 配置文件</strong>

<strong>做什么</strong>：三个服务写好之后，用一个 JSON 配置文件统一描述，AI 客户端一次全部接入。

<strong>怎么做</strong>：文件放在 `/Volumes/HAO/PY/2026/MCP/mcp-servers.json`（示例中 Key 已脱敏，实际文件里是真实 Key）：

```json
{
  "mcpServers": {
    "bltcy": {
      "command": "/Users/yons/miniconda3/envs/modelscope/bin/python",
      "args": ["/Volumes/HAO/PY/2026/MCP/bltcy/server.py"],
      "env": { "BLTCY_API_KEY": "sk-xxxxxxxxxxxxxxxx" }
    },
    "bizyair-i2": {
      "command": "/Users/yons/miniconda3/envs/modelscope/bin/python",
      "args": ["/Volumes/HAO/PY/2026/MCP/bizyair-i2/server.py"],
      "env": { "BIZYAIR_API_KEY": "sk-xxxxxxxxxxxxxxxx" }
    },
    "ms-image-gen-mcp": {
      "command": "/Users/yons/miniconda3/envs/modelscope/bin/python",
      "args": ["/Volumes/HAO/PY/2026/MCP/ms-image-gen-mcp/ms_image_gen_mcp/server.py"],
      "env": { "MODELSCOPE_API_KEY": "ms-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" }
    }
  }
}
```

三个字段都好理解：`command` 是用哪个程序启动（我们统一用 conda 环境的 python），`args` 是服务脚本路径，`env` 是注入给服务的环境变量（Key 从这里传进去，不写死在代码里）。

配置文档在客户端里的样子：

![mcp-servers-json 配置文档](<https://modelscope.cn/models/bozoyan/dsh-bizyair-i2-assets/resolve/master/mcp-tutorial/06-json-config.png>)

<strong>预期看到什么</strong>：在 AI 客户端里导入这份配置（或把内容粘进客户端的 MCP 设置），重启后工具列表里出现 `generate_image`、`text_to_image`、`search_models` 等工具，就是接入成功了。下面两张图是客户端里自定义和管理 MCP 服务器的界面，服务有改动时（比如换脚本路径、换 Key）在"编辑"里改完保存重启即可：

![Agent 中自定义 MCP 服务器管理器](<https://modelscope.cn/models/bozoyan/dsh-bizyair-i2-assets/resolve/master/mcp-tutorial/07-mcp-manager.png>)

![Agent 中编辑 MCP 服务器](<https://modelscope.cn/models/bozoyan/dsh-bizyair-i2-assets/resolve/master/mcp-tutorial/08-mcp-edit.png>)

<a id="c36-s11"></a>

## <strong>提示词小课堂：人物类提示词怎么写</strong>

工具接好了只是第一步，出图质量的大头在提示词上。我之前整理过一套摄影人像的提示词心得（krea2 模型实测总结，大部分原则对其他模型同样适用），这里提炼出最通用的几条，配合上文真人 Lora 的场景正好用得上。

一条结构完整的人物提示词，建议按这个顺序组织，每一段都别偷懒：

```text
[人物主体] + [五官与表情] + [服装] + [姿势动作] + [光源] + [镜头] + [画质词]
```

逐段拆解：

<strong>① 人物主体要锁定特征。</strong> 人种、年龄、发型一次写清，比如 `A young East Asian woman in her mid-20s, jet black hair in a sleek straight cut`。特征锁定后全篇保持一致，不要前面写黑发后面又冒出棕发。真人 Lora 尤其依赖这段描述——Lora 提供的是"某个人"的特征，提示词提供的是"这个人此刻的样子"，两者缺一不可。

<strong>② 姿势要具体到重心和手。</strong> 只写 `standing` 或 `sitting`，AI 十有八九给你一个僵硬的站姿。要写明重心在哪条腿、手放在哪里、身体朝向，例如 `weight on one leg with the hip slightly shifted, one hand resting on her hip`，出图的动态感完全不同。

<strong>③ 光影放在提示词前半段。</strong> 光源方向、软硬（soft/hard/diffused）、色温写前面更容易被准确渲染，比如 `warm golden hour backlight from the right`。想要氛围感可以加 `volumetric light`（体积光）、`lens flare`（镜头光晕）这类词，但一套提示词最多用一两个，多了会打架。

<strong>④ 镜头焦段按场景选。</strong> 人物特写用 `85mm lens`（中焦突出人物、背景奶油虚化），大场景用 `24-35mm` 广角展现空间感。

<strong>⑤ 画质词克制。</strong> 结尾放两三个就够（`8K, photorealistic`），堆一大串画质词反而稀释主体权重，画面过度锐化反而一股"AI味"。

<strong>⑥ 色彩对比写具体。</strong> 写 `deep teal and warm gold color palette`（两组明确的对比色）比笼统一句 `colorful` 效果好得多。

最后补一个参数经验：`guidance`（引导强度，相当于 CFG）柔光人像用 7 左右保持通透，暗调强对比场景可以到 8 以上；`steps`（采样步数）质量敏感的任务给足 30 步，快速出草稿 8 步就够——这也正是魔搭 MCP 里文生图默认 `steps=8, guidance=1`（求快）、图生图默认 `steps=30, guidance=4`（求精）的差别。

<a id="c36-s12"></a>

## <strong>踩坑记录 / 常见问题</strong>

这部分是我这次实践真实踩的坑，每个都附定位过程，照着避坑能省不少时间。

<a id="c36-s13"></a>

### <strong>坑 1：装了最新版 mcp 包，服务直接报 `ModuleNotFoundError: No module named 'mcp.server.fastmcp'`</strong>

AI 客户端连接时报 `Connection closed`，手动跑服务看到完整报错：

```text
raise ModuleNotFoundError(_MESSAGE, name=__name__)
ModuleNotFoundError: No module named 'mcp.server.fastmcp'.
This is mcp 2.x, where FastMCP was renamed to MCPServer ...
```

定位：报错信息其实已经把答案说出来了——`mcp` 包 2.x 大版本把 `FastMCP` 类改名成了 `MCPServer`，而目前绝大多数教程和现成代码都是按 1.x 的 API 写的。

解决：安装时固定版本 `pip install "mcp<2"`。我环境里装到的是 1.30.0。

<a id="c36-s14"></a>

### <strong>坑 2：uvx 启动命令里写 `mcp<2`，报 `An executable named '2' is not provided by package`</strong>

我一开始想用 `uvx` 拉起魔搭那个 MCP，命令里写了 `--with mcp<2`，结果报错说找不到叫 `2` 的可执行程序。折腾半天才反应过来：<strong>命令行里 `<` 是输入重定向符号</strong>，`mcp<2` 被 shell 拆成了 `mcp` 加"从名为 2 的文件读入"，后面的参数全乱了。而且 `uvx --from 包名` 后面只能跟包自带的命令名，不能直接接 python 路径。

解决：彻底放弃 uvx，缺的依赖直接装进 conda 环境，用 python 绝对路径直接跑 `server.py`。反而更简单，三个服务的启动方式还完全统一了。

<a id="c36-s15"></a>

### <strong>坑 3：API Key 读了半天是空的</strong>

BizyAir 的 Key 我明明配置过，服务里就是读不到。排查发现它只存在于我的 shell 环境变量里，并不在 `~/.hermes/.env` 文件中——而 MCP 客户端拉起服务时不一定会继承交互终端的环境变量。

解决：把 Key 统一写进 MCP 配置文件的 `env` 字段（第五步的做法），由客户端在启动时注入，不再依赖 shell 环境。

<a id="c36-s16"></a>

### <strong>坑 4（常见坑提示）：MCP 服务里千万别往 stdout 打印日志</strong>

stdio 模式下，stdout 是 MCP 协议的通信通道。如果你的工具函数里 `print()` 了进度信息，会把 JSON-RPC 消息流搅乱，客户端直接解析失败。日志一律打到 stderr（`print(..., file=sys.stderr)`），这是 MCP 开发的隐形规矩。我的 bizyair-i2 用子进程隔离方案恰好绕开了这个问题——CLI 的所有输出都被 `capture_output=True` 捕获了，不会污染协议通道。

<a id="c36-s17"></a>

## <strong>小结</strong>

到这里，三个生图服务就全部 MCP 化了。回顾一下这次实践我最大的三点收获：

1. <strong>三种封装思路各有适用场景</strong>：直接调 API 最干净（bltcy）、子进程套壳 CLI 最省事且自带故障隔离（bizyair-i2）、社区现成项目直接跑最零成本（ms-image-gen-mcp）。以后遇到新服务，按"有没有现成脚本"来选路子就行。
2. <strong>版本锁定意识</strong>：`mcp<2` 这种大版本变更（类都改名了）随时可能发生，教程代码和生产配置里显式锁版本能少踩很多坑。
3. <strong>配置即文档</strong>：一份 `mcp-servers.json` 把服务路径、启动方式、凭证来源全部收敛在一起，换台电脑只需要改路径。

不足是目前三个服务的工具命名还不完全统一（比如都叫"文生图"但参数名各异），下一步打算在 AI 侧写一个路由提示词，让它根据价格、速度、画质需求自动选渠道。有兴趣的话下篇继续。

<a id="c36-s18"></a>

## <strong>模型信息</strong>

本项目基于 ModelScope 魔搭社区的大模型开发，感谢社区提供免费算力与模型支持：

- <strong>文生图默认模型</strong>：`bozoyan/k-yanbo`
- <strong>模型主页</strong>：[https://modelscope.cn/models/bozoyan/k-yanbo](<https://modelscope.cn/models/bozoyan/k-yanbo>)
- <strong>图生图默认模型</strong>：`FireRedTeam/FireRed-Image-Edit-1.1`
- <strong>模型主页</strong>：[https://modelscope.cn/models/FireRedTeam/FireRed-Image-Edit-1.1](<https://modelscope.cn/models/FireRedTeam/FireRed-Image-Edit-1.1>)
- <strong>调用方式</strong>：通过 `ms-image-gen-mcp` 的 `text_to_image` / `text_image_to_image` 工具，请求魔搭 API-Inference 服务（`https://api-inference.modelscope.cn/`）
- <strong>找更多模型</strong>：`search_models` 工具可直接搜索魔搭社区支持推理的生图模型
