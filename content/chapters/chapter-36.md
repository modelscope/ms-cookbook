<!-- Generated from ../source-html/chapter-36.html; do not edit independently. -->

# 快速使用 AtomCode

AtomCode 是 Claude Code / Codex 的开源平替，一个住在你的终端里的 AI 编程 Agent：连接任意 OpenAI 兼容大模型，自主读文件、改代码、跑测试、自我验证。本项目 100% 由 AI 生成，用 Rust 构建，迭代迅速，不断汲取 Claude Code 和 Codex 的最新技术。

目前，官方的 CodingPlan 提供 DeepSeek-V4-Flash + Qwen3-VL 的免费额度，量大管用，注册即用。

<table><thead><tr><th><p>项目</p></th><th><p>说明</p></th></tr></thead><tbody><tr><td><p>版本</p></td><td><p>v0.2.0（2026 年 7 月校核升级）</p></td></tr><tr><td><p>适用版本</p></td><td><p>AtomCode V4.25.9+</p></td></tr><tr><td><p>推荐模型</p></td><td><p>DeepSeek-V4 / Qwen3 / GLM-4-Plus / Claude Sonnet</p></td></tr><tr><td><p>作者</p></td><td><p>禾路（jsxyhelu）</p></td></tr><tr><td><p>原始版本</p></td><td><p>v0.0.1（2026 年 6 月）</p></td></tr><tr><td><p>参考来源</p></td><td><p>AtomCode 官方文档、DeepSeek 公开文档、《Claude Code 从入门到精通》(花叔)</p></td></tr></tbody></table>

> <strong>免责声明</strong>：本文基于 AtomCode 官方文档（[https://atomcode.atomgit.com/docs/](<https://atomcode.atomgit.com/docs/>)）及作者实操经验编写。AI 工具迭代极快，请结合官方文档验证。AtomCode 为 100% AI 生成的开源项目（MIT 协议），用 Rust 构建，持续迭代中。

> <strong>v0.2.0 更新说明</strong>：本版基于 v0.1.0 进行全面校核——修复了全角引号方向错误（成对右引号修正为左右配对）；修正了 Rust 工具链版本要求（1.88+ → 1.75+）；新增 IDE 插件（VS Code / JetBrains）与卸载说明章节；在附录对比表中补充了 IDE 插件维度。

全书按一条主线走：<strong>一个有基础经验的工程师怎么在一周内从零用 AI 构建产品</strong>。

<table><thead><tr><th><p>阶段</p></th><th><p>章节</p></th><th><p>你会学到</p></th></tr></thead><tbody><tr><td><p>Day 1 · 上手</p></td><td><p>§01 - §03</p></td><td><p>理解 AI 编程 → 安装配置 → 做出第一个项目</p></td></tr><tr><td><p>Day 2-3 · 核心</p></td><td><p>§04 - §06</p></td><td><p>掌握工作流 → 命令与快捷键 → 学会有效沟通</p></td></tr><tr><td><p>Day 4-5 · 进阶</p></td><td><p>§07 - §08</p></td><td><p>扩展能力（Skills / Hooks / MCP / 代码图谱）→ 多 Agent 协作</p></td></tr><tr><td><p>Day 6-7 · 实战</p></td><td><p>§09 - §10</p></td><td><p>独立构建完整产品 → 建立长期心智模型</p></td></tr></tbody></table>

每章都有实操部分，可以跟着做。不用一口气读完，读一章、做一章、再回来读下一章，完全没问题。

<a id="c36-s1"></a>

## §01 为什么是 AtomCode

AtomCode 与 Claude Code 的核心差异，先放一张对比表。AtomCode 并非 Claude Code 的简单模仿，而是在国产化话语体系下的一次重新构建，两者在设计理念、技术栈、模型支持和扩展能力上存在显著差异：

<table><thead><tr><th><p>维度</p></th><th><p>Claude Code</p></th><th><p>AtomCode</p></th></tr></thead><tbody><tr><td><p>开源协议</p></td><td><p>闭源商业产品</p></td><td><p>开源（MIT），100% AI 生成</p></td></tr><tr><td><p>技术栈</p></td><td><p>Bun + React + Ink + TypeScript</p></td><td><p>Rust 1.75+ 原生编译</p></td></tr><tr><td><p>模型支持</p></td><td><p>仅 Claude 系列</p></td><td><p>任意 OpenAI 兼容 API（DeepSeek / Qwen / GLM / Ollama 等）</p></td></tr><tr><td><p>代码图谱</p></td><td><p>无</p></td><td><p>8 个代码图谱工具（符号导航 / 调用链 / 影响面分析）</p></td></tr><tr><td><p>项目指令</p></td><td><p>CLAUDE.md</p></td><td><p>.atomcode.md（兼容 AGENTS.md / CLAUDE.md）</p></td></tr><tr><td><p>视觉能力</p></td><td><p>Claude 原生视觉</p></td><td><p>视觉预处理器（非视觉模型也能处理图片）</p></td></tr><tr><td><p>WebUI</p></td><td><p>Desktop App</p></td><td><p>内置 /webui，浏览器实时同步</p></td></tr><tr><td><p>后台会话</p></td><td><p>Subagents</p></td><td><p>/bg 16 槽位后台会话</p></td></tr><tr><td><p>Plugin 生态</p></td><td><p>原生生态</p></td><td><p>兼容 Claude Code Plugin 协议</p></td></tr><tr><td><p>平台支持</p></td><td><p>macOS / Linux / Windows</p></td><td><p>macOS / Linux / Windows / HarmonyOS PC</p></td></tr><tr><td><p>IDE 插件</p></td><td><p>无原生 IDE 插件</p></td><td><p>VS Code + JetBrains 插件（侧边栏 / 右键菜单 / Diff 预览）</p></td></tr></tbody></table>

<strong>【国产化优势】</strong> 在国产化话语体系下，「国产开源软件 + 国产大模型」有着特殊优势：数据不出境、无网络依赖门槛、符合信创要求。AtomCode + DeepSeek / Qwen 的组合，实现了从工具到模型的完整国产化替代。

<a id="c36-s2"></a>

### 这本书写给谁

- <strong>工程师，想提高 10 倍效率。</strong> 你已经会写代码，但每天大量时间花在样板代码、调试、写测试、处理 CI/CD 上。AtomCode 能接管这些，让你把精力放在架构决策和产品思考上。
- <strong>产品经理，想自己做 MVP。</strong> 你有产品直觉和用户洞察，但受限于开发资源。AtomCode 让你一个周末做出一个能跑的原型，不用等排期。
- <strong>创业者，想实现一人公司。</strong> 你想验证商业想法，但不想在技术上花太多钱和时间。AtomCode 让一个人拥有一个小团队的开发能力。

<a id="c36-s3"></a>

## §02 10 分钟完成安装

安装过程比你想象的简单。AtomCode 支持 macOS、Linux、Windows 和 HarmonyOS PC 四大平台。

<a id="c36-s4"></a>

### 方式 1：一键安装（推荐）

macOS / Linux / HarmonyOS PC：

```bash
curl -fsSL https://raw.atomgit.com/atomgit_atomcode/atomcode/raw/main/scripts/install.sh | sh
```

Windows PowerShell：

```powershell
irm https://raw.atomgit.com/atomgit_atomcode/atomcode/raw/main/scripts/install.ps1 | iex
```

<a id="c36-s5"></a>

### 方式 2：通过 npm 安装

已安装 Node.js 18+ 时，可以直接走 npm 全局安装，自动解析对应平台预编译二进制：

```bash
npm install -g @atomgit.com/atomcode
```

<a id="c36-s6"></a>

### 方式 3：通过 Homebrew 安装

```bash
brew install --cask atomcode
```

<a id="c36-s7"></a>

### 方式 4：从源码构建

需要 Rust 1.75+ 工具链：

```bash
git clone https://atomgit.com/atomgit_atomcode/atomcode.git
cd atomcode
cargo build --release
cp target/release/atomcode ~/.local/bin/
atomcode --version
```

<a id="c36-s8"></a>

### 首次启动与配置

直接在任意目录运行 `atomcode`，第一次启动会自动弹出 3 步首次启动向导（随时可用 `/welcome` 重新打开）：

1\. <strong>第 1 步 · 欢迎</strong>：显示版本信息和核心特性。

2\. <strong>第 2 步 · 语言选择</strong>：自动检测 / English / 简体中文，选完立即生效并写回 config.toml。

3\. <strong>第 3 步 · 配置接入方式（三选一）</strong>：

- <strong>用 AtomGit CodingPlan 一键接入（推荐）</strong>——OAuth 登录，自动申领免费额度，自动配置 provider；
- <strong>手动配置 provider</strong>——已有 API Key 时选择，进入 provider 管理界面；
- <strong>跳过，先进 TUI 探索</strong>——之后再 `/login` 或 `/provider` 完成配置。

<strong>【局域网 / 本地模型经验】</strong> 如果在局域网部署、用本地大模型（如 Ollama）的话，记得一定要随便写一个 api-key，才能够顺利运行下去，这是经验之谈。

<a id="c36-s9"></a>

### 配置文件位置

配置文件采用 TOML 格式，支持多 provider 并行存在、随时切换：

- macOS / Linux / HarmonyOS PC：`~/.atomcode/config.toml`
- Windows：`%USERPROFILE%\.atomcode\config.toml`
- 也可通过 `--config /path/to/config.toml` 指定任意路径

最小配置示例：

```toml
default_provider = "deepseek"

[providers.deepseek]
type = "openai"
api_key = "sk-xxxxxxxxxxxxxxxx"
model = "deepseek-chat"
base_url = "https://api.deepseek.com/v1"
context_window = 64000
```

AtomCode 支持三种 provider 类型：`openai`（兼容 DeepSeek / Qwen / GLM / SiliconFlow 等）、`claude`（Anthropic）、`ollama`（本地模型）。可以同时配置多个 provider，用 `/provider` 在 TUI 中随时切换。

<strong>【视觉预处理器】</strong> 当主 provider 不支持图片输入时，AtomCode 会自动调用一个独立的 VL 预处理器（视觉模型）对图片做 OCR + 描述，把结果作为文本传给主模型。配置 `vision_preprocessor_provider` 字段即可启用。这是 AtomCode 的独有功能，让纯文本模型也能「看图说话」。

<a id="c36-s10"></a>

### 卸载 AtomCode

不再需要 AtomCode 时，用内置的 `uninstall` 子命令一步清理：

```bash
atomcode uninstall
```

它会按组询问是否删除二进制、PATH 编辑、凭据（`~/.atomcode/auth.toml`）、运行状态（`~/.atomcode/sessions/`）。非交互式参数：

<table><thead><tr><th><p>参数</p></th><th><p>行为</p></th></tr></thead><tbody><tr><td><p><code>--yes</code></p></td><td><p>按默认决策走</p></td></tr><tr><td><p><code>--purge</code></p></td><td><p>一键全清，包括所有会话历史</p></td></tr><tr><td><p><code>--keep-data</code></p></td><td><p>只删二进制，保留 <code>~/.atomcode/</code></p></td></tr><tr><td><p><code>--dry-run</code></p></td><td><p>只打印计划不执行</p></td></tr></tbody></table>

<strong>【注意】</strong> `--purge` 会连带删除所有会话历史、记忆、自定义 provider 配置、OAuth token，不可逆。如果以后还可能用 AtomCode，优先用默认交互式或 `--keep-data`。

<a id="c36-s11"></a>

### IDE 插件：在编辑器里也能用

除了终端 TUI，AtomCode 还提供了 VS Code 和 JetBrains（IntelliJ IDEA / WebStorm / PyCharm / GoLand）的 IDE 插件，让终端级 AI 能力无缝接入编辑器。

<strong>安装方式</strong>

- <strong>VS Code</strong>：在 Marketplace 搜索 AtomCode 安装，或命令行执行 `code --install-extension atomcode-tools.atomcode-tools`；
- <strong>JetBrains</strong>：在 Plugins Marketplace 搜索 AtomCode 安装。

<strong>核心功能</strong>

- <strong>侧边栏聊天</strong>——在编辑器侧边栏打开 AtomCode 面板，不离开上下文即可与 AI 对话；
- <strong>Diff 代码预览</strong>——所有代码变更以 IDE 原生 diff 视图展示，确认后才写入文件；
- <strong>右键菜单</strong>——选中代码，右键 Explain / Fix / Optimize / Add to Chat，全语言支持；
- <strong>会话管理</strong>——按时间分组的历史会话，支持搜索、重命名、删除、恢复；
- <strong>多模型与 Thinking</strong>——Claude / OpenAI / DeepSeek / GLM / Qwen / Ollama，支持 thinking 参数配置。

<strong>【使用建议】</strong> IDE 插件与终端 TUI 共享同一份 config.toml 配置和会话历史，可以交替使用：终端里跑长任务，IDE 里做精细编辑，两者各有所长。

<a id="c36-s12"></a>

## §03 你的第一个项目

理论讲完了，直接上手。这一章从零做一个真实的 CLI 工具。做完之后，你就真正理解对话式编程是怎么回事了。

<a id="c36-s13"></a>

### 做个什么

一个<strong>每日 AI 新闻聚合器</strong>，CLI 工具。功能很简单：

- 从几个 RSS 源（知乎、豆瓣等）抓取最新文章；
- 用 AI 总结每篇文章的要点；
- 输出一份格式整齐的 Markdown 日报。

为什么选这个？够小，一个下午能做完；又够完整，涉及网络请求、数据处理、AI 调用、文件输出。一次项目就能把 AtomCode 的各种能力体验个遍。

<a id="c36-s14"></a>

### 第一步：告诉 Atom 你要什么

启动 AtomCode，用 `/cd` 命令进入一个空文件夹。然后，用自然语言告诉 Atom 你想要什么：

```text
制作一个 AI 新闻聚合器，CLI 工具，具体功能包括：
① 从几个 RSS 源（知乎、豆瓣等）抓取最新文章；
② 用 AI 总结每篇文章的要点；
③ 输出一份格式整齐的 Markdown 日报。
首先给出实现建议
```

注意最后那句「首先给出实现建议」。这不是客气，是一个重要技巧：<strong>让 Atom 先想清楚再动手</strong>。

<a id="c36-s15"></a>

### 第二步：看它怎么想的

Atom 收到需求后，不会直接开写，会先给你一个方案。这时候你就是在看工程方案的产品经理。觉得行就说 OK，想调整就直接说。

<strong>【技术选型经验】</strong> 主流方案包括 Python 和 Node.js。一般来说，纯网络程序倾向 Python，带界面的使用 Node.js。这个来回就是对话式编程的核心——大模型给的建议通常全面且正确，但在此基础上提出针对性修改意见或找到关键错误，就是 AI 时代工程师的能力。

<a id="c36-s16"></a>

### 第三步：看它干活

确认方案后，执行「执行」。终端里会看到一系列操作：Atom 创建文件结构、编写核心模块、安装依赖包、运行测试。如果报错了，它会自己读错误信息、找问题、修代码、再运行，形成自动修复循环。

整个过程大约 2-5 分钟。你干嘛？看着就行。就像把任务交给新同事，前几次你会盯着看他怎么做事。等熟悉了他的风格，以后放心让他自己干就好。

<a id="c36-s17"></a>

### 第四步：看看结果对不对

Atom 干完了，但可能还没有配置 API key，所以还没有跑真实的测试。直接告诉它，并要求其开展测试。如果一切顺利，你会在目录下看到一个 Markdown 文件。

<a id="c36-s18"></a>

### 第五步：进一步修改

能跑了，但是功能不多。比如更倾向于获得国内的新闻，那么要求 AtomCode 让你来翻牌子。

每一轮，Atom 改代码、跑测试、确认结果。你始终只做两件事：<strong>说清楚要什么，验证结果</strong>。

<strong>【警惕幻觉】</strong> AtomCode 让你感觉能够实现很多东西，但需要注意这可能只是幻觉。判断功能的实现本身是非常个性化的操作，这里正是工程师的经验发挥作用的地方。

<a id="c36-s19"></a>

## §04 核心工作流

跑通第一个项目之后，你可能觉得 AtomCode 也就这样——写代码、确认权限、看结果。但日常用下来，真正拉开效率差距的是几个核心工作模式。这一章把它们拆开聊。

<a id="c36-s20"></a>

### Plan 模式：先想清楚再动手

Plan 模式的作用很直接：<strong>让 Atom 只规划、不执行</strong>。它会告诉你它打算怎么做，但不会动你的代码、不会装包、不会运行命令。你们来回讨论方案，确认了再放手让它去做。

- <strong>如何进入</strong>：在 AtomCode 的输入框中输入 `/plan`。在这种情况下，它可以读取文件来理解代码，但不会修改任何文件。它会给出详细的实现方案，包括要改哪些文件、怎么改。你可以反复讨论、修改方案。
- <strong>切换到执行模式</strong>：输入 `/build` 则切换为执行模式（Build 模式）。因为计划已经讨论充分，你可以放心地让 Atom 一次性执行。

<strong>【流程精髓】</strong> 把纠结放在 Plan 阶段解决完，执行阶段一气呵成。边做边改、反复返工是最浪费 tokens 的用法。

<a id="c36-s21"></a>

### /goal：自动循环直到达成

AtomCode 独有功能：`/goal` 命令设定一个完成目标，让 agent 自动循环——一轮接一轮——直到目标达成。

```text
/goal 所有测试通过且无 TypeScript 编译错误   # 设定目标
/goal                                        # 查看当前目标与轮数
/goal clear                                  # 停止自动循环
```

这适合需要多轮迭代的任务，比如「修复所有测试直到通过」或「重构直到代码审查无问题」。你设定目标后可以去做别的事，AtomCode 会自己一轮一轮地推进。

<a id="c36-s22"></a>

### WebUI：同步查看执行过程

输入 `/webui`，能够以 web 页面的形式同步查看执行过程，并自动打开浏览器（默认绑定 127.0.0.1:13457）。当前 TUI 会话会自动接入实时同步。

```text
/webui       # 启动浏览器界面
/webui lan   # 暴露到局域网（等价于 --host 0.0.0.0）
/webui stop  # 关闭 webui 服务
/sync        # 把当前 TUI 接入正在运行的 webui 会话
/sync off    # 退出同步
```

WebUI 支持多浏览器 / 终端同时围观同一会话，两端实时双向同步。配合蒲公英虚拟 IP 可远程访问。

<a id="c36-s23"></a>

### 权限管理

AtomCode 的权限体系分为三个层次：

<table><thead><tr><th><p>方式</p></th><th><p>省心程度</p></th><th><p>安全程度</p></th><th><p>适合谁</p></th></tr></thead><tbody><tr><td><p><code>-y / --dangerously-skip-permissions</code></p></td><td><p>高</p></td><td><p>低（跳过所有确认）</p></td><td><p>CI/CD、沙箱评测</p></td></tr><tr><td><p>「始终允许」（会话级）</p></td><td><p>中</p></td><td><p>中</p></td><td><p>日常开发</p></td></tr><tr><td><p>逐个确认（默认）</p></td><td><p>低</p></td><td><p>最高</p></td><td><p>高风险操作、初学阶段</p></td></tr></tbody></table>

<strong>【破坏性命令拦截】</strong> `rm -rf`、`dd`、`mkfs`、`sudo` 等高危命令，以及会清库重建表的数据库迁移（如 `migrate:fresh`、`db:reset`）都会强制弹出权限确认。这类确认始终触发——即便之前对 bash 选过「始终允许」也不能跳过。写入 `/etc`、`~/.ssh` 等敏感路径同样强制确认。

<a id="c36-s24"></a>

### 会话管理

- `/resume` —— 在不同会话之间切换或恢复（按时间倒序显示）；
- `/session` —— 新建一个干净会话；
- `/cd` 或直接输入 `cd /path` —— 切换工作目录（状态栏实时更新）；
- `/clear` —— 清空当前会话的消息（保留会话 ID 便于以后 `/resume`）；
- `/compact` —— 压缩历史消息以腾出上下文预算；
- `/undo` —— 回退对话记忆到上一轮（不恢复磁盘文件）；
- `/cost` —— 查看当前会话 token 用量。

<a id="c36-s25"></a>

### 六大常见坑

<table><thead><tr><th><p>坑</p></th><th><p>表现</p></th><th><p>解决方案</p></th></tr></thead><tbody><tr><td><p>1. 一个会话什么都塞</p></td><td><p>修 bug、加功能、重构全在一个会话</p></td><td><p>一个会话聚焦一个任务，做完就 <code>/clear</code> 或 <code>/session</code></p></td></tr><tr><td><p>2. 反复纠正越改越偏</p></td><td><p>纠正两次还是不对</p></td><td><p>果断 <code>/undo</code> 或 <code>/clear</code> 重来，用更好的初始 prompt</p></td></tr><tr><td><p>3. 看着像对的就接受</p></td><td><p>没实际运行就接受代码</p></td><td><p>每一轮改动都实际运行一次</p></td></tr><tr><td><p>4. 过度微操</p></td><td><p>每写一个文件都要看</p></td><td><p>关注结果，让 Atom 把完整任务做完</p></td></tr><tr><td><p>5. 需求模糊</p></td><td><p>「优化一下」「好看点」</p></td><td><p>给具体的、可验证的需求</p></td></tr><tr><td><p>6. 不写 .atomcode.md</p></td><td><p>每次新会话都重新解释项目</p></td><td><p>建立 .atomcode.md 并持续迭代</p></td></tr></tbody></table>

<a id="c36-s26"></a>

## §05 命令与快捷键

在 TUI 输入框中以 `/` 开头即可触发斜杠命令，并获得自动补全菜单。AtomCode 内置 30+ 个斜杠命令，Skills 和 Plugin 加载的命令也会自动出现在补全菜单里。

<a id="c36-s27"></a>

### 核心功能命令

<table><thead><tr><th><p>命令</p></th><th><p>作用</p></th></tr></thead><tbody><tr><td><p><code>/login</code></p></td><td><p>推荐——一条命令完成 AtomGit OAuth + 申领 CodingPlan 免费额度 + 自动写 provider 配置</p></td></tr><tr><td><p><code>/resume</code></p></td><td><p>打开会话选择器，恢复任意一个之前的持久化会话</p></td></tr><tr><td><p><code>/session</code></p></td><td><p>创建一个全新的、干净的会话</p></td></tr><tr><td><p><code>/bg</code></p></td><td><p>将当前会话放到后台并打开新的前台会话（最多 16 个并行后台槽位）</p></td></tr><tr><td><p><code>/provider</code></p></td><td><p>打开 provider 管理界面，增删改切换</p></td></tr><tr><td><p><code>/model</code></p></td><td><p>在当前 provider 下切换模型，或跨 provider 切换</p></td></tr><tr><td><p><code>/cd</code></p></td><td><p>切换工作目录，并写回 default_workdir</p></td></tr></tbody></table>

<a id="c36-s28"></a>

### 工具与实用操作

<table><thead><tr><th><p>命令</p></th><th><p>作用</p></th></tr></thead><tbody><tr><td><p><code>/view &lt;文件路径&gt;</code></p></td><td><p>以只读浮层打开文件内容（支持方向键翻页）</p></td></tr><tr><td><p><code>/undo</code> · <code>/undo N</code></p></td><td><p>把对话记忆回退到上一轮（或第 N 轮）之前，prompt 还原回输入框</p></td></tr><tr><td><p><code>/diff</code></p></td><td><p>显示当前工作目录未提交改动的 git diff</p></td></tr><tr><td><p><code>/review</code></p></td><td><p>对当前改动做代码审查（<code>/review staged</code> 审查暂存区，<code>/review &lt;base&gt;</code> 对比基准）</p></td></tr><tr><td><p><code>/cost</code></p></td><td><p>展示当前会话输出 token 数和上下文用量</p></td></tr><tr><td><p><code>/context</code></p></td><td><p>显示本轮上下文预算分解：系统提示、工具定义、总消息数等</p></td></tr><tr><td><p><code>/compact</code></p></td><td><p>压缩历史消息，把早期对话压缩成摘要以腾出上下文预算</p></td></tr><tr><td><p><code>/clear</code></p></td><td><p>清空当前会话的消息（保留工作目录和模型）</p></td></tr><tr><td><p><code>/init</code></p></td><td><p>扫描当前工作目录，生成 / 刷新 .atomcode.md 项目指令文件</p></td></tr><tr><td><p><code>/worktree &lt;子命令&gt;</code></p></td><td><p>Git worktree 隔离：create / list / done / cleanup</p></td></tr><tr><td><p><code>/issue</code></p></td><td><p>交互式向导：在 AtomGit 仓库创建新 issue</p></td></tr></tbody></table>

<a id="c36-s29"></a>

### 对话模式与思考

<table><thead><tr><th><p>命令</p></th><th><p>作用</p></th><th><p></p></th><th><p></p></th></tr></thead><tbody><tr><td><p><code>/plan</code></p></td><td><p>切到 Plan 模式：只读探索，不能写盘。适合动手前理清方案</p></td><td><p></p></td><td><p></p></td></tr><tr><td><p><code>/build</code></p></td><td><p>切回 Build 模式（默认）：全部工具可用，可以读、写、执行</p></td><td><p></p></td><td><p></p></td></tr><tr><td><p><code>/goal &lt;目标&gt;</code></p></td><td><p>设定完成目标，让 agent 自动循环直到达成。<code>/goal clear</code> 停止</p></td><td><p></p></td><td><p></p></td></tr><tr><td><p><code>/think on</code> / <code>/think off</code></p></td><td><p>开关 extended thinking（对 Claude / DeepSeek-R1 / GLM-4.5 等支持）</p></td><td><p></p></td><td><p></p></td></tr><tr><td><p><code>/think budget &lt;N&gt;</code></p></td><td><p>给 thinking 设 token 预算上限（对 Claude 系列生效）</p></td><td><p></p></td><td><p></p></td></tr><tr><td><p>`/effort &lt;high\</p></td><td><p>max\</p></td><td><p>off&gt;`</p></td><td><p>DeepSeek 推理努力控制——用更多延迟 / token 换取更深推理</p></td></tr></tbody></table>

<a id="c36-s30"></a>

### 永久记忆

<table><thead><tr><th><p>命令</p></th><th><p>作用</p></th></tr></thead><tbody><tr><td><p><code>/remember &lt;内容&gt;</code></p></td><td><p>记一条到项目级记忆（绑定当前工作目录）</p></td></tr><tr><td><p><code>/remember --global &lt;内容&gt;</code></p></td><td><p>记一条到全局记忆（所有项目共享）</p></td></tr><tr><td><p><code>/forget &lt;关键词&gt;</code></p></td><td><p>删除全局 + 项目记忆中含该关键词的所有条目</p></td></tr><tr><td><p><code>/memory</code></p></td><td><p>查看当前生效的所有记忆，按 [Global] / [Project] 分组</p></td></tr></tbody></table>

<a id="c36-s31"></a>

### 扩展生态

<table><thead><tr><th><p>命令</p></th><th><p>作用</p></th><th><p></p></th><th><p></p></th><th><p></p></th></tr></thead><tbody><tr><td><p><code>/setup</code></p></td><td><p>扫描项目，联网检索并推荐适合的 atomcode skill 安装</p></td><td><p></p></td><td><p></p></td><td><p></p></td></tr><tr><td><p><code>/skills</code></p></td><td><p>浏览当前已加载的 skills（项目级 + 用户级）</p></td><td><p></p></td><td><p></p></td><td><p></p></td></tr><tr><td><p><code>/plugin</code></p></td><td><p>打开交互式插件管理器，浏览 marketplace、安装 / 卸载插件</p></td><td><p></p></td><td><p></p></td><td><p></p></td></tr><tr><td><p>`/plugin marketplace add\</p></td><td><p>remove\</p></td><td><p>update\</p></td><td><p>list`</p></td><td><p>管理 marketplace 注册</p></td></tr><tr><td><p><code>/plugin install &lt;plugin&gt;@&lt;marketplace&gt;</code></p></td><td><p>从指定 marketplace 安装插件</p></td><td><p></p></td><td><p></p></td><td><p></p></td></tr><tr><td><p><code>/mcp</code></p></td><td><p>列出已成功连接的 MCP server 及状态</p></td><td><p></p></td><td><p></p></td><td><p></p></td></tr><tr><td><p><code>/mcp tools &lt;server&gt;</code></p></td><td><p>异步列出某个 MCP server 暴露的远端 tools</p></td><td><p></p></td><td><p></p></td><td><p></p></td></tr><tr><td><p><code>/mcp reload</code></p></td><td><p>重新读取 .mcp.json 并后台重连所有 server</p></td><td><p></p></td><td><p></p></td><td><p></p></td></tr></tbody></table>

<a id="c36-s32"></a>

### WebUI 与同步

<table><thead><tr><th><p>命令</p></th><th><p>作用</p></th></tr></thead><tbody><tr><td><p><code>/webui</code></p></td><td><p>启动浏览器界面并自动打开浏览器（默认 127.0.0.1:13457）</p></td></tr><tr><td><p><code>/webui lan</code></p></td><td><p>暴露到局域网（等价于 <code>--host 0.0.0.0</code>）</p></td></tr><tr><td><p><code>/webui stop</code></p></td><td><p>关闭 webui 服务</p></td></tr><tr><td><p><code>/sync</code></p></td><td><p>把当前 TUI 接入正在运行的 webui 会话，两端实时双向同步</p></td></tr><tr><td><p><code>/sync off</code></p></td><td><p>退出同步，回到独立会话</p></td></tr></tbody></table>

<a id="c36-s33"></a>

### 配置与帮助

<table><thead><tr><th><p>命令</p></th><th><p>作用</p></th></tr></thead><tbody><tr><td><p><code>/status</code></p></td><td><p>显示登录状态、当前 provider、模型、上下文预算、CodingPlan 用量</p></td></tr><tr><td><p><code>/config</code></p></td><td><p>显示 ~/.atomcode/config.toml 的路径</p></td></tr><tr><td><p><code>/reload</code></p></td><td><p>从磁盘热加载 config.toml，不需重启</p></td></tr><tr><td><p><code>/language</code></p></td><td><p>切换界面语言：自动检测 / English / 简体中文</p></td></tr><tr><td><p><code>/welcome</code></p></td><td><p>重新打开 3 步首次启动向导</p></td></tr><tr><td><p><code>/upgrade</code></p></td><td><p>自动升级到最新版本；<code>/upgrade rollback</code> 回滚</p></td></tr><tr><td><p><code>/guide</code></p></td><td><p>内置上手向导：<code>/guide &lt;主题&gt;</code> 直接讲解</p></td></tr><tr><td><p><code>/help</code></p></td><td><p>展示所有可用斜杠命令的列表</p></td></tr><tr><td><p><code>/quit</code> · <code>/exit</code></p></td><td><p>退出 atomcode（也可以连按两次 Ctrl+C）</p></td></tr></tbody></table>

<a id="c36-s34"></a>

### 快捷键速查

<table><thead><tr><th><p>快捷键</p></th><th><p>作用</p></th></tr></thead><tbody><tr><td><p><code>Enter</code></p></td><td><p>发送消息</p></td></tr><tr><td><p><code>Shift+Enter</code> / <code>Ctrl+Enter</code> / <code>Ctrl+J</code></p></td><td><p>换行（需 Kitty 键盘协议：kitty / WezTerm / Alacritty / iTerm2≥3.5 / Windows Terminal≥1.21）</p></td></tr><tr><td><p><code>Alt+Enter</code></p></td><td><p>换行（多数终端可用，Windows Terminal 默认绑给切换全屏需解绑）</p></td></tr><tr><td><p><code>Esc</code></p></td><td><p>打断模型正在进行的流式输出</p></td></tr><tr><td><p><code>Ctrl+C</code>（两次）</p></td><td><p>退出 atomcode</p></td></tr><tr><td><p><code>@</code>（行首或空白后）</p></td><td><p>弹出项目内文件 / 目录候选菜单</p></td></tr><tr><td><p><code>$</code>（行首）</p></td><td><p>弹出 skills 菜单，可直接带参数调用 skill</p></td></tr><tr><td><p><code>/</code>（行首）</p></td><td><p>弹出斜杠命令补全菜单</p></td></tr><tr><td><p><code>↑</code> / <code>↓</code></p></td><td><p>在补全菜单中切换候选</p></td></tr><tr><td><p><code>Tab</code> / <code>Enter</code></p></td><td><p>在补全菜单中确认选择</p></td></tr></tbody></table>

<strong>【命令使用技巧】</strong> 自动补全——输入 `/` 后会立刻弹出补全菜单，用 `↑↓` 选择，`Tab` / `Enter` 确认。模糊匹配——补全支持子串匹配，比如输入 `/prov` 就能命中 `/provider`。Skills 也会出现在菜单里——添加自定义 skill 后，它们会以相同格式出现在补全菜单里。

<a id="c36-s35"></a>

## §06 进阶对话技巧

AtomCode 不是搜索引擎，你不需要精心雕琢关键词。但怎么跟它说话，确实会影响输出质量。这一章聊的都是实战中真正管用的对话策略，不讲理论。

<a id="c36-s36"></a>

### 一、怎么说话 AtomCode 才听得懂

很多人第一次用 AtomCode，会写「帮我做一个用户管理系统」。AtomCode 会做，但做出来的东西大概率不是你想要的。信息太少，它只能猜。

AtomCode 官方文档总结了几条描述任务的原则：

<table><thead><tr><th><p>原则</p></th><th><p>说明</p></th><th><p>示例</p></th></tr></thead><tbody><tr><td><p>说目标，不说步骤</p></td><td><p>模型有足够的探索能力，你只需告诉它要什么</p></td><td><p>「修复登录后跳 404 的 bug」，而不是「打开 src/auth/callback.ts，删除第 27 行…」</p></td></tr><tr><td><p>点明约束</p></td><td><p>当你有偏好时明确说出</p></td><td><p>「保持 API 兼容」、「不改动测试文件」、「用 TypeScript 而不是 JS」</p></td></tr><tr><td><p>给出验证方式</p></td><td><p>让模型完成自我验证闭环</p></td><td><p>「改完后跑 npm test 确认通过」</p></td></tr><tr><td><p>先问后改</p></td><td><p>不确定方向时先让它分析</p></td><td><p>「分析这个模块的结构并提出重构方案」，对齐之后再动手</p></td></tr></tbody></table>

三个核心原则可以浓缩为三个字：

- <strong>具体。</strong> 文件名、行号、函数名、期望行为，能给就给。越具体的指令，越精确的输出。
- <strong>指向。</strong> 你代码库里一定有写得好的部分。把它们当参考范本指给 AtomCode 看。「像那个一样做」比「做一个漂亮的」有效 100 倍。
- <strong>克制。</strong> 一次只做一件事。任务大就分步来，每步确认结果后再下一步。一条消息里塞三个不相关的需求，AtomCode 大概率只做好其中一个。

<strong>【心态建议】</strong> 把 AtomCode 当成一个非常聪明但刚入职的同事。能力很强，但不了解你项目的历史和惯例。你给的上下文越精准，它的产出越接近预期。

<a id="c36-s37"></a>

### 二、Context Engineering：信息不是越多越好

Context 不只是你打的那句话。`.atomcode.md` 的内容、AtomCode 读过的文件、你粘贴的截图、对话历史，全部加起来都是 Context。

直觉上你可能觉得：给 AtomCode 的信息越多越好吧？恰恰相反。上下文太多，模型表现反而变差。它会在海量信息中迷失，做出混乱的决策。

AtomCode 提供了几种方式主动管理上下文：

<table><thead><tr><th><p>方式</p></th><th><p>命令 / 操作</p></th><th><p>说明</p></th><th><p></p></th></tr></thead><tbody><tr><td><p>查看上下文预算</p></td><td><p><code>/context</code></p></td><td><p>显示本轮上下文预算分解：系统提示、工具定义、冷区压缩、总消息数、context window 占用</p></td><td><p></p></td></tr><tr><td><p>压缩历史</p></td><td><p><code>/compact</code></p></td><td><p>把早期对话压缩成摘要以腾出上下文预算</p></td><td><p></p></td></tr><tr><td><p>清空对话</p></td><td><p><code>/clear</code></p></td><td><p>清空当前会话消息（保留会话 ID 便于 <code>/resume</code>）</p></td><td><p></p></td></tr><tr><td><p>引用文件</p></td><td><p><code>@文件路径</code></p></td><td><p>告诉 AtomCode 去读某个特定文件，不会无脑塞进上下文</p></td><td><p></p></td></tr><tr><td><p>粘贴截图</p></td><td><p><code>Ctrl+V</code> / 拖拽</p></td><td><p>UI 问题直接截图粘贴，比文字描述准确 10 倍</p></td><td><p></p></td></tr><tr><td><p>非交互模式</p></td><td><p>`cat error.log \</p></td><td><p>atomcode -p '分析这些错误'`</p></td><td><p>直接把日志 pipe 给 AtomCode</p></td></tr></tbody></table>

<a id="c36-s38"></a>

#### 代码图谱：AtomCode 独有的上下文优化

这是 AtomCode 区别于 Claude Code 的最大亮点。借助代码图谱索引，模型无需读遍整棵代码树就能精准定位符号、引用和调用关系，在大型仓库上效果尤其明显——大幅减少上下文消耗。

<table><thead><tr><th><p>图谱工具</p></th><th><p>作用</p></th><th><p>对比传统方式</p></th></tr></thead><tbody><tr><td><p><code>read_symbol</code></p></td><td><p>精准读取某个符号的完整定义片段，不用把整个文件拉进上下文</p></td><td><p>传统：read_file 读整个文件，浪费大量 token</p></td></tr><tr><td><p><code>find_references</code></p></td><td><p>查找某个符号被引用的所有位置</p></td><td><p>传统：grep 搜索，容易漏匹配或误匹配</p></td></tr><tr><td><p><code>trace_callers</code></p></td><td><p>回溯某个函数的调用方链路</p></td><td><p>传统：手动追踪多个文件</p></td></tr><tr><td><p><code>blast_radius</code></p></td><td><p>评估修改某个符号可能影响到的文件 / 符号范围</p></td><td><p>传统：凭经验猜测，容易遗漏</p></td></tr></tbody></table>

典型场景：你说「我想改 formatDate 的签名，影响面有多大？」，AtomCode 会自动调用 `blast_radius` \+ `find_references`，几秒钟给出精确的影响范围，而不需要读遍所有文件。

<a id="c36-s39"></a>

### 三、让 AtomCode 采访你

当你要做一个比较大的功能（比如从零搭建一个支付系统），不要一上来就写需求文档。先对 AtomCode 说：

```text
我要做一个支付系统，在动手之前，请你先问我一系列问题，
帮我把需求梳理清楚。每次只问一个问题。
```

AtomCode 会开始问你一系列问题：支持哪些支付方式？需要处理退款吗？并发量预估多少？需要支持 webhook 回调吗？用什么货币？

这些问题中，至少有一半是你自己没考虑过的。AtomCode 帮你做了需求分析师的工作。

采访结束后，让 AtomCode 把答案整理成一份 Spec（规格文档）。然后关键来了：<strong>开一个全新的会话，把 Spec 喂给新的 AtomCode，让它执行</strong>。

<strong>【为什么要开新会话】</strong> 采访过程中积累的对话历史已经很长了，占了大量上下文。新会话从一份干净的 Spec 开始，AtomCode 能更专注地执行，不会被中间讨论过程干扰。用 `/session` 新建会话，或用 `atomcode -c` 恢复上次会话后 `/clear` 再开始。

<a id="c36-s40"></a>

### 四、把 AtomCode 当高级工程师提问

很多人只把 AtomCode 当写代码的工具。其实它同样是一个极好的代码库导航员。借助代码图谱工具，你可以直接问它：

- 「项目里的 logging 怎么工作的？」→ AtomCode 调用 `list_symbols` 和 `read_symbol` 梳理结构；
- 「怎么新建一个 API endpoint？」→ AtomCode 找到现有 endpoint 作为范本；
- 「这个 useAuth hook 的调用链是什么？」→ AtomCode 调用 `trace_callees` 追踪下游；
- 「src/lib/db.ts 和 src/utils/database.ts 有什么区别？为什么有两个？」→ AtomCode 读取两个文件的符号定义做对比。

比读文档快，比问同事方便，尤其是刚接手一个新项目的时候。

<a id="c36-s41"></a>

### 五、多轮对话策略

和 AtomCode 的对话不是一次性的。你经常需要在多轮对话中逐步推进一个任务。这里有几个经过实战验证的策略：

<strong>策略 1：紧密反馈循环。</strong> 别等 AtomCode 写完 500 行代码再看结果。发现方向偏了，立刻纠正。越早纠正成本越低。AtomCode 写了 10 行时你说「不对，换个方式」，成本几乎为零。

<strong>策略 2：两次纠正不行，换条路。</strong> 纠正了两次 AtomCode 还是不按你的意思来？别继续纠正了。用 `/undo` 回退到跑偏之前的状态，或者 `/clear` 清掉上下文，用一个更好的初始 prompt 重新开始。在一个已经跑偏的对话里纠缠，往往越绕越远。

<strong>策略 3：换任务就清上下文。</strong> 写完一个组件后要去改数据库 schema？用 `/session` 开一个新会话。不同任务有不同的上下文需求，把前一个任务的对话历史带进新任务只会增加噪音。

<strong>策略 4：用 /bg 做后台调研。</strong> 有时你需要 AtomCode 先调研再动手：「看看这个库怎么用」「分析一下竞品的实现方式」。这些调研任务可以用 `/background` 或 `/bg` 来做，调研结果返回主会话，中间的思考过程不会污染主上下文。

<a id="c36-s42"></a>

### 六、Effort 级别与思考模式

AtomCode 的思考控制与 Claude Code 有所不同，它针对不同模型提供了差异化的控制方式：

<table><thead><tr><th><p>命令</p></th><th><p>作用</p></th><th><p>适用模型</p></th><th><p>与 CC 对比</p></th><th><p></p></th><th><p></p></th></tr></thead><tbody><tr><td><p><code>/think on</code> / <code>/think off</code></p></td><td><p>开关 extended thinking，模型输出推理过程</p></td><td><p>Claude / DeepSeek-R1 / GLM-4.5 等</p></td><td><p>CC 无此命令，thinking 通过其他方式控制</p></td><td><p></p></td><td><p></p></td></tr><tr><td><p><code>/think budget &lt;N&gt;</code></p></td><td><p>给 thinking 设 token 预算上限</p></td><td><p>Claude 系列</p></td><td><p>CC 通过参数控制</p></td><td><p></p></td><td><p></p></td></tr><tr><td><p>`/effort &lt;high\</p></td><td><p>max\</p></td><td><p>off&gt;`</p></td><td><p>推理努力控制，用更多延迟 / token 换取更深推理</p></td><td><p>DeepSeek 系列</p></td><td><p>CC 有 Low/Medium/High/Max 四级，AtomCode 的 effort 主要针对 DeepSeek</p></td></tr><tr><td><p><code>/goal &lt;目标&gt;</code></p></td><td><p>设定目标让 agent 自动循环直到达成</p></td><td><p>所有模型</p></td><td><p>CC 无此功能，这是 AtomCode 独有</p></td><td><p></p></td><td><p></p></td></tr></tbody></table>

<strong>【别省这个钱】</strong> 很多人觉得「这个任务简单，调到低 effort 省点时间」。但低 effort 做错了，你纠正它花的时间可能比直接用 high 做对还长。建议保持 `/think on` 和 `/effort high` 作为默认设置。

<a id="c36-s43"></a>

### 七、图片附件与视觉预处理器

AtomCode 支持把图片带进对话——报错截图、UI mock、白板照片等。提供三条入口：

- `Ctrl+V` —— 系统剪贴板里有图片时，按 `Ctrl+V` 直接 attach，任何终端都通用；
- `Cmd+V`（macOS / iTerm2，需配置）—— iTerm2 设置中把 ⌘V 映射为 Send Hex Codes: 0x16；
- <strong>Finder 拖拽</strong> —— 把图片直接拖进终端窗口，AtomCode 识别到图片路径 + 扩展名 + 文件存在 + 大小 ≤ 20MB 时自动 attach。

每次成功 attach 时，输入框会插入一个 `[Image #N]` 标记，提交时图片字节随消息一起发。

<strong>非视觉模型怎么处理图片？</strong> 当前 active provider 不支持图片输入时（比如 DeepSeek-V3 / Kimi 等纯文本模型），AtomCode 不会直接拒绝，而是会自动调用一个独立的 VL 预处理器（视觉模型，比如 Qwen3-VL / GLM-4V）对图片做 OCR + 描述，把结果作为文本传给主模型。

<strong>【AtomCode 独有功能】</strong> 这是 AtomCode 区别于 Claude Code 的一个重要特性。Claude Code 依赖 Claude 模型的原生视觉能力，而 AtomCode 的视觉预处理器让任意纯文本模型都能「看图说话」——即使你用的是免费的 DeepSeek，也能贴截图问问题。VL 调用使用无进展超时：只要 stream 持续吐 chunk 不限总时长，30 秒没动静才算超时。

<a id="c36-s44"></a>

## §07 扩展能力：Skills、Hooks 与 MCP

用到后面你会发现，AtomCode 真正的价值不是它本身有多强，而是你能在它身上接多少东西。Skills、Hooks、MCP、Plugin 四种扩展机制，加上独有的代码图谱工具，让它从一个终端工具变成一个可以无限生长的工作台。

<a id="c36-s45"></a>

### 一、为什么需要扩展

你一开始可能以为 AtomCode 装好就完事了。后来发现自己总在重复同样的话：每次提交代码前念叨一遍「先跑个 lint」、每次新建组件要交代一遍项目规范、每次查数据要手动复制 SQL 结果贴给 AtomCode。

这种重复一旦超过三次，就该想办法自动化了。AtomCode 提供了四种扩展机制，各自解决不同层面的问题。

<a id="c36-s46"></a>

### 二、四种扩展机制对比

<table><thead><tr><th><p>机制</p></th><th><p>本质</p></th><th><p>确定性</p></th><th><p>适用场景</p></th><th><p>AtomCode 特色</p></th></tr></thead><tbody><tr><td><p>Skills</p></td><td><p>Markdown 指令包（SKILL.md）</p></td><td><p>高但非 100%（advisory）</p></td><td><p>领域知识、可复用工作流</p></td><td><p>$ 菜单调用、use_skill 工具自动触发、/setup 自动推荐</p></td></tr><tr><td><p>Hooks</p></td><td><p>Shell 脚本钩子</p></td><td><p>100% 确定执行</p></td><td><p>格式化、lint、安全检查</p></td><td><p>支持 6 种事件，与 CC 兼容（部分事件不支持）</p></td></tr><tr><td><p>MCP</p></td><td><p>外部工具连接器</p></td><td><p>100%</p></td><td><p>数据库、API、第三方服务</p></td><td><p>tools-only，兼容 Cursor / .mcp.json 配置</p></td></tr><tr><td><p>Plugin</p></td><td><p>skill / 命令 / hook 集合</p></td><td><p>混合</p></td><td><p>一键安装完整工作流</p></td><td><p>兼容 Claude Code Plugin 协议</p></td></tr><tr><td><p>代码图谱</p></td><td><p>内置符号索引工具</p></td><td><p>100%（内置）</p></td><td><p>大型代码库导航、重构风险评估</p></td><td><p>AtomCode 独有，CC 无此能力</p></td></tr></tbody></table>

四者的关系：<strong>Skills 教 AtomCode 怎么做事，Hooks 在关键节点自动执行检查，MCP 把外面的世界接进来，Plugin 把前三者打包成一键安装的扩展包。</strong> 代码图谱则是 AtomCode 内置的差异化能力。

<a id="c36-s47"></a>

### 三、代码图谱：AtomCode 最大的差异化亮点

这是 AtomCode 区别于一般 agent 的最大亮点。借助代码图谱索引，模型无需读遍整棵代码树就能精准定位符号、引用和调用关系，在大型仓库上效果尤其明显。Claude Code 目前没有类似能力。

<a id="c36-s48"></a>

#### 8 个代码图谱工具详解

<table><thead><tr><th><p>工具</p></th><th><p>作用</p></th><th><p>典型使用场景</p></th></tr></thead><tbody><tr><td><p><code>list_symbols</code></p></td><td><p>列出某个文件或目录下定义的所有符号（函数、类、常量等）</p></td><td><p>快速了解一个模块有哪些功能</p></td></tr><tr><td><p><code>read_symbol</code></p></td><td><p>精准读取某个符号的完整定义片段，不用把整个文件拉进上下文</p></td><td><p>只看某个函数的实现，不浪费 token</p></td></tr><tr><td><p><code>find_references</code></p></td><td><p>查找某个符号被引用的所有位置</p></td><td><p>评估改名 / 修改签名的影响范围</p></td></tr><tr><td><p><code>trace_callers</code></p></td><td><p>回溯某个函数的调用方链路</p></td><td><p>定位「谁在调用这个函数」</p></td></tr><tr><td><p><code>trace_callees</code></p></td><td><p>展开某个函数内部调用了哪些下游</p></td><td><p>理解「这个函数依赖了什么」</p></td></tr><tr><td><p><code>trace_chain</code></p></td><td><p>在两个符号之间搜索可能的调用链</p></td><td><p>追踪「从 A 到 B 的完整调用路径」</p></td></tr><tr><td><p><code>file_deps</code></p></td><td><p>分析某个文件的 import / 依赖关系</p></td><td><p>梳理模块间依赖</p></td></tr><tr><td><p><code>blast_radius</code></p></td><td><p>评估修改某个符号可能影响到的文件 / 符号范围</p></td><td><p>重构前评估风险——这是最强大的工具</p></td></tr></tbody></table>

典型使用场景：

- <strong>重构前评估风险</strong> ——「我想改 formatDate 的签名，影响面有多大？」模型调用 `blast_radius` \+ `find_references`，几秒给出精确影响范围；
- <strong>定位 Bug 根源</strong> ——「用户点击按钮为什么没响应？」从入口函数开始 `trace_callees`，一路下探；
- <strong>读懂陌生代码</strong> ——「帮我讲讲 AuthService.login 是怎么跑的」→ `read_symbol` \+ `trace_callees`；
- <strong>梳理调用关系</strong> ——「这个函数被哪些地方调用？」→ `trace_callers`，快速定位上游。

<strong>【与 Claude Code 的对比】</strong> Claude Code 依赖传统的文件读取和 grep/glob 搜索来理解代码结构，在大型仓库中需要读取大量文件，消耗大量上下文 token。AtomCode 的代码图谱通过符号索引直接定位，精准且省 token。这是 AtomCode 在大型项目场景下的核心优势。

<a id="c36-s49"></a>

### 四、Skills：最值得先学的扩展

Skills 是最容易上手的扩展方式。原理简单：在 skills 目录下创建一个文件夹，放一个 SKILL.md 文件，AtomCode 就会根据上下文自动加载里面的指令。

<strong>Skill 文件结构</strong>

```text
my-skills/
├── release/
│   └── SKILL.md
├── write-changelog/
│   └── SKILL.md
└── debug-flaky-test/
    ├── SKILL.md
    └── references/
        └── pattern-library.md
```

<strong>SKILL.md 格式</strong>

```markdown
---
name: release
description: 发布一个新的 release tag，更新 changelog，并打包
---

## 何时使用
当用户说"发布新版本"、"出一个 release"、"打 tag"时使用。

## 步骤
1. 通过 git log 确认上次发布以来的改动
2. 让用户确认 semver 版本号（patch/minor/major）
3. 更新 CHANGELOG.md 中新增条目
4. 运行 pnpm build 并确保构建通过
5. 创建 git tag v<version> 并写上发布说明
6. 运行 pnpm publish

## 规则
- 版本号必须符合 semver
- 不允许绕过测试，任何失败都必须先修复
```

<strong>Skill 目录</strong>

- 全局：`~/.atomcode/skills/`
- 项目级：当前工作目录及其上级的 `.atomcode/skills/`（如有）
- 项目级会覆盖同名全局 skill，方便在不同项目用同一个名字定义不同流程。

<strong>三种调用方式</strong>

<table><thead><tr><th><p>调用方式</p></th><th><p>操作</p></th><th><p>特点</p></th></tr></thead><tbody><tr><td><p>斜杠命令</p></td><td><p>输入 <code>/skill-name</code>，如 <code>/release</code></p></td><td><p>与内置命令一致，出现在补全菜单</p></td></tr><tr><td><p>$ 菜单</p></td><td><p>行首输入 <code>$</code>，弹出 skills 菜单，可直接带参数：<code>$brainstorming 帮我想登录方案</code></p></td><td><p>专门用来挑 skill，支持带参数</p></td></tr><tr><td><p>模型自动触发</p></td><td><p>模型调用 use_skill 工具，根据任务自动选择相关 skill</p></td><td><p>无需手动调用，智能匹配</p></td></tr></tbody></table>

<strong>/setup：自动推荐 Skills</strong>

AtomCode 独有功能：第一次执行 `/setup` 时，会扫描项目（语言、框架、已有 hook 等），联网检索并推荐适合该代码库的 atomcode skill 安装。

```text
/setup                  # 扫描项目并推荐 skill
/setup 重点关注测试      # 加 steering 文字引导推荐方向
```

<a id="c36-s50"></a>

### 五、Hooks：不是建议，是强制

Skills 有一个天然的局限：它本质上是对 AtomCode 的「建议」。AtomCode 会尽量遵守，但遵从率不是 100%，尤其在长对话后期，它可能就忘了。大多数场景下够用，但有些事情你需要 100% 的确定性。Hooks 就是为了解决这个问题。

<strong>【Hooks vs .atomcode.md：本质区别】</strong> `.atomcode.md` 是建议，Hooks 是强制执行。`.atomcode.md` 通过自然语言影响 AtomCode 的行为；Hooks 是平台层面的机制，在特定生命周期节点触发 Shell 脚本，AtomCode 无法跳过或忽略。

<strong>AtomCode 支持的 Hook 事件</strong>

<table><thead><tr><th><p>事件</p></th><th><p>触发时机</p></th><th><p>典型用途</p></th><th><p>CC 兼容性</p></th></tr></thead><tbody><tr><td><p><code>UserPromptSubmit</code></p></td><td><p>用户消息提交后，LLM 调用前</p></td><td><p>注入额外上下文 / 路由 / 阻断</p></td><td><p>兼容</p></td></tr><tr><td><p><code>PreToolUse</code></p></td><td><p>工具调用前</p></td><td><p>校验、阻断、改参</p></td><td><p>兼容</p></td></tr><tr><td><p><code>PostToolUse</code></p></td><td><p>工具调用后</p></td><td><p>审计、自动格式化、自动测试</p></td><td><p>兼容</p></td></tr><tr><td><p><code>SessionStart</code></p></td><td><p>session 启动</p></td><td><p>预热、记录</p></td><td><p>兼容</p></td></tr><tr><td><p><code>SessionEnd</code></p></td><td><p>session 结束</p></td><td><p>清理、归档</p></td><td><p>兼容</p></td></tr><tr><td><p><code>Notification</code></p></td><td><p>系统通知</p></td><td><p>转发外部告警通道</p></td><td><p>兼容</p></td></tr></tbody></table>

<strong>【与 Claude Code 的差异】</strong> AtomCode 当前不支持以下 CC 事件（会被静默跳过）：Stop、PreCompact、SubagentStop。如果你的 Hook 依赖这些事件，需要寻找替代方案。此外，多行 indent JSON 输出时，最后一行 JSON parser 可能失败，建议 hook 作者用单行 `json.dumps()` 输出。

<strong>实用案例</strong>

- <strong>案例 1：自动格式化。</strong> 每次 AtomCode 编辑文件后自动跑 eslint，不依赖 AtomCode「记住」要格式化。用 `PostToolUse` hook 实现。
- <strong>案例 2：自动批准低风险操作。</strong> 用 `PreToolUse` hook 把权限请求路由到一个脚本，脚本判断操作类型，低风险的（读文件、运行测试）自动批准，高风险的（删除文件、推送代码）仍然弹出确认。
- <strong>案例 3：注入上下文。</strong> 用 `UserPromptSubmit` hook 在用户消息后追加项目特定的额外上下文，让模型获得更多信息。

<a id="c36-s51"></a>

### 六、MCP：让 AtomCode 看到外面的世界

Skills 教 AtomCode 知识，Hooks 保证执行确定性，但它们都在 AtomCode 的内部世界运作。如果你需要 AtomCode 直接查数据库、调 API、读取设计稿，就需要 MCP。

MCP（Model Context Protocol）是一个开放协议，把外部程序或 HTTP 服务的「工具」接到 AtomCode，让模型像调用内置工具一样使用它们。AtomCode 从 v4.20.4 起内置 MCP 客户端，直接复用 Cursor 等同样使用 `mcpServers` 配置块的生态。

<strong>两个配置位置</strong>

<table><thead><tr><th><p>路径</p></th><th><p>作用域</p></th></tr></thead><tbody><tr><td><p><code>&lt;项目根&gt;/.mcp.json</code></p></td><td><p>仅当前项目可见，适合跟代码同仓库</p></td></tr><tr><td><p><code>~/.atomcode/mcp.json</code></p></td><td><p>用户全局，跨所有项目共享</p></td></tr></tbody></table>

<strong>配置示例</strong>

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
      "timeout_ms": 10000
    },
    "github": {
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_TOKEN}"
      }
    }
  }
}
```

<strong>一行命令添加 server</strong>

```bash
atomcode mcp add playwright npx @playwright/mcp@latest            # 项目级
atomcode mcp add playwright npx @playwright/mcp@latest --global   # 用户全局
```

<strong>权限审批</strong>

MCP 工具默认每次调用都需要确认，因为远端是外部不可信代码：

- 按 `Y` —— 单次允许；
- 按 `A` —— 在当前会话内放行该工具（下次启动后失效，不会持久化）；
- 按 `N` —— 拒绝本次调用。

<strong>【当前限制（与 CC 对比）】</strong> AtomCode MCP 当前仅支持 tools 能力；尚未实现 resources / prompts / OAuth / roots / elicitation。Claude Code 的 MCP 支持更全面（OAuth、resources、prompts 等）。已在用 Cursor 配 MCP server 的话，常见 command / url 类型配置通常可复用。工具结果只取 text 类型 content 块，image / resource 块当前忽略。

<a id="c36-s52"></a>

### 七、Plugin 系统：打包好的扩展包

Skills、Hooks、MCP 可以各自独立使用，但组合起来才真正厉害。Plugin 就是这种组合的打包形式，通过 git 仓库分发。一行 `/plugin install` 就能把别人写好的工作流装到 AtomCode 里，装完即用。

<strong>【与 Claude Code 生态兼容】</strong> AtomCode 的 plugin 协议与 Claude Code 兼容！CC 生态的 plugin 仓库可以直接安装运行。marketplace 根目录的 `.claude-plugin/marketplace.json` 或 `.atomcode-plugin/marketplace.json` 都可以识别。这意味着你可以直接复用 Claude Code 社区积累的插件生态。

<strong>Plugin 管理命令</strong>

<table><thead><tr><th><p>命令</p></th><th><p>作用</p></th></tr></thead><tbody><tr><td><p><code>/plugin</code></p></td><td><p>打开交互式插件管理器，浏览 marketplace、安装 / 卸载</p></td></tr><tr><td><p><code>/plugin marketplace add &lt;url&gt;</code></p></td><td><p>克隆 git 仓库并注册为 marketplace</p></td></tr><tr><td><p><code>/plugin install &lt;plugin&gt;@&lt;marketplace&gt;</code></p></td><td><p>从指定 marketplace 安装一个插件</p></td></tr><tr><td><p><code>/plugin uninstall &lt;plugin&gt;@&lt;marketplace&gt;</code></p></td><td><p>卸载已安装的插件</p></td></tr><tr><td><p><code>/plugin list</code></p></td><td><p>列出本地已安装的所有插件</p></td></tr><tr><td><p><code>/plugin reload</code></p></td><td><p>重新加载所有插件</p></td></tr></tbody></table>

<strong>Plugin 可以包含的资产</strong>

- <strong>Skill</strong> —— 带 plugin-name 命名空间，避免冲突；
- <strong>命令</strong> —— 与 skill 类似，可包含内联 Bash 脚本预计算信息；
- <strong>Hook</strong> —— 按事件触发，立即激活。

<strong>实战：安装昇腾插件</strong>

```text
/plugin marketplace add https://gitcode.com/gmq123/ascend-model-agent-plugin
# > marketplace `ascend-model-agent-plugin` added at 7a59537 (1 plugins)

/plugin install ascend-model-agent-plugin@ascend-model-agent-plugin
# > installed — 23 skills loaded, 5 skipped

# 装完后，plugin 贡献的 skill 出现在 / 菜单，带前缀：
# /ascend-model-agent-plugin:ascend-model-verification
```

<a id="c36-s53"></a>

### 八、三种扩展机制的协作

实际项目中，多种机制经常协同工作。一个完整的例子：

假设你的团队有这样一个工作流：收到 bug 报告 → 定位问题 → 修复 → 跑测试 → 提交 PR → 通知相关人。

- <strong>MCP（Slack）</strong> —— 让 AtomCode 收到 bug 报告并能回复修复结果；
- <strong>Skill（fix-issue）</strong> —— 指导 AtomCode 按标准流程定位和修复问题；
- <strong>代码图谱（trace&#95;callers + blast&#95;radius）</strong> —— 精准定位 bug 根源和影响范围；
- <strong>Hook（PostToolUse）</strong> —— 确保每次修改后都自动跑测试和格式化；
- <strong>Plugin</strong> —— 把以上 skill + hook 打包，团队成员一键安装。

单独用任何一个都有价值，组合起来就是一个完整的自动化 bug 修复流水线。

<a id="c36-s54"></a>

## §08 多 Agent 协作

AtomCode 最被低估的能力不是它写代码有多快，而是它可以同时跑很多个。学会并行之后，你的工作模式会从「一个人配一个 AI」变成「一个人指挥一支 AI 团队」。

> <strong>重要说明</strong>：本章内容基于 AtomCode V4.25.9 的实际功能编写。原始 v0.0.1 文档中本章大量内容引自《Claude Code 从入门到精通》，其中 Agent Teams、Coordinator Mode、Remote Control、`/schedule`、`/loop` 等是 Claude Code 的功能，AtomCode 目前尚不支持。本章已根据 AtomCode 实际能力重写。

<a id="c36-s55"></a>

### 一、为什么需要并行

AtomCode 的工作模式是「你给任务 → AtomCode 花几分钟执行 → 你 review 结果 → 给下一个任务」。中间有大量等待时间。只开一个 session，大部分时间你在等 AtomCode 干活。

开多个 session，你 review 第一个的时候其他几个还在跑，等待时间几乎降到零。关键前提是：<strong>每个 session 需要在独立的代码环境中运行</strong>，否则它们会互相覆盖文件，制造冲突。

<a id="c36-s56"></a>

### 二、AtomCode 的并行方案 vs Claude Code

<table><thead><tr><th><p>并行方式</p></th><th><p>Claude Code</p></th><th><p>AtomCode</p></th></tr></thead><tbody><tr><td><p>Git Worktree 隔离</p></td><td><p>原生支持，自动创建 worktree</p></td><td><p><code>/worktree create</code> / <code>list</code> / <code>done</code> / <code>cleanup</code></p></td></tr><tr><td><p>后台会话</p></td><td><p>Subagents（独立上下文）</p></td><td><p><code>/bg</code> 16 个并行后台槽位，模型在后台继续工作</p></td></tr><tr><td><p>一次性后台任务</p></td><td><p>通过 subagent 实现</p></td><td><p><code>/background &lt;任务&gt;</code>，只读工具子集</p></td></tr><tr><td><p>Agent Teams</p></td><td><p>支持（Writer / Reviewer 等模式）</p></td><td><p>暂不支持</p></td></tr><tr><td><p>Coordinator Mode</p></td><td><p>支持（四阶段协调）</p></td><td><p>暂不支持</p></td></tr><tr><td><p>Fan-out 批处理</p></td><td><p><code>/batch</code> 命令交互式规划</p></td><td><p>非交互 <code>-p</code> 模式 + shell 循环</p></td></tr><tr><td><p>远程控制</p></td><td><p>Remote Control + claude.ai/code</p></td><td><p><code>/webui lan</code> 局域网访问</p></td></tr><tr><td><p>定时任务</p></td><td><p><code>/schedule</code> 云端定时</p></td><td><p>暂不支持（可用系统 crontab + <code>atomcode -p</code> 替代）</p></td></tr><tr><td><p>长时间运行</p></td><td><p><code>/loop</code> 本地最多 3 天</p></td><td><p><code>/goal</code> 自动循环（无固定时限）</p></td></tr></tbody></table>

<a id="c36-s57"></a>

### 三、Git Worktrees：并行的基础设施

Git Worktree 允许你从同一个仓库创建多个工作目录，每个工作目录在不同的分支上，文件系统完全隔离。AtomCode 对 worktree 做了原生支持：

<table><thead><tr><th><p>命令</p></th><th><p>作用</p></th></tr></thead><tbody><tr><td><p><code>/worktree create</code></p></td><td><p>在新分支上拉一份独立 worktree，文件系统完全隔离</p></td></tr><tr><td><p><code>/worktree list</code></p></td><td><p>查看现有 worktree</p></td></tr><tr><td><p><code>/worktree done</code></p></td><td><p>把 worktree 改动 squash 回主分支</p></td></tr><tr><td><p><code>/worktree cleanup</code></p></td><td><p>清理已完成的 worktree</p></td></tr></tbody></table>

典型场景：你想同时开发三个功能，每个功能在自己的分支上。用 `/worktree create` 创建三个隔离的工作目录，分别启动 AtomCode 会话，互不干扰。完成后用 `/worktree done` 把改动合并回主分支。

<a id="c36-s58"></a>

### 四、/bg：后台会话（AtomCode 核心并行能力）

这是 AtomCode 最实用的并行功能。`/bg` 把当前会话放到后台、打开新的前台会话，随时可以切回去。最多支持 16 个并行后台槽位。

<strong>【关键特性：后台不只是「挂起」】</strong> `/bg` 后台并不只是「挂起」——模型真的会在后台继续干活！你把一个耗时任务放到后台后，可以切到新前台做别的事。后台任务跑完后状态切到「已完成」，`/bg <N>` 切回去直接拿到结果。

<table><thead><tr><th><p>命令</p></th><th><p>作用</p></th></tr></thead><tbody><tr><td><p><code>/bg</code></p></td><td><p>把当前会话送到后台，打开新的前台</p></td></tr><tr><td><p><code>/bg list</code>（别名 <code>/bg ls</code>）</p></td><td><p>列出所有后台会话：编号、ID、状态、创建时间、摘要</p></td></tr><tr><td><p><code>/bg &lt;N&gt;</code></p></td><td><p>恢复第 N 号后台为前台（当前前台会被换下到后台）</p></td></tr><tr><td><p><code>/bg drop &lt;N&gt;</code></p></td><td><p>丢弃第 N 号后台会话</p></td></tr><tr><td><p><code>/bg help</code></p></td><td><p>显示内置帮助</p></td></tr></tbody></table>

<strong>后台会话状态</strong>

- <strong>运行中</strong> —— 模型还在执行，工具调用 / 输出在后台继续推进；
- <strong>空闲</strong> —— 模型轮次跑完，等你的下一条 prompt；
- <strong>已完成</strong> —— 会话已经显式结束；
- <strong>已取消 / 错误</strong> —— 被中断或后台运行时出错。

典型场景：主前台正在调试 A 模块，模型一边改一边跑 `cargo check`（耗时）。这时想到要顺便重构 B 模块——直接 `/bg` 切到新前台开始 B；A 那边的 build 在后台跑完状态切到「已完成」，`/bg 1` 切回去拿结果。

<a id="c36-s59"></a>

### 五、/background：一次性后台派发

如果不想专门切换前后台、只是「顺手让它跑一下查个东西」，用 `/background` 兼容入口：

```text
/background 列出 src 下未使用的依赖
```

会在一个 `/bg` 槽位里启动一次性任务（默认配置为只读工具子集，不污染主对话上下文）。跑完后用 `/bg list` 看状态，`/bg <N>` 切过去读结果，`/bg drop <N>` 丢弃。

<strong>【/bg vs /background 的区别】</strong> `/bg` —— 把当前完整会话挪到后台，打开新前台。适合需要长期跟进的多任务并行。`/background` —— 直接派发一个一次性任务到后台槽位，不切换前台。适合「顺手查个东西」的轻探索。

<a id="c36-s60"></a>

### 六、非交互批处理：-p 模式

AtomCode 支持非交互模式，用 `-p` 参数传入 prompt，适合在脚本中调用和批量处理：

```bash
# 单次执行
atomcode -p "简要介绍一下这个仓库"

# 批量处理：配合 shell 循环
for file in src/components/*.tsx; do
  atomcode -p "给 $file 添加 TypeScript 类型注解" &
done
wait
```

注意末尾的 `&`：这让每个 AtomCode 实例在后台并行运行。如果有 50 个文件要迁移，50 个 AtomCode 同时跑，可能几分钟就完成了原本需要一整天的工作。

<strong>非交互模式实用参数</strong>

<table><thead><tr><th><p>参数</p></th><th><p>作用</p></th></tr></thead><tbody><tr><td><p><code>-p</code> / <code>--prompt TEXT</code></p></td><td><p>非交互模式，单次执行并把回复写到 stdout</p></td></tr><tr><td><p><code>--prompt-file PATH</code></p></td><td><p>从文件读取 prompt（适合长文本，与 <code>-p</code> 互斥）</p></td></tr><tr><td><p><code>-v</code> / <code>--verbose</code></p></td><td><p>非交互模式下把工具调用、token 用量等信息打到 stderr</p></td></tr><tr><td><p><code>--max-turns N</code></p></td><td><p>强制限制 Agent 循环的最大轮数，防止无限跑下去</p></td></tr><tr><td><p><code>--disable-tools LIST</code></p></td><td><p>逗号分隔，禁用某些工具。如 <code>--disable-tools bash,web_fetch</code></p></td></tr><tr><td><p><code>-y</code> / <code>--dangerously-skip-permissions</code></p></td><td><p>跳过所有权限确认，自动批准所有工具调用</p></td></tr></tbody></table>

<a id="c36-s61"></a>

### 七、WebUI 多端协作：/webui + /sync

AtomCode 内置了 WebUI 功能，这是 Claude Code 所不具备的差异化能力。通过 `/webui` 启动浏览器界面，可以实现多端实时协作：

```text
/webui      # 启动浏览器界面，自动打开浏览器（127.0.0.1:13457）
/webui lan  # 暴露到局域网（等价于 --host 0.0.0.0）
/sync       # 把当前 TUI 接入 webui 会话，两端实时双向同步
/sync off   # 退出同步
```

WebUI 支持多个浏览器 / 终端同时围观同一会话。你可以在一台电脑上用 TUI 操作，在另一台电脑的浏览器上实时查看。配合蒲公英虚拟 IP 还可以远程访问。

<a id="c36-s62"></a>

### 八、/goal：自动循环

AtomCode 独有功能：设定一个完成目标，让 agent 自动循环——一轮接一轮——直到目标达成。这相当于一个简化的「无人值守」模式：

```text
/goal 所有测试通过且无 TypeScript 编译错误
# AtomCode 开始自动循环：改代码 → 跑测试 → 有错误 → 继续改 → 再跑测试 → ...
# 你可以去做别的事，它自己一轮一轮推进

/goal        # 查看当前目标与已运行轮数
/goal clear  # 停止自动循环
```

适合场景：修复所有测试直到通过、重构直到代码审查无问题、批量修复 lint 错误等。你设定目标后可以切换到其他会话做事，AtomCode 会在后台持续推进。

<a id="c36-s63"></a>

### 九、AtomCode 目前没有的高级功能

诚实地说，以下 Claude Code 功能 AtomCode 目前尚不支持，但有自己的替代方案：

<table><thead><tr><th><p>CC 功能</p></th><th><p>说明</p></th><th><p>AtomCode 替代方案</p></th></tr></thead><tbody><tr><td><p>Agent Teams</p></td><td><p>多 session 互相通信、协调分工，Writer / Reviewer 等模式</p></td><td><p>用 <code>/bg</code> 多会话 + 手动协调，或多个终端窗口</p></td></tr><tr><td><p>Coordinator Mode</p></td><td><p>四阶段自动协调：Research → Synthesis → Implementation → Verification</p></td><td><p>用 <code>/plan</code> + <code>/build</code> 手动分阶段，<code>/goal</code> 自动迭代</p></td></tr><tr><td><p>Fan-out 批处理</p></td><td><p><code>/batch</code> 交互式规划批量任务，自动启动数十个 agent 并行</p></td><td><p>用 <code>-p</code> 非交互模式 + shell 循环批处理</p></td></tr><tr><td><p>Remote Control</p></td><td><p>手机远程创建和管理本地 session</p></td><td><p><code>/webui lan</code> 局域网访问 + 手机浏览器</p></td></tr><tr><td><p><code>/schedule</code></p></td><td><p>云端定时任务，电脑关机也照跑</p></td><td><p>系统 crontab + <code>atomcode -p</code></p></td></tr><tr><td><p><code>/loop</code></p></td><td><p>本地长时间无人值守运行最多 3 天</p></td><td><p><code>/goal</code> 自动循环（无固定时限）</p></td></tr><tr><td><p>Subagents</p></td><td><p>主 session 调用专家 agent，独立上下文</p></td><td><p><code>/background</code> 一次性后台任务（只读工具子集）</p></td></tr></tbody></table>

<strong>【AtomCode 的迭代速度】</strong> AtomCode 是 100% AI 生成的开源项目，迭代极快。上述不支持的功能可能在后续版本中加入。建议定期用 `/upgrade` 更新到最新版本，并关注官方文档（[https://atomcode.atomgit.com/docs/](<https://atomcode.atomgit.com/docs/>)）的更新。

<a id="c36-s64"></a>

### 十、实用经验

- <strong>从 2 个 session 开始就好。</strong> 不用一上来就开 10 个。先习惯在两个之间切换：一个做主任务，另一个做辅助的（写测试、做 code review）。等觉得游刃有余了再加。
- <strong>每个 session 给一个明确的角色。</strong> 不要让所有 session 都做「随便什么任务」。给它们分工：这个负责前端、那个负责后端、那个专门跑测试。角色越清晰，你管理起来越轻松。
- <strong>用 git 分支隔离一切。</strong> 每个 session 在自己的分支上工作，通过 `/worktree` 或手动 git 分支管理。千万不要让多个 session 操作同一个分支，冲突解到怀疑人生。
- <strong>定期扫一眼，不要完全放羊。</strong> 并行不等于不管。每隔 15-20 分钟看看各个 session 的进度（`/bg list`），及时纠偏。一个 session 跑偏了及时停掉，比让它跑完再返工划算得多。
- <strong>用 /webui 同步监控。</strong> 开一个 `/webui`，在浏览器里实时看执行过程，比在终端来回切更高效。

<a id="c36-s65"></a>

## §09 从零构建一个完整产品

我们要做的是一个 Web 应用：用户粘贴一篇文章的 URL，系统自动抓取内容、调用 AI API 生成摘要，并把历史记录存下来。

<a id="c36-s66"></a>

### 为什么选这个项目

- 技术栈覆盖面刚好：前端（Next.js 页面）、后端（API 路由）、数据库（SQLite）、外部 API 调用，四层都有；
- 足够展示 AtomCode 在不同场景下的能力，又不至于复杂到写不完；
- 每一层可以独立开发，正好适合用 AtomCode 的多会话并行；
- 你做完能自己用——一个你自己会用的产品，做起来动力完全不同。

<a id="c36-s67"></a>

### 阶段一：需求分析和规划（/plan 模式）

打开终端，进入你想存放项目的目录，输入 `/plan` 切到 Plan 模式。这一步非常关键，首先进行设计：

```text
我要做一个 AI 文章摘要工具，Web 应用。核心功能：
- 用户输入文章 URL
- 系统抓取文章内容
- 调用 AI API 生成 3 种不同长度的摘要（一句话 / 短摘要 / 详细摘要）
- 存储历史记录，用户可以回看

技术要求：Next.js 15 App Router / SQLite + Drizzle ORM / Tailwind CSS

请分析需求，给出完整的技术方案和项目结构。
```

AtomCode 在 Plan 模式下会输出一份详细的方案。不要急着说「开始做」。仔细看方案，挑出你觉得不对的地方。这种追问很重要——AI 擅长生成「看起来合理」的方案，但细节上可能有坑。你的判断力在这一步最有价值。

确认方案后，让 AtomCode 生成一份 `.atomcode.md`（注意首先要切回 `/build` 状态）：

```text
基于我们讨论的方案，帮我写一份 .atomcode.md。要求：
- 项目根目录一份全局的
- src/app/ 下前端相关的
- src/lib/ 下后端和数据库相关的
- 说清楚技术栈、代码风格、文件命名规范
```

<strong>【.atomcode.md 是 AtomCode 的地图】</strong> 在多会话并行的时候，每个会话都会读自己工作目录下的 `.atomcode.md` 来理解上下文。现在花时间把它写好，后面能省很多事。注意 AtomCode 也兼容 AGENTS.md 和 CLAUDE.md 格式。

<a id="c36-s68"></a>

### 阶段二：基础搭建（/build 模式）

方案确认了，`.atomcode.md` 也准备好了，现在让 AtomCode 动手。给它第一个任务：初始化项目、安装依赖、创建基本目录结构、配置 Drizzle 和数据库 Schema、写最简单的首页。

几个注意事项：

- <strong>让它跑完再看，不要中途打断。</strong> 项目初始化是一连串有依赖关系的操作，打断容易导致半成品状态。
- <strong>跑完之后验证。</strong> 手动执行 `npm run dev`，自己打开浏览器看一眼。
- <strong>立刻手动提交一次：</strong> `git init && git add . && git commit -m "init: project scaffold"`
- <strong>每个里程碑都 commit。</strong> 这不是洁癖，是保险。后面多个会话并行改代码，万一改崩了，你要能回退到一个干净的状态。

<strong>【经验之谈】</strong> 测试和 git 操作建议自己使用命令行执行，而不是让 AtomCode 代劳。这是保证项目可控性的关键。

<a id="c36-s69"></a>

### 阶段三：核心内容开发（多会话并行）

基础搭建完成后，可以开始多会话并行开发。三个 Agent 分别负责前端、后端、数据库：

<strong>Agent 1 · 前端 UI 设计</strong>

```text
基于 .atomcode.md 中的设计方案，实现前端所有页面：首页（URL 输入框、提交按钮、加载动画、摘要结果展示）、历史记录页（摘要列表、搜索过滤）、布局组件。用 Tailwind CSS，风格简洁干净。不需要实际调用 API，用 mock 数据把界面先做出来。
```

<strong>Agent 2 · 后端 API 设计</strong>

```text
实现三个 API 路由：POST /api/summarize（接收 URL、抓取文章、调用 AI 生成三档摘要、存入数据库）、GET /api/history（分页返回历史记录）、GET /api/history/:id（查询单条详情）。AI 密钥从环境变量读取。
```

<strong>Agent 3 · 数据库</strong>

```text
实现数据库层：Schema 定义（summaries 表）、数据库连接（Drizzle 实例）、CRUD 工具函数、迁移脚本、单元测试。
```

<strong>【接口约定是关键】</strong> 在 `.atomcode.md` 里把所有接口约定写清楚。字段名、类型、返回格式，越具体越好。这 10 分钟的约定能省后面 1 小时的对齐。这里的提示词体现了很强的实际业务能力，并不是简简单单设计就能够写出来的。

<a id="c36-s70"></a>

### 阶段四：集成和测试（/review + 实际数据）

在正式开展使用之前，输入 `/review` 开展代码检测。逐个修复，每修一个问题验证是否影响其他地方。等所有 TypeScript 编译错误都消除了，再做一次完整测试：

- 启动 dev server；
- 调用 `POST /api/summarize`，传入一个真实的文章 URL；
- 检查返回的摘要是否正确；
- 调用 `GET /api/history`，检查是否有刚才的记录；
- 检查前端页面能否正常展示。

测试通过后，commit 并打 tag：

```bash
git add . && git commit -m "feat: integrate all modules"
git tag v0.2.0
```

<a id="c36-s71"></a>

### 阶段五：优化和部署

- <strong>写 README.md</strong>：项目简介、安装和运行步骤、环境变量配置、部署到 Vercel 的步骤；
- <strong>优化错误处理</strong>：统一错误响应格式、前端错误提示 UI、文章抓取失败降级方案、API 调用超时重试；
- <strong>添加 SEO 和性能优化</strong>：页面 metadata、OG 图片、SSG、图片和字体优化。

这里可以输入 `/webui` 查看整个操作的过程，在浏览器中集中展现。

<a id="c36-s72"></a>

## §10 心智模型与持续进化

在上面这些例子中，容易被忽视的，是镶嵌在关键字上下文中的智慧——对于项目发挥作用起到了关键作用。这些智慧，来自于工程师的经验和判断，而不仅仅是工具本身的能力。

<a id="c36-s73"></a>

### 一、三层心智模型

和 AtomCode 的协作可以分为三个层次，投入精力的回报特征完全不同：

<table><thead><tr><th><p>层次</p></th><th><p>含义</p></th><th><p>投入方式</p></th><th><p>回报特征</p></th></tr></thead><tbody><tr><td><p>Prompt 层</p></td><td><p>你在终端里输入的每句话</p></td><td><p>每次对话都要重新投入</p></td><td><p>一次性回报</p></td></tr><tr><td><p>Context 层</p></td><td><p>.atomcode.md、文件结构、git 历史等 AtomCode 自动读取的信息</p></td><td><p>写一次 .atomcode.md，持续生效</p></td><td><p>复利回报</p></td></tr><tr><td><p>Harness 层</p></td><td><p>Skills、Hooks、MCP、代码图谱、/bg 并行等自动化环境</p></td><td><p>搭一次自动化流程，永久运行</p></td><td><p>指数回报</p></td></tr></tbody></table>

<strong>【关键结论】</strong> 把时间花在构建 Context 和 Harness 上，而不是优化 Prompt。初学者把精力全花在 Prompt 层——每次对话都从零开始描述需求。高手把信息沉淀到 Context 层（写好 .atomcode.md），把重复劳动交给 Harness 层（Skills / Hooks / MCP）。用三个月养出来的 .atomcode.md + Skills 集合，是你最有价值的 AI 资产。

<a id="c36-s74"></a>

### 二、AtomCode 的三层优势

AtomCode 在三层模型上都有自己的独特优势：

<strong>Prompt 层优势：多模型 + 视觉预处理器</strong>

- 支持任意 OpenAI 兼容模型——按任务选模型：复杂推理用 DeepSeek-R1，日常开发用 DeepSeek-V4，代码生成用 Qwen3；
- `/think` 和 `/effort` 控制——针对不同模型的差异化思考控制；
- 视觉预处理器——纯文本模型也能处理图片，不必绑定视觉模型。

<strong>Context 层优势：代码图谱 + 多格式兼容</strong>

- 代码图谱 8 个工具——精准定位符号，大幅减少上下文消耗；
- .atomcode.md 兼容 AGENTS.md 和 CLAUDE.md——一套指令文件多工具共享；
- `/context` 实时查看预算——主动管理上下文窗口。

<strong>Harness 层优势：/bg 并行 + /goal 自动循环 + WebUI</strong>

- `/bg` 16 槽位后台会话——模型在后台继续工作，不阻塞前台；
- `/goal` 自动循环——设定目标让 agent 自己迭代；
- `/webui` \+ `/sync`——多端实时协作；
- Plugin 兼容 CC 生态——直接复用 Claude Code 社区插件。

<a id="c36-s75"></a>

### 三、身份转变

使用 AtomCode 的过程，你的身份会经历一次根本性转变：从「写代码的人」变成「给指令的人」。

<table><thead><tr><th><p>维度</p></th><th><p>传统工程师</p></th><th><p>AtomCode 时代的工程师</p></th></tr></thead><tbody><tr><td><p>核心能力</p></td><td><p>语法熟练度、框架 API 记忆、手动调试</p></td><td><p>需求拆解能力、架构判断力、输出质量评审、产品品味</p></td></tr><tr><td><p>日常工作</p></td><td><p>写代码、改 bug、写测试</p></td><td><p>定义要做什么、判断做得对不对、迭代改进</p></td></tr><tr><td><p>价值来源</p></td><td><p>代码实现的质量和速度</p></td><td><p>需求定义的准确性和产品方向的判断</p></td></tr><tr><td><p>协作对象</p></td><td><p>其他工程师</p></td><td><p>AI Agent 团队（多个 /bg 会话）</p></td></tr></tbody></table>

<a id="c36-s76"></a>

### 四、能力转移

AI 不会让工程师失业，但会改变工程师需要的能力。从 AtomCode 的使用经验看：

- <strong>语法熟练度 → 需求拆解能力。</strong> 你不需要记住每个 API 的参数，但需要能把模糊的需求拆成具体的、可执行的步骤。
- <strong>框架 API 记忆 → 架构判断力。</strong> AtomCode 能写代码，但选择什么架构、用什么模式，仍然需要人来判断。
- <strong>手动调试 → 输出质量评审。</strong> AtomCode 一小时能写 2000 行代码，你的任务变成了判断这些代码对不对、好不好。
- <strong>代码模板 → 产品品味。</strong> 当实现不再是瓶颈，决定做什么、什么值得做，变得更重要。

<a id="c36-s77"></a>

### 五、验证比开发更重要

AI 一小时能写 2000 行代码，如果不验证，问题会在后面以更大成本爆发。每完成一个模块立刻验证：

- 用 `/review` 做代码审查——AtomCode 内置的代码审查工具；
- 用 `/plan` 先讨论方案——把纠结放在 Plan 阶段解决完；
- 每一轮改动都实际运行一次——不要「看着像对的就接受」；
- 用代码图谱的 `blast_radius` 评估修改影响——避免意外破坏。

<a id="c36-s78"></a>

### 六、产品感知是最大杠杆

AI 能让执行速度提升 10 倍，但方向错了只是 10 倍速度走向错误。决定产品好不好的，从来不是代码有多精妙，而是需求定义有多准确。

在 AtomCode 的实践中，那些成功的项目——无论是 AI 新闻聚合器还是文章摘要工具——成功的关键不是代码写得多好，而是：

- 需求描述足够具体（文件路径、技术选型、验证方式）；
- 方案讨论足够充分（`/plan` 模式来回对齐）；
- 接口约定足够清晰（.atomcode.md 写到位）；
- 迭代节奏足够紧凑（每步验证、每里程碑 commit）。

这些都是产品感知和工程判断的体现，而不是代码能力的体现。

<a id="c36-s79"></a>

### 七、持续进化

AtomCode 本身也在持续进化。它是 100% AI 生成的开源项目，迭代极快，不断汲取 Claude Code 和 Codex 的最新技术。你能做的：

- 定期 `/upgrade` 更新到最新版本；
- 关注官方文档（[https://atomcode.atomgit.com/docs/](<https://atomcode.atomgit.com/docs/>)）的更新；
- 持续迭代你的 .atomcode.md——每次 AtomCode 犯错就加一条规则；
- 把重复工作流写成 Skill——超过两次的操作就值得封装；
- 参与社区——终端内直接运行 `/issue` 即可快速创建 issue。

让我们举起酒杯，祝福那些将智慧镶嵌在代码中的程序员们！

<a id="c36-s80"></a>

## 附录 A：能够运行的代码是最好的学习资料

——为什么要做这个手册

其实这个手册，只是在看过花叔的《Claude Code 从入门到精通》后，发现 AtomCode 并没有相关的材料，所以基于官方文档和自己的一点点经验进行的拙劣的模仿。当然，在这个过程中，我是首要收益者，收获了很多之前不是很清楚的知识，而且也欣然发现 AtomCode 在快速迭代，很多功能在完善和补充。

这里要额外说的，是方法论，其实也是一直以来我总结的经验：<strong>能够运行的代码是最好的学习资料。</strong>

以前在研究使用 OpenCV 的时候，就会发现把书上的例子跑一遍，就会有很多具体的收获。当遇到具体的现实的问题的时候，便会有很多迁移的灵感；这些灵感聚沙成塔、集腋成裘，变成了系统的方法，或者叫做经验。那么到了今天，仍然是这样，程序员的经验和灵感、判断仍然是最重要的，而这些点滴收获，只能通过手搓具体的例子，让知识首先在脑子里面融会贯通，然后通过外力放大。

其实，如果进一步看，在本书的例子中，关于项目构建的提示词都是非常具体且具有指向性的——这也是软件的构建过程能够顺利的根本原因。那么这些提示词至少是在工程师的判断下产出的，而产出的来源就是曾经写过的可以运行的代码。

让我们举起酒杯，祝福那些将智慧镶嵌在代码中的程序员们！

<strong>参考资料</strong>

- AtomCode 官方文档：[https://atomcode.atomgit.com/docs/zh/index.html](<https://atomcode.atomgit.com/docs/zh/index.html>)
- 《Claude Code 从入门到精通》—— 花叔
- AtomCode 开源仓库：[https://atomgit.com/atomgit_atomcode/atomcode](<https://atomgit.com/atomgit_atomcode/atomcode>)

<a id="c36-s81"></a>

## 附录 B：Claude Code vs AtomCode 全面对比

本附录基于 Claude Code v2.1.88+ 和 AtomCode V4.25.9 的实际功能，从多个维度进行全面对比。

<a id="c36-s82"></a>

### 一、基本信息对比

<table><thead><tr><th><p>维度</p></th><th><p>Claude Code</p></th><th><p>AtomCode</p></th></tr></thead><tbody><tr><td><p>开源协议</p></td><td><p>闭源商业产品（Anthropic）</p></td><td><p>开源 MIT，100% AI 生成</p></td></tr><tr><td><p>开发语言</p></td><td><p>TypeScript（严格模式）</p></td><td><p>Rust 1.75+</p></td></tr><tr><td><p>运行时</p></td><td><p>Bun（非 Node.js）</p></td><td><p>原生编译二进制</p></td></tr><tr><td><p>UI 框架</p></td><td><p>React + Ink（终端 React）</p></td><td><p>Rust TUI</p></td></tr><tr><td><p>Schema 验证</p></td><td><p>Zod v4</p></td><td><p>Rust 类型系统</p></td></tr><tr><td><p>版本</p></td><td><p>v2.1.88+</p></td><td><p>V4.25.9+</p></td></tr><tr><td><p>平台</p></td><td><p>macOS / Linux / Windows</p></td><td><p>macOS / Linux / Windows / HarmonyOS PC</p></td></tr><tr><td><p>安装方式</p></td><td><p>npm / Homebrew</p></td><td><p>curl 脚本 / npm / Homebrew / 源码</p></td></tr><tr><td><p>构建代码规模</p></td><td><p>~51 万行 TypeScript</p></td><td><p>未公开（Rust）</p></td></tr><tr><td><p>定价</p></td><td><p>Claude 订阅 / API 计费</p></td><td><p>免费开源 + CodingPlan 免费额度</p></td></tr><tr><td><p>IDE 插件</p></td><td><p>无原生 IDE 插件</p></td><td><p>VS Code + JetBrains（侧边栏聊天、右键菜单、Diff 预览）</p></td></tr></tbody></table>

<a id="c36-s83"></a>

### 二、模型支持对比

<table><thead><tr><th><p>维度</p></th><th><p>Claude Code</p></th><th><p>AtomCode</p></th><th><p></p></th><th><p></p></th></tr></thead><tbody><tr><td><p>支持模型</p></td><td><p>仅 Claude 系列（Sonnet / Opus / Haiku）</p></td><td><p>任意 OpenAI 兼容 API（DeepSeek / Qwen / GLM / Ollama 等）</p></td><td><p></p></td><td><p></p></td></tr><tr><td><p>多 Provider</p></td><td><p>不支持</p></td><td><p>支持，可同时配置多个 provider 随时切换</p></td><td><p></p></td><td><p></p></td></tr><tr><td><p>本地模型</p></td><td><p>不支持</p></td><td><p>支持 Ollama 本地部署</p></td><td><p></p></td><td><p></p></td></tr><tr><td><p>视觉能力</p></td><td><p>Claude 原生视觉</p></td><td><p>视觉预处理器（VL preprocessor，非视觉模型也能处理图片）</p></td><td><p></p></td><td><p></p></td></tr><tr><td><p>免费额度</p></td><td><p>有限免费试用</p></td><td><p>CodingPlan 提供 DeepSeek-V4-Flash + Qwen3-VL 免费额度</p></td><td><p></p></td><td><p></p></td></tr><tr><td><p>国产模型</p></td><td><p>不支持</p></td><td><p>原生支持 DeepSeek / Qwen / GLM 等国产模型</p></td><td><p></p></td><td><p></p></td></tr><tr><td><p>思考控制</p></td><td><p>通过参数控制</p></td><td><p><code>/think on</code> / <code>off</code>、<code>/think budget</code>、`/effort &lt;high\</p></td><td><p>max\</p></td><td><p>off&gt;`</p></td></tr></tbody></table>

<a id="c36-s84"></a>

### 三、核心工具对比

<table><thead><tr><th><p>工具类别</p></th><th><p>Claude Code</p></th><th><p>AtomCode</p></th></tr></thead><tbody><tr><td><p>文件操作</p></td><td><p>Read / Write / Edit / Bash / Grep / Glob</p></td><td><p>read_file / write_file / edit_file / search_replace / bash / grep / glob / list_directory / change_dir（9 个）</p></td></tr><tr><td><p>代码图谱</p></td><td><p>无</p></td><td><p>8 个：list_symbols / read_symbol / find_references / trace_callers / trace_callees / trace_chain / file_deps / blast_radius</p></td></tr><tr><td><p>Web 工具</p></td><td><p>WebFetch / WebSearch</p></td><td><p>web_search / web_fetch（2 个）</p></td></tr><tr><td><p>自动化</p></td><td><p>通过 Skills / Hooks 实现</p></td><td><p>auto_fix（自动修复 lint / typecheck）+ use_skill（2 个）</p></td></tr><tr><td><p>工具总数</p></td><td><p>未公开具体数量</p></td><td><p>21 个内置工具</p></td></tr><tr><td><p>工具禁用</p></td><td><p>不支持</p></td><td><p>支持 <code>--disable-tools LIST</code></p></td></tr></tbody></table>

<strong>【代码图谱是核心差异】</strong> AtomCode 的 8 个代码图谱工具是其最大的差异化优势。在大型代码库中，Claude Code 需要用 Grep / Glob / Read 反复搜索和读取文件来理解代码结构，消耗大量上下文 token。AtomCode 通过符号索引直接定位，精准且省 token。`blast_radius`（影响面分析）尤其有价值——重构前可以精确评估修改风险。

<a id="c36-s85"></a>

### 四、扩展机制对比

<table><thead><tr><th><p>机制</p></th><th><p>Claude Code</p></th><th><p>AtomCode</p></th></tr></thead><tbody><tr><td><p>Skills</p></td><td><p>Markdown 指令包，.claude/skills/ 目录</p></td><td><p>SKILL.md 格式，~/.atomcode/skills/ 和 .atomcode/skills/，支持 $ 菜单和 use_skill 工具</p></td></tr><tr><td><p>Hook 事件</p></td><td><p>PreToolUse / PostToolUse / Stop / PreCompact / SubagentStop / PermissionRequest 等</p></td><td><p>UserPromptSubmit / PreToolUse / PostToolUse / SessionStart / SessionEnd / Notification（不支持 Stop / PreCompact / SubagentStop）</p></td></tr><tr><td><p>MCP</p></td><td><p>完整支持（tools / resources / prompts / OAuth）</p></td><td><p>tools-only（不支持 resources / prompts / OAuth），兼容 Cursor / .mcp.json 配置</p></td></tr><tr><td><p>Plugin</p></td><td><p>原生生态</p></td><td><p>兼容 Claude Code Plugin 协议，CC 生态可直接安装</p></td></tr><tr><td><p>Slash Commands</p></td><td><p>支持</p></td><td><p>支持，带内联 Bash 脚本预计算</p></td></tr><tr><td><p>/setup 自动推荐</p></td><td><p>无</p></td><td><p>有——扫描项目并联网推荐适合的 skill</p></td></tr></tbody></table>

<a id="c36-s86"></a>

### 五、并行与协作对比

<table><thead><tr><th><p>功能</p></th><th><p>Claude Code</p></th><th><p>AtomCode</p></th></tr></thead><tbody><tr><td><p>Git Worktree</p></td><td><p>原生支持，自动创建</p></td><td><p><code>/worktree create</code> / <code>list</code> / <code>done</code> / <code>cleanup</code></p></td></tr><tr><td><p>后台会话</p></td><td><p>Subagents（独立上下文）</p></td><td><p><code>/bg</code> 16 个并行槽位，模型在后台继续工作</p></td></tr><tr><td><p>一次性后台任务</p></td><td><p>通过 subagent</p></td><td><p><code>/background &lt;任务&gt;</code>（只读工具子集）</p></td></tr><tr><td><p>Agent Teams</p></td><td><p>支持（Writer / Reviewer / TDD 等模式）</p></td><td><p>暂不支持</p></td></tr><tr><td><p>Coordinator Mode</p></td><td><p>支持（四阶段自动协调）</p></td><td><p>暂不支持</p></td></tr><tr><td><p>Fan-out 批处理</p></td><td><p><code>/batch</code> 交互式规划</p></td><td><p><code>-p</code> 非交互模式 + shell 循环</p></td></tr><tr><td><p>远程访问</p></td><td><p>Remote Control + claude.ai/code</p></td><td><p><code>/webui lan</code> 局域网 + 手机浏览器</p></td></tr><tr><td><p>定时任务</p></td><td><p><code>/schedule</code> 云端定时</p></td><td><p>暂不支持（crontab + <code>-p</code> 替代）</p></td></tr><tr><td><p>长时间运行</p></td><td><p><code>/loop</code> 最多 3 天</p></td><td><p><code>/goal</code> 自动循环</p></td></tr><tr><td><p>WebUI</p></td><td><p>Desktop App</p></td><td><p>内置 <code>/webui</code>，浏览器实时同步</p></td></tr></tbody></table>

<a id="c36-s87"></a>

### 六、项目指令文件对比

<table><thead><tr><th><p>维度</p></th><th><p>Claude Code</p></th><th><p>AtomCode</p></th></tr></thead><tbody><tr><td><p>文件名</p></td><td><p>CLAUDE.md</p></td><td><p>.atomcode.md（查找顺序：.atomcode.md → ATOMCODE.md → AGENTS.md → CLAUDE.md）</p></td></tr><tr><td><p>层级结构</p></td><td><p>全局 / 项目 / 子目录三级</p></td><td><p>全局 / 项目级，向上逐级查找</p></td></tr><tr><td><p>AGENTS.md 兼容</p></td><td><p>不支持</p></td><td><p>原生支持（开放标准 agents.md）</p></td></tr><tr><td><p>Auto Memory</p></td><td><p>有（自动记忆）</p></td><td><p>/remember 手动记忆 + /memory 查看</p></td></tr><tr><td><p>/init 生成</p></td><td><p>有</p></td><td><p>有——扫描项目生成 .atomcode.md</p></td></tr></tbody></table>

<strong>【AtomCode 的多格式兼容是优势】</strong> AtomCode 支持 .atomcode.md、ATOMCODE.md、AGENTS.md、CLAUDE.md 四种格式，查找顺序先找到的先生效。这意味着如果你同时在用 Claude Code 和 AtomCode，可以用 AGENTS.md 让两者共享同一份指令文件，避免重复维护。

<a id="c36-s88"></a>

### 七、独特功能对比

<strong>AtomCode 独有（Claude Code 没有）</strong>

- 代码图谱 8 个工具——符号导航、调用链追踪、影响面分析；
- 视觉预处理器——非视觉模型也能处理图片；
- /bg 16 槽位后台会话——模型在后台继续工作；
- /goal 自动循环——设定目标让 agent 自己迭代；
- /webui 内置 WebUI——浏览器界面实时同步；
- /review 内置代码审查——/review、/review staged、/review &lt;base&gt;；
- IDE 插件——VS Code + JetBrains 原生插件，侧边栏聊天、右键菜单、Diff 预览；
- /setup 自动推荐 Skills——扫描项目联网推荐；
- 视觉预处理器配置——vision&#95;preprocessor&#95;provider 字段；
- 多 Provider 切换——/provider 随时切换不同模型；
- \$ 菜单调用 Skills——行首 \$ 弹出 skills 菜单；
- /upgrade 自动升级——/upgrade rollback 回滚。

<strong>Claude Code 独有（AtomCode 没有）</strong>

- Agent Teams——多 session 互相通信、协调分工；
- Coordinator Mode——四阶段自动协调（Research → Synthesis → Implementation → Verification）；
- Fan-out /batch——交互式规划批量任务；
- Remote Control——手机远程管理本地 session；
- /schedule——云端定时任务；
- /loop——本地长时间无人值守运行最多 3 天；
- Subagents——主 session 调用专家 agent（独立上下文 + 自定义工具权限）；
- Computer Use——控制鼠标键盘操作桌面应用；
- Voice Mode——语音对话；
- MCP 完整支持——resources / prompts / OAuth / roots / elicitation；
- 更多 Hook 事件——Stop / PreCompact / SubagentStop。

<a id="c36-s89"></a>

### 八、总结：谁该用哪个

<table><thead><tr><th><p>场景</p></th><th><p>推荐</p></th><th><p>原因</p></th></tr></thead><tbody><tr><td><p>国产化 / 信创要求</p></td><td><p>AtomCode</p></td><td><p>开源 + 国产模型，数据不出境</p></td></tr><tr><td><p>大型代码库开发</p></td><td><p>AtomCode</p></td><td><p>代码图谱大幅减少上下文消耗</p></td></tr><tr><td><p>多模型灵活切换</p></td><td><p>AtomCode</p></td><td><p>支持任意 OpenAI 兼容 API</p></td></tr><tr><td><p>本地 / 离线模型</p></td><td><p>AtomCode</p></td><td><p>支持 Ollama 本地部署</p></td></tr><tr><td><p>免费使用</p></td><td><p>AtomCode</p></td><td><p>CodingPlan 免费额度</p></td></tr><tr><td><p>需要 Agent Teams 高级协作</p></td><td><p>Claude Code</p></td><td><p>Agent Teams / Coordinator Mode 更成熟</p></td></tr><tr><td><p>需要无人值守长时间运行</p></td><td><p>Claude Code</p></td><td><p>/loop 和 /schedule 更完善</p></td></tr><tr><td><p>MCP 完整生态</p></td><td><p>Claude Code</p></td><td><p>resources / prompts / OAuth 支持更全</p></td></tr><tr><td><p>Claude 模型最佳体验</p></td><td><p>Claude Code</p></td><td><p>原生优化，无兼容层</p></td></tr><tr><td><p>HarmonyOS PC</p></td><td><p>AtomCode</p></td><td><p>唯一支持鸿蒙的 AI 编程 Agent</p></td></tr><tr><td><p>IDE 内开发</p></td><td><p>AtomCode</p></td><td><p>原生 VS Code / JetBrains 插件，侧边栏 + 右键 + Diff 预览</p></td></tr></tbody></table>

两者并非互斥。AtomCode 兼容 CLAUDE.md 格式和 CC Plugin 协议，可以同时使用。很多开发者用 Claude Code 做复杂协作，用 AtomCode 做日常开发和国产模型场景。
