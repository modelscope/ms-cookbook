<!-- Generated from ../source-html/chapter-29.html; do not edit independently. -->

# 快速使用 Claude Code

这篇我们直接上手 Claude Code，从安装、登录、接入模型，一直用到自己的项目里。

如果你想让 AI 帮你改代码、整理文章，或者开发一个每天都能用上的小工具，可以跟着往下做。

<a id="c29-s1"></a>

## Claude Code 是什么？

Claude Code 是 Anthropic 推出的 AI 编程工具。你给它一个任务，它可以读取项目文件、分析实现方式、修改代码，再运行命令检查结果。

![正文配图](<../../assets/manuscript-20260914/c27-0c498f3aa4fdd2.webp>)

<p></p>

它的工作过程，可以理解为：<strong>理解需求 → 查看文件 → 制定方案 → 执行修改 → 检查结果。</strong>

比如，你可以让它解释一个看不懂的项目，排查一个报错，补一个功能，也可以让它读取本地的 Markdown 文章，生成摘要、整理目录、改写成不同平台的文案。

这篇主要使用终端版。安装后，在项目文件夹里输入 `claude`，就能开始对话；习惯图形界面的朋友，也可以选择桌面应用或编辑器集成。[Claude Code 产品介绍](<https://code.claude.com/docs/en/overview>)

<strong>先跑通一个小任务，后面再逐步加上项目规则、Skills 和外部工具。</strong>

> 截图用于说明操作位置与界面效果，具体版本、模型名称和套餐信息以实际页面为准。命令请使用正文中的代码块。

<a id="c29-s2"></a>

## 安装前，准备好这几样

先检查电脑环境：

<table><thead><tr><th><p>项目</p></th><th><p>要求</p></th></tr></thead><tbody><tr><td><p>macOS</p></td><td><p>macOS 13 或更高版本</p></td></tr><tr><td><p>Windows</p></td><td><p>Windows 10 1809 或更高版本，可以原生使用，也可以使用 WSL</p></td></tr><tr><td><p>Linux</p></td><td><p>Ubuntu 20.04+、Debian 10+ 等受支持的发行版</p></td></tr><tr><td><p>内存</p></td><td><p>至少 4GB</p></td></tr><tr><td><p>网络</p></td><td><p>能正常连接所选模型服务，完成认证和请求</p></td></tr><tr><td><p>Node.js</p></td><td><p>原生安装不需要；选择 npm 安装时，需要 Node.js 22 或更高版本</p></td></tr></tbody></table>

Windows 推荐安装 Git for Windows，以便使用 Bash 工具；没有安装时，当前版本也支持使用 PowerShell 工具。完整要求见[安装文档](<https://code.claude.com/docs/en/setup>)。

接着确定模型从哪里来：

- 有 Claude Pro、Max，或者已开通相应权限的 Team、Enterprise 账号，可以用 Claude 账号登录。
- 使用 Claude Console，则按 API 用量计费。
- 想接入 Kimi，可以按第 5 节配置对应的 API 服务。

Claude 免费账号不包含 Claude Code 使用权限。Claude 订阅和 Console API 余额是两套计费方式，购买订阅不会自动给 API 账户充值。[账号与认证说明](<https://code.claude.com/docs/en/authentication>)

<a id="c29-s3"></a>

## 安装 Claude Code

下面两种安装方式，<strong>选一种即可</strong>。

<strong>方式一：原生安装</strong>

macOS 打开“终端”；Linux 或 WSL 打开自己的终端，输入：

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Windows 在开始菜单中搜索并打开 PowerShell，输入：

```powershell
irm https://claude.ai/install.ps1 | iex
```

注意，Windows 这条命令要在 <strong>PowerShell</strong> 中执行。原生安装默认自动更新，安装命令来自[官方快速开始](<https://code.claude.com/docs/en/quickstart>)。

<strong>方式二：通过 npm 安装</strong>

如果电脑已经装好 Node.js，也可以走 npm。

先在终端检查版本：

```bash
node -v
npm -v
```

Node.js 需要 22 或更高版本。还没安装的朋友，可以从 [Node.js 官网](<https://nodejs.org/en/download>)获取符合要求的版本。

Windows 使用这条路线时，可以按 `Windows + R`，输入 `cmd`，点击“确定”，打开命令提示符：

![正文配图](<../../assets/manuscript-20260914/c27-54353c06d54dd2.webp>)

<p></p>

然后执行安装命令，macOS、Linux 也可以在自己的终端里执行同一条：

```bash
npm install -g @anthropic-ai/claude-code
```

看到安装完成的提示后，就可以继续了：

![正文配图](<../../assets/manuscript-20260914/c27-55d0b16cc95231.webp>)

如果 npm 报权限错误，先检查 Node.js 的安装方式，或改用前面的原生安装方式。不要直接给安装命令加 `sudo`。[npm 安装说明](<https://code.claude.com/docs/en/setup>)

<strong>最后，检查是否装成功。</strong>

无论选择哪种方式，都在终端执行：

```bash
claude --version
claude doctor
```

第一条显示版本号，第二条检查安装环境。能显示版本，说明程序已经装好，下一步完成账号登录。

<a id="c29-s4"></a>

## 进入项目，开始第一次对话

<strong>第一步：打开自己的项目目录。</strong>

先准备一个测试文件夹，可以放一个小项目，也可以放几篇文章的副本。

在终端输入：

```bash
cd "你的项目文件夹路径"
claude
```

把引号里的内容换成自己的实际路径，路径里有空格时保留引号。

下面这张图，就是用 `cd` 进入文件夹的过程。前面的路径变了，说明终端已经切换到对应目录：

![正文配图](<../../assets/manuscript-20260914/c27-c8afa6f6553dbe.webp>)

记住，<strong>你在哪个文件夹里启动 Claude Code，它就从哪个工作目录开始处理任务。</strong>

<strong>第二步：选择界面主题。</strong>

首次启动时，按提示完成界面设置。如果出现主题选择，使用方向键选择，再按回车确认。

我选的是 Dark，黑底界面看着挺舒服。

![正文配图](<../../assets/manuscript-20260914/c27-422e7a719360c9.webp>)

<strong>第三步：选择登录方式。</strong>

有 Claude 订阅的朋友，选择 Claude 账号；使用官方 API 的朋友，选择 Console 对应的入口。

![正文配图](<../../assets/manuscript-20260914/c27-17cbb2cca1037f.webp>)

按照提示在浏览器完成授权，完成后回到终端。如果浏览器没有自动打开，就复制界面提供的登录链接。

需要重新登录时，在 Claude Code 对话里输入：

```text
/login
```

使用 Kimi 的朋友，可以先跳到第 5 节完成配置，再回来测试。

<strong>第四步：确认状态，发一句话。</strong>

在 Claude Code 中输入：

```text
/status
```

检查当前目录、账号或凭据来源、模型配置，再发一句“你好”。

终端里的对话效果如下：

![正文配图](<../../assets/manuscript-20260914/c27-d81112228d0ee0.webp>)

能收到回复以后，再让它做一点真正和文件有关的事：

```text
请用中文回复。
列出当前目录第一层的文件和文件夹，说明这个目录主要用来做什么。
先只阅读，不修改文件。信息不足的地方直接告诉我。
```

当它能够找到你准备的文件，就完成了从“装上工具”到“开始使用”的第一步。

这里分清两种命令：`claude`、`claude doctor` 在电脑终端里输入；`/status`、`/login` 在进入 Claude Code 后输入。

<a id="c29-s5"></a>

## 把 Kimi 接入 Claude Code

Claude Code 负责操作文件和工具，模型负责理解与生成。接入 Kimi 后，你依然在 Claude Code 里工作，但模型请求会发给 Kimi。

先分清两个服务：

<table><thead><tr><th><p>使用方式</p></th><th><p>Key 从哪里获取</p></th><th><p>服务地址</p></th></tr></thead><tbody><tr><td><p>Kimi 开放平台，按 API 用量计费</p></td><td><p>Kimi 开放平台控制台</p></td><td><p><code>https://api.moonshot.cn/anthropic</code></p></td></tr><tr><td><p>Kimi Code，使用对应套餐权益</p></td><td><p>Kimi Code 控制台</p></td><td><p><code>https://api.kimi.com/coding/</code></p></td></tr></tbody></table>

两种服务的 Key、模型名称和额度需要分别配置。下面演示<strong>开放平台路线</strong>；Kimi Code 用户使用[对应的官方接入配置](<https://www.kimi.com/code/docs/third-party-tools/claude-code.html>)。

<strong>第一步：创建 API Key。</strong>

打开 [Kimi 开放平台](<https://platform.kimi.com/>)，注册或登录后，进入 API Key 管理页面。

![正文配图](<../../assets/manuscript-20260914/c27-66da1746ca21c9.webp>)

点击“创建 API Key”，填写一个方便自己识别的名称，比如 `claude-code`，再确认创建。

![正文配图](<../../assets/manuscript-20260914/c27-cd16ec4618a436.webp>)

把生成的 Key 保存在自己的密码管理器中，配置时需要使用。它相当于调用接口的凭证，不要放进文章、截图或公开代码仓库。

<strong>第二步：写入模型配置。</strong>

退出正在运行的 Claude Code。找到用户目录中的 `.claude/settings.json`：

- macOS、Linux：`~/.claude/settings.json`
- Windows：`C:\Users\你的用户名\.claude\settings.json`

没有这个文件，就创建 `.claude` 文件夹和 `settings.json`。文件已存在时，先留一份副本，再合并下面的 `env` 字段，保留其他设置。

下面将各任务使用的模型统一配置为 `kimi-k3[1m]`，先跑通一套模型：

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.moonshot.cn/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "YOUR_MOONSHOT_API_KEY",
    "ANTHROPIC_MODEL": "kimi-k3[1m]",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "kimi-k3[1m]",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "kimi-k3[1m]",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "kimi-k3[1m]",
    "ANTHROPIC_DEFAULT_FABLE_MODEL": "kimi-k3[1m]",
    "CLAUDE_CODE_SUBAGENT_MODEL": "kimi-k3[1m]",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "1000000",
    "CLAUDE_CODE_EFFORT_LEVEL": "max"
  }
}
```

把 `YOUR_MOONSHOT_API_KEY` 换成自己的 Key。这里的模型映射和参数依据 [Kimi 开放平台接入文档](<https://platform.kimi.com/docs/guide/claude-code-kimi>)整理；使用前确认账号有对应模型的访问权限。

如果首次使用第三方服务，仍停在账号引导页，按同一份官方文档完成一次初始化：在用户目录的 `.claude.json` 顶层加入 `"hasCompletedOnboarding": true`，保留已有字段。这个文件和 `.claude/settings.json` 是两个不同的文件。

检查配置时，留意有没有同时设置 `ANTHROPIC_API_KEY`。这条开放平台路线使用 `ANTHROPIC_AUTH_TOKEN`，应移除冲突的认证字段。`settings.json` 中的 `env` 会覆盖终端同名变量，所以不要在几处填互相矛盾的地址和模型。

<strong>第三步：重新启动并验证。</strong>

在项目目录中运行：

```bash
claude
```

再输入 `/status`，确认服务地址为 `https://api.moonshot.cn/anthropic`，模型为配置的 Kimi 模型。

先发送“你好”，再试一次文件读取。两个操作都成功，才说明对话和项目操作都跑通了。

如果使用终端里的 `export` 临时设置变量，需要在<strong>同一个终端窗口</strong>里启动 `claude`；关掉窗口后，临时变量不会自动保留。

<a id="c29-s6"></a>

## 让 Claude Code 真正开始干活

我更建议从一个明确的小需求开始。

比如读懂项目：

```text
阅读 README 和主要入口文件，告诉我：
1. 这个项目解决什么问题。
2. 主要目录分别负责什么。
3. 应该用什么命令启动、构建和检查。
先给我说明，不修改代码。
```

比如修复问题：

```text
平台选择框里的文字显示不全。
复现方式：打开内容分发助手，展开平台列表，选择“小红书”。
预期效果：完整显示平台名称，窗口变窄后仍能正常操作。
请定位相关样式，只修改这个问题，并告诉我怎么验证。
```

任务稍复杂时，先让它出方案。在终端启动计划模式：

```bash
claude --permission-mode plan
```

也可以在现有会话中按 `Shift+Tab`，切换到 Plan 模式。看完方案，确认方向，再选择实施。想查看各项操作的权限提示，可以使用 `claude --permission-mode default` 启动，并留意界面的权限状态。[权限模式说明](<https://code.claude.com/docs/en/permission-modes>)

<strong>把长期规则写进 CLAUDE.md。</strong>

有些话，不需要每次都重复。比如使用什么语言、项目用什么技术、结果放在哪里，都可以写进项目根目录的 `CLAUDE.md`。

在 Claude Code 中输入 `/init`，生成初稿后再检查、修改。以内容分发插件为例，可以写成：

```markdown
# 项目说明

这是一个 Obsidian 内容分发助手插件，使用 TypeScript。
目标是把 Markdown 笔记转换成不同平台的文案。

# 协作要求

- 使用中文回复，修改前先阅读相关代码。
- 使用 Obsidian 的 API 和主题变量，保持与应用界面一致。
- 原始笔记只用于读取，生成结果放在独立的预览区域。
- API Key 通过设置页配置，不写死在源码里。
- 每次完成后说明改动、检查结果和仍需手动验证的部分。
```

项目规则要具体，能指导实际操作。`CLAUDE.md` 的文件名按这个大小写写；需要查看记忆设置时，可以使用 `/memory`。[项目记忆说明](<https://code.claude.com/docs/en/memory>)

<p></p>
