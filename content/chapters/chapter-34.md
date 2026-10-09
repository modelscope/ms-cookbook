<!-- Generated from ../source-html/chapter-34.html; do not edit independently. -->

# Mini AI Scientist：让 4B 开源模型自己做实验、发现隐藏规律

<a id="c34-s1"></a>

## 1\. 背景

"AI Scientist"是近来 Agent 方向的热门话题：让大模型自己提出假设、设计实验、分析数据，最后得出结论。但如果直接让模型做开放式科研，很快会遇到两个问题：一是小模型很难完成；二是结果<strong>无法判断对错</strong>——模型说"我发现了 X"，却没有标准答案可以核对，也就没法比较不同模型、不同 Agent 设计的好坏。

我们换一个思路：先把科研压缩成一个<strong>最小但完整、而且可以自动验证</strong>的闭环。研究对象是一台"黑盒机器"，输入两个整数 a、b（0～20），输出一个整数，内部规则未知，可能还带条件分支，例如"a 为偶数时输出 a+b，否则输出 a×b"。模型只能通过做实验来了解它，最后提交一条规则。因为输入只有 21×21=441 种，提交的规则可以在全部输入上逐一核对，<strong>不需要 LLM 当裁判</strong>。

本文用 Qwen3 系列开源模型和 vLLM，在魔搭 Notebook 中一步步搭建这个 Mini AI Scientist，并回答一个实际问题：<strong>多小的开源模型能完成这类"科学发现"？瓶颈在模型规模、思考模式，还是 Agent 的流程设计？</strong>

<table><thead><tr><th><p>项目</p></th><th><p>内容</p></th></tr></thead><tbody><tr><td><p>一句话简介</p></td><td><p>给开源模型一台隐藏规则的黑盒机器，让它自己提出假设、设计实验、调用 Python 检验并修正，最终提交规则，由程序在 441 个输入上穷举验证对错。</p></td></tr><tr><td><p>适用对象</p></td><td><p>做 LLM Agent、推理与评测的开发者；想把 AI Scientist 落到可量化实验的同学；需要可验证奖励环境（如 GRPO）的训练者。</p></td></tr><tr><td><p>难度与耗时</p></td><td><p>进阶。首次复现约 60 分钟：安装依赖约 10 分钟，下载模型约 5 分钟，Notebook 运行约 35 分钟（单卡 A100 实测，24GB 显卡会更慢）。</p></td></tr><tr><td><p>运行方式</p></td><td><p>魔搭 Notebook（单卡 GPU，≥24GB 显存），本地 vLLM 推理，无需任何 API Key。</p></td></tr><tr><td><p>主要模型与工具</p></td><td><p>Qwen3-4B（思考模式，主模型）；Qwen3-0.6B/1.7B/8B 与 Qwen2.5-Instruct 用于对比；vLLM 0.11.0；Python AST 沙箱。</p></td></tr></tbody></table>

本 Case 的输入、输出与完成边界如下：

<table><thead><tr><th><p>项目</p></th><th><p>说明</p></th></tr></thead><tbody><tr><td><p>输入</p></td><td><p>一台隐藏规则的黑盒机器（12 条规则、3 个难度等级）、实验预算 30 次、最多 15 轮交互</p></td></tr><tr><td><p>输出</p></td><td><p>模型提交的规则（Python 表达式）、完整的科研过程记录（JSONL）、自动评测结果（是否正确、一致率、实验次数）</p></td></tr><tr><td><p>完成标准</p></td><td><p>提交规则在全部 441 个输入上与真实规则完全一致，才算"发现成功"</p></td></tr><tr><td><p>边界</p></td><td><p>规则是两个整数输入上的确定性函数，不涉及噪声、连续变量和真实物理实验（拓展方向见第 7 节）</p></td></tr></tbody></table>

<a id="c34-s2"></a>

## 2\. 解决思路

整体思路是让模型与 Python 各司其职：<strong>模型负责决定</strong>（提出什么假设、做什么实验、什么时候下结论），<strong>Python 负责执行与校验</strong>（运行实验、计算、逐条核对假设），<strong>黑盒实验室保管真值</strong>（最后的穷举验证）。完整流程如下图所示：

![图 1：Mini AI Scientist 的科研闭环。蓝色为模型决策，绿色为 Python 执行与校验，橙色为黑盒实验室与真值。](<../../assets/mini-ai-scientist/flow.png>)

每一轮，模型输出一个 JSON 动作，从下面四个工具中选一个：

<table><thead><tr><th><p>工具</p></th><th><p>作用</p></th><th><p>是否消耗实验预算</p></th></tr></thead><tbody><tr><td><p><code>experiment</code></p></td><td><p>选择最多 6 组输入，在黑盒机器上运行</p></td><td><p>是（共 30 次）</p></td></tr><tr><td><p><code>compute</code></p></td><td><p>让 Python 在全部观测上计算派生列，例如 <code>out - a*b</code>，并提示哪一列是常数</p></td><td><p>否</p></td></tr><tr><td><p><code>check</code></p></td><td><p>用候选规则逐条核对已观测数据，列出对与错的行</p></td><td><p>否</p></td></tr><tr><td><p><code>submit</code></p></td><td><p>提交最终规则，结束研究</p></td><td><p>—</p></td></tr></tbody></table>

围绕这四个工具，代码分成几个模块：

<table><thead><tr><th><p>模块</p></th><th><p>作用</p></th></tr></thead><tbody><tr><td><p><code>lab.py</code> 隐藏规则实验室</p></td><td><p>保存 12 条真实规则；执行实验；在 441 个输入上做等价验证</p></td></tr><tr><td><p><code>compile_expr</code> 安全沙箱</p></td><td><p>只允许算术、比较、<code>X if C else Y</code> 和 <code>abs/min/max</code>，拒绝任意代码执行</p></td></tr><tr><td><p><code>agent.py</code> Agent 循环</p></td><td><p>解析动作、调用工具、组织反馈；用"实验记录本"保存已检验的假设，只保留最近 3 轮对话，控制上下文长度</p></td></tr><tr><td><p>提交关卡（可选）</p></td><td><p>提交时如果规则与模型自己已观测的数据矛盾，就拒绝并列出矛盾行</p></td></tr><tr><td><p><code>backend.py</code> 推理后端</p></td><td><p>用 vLLM 批量推理；剥离 <code>&lt;think&gt;</code> 思考内容，只把最终动作写回对话</p></td></tr></tbody></table>

选型上有三点考虑。第一，<strong>Qwen3 系列</strong>同一家族覆盖 0.6B～8B，并且可以按请求开关思考模式，适合做"规模 × 思考"的对照。第二，<strong>vLLM</strong>：思考模式每轮会生成数千 token，用 transformers 跑 Qwen3-8B，4 个 episode 就要 28 分钟；换成 vLLM 批量推理，36 个 episode 只需 33 分钟。第三，<strong>穷举验证而非 LLM 裁判</strong>：输入空间只有 441 种，等价性可以精确判定，评测零成本、没有歧义。

<a id="c34-s3"></a>

## 3\. 前置准备

<table><thead><tr><th><p>项目</p></th><th><p>要求与版本</p></th></tr></thead><tbody><tr><td><p>平台</p></td><td><p>魔搭 Notebook GPU 环境，单卡 ≥24GB 显存。本文实测环境为 Linux、单卡 A100 80GB</p></td></tr><tr><td><p>运行时</p></td><td><p>Python 3.11</p></td></tr><tr><td><p>依赖</p></td><td><p><code>vllm==0.11.0</code>（自带 <code>torch==2.8.0+cu128</code>）、<code>transformers&gt;=4.56,&lt;5</code>、<code>modelscope</code>、<code>pandas</code>、<code>matplotlib</code></p></td></tr><tr><td><p>驱动</p></td><td><p>NVIDIA 驱动需支持 CUDA 12.8 及以上</p></td></tr><tr><td><p>模型</p></td><td><p><code>Qwen/Qwen3-4B</code>（约 8GB，从魔搭下载）；可选 <code>Qwen/Qwen3-8B</code>（约 16GB）</p></td></tr><tr><td><p>数据</p></td><td><p>无需下载。12 条隐藏规则定义在代码中，开局观测由随机种子生成，完全可复现</p></td></tr><tr><td><p>权限</p></td><td><p>无需 API Key 或 Token</p></td></tr></tbody></table>

<strong>第 1 步：安装依赖</strong>

在 Notebook 的第一个单元格中运行下面的命令。安装完成后，<strong>重启 Kernel</strong> 再继续：

```bash
pip install -q "vllm==0.11.0" "transformers>=4.56,<5" modelscope pandas matplotlib
```

<strong>第 2 步：获取代码</strong>

本文的完整代码、Notebook 和实测结果都在 [mini-ai-scientist 仓库](<https://github.com/14H034160212/mini-ai-scientist>)中：

```bash
git clone https://github.com/14H034160212/mini-ai-scientist.git mini_ai_scientist
cd mini_ai_scientist
python scripts/test_lab.py      # 无需 GPU 的自检，应输出 all lab tests passed
```

打开仓库中的 `mini_ai_scientist.ipynb`，按顺序运行即可。下文的每个步骤都对应 Notebook 中的单元格，截图均来自本文实测运行（为便于阅读，截图中略去了 vLLM 的启动日志）。

<strong>第 3 步：检查环境</strong>

运行环境检查单元格，确认 `transformers` 为 4.x、`vllm` 为 0.11.0，并能看到 GPU 型号与显存。环境变量 `USE_MODELSCOPE=1` 表示模型权重从魔搭下载。

![图 2：环境检查：Python、torch、transformers、vLLM 版本与 GPU 信息。](<../../assets/mini-ai-scientist/env.png>)

复现时需要提前留意下面三个问题，它们都是我们实际踩过的坑：

- <strong>transformers 5.x 与 vLLM 0.11 不兼容</strong>，会报 `Qwen2Tokenizer has no attribute all_special_tokens_extended`，请安装 `transformers<5`。
- <strong>CUDA 13 构建的 vLLM 需要更新的驱动</strong>，会报 `CUDA driver version is insufficient`，请使用本文固定的 `vllm==0.11.0`。
- 在 `.py` 脚本里使用 vLLM 时，入口代码要放在 `if __name__ == "__main__":` 下（vLLM 以 spawn 方式启动子进程）；Notebook 中没有这个问题。

<a id="c34-s4"></a>

## 4\. 分步实战

我们先验证不依赖模型的模块（4.1～4.3，CPU 即可），再接入模型（4.4～4.8）。每一步最后都有一个检查单元格，用 `assert` 判断这一步是否成功。

<a id="c34-s5"></a>

### 4.1 搭建隐藏规则实验室

<strong>目标</strong>：构造研究对象——一台规则未知、但真值可以穷举验证的黑盒机器。

<strong>输入与操作</strong>：12 条规则分三个难度等级。Tier 1 是单一公式（如 `a + b`）；Tier 2 带一个条件分支（如按 a 的奇偶切换公式）；Tier 3 是嵌套条件或取模条件（如 `(a + b) % 5 == 0`）。`Lab(rule, seed)` 会用随机种子生成 3 个开局观测。

```python
from mini_scientist import Lab, RULES, RULES_BY_NAME

lab = Lab(RULES_BY_NAME["parity_a"], seed=0)
print("开局观测 (a, b, out):", lab.observations)
print("做一次实验 [(3,4), (4,4)] ->", lab.run([(3, 4), (4, 4)]))
```

<strong>检查方法</strong>：每条真实规则对自身的验证必须 100% 正确；同一种子的开局观测必须完全相同。

![图 3：步骤 1：12 条规则、开局观测与一次实验结果，检查通过。](<../../assets/mini-ai-scientist/step1-lab.png>)

<a id="c34-s6"></a>

### 4.2 让模型"调用 Python"的安全沙箱

<strong>目标</strong>：模型写的规则和计算式要被真正执行，但不能执行任意代码。

<strong>输入与操作</strong>：`compile_expr` 先解析表达式的语法树，只放行算术、比较、`X if C else Y` 与 `abs/min/max`，指数只允许 0～4 的常数。

<strong>检查方法</strong>：`__import__`、属性访问、超大指数必须被拒绝；判定看的是语义等价，所以 `max(a, b) - min(a, b)` 也应被判为 `|a - b|` 的正确答案。

![图 4：步骤 2：危险表达式被拒绝，等价规则被判为正确。](<../../assets/mini-ai-scientist/step2-sandbox.png>)

<a id="c34-s7"></a>

### 4.3 用"脚本模型"空跑 Agent 循环

<strong>目标</strong>：接入真实模型之前，先确认 Agent 循环、四个工具和评测流程本身没有问题。

<strong>输入与操作</strong>：用一个按固定剧本回复的假模型走一遍：做实验 → 计算 → 检验错误假设 → 检验正确假设 → 提交。Notebook 中同时打印了模型实际看到的系统提示词。

<strong>检查方法</strong>：空跑必须"发现成功"，并且实验 3 次、检验 2 次、计算 1 次、没有格式错误。下图中可以看到 `check` 的反馈：错误假设 `a - b` 会列出对与错的行，帮助模型定位条件分支。

![图 5：步骤 3：系统提示词与脚本模型空跑的逐轮反馈，检查通过。](<../../assets/mini-ai-scientist/step3-dryrun.png>)

<a id="c34-s8"></a>

### 4.4 加载模型（vLLM + 思考模式）

<strong>目标</strong>：在 GPU 上加载 Qwen3-4B，开启思考模式。

<strong>输入与操作</strong>：

```python
from mini_scientist.backend import VLLMBackend

MODEL = "Qwen/Qwen3-4B"      # 显存充足可换 "Qwen/Qwen3-8B"
backend = VLLMBackend(MODEL, thinking=True, max_tokens=8192,
                      max_model_len=20480, gpu_memory_utilization=0.85)
```

几个关键参数的含义：`max_tokens=8192` 是每轮思考加回答的上限；`max_model_len=20480` 是上下文长度，实验记录本让对话保持很短，这个长度足够；采样使用 Qwen3 官方推荐的思考模式参数 `temperature=0.6, top_p=0.95, top_k=20`，因为贪心解码容易让思考模型陷入循环；`gpu_memory_utilization=0.85` 在 24GB 显卡上可以正常运行 4B，显存不足时可调小或换 `Qwen/Qwen3-1.7B`。

<strong>过程与输出</strong>：首次运行会从魔搭下载约 8GB 权重，并做 CUDA Graph 编译。实测加载用时 37 秒（已下载、有编译缓存时）。随后发送一个最简单的请求做冒烟测试。

<strong>检查方法</strong>：模型的第一轮回复能被解析成带 `tool` 字段的 JSON 动作。

![图 6：步骤 4：模型加载完成，第一轮回复是合规的 experiment 动作。](<../../assets/mini-ai-scientist/step4-model.png>)

<a id="c34-s9"></a>

### 4.5 一次完整的科研过程

<strong>目标</strong>：观察模型如何从 3 个开局观测出发，一步步做实验、检验，直到提交。

<strong>输入与操作</strong>：规则 `parity_a`（Tier 2：a 为偶数时输出 `a + b`，否则输出 `a * b`），开局种子为 0。模型看不到真实规则。

<strong>过程与输出</strong>：下图是一次真实运行。模型从 3 个开局观测中猜出"按 a 的奇偶切换"，再用 (2,3) 和 (3,4) 两组对照实验验证，确认后提交，441 个输入全部一致，用时 76 秒。

<strong>检查方法</strong>：过程完整结束并得到验证结果。由于采样存在随机性，单次结果可能成功也可能失败，这正是 4.6 节要用多条规则统计的原因。

![图 7：步骤 5：Qwen3-4B 发现 parity&#95;a 规则的完整过程，441 个输入全部一致。](<../../assets/mini-ai-scientist/step5-episode.png>)

<a id="c34-s10"></a>

### 4.6 批量评测

<strong>目标</strong>：用统一口径衡量 Agent 的发现能力。

<strong>输入与操作</strong>：12 条规则各建一个 episode（种子 0），所有 episode 同步推进，每轮做一次批量推理：

```python
eps = [Episode(Lab(r, seed=0)) for r in RULES]
results = run_batch(backend, eps)      # 每轮一次批量推理，直到全部提交
```

<strong>过程与输出</strong>：完整过程保存在 `results/notebook/Qwen3-4B_think.jsonl`，每行包括提交规则、441 点一致率、实验次数和逐轮记录。实测用时 930 秒，总体解出 6/12：Tier 1 全部解出（4/4），Tier 2 解出 2/4，Tier 3 为 0/4。

<strong>检查方法</strong>：我们用同一配置跑了 3 个种子，每个种子解出 6～7/12、Tier 1 解出 3～4/4。因此正常范围是：总体 ≥4/12 且 Tier 1 ≥3/4。另外，vLLM 的采样种子是固定的，我们在同一环境中两次运行这一步，结果完全相同。

![图 8：步骤 6：12 条规则的逐条结果与按难度汇总，结果在正常范围内。](<../../assets/mini-ai-scientist/step6-batch.png>)

<a id="c34-s11"></a>

### 4.7 分析失败：模型和自己的数据"唱反调"

<strong>目标</strong>：弄清失败到底是"找不到规律"，还是别的原因。

<strong>输入与操作</strong>：对每个失败的 episode，把模型提交的规则放回它<strong>自己做过的全部实验</strong>上逐条核对。

<strong>过程与输出</strong>：在这次运行中，6 个失败里有 1 个提交了与自身数据矛盾的规则（`threshold_b`，矛盾 2 行），另有 1 个（`nested`）到最后也没有提交。这个比例在不同配置之间差别很大：完整实验中，不开思考的 Qwen3-8B 有 23/24 次失败属于这种情况，开启思考后降到 10/20（见第 5 节）。也就是说，很多失败不是不会发现，而是<strong>没核对就下结论</strong>。

<strong>检查方法</strong>：表中"与自身数据矛盾的行数"为 0 表示规则与已有数据一致但仍然错误（数据不足以排除），大于 0 表示自相矛盾，-1 表示未提交。

![图 9：步骤 7：失败 episode 的提交规则与模型自身数据的矛盾情况。](<../../assets/mini-ai-scientist/step7-failures.png>)

<a id="c34-s12"></a>

### 4.8 加一道"提交关卡"

<strong>目标</strong>：把"结论必须与自己的数据一致"这条科研规范写进 Agent。

<strong>输入与操作</strong>：`Episode(..., gate=True)`，其余设置与 4.6 完全相同。提交时如果规则与已观测数据矛盾，就拒绝提交、列出矛盾行，让模型继续研究。为保证每个 episode 都能结束，最后一轮的提交不经过关卡。

<strong>过程与输出</strong>：实测用时 1007 秒，解出数从 6/12 变为 7/12，关卡共拦截 5 次矛盾提交。

<strong>检查方法</strong>：被拦截次数 `rejected` 大于 0，说明关卡确实拦下了矛盾结论。单种子的差异会受随机性影响，多种子、多规模的结果见第 5 节。

![图 10：步骤 8：开启提交关卡前后的解出数对比。](<../../assets/mini-ai-scientist/step8-gate.png>)

<a id="c34-s13"></a>

## 5\. 完整运行与结果

Notebook 中的 4.6～4.8 是单种子的精简版。完整实验用命令行脚本一次跑完，实测单卡 A100 约 4 小时：

```bash
CUDA_VISIBLE_DEVICES=0 bash scripts/run_sweep.sh
python scripts/analyze.py results/sweep    # 生成 summary.md 与 solve_rate.png
```

每个配置运行 12 条规则 × 3 个种子 = 36 个 episode，共 17 个配置：Qwen3-0.6B/1.7B/4B/8B 各开关思考、提交关卡、Qwen2.5-Instruct 对照，以及去掉 `compute` 或 `check` 工具的消融。所有逐轮记录都保存在 `results/sweep/`，完整结果表见仓库中的 `results/sweep/summary.md`。

需要说明的是，每组只有 36 个 episode，解出率在 50% 附近时，单组的标准误约为 8 个百分点。因此下面只把明显大于这个量级的差异当作结论。

<a id="c34-s14"></a>

### 5.1 思考模式比参数量更重要

![图 11：Qwen3 各规模模型开启与关闭思考模式时的解出率（每组 36 个 episode）。](<../../assets/mini-ai-scientist/solve_rate.png>)

<table><thead><tr><th><p>模型</p></th><th><p>关闭思考</p></th><th><p>开启思考</p></th><th><p>失败中与自身数据矛盾（关 → 开）</p></th></tr></thead><tbody><tr><td><p>Qwen3-0.6B</p></td><td><p>0/36</p></td><td><p>7/36</p></td><td><p>36/36 → 26/29</p></td></tr><tr><td><p>Qwen3-1.7B</p></td><td><p>5/36</p></td><td><p>14/36</p></td><td><p>28/31 → 5/22</p></td></tr><tr><td><p>Qwen3-4B</p></td><td><p>10/36</p></td><td><p><strong>20/36</strong></p></td><td><p>25/26 → 7/16</p></td></tr><tr><td><p>Qwen3-8B</p></td><td><p>12/36</p></td><td><p>16/36</p></td><td><p>23/24 → 10/20</p></td></tr></tbody></table>

每个规模开启思考后，解出率都明显提升；开启思考的 1.7B（14/36）已经超过不开思考的 8B（12/36）。4B 与 8B（开思考）之间的差距在随机波动范围内，所以<strong>在这个任务上，4B 已经够用</strong>，魔搭免费 GPU 也能运行。

表格最后一列揭示了思考带来的主要收益：不开思考时，失败几乎全部是"提交了与自己实验数据矛盾的规则"；开启思考后，这类失败大幅减少（0.6B 例外，它开启思考后仍然大多自相矛盾）。

<a id="c34-s15"></a>

### 5.2 提交关卡：能拦住矛盾结论，但能否改对取决于模型

<table><thead><tr><th><p>配置</p></th><th><p>无关卡</p></th><th><p>有关卡</p></th><th><p>关卡拦截次数</p></th></tr></thead><tbody><tr><td><p>Qwen3-8B 开思考</p></td><td><p>16/36</p></td><td><p>19/36</p></td><td><p>12 次（6 个 episode）</p></td></tr><tr><td><p>Qwen3-4B 开思考</p></td><td><p>20/36</p></td><td><p>20/36</p></td><td><p>22 次（7 个 episode）</p></td></tr><tr><td><p>Qwen3-1.7B 开思考</p></td><td><p>14/36</p></td><td><p>16/36</p></td><td><p>30 次（8 个 episode）</p></td></tr><tr><td><p>Qwen3-8B 关思考</p></td><td><p>12/36</p></td><td><p>11/36</p></td><td><p>48 次（12 个 episode）</p></td></tr></tbody></table>

关卡只能告诉模型"你的结论和数据矛盾"，不能告诉它怎么改对。开启思考的模型被拦下后有时能自己修正，所以小幅提升；不开思考的 8B 被拦下后反复提交错误规则，直到轮数用完。这些差异都在随机波动范围内，我们的结论是：<strong>流程设计可以帮模型避免草率下结论，但修正假设的能力仍然要靠模型自己的推理。</strong>

<a id="c34-s16"></a>

### 5.3 工具要匹配模型能力

<table><thead><tr><th><p>配置（Qwen3-8B 开思考）</p></th><th><p>解出</p></th><th><p>说明</p></th></tr></thead><tbody><tr><td><p>完整工具</p></td><td><p>16/36</p></td><td><p>平均每个 episode 只用 0.36 次 <code>compute</code></p></td></tr><tr><td><p>去掉 <code>compute</code></p></td><td><p>20/36</p></td><td><p>没有变差</p></td></tr><tr><td><p>去掉 <code>check</code></p></td><td><p>17/36</p></td><td><p>没有变差</p></td></tr></tbody></table>

`compute` 最初是为不会思考、心算容易出错的模型设计的。开启思考的模型会在思考过程里自己计算，几乎不用这个工具（1.7B 平均每个 episode 只用 0.06 次），去掉它也不会变差。对弱模型必要的辅助，对强模型可能只是多余的选项。

<a id="c34-s17"></a>

### 5.4 其他观察

- <strong>上一代非推理模型明显更弱</strong>：Qwen2.5-7B-Instruct 与 3B-Instruct 均为 5/36，1.5B 为 0/36，从 3B 到 7B 没有提升。
- <strong>Tier 3 仍是能力边界</strong>：嵌套或取模条件的规则，所有配置中最好的成绩只有 2/12（Qwen3-8B 开思考 + 提交关卡）。

<a id="c34-s18"></a>

## 6\. 评测与验收

<a id="c34-s19"></a>

### 6.1 功能验收

- Notebook 步骤 1～3 的检查全部通过（不需要 GPU）。
- 步骤 6、8 生成 `results/notebook/*.jsonl`，每行包括提交规则、441 点一致率、实验次数和完整过程。
- 运行 `python scripts/test_lab.py` 输出 `all lab tests passed`。

<a id="c34-s20"></a>

### 6.2 质量验收

我们使用三个指标：<strong>发现成功率</strong>（提交规则在 441 个输入上与真实规则完全一致的比例，按难度分层报告）、<strong>一致率</strong>（提交规则与真实规则结果相同的输入比例，用来衡量部分正确）、<strong>实验效率</strong>（成功时平均使用的实验次数）。Qwen3-4B 开启思考时，单种子的正常范围是总体 ≥4/12、Tier 1 ≥3/4。

作为对照，我们还实现了一个不用 LLM 的基线：随机做实验，同时在约 1.2 万条 `F if C else G` 形式的候选规则中排除与数据不符的。

![图 12：穷举搜索基线：解出 32/36，但平均实验次数远高于 LLM。](<../../assets/mini-ai-scientist/baseline.png>)

穷举基线解出 32/36，看起来比 LLM 好，但它有两个本质局限：一是<strong>表达能力受限于候选语法</strong>，两层嵌套的 `nested` 规则不在候选空间中，永远发现不了；二是<strong>实验是盲目的</strong>，即使是最简单的 Tier 1 规则，平均也要用 29 次实验；而开启思考的 Qwen3-8B 与 4B 成功时，平均只用了 3.9 次和 7.6 次。LLM 科学家的价值在于有针对性地设计实验，差距在于推理的可靠性。

<a id="c34-s21"></a>

### 6.3 异常验收

<table><thead><tr><th><p>异常情况</p></th><th><p>实际出现在</p></th><th><p>系统表现</p></th></tr></thead><tbody><tr><td><p>思考过长被截断，没有输出 <code>&lt;/think&gt;</code></p></td><td><p>Qwen3 思考模式约 10%～20% 的轮次（8B 24/194，4B 31/158）</p></td><td><p>不把半截思考当作回答写回对话；提示"想得简短一些"，并计入 <code>truncated</code></p></td></tr><tr><td><p>输出格式不合规（如 LaTeX 转义 <code>\(</code>、输入写成 <code>{"a":3,"b":4}</code>）</p></td><td><p>小模型常见</p></td><td><p>宽松解析；无法解析时计入格式错误并提示重试，单个 episode 出错不会中断整批评测</p></td></tr><tr><td><p>同一检验反复执行、原地打转</p></td><td><p>Qwen2.5-7B</p></td><td><p>拦截重复的 <code>check</code>/<code>compute</code>，提示去做新实验</p></td></tr><tr><td><p>提交与自身数据矛盾的结论</p></td><td><p>各规模模型普遍</p></td><td><p>开启提交关卡时拒绝，并列出矛盾行</p></td></tr><tr><td><p>恶意代码</p></td><td><p>演示用</p></td><td><p>AST 白名单拒绝（见 4.2）</p></td></tr></tbody></table>

![图 13：异常验收：思考截断、畸形输入与矛盾提交的实际处理结果。](<../../assets/mini-ai-scientist/exceptions.png>)

<a id="c34-s22"></a>

## 7\. 已知限制、排错与可复用方向

<strong>已知限制</strong>

- 规则空间较小（两个整数输入、确定性输出），离真实科研还有距离。
- 采样有随机性，单次结果会波动，结论应以多种子统计为准；本文每个配置只有 36 个 episode，较小的差异不具备统计意义。
- Tier 3 规则对 8B 以内的模型仍然很难。
- 思考模式的计算开销约为非思考模式的 10～14 倍，且约 10%～20% 的轮次会因思考过长被截断。

<strong>常见问题</strong>

<table><thead><tr><th><p>现象</p></th><th><p>原因</p></th><th><p>解决方法</p></th></tr></thead><tbody><tr><td><p><code>Qwen2Tokenizer has no attribute all_special_tokens_extended</code></p></td><td><p>transformers 5.x 与 vLLM 0.11 不兼容</p></td><td><p>安装 <code>transformers&lt;5</code> 后重启 Kernel</p></td></tr><tr><td><p><code>CUDA driver version is insufficient for CUDA runtime version</code></p></td><td><p>安装了 CUDA 13 构建的 vLLM</p></td><td><p>固定 <code>vllm==0.11.0</code></p></td></tr><tr><td><p><code>Free memory on device ... is less than desired GPU memory utilization</code></p></td><td><p>显存被其他进程占用</p></td><td><p>调小 <code>gpu_memory_utilization</code>，或结束占用显存的进程</p></td></tr><tr><td><p>脚本中报 <code>An attempt has been made to start a new process before ... bootstrapping</code></p></td><td><p>vLLM 用 spawn 方式启动子进程</p></td><td><p>把入口代码放在 <code>if __name__ == "__main__":</code> 下</p></td></tr><tr><td><p><code>decoder prompt is longer than the maximum model length</code></p></td><td><p>截断的思考被当成回答写回对话</p></td><td><p>代码已在 <code>split_thinking</code> 中处理；修改后端时请保留这段逻辑</p></td></tr></tbody></table>

<strong>可复用方向</strong>

- 把观测改成带噪声、三元输入或浮点输出，考察重复实验与统计推断能力。
- 环境自带可验证奖励（441 点精确匹配），可以直接用于 GRPO 等强化学习，训练小模型的"科研策略"。
- "模型决策 + Python 执行 + 真值验证"的结构，也适用于数据分析 Agent 的自动评测、SQL 与公式推断、系统辨识和故障定位等场景。

<a id="c34-s23"></a>

## 8\. 代码、数据与参考资料

- 代码仓库：[mini-ai-scientist](<https://github.com/14H034160212/mini-ai-scientist>)，包含 `mini_scientist/` 源码、`scripts/`、带真实输出的 Notebook，以及 `results/sweep/` 下 17 个配置的完整逐轮记录。
- 数据：无外部数据。12 条规则定义在 `mini_scientist/lab.py` 中，开局观测由随机种子生成。
- 模型（Apache-2.0）：[Qwen3-4B](<https://modelscope.cn/models/Qwen/Qwen3-4B>)、[Qwen3-8B](<https://modelscope.cn/models/Qwen/Qwen3-8B>)、[Qwen3-1.7B](<https://modelscope.cn/models/Qwen/Qwen3-1.7B>)、[Qwen3-0.6B](<https://modelscope.cn/models/Qwen/Qwen3-0.6B>)。
- 推理框架：[vLLM](<https://github.com/vllm-project/vllm>)（Apache-2.0）。
- 相关工作：Sakana AI 的 The AI Scientist；BoxingGym（实验设计基准）；Popper（LLM Agent 的可证伪检验）。

<a id="c34-s24"></a>

## 9\. 小结

本文用开源模型搭建了一个可以自动验证的 Mini AI Scientist：模型负责提出假设、设计实验和下结论，Python 负责执行和校验，穷举验证给出确定的对错。实验表明，在这个任务上，<strong>开启思考的 4B 模型已经能精确发现过半的隐藏规则</strong>；思考模式的主要作用，是让模型的结论与自己的实验数据保持一致。而 Tier 3 规则的低成功率也提醒我们，小模型离可靠的"科学发现"还有不小的距离——这个可验证的环境，正好可以作为后续改进与训练的起点。
