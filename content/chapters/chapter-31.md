<!-- Generated from ../source-html/chapter-31.html; do not edit independently. -->

# 快速使用 DeepSeek Harness

DeepSeek 在 2026 年 8 月 13 号开源了他们的第一个 Agent 产品：DeepSeek Harness。

这 Star 涨得快的离谱。我记得仅仅一天就涨到了 <strong>64.2k Star</strong>，写这篇的时候已经 221K Star 了。一个月的时间，涨了 22 万星，恐怖如斯。

![正文配图](<../../assets/manuscript-20260914/c29-742525f0e682d2.webp>)

安装其实非常简单：只要你电脑环境没问题，核心就一条命令：

```bash
npx @deepseek-ai/dsh web
```

简单，但不代表每台电脑都能一次安装成功，还是有一些小坑在这里面。

我在自己的 Mac 上完整跑了一遍安装流程，安装明明成功了，启动的时候还是踩了一个 Node.js 版本的坑（后面细说）。

![正文配图](<../../assets/manuscript-20260914/c29-f846a2a5a71b4c.webp>)

这篇将分享两种安装方案，都是实际跑通过的：

1. 懒人路线：把提示词直接甩给 Codex、Claude Code 或者其他 Agent，让它替你检查环境、安装和验证。
2. 动手路线：自己一步一步装，遇到报错丢给 AI 看。

<a id="c31-s1"></a>

## 我这台机器的实测环境

- macOS 26.0.1，Apple Silicon（arm64）
- zsh 5.9
- Node.js v22.19.0
- npm / npx 10.9.3
- `@deepseek-ai/dsh 0.1.0-rc.6`
- Web UI：`http://127.0.0.1:3080`

<a id="c31-s2"></a>

## 方法一：直接把活儿甩给 Agent

把下面这段完整发给 Codex、Claude Code 或者其他能跑终端命令的 Agent：

```text
请根据我当前电脑环境安装并启动 DeepSeek Harness：
1. 先检查 Node.js、npm、系统架构和 3080 端口；缺少依赖时先说明再安装。
2. 使用 npm 全局安装 @deepseek-ai/dsh。
3. 根据当前版本的 --help 和官方 GitHub README 确认正确的 Web UI 启动命令，不要猜参数。
4. 启动后验证本机端口和网页是否可访问，并告诉我打开地址。
5. 遇到问题先查 https://github.com/deepseek-ai/deepseek-harness ，不要输出或修改任何 API Key。
```

<p></p>

<a id="c31-s3"></a>

## 方法二：自己动手，一步步装

<a id="c31-s4"></a>

### 第 1 步：检查环境

```bash
node -v
npm -v
uname -m
```

我这边分别得到 Node.js v22.19.0、npm 10.9.3 和 arm64。

DeepSeek Harness 当前仓库声明的 Node.js 范围是：

```text
^22.19.0 || >=24.0.0
```

低于这个范围，先把 Node.js 升上去再说。

<a id="c31-s5"></a>

### 第 2 步：尝个鲜/长期用

如果只想尝鲜体验：

```bash
npx @deepseek-ai/dsh web
```

准备长期使用：

```bash
npm install -g @deepseek-ai/dsh
```

我实测的时候，官方 npm registry 在这台电脑上 DNS 超时了，最后是走镜像装好的：

```bash
npm install -g @deepseek-ai/dsh --registry=https://registry.npmmirror.com
```

验证安装：

```bash
dsh --version
dsh --help
```

实测版本 `0.1.0-rc.6`。当前版本里，`dsh web` 是 `dsh --profile web` 的短写。

<a id="c31-s6"></a>

### 第 3 步：启动网页端

```bash
dsh web
```

等价写法：

```bash
dsh --profile web
```

启动成功会显示：

```text
dsh web: http://127.0.0.1:3080
```

浏览器打开 `http://127.0.0.1:3080` 就能看到界面了。

<a id="c31-s7"></a>

## 装好了，为什么还是启动失败？

我第一次启动，`dsh` 实际调用的是 `/usr/local/bin/node`，对应 Node.js v22.14.0，但是直接报错了：

```text
The requested module 'node:zlib' does not provide an export named 'createZstdDecompress'
```

排查下来，是执行 `dsh` 的 Node 太旧，缺少它需要的 Zstd API。切到 Node.js v22.19.0，Harness 就能正常启动🤦‍♂️

![正文配图](<../../assets/manuscript-20260914/c29-7021cec3f8f494.webp>)

所以不能只看某个终端里的 `node -v`，还要看：

```bash
which node
which dsh
```

如果你电脑上同时装了 nvm、Homebrew 和系统 Node，特别容易出现"你看到的是一个 Node，真正干活的是另一个 Node"这种灵异现象。

<a id="c31-s8"></a>

## 第一次打开网页

首次访问会先看到"内测声明"。

![正文配图](<../../assets/manuscript-20260914/c29-d4c55308985133.webp>)

点继续，进入 API Key 引导。

![正文配图](<../../assets/manuscript-20260914/c29-0dfb6d0697d126.webp>)

你可以立刻填 DeepSeek 的 API Key，也可以先点"稍后配置"。如果环境或 Harness 设置里已经有可识别的 Key，可能不用重复填，以当前版本的实际页面为准。

我后面是通过 Web 引导页保存的 Key。当前版本会把凭据写进 `~/.dsh/.credentials.yaml`，实测文件权限是 `600`，只有当前用户可读写。

<a id="c31-s9"></a>

## 选工作区，新建会话

点左侧"添加工作区"，选一个你准备交给 Harness 接管的文件夹。我用的是一个空白测试目录 `DeepSeek-harness-Work`。

新建会话后，输入框解锁，主界面有四个关键状态：

![正文配图](<../../assets/manuscript-20260914/c29-f8ad18cd3d42d9.webp>)

1. 工作区：Agent 能动的项目范围；
2. 模式：标准、PTC、极简或创造；
3. 权限：比如 Workspace Write；
4. 模型与推理等级：我这次是 DeepSeek-V4-Flash High。

第一次玩，千万不要直接选重要项目。先拿空目录确认权限和行为，再上真实的代码仓库。

<a id="c31-s10"></a>

## 用一个最小任务，验证它真的能干活

我在测试目录放了两个文件：

- `project-notes.md`：项目目标、文件说明和约束；
- `tasks.csv`：3 条待办。

发给 Harness 的提示词：

```text
请先阅读当前目录里的 project-notes.md 和 tasks.csv，整理这个小项目的目标、文件说明和待办事项，并生成一份简洁的 README.md。开始前先给出计划；除 README.md 外不要修改其他文件。
```

别小看这个任务，它一次能验证五件事：工作区、文件读取、计划、文件写入和约束遵守。

我先把权限切到 Read Only，跑了一次纯连通性测试。DeepSeek-V4-Flash 按要求返回"DeepSeek Harness API 实测成功"，没有调用任何工具。界面显示用时约 2 秒、首 token 约 2.5 秒、约 241 tok/s，这个速度是真挺快的。

![正文配图](<../../assets/manuscript-20260914/c29-096c573d38eae8.webp>)

然后在切换回 Workspace Write，跑完整的任务。Agent 的实际流程是：

1. 先列计划；
2. 读取 `project-notes.md` 和 `tasks.csv`；
3. 归纳项目目标、文件说明和待办事项；
4. 生成 `README.md`；
5. 再检查一遍目录，确认其他文件没被动过。

整个任务用时约 12 秒，唯一新增的文件就是 `README.md`。我还是不太放心，又在 Agent 外部对两个原始文件做了 SHA-256 对比，跟测试前的副本完全一致。"除 README 外不要修改其他文件"这条约束，它是真的遵守。

![正文配图](<../../assets/manuscript-20260914/c29-21feb289c94428.webp>)

<a id="c31-s11"></a>

## 四种模式怎么选

![正文配图](<../../assets/manuscript-20260914/c29-4681294155d0a3.webp>)

本机"设置 → Agent 预设"页能直接看到四张预设卡片，每个预设都能查看或复制，页面还有"用创造模式创作自定义预设"的入口。

![正文配图](<../../assets/manuscript-20260914/c29-7c7927e707f1d6.webp>)

<a id="c31-s12"></a>

### 标准模式

完整编码 Agent，支持文件编辑、Shell、文件与网页检索、Skills、计划、目标、子代理和工作流。第一次用，直接选它。

<a id="c31-s13"></a>

### PTC 模式

标准模式的能力都有，另外通过 Code Mode SDK 暴露工具，让模型用 TypeScript 程序组合多步操作。适合批量处理和自动化流程。

<a id="c31-s14"></a>

### 极简模式

只保留持久 Bash 和 `str_replace_editor`，适合最小环境和模型基准测试。

<a id="c31-s15"></a>

### 创造模式

在标准模式上加了运行时检查、插件实验和自定义 preset 创作，适合魔改 Harness、开发新的 Agent 模板。

<a id="c31-s16"></a>

## 它和 Codex、Claude Code 最不一样的地方

一句话：DeepSeek Harness 不只是一个固定的编程 Agent，更像一套"给 Agent 装能力的装扮系统"。

官方的说法是：<strong>一切皆插件</strong>。

模型、工具、技能、会话、沙箱、存储、循环、调度和 UI，全都是插件。你可以换模型、装外部工具、接 Skills、调权限、开搜索、改界面、调用子 Agent，甚至重新组合运行模式。

这话听起来像宣传语，但我在本机"设置 → 插件 → 插件列表"里有一大堆插件：模型、会话、凭据、沙箱、权限、Skills、目标、子 Agent、工作流、Web 搜索、工作区、Trajectory，还有一大堆 UI 组件。

![正文配图](<../../assets/manuscript-20260914/c29-504091d01836ce.webp>)

它还提供仅追加的会话日志，把系统提示词、工具调用、子 Agent 调度和上下文注入放进同一条事件流，方便恢复、分叉、检索和回放。

所以它更像一个能被开发者反复魔改的 Agent 底座，而不是单纯的"DeepSeek 版 Codex"。

<a id="c31-s17"></a>

## 全网目前最火的 5 类玩法

GitHub 的 [dsh-plugin Topic](<https://github.com/topics/dsh-plugin>) 有非常多的公开仓库。

![正文配图](<../../assets/manuscript-20260914/c29-673698eb90f6a2.webp>)

<a id="c31-s18"></a>

### 接进完整 AI 工作台

[iPolloWork](<https://github.com/Devin-AXIS/iPolloWork>)：覆盖代码、设计、PPT、网站和视频工作流，把 DSH 用作专门子 Agent 的委派层。

<a id="c31-s19"></a>

### 做跨平台内容发现 Agent

[OpenBiliClaw](<https://github.com/whiteguo233/OpenBiliClaw>)：覆盖 B 站、小红书、抖音、YouTube、X、知乎、Reddit、微博和开放 Web，并声明支持 DeepSeek Harness 插件。

<a id="c31-s20"></a>

### 魔改 Web UI

[dsh-web-ui](<https://github.com/zhu1090093659/dsh-web-ui>)：提供任务看板、Git 图、右侧面板、远程手机 UI、Token 统计，甚至还有宠物和皮肤中心，整挺花🤣

![正文配图](<../../assets/manuscript-20260914/c29-2eccfd67e8e506.webp>)

<a id="c31-s21"></a>

### 给纯文本 Agent 补视觉

[modlens](<https://github.com/liustack/modlens>)：可以把截图转成 OCR、布局和语义等结构化证据，可以拿来做图片问答、前端 UI 还原和 GUI 自动化。

<a id="c31-s22"></a>

### 替换交互层

[dsh-TUI](<https://github.com/ccch1mneyyy/dsh-TUI>)：目标是做 Claude Code 风格的全屏终端。

[DSH-better-sidebar](<https://github.com/omdsh-dev/DSH-better-sidebar>)：把文件、终端、Git 和子代理集中到侧边栏工作台。

<a id="c31-s23"></a>

#### 生成复杂 3D 交互应用，并用 Trajectory 追踪全过程

[<span>@</span>stevibe](<https://x.com/stevibe/status/2087903879845515676>) 用 Harness 生成了一个 3D 魔方：27 分钟、52 个步骤。还特别强调，可以在 Trajectory 页面逐条检查 assistant 和工具调用。

![正文配图](<../../assets/manuscript-20260914/c29-b94a339a40636c.webp>)

这个案例说明，Harness 不只是改几行代码的工具。需要较长执行链、又想保留全程证据的复杂任务，才是它的主场。

<a id="c31-s24"></a>

#### 生成高精度工程类 3D 仿真

[<span>@</span>NFT&#95;Chen](<https://x.com/NFT_Chen/status/2087958659838149033>) 展示了一个四冲程柴油机 3D 交互仿真：气缸、活塞、曲轴、配气、燃油、润滑、冷却系统全都有，还能拖拽视角、看相位和实时运行参数。

![正文配图](<../../assets/manuscript-20260914/c29-1fddb246534d0e.webp>)

比起一句"帮我做个网页"，这种带明确结构、物理逻辑和交互要求的任务，更能看出模型、工具调用和长任务调度到底行不行。

<a id="c31-s25"></a>

#### 用插件魔改 UI，把预览面板直接嵌进工作台

[<span>@</span>dotey](<https://x.com/dotey/status/2088059102131794012>) 展示了插件化 UI：左边是 Agent 对话和执行过程，右边直接打开 Explorer、Tasks、网页或 PPT 预览。

![正文配图](<../../assets/manuscript-20260914/c29-0da519f1eefe32.webp>)

这可能是目前最能体现"一切皆插件"的大众化玩法：不动 Agent 的核心任务，只换交互层，就能把 Harness 改造成 PPT 工作台、网页工作台或者代码预览器。

<a id="c31-s26"></a>

#### 把 Harness 做成可学习、可运行的教程和知识产品

[<span>@</span>yanhua1010](<https://x.com/yanhua1010/status/2087918781326848460>) 做了一套"从零实现一个 AI Agent"的 Harness 教程，包含原理、源码拆解、渐进式 Demo 和可运行项目。

![正文配图](<../../assets/manuscript-20260914/c29-32aa21aba79b5e.webp>)

很多人已经不满足于"把它装起来"，更想搞懂插件、Agent Loop、上下文和运行时到底是怎么组合的。

<p></p>

<a id="c31-s27"></a>

## 实测 Case 1：把 Harness 变成"对话 + 文件 + 预览"工作台

先复现 <span>@</span>dotey 那个插件化工作台，就是上面表格里收藏反超点赞的那条，对应插件 DSH-better-sidebar。

安装没有跑任何远程脚本，直接走 DSH 官方插件命令：

```bash
dsh plugin --profile web add dsh-better-sidebar@0.10.3
```

安装器最终退出码 0，`dsh plugin --profile web list --depth 0` 也明确列出了 `dsh-better-sidebar 0.10.3`。重启的时候又踩到那个 Node 版本坑：沙箱外登录 Shell 默认调用 Node.js 22.14.0，而当前 DSH 的持久化模块需要更新的 Zstd API；显式切回本机的 Node.js 22.19.0 之后，DSH 正常监听 `127.0.0.1:39201`。

![正文配图](<../../assets/manuscript-20260914/c29-782c093a2dcd7a.webp>)

重新打开原来的测试会话，右侧已经出现 Explorer，能直接看到工作区里的 `project-notes.md`、`tasks.csv` 和 Harness 生成的 `README.md`。这一步验证的重点是插件 UI 真的加载了，不是"依赖写进了 package.json"就完事。

![正文配图](<../../assets/manuscript-20260914/c29-f89d6137c60e47.webp>)

接着在 Explorer 里点 `README.md`，右侧不用离开会话就出现 Markdown 预览，还能切换编辑和保存。这就是 Harness 的实用点：左边继续让 Agent 干活，右边同时检查文件和成品。插件不是单独的玩具，它在同一个运行时里直接拼成了工作台。

<strong>实测结论：完整跑通。</strong>安装、配置登记、Node 兼容性处理、插件加载、工作区文件浏览和 Markdown 实时预览，六个环节全部验证。

<a id="c31-s28"></a>

## 实测 Case 2：OpenPencil 可编辑设计组合，为什么只能判"部分成功"

先安装项目包：

```bash
dsh plugin --profile web add @zseven-w/dsh-openpencil@0.1.0-rc.1
```

安装器退出码 0，重启后的创造模式也确实拿到了 `openpencil_new` 和 `openpencil_render` 两个工具。我让它创建一个 1200×675 的可编辑 `harness-case-board.op`，并且明确禁止用普通文本或 SVG 冒充。

结果工具真正执行到事务层，返回 `OpenPencil editor host binary is unavailable`🤔

翻了一圈：本机 `/Applications` 里没有 OpenPencil.app，PATH 里也没有对应可执行文件，插件缓存只有 `render-access.key`，没有 editor host binary。创建失败后没有残留 `.op` 文件，后续渲染自然又报 `.op file not found`。

![正文配图](<../../assets/manuscript-20260914/c29-39e7a7f59fa15a.webp>)

<strong>实测结论：部分成功。</strong>插件安装和工具注册没问题，但可编辑文件的创建与渲染没跑通。缺的不是 API Key，而是 OpenPencil 的桌面/编辑器 Host。只装 DSH 插件包，不等于拥有外部桌面运行时。遇到同样的报错，也不要拿 SVG 改后缀伪造成功。

<a id="c31-s29"></a>

## 实测 Case 3：让 Agent 在运行中给自己造一个新工具

我设计了一个 Case：

创造模式必须在当前会话里临时注册一个 `task_csv_summary` 工具，立刻调用它分析 `tasks.csv`，再生成 `tasks-dashboard.md`。

Agent 先用 `cordis_inspect_*` 查询 `harness.defineTool/registerTool`、Host `fs` 服务和工具列表，然后通过 `cordis_define` 创建 `csvsum-1/pkg-1`，再用 `cordis_run` 启动为 `run-1`。`Tool.listTools` 确认 `task_csv_summary` 已经进了当前 Agent 的工具集。

![正文配图](<../../assets/manuscript-20260914/c29-f56acd3cdd3c2d.webp>)

关键一步不是"代码写出来了"，而是下一轮模型步骤真的调用了 `task_csv_summary("tasks.csv")`。工具经 Host `fs` 服务读取 CSV，返回：总任务数 3；P0=2、P1=1；待处理=2、进行中=1；P0 未完成 2 项。整个统计没有用 Bash、Python、Node 脚本或者模型心算代替，就是它自己刚造出来的工具在干活。

然后 Agent 只根据工具返回的 JSON 写出 `tasks-dashboard.md`，侧边栏立刻打开 Markdown 预览。原来的 `tasks.csv`、`README.md`、`project-notes.md` 我逐字节复查过，一个字都没变。

![正文配图](<../../assets/manuscript-20260914/c29-873ba97a9f9341.webp>)

<strong>实测结论：完整跑通，而且这个 Case 最能体现 Harness 的差异。</strong>

同一个会话里跑完"检查运行时 → 创建插件 → 加载插件 → 动态工具进入模型工具集 → 实际调用 → 生成可预览产物"，全程不用重启。看到它把自己刚造的工具用起来的那一刻，我承认有被小小震撼到。这个临时插件重启后会失效，想长期用的话，再打包成正式 DSH 插件就行。

<a id="c31-s30"></a>

## 最后

只想最快打开：

```bash
npx @deepseek-ai/dsh web
```

准备长期用：

```bash
npm install -g @deepseek-ai/dsh
dsh web
```

打不开的时候，先确认真正执行 `dsh` 的 Node.js 满不满足 `^22.19.0 || >=24.0.0`，我这次前后两个坑全都是它。

打开之后：添加 API Key、选一个测试工作区、用标准模式跑一个能读文件并生成 README 的最小任务。五分钟，就能验证它在你机器上到底行不行。

从一条命令装好，到插件工作台，再到 Agent 在运行中给自己造工具，DeepSeek Harness 并不是“DeepSeek 版 Codex”：它把模型、工具、UI 全部拆成了可替换的插件。<strong>它不是一个定死的产品，你可以按自己的工作流，把它重新拼装成一套属于你的 Agent 底座。</strong>

<p></p>

<p></p>
