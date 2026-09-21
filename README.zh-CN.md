<p align="right"><a href="README.md">English</a> · 简体中文</p>

<p align="center">
  <img src="assets/home/book-hero.webp" width="360" alt="魔搭紫皮书：开源模型应用实战封面">
</p>

<h1 align="center">ModelScope Cookbook · 魔搭紫皮书</h1>
<p align="center"><strong>让开源模型，从知识走向实践。</strong></p>
<p align="center">选得对 · 跑得起 · 调得好 · 用得上</p>

<p align="center">
  <a href="https://modelscope.cn/studios/ms-cookbook-team/ms-cookbook"><img src="https://img.shields.io/badge/在线阅读-ModelScope-7043DB?style=flat-square" alt="在魔搭创空间在线阅读"></a>
  <a href="https://github.com/modelscope/ms-cookbook/stargazers"><img src="https://img.shields.io/github/stars/modelscope/ms-cookbook?style=flat-square&amp;color=7043DB" alt="GitHub stars"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-7043DB?style=flat-square" alt="许可证：Apache 2.0"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/参与共建-Welcome-287D70?style=flat-square" alt="欢迎参与共建"></a>
</p>

<p align="center">
  <a href="#项目介绍">项目介绍</a> ·
  <a href="#开始阅读">开始阅读</a> ·
  <a href="#学习路线">学习路线</a> ·
  <a href="#内容导航">内容导航</a> ·
  <a href="#读者社区">读者社区</a> ·
  <a href="#参与共建">参与共建</a>
</p>

---

## 项目介绍

**魔搭紫皮书是一个面向开发者的开源模型应用实战项目，围绕真实任务，系统介绍模型选型、推理运行、数据准备、微调评测与应用开发。**

从“模型可以下载”到“模型真正用起来”，中间还有一系列具体问题：业务需求该选哪类模型？现有硬件能跑多大规模？如何用自己的数据微调？效果提升该怎样验证？本书结合 **EvalScope、ms-swift、DiffSynth、Ollama** 等工具，以及 RAG 与 Agent 工作流，把这些选择与动手操作衔接起来。

项目希望帮助读者建立**从任务定义到效果验证的实践能力**：先跑通一个结果，再理解运行条件与方法边界，逐步构建能够复现、评测和改进的应用。书中案例覆盖企业知识问答、语音助手、客服质检、AI 健身教练、商品营销图和产线巡检等场景。

> **8 篇主题 · 35 个章节 · 34 章可读**

## 开始阅读

**[在魔搭创空间在线阅读 →](https://modelscope.cn/studios/ms-cookbook-team/ms-cookbook)**

打开即可阅读，无需安装。网站提供全文关键词搜索、阅读路径、章节导航、代码复制、图片放大与数学公式渲染，支持桌面和手机访问。

如需本地阅读：

```bash
git clone https://github.com/modelscope/ms-cookbook.git
cd ms-cookbook
python3 -m http.server 4173 --bind 127.0.0.1
```

打开 [http://127.0.0.1:4173/#home](http://127.0.0.1:4173/#home)。端口被占用时，将命令和地址中的端口一并改为 `4174`。按 `Ctrl+C` 停止服务。

本地阅读只需 Python 3 与现代浏览器，无需安装项目依赖、执行构建、配置 API 密钥或使用 GPU。各章实践所需的软件、模型文件、访问凭据和算力条件，以章节说明为准。

## 学习路线

| 你的目标 | 推荐章节 | 实践收获 |
| --- | --- | --- |
| **从零开始** | [01](content/chapters/chapter-01.md) → [05](content/chapters/chapter-05.md) → [07](content/chapters/chapter-07.md) | 理解模型、定义任务，完成第一次推理 |
| **深入模型** | [12](content/chapters/chapter-12.md) → [13](content/chapters/chapter-13.md) → [15](content/chapters/chapter-15.md) | 准备训练数据、开展轻量微调，用评测检验效果 |
| **走向应用** | [19](content/chapters/chapter-19.md) → [27](content/chapters/chapter-27.md) → [28](content/chapters/chapter-28.md) | 连接知识库、外部工具与可复用 Skill |
| **AIGC 创作** | [21](content/chapters/chapter-21.md) → [22](content/chapters/chapter-22.md) → [23](content/chapters/chapter-23.md) → [25](content/chapters/chapter-25.md) | 从案例出发，学习图像 LoRA、商品图创作与理论基础 |

### 适合谁学？怎么学？

- **开发者与在校学生：** 希望通过可操作的示例，建立开源模型应用的基础认知。
- **应用工程师：** 正在处理模型选型、资源配置、数据微调与效果评测问题。
- **AIGC 实践者：** 希望探索图像定制、生成与编辑工作流。

代码实践建议具备基础 Python 与命令行知识。可以按路线循序学习，也可以从当前任务对应的案例入手：先检查环境要求，再复现示例，然后替换为自己的输入，记录结果与局限。

## 内容导航

点击章节在 GitHub 阅读，或前往[在线阅读网站](https://modelscope.cn/studios/ms-cookbook-team/ms-cookbook)。

| 章节 | 关键内容 |
| --- | --- |
| **第一篇　认识开源模型** | |
| [01 · 开源模型正在改变什么](content/chapters/chapter-01.md) | 开放程度、能力边界与许可证 |
| [02 · 开源模型还没用上，先卡在下载这一步？](content/chapters/chapter-02.md) | 模型库检索、模型卡与下载方式 |
| [03 · 数据，是你要做开源模型微调的基石](content/chapters/chapter-03.md) | 数据来源、质量与微调准备 |
| [04 · 没有资源也能玩开源模型，因为这里资源免费](content/chapters/chapter-04.md) | 模型与算力资源入口 |
| **第二篇　从问题出发：找到适合场景的开源模型** | |
| [05 · 要把业务问题转换成模型任务问题](content/chapters/chapter-05.md) | 任务定义、输入输出与评估标准 |
| [06 · 先评再选：用 EvalScope 形成开源模型的第一份报告](content/chapters/chapter-06.md) | 使用 EvalScope 建立选型基线 |
| **第三篇　跑得起：让第一个开源模型工作起来** | |
| [07 · 30 分钟带你快速看到第一个结果](content/chapters/chapter-07.md) | 完成首次模型推理 |
| [08 · 多大模型，选择什么样的服务器配置](content/chapters/chapter-08.md) | 参数规模、显存与服务器选型 |
| [09 · 笔记本也能跑开源模型，先从 Ollama 开始](content/chapters/chapter-09.md) | 使用 Ollama 开展本地推理 |
| [10 · 把模型放到云端跑，用 Notebook 试试 CPU 和 GPU](content/chapters/chapter-10.md) | 在云端 Notebook 中运行模型 |
| [11 · 模型需要资源太多，量化能帮上什么忙？](content/chapters/chapter-11.md) | 量化精度与资源开销 |
| **第四篇　调得好：把通用模型变成场景模型** | |
| [12 · 业务素材这么多，怎么变成能训练的数据？](content/chapters/chapter-12.md) | 从业务资料整理训练样本 |
| [13 · 快速用 ms-swift，完成开源模型的轻量微调](content/chapters/chapter-13.md) | 使用 ms-swift 开展轻量微调 |
| [14 · 模型已经会回答了，为什么还要做偏好对齐？](content/chapters/chapter-14.md) | 理解偏好对齐的目标与方法 |
| [15 · 微调有没有用，测才知道？](content/chapters/chapter-15.md) | 对比微调前后的模型效果 |
| **第五篇　场景篇：从模型走向完整业务系统** | |
| [16 · AI 健身教练：跟着视频练，让 AI 指出动作不标准的地方](content/chapters/chapter-16.md) | 人体关键点与动作对比 |
| [17 · 智能客服质检：AI 能从一通客服电话中分析出什么？](content/chapters/chapter-17.md) | 通话转写与服务质量分析 |
| [18 · 搭建一个能听也能说的语音助手](content/chapters/chapter-18.md) | 串联语音识别、问答与合成 |
| [19 · 实现一个企业知识问答助手](content/chapters/chapter-19.md) | 知识库检索与 RAG 问答 |
| [20 · 场景有千千万，欢迎你来共建出你的场景](content/chapters/chapter-20.md) | 可复现业务场景的共建邀请 |
| **第六篇　AIGC 特別篇** | |
| [21 · 10 个 Case，带你看看 AIGC 的开源模型能做到什么地步](content/chapters/chapter-21.md) | 开源生成模型的应用案例 |
| [22 · 定制？使用 DiffSynth 训练图像 LoRA](content/chapters/chapter-22.md) | 使用 DiffSynth 定制图像 LoRA |
| [23 · 一张商品营销图，从生成到修改怎么做？](content/chapters/chapter-23.md) | 商品图生成与编辑 |
| [24 · 开源模型也能做出像样的 AI 视频吗？](content/chapters/chapter-24.md) | MiniMax H3 部署教程待更新 |
| [25 · 补充：AIGC 理论知识](content/chapters/chapter-25.md) | 图像与视频生成基础 |
| **第七篇　Agent 特别篇** | |
| [26 · Agent 是什么，它能做什么事？](content/chapters/chapter-26.md) | Agent 的组成、执行流程与适用场景 |
| [27 · MCP：让模型连接外部工具](content/chapters/chapter-27.md) | 连接模型与外部工具 |
| [28 · Skill：把任务方法封装成能力](content/chapters/chapter-28.md) | 组织可复用的任务方法 |
| [29 · 快速使用 Claude Code](content/chapters/chapter-29.md) | Claude Code 入门 |
| [30 · 快速使用 PI](content/chapters/chapter-30.md) | PI 入门 |
| [31 · 快速使用 DeepSeek Harness](content/chapters/chapter-31.md) | DeepSeek Harness 入门 |
| [32 · 补充：Agent 框架知识](content/chapters/chapter-32.md) | Agent 框架基础 |
| [33 · 产线巡检 Agent：用 Penguin Harness 快速开发与优化](content/chapters/chapter-33.md) | 用 Penguin Harness 开发产线巡检 Agent，并通过评测优化 |
| **第八篇 补充内容** | |
| [34 · 补充：大模型基础知识](content/chapters/chapter-34.md) | 模型结构、训练、推理与局限 |
| [35 · 主流 LLM 评测](content/chapters/chapter-35.md) | 主流模型评测的共建邀请 |

## 场景实践

| 应用案例 | 探索的实现流程 | 章节 |
| --- | --- | --- |
| AI 健身教练 | 识别人体关键点，对比跟练动作与示范 | [16](content/chapters/chapter-16.md) |
| 智能客服质检 | 从通话录音到文字转写与服务分析 | [17](content/chapters/chapter-17.md) |
| 语音助手 | 串联语音识别、模型问答与语音合成 | [18](content/chapters/chapter-18.md) |
| 企业知识问答 | 检索知识库，为回答提供参考依据 | [19](content/chapters/chapter-19.md) |
| 商品营销图 | 完成商品图像生成与编辑 | [23](content/chapters/chapter-23.md) |
| 产线巡检 | 用 Penguin Harness 开发产线巡检 Agent，并通过评测优化 | [33](content/chapters/chapter-33.md) |

## 读者社区

<p align="center">
  <img src="assets/dada/dada.webp" width="88" alt="搭搭社区形象">
</p>

欢迎交流学习问题、分享复现记录，也欢迎把实践经验带回项目。

<table>
  <tr>
    <td align="center"><img src="assets/community/qr.png" width="200" alt="魔搭紫皮书社区二维码"><br><strong>魔搭紫皮书社区</strong></td>
    <td align="center"><img src="assets/community/agentwork-qr.png" width="200" alt="AgentWork 社区二维码"><br><strong>AgentWork 社区</strong></td>
  </tr>
</table>

使用微信扫码，或保存图片后从相册识别。如二维码失效，欢迎通过 [Issue](https://github.com/modelscope/ms-cookbook/issues/new) 反馈。

## 参与共建

你可以选择两种方式分享成果：

- **GitHub：** 在 [Issues](https://github.com/modelscope/ms-cookbook/issues) 中反馈问题，或提交范围清晰的 [Pull Request](https://github.com/modelscope/ms-cookbook/pulls)。请注明相关章节或页面、参考依据及验证步骤。
- **魔搭：** 前往[开发者实践](https://modelscope.cn/spotlight)，选择 **创建内容**，添加专题 **#魔搭紫皮书** 后投稿。

欢迎贡献技术勘误、可复现应用案例、AIGC 工作流与阅读体验改进。界面调整应保留文章内容与结构，正文修订需提供明确来源或作者确认。请勿提交访问凭据、个人隐私数据或未经授权的材料。

完整流程见 [CONTRIBUTING.md](CONTRIBUTING.md)。

### 致谢

感谢 [freestylefly](https://github.com/freestylefly)、[yingdachen](https://github.com/yingdachen)、[liucongg](https://github.com/liucongg)，以及每一位帮助项目改进的共建者。[查看全部贡献记录 →](https://github.com/modelscope/ms-cookbook/graphs/contributors)

感谢 [Datawhale Hello-Agents](https://github.com/datawhalechina/hello-agents) 提供 README 组织参考。

## 维护说明

<details>
<summary><strong>章节源文件、校验与仓库结构</strong></summary>

### 内容维护位置

- `content/chapters/`：供 GitHub 阅读的 Markdown 章节，构建时自动生成。
- `content/source-html/`：保留原稿结构的 HTML 构建源文件，正文修改在此完成。
- `content/manifest.json`：篇章标题、顺序、状态与快照日期。
- `content/sync-report.json`：导入时的原稿版本与校验证据。
- `assets/content.js`：网站加载的生成数据。
- `index.html`、`assets/paper.js` 与站点样式文件：阅读界面。
- `assets/dada/`、`assets/community/`：插画与社区二维码。
- `assets/manuscript-20260914/`：本地正文图片与附件。

完成已确认的正文修订后：

```bash
python3 scripts/build-content.py
node scripts/build-content.mjs --check
node scripts/check-site.mjs
```

构建使用 Python 3，校验还需要 Node.js 22 或更新版本。请同时提交源文件与生成数据，并预览受影响的桌面和手机页面。直接阅读现有站点无需执行这些步骤。

</details>

<details>
<summary><strong>GitHub → 魔搭创空间自动发布</strong></summary>

[部署工作流](.github/workflows/deploy-modelscope.yml)会将 `main` 分支中的站点文件更新发布到公开创空间 `ms-cookbook-team/ms-cookbook`，也支持在 GitHub Actions 手动触发。

工作流使用仓库 Secret `MODELSCOPE_API_KEY`，将已提交的文件同步到创空间的 `master` 分支，生成中文创空间卡片并触发部署。只有线上页面与部署提交校验通过，任务才会成功。代码与正文统一在 GitHub 维护。

</details>

## 开源协议

本仓库采用 [Apache License 2.0](LICENSE)。书中引用的模型、数据集与工具适用各自的许可证及使用条款；正文图片和附件的权利归原作者或相应权利人所有。

第三方组件保留各自许可证：[KaTeX · MIT](assets/katex/LICENSE)、[Remix Icon · Apache 2.0](assets/home/REMIX-LICENSE)、[Noto Serif SC · SIL OFL 1.1](assets/home/NOTO-LICENSE.txt)、[搭搭 · MIT](assets/dada/LICENSE)。详见[搭搭来源声明](assets/dada/NOTICE.md)、[网站素材说明](assets/paper/ATTRIBUTION.txt)、[共用素材说明](assets/home/ATTRIBUTION.txt)与[插画说明](assets/review/ATTRIBUTION.md)。
