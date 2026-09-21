<p align="right">English · <a href="README.zh-CN.md">简体中文</a></p>

<p align="center">
  <img src="assets/home/book-hero.webp" width="360" alt="ModelScope Cookbook — purple book cover">
</p>

<h1 align="center">ModelScope Cookbook</h1>
<p align="center"><strong>From open-source models to practical AI applications.</strong></p>
<p align="center">魔搭紫皮书 · Choose a model. Run it. Adapt it. Build with it.</p>

<p align="center">
  <a href="https://modelscope.cn/studios/ms-cookbook-team/ms-cookbook"><img src="https://img.shields.io/badge/Read_Online-ModelScope-7043DB?style=flat-square" alt="Read online on ModelScope"></a>
  <a href="https://github.com/modelscope/ms-cookbook/stargazers"><img src="https://img.shields.io/github/stars/modelscope/ms-cookbook?style=flat-square&amp;color=7043DB" alt="GitHub stars"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-7043DB?style=flat-square" alt="License: Apache 2.0"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/Contributions-Welcome-287D70?style=flat-square" alt="Contributions welcome"></a>
</p>

<p align="center">
  <a href="#overview">Overview</a> ·
  <a href="#start-reading">Start reading</a> ·
  <a href="#learning-paths">Learning paths</a> ·
  <a href="#book-contents">Chapter guide</a> ·
  <a href="#community">Community</a> ·
  <a href="#contributing">Contribute</a>
</p>

---

## Overview

**ModelScope Cookbook is a hands-on, open-source guide to using open-source AI models in real applications.** It brings model selection, inference, data preparation, fine-tuning, evaluation, and application development into one structured learning resource.

A useful model application starts with practical decisions: which model fits the task, what hardware it needs, how to adapt it to your data, and how to judge the result. The cookbook connects these decisions to runnable examples, using tools such as **EvalScope, ms-swift, DiffSynth, and Ollama**, alongside RAG and Agent workflows.

The goal is to help developers move from a first successful inference to applications they can reproduce, evaluate, and improve. Examples cover enterprise knowledge Q&A, speech assistants, customer-service quality analysis, fitness coaching, product-image creation, and production-line inspection.

> **8 parts · 35 chapters · 34 available to read**

## Start reading

**[Read online on ModelScope →](https://modelscope.cn/studios/ms-cookbook-team/ms-cookbook)**

No installation is needed for online reading. The website includes full-text keyword search, guided reading paths, chapter navigation, code copying, image enlargement, and rendered mathematical formulas.

For local reading:

```bash
git clone https://github.com/modelscope/ms-cookbook.git
cd ms-cookbook
python3 -m http.server 4173 --bind 127.0.0.1
```

Open [http://127.0.0.1:4173/#home](http://127.0.0.1:4173/#home). If the port is occupied, use `4174` in both the command and URL. Stop the server with `Ctrl+C`.

Reading locally requires Python 3 and a modern browser; it requires no project dependencies, build step, API key, or GPU. Individual exercises may require model downloads, credentials, software, or compute resources as described in their chapters.

## Learning paths

| Your goal | Recommended chapters | What you will practice |
| --- | --- | --- |
| **Get started** | [01](content/chapters/chapter-01.md) → [05](content/chapters/chapter-05.md) → [07](content/chapters/chapter-07.md) | Understand models, define a task, and run a first inference |
| **Adapt a model** | [12](content/chapters/chapter-12.md) → [13](content/chapters/chapter-13.md) → [15](content/chapters/chapter-15.md) | Prepare training data, fine-tune, and evaluate against a baseline |
| **Build an application** | [19](content/chapters/chapter-19.md) → [27](content/chapters/chapter-27.md) → [28](content/chapters/chapter-28.md) | Combine knowledge retrieval, external tools, and reusable skills |
| **Create with generative AI** | [21](content/chapters/chapter-21.md) → [22](content/chapters/chapter-22.md) → [23](content/chapters/chapter-23.md) → [25](content/chapters/chapter-25.md) | Explore examples, customize image LoRA, create product visuals, and study the foundations |

### Who is this for?

- **Developers and students** seeking a practical introduction to open-source model applications.
- **Application engineers** working on model selection, resource planning, fine-tuning, or evaluation.
- **AIGC practitioners** exploring image customization, generation, and editing.

Basic Python and command-line familiarity are useful for the coding exercises. Begin with a chapter that fits your current task, check its environment requirements, reproduce the example, and then test it with your own inputs. Record results and limitations before moving on.

## Book contents

Read each chapter on GitHub, or use the [online reading website](https://modelscope.cn/studios/ms-cookbook-team/ms-cookbook). Chapter titles are in Chinese.

| Chapter | Focus |
| --- | --- |
| **Part 1 · Understanding open-source models** | |
| [01 · 开源模型正在改变什么](content/chapters/chapter-01.md) | Openness, capabilities, and licensing |
| [02 · 开源模型还没用上，先卡在下载这一步？](content/chapters/chapter-02.md) | Model discovery, model cards, and downloads |
| [03 · 数据，是你要做开源模型微调的基石](content/chapters/chapter-03.md) | Data sources, quality, and preparation |
| [04 · 没有资源也能玩开源模型，因为这里资源免费](content/chapters/chapter-04.md) | Model and compute resources |
| **Part 2 · From a problem to a model task** | |
| [05 · 要把业务问题转换成模型任务问题](content/chapters/chapter-05.md) | Tasks, inputs, outputs, and evaluation criteria |
| [06 · 先评再选：用 EvalScope 形成开源模型的第一份报告](content/chapters/chapter-06.md) | Model-selection baselines with EvalScope |
| **Part 3 · Running your first models** | |
| [07 · 30 分钟带你快速看到第一个结果](content/chapters/chapter-07.md) | A first inference run |
| [08 · 多大模型，选择什么样的服务器配置](content/chapters/chapter-08.md) | Model size, memory, and server selection |
| [09 · 笔记本也能跑开源模型，先从 Ollama 开始](content/chapters/chapter-09.md) | Local inference with Ollama |
| [10 · 把模型放到云端跑，用 Notebook 试试 CPU 和 GPU](content/chapters/chapter-10.md) | CPU and GPU inference in cloud notebooks |
| [11 · 模型需要资源太多，量化能帮上什么忙？](content/chapters/chapter-11.md) | Quantization and resource trade-offs |
| **Part 4 · Fine-tuning and evaluation** | |
| [12 · 业务素材这么多，怎么变成能训练的数据？](content/chapters/chapter-12.md) | Turning business materials into training data |
| [13 · 快速用 ms-swift，完成开源模型的轻量微调](content/chapters/chapter-13.md) | Lightweight fine-tuning with ms-swift |
| [14 · 模型已经会回答了，为什么还要做偏好对齐？](content/chapters/chapter-14.md) | Goals and methods of preference alignment |
| [15 · 微调有没有用，测才知道？](content/chapters/chapter-15.md) | Comparing baseline and fine-tuned models |
| **Part 5 · Application systems** | |
| [16 · AI 健身教练：跟着视频练，让 AI 指出动作不标准的地方](content/chapters/chapter-16.md) | Pose estimation and movement comparison |
| [17 · 智能客服质检：AI 能从一通客服电话中分析出什么？](content/chapters/chapter-17.md) | Call transcription and quality analysis |
| [18 · 搭建一个能听也能说的语音助手](content/chapters/chapter-18.md) | Speech recognition, Q&A, and synthesis |
| [19 · 实现一个企业知识问答助手](content/chapters/chapter-19.md) | Knowledge retrieval and RAG |
| [20 · 场景有千千万，欢迎你来共建出你的场景](content/chapters/chapter-20.md) | Invitation to contribute reproducible application tutorials |
| **Part 6 · Generative AI** | |
| [21 · 10 个 Case，带你看看 AIGC 的开源模型能做到什么地步](content/chapters/chapter-21.md) | Open generative-model use cases |
| [22 · 定制？使用 DiffSynth 训练图像 LoRA](content/chapters/chapter-22.md) | Image LoRA customization with DiffSynth |
| [23 · 一张商品营销图，从生成到修改怎么做？](content/chapters/chapter-23.md) | Product-image generation and editing |
| [24 · 开源模型也能做出像样的 AI 视频吗？](content/chapters/chapter-24.md) | MiniMax H3 deployment tutorial pending |
| [25 · 补充：AIGC 理论知识](content/chapters/chapter-25.md) | Image and video generation fundamentals |
| **Part 7 · Agents** | |
| [26 · Agent 是什么，它能做什么事？](content/chapters/chapter-26.md) | Agent components, execution loop, and use cases |
| [27 · MCP：让模型连接外部工具](content/chapters/chapter-27.md) | Connecting models to external tools |
| [28 · Skill：把任务方法封装成能力](content/chapters/chapter-28.md) | Reusable task methods and workflows |
| [29 · 快速使用 Claude Code](content/chapters/chapter-29.md) | Getting started with Claude Code |
| [30 · 快速使用 PI](content/chapters/chapter-30.md) | Getting started with PI |
| [31 · 快速使用 DeepSeek Harness](content/chapters/chapter-31.md) | Getting started with DeepSeek Harness |
| [32 · 补充：Agent 框架知识](content/chapters/chapter-32.md) | Agent framework fundamentals |
| [33 · 产线巡检 Agent：用 Penguin Harness 快速开发与优化](content/chapters/chapter-33.md) | Develop a production-line inspection Agent with Penguin Harness and optimize it through evaluation |
| **Part 8 · Supplementary fundamentals** | |
| [34 · 补充：大模型基础知识](content/chapters/chapter-34.md) | Model architecture, training, inference, and limitations |
| [35 · 主流 LLM 评测](content/chapters/chapter-35.md) | Invitation to contribute evaluations of mainstream models |

## Application examples

| Example | Workflow explored | Chapter |
| --- | --- | --- |
| AI fitness coach | Compare body keypoints and exercise movements | [16](content/chapters/chapter-16.md) |
| Customer-service quality analysis | Turn call recordings into text and analysis | [17](content/chapters/chapter-17.md) |
| Speech assistant | Connect speech recognition, model responses, and speech synthesis | [18](content/chapters/chapter-18.md) |
| Enterprise knowledge assistant | Retrieve reference material for grounded answers | [19](content/chapters/chapter-19.md) |
| Product marketing visuals | Generate and edit product images | [23](content/chapters/chapter-23.md) |
| Production-line inspection | Develop a production-line inspection Agent with Penguin Harness and optimize it through evaluation | [33](content/chapters/chapter-33.md) |

## Community

<p align="center">
  <img src="assets/dada/dada.webp" width="88" alt="Dada community mascot">
</p>

Share questions, reproduction notes, and practical experience with other readers.

<table>
  <tr>
    <td align="center"><img src="assets/community/qr.png" width="200" alt="ModelScope Cookbook community QR code"><br><strong>ModelScope Cookbook community</strong></td>
    <td align="center"><img src="assets/community/agentwork-qr.png" width="200" alt="AgentWork community QR code"><br><strong>AgentWork community</strong></td>
  </tr>
</table>

Scan with WeChat, or save the image and scan it from your photo library. If a code expires, please [open an issue](https://github.com/modelscope/ms-cookbook/issues/new).

## Contributing

There are two ways to share your work:

- **GitHub:** report a problem in [Issues](https://github.com/modelscope/ms-cookbook/issues), or submit a focused [pull request](https://github.com/modelscope/ms-cookbook/pulls). Include the affected chapter or page, supporting references, and verification steps.
- **ModelScope:** visit [Developer Practices](https://modelscope.cn/spotlight), choose **创建内容** (Create content), and add the topic **#魔搭紫皮书**.

We welcome technical corrections, reproducible application examples, AIGC workflows, and reading-experience improvements. Preserve article wording and structure when making interface changes; content corrections need a clear source or author approval. Never include credentials, personal data, or material you cannot redistribute.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

### Acknowledgments

Thank you to [freestylefly](https://github.com/freestylefly), [yingdachen](https://github.com/yingdachen), [liucongg](https://github.com/liucongg), and everyone helping improve the project. [View all contributors →](https://github.com/modelscope/ms-cookbook/graphs/contributors)

Thanks to [Datawhale's Hello-Agents](https://github.com/datawhalechina/hello-agents) for the README organization reference.

## Maintenance

<details>
<summary><strong>Chapter sources, validation, and repository structure</strong></summary>

### Source of truth

- `content/chapters/`: GitHub-readable Markdown chapters, generated during builds.
- `content/source-html/`: canonical HTML sources that preserve the manuscript structure; make content edits here.
- `content/manifest.json`: titles, order, status, and snapshot date.
- `content/sync-report.json`: import-time source revisions and verification evidence.
- `assets/content.js`: generated chapter data loaded by the website.
- `index.html`, `assets/paper.js`, and the site stylesheets: reading interface.
- `assets/dada/` and `assets/community/`: artwork and community QR images.
- `assets/manuscript-20260914/`: bundled chapter images and attachments.

After an approved chapter edit:

```bash
python3 scripts/build-content.py
node scripts/build-content.mjs --check
node scripts/check-site.mjs
```

Building uses Python 3; validation also requires Node.js 22 or newer. Commit regenerated data with its sources. Preview affected pages on desktop and mobile. Reading an already-built checkout does not require these steps.

</details>

<details>
<summary><strong>GitHub → ModelScope automatic deployment</strong></summary>

The [deployment workflow](.github/workflows/deploy-modelscope.yml) publishes changes to site files on `main` to the public Studio `ms-cookbook-team/ms-cookbook`. It can also be triggered manually from GitHub Actions.

The workflow uses the repository secret `MODELSCOPE_API_KEY`, synchronizes committed files to the Studio's `master` branch, prepares a Chinese Studio card, and triggers deployment. It verifies the live page and deployed Git SHA before succeeding. GitHub remains the source of truth for code and content.

</details>

## License

This repository uses the [Apache License 2.0](LICENSE). Referenced models, datasets, and tools have their own licenses and terms. Chapter images and attachments remain subject to the rights of their authors or respective rights holders.

Bundled third-party components retain their licenses: [KaTeX · MIT](assets/katex/LICENSE), [Remix Icon · Apache 2.0](assets/home/REMIX-LICENSE), [Noto Serif SC · SIL OFL 1.1](assets/home/NOTO-LICENSE.txt), and [Dada · MIT](assets/dada/LICENSE). See the [Dada notice](assets/dada/NOTICE.md), [site attribution](assets/paper/ATTRIBUTION.txt), [shared asset attribution](assets/home/ATTRIBUTION.txt), and [artwork notes](assets/review/ATTRIBUTION.md).
