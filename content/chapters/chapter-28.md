<!-- Generated from ../source-html/chapter-28.html; do not edit independently. -->

# Skill：把任务方法封装成能力

第一次让 Agent 整理会议纪要时，可能要解释很多要求：哪些内容算结论，怎样提取待办，负责人缺失时怎么处理，最后用什么格式输出。第二次遇到类似任务，这些要求又要重新说一遍。换一个同事或换一个 Agent，还得再解释一次。问题不在于 Agent 不会整理会议纪要，而在于这套方法只存在于某次对话中。它没有被保存，也没有变成可以重复调用的能力。

Skill 解决的就是这个问题，把一类任务的说明、步骤、工具、参考资料和验收标准放在一起。以后再遇到同类任务，Agent 可以先读取这套方法，再按照已经验证过的规则完成工作。

<a id="c28-s1"></a>

## <strong>Skill 是什么</strong>

Skill 可以理解为提供给 Agent 的一份专业工作手册。不改变模型参数，是把完成某类任务时需要遵守的方法保存下来，让 Agent 知道什么时候使用、先做什么、需要哪些工具，以及怎样判断结果是否合格。以整理会议纪要为例。有经验的项目助理会先检查材料，再区分讨论意见、最终结论和未决问题，随后提取行动项、负责人和截止时间，最后按统一模板输出并复核。原文没有的信息不会凭常识补写。

如果这些方法只保存在人的脑中，Agent 每次都要重新摸索。把它们写进 Skill 后，同一套方法就能在不同会议中重复使用，也可以由团队共同维护。换个方式说，Skill 是一种面向 Agent 的可复用能力包。它用任务说明、执行步骤、工具和资源、输出标准与异常处理，描述一类任务应该怎样完成。

以会议纪要 Skill 为例。该 Skill 通过接收会议转写稿、聊天记录或散乱笔记，输出会议信息、关键结论、行动项和未决问题。先看最核心的`SKILL.md`。文件开头使用 YAML 元数据说明 Skill 的名称和使用场景，后面使用 Markdown 编写具体工作方法。

<p></p>

```yaml
---
name: meeting-notes
description: 将会议转写稿、聊天记录或散乱笔记整理为结构化会议纪要。当用户要求提取会议结论、行动项或待确认问题时使用。
---

会议纪要整理

执行步骤

检查输入是否包含可识别的会议内容。
区分讨论意见、最终结论和未决问题。
提取行动项、负责人和截止时间。
无法确认的信息标记为“待确认”。
按规定模板输出，并与原始记录复核。
```

其中，`name`和`description`是规范中的必填字段。`name`是给当前 Skill 起个名字，`description`则给当前 Skill 进行任务描述，那 Skill 是怎样进入并完成一次任务的呢？

安装 Skill 以后，系统不会把所有文件一股脑交给大模型。常见的运行过程分为三步：

1. 系统先提供已安装 Skill 的名称和描述。大模型根据用户任务判断哪些能力可能相关。
2. 某个 Skill 被选中后，系统再加载它的`SKILL.md`，大模型据此检查输入并执行核心步骤。
3. 执行到特定环节时，才按说明读取参考资料、套用模板或运行脚本。

例如，用户提出把一份会议记录整理成纪要，大模型或 Agent 工具会从多个 Skill 中匹配会议纪要能力，再读取其完整规则。若任务还要求生成 Excel 行动项表，还可能同时选用表格处理 Skill。大模型负责结合当前任务作判断，Skill 负责提供稳定的方法，平台或 Agent 框架负责加载文件和调用工具。

相较于维护的 Skill，与 Prompt、工作流、MCP 有什么区别呢？接下来做一些梳理。

<a id="c28-s2"></a>

## <strong>Skill 与 Prompt 的区别</strong>

Prompt 是你在当前任务中交给大模型或 Agent 的输入，通常包括目标、材料、限制条件和输出要求。它回答的是这一次要做什么。例如：

```text
请把这段会议记录整理成会议纪要，列出结论和待办事项。
```

这条 Prompt 已经说明本次目标，但没有完整规定什么算最终结论、负责人缺失时怎么办、能否补全原文没有的信息，以及输出采用什么结构。Skill 把这些相对稳定的规则提前保存下来。下一次再处理会议记录时，你只需要提供本次材料和具体要求，不必重新复制整套方法。从作用、载体、加载方式以及版本管理等角度，对 Prompt 与 Skill 做个对比：

<table><tbody><tr><td><p>维度</p></td><td><p>Prompt</p></td><td><p>Skill</p></td></tr><tr><td><p>主要作用</p></td><td><p>描述当前任务</p></td><td><p>定义一类任务通常怎样完成</p></td></tr><tr><td><p>使用周期</p></td><td><p>多数只用于当前请求</p></td><td><p>可以被多次调用和持续维护</p></td></tr><tr><td><p>载体</p></td><td><p>对话中的文字、文件和上下文</p></td><td><p>包含<code>SKILL.md</code>及可选资源的目录</p></td></tr><tr><td><p>内容</p></td><td><p>目标、材料、约束和输出要求</p></td><td><p>触发条件、步骤、工具、模板、异常和验收</p></td></tr><tr><td><p>加载方式</p></td><td><p>通常直接进入当前上下文</p></td><td><p>可以按任务需要逐层加载</p></td></tr><tr><td><p>版本管理</p></td><td><p>容易散落在聊天记录中</p></td><td><p>可以纳入 Git 并保留变更记录</p></td></tr></tbody></table>

<p></p>

当然，Prompt 和 Skill 并不是二选一，Prompt 负责告诉大模型或 Agent 这一次要处理哪份材料、有什么临时要求，而 Skill 则负责提供这类任务已经沉淀好的做法。同一个 Skill 面对不同输入时，仍然需要 Prompt 说明本次目标。不是每条 Prompt 都值得做成 Skill。一个只做一次、目标还在变化的任务，先用 Prompt 跑通更合适。等同类任务反复出现、处理方法逐渐稳定，再把它沉淀成 Skill。

<p></p>

<a id="c28-s3"></a>

## <strong>Skill 与工作流的区别</strong>

工作流是一套用于组织多个任务节点的运行安排，通常会规定先后顺序、条件分支、数据传递和失败后的去向。它回答的是多个环节怎样衔接。

例如，一条周报工作流可以是：

```text
读取原始数据 → 清洗字段 → 生成图表 → 撰写分析 → 导出周报
```

Skill 关注的是某个能力单元应该怎样完成。上面的每一步都可以由一个 Skill 提供方法，也可以由脚本、人工操作或其他工具完成。两者的区别不在于谁固定、谁灵活，而在于关注对象不同：

- 工作流主要组织任务节点、顺序、分支和数据传递；
- Skill 主要封装完成某类任务所需的知识、规则、资源和工具使用方法。

一个 Skill 内部可以包含固定步骤，也可以包含条件判断。一个工作流也可以在某个节点调用 Agent，让 Agent 根据现场情况决定下一步。例如，会议纪要 Skill 可以根据输入作出不同处理：

- 输入没有会议正文时，停止生成并请求补充；
- 原文明确写出负责人时，直接写入行动项；
- 原文没有负责人时，标记为待确认；
- 多份材料互相矛盾时，列出冲突，不自行决定哪一份正确；
- 用户只要求行动项时，省略完整的会议摘要。

在真实系统中，Skill 和工作流经常组合使用：工作流负责把多个环节串起来，Skill 负责让其中某个环节按照稳定方法完成。

<p></p>

<a id="c28-s4"></a>

## <strong>Skill 与 MCP 的区别</strong>

<p></p>

MCP 是模型上下文协议，用于以统一方式向 Agent 提供外部工具、资源和提示模板。它回答的是 Agent 怎样连接和调用外部能力。通过 MCP，Agent 可以连接数据库、知识库、项目管理系统、地图服务或其他业务系统。但连接成功只代表 Agent 可以使用某项能力，不代表它已经知道应该怎样完成业务任务。假设 Agent 已经能读取项目管理系统，它仍然需要知道：

- 应该查询哪个项目；
- 统计什么时间范围；
- 哪些状态算已完成；
- 哪些字段属于敏感信息；
- 最终用什么格式生成项目报告；
- 创建、修改或删除记录前是否需要确认。

这些任务规则更适合写进 Skill。可以把两者的关系概括为：MCP 提供连接外部工具和数据的标准方式，Skill 描述怎样使用这些能力完成一类任务。

一个 Skill 可以指导 Agent 调用 MCP 工具，也可以完全不使用 MCP。一个 MCP 服务也可以被多个 Skill 采用。涉及发送消息、修改记录、删除数据、产生费用或公开发布时，Skill 应明确规定确认点，不能因为工具已经连接就默认允许执行。

<table><tbody><tr><td><p>概念</p></td><td><p>主要回答的问题</p></td><td><p>典型内容</p></td></tr><tr><td><p>Prompt</p></td><td><p>这一次要做什么</p></td><td><p>当前目标、材料和临时要求</p></td></tr><tr><td><p>Skill</p></td><td><p>这类任务通常怎样做</p></td><td><p>方法、规则、资源、工具和验收</p></td></tr><tr><td><p>工作流</p></td><td><p>多个环节怎样衔接</p></td><td><p>节点、顺序、分支和结果传递</p></td></tr><tr><td><p>MCP</p></td><td><p>Agent 怎样连接外部能力</p></td><td><p>工具、资源、参数和调用接口</p></td></tr></tbody></table>

<p></p>

<a id="c28-s5"></a>

## <strong>Skill 的基本组成</strong>

<p></p>

一个完整的 Skill，既要有说明任务方法的内容，也要有承载这些内容的文件。就任务本身来说，需要写清触发条件、输入、执行步骤、工具和资源、输出、异常处理；就文件组织来说，至少要有入口文件`SKILL.md`，复杂一些的 Skill 还会配上参考资料、模板、脚本和测试案例。以会议纪要 Skill 为例，完整目录可以这样组织：

<p></p>

```text
meeting-notes/
├── SKILL.md                         # 入口：名称、描述、输入、步骤和验收
├── references/
│   ├── terms.md                     # 术语表和内容分类规则
│   └── privacy-rules.md             # 敏感信息与脱敏要求
├── assets/
│   └── meeting-template.md          # 纪要输出模板
├── scripts/
│   └── clean-transcript.py          # 清理时间戳和重复口头语
└── tests/
    ├── normal-case.md                # 信息完整的测试案例
    ├── boundary-case.md              # 信息缺失或存在冲突的案例
    └── failure-case.md               # 无法继续处理的案例
```

<p></p>

其中，`SKILL.md`是整个目录的入口。Agent 先从这里了解 Skill 适合处理什么任务、需要什么输入、按什么步骤执行。进一步地，根据其他约束，可以补充其他工具或代码，如上述目录组织中，如果遇到专业术语或隐私要求时，可以读取`references/` 目录获取相关信息；再生成结果阶段，可以套用`assets/`中的模板；需要稳定完成文本清洗等机械操作时，再运行`scripts/`中的程序。`tests/`主要用于开发和改版后的验证，不是每次执行任务都要加载的内容。在构建阶段，目录不要求一次完全建设完毕。规则较少时，一个`SKILL.md`就能组成可运行的 Skill；当主文件越来越长，或者某项资料、模板和脚本需要反复使用时，可以进一步进行拆分。无论文件多少，Agent 实际执行的仍然是下面这条任务链：

<p></p>

```text
用户提出任务
    ↓
大模型根据名称和description筛选相关Skill
    ↓
加载选中Skill的SKILL.md
    ↓
检查输入 → 执行步骤 → 使用工具和资源 → 生成并检查输出
    ↓
遇到异常时按规则停止、降级或请求补充
```

<p></p>

当 l 同时存在多个 Skil 时，大模型通常先比较每个 Skill 的名称和描述，再选择与当前意图最相关的最小集合。例如，把会议记录整理成纪要并导出行动项表，可能同时需要会议纪要 Skill 和表格处理 Skill；如果只要求整理文字，则没有必要加载表格能力。具体筛选和调用方式由所用平台或 Agent 框架实现，但 Skill 作者必须把适用场景和边界写清楚，才能帮助大模型作出正确选择。

下面从触发条件、输入检查、执行步骤、工具与资源以及输出控制等方面进行介绍

<strong>1、触发条件</strong>

所谓触发条件，是指 Skill 提供大模型在众多 Skill 中找到当前需要的能力，主要体现在`SKILL.md`开头的`name`和`description`中。以会议纪要 Skill 为例。`name`是 Skill 的标识名称，通常使用小写字母、数字和连字符，并与目录名称保持一致。它要简短、明确，让人和系统都能区分这项能力。例如：

```yaml
name: meeting-notes
```

`description`用来说明这项 Skill 能做什么、遇到什么任务时应该使用。大模型读取用户任务后，会把任务意图与已安装 Skill 的名称和描述进行比较；匹配成功，才继续加载完整的`SKILL.md`。会议纪要 Skill 的 description 可以这样写：

```yaml
description: 将会议转写稿、聊天记录或散乱笔记整理为结构化会议纪要。当用户要求生成会议摘要、提取结论、行动项或待确认问题时使用。
```

<p></p>

不要为了增加触发概率塞入大量无关关键词。描述太宽，Agent 会在不相关的任务中误用；描述太窄，又可能在真正需要时找不到它。因为，最终完成 Skill 的编写，还需要依赖测试，测试时需要同时验证应该触发和不应该触发的任务，例如有一个会议录音 ASR 识别的 Skill，就不能在会议纪要相关任务时触发。

<p></p>

<strong>2、输入检查</strong>

所谓的输入检查，是指在开始执行某个 Skill 时，Agent 或大模型需要知道，在完成任务时，需要什么、哪些材料必需、哪些可以缺省，以及缺少关键信息时怎样处理。因此选中 Skill 后，下一步不是立刻生成结果，而是检查材料是否足够。以会议纪要 Skill 为例，对于输入部分，可以这样约定：

- 必需输入：会议转写稿、聊天记录或会议笔记中的至少一种；
- 可选输入：会议名称、时间、参与人名单和纪要模板；
- 输入边界：文件名和用户的概括不能替代会议原文；
- 缺失处理：没有会议正文时停止生成，并请用户补充材料。

<strong>3、执行步骤</strong>

输入检查通过后，Agent 才开始正式处理任务。执行步骤要写清楚从读取材料到交付结果的完整顺序：每一步处理什么，得到什么中间结果，遇到不同情况时转到哪里。只写分析内容、提取重点，还不足以让 Agent 稳定执行。会议纪要 Skill 可以按照下面的顺序处理：

```text
1. 读取全部会议材料；文件为空或无法读取时，转入异常处理。
2. 识别会议主题、时间和参与人，缺失字段暂时保留为空。
3. 清理不影响原意的口头语和重复内容，同时保留原始材料不变。
4. 按议题整理内容，把发言分别归入观点、决定和待确认问题。
5. 从会议内容中提取已经明确分派的行动项，并记录任务、负责人和截止时间。
6. 负责人或截止时间在原文中没有出现时，将对应字段标记为“待确认”。
7. 把整理结果填入会议纪要模板。
8. 逐项回查原文；无法找到依据的结论和行动项不得交付。
```

按照上述举例的这组步骤，有明确的入口、处理顺序和结束条件。第 1 步决定任务能否继续，第 2 至第 6 步形成结构化内容，第 7 步生成交付结果，第 8 步负责验收。执行步骤写到这个程度，后面的工具、模板和异常规则才知道应该接在哪个环节。

<strong>4、工具和资源</strong>

执行步骤说明要做什么，工具和资源说明具体依靠什么完成。工具负责执行动作，例如读取文件、运行脚本；资源负责提供规则和模板，例如术语表、隐私要求和纪要格式。两者都要写出具体名称和使用时机。会议纪要 Skill 可以使用下面这些内容：

<table><tbody><tr><td><p>类型</p></td><td><p>具体工具或资源</p></td><td><p>使用时机</p></td><td><p>作用</p></td></tr><tr><td><p>文件读取工具</p></td><td><p>Python 的<code>pathlib.Path.read_text()</code></p></td><td><p>执行第 1 步时</p></td><td><p>读取 UTF-8 编码的 TXT 或 Markdown 会议记录</p></td></tr><tr><td><p>Word 读取工具</p></td><td><p><code>python-docx</code></p></td><td><p>输入为 DOCX 时</p></td><td><p>读取 Word 文档中的段落和表格文字</p></td></tr><tr><td><p>清洗脚本</p></td><td><p><code>scripts/clean-transcript.py</code></p></td><td><p>划分议题前</p></td><td><p>清理时间戳、连续重复句和不影响原意的口头语</p></td></tr><tr><td><p>术语资源</p></td><td><p><code>references/terms.md</code></p></td><td><p>遇到简称或专业名词时</p></td><td><p>统一项目名、产品名和人员称谓</p></td></tr><tr><td><p>隐私资源</p></td><td><p><code>references/privacy-rules.md</code></p></td><td><p>输出前复核时</p></td><td><p>判断个人信息和业务敏感内容是否需要脱敏</p></td></tr><tr><td><p>输出模板</p></td><td><p><code>assets/meeting-template.md</code></p></td><td><p>生成纪要时</p></td><td><p>规定会议信息、结论、行动项和未决问题的排列方式</p></td></tr></tbody></table>

`SKILL.md`不能只列出这些名称，还要说明什么时候调用。例如，普通 TXT 直接使用`pathlib`读取；DOCX 改用`python-docx`；文本中出现项目简称时才读取术语表；需要对外发送时再检查隐私规则。脚本还应说明输入、输出和依赖，运行失败后进入哪条异常处理。访问令牌和密码不能写进 Skill 文件或脚本。

<strong>5、输出控制</strong>

完成处理后，Agent 需要知道怎样交付。输出控制阶段要求不能只写生成会议纪要，还要说明结构、格式和完成标准。根据要求，可以约定输出格式，例如：

<p></p>

```markdown
会议纪要

一、会议信息

会议主题：
会议时间：
参与人员：
二、关键结论

……
三、行动项


四、未决问题
如果结果需要保存为文件，还应说明文件类型、命名规则和保存位置。
```

<strong>6、异常处理</strong>

异常处理贯穿输入、执行、工具调用和输出检查，不是最后才补上的说明。它决定 Agent 遇到问题时是继续、降级、停止，还是请求用户确认。

常见异常包括输入为空、文件损坏、依赖缺失、外部服务不可用、工具权限不足，以及不同材料中的信息互相矛盾。可以使用下面四条统一原则：

<p></p>

1. 不伪造缺失信息；
2. 能安全降级时，说明限制后完成仍可完成的部分；
3. 无法继续时，指出失败步骤、原因和需要补充的材料；
4. 涉及覆盖、删除、发送、付费或敏感数据时，先请求确认。

<a id="c28-s6"></a>

## <strong>如何设计一个 Skill</strong>

<p></p>

前面已经说明 Skill 怎样被发现、怎样执行，以及一项完整能力需要包含哪些部分。现在把这些内容真正落到会议纪要案例中。

设计 Skill 的核心，不是先建目录或写一段很长的 Prompt，而是把人的工作经验整理成 Agent 能够执行和检查的方法。这个过程可以分成六步：选择适合封装的任务，确定目标和边界，复盘人工方法，把经验改写成规则，写出可以执行的第一版，最后跑通最短闭环。每一步都会产生下一步需要的内容：任务范围决定输入输出，人工方法形成执行步骤，初稿把这些内容组织起来，测试结果再推动下一版修改。

下面继续以会议纪要 Skill 为例，从一项模糊需求逐步形成可以在魔搭中运行的能力。

<strong>1、先选择适合封装的任务</strong>

适合做成 Skill 的任务通常有几个共同点：

- 会重复出现；
- 每次输入不同，但处理方法相似；
- 规则相对稳定；
- 输出有明确结构；
- 结果可以抽查或测试；
- 失败后可以安全停止或重新运行。

整理会议纪要符合这些条件：每次会议内容不同，但检查材料、识别结论、提取行动项和组织输出的方法基本一致；结果还可以回到原文逐项复核。因此，本章选择它作为贯穿案例。

如果任务目标本身还没有说清楚，或者每次都要完全依赖临场判断，先不要急着做 Skill。可以先用 Prompt 完成几次，等方法稳定后再沉淀。

<strong>2、写清目标和边界</strong>

选定任务后，要把宽泛愿望缩小成能够交付和验收的目标。做一个办公助手范围太大，无法成为一个稳定的 Skill。

会议纪要 Skill 的第一版目标可以写成：

> 接收一份原始会议记录，输出包含会议信息、关键结论、行动项和未决问题的结构化纪要；不根据常识补写原文中没有的负责人、日期和结论。

这个目标说清了输入、输出和禁止事项。第一版的输入是已经形成文字的会议记录，不负责录音转写；结果先保存为 Markdown，不自动发邮件，也不写入项目管理系统。边界越清楚，后面的步骤、异常和测试越容易定义。

<strong>3、复盘人工完成任务的方法</strong>

目标明确后，可以先把人工完成任务时真正采用的方法找出来，再判断哪些动作可以固定，哪些地方仍然需要结合上下文判断。整理的逻辑可以按照法：先进行三层过滤，再完成四维提取。

所谓三层过滤，可以按顺序处理会议转写稿：

1. 过滤不影响原意的口头语和语气词；
2. 排除与会议议题无关的闲聊和跑题内容；
3. 合并重复表达，但保留不同人员提出的不同意见。

完成清理后，再从四个维度整理信息：

1\. <strong>议题</strong>：会议讨论了哪些问题；

2\. <strong>观点</strong>：围绕每个议题，各方提出了哪些关键意见；

3\. <strong>决策</strong>：哪些事项已经形成明确共识；

4\. <strong>待办</strong>：谁需要在什么时间之前完成什么任务。

<p></p>

这套方法非常适合用来复盘会议纪要任务，因为它还原了人工整理时的真实顺序：先降低原始材料中的噪声，再识别内容之间的关系，最后提取需要执行的任务。复盘时还要继续追问几个细节：删减内容是否会改变原意，什么表达才能算作正式决策，负责人或截止时间缺失时怎样处理，材料前后矛盾时是否需要请用户确认。经过这一步，得到的不是一段泛泛的经验总结，而是一条可以继续拆解的处理路线。下一小节再把其中的过滤、分类、提取和复核，改写成 Agent 可以执行的动作、条件和检查点。

<strong>4、把经验改写成动作、条件和检查点</strong>

接下来把上述记录中的经验，改写成 Agent 可以执行的三类语句：

- 动作：读取原始记录，提取明确出现的行动项。
- 条件：如果原文没有负责人，则标记为待确认。
- 检查点：输出前逐项核对关键结论能否在原文中找到依据。

三类语句要连起来使用。先执行动作，遇到不同情况时按条件分支，完成后用检查点验收。例如，先提取行动项；若负责人或截止时间缺失，则保留行动项并标记待确认；输出前再核对每项任务是否都能在原文中找到依据。如果一句要求无法判断是否完成，就继续把它拆小。

<strong>5、把规则写进第一版 SKILL.md</strong>

经过前面的梳理，第一版`SKILL.md`已经有了材料。写的时候可以按照 Agent 处理任务的顺序组织，比如在会议纪要任务中，需要先总结正常会议的结论，在进一步整理出下一步的任务以及待确认的问题等，以此顺序来输出 Skill 的描述信息。例如：

```markdown
---
name: meeting-notes
description: 将会议记录整理为包含结论、行动项和待确认问题的结构化纪要。当用户要求整理会议内容或提取会议任务时使用。
---

# 会议纪要整理

## 输入要求

- 必须提供可读取的会议正文。
- 会议名称、时间和参与人可以缺少，但不得自行补写。

## 执行步骤

1. 检查会议正文是否可读。
2. 区分讨论意见、已经确认的结论和待确认问题。
3. 提取行动项、负责人和截止时间。
4. 对照原文复核结论和行动项。

## 输出要求

- 输出会议信息、关键结论、行动项和待确认问题。
- 原文缺少的负责人或截止时间标记为待确认。

## 异常处理

- 没有会议正文时停止，并请用户补充材料。
- 不同内容互相冲突时保留冲突，不自行选择答案。
```

<strong>6、先跑通最短闭环</strong>

为了进一步考虑实际使用的底座模型、Agent 工具等，需要对当前整理的 Skill 进行验证。需要先验证整理时 Skill 能否从输入走到合格输出。第一版可以从以下几个方面进行观察：识别任务情况、核心步骤执行情况、输出结果是否满足条件等方面进行观察，进一步地，可以按下面的方法完成第一次验证：

1. 只准备`SKILL.md`、一份信息完整的会议记录和一份期望的纪要结构。
2. 用一条明确的 Prompt 提交任务，例如：读取`meeting.txt`，使用会议纪要 Skill 生成 Markdown 纪要，不要补写原文没有的信息。
3. 检查 Skill 是否被正确选中，输入是否成功读取，结论和行动项能否回到原文找到依据。
4. 检查缺失的负责人和日期是否保留为待确认，输出是否符合模板，原始文件是否保持不变。
5. 记录第一次失败的位置。每次只调整一类规则，再用同一份材料重跑，确认修改确实解决了问题。
6. 信息完整的样例通过后，再加入缺字段、内容冲突和空文件等测试，防止改好一种情况却破坏另一种情况。

当 Skill 能够被稳定选中、正确读取输入、按规定结构输出，并且面对缺失信息时不编造内容，整体执行过程、输出内容，基本符合 Skill 中的预定，才算跑通。此后再根据真实需求增加其他要求，例如数据清洗工具、脱敏规则、长文本分段或外部系统连接。下一节就在魔搭的环境中完成这条最短路线。

<p></p>

<a id="c28-s7"></a>

## 在魔搭中使用 Skill

前面已经完成了会议纪要 Skill 的设计。下面在魔搭 Notebook 中实现这项能力，以差旅报销和客户接待的办公例会为例，将会议记录整理为已确认事项、待办事项和待确认事项，并检查 Skill 的调用过程。下面按实验步骤介绍主要操作和关键代码，涉及的辅助函数和变量需提前定义。

<p></p>

<a id="c28-s8"></a>

### <strong>实验任务与环境准备</strong>

本实验使用 Qwen3-4B 完成推理。这里主要补充 Skill 所需的组件，ms-swift 和模型部署的基本用法可参考前面章节。

首先，运行以下代码，查看当前 Python 和依赖包的版本：

```python
import sys
import importlib.metadata as metadata

print("Python：", sys.version)
for package in ["ms-agent", "modelscope", "omegaconf"]:
    try:
        print(package, metadata.version(package))
    except metadata.PackageNotFoundError:
        print(package, "未安装")
```

本次实验使用 Python 3.12.13、ms-agent 1.6.0、modelscope 1.39.0 和 omegaconf 2.3.0。其中，ms-agent 负责加载 Skill 和读取参考文件，modelscope 用于访问社区资源，ms-swift 和 vLLM 提供模型推理服务。如果依赖尚未准备好，先安装`ms-agent==1.6.0`等实验组件，保留已有训练包和基础数值计算包的版本。安装完成后重启内核，再继续后续操作。在`modelscope_skill_lab`下创建带有时间标识的目录，分别保存每次实验的 Skill、案例和报告。代码如下：

```python
WORK_DIR = (Path.cwd() / "modelscope_skill_lab").resolve()
RUN_DIR = WORK_DIR / (
    datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
)
for name in ["releases", "tests", "reports", "downloads", "config"]:
    (RUN_DIR / name).mkdir(parents=True, exist_ok=True)
```

其中，`releases`保存 Skill 版本，`tests`保存测试输入，`reports`保存结果，`config`保存模型配置，便于后续核对和比较。

<p></p>

<a id="c28-s9"></a>

### <strong>创建与安装会议纪要 Skill</strong>

前面已经说明了 Skill 的组成，这里直接将会议纪要规则写入文件。本实验只需要一个入口文件和一份输出约定，目录形式如下：

```text
releases/
└── 1.0.0/
    └── meeting-notes/
        ├── SKILL.md
        └── references/
            └── output-contract.md
```

`SKILL.md`保存适用范围、处理步骤和异常规则，开头的名称、描述和版本用于标识这项能力。头部内容如下：

```yaml
---
name: meeting-notes
description: 将会议转写稿、群聊会议记录或会议笔记整理为中文会议纪要，提取已确认的结论、行动项和待确认问题。用户要求会议纪要或会议行动项时使用；一般知识问答、模型训练原理解释不使用。
version: "1.0.0"
---
```

在执行步骤中，本实验特别保留了三类约束：没有会议正文时请求补充材料；负责人和截止时间没有明确出现时标为“待确认”；结论和行动项必须引用原文作为依据。这些规则会在 17.8 的测试中逐项检查。

为了便于检查，模型先输出 JSON，再由程序整理成会议纪要。`output-contract.md`规定输出字段，并增加处理状态和原文依据，主要内容如下：

<table><tbody><tr><td><p>字段</p></td><td><p>内容</p></td></tr><tr><td><p><code>status</code></p></td><td><p><code>ok</code>、<code>needs_input</code>或<code>unsupported</code></p></td></tr><tr><td><p><code>title</code></p></td><td><p>会议主题</p></td></tr><tr><td><p><code>decisions</code></p></td><td><p>已确认的结论及原文依据</p></td></tr><tr><td><p><code>actions</code></p></td><td><p>任务、负责人、截止时间和原文依据</p></td></tr><tr><td><p><code>unresolved</code></p></td><td><p>待确认事项或存在的冲突</p></td></tr><tr><td><p><code>message</code></p></td><td><p>需要补充的材料或无法处理的原因</p></td></tr></tbody></table>

其中，`decisions`和`actions`中的`evidence`字段要求引用原文的连续片段。模型可以概括任务内容，但用于核对的证据不能改写。当`status`不为`ok`时，结论和行动项应为空数组，同时在`message`中说明原因。

将入口内容和输出约定分别保存在`SKILL_V1`、`OUTPUT_CONTRACT`两个变量中，再写入对应文件：

```python
V1_DIR = RUN_DIR / "releases" / "1.0.0" / SKILL_NAME
(V1_DIR / "references").mkdir(parents=True, exist_ok=True)
(V1_DIR / "SKILL.md").write_text(SKILL_V1, encoding="utf-8")
(V1_DIR / "references" / "output-contract.md").write_text(
    OUTPUT_CONTRACT, encoding="utf-8"
)
```

运行以后，可以在文件浏览器中找到上述目录，打开`SKILL.md`确认内容已经写入。相关内容如下图所示。

当然，魔搭 Skills 中心（<u>https://modelscope.cn/skills</u>）也提供了相关资源，读者可以直接从魔搭 Skills 中心选择已有资源，将页面中的安装标识填入`COMMUNITY_SKILL_ID`，通过下面的接口下载：

```python
COMMUNITY_SKILL_ID = ""  # 填写从社区页面复制的安装标识。
if COMMUNITY_SKILL_ID:
    COMMUNITY_DIR = Path(HubApi().download_skill(
        skill_id=COMMUNITY_SKILL_ID,
        local_dir=str(RUN_DIR / "downloads"),
    )).resolve()
    print((COMMUNITY_DIR / "SKILL.md").read_text(encoding="utf-8"))
```

<p></p>

<a id="c28-s10"></a>

### <strong>加载 Skill 与读取参考文件</strong>

文件准备好后，使用 ms-agent 的`SkillLoader`加载本地目录，读取名称、描述、版本和资源路径。代码如下：

```python
from ms_agent.skill.loader import SkillLoader
from ms_agent.skill.schema import SkillContext

loader = SkillLoader()
registered = loader.load_skills(str(V1_DIR.resolve()))
print(loader.list_skills())
```

本次加载记录为`['meeting-notes@1.0.0']`。其中，`meeting-notes`是 Skill 的 ID，`1.0.0`是规则版本，与 ms-agent 软件包的版本不同。加载目录以后，可以通过`SkillContext`读取参考文件。下面的代码只加载名为`output-contract.md`的参考资料：

```python
skill = next(iter(registered.values()))
context = SkillContext(skill=skill, root_path=V1_DIR)
references = context.load_references(names=["output-contract.md"])
print(references[0]["content"])
```

为了让模型请求读取文件，本实验通过自定义的`NotebookSkillTools`封装了两个工具函数：

<table><tbody><tr><td><p>工具函数</p></td><td><p>作用</p></td><td><p>主要参数</p></td></tr><tr><td><p><code>skills_list</code></p></td><td><p>列出已加载 Skill 的 ID、版本和用途</p></td><td><p>无</p></td></tr><tr><td><p><code>skill_view</code></p></td><td><p>读取 Skill 入口或指定参考文件</p></td><td><p><code>skill_id</code>、可选的<code>file_path</code></p></td></tr></tbody></table>

读取入口时，调用`skill_view`并传入`{"skill_id": "meeting-notes"}`；读取参考文件时，再指定`file_path`。其中，`meeting-notes`是读取对象，`skill_view`是执行读取的工具。

加载与读取检查如下：

```python
ACTIVE_DIR = V1_DIR
runtime = make_runtime(ACTIVE_DIR)

viewed = runtime.tools.call_tool(
    tool_name="skill_view",
    tool_args={"skill_id": SKILL_NAME},
)
reference = runtime.tools.call_tool(
    tool_name="skill_view",
    tool_args={
        "skill_id": SKILL_NAME,
        "file_path": "references/output-contract.md",
    },
)
print("入口读取成功：", "content" in json.loads(viewed))
print("参考资料读取成功：", "content" in json.loads(reference))
```

`make_runtime()`负责校验目录、加载版本和准备工具。本次入口和参考资料的读取结果均为`True`，说明文件能够正常访问，接下来就可以让模型发起读取请求。Skill 加载与资源读取结果如下。

<p></p>

<a id="c28-s11"></a>

### <strong>部署模型并配置推理接口</strong>

本实验使用魔搭社区的`Qwen/Qwen3-4B`，通过 ms-swift 部署为 OpenAI 兼容接口。在已安装 ms-swift 和 vLLM 的 GPU 环境终端中运行：

```bash
CUDA_VISIBLE_DEVICES=0 swift deploy \
  --model Qwen/Qwen3-4B \
  --load_args false \
  --infer_backend vllm \
  --enable_thinking false \
  --host 0.0.0.0 \
  --port 18002 \
  --api_key 123 \
  --vllm_gpu_memory_utilization 0.8 \
  --vllm_max_model_len 8000 \
  --max_new_tokens 2000
```

<p></p>

在魔搭中，模型启动阶段的结果如下：

服务日志，当输出如下内容表示服务已启动完毕：

```markdown
INFO:Application startup complete.
INFO:Uvicorn running on http://0.0.0.0:18002 (Press CTRL+C to quit)
```

魔搭端启动成功的日志如下：

<p></p>

<a id="c28-s12"></a>

### <strong>通过办公对话调用 Skill</strong>

下面使用一份行政例会记录进行调用。材料中包含两项已经确认的安排、两名负责人的具体任务，以及一项仍需确认的信息：

```text
会议主题：本周行政工作安排。会议时间：2026-09-04。
主管：今天确认两件事。第一，本月差旅报销材料统一在下周二前收齐；
第二，客户接待会定在下周三下午三点，地点是三楼会议室。
李明：报销材料我来收集，截止时间为2026-09-08。
王敏：我负责预订三楼会议室并发送会议邀请，截止时间为2026-09-07。
小周：客户可能有两个人线上参加，不过还没确认。
主管：线上参会名单先记为待确认，其他事项按刚才的安排推进。
```

模型需要整理会议中已经确认的安排，列出任务、负责人和截止时间，并保留尚未确定的信息。这里生成的是纪要，不实际办理报销或发送邀请。先使用明确指定 Skill 的请求，再使用日常办公中常见的自然语言请求，对比两种表达能否调用同一项能力。核心调用代码如下：

```python
explicit_result = await run_skill_task(
    "用 meeting-notes 帮我整理一下刚才的办公例会，"
    "把报销和客户接待的安排、负责人、截止时间列清楚。"
    + "\n\n会议记录：\n" + DEMO_TEXT,
    ACTIVE_DIR,
)

natural_result = await run_skill_task(
    "这是刚才例会的记录，帮我整理成一份简短纪要，"
    "方便发到工作群。还没确定的事情单独列出来。"
    + "\n\n会议记录：\n" + DEMO_TEXT,
    ACTIVE_DIR,
)
```

其中，`run_skill_task()`为每次任务新建对话，并将 Skill 索引和工具定义发送给模型。模型提出读取请求后，由程序执行文件读取，再把内容返回给模型。为了避免模型反复读取已经获得的资料，程序会检查入口和输出约定是否都已读取成功。两者都具备后，进入最终答案生成阶段。关键判断如下：

```python
ready_to_answer = (
    read_skill_successfully(result)
    and read_skill_successfully(result, "references/output-contract.md")
)

if ready_to_answer:
    messages[0]["content"] = (
        system + "\n技能入口和输出规则已读取完成。"
        "现在根据原始会议材料生成最终结果，"
        "只输出符合规则的 JSON，不再调用工具。"
    )

message, finish_reason, usage = await asyncio.to_thread(
    model_call, messages, [] if ready_to_answer else api_tools
)
```

资料读取完成后，请求使用`tool_choice="none"`，让模型生成最终答案。提示更新在已有的`system`消息中，工具结果后仍由模型回复，保持角色顺序。本次两种请求都读取了 Skill 和输出约定，生成了办公纪要。结果保留了报销和客户接待安排，列出李明、王敏的任务，并将线上参会人数记为待确认。不同调用的措辞略有差异，可对照原文复核。

页面展示的是整理后的纪要，保存的 JSON 仍包含`evidence`等字段。原文引用和异常输入的处理，将在后面的测试中继续检查。

<p></p>

<a id="c28-s13"></a>

### <strong>检查与调试调用过程</strong>

调用完成后，检查入口、输出约定是否读取，以及读取失败时能否报告原因。`trace`保存了每轮模型回复、工具参数和返回内容，可用于定位问题。例如，检查前面两次调用的读取情况，可以使用下面的代码：

```python
rows = []
for label, result in [("显式调用", explicit_result), ("自然语言调用", natural_result)]:
    rows.append({
        "调用方式": label,
        "请求状态": result["run_status"],
        "入口已读取": read_skill_successfully(result),
        "规则已读取": read_skill_successfully(
            result, "references/output-contract.md"
        ),
    })
display(pd.DataFrame(rows))
```

本次两种调用均为`completed`，入口和规则读取均为`True`，说明请求结束且资料已读取。纪要内容是否正确，还需要进一步检查。为了检查工具的异常处理，还可以故意传入不存在的 Skill ID 和不存在的参考文件。例如：

```python
missing_resource = runtime.tools.call_tool(
    tool_name="skill_view",
    tool_args={
        "skill_id": SKILL_NAME,
        "file_path": "references/does-not-exist.md",
    },
)
print("缺失文件处理是否符合预期：", "error" in json.loads(missing_resource))
```

这里故意使用不存在的文件，返回`error`表示正确识别了问题。表示本次所传入的内容将其标为“处理是否符合预期”，可以避免与实际运行故障混淆。

常规展示保留检查结果即可。需要排查时，再从`reports`中查看对应轮次的完整回复和工具记录。

<p></p>

<a id="c28-s14"></a>

## Skill 的测试与版本

一次调用完成后，还需要用不同材料检查 Skill 是否可靠。下面准备固定案例，验证信息提取和异常处理，并将结果与 Skill 版本一起保存。

本节继续使用同一份会议纪要 Skill。先建立测试矩阵和检查条件，再运行第一版测试，最后修改规则、比较两个版本并演示回退。

<p></p>

<a id="c28-s15"></a>

### <strong>准备测试案例</strong>

案例需要同时记录输入和预期行为。正常案例检查信息提取，边界案例检查不确定信息的处理，失败案例检查能否停止并说明原因，另设不相关任务检查误触发。

测试矩阵如下：

<table><tbody><tr><td><p>编号</p></td><td><p>类别</p></td><td><p>输入特征</p></td><td><p>预期行为</p></td></tr><tr><td><p>N01</p></td><td><p>正常</p></td><td><p>包含报销和客户接待安排的完整办公例会</p></td><td><p>保留结论、任务、负责人和截止时间</p></td></tr><tr><td><p>N02</p></td><td><p>正常</p></td><td><p>已经写明行动项的简短会议笔记</p></td><td><p>提取明确的任务、负责人和日期</p></td></tr><tr><td><p>B01</p></td><td><p>边界</p></td><td><p>已经安排任务，但未确定截止时间</p></td><td><p>日期填写“待确认”</p></td></tr><tr><td><p>B02</p></td><td><p>边界</p></td><td><p>有人提出建议，会议尚未批准</p></td><td><p>不生成已确认决定，保留待确认事项</p></td></tr><tr><td><p>B03</p></td><td><p>边界</p></td><td><p>两份记录对同一事项的时间表述冲突</p></td><td><p>保留冲突，不自行选择结论</p></td></tr><tr><td><p>B04</p></td><td><p>边界</p></td><td><p>有人提出需要完成一项工作，但未指定负责人</p></td><td><p>不把发言人自动作为负责人</p></td></tr><tr><td><p>F01</p></td><td><p>失败</p></td><td><p>没有会议正文</p></td><td><p>返回<code>needs_input</code>并说明需要补充材料</p></td></tr><tr><td><p>F02</p></td><td><p>失败</p></td><td><p>提供的是产品说明书</p></td><td><p>返回<code>unsupported</code>，不生成会议结论和行动项</p></td></tr><tr><td><p>T01</p></td><td><p>不应触发</p></td><td><p>一般知识问答，与会议纪要无关</p></td><td><p>直接回答，不读取会议纪要 Skill</p></td></tr></tbody></table>

每个案例用一个字典保存输入和检查条件。下面分别选取一个正常案例、边界案例和失败案例，展示其写法：

```python
# 办公例会中的两项截止日期应与原文保持一致。
normal_case = {
    "id": "N01", "kind": "正常", "text": DEMO_TEXT, "status": "ok",
    "owners": ["李明", "王敏"],
    "due_values": ["2026-09-08", "2026-09-07"],
    "min_actions": 2, "min_decisions": 1,
}

boundary_case = {
    "id": "B01", "kind": "边界",
    "text": "测试会议记录：已安排陈晨整理测试用例，会上没有确定截止时间。",
    "status": "ok", "owners": ["陈晨"],
    "due_values": ["待确认"], "min_actions": 1,
}

failure_case = {
    "id": "F01", "kind": "失败", "text": "", "status": "needs_input",
}
```

`status`规定预期状态，`owners`和`due_values`检查负责人和日期，`min_actions`规定最少行动项数量。这些条件只用于验收，模型接收的仍是用户请求和案例正文。

更换材料后，预期日期和负责人也要同步更新。上面的 N01 已按办公例会填写日期；已保存的测试记录仍有旧日期预期，后面会说明其影响。

<p></p>

<a id="c28-s16"></a>

### <strong>定义检查条件</strong>

案例准备好以后，需要把“正确完成”的要求写成可以执行的检查。使用`check_output()`对模型返回结果进行验收，主要包括下面几个方面：

<table><tbody><tr><td><p>检查内容</p></td><td><p>判断方法</p></td></tr><tr><td><p>请求是否结束</p></td><td><p>检查<code>run_status</code>，区分正常返回、服务错误和轮次耗尽</p></td></tr><tr><td><p>资料是否读取</p></td><td><p>检查工具记录中入口和输出约定的实际返回</p></td></tr><tr><td><p>输出格式是否正确</p></td><td><p>检查 JSON 能否解析，以及字段名称和类型是否符合约定</p></td></tr><tr><td><p>关键信息是否符合案例</p></td><td><p>检查状态、负责人、截止时间和条目数量</p></td></tr><tr><td><p>原文依据是否存在</p></td><td><p>检查<code>evidence</code>是否为会议正文中的连续片段</p></td></tr><tr><td><p>失败输入是否停止生成</p></td><td><p>检查异常状态下结论和行动项为空，并说明原因</p></td></tr><tr><td><p>是否误用 Skill</p></td><td><p>对不相关任务检查是否发生了<code>skill_view</code>调用</p></td></tr></tbody></table>

以原文依据为例，模型生成的结论可以是概括性的文字，但`evidence`需要保留原始表述。下面是验收函数中的关键判断：

```python
if item["evidence"] not in case["text"]:
    problems.append(field + " 的证据不在原文中")
```

`item`表示当前条目，`field`表示正在检查的字段。该判断可发现引用被改写或引用来源错误，但证据能否支持结论，仍需人工复核。对于没有正文或材料不适用的案例，还需要检查模型有没有停止生成纪要内容。关键代码如下：

```python
if data["status"] != case["status"]:
    problems.append("status 不符合预期")

if case["status"] != "ok":
    if data["decisions"] or data["actions"] or not data["message"].strip():
        problems.append("失败情形应停止生成纪要内容并说明原因")
```

例如，F01 应返回`needs_input`。如果仍返回`ok`，或者说明材料不足的同时生成了会议决定，都不符合要求。还可以人为加入错误日期、删除读取记录，检查验收函数能否识别问题。这是检查代码的自测，不能代替真实模型测试。文件缺失、模拟服务失败和输入过长用于检查程序能否报告异常；F01、F02 则检查模型面对异常材料时的回答。两类结果分别记录。

<p></p>

<a id="c28-s17"></a>

### <strong>运行测试并分析结果</strong>

`run_suite()`依次运行案例，每次新建对话，保存结果和工具记录，再调用`check_output()`生成问题清单。主要代码如下：

```python
CASE_IDS = None   # None表示运行全部案例。
REPEATS = 1       # 本次每个案例运行一次。

v1_results, v1_report_dir = await run_suite(
    V1_DIR, case_ids=CASE_IDS, repeats=REPEATS
)
display(v1_results)
print("原始输出和轨迹：", v1_report_dir)
```

`PASS_AUTO`表示自动检查通过，`FAIL`表示结果不符合要求，`ERROR`表示运行未正常完成。`human_review`记录人工复核状态，本次仍为`pending`。本次 1.0.0 版本的实际记录中，9 个案例有 6 个自动通过、3 个失败，未出现标记为`ERROR`的案例。结果如下：

<table><tbody><tr><td><p>案例</p></td><td><p>自动检查结果</p></td><td><p>记录中的主要问题</p></td></tr><tr><td><p>N01</p></td><td><p>FAIL</p></td><td><p>结论的证据未匹配原文；旧的截止日期预期未满足</p></td></tr><tr><td><p>N02</p></td><td><p>PASS_AUTO</p></td><td><p>未触发当前检查条件中的问题</p></td></tr><tr><td><p>B01</p></td><td><p>PASS_AUTO</p></td><td><p>未触发当前检查条件中的问题</p></td></tr><tr><td><p>B02</p></td><td><p>PASS_AUTO</p></td><td><p>未触发当前检查条件中的问题</p></td></tr><tr><td><p>B03</p></td><td><p>PASS_AUTO</p></td><td><p>未触发当前检查条件中的问题</p></td></tr><tr><td><p>B04</p></td><td><p>PASS_AUTO</p></td><td><p>未触发当前检查条件中的问题</p></td></tr><tr><td><p>F01</p></td><td><p>FAIL</p></td><td><p>处理状态不符合预期，未满足异常输入的停止生成要求</p></td></tr><tr><td><p>F02</p></td><td><p>FAIL</p></td><td><p>处理状态不符合预期，未满足异常输入的停止生成要求</p></td></tr><tr><td><p>T01</p></td><td><p>PASS_AUTO</p></td><td><p>未发生会议纪要 Skill 的读取请求</p></td></tr></tbody></table>

N01 首先存在测试预期不一致的问题：正文中王敏的截止日期为`2026-09-07`，测试代码却仍要求`2026-09-09`。因此，这项日期报错不能直接归为模型错误，应先修正`due_values`再重跑。N01 还存在证据未匹配原文的问题。同一办公示例的调用轨迹中，模型将原文“第二，客户接待会定在下周三下午三点，地点是三楼会议室。”改成了“主管：客户接待会定在下周三下午三点，地点是三楼会议室。”。含义虽然接近，但增加了该片段中没有的称谓，不符合`evidence`逐字摘录的要求。

F01 没有正文，应请求补充材料；F02 提供产品说明书，应说明材料不适用。本次两项均未满足状态和停止生成要求，需要结合案例报告中的最终文本和工具轨迹进一步分析。后续应先校准测试预期，再完善证据引用和异常处理规则。自动通过的案例也要对照原文复核。

<p></p>

<a id="c28-s18"></a>

### <strong>修改 Skill 并比较版本</strong>

<p></p>

保留 1.0.0，在新目录中创建候选版本 1.0.1，并补充负责人判定规则。两个版本分别加载和测试，便于比较。下面是版本创建代码的主要部分：

```python
V2_DIR = RUN_DIR / "releases" / "1.0.1" / SKILL_NAME
if not V2_DIR.exists():
    shutil.copytree(V1_DIR, V2_DIR)
    updated = (V2_DIR / "SKILL.md").read_text(encoding="utf-8")
    updated = updated.replace('version: "1.0.0"', 'version: "1.0.1"', 1)
    updated += (
        "\n## 负责人判定补充\n"
        "发言人不自动等于负责人；提出安排、建议或疑问的人，"
        "没有明确接受任务时，负责人仍为“待确认”。\n"
    )
    (V2_DIR / "SKILL.md").write_text(updated, encoding="utf-8")
```

这项规则针对 B04：提出工作的人不一定是负责人。由于输入输出结构未变，本实验将其记为修订版本，并在`CHANGELOG.md`中记录规则、关联案例和候选状态。

接下来使用相同的模型、案例和重复次数测试候选版本，再按案例编号进行合并比较。核心代码如下：

```python
v2_results, v2_report_dir = await run_suite(
    V2_DIR, case_ids=CASE_IDS, repeats=REPEATS
)
comparison = v1_results.merge(
    v2_results,
    on=["case_id", "repeat", "kind"],
    suffixes=("_v1", "_v2"),
)
display(comparison[[
    "case_id", "automatic_result_v1", "automatic_result_v2",
    "problems_v1", "problems_v2",
]])
```

相关过程结果如下：

在本次保存的记录中，1.0.0 有 6 项自动通过，1.0.1 有 7 项自动通过。逐项对比以后，可以看到变化集中在 F01：

本次只观察到 F01 由失败变为自动通过，尚不能证明新增规则带来了稳定改善。修改针对负责人判定，变化却发生在空输入案例；每例也只运行一次，N01 预期仍需校准。采用候选版本前，应修正测试条件，让两版重跑相同案例，并提高`REPEATS`检查稳定性。人工复核后，再决定是否采用；F02 等未通过的情况继续完善规则。

<p></p>

<a id="c28-s19"></a>

### <strong>保存版本与回退</strong>

每个版本都需要保存完整文件和测试记录。本实验在`release-manifest.json`中记录文件清单和哈希，同时保存变更说明、配置和报告。主要产物如下：

<table><tbody><tr><td><p>文件或目录</p></td><td><p>保存内容</p></td></tr><tr><td><p><code>releases/1.0.0/</code>、<code>releases/1.0.1/</code></p></td><td><p>两个版本的 Skill 目录和版本清单</p></td></tr><tr><td><p><code>CHANGELOG.md</code></p></td><td><p>规则变化及关联案例</p></td></tr><tr><td><p><code>tests/</code></p></td><td><p>固定的测试输入与预期条件</p></td></tr><tr><td><p><code>reports/</code></p></td><td><p>模型输出、工具轨迹、自动检查结果和版本比较表</p></td></tr><tr><td><p><code>config/active-skill.json</code></p></td><td><p>当前使用的版本、路径和文件哈希</p></td></tr><tr><td><p><code>environment.json</code>、<code>pip-freeze.txt</code></p></td><td><p>本次运行环境记录</p></td></tr></tbody></table>

`activate_version()`检查目录和文件哈希，再创建新的运行器，保证版本清单与实际规则一致。

```python
ACTIVE_DIR, runtime = activate_version("1.0.1")
print("切到候选版：", ACTIVE_DIR)

ACTIVE_DIR, runtime = activate_version("1.0.0")
print("回退到旧版：", ACTIVE_DIR)
```

本次已完成从 1.0.1 切回 1.0.0 的文件校验和加载，但回退后没有再次调用模型，尚未验证回退后的测试结果。

如果需要确认回退后的行为，应继续对当前目录执行测试：

```python
rollback_results, rollback_report_dir = await run_suite(
    ACTIVE_DIR, case_ids=CASE_IDS, repeats=REPEATS
)
display(rollback_results)
```

保存规则、案例、结果和环境信息后，就能追溯每个版本的表现。后续修改应对应具体案例，经过测试和复核，再决定采用新版本还是恢复原版。

<p></p>

本章节所有实验数据和代码，可参考：

https://modelscope.cn/gallery/liucong/0e182f07-3330-40cc-ba59-173b7cc609b7
