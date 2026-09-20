<!-- Generated from ../source-html/chapter-33.html; do not edit independently. -->

# 用 Penguin Harness 快速开发并优化产线巡检 Agent 应用

<a id="c33-s1"></a>

## 1\. 背景

当前，制造业正持续推进自动化与智能化转型，生产现场对设备运行管理和异常响应效率也提出了更高要求。让 Agent 技术更深入地参与日常巡检与异常处理，成为提升生产运维效率的一个重要方向。

在生产运维中，产线的稳定运行离不开日常巡检和异常处理。现场人员需要结合设备状态与生产信息判断问题，并协调后续处置。例如，部分产线在供电恢复后仍需人工重启，响应不及时就会延长停机时间，影响生产。如何减轻重复工作、提高异常响应效率，是产线运维中的一个实际需求。

目前，Agent 为这类工作提供了一种新的实现方式：将业务知识、信息分析和工具调用结合起来，协助完成从发现问题到执行处理的工作流程。在这类场景中，Agent 可以结合运行资料和设备当前状态分析停机原因（例如停电），并在确认具备运行条件后调用工具恢复产线。下面以供电恢复后输送带仍未运行的情况为例，对比人工与 Agent 的处理流程：

![图 1：来电后输送带未恢复，人工与 Agent 的处理流程示意。](<../../assets/penguin-harness/figure-01.png>)

<em>图 1：来电后输送带未恢复，人工与 Agent 的处理流程示意。</em>

不过，开发这样的 Agent 仍需要完成应用开发和效果验证，并在运行后持续优化。Penguin Harness 是一个用于自动化开发和优化 Agent 的框架，可以大大减少这些工作所需的人工投入。使用者提供业务需求、示例、规范和相关接口，Penguin Harness 据此开发 Agent 及配套网页应用，并结合评测反馈持续改进 Agent 的任务表现。具体流程如下图所示：

![图 2：Penguin Harness 开发与优化产线巡检 Agent。](<../../assets/penguin-harness/figure-02.png>)

<em>图 2：Penguin Harness 开发与优化产线巡检 Agent。</em>

本文以产线巡检为例，展示如何使用 Penguin Harness 开发和优化 Agent 应用。在本例中，Agent 负责分析设备异常和调用设备工具，配套网页供用户上传资料、发起任务和查看结果。

<a id="c33-s2"></a>

## 2\. Penguin Harness 的基础使用

在开始开发之前，我们需要先安装 Penguin Harness 客户端、接入模型，并完成一次简单交互。下面以桌面客户端和 DeepSeek Flash 为例，介绍后文会用到的基础操作。

<a id="c33-s3"></a>

### 2.1 下载并打开客户端

打开 [Penguin Harness 客户端下载页面](<https://penguin.ooo/download>)，选择与自己电脑系统对应的安装包，下载后按提示安装。

![图 3：客户端下载页：按操作系统选择安装包。](<../../assets/penguin-harness/figure-03.png>)

<em>图 3：客户端下载页：按操作系统选择安装包。</em>

安装完成后，打开客户端。在主界面左侧点击“模型库”，即可配置接下来要使用的模型。

![图 4：Penguin Harness 主界面，左侧为“模型库”入口。](<../../assets/penguin-harness/figure-04.png>)

<em>图 4：Penguin Harness 主界面，左侧为“模型库”入口。</em>

<a id="c33-s4"></a>

### 2.2 接入模型 API

Penguin Harness 通过模型 API 完成分析和任务执行。使用 DeepSeek 时，先在 [DeepSeek 开放平台](<https://platform.deepseek.com/>)创建 API Key，再将它填入客户端。API Key 用于验证模型调用身份。

在“模型库”中展开 DeepSeek 分组，打开 DeepSeek Flash 的模型配置，填入自己的 API Key，点击“确认”保存。通过官方服务接入时，API 地址为 [[https://api.deepseek.com](<https://api.deepseek.com>)](<https://api.deepseek.com>)，模型 ID 为 deepseek-flash。下图标出了对应位置。

![图 5：DeepSeek Flash 模型配置：填写 API Key、API 地址和模型 ID。密钥已遮挡。](<../../assets/penguin-harness/figure-05.png>)

<em>图 5：DeepSeek Flash 模型配置：填写 API Key、API 地址和模型 ID。密钥已遮挡。</em>

<a id="c33-s5"></a>

### 2.3 选择 DeepSeek 模型

保存后，DeepSeek Flash 会显示在模型库中。下图中的“默认”标签表示它已设为默认模型；也可以在每次任务开始前单独选择模型。

![图 6：模型库中的 DeepSeek Flash；“默认”标签表示当前默认模型。](<../../assets/penguin-harness/figure-06.png>)

<em>图 6：模型库中的 DeepSeek Flash；“默认”标签表示当前默认模型。</em>

点击左侧“新建对话”，在输入框右下方打开模型列表，选择 DeepSeek Flash。列表中的勾选标记表示本次任务将使用该模型。

![图 7：在输入框右下方选择本次任务使用的模型。](<../../assets/penguin-harness/figure-07.png>)

<em>图 7：在输入框右下方选择本次任务使用的模型。</em>

<a id="c33-s6"></a>

### 2.4 开始一次任务

为了跟着本文从零开发，可以先将 [line-recovery-starter 仓库](<https://github.com/rank-Yu/line-recovery-starter>)克隆到本地。仓库只提供业务需求、数据契约、示例数据包和模拟设备服务。在已安装 Git 的电脑上，打开终端，运行：

```text
git clone https://github.com/rank-Yu/line-recovery-starter.git
```

命令完成后，当前目录下会生成 line-recovery-starter 文件夹。回到 Penguin Harness，点击输入框下方的工作区入口，选择这个文件夹，再点击“使用此目录”。后续任务就可以读取其中的项目材料。

![图 8：选择项目文件夹后，点击“使用此目录”。](<../../assets/penguin-harness/figure-08.png>)

<em>图 8：选择项目文件夹后，点击“使用此目录”。</em>

输入框下方的“技能”菜单列出了当前可用的技能，它们为特定任务提供操作说明。可以先熟悉这个入口，开发或评测时再选择相应技能；本次读取项目的简单任务无需额外选择。

![图 9：输入框下方的“技能”菜单，列出当前可用技能。](<../../assets/penguin-harness/figure-09.png>)

<em>图 9：输入框下方的“技能”菜单，列出当前可用技能。</em>

准备好后，在会话输入框中发送一条简单指令，让 Penguin Harness 先了解工作区：

>
> 请查看当前工作区的 README.md，简要介绍项目用途，以及 contracts、examples、interfaces 三个目录的作用，控制在 150 字以内。只读取文件，不修改或运行项目。

![图 10：选定工作区并输入指令后，点击右侧箭头发送。](<../../assets/penguin-harness/figure-10.png>)

<em>图 10：选定工作区并输入指令后，点击右侧箭头发送。</em>

发送后，可以在对话中查看回复，并展开工具调用记录，了解它读取了哪些文件。得到与工作区内容相符的介绍后，就完成了首次交互。

![图 11：任务完成后的项目介绍与文件读取记录。](<../../assets/penguin-harness/figure-11.png>)

<em>图 11：任务完成后的项目介绍与文件读取记录。</em>

接下来，我们以产线巡检为例，准备业务材料，并让 Penguin Harness 开发 Agent 及配套网页应用。

<a id="c33-s7"></a>

## 3\. 从零开发产线巡检 Agent 应用

<a id="c33-s8"></a>

### 3.1 准备业务规范文件与输入示例

第二章已经将 [line-recovery-starter 仓库](<https://github.com/rank-Yu/line-recovery-starter>)克隆到本地。这个仓库保留了原项目的业务规范文件、输入示例、数据契约和两个模拟设备 MCP 服务，尚未包含生成后的 Agent 应用。本章从这份材料出发，介绍开发、启动和结果核查步骤。

先看仓库根目录的 [README.md](<https://github.com/rank-Yu/line-recovery-starter/blob/main/README.md>)。它是交给 Penguin Harness 的需求文档，下面概括业务场景和交付要求，完整内容以仓库原文为准：

```text
目标：制作中文产线恢复助手，支持上传 ZIP 或加载示例。

业务场景：
1. 来电后输送带仍未运行：核对供电、驱动与运行许可，
   满足条件后请求恢复，再检查带速和新的出口计数。
2. 温度升高导致输送暂停：请求开启散热并观察温度，
   温度达标且重新获得运行许可后，再请求恢复输送。

处理要求：结合运行记录、日志、状态和图片判断；
先查询工具当前状态，再决定操作，最后核查新反馈。
条件不足或反馈未确认时，如实说明并转人工。

交付内容：在 app/ 生成 Agent、后端、中文前端和启动说明，
接入已有的两个 MCP 服务，展示证据、动作记录和结果。
工具未连接时明确提示，不伪造动作成功。
```

业务说明之外，Penguin Harness 还需要知道应用将收到哪些资料，以及应该输出什么格式。仓库中的材料分别承担以下作用：

<table>
<thead>
<tr>
<th>工作区材料</th>
<th>开发时的用途</th>
</tr>
</thead>
<tbody>
<tr>
<td>README.md</td>
<td>业务需求、材料阅读顺序和应用交付要求</td>
</tr>
<tr>
<td>examples/input/</td>
<td>示例数据包，包括运行记录、事件日志、状态快照、工位图片与操作说明</td>
</tr>
<tr>
<td>contracts/</td>
<td>输入、设备状态、操作和报告的格式规范</td>
</tr>
<tr>
<td>interfaces/</td>
<td>输送恢复与散热控制 MCP 服务，以及初始化和接入说明</td>
</tr>
</tbody>
</table>

打开 [examples/input/](<https://github.com/rank-Yu/line-recovery-starter/tree/main/examples/input>)，可以看到这份示例数据包，主要文件如下：

```text
examples/input/
├── request.json          # 本次要解决的问题
├── telemetry.csv         # 电压、带速、温度和产出记录
├── events.jsonl          # 设备事件日志
├── device_state.json     # 采集时的设备状态
├── images/frame_001.png  # 工位图片
├── operating_guide.md    # 设备操作说明
└── ...
```

例如，events.jsonl 记录了设备状态变化。下面摘取两条记录，只展示时间和消息内容，其余字段与记录省略：

```text
{
  "timestamp": "2026-09-15T09:00:40+08:00",
  "message": "上游24 V电源有效反馈由1变0，驱动支路电压降至0 V；独立供电的控制器保持在线。"
}
...
{
  "timestamp": "2026-09-15T09:01:12+08:00",
  "message": "驱动重新就绪；配置禁止来电自动启动，等待新的获准运行请求。"
}
```

这些日志会和运行数据、工位图片一起交给 Agent，供它分析停机原因和恢复条件。

接下来，先看看仓库中的两个 MCP 服务分别提供哪些设备工具。

<a id="c33-s9"></a>

### 3.2 了解两个 MCP 服务

Agent 分析出停机原因后，还需要查询设备当前的状态，并执行相应操作。仓库的 interfaces/ 目录已经提供了两个 MCP 服务，Penguin Harness 开发应用时会接入它们，无需从头编写设备接口。

<table>
<thead>
<tr>
<th>MCP 服务</th>
<th>用途</th>
</tr>
</thead>
<tbody>
<tr>
<td>power-control</td>
<td>查询供电和输送带状态，在条件满足时启动输送带。</td>
</tr>
<tr>
<td>cooling-control</td>
<td>查询温度和风机状态，开启风机散热。</td>
</tr>
</tbody>
</table>

例如，供电恢复后输送带仍未运行，Agent 会先通过 power-control 检查设备状态，满足条件后请求启动，再查看带速和产出是否恢复。如果是温度过高导致停机，则先通过 cooling-control 开启风机，等温度降下来，再检查能否启动输送带。

两个服务都在本地模拟环境中运行，不连接真实产线设备。后文演示中的启动、降温和产出变化，都来自这个模拟环境。

这一节先了解两个服务的分工和使用顺序。具体的启动方式与接入配置，可以查看 [interfaces/README.md](<https://github.com/rank-Yu/line-recovery-starter/blob/main/interfaces/README.md>)。

<a id="c33-s10"></a>

### 3.3 开发并启动 Agent 应用

回到 Penguin Harness，新建对话，确认工作区选中 line-recovery-starter。

![图 12：选择 line-recovery-starter 目录作为开发工作区。](<../../assets/penguin-harness/figure-12.png>)

<em>图 12：选择 line-recovery-starter 目录作为开发工作区。</em>

打开输入框下方的“技能”菜单，选择 agent-initialization 技能。

![图 13：在技能菜单中选择 agent-initialization。](<../../assets/penguin-harness/figure-13.png>)

<em>图 13：在技能菜单中选择 agent-initialization。</em>

接着，将 README 中的开发指令发送给 Penguin Harness，让它根据仓库中的已有材料开发产线巡检 Agent 与配套网页。

>
> 请使用 agent-initialization，先读 README.md，再看 contracts/、interfaces/ 和 examples/input/，在 app/ 制作产线恢复助手，包括 Agent、后端、中文前端和启动说明。按现有契约实现两个 MCP 的客户端；服务未交付时明确显示未连接，不伪造动作成功。用 example 联调输入读取和页面，保留初始版本，本轮不扩充数据、不做优化或正式评分。

![图 14：确认工作区、技能和模型后，发送完整开发指令。](<../../assets/penguin-harness/figure-14.png>)

<em>图 14：确认工作区、技能和模型后，发送完整开发指令。</em>

收到指令后，Penguin Harness 开始读取材料，开发产线巡检 Agent 和配套网页。展开运行记录，可以查看具体的运行记录。

![图 15：Penguin Harness 开发过程中读取项目资料。](<../../assets/penguin-harness/figure-15.png>)

<em>图 15：Penguin Harness 开发过程中读取项目资料。</em>

开发用时约 20 分钟，完成后给出了以下交付说明：

![图 16：原项目的初始交付说明：应用框架先交付，设备接口随后继续接通。](<../../assets/penguin-harness/figure-16.png>)

<em>图 16：原项目的初始交付说明：应用框架先交付，设备接口随后继续接通。</em>

本例已完成的应用保存在 [line-recovery 仓库的 app/ 目录](<https://github.com/lzh368/line-recovery/tree/1e1f1e33d2ea55feafa89ae22895623179f68cfd/app>)中，主要文件结构如下：

```text
app/
├── agent/                 # Agent 的角色说明与技能
│   ├── persona.md
│   └── skills/
├── src/                   # 后端、案例分析与工具调用
├── public/                # 配套网页
├── config/
│   └── interfaces.json    # 两个 MCP 服务的连接配置
├── package.json           # 项目依赖与启动命令
└── README.md              # 安装、配置与启动说明
```

<a id="c33-s11"></a>

### 3.4 演示 Penguin Harness 开发的 Agent 应用

Penguin Harness 每次开发出的应用，页面和文件结构可能有所不同。下面使用我们已经开发好的产线恢复助手进行演示。

准备好 Node.js 和 Python ，将 [line-recovery 仓库](<https://github.com/lzh368/line-recovery>)克隆到本地，切换到本文演示的版本，再安装并初始化应用：

```text
git clone https://github.com/lzh368/line-recovery.git
cd line-recovery
git checkout 1e1f1e33d2ea55feafa89ae22895623179f68cfd
python3 interfaces/manage.py init --profile power-return
cd app
npm install
npm run setup
cp -n .env.example .env
```

在 app/.env 中填入 DEEPSEEK&#95;API&#95;KEY，随后在当前 app/ 目录启动应用：

```text
npm start
```

在浏览器打开终端显示的本地地址，即可进入产线恢复助手。详细配置见 [app/README.md](<https://github.com/lzh368/line-recovery/tree/1e1f1e33d2ea55feafa89ae22895623179f68cfd/app/README.md>)。下图为创空间演示版尚未载入资料时的初始界面。

![图 17：产线恢复助手初始界面。](<../../assets/penguin-harness/figure-17.png>)

<em>图 17：产线恢复助手初始界面。</em>

下面我们以 lr&#95;101 产线资料包为例，演示供电恢复后输送带仍未运行时的分析和恢复过程。所有设备操作都在模拟环境中进行。

打开应用后，左侧是案例列表和“上传资料包”入口，右侧展示当前案例。下图是已载入示例数据包的首页，红框标出了资料上传入口。

![图 18：产线恢复助手首页，红框为资料上传入口。](<../../assets/penguin-harness/figure-18.png>)

<em>图 18：产线恢复助手首页，红框为资料上传入口。</em>

本次使用[产线巡检示例数据包（lr&#95;101）](<https://github.com/lzh368/line-recovery/tree/1e1f1e33d2ea55feafa89ae22895623179f68cfd/data/dataset/optimization/lr_101>)，包含模拟工位的图片、运行记录和日志。下面的截图与结果来自已开发完成应用对该案例的一次运行；另外，line-recovery-starter 仓库自带的示例数据包对应的也是 lr&#95;001 数据包。

点击“载入 example”，即可加载 lr&#95;101 示例资料。也可以下载 [lr&#95;101.zip](<https://github.com/lzh368/line-recovery/raw/refs/heads/main/docs/penguin-harness/attachments/lr_101.zip>)，在左侧选择文件，点击“上传并解析”，再从案例列表中选中它。

加载后，点击右侧“工位图片”页签，查看工位和纸箱的分布。

![图 19：查看案例中的工位图片。](<../../assets/penguin-harness/figure-19.png>)

<em>图 19：查看案例中的工位图片。</em>

接着切换到“时序数据”页签，查看供电和带速的变化。如下图所示，供电已经恢复，但带速仍为零，产出计数也没有增加。

![图 20：供电已经恢复，但带速仍为零。](<../../assets/penguin-harness/figure-20.png>)

<em>图 20：供电已经恢复，但带速仍为零。</em>

切换到“诊断与证据”页签，点击“开始诊断”；已有报告时，按钮显示为“重新诊断”。完成后，页面会展示 Agent 的分析结论和对应证据。

![图 21：Agent 的停机分析与对应证据。](<../../assets/penguin-harness/figure-21.png>)

<em>图 21：Agent 的停机分析与对应证据。</em>

从上图中可以看到，Agent 判断输送带因供电中断而停机。虽然供电已经恢复、驱动已经就绪，但设备没有收到新的运行请求，因此仍未启动。本次停机与温度无关，无需开启风机。

诊断结束后，切换到“动作与反馈”页签，可以查看 Agent 的操作记录：通过 MCP 查询当前设备状态，确认可以启动后恢复输送，再读取带速和产出反馈。

![图 22：恢复输送后，带速和产出计数发生变化。](<../../assets/penguin-harness/figure-22.png>)

<em>图 22：恢复输送后，带速和产出计数发生变化。</em>

上图中的执行反馈显示，带速恢复到 0.397 m/s，出口累计计数从 1813 增至 1816，说明模拟输送带已经重新运行，并有新的纸箱通过。应用将这些结果和分析结论一起记录在报告中。

<a id="c33-s12"></a>

## 4\. 用 Penguin Harness 优化产线巡检 Agent

上一章演示了一个案例的处理过程。接下来，我们让 Penguin Harness 用更多案例评测原版应用，根据发现的问题进行优化。下图展示了从原版应用到优化后应用的过程：

![图 23：Penguin Harness 评测与优化 Agent 应用。](<../../assets/penguin-harness/figure-23.png>)

<em>图 23：Penguin Harness 评测与优化 Agent 应用。</em>

<a id="c33-s13"></a>

### 4.1 准备并发起评测与优化任务

在 Penguin Harness 中新建对话，选择上一节已克隆到本地的 [line-recovery 仓库](<https://github.com/lzh368/line-recovery/tree/1e1f1e33d2ea55feafa89ae22895623179f68cfd>)作为工作区，再点击“使用此目录”，如下图所示。

![图 24：选择 line-recovery 根目录，点击“使用此目录”。](<../../assets/penguin-harness/figure-24.png>)

<em>图 24：选择 line-recovery 根目录，点击“使用此目录”。</em>

本次任务使用 [10 份案例](<https://github.com/lzh368/line-recovery/tree/1e1f1e33d2ea55feafa89ae22895623179f68cfd/data/dataset/optimization>)作为训练集，用于指导优化，另外用 [7 份案例](<https://github.com/lzh368/line-recovery/tree/1e1f1e33d2ea55feafa89ae22895623179f68cfd/data/gate-set-7>)作为测试集，检查优化后的表现。

每份案例都准备了参考答案。评测时，对照答案检查 Agent 是否判断正确、操作得当，并取得预期结果，逐项评分后计算平均分。

我们选中 agent-evaluation 和 agent-optimization 技能，如下图所示。前者负责组织评测，后者根据评测结果优化 Agent。

![图 25：选中 agent-evaluation 和 agent-optimization，菜单中两项均显示勾选。](<../../assets/penguin-harness/figure-25.png>)

<em>图 25：选中 agent-evaluation 和 agent-optimization，菜单中两项均显示勾选。</em>

接下来，将下面的指令填入输入框，让 Penguin Harness 评测初版、根据训练集中的问题修改 Agent，再用测试集检查效果。

```text
使用 agent-evaluation 和 agent-optimization，先读 data/dataset/evaluator/README.md 和 data/gate-set-7/README.md。用 example 联调工具与反馈，保存代码和完整 Agent State 为 v1。评测 10 份 optimization 案例和 gate-set-7 七例，封存测试结果。只依据 optimization 结果和 trace 优化一轮；冻结 v2 后复测相同测试，测试材料不用于优化。每例 runs=1，独立设备库和 State，模型、预算及评分规则一致。将版本、报告、工具记录和成绩存入 reports/experiments/ 新目录，不覆盖已有记录，给出前后对比与路径。
```

![图 26：填好优化指令后的待发送状态；红框为发送按钮，本次截图未启动任务。](<../../assets/penguin-harness/figure-26.png>)

<em>图 26：填好优化指令后的待发送状态；红框为发送按钮，本次截图未启动任务。</em>

点击图中红框标出的发送按钮。展开运行记录，可以看到 Penguin Harness 读取评测说明和相关技能，准备评测与优化任务，如下图所示。

![图 27：评测与优化任务启动后的工具调用记录。](<../../assets/penguin-harness/figure-27.png>)

<em>图 27：评测与优化任务启动后的工具调用记录。</em>

任务完成后，Penguin Harness 会给出报告的保存位置。下面结合仓库中已保存的完整实验报告，查看优化结果。

<a id="c33-s14"></a>

### 4.2 查看优化结果

我们在 [line-recovery 仓库](<https://github.com/lzh368/line-recovery/tree/1e1f1e33d2ea55feafa89ae22895623179f68cfd/reports/experiments>)中保存了已完成的评测与优化报告，下面看看优化后的表现。

如下图所示，训练集平均分从 69.23 提高到 100.00，七例测试的历史汇总均分从 86.65 提高到 98.57。

![图 28：优化前后成绩。训练集来自 round1；七例测试来自 gate-set-7，先取每例历史运行均分，再对七例求平均，各案例和版本的运行次数不完全相同。](<../../assets/penguin-harness/figure-28.png>)

<em>图 28：优化前后成绩。训练集来自 round1；七例测试来自 gate-set-7，先取每例历史运行均分，再对七例求平均，各案例和版本的运行次数不完全相同。</em>

从 [line-recovery 仓库中已保存的报告](<https://github.com/lzh368/line-recovery/tree/1e1f1e33d2ea55feafa89ae22895623179f68cfd/reports/experiments>)可以看到，在设备状态不明确的案例中，优化后的 Agent 不再贸然请求操作；在过热停机的案例中，它能在降温后继续恢复输送，并确认产出是否恢复。因此，评测分数提升和具体案例分析两方面都说明，Penguin Harness 优化后的产线巡检 Agent，在异常判断和恢复操作上都有了更好的表现。

<a id="c33-s15"></a>

## 5\. 投入与运行成本

除了任务表现，开发和使用 Agent 的成本也是落地时需要考虑的问题。下面分别介绍开发与优化阶段、日常运行阶段的成本。

<a id="c33-s16"></a>

### 5.1 Agent 开发与优化的成本

在开发阶段，Penguin Harness 可以承担应用生成、工具联调和批量评测等工作，使用者主要负责提供需求与示例，并核查交付结果。以这类应用的开发和一轮优化为例，使用 DeepSeek Flash 的模型调用费用约为 5～20 元。

<table>
<thead>
<tr>
<th>投入项目</th>
<th>人工开发与调试</th>
<th>使用 Penguin Harness</th>
</tr>
</thead>
<tbody>
<tr>
<td>开发与一轮优化</td>
<td>开发、联调和评测的人工费用</td>
<td>使用 DeepSeek Flash，模型调用费用约 <strong>5～20 元</strong></td>
</tr>
<tr>
<td>配套投入</td>
<td>需求梳理、环境配置、测试验收</td>
<td>提供需求与示例、核查结果</td>
</tr>
</tbody>
</table>

<a id="c33-s17"></a>

### 5.2 单次巡检任务的运行成本

Agent 投入使用后，每处理一份案例都会产生相应的模型调用费用。按单次任务累计输入 10 万 Token、输出 1 万 Token 估算，使用 DeepSeek Flash 的模型调用费用约为 0.15～0.30 元。

<table>
<thead>
<tr>
<th>指标</th>
<th>人工处理</th>
<th>Agent 处理</th>
</tr>
</thead>
<tbody>
<tr>
<td>单次直接费用</td>
<td>处理工时 × 人力单价</td>
<td>模型调用费约 <strong>0.15～0.30 元/次（估算）</strong></td>
</tr>
<tr>
<td>其他成本</td>
<td>管理、工具等费用</td>
<td>服务器、维护及人工复核费用</td>
</tr>
</tbody>
</table>

<a id="c33-s18"></a>

## 6\. 总结

本文以产线恢复助手为例，演示了如何用 Penguin Harness 开发 Agent 和配套网页，并通过评测和优化改善 Agent 的实际业务表现。对于其他业务场景，也可以先准备明确的需求、示例数据和工具接口，让 Penguin Harness 完成应用开发，再用实际案例检查效果、逐步改进。

---

可以在魔搭创空间体验本文的两个演示：

- [Penguin Harness 演示](<https://modelscope.cn/studios/rankyu/line-recovery>)：体验用 Penguin Harness 开发 Agent 应用。
- [产线恢复助手演示](<https://modelscope.cn/studios/rankyu/line-recovery-app>)：体验已开发完成的 Agent 应用。

请勿在公用创空间中输入或保存私人 API Key。如需使用自己的 API Key，请先将空间复制到自己的账号下，设置为非公开后再使用。
