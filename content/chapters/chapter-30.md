<!-- Generated from ../source-html/chapter-30.html; do not edit independently. -->

# 快速使用 PI

Pi 的核心是 Agent Loop、模型调用、工具和终端界面。你需要 Skills、Prompt Templates、Extensions 和 Packages ，配上就行。

![正文配图](<../../assets/manuscript-20260914/c28-f8d0dc4f94a6ac.webp>)

另外，如果你平时已经在折腾 Codex、Claude Code、Agent Skills，Pi 还是很值得学习一下的。

<p></p>

<a id="c30-s1"></a>

## <strong>这次测试的本地环境</strong>

- 系统：macOS 26.0.1，Apple Silicon；
- Node.js：v26.7.0；
- npm：11.19.0；
- Pi：v0.85.1；
- 安装方式：临时目录隔离安装，165 个包，17 秒完成；

<p></p>

<a id="c30-s2"></a>

## <strong>Pi 到底是什么？</strong>

官方给它的定位是“minimal terminal coding harness”，翻成大白话，就是一套极简的终端 Agent 底座。

它的仓库里有几块核心组件：

- `pi-ai`：统一连接 OpenAI、Anthropic、Google、DeepSeek、OpenRouter、Ollama 等模型；
- `pi-agent-core`：负责工具调用、状态管理和 Agent 循环；
- `pi-tui`：终端交互界面；
- `pi-coding-agent`：我们真正安装和使用的 CLI。

Pi 默认交给模型的核心工具只有四个：`read`、`write`、`edit` 和 `bash`。

新版 CLI 里还能按需开放 `grep`、`find`、`ls`，Windows 也有可选的 PowerShell 工具。

看起来东西不多，但 Agent 底层无非就是读、写、改、执行。很多更复杂的能力，其实都可以从这几个原语长出来。

![正文配图](<../../assets/manuscript-20260914/c28-f3d9d1eae668f1.webp>)

很多 Agent 产品会把计划、子 Agent、MCP、权限审批和任务列表全部做好，用户只需要设置一下就行。

Pi 是给你一个能跑的 Agent 骨架，可以自定义 Agent。想要计划模式，就用文件写或者装扩展；想要子 Agent，就用 tmux 拉起多个 Pi，或者自己写 Extension；想接 MCP，也可以装对应扩展。

它更像一套已经通水通电的毛坯房。住得舒不舒服，取决于你后面怎么装修。

<a id="c30-s3"></a>

## 安装

<a id="c30-s4"></a>

### <strong>方法一：直接丢给 Agent 帮忙安装</strong>

如果你已经在用 Codex、Claude Code 或其他能操作终端的 Agent，可以把下面这段完整发给它：

```text
请根据我当前电脑环境安装并验证 Pi Coding Agent：

1. 先检查操作系统、CPU 架构、Node.js、npm，以及当前 PATH 中真正生效的 node 和 npm；
2. Pi 当前要求 Node.js >= 22.19.0，不满足时先说明升级方案，不要直接改动我的环境；
3. 使用官方 npm 包 @earendil-works/pi-coding-agent 安装，保留官方建议的 --ignore-scripts；
4. 安装后运行 pi --version 和 pi --help 验证；
5. 不读取、不打印、不修改任何 API Key 或登录凭据；
6. 告诉我如何通过 /login 登录已有订阅，以及如何在空白测试目录中做一次只读验证；
7. 遇到问题先核对项目官方仓库和官网的当前文档，不要猜参数。
```

<p></p>

<a id="c30-s5"></a>

### <strong>方法二：自己动手，一步步装</strong>

<strong>第 1 步：检查 Node.js 和 npm</strong>

macOS、Linux 打开终端，Windows 打开 PowerShell，先执行：

```bash
node -v
npm -v
```

Pi 当前 npm 包的 Node.js 要求是：

```text
>= 22.19.0
```

如果 `node -v` 低于这个版本，先升级 Node.js。电脑里同时装过 nvm、Homebrew、系统 Node 的朋友，再多看两眼：

```bash
which node
which npm
```

有时候你以为自己升级过了，但被终端调用的还是旧版本。这个坑在 CLI 工具里非常常见。

Windows 还有一个额外要求。Pi 默认通过 Git Bash 跑 Bash 命令，装好 Git for Windows 就行。

<strong>第 2 步：安装 Pi</strong>

官方 npm 安装命令：

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
```

提醒一下，这里的 `--ignore-scripts` 需要保留。它会禁止依赖在安装阶段执行生命周期脚本，而 Pi 的正常 npm 安装并不需要这些脚本。

官网还提供一键安装脚本：

```bash
curl -fsSL https://pi.dev/install.sh | sh
```

这几个方案都可以。但`curl | sh` 确实是最省事的。

安装完验证：

```bash
pi --version
pi --help
```

截至 2026 年 9 月 12 日，官方仓库当前版本是 `0.85.1`。项目迭代很快，版本号对不上不一定是安装失败，可以先看 GitHub Releases 和本地 `pi --version`。

![正文配图](<../../assets/manuscript-20260914/c28-1f91a7b2f904a0.webp>)

官网文档的 Quick start 也是这一条 npm 命令。

![正文配图](<../../assets/manuscript-20260914/c28-3a8ce1166a3644.webp>)

<strong>装好了，为什么还是启动不了？</strong>

最常见的一种情况，是终端提示：

```text
pi: command not found
```

可以先关掉终端重新打开，再看 npm 的全局安装位置：

```bash
npm config get prefix
npm list -g --depth=0
```

如果列表里已经有 `@earendil-works/pi-coding-agent`，说明包大概率装上了，只是 npm 的全局可执行目录没进 PATH。macOS 和 Linux 通常要检查全局前缀下的 `bin` 目录，Windows 则检查 npm 的全局目录。

另一类问题是 Node.js 版本看着没问题，执行 Pi 的时候却还在用旧环境。把下面几项一起看看：

```bash
which node
which npm
which pi
node -v
pi --version
```

如果 `pi` 能打开，但模型列表是空的，先执行 `/login`，再用 `/model` 选择模型。也可以退出后在命令行检查：

```bash
pi --list-models
```

<p></p>

<strong>第 3 步：登录模型</strong>

直接启动：

```bash
pi
```

打开以后，可以看到界面比较简洁：中间就是输入框，底部显示当前目录、上下文和模型。

![正文配图](<../../assets/manuscript-20260914/c28-85acc4da5f90b2.webp>)

进入终端界面后输入：

```text
/login
```

Pi 会让你选择模型提供商。官方目前支持 15 家以上，既能走 API Key，也能登录已有的订阅。

如果你有 ChatGPT Plus 或 Pro，可以选择 OpenAI Codex；也支持 GitHub Copilot。Claude Pro/Max 虽然能登录，但官方特别提醒，第三方 Harness 的调用会走 Anthropic 的 extra usage，按 Token 额外计费，不会直接消耗套餐内额度。这一点要特别注意一下。

用 DeepSeek API 的朋友，也可以在环境变量里提供：

```bash
export DEEPSEEK_API_KEY=你的Key
pi
```

不过对小白来说，我还是更建议在 Pi 里用 `/login`。凭据会保存在 `~/.pi/agent/auth.json`。

登录成功后，用下面两个命令，可以切模型和思考等级：

```text
/model
/thinking
```

`Ctrl+L` 也能快速打开模型选择器，`Shift+Tab` 可以切换思考等级。

![正文配图](<../../assets/manuscript-20260914/c28-299dc6897340df.webp>)

<strong>第 4 步：跑一次只读检查</strong>

进入一个你准备测试的项目目录，再执行下面的指令：

```bash
pi --tools read,grep,find,ls -p "阅读当前目录，告诉我项目是做什么的、入口文件在哪里、应该运行什么检查。不要修改任何文件。"
```

这里用了 Pi 的 Print 模式，任务完成后会直接退出；`--tools` 把可用工具锁定在读取范围里面。然后检查三件事：模型能不能连上、Pi 能不能读到工作区、工具限制有没有生效。

如果你只是想看某几个文件，也可以把文件直接塞给它：

```bash
pi -p @README.md "用大白话解释这个项目的安装和启动方式"
```

Pi 也支持查看图片：

```bash
pi -p @screenshot.png "看看这个报错页面，给我排查顺序"
```

<strong>第 5 步：验证写入能力</strong>

建一个专门的测试目录：

```bash
mkdir pi-playground
cd pi-playground
pi
```

把下面这个最小任务发给它：

```text
请先确认当前工作目录，并列出已有文件。
然后创建一个 hello-pi.md，内容包括：当前时间、工作目录、你能使用的工具名称。
除 hello-pi.md 外，不要创建、修改或删除任何文件。
完成后重新检查目录，并告诉我实际发生了哪些变化。
```

这个任务没什么技术含量，但很适合做验证。它会碰到目录读取、文件写入、约束遵守和结果复查。

确认这些都正常后，我们才能更放心的把 Pi 放进真实项目。

如果项目里带有 `.pi/settings.json`、`.pi` 资源或项目级 Skills，Pi 可能会询问是否信任当前目录。

信任项目意味着它可以加载项目配置、安装缺失的项目包，并执行项目 Extension。

<p></p>

<strong>先记住这些 Pi 的常用命令</strong>

- `/login`：登录或切换模型提供商；
- `/model`：换模型；
- `/thinking`：调整思考等级；
- `/new`：新建会话；
- `/resume`：继续历史会话；
- `/tree`：打开会话树，跳回任意节点；
- `/compact`：手动压缩上下文；
- `/reload`：重新加载配置、Skills、扩展和主题；
- `/hotkeys`：查看全部快捷键；
- `/session`：看当前会话文件、ID、Token 和费用。

我觉得这个指令很重要 `/tree`。

普通聊天如果前面如果方向错了，后面可能只有重新开一个会话。Pi 的 Session 用树结构保存，你可以跳回某条旧消息，从那里长出一条新分支，原来的分支还在同一个 JSONL 文件里。

比如让 Agent 重构代码，跑到一半如果发现路线不对，直接回到“开始重构”之前，再换个方案，这样就不用把前面的上下文全喂一遍。特别是长任务里，这个功能非常实用。

pi 的会话默认按工作目录保存在：

```text
~/.pi/agent/sessions/
```

命令行里还可以这样继续对话：

```bash
pi -c
pi -r
```

前者继续最近一次会话，后者让你挑历史会话。

<strong>用到自己的产品里</strong>

Pi 不止能在终端里聊天。

官方把它的使用方式归成四组：Interactive、Print/JSON、RPC 和 SDK。其中 Print 与 JSON 都适合程序化的一次性或流式任务，所以被放在同一组。

默认直接执行 `pi`，进入 Interactive 模式，适合日常写代码和长任务。

Print 模式适合一次性命令：

```bash
pi -p "检查这个项目有哪些明显问题"
```

JSON 模式会持续输出事件流，方便接 Shell 脚本、日志系统或自己的自动化程序：

```bash
pi --mode json "分析当前项目"
```

RPC 模式通过标准输入输出接收 JSONL，适合把 Pi 嵌进非 Node.js 应用：

```bash
pi --mode rpc
```

Pi 还有 SDK。开发者可以直接在 TypeScript 项目里创建 Agent Session，把 Pi 当成自己的 Agent Runtime。

所以你看到的是同一套内核，但在终端、脚本、服务和自己的产品里都能用。

<a id="c30-s6"></a>

## <strong>三个官方案例，更了解 Pi</strong>

下面三个案例来自 Pi 官方公开页面。主要是想让大家更清楚这套 Harness 到底怎么用。

<a id="c30-s7"></a>

### <strong>案例一：一份树形会话</strong>

刚刚说了，Pi 的会话不是只有一条聊天流水线。官方共享会话页左边直接展示了 241 个节点和不同分支；右边则能展开 System Prompt、工具、消息和调用记录。

这比“支持历史记录”更具体，更实用。你可以回到旧节点另起一条路，也可以把完整过程导出。对

![正文配图](<../../assets/manuscript-20260914/c28-c72aaef02c6baa.webp>)

<a id="c30-s8"></a>

### <strong>案例二：把别人的扩展、Skills 和主题直接装进来</strong>

Pi 官网有一个 Package Catalog。有 5,435 个条目，里面既有 MCP Adapter、网页访问，也有工作流、数据库和待办组件。

这些是能用 `pi install npm:<package>` 直接装进本机的能力包。换句话说，Pi 的扩展生态是非常丰富的。

![正文配图](<../../assets/manuscript-20260914/c28-825b36602d2e3b.webp>)

<a id="c30-s9"></a>

### <strong>案例三：把 Doom 塞进终端</strong>

这个 Case 很离谱，但也最能说明 Extension 能扩展到什么程度。官方演示里，Agent 在后台执行任务，Doom 直接嵌在 Pi 的 TUI 里！这个交付做的真心不错，而且底部也仍然保留了模型、Token、费用和任务状态。

Extension 能接事件、改界面、注册工具，甚至把整个交互层换掉。

![正文配图](<../../assets/manuscript-20260914/c28-c3b89b5e1fba71.webp>)

<p></p>

<a id="c30-s10"></a>

## <strong>把你现成的 Codex、Claude Skills 接进来</strong>

Pi 会自动扫描这些位置：

```text
~/.pi/agent/skills/
~/.agents/skills/
.pi/skills/
.agents/skills/
```

其中项目级 Skills 只有在项目被信任后才会加载。

如果你已经积累了一堆 Claude Skills 或 Codex Skills，可以编辑全局设置：

```text
~/.pi/agent/settings.json
```

加入：

```json
{
  "skills": [
    "~/.claude/skills",
    "~/.codex/skills"
  ]
}
```

回到 Pi 里执行：

```text
/reload
```

Skills 会以渐进式方式加载。启动时只把名称和描述放进上下文，任务匹配后再读取完整 `SKILL.md`，不会一上来把所有说明都塞进上下文。

想强制调用某个 Skill，可以输入：

```text
/skill:skill-name
```

这个设计和现在的 Agent Skills 标准是对齐的。你过去给 Codex、Claude Code 做的很多 Skill 能力包，都可以复用。

<a id="c30-s11"></a>

## <strong>让 Pi 扩展更多能力</strong>

Skills 主要解决“怎么做”，Extensions 能直接改 Pi 本身，功能更加强大。

一个 Extension 可以注册新工具、新命令、新快捷键和事件；能改状态栏、编辑器、弹窗、主题；也能实现子 Agent、计划模式、权限门、Git 自动提交、SSH 执行、沙箱，甚至补上 MCP。

官方首页展示的 Doom，就是一个很直观的 Extension 例子。

官方建议：你缺什么能力，就让 Pi 给自己写一个 Extension。改完执行 `/reload`，还可以继续当前的工作。

如果这套能力以后还要复用，可以把 Extension、Skill、Prompt 和主题都装进一个 Pi Package：

```bash
pi install npm:@foo/pi-tools
pi install git:github.com/user/repo
pi list
pi config
```

说明一下，Pi Package 跟浏览器里的隔离插件完全两回事。

<p></p>

<strong>它最容易被忽略的坑：默认没有权限保护</strong>

Pi 默认不会像一些桌面 Agent 那样，删文件、跑命令之前弹一个确认框。它直接继承了启动进程的文件、网络、凭据和系统权限。

但是这不算隐藏 Bug，官方首页就把“No permission popups”写得很明白。

对熟悉终端的人，这代表 YOLO 模式，也就是任务不会频繁被打断。

但对小白来说，可能一句写得不够严谨的 Prompt，真有可能让 Agent 干坏事，比如清空你的 C 盘啥的。。。

小白第一次使用，一定要注意以下几点：

- 先用空白目录，不要上来就打开桌面、文档或整个 Home 目录；
- 读代码时，用 `--tools read,grep,find,ls` 锁成只读；
- 不要让模型读取 `~/.pi/agent/auth.json`、`.env` 和其他凭据文件；
- 第三方 Package 和 Extension 先审源码，再安装；
- 真要让它长时间自动跑，放进 Docker、OpenShell 或其他沙箱。

官方给了多种隔离方案。最容好用的是把整个 Pi 放进 Docker。

需要注意，挂载进去的工作目录依然能写回宿主机；把本机的 `~/.pi/agent` 也挂进去，则会把认证和会话文件一起暴露给容器。

另外，Pi 启动时会检查新版本；首次安装或检测到升级后，还会发送匿名版本信息。介意这块，可以在设置里关闭安装遥测，或者使用：

```bash
PI_TELEMETRY=0 pi
```

需要完全关闭启动时的联网检查，可以用：

```bash
PI_OFFLINE=1 pi
```

<a id="c30-s12"></a>

## <strong>Pi 适合谁？</strong>

如果你只想下载一个产品，登录，然后在安全护栏里稳定使用，Pi 不一定是最省心的选择。它有意省掉了一些“装好就该有”的功能，很多东西需要自己配。

已经在用多个模型、手里有不少 Skills、想把 Agent 接进脚本或产品、对终端和权限有基本判断的人，会更容易感受到它的价值。尤其是做一人公司和独立开发的朋友。

当然，自由度越高，安全这块更需要自己把好关。

<p></p>

<p></p>
