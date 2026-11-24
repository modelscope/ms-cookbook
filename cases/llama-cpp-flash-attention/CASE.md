# 两个人同时提问时，怎样让本地大模型更快开口？

## 用 llama.cpp 部署 Qwen3.8-27B Q4，并实测 Flash Attention 的效果

一台只有一张 24GB 显卡的机器，已经能装下量化后的 27B 模型。但如果两个人同时提问，能不能都得到回答？等待第一段文字的时间会不会太长？打开 Flash Attention 后，情况是否真的改善？

这篇教程跟着一次已经跑过的魔搭 Notebook 实验，从检查 GPU、下载模型、启动服务、发送问题，到比较两组结果，走完整条链路。实测环境是一张 NVIDIA A10，不是手机或个人电脑。对同一批长档问题各发起 20 次请求、保持两路并发时，首段输出等待时间的 P95 从 **1.7893 秒**降到 **1.5740 秒**，约减少 **12.0%**。这是这台机器和这批问题的观测值，不代表所有设备都能得到同样的提升。

> 实测日期：2026-10-17。本文的命令和图片基于一次已经完成的实验。图片是实验后对保存的输入、日志和结果进行核验时拍摄的，不能当作“截图时重新跑完下载、编译和全部压测”的证明。完整指标定义和实验限制见 [技术附录](CASE_TECHNICAL.md)。

- **适合谁**：第一次在 GPU Notebook 部署本地模型、想知道“参数改了以后到底有没有变快”的读者。
- **难度与时间**：命令会逐步解释，但需要会复制 Linux 终端命令；首次准备约 1 到 3 小时。
- **运行方式**：魔搭 GPU Notebook 的 Linux 终端；一张 A10 24GB；llama.cpp `b10430`。
- **最后得到什么**：本机模型服务、正常与异常请求记录、四轮对照数据、CSV 和推荐报告。

## 先认识我们要解决的问题

想象两位同事共用一个放在内网的问答服务。服务能回答问题，但他们同时发问时，页面迟迟不出现文字。管理员想知道：是服务出错了，还是只是变慢了？调整一个推理参数以后，等待时间有没有缩短？

本文把问题限定得很清楚：**模型、机器、输入问题和其他服务参数都保持不变，只比较 Flash Attention 关闭和开启。** 我们会先确保服务正常，再测量等待时间、整体处理速度、请求成功率和显存占用。最后生成一份可追溯到原始请求的报告。

整个过程可以先记成一条线：

```text
公开中文问题
    ↓
llama.cpp 在 A10 上加载 GGUF 模型
    ↓
脚本模拟一人或两人提问，并记录每条请求
    ↓
比较 Flash Attention 关闭 / 开启
    ↓
得到汇总表、推荐配置和原始证据
```

### 读命令前，弄懂这几个词

- **GGUF** 是模型权重的文件格式。本文用的模型文件约 16.8GB，文件名以 `.gguf` 结尾。
- **Q4_K_M** 是量化方式。可以粗略理解为把模型权重压缩到较低精度，让 27B 模型更容易装进 24GB 显卡。量化可能影响回答质量，本文没有评测这部分。
- **llama.cpp** 是运行模型的程序。这里使用它的 `llama-server`，让脚本通过本机 HTTP 接口发送问题。
- **Flash Attention** 是推理时的一种注意力计算实现。本文用 `-fa off` 和 `-fa on` 切换。它是否更快，要靠同一负载的实测回答。
- **首段输出等待时间**，下文简称 **TTFT**，是从客户端发出请求，到收到第一段非空流式文字的时间。模型可能先输出推理文字，所以它不一定是最终答案正文的第一个字。
- **token** 是模型处理文字时使用的单位，不等于一个汉字。本文记录实际输入、输出 token 数；`max_tokens=64` 表示最多生成 64 个 token。
- **JSONL** 是“一行一条 JSON 记录”的文本文件。输入的每一行是一道问题，结果的每一行是一条请求，方便逐条检查。
- **SHA256** 可以理解成文件指纹。下载后的指纹与本文记录一致，才能确认比较时使用的是同一个文件；它不代表模型质量好坏。
- **并发 2** 是测试脚本同时维持最多两条请求，用来模拟两个人同时使用；这不等于测试了成百上千名用户。

还有一个统计词 **P95**：把一组等待时间从短到长排好，P95 用来观察靠后、较慢的请求。本文 20 次请求按“最近秩”取第 19 个值。只看最快的一次，不能代表两个人日常使用时的体验。

## 开始前需要什么？

这次实验使用 [魔搭 Notebook 工作区](https://www.modelscope.cn/code/workspace) 的 Linux GPU 实例。作者实测到的显卡为 NVIDIA A10，显存 24564 MiB，驱动版本 550.54.15。模型、下载缓存、CUDA 工具链和编译文件合计需要较大空间，建议在 `/mnt/workspace` 留出至少 **35GB**。首次运行通常需要 **1 到 3 小时**，主要时间花在下载约 16.8GB 的模型和编译程序上。Notebook 的剩余时长不足时，先延长或重新启动实例。

本教程配套的目录里有：

```text
cases/llama-cpp-flash-attention/
├── CASE.md                  本教程
├── CASE_TECHNICAL.md        指标口径与实验限制
├── scripts/
│   ├── setup.sh             下载模型、准备 CUDA、编译 llama.cpp
│   ├── smoke.py             测试正常请求和错误请求
│   ├── bench.py             执行性能测试
│   └── report.py            汇总结果
├── data/
│   └── workload.jsonl       8 条公开中文问题
└── figures/                 本文使用的真实核验截图
```

教程、脚本、样例输入、截图和汇总表发布在[公开代码仓库](https://github.com/qiyuefffs/llm-serving-diagnosis)。魔搭临时工作区里还保存着完整原始结果，但它不是公开下载地址；原始证据和全新环境复现仍需补齐，不能仅凭仓库现有文件宣称已经完成投稿验收。

下面的命令都在 **魔搭 Notebook 的 Linux 终端**执行。不要把 `root@...#` 或 `case$` 这样的提示符一并复制。新复现的工作目录是 `/mnt/workspace/llm-serving-diagnosis/cases/llama-cpp-flash-attention`。原始实验在仓库根目录运行，历史截图里的旧路径保留；目录整理不表示已重新完成 GPU 实验。

## 第一步：打开终端，确认机器符合要求

先在浏览器打开 [魔搭 Notebook 工作区](https://www.modelscope.cn/code/workspace) 并登录。创建或启动一台 GPU 实例；本次记录所用的是 A10 24GB。等待页面显示“实例运行中”，再进入 Code Editor。编辑器底部通常有“终端”面板；若面板没有显示，可以用顶部的“终端”菜单新建终端，或按 `Ctrl+J` 显示底部面板。看到类似 `root@...:/mnt/workspace#` 的提示符后，才在这里粘贴下面的 Linux 命令。不同页面版本的按钮位置可能变化，关键是确认**命令运行在 GPU 实例内**，而不是自己电脑的 PowerShell 中。

先运行：

```bash
nvidia-smi
df -h /mnt/workspace
python3 --version
```

`nvidia-smi` 会显示 GPU 名称、显存和驱动。本文实测看到 `NVIDIA A10`、`24564 MiB`、驱动 `550.54.15`。`df -h` 用来确认工作区还有足够的磁盘空间；`python3 --version` 确认 Python 3 可用。如果第一条命令找不到 GPU，先检查 Notebook 是否选了 GPU 实例，暂时不要下载模型。

接着安装下载和编译所需工具：

```bash
apt-get update
apt-get install -y aria2 cmake g++ make python3-pip curl git
```

这里的 `aria2` 用来并发下载大文件，`cmake`、`g++`、`make` 用来编译 llama.cpp，`curl` 用来检查服务接口。安装结束后没有报错，才能进入下一步。不同 Notebook 镜像的系统包或权限可能不同；报错时先记录完整终端输出。

## 第二步：准备项目文件，看看测试问题是什么

在**云端终端**运行下面的命令，直接从公开仓库取得教程、脚本和测试输入：

```bash
cd /mnt/workspace
git clone https://github.com/qiyuefffs/llm-serving-diagnosis.git
cd /mnt/workspace/llm-serving-diagnosis/cases/llama-cpp-flash-attention
ls scripts data
```

`ls` 正常应列出四个脚本和一个 `workload.jsonl`。若仓库已经存在，不要再次克隆到同一位置；进入现有仓库的 `cases/llama-cpp-flash-attention` 子目录并核对文件。旧版工作区可能还保存原始实验结果，应先备份再整理，避免覆盖。网页 IDE 上传曾失败，因此公开仓库是读者优先使用的获取方式。

`workload.jsonl` 里每行是一道问题。脚本会把它们分成短问题和较长问题，分别测量。运行：

```bash
wc -l data/workload.jsonl
python3 -c 'import json,collections; x=[json.loads(s) for s in open("data/workload.jsonl",encoding="utf-8")]; print(collections.Counter(r["bucket"] for r in x)); print([r["id"] for r in x])'
sha256sum data/workload.jsonl
```

应该看到 **8 行**，`short` 与 `long` 各 **4 条**，ID 为 `s01` 到 `s04`、`l01` 到 `l04`。SHA256 应为 `18de6bb66f8cfe3e5dcad5df776cc200728c564aa781516dd5670007d73571f3`。这些是作者编写的公开部署问题，用于模拟真实的验收需求，不含客户数据，也不冒充生产流量。

![输入文件校验：8 行问题，两类各 4 条，以及 SHA256。](figures/00-workload-check.png)

*图 1. 用 `wc`、Python 和 `sha256sum` 核对测试输入。截图中的结果是对本次实验输入文件的事后核验。*

## 第三步：下载模型并编译推理服务

我们用固定的模型和 llama.cpp 版本做比较，避免两次测试的差异来自换模型或换程序。模型来自 [Abiray/Qwen3.8-27B-Q4_K_M-GGUF](https://www.modelscope.cn/models/Abiray/Qwen3.8-27B-Q4_K_M-GGUF)，文件名为 `Qwen3.8-27B-Q4_K_M.gguf`。推理引擎固定为 [llama.cpp b10430](https://github.com/ggml-org/llama.cpp/tree/b10430)。

在项目目录运行：

```bash
cd /mnt/workspace/llm-serving-diagnosis/cases/llama-cpp-flash-attention
bash scripts/setup.sh
```

脚本会做四件事：用 `aria2c -x 8 -s 8` 开 8 个连接下载模型；下载固定版本的 llama.cpp 源码；在当前 Case 目录准备 CUDA 12.4 工具链；编译 `build-cuda12/bin/llama-server`。本次 A10 使用 CUDA 12.4 实际跑通，实例自带的 CUDA 13.0 曾引起兼容问题，所以脚本使用局部的 CUDA 12.4。`nvidia-smi` 报告的兼容能力不等于已安装的工具链版本，复现时不要随意更改这里的固定版本。脚本默认工作目录由自身位置决定。

下载的模型实际大小为 **16,810,714,400 字节**。下载断开时，`aria2` 的 `-c` 参数支持续传；重新运行同一脚本前先看原报错。模型和源码包都会检查 SHA256，文件不匹配时不能继续拿来做对照。

脚本完成后，运行下面三条检查命令。第一条把局部 CUDA 库放到当前终端的运行库搜索路径最前面；**每次新开终端都要重新执行这条 `export`**：

```bash
cd /mnt/workspace/llm-serving-diagnosis/cases/llama-cpp-flash-attention
export LD_LIBRARY_PATH="$PWD/cuda12/cuda_nvcc-linux-x86_64-12.4.131-archive/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
./build-cuda12/bin/llama-server --help >/dev/null && echo "llama-server: OK"
sha256sum models/Qwen3.8-27B-Q4_K_M.gguf
```

看到 `llama-server: OK` 表示可执行文件可以启动。模型 SHA256 应为 `6a96cc760fc65cc6b9ea7f1922e3ff8b2a48c09f209456f23bbae9ef7032c867`。计算 16.8GB 文件的哈希可能要等一会儿；终端暂时没有输出不一定是卡住。模型来源、文件哈希和版本必须一致，后面的速度才能合理对照。

![A10 GPU、llama-server 可执行文件和模型 SHA256 的核验输出。](figures/01-environment-model-hash.png)

*图 2. A10、驱动版本、`llama-server: OK` 和权重哈希。画面是命令完成后的状态，执行命令见上方。*

**关于构建证据的真实情况**：本次云端 `logs/build-cuda12.log` 留有早期一次编译失败的记录，不能当成成功证明。修正后，二进制通过 `--help` 检查，也实际加载模型并提供服务；但成功构建的完整终端日志没有留存。`setup.sh` 是根据本次成功的操作整理出的入口，尚未在第二个全新实例从头执行。正式投稿前必须补做这次全新环境验证。

## 第四步：先按默认对照配置启动服务

这里的“默认对照”指 **Flash Attention 关闭**，记为 `fa_off`。先确认端口没有运行旧服务：

```bash
ps -o pid,args -C llama-server
```

如果没有进程，可以继续。若列出了你之前启动的服务，请先核对它是否属于本项目，再按文末“停服”命令结束；不要直接占用同一个 8000 端口。

执行下面的启动命令：

```bash
mkdir -p logs results
./build-cuda12/bin/llama-server \
  -m models/Qwen3.8-27B-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8000 -ngl 99 -c 4096 -np 2 -fa off \
  > logs/server-fa-off.log 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > logs/server.pid
```

这段命令看着长，但只需抓住几项：

- `-m` 指向刚刚下载并校验的模型文件。
- `--host 127.0.0.1 --port 8000` 让服务只接受本机访问。本文没有设置对外访问所需的认证，**不要把这个端口直接暴露到公网**。
- `-ngl 99` 尝试把模型层放到 GPU；`-c 4096` 是服务总上下文长度；`-np 2` 设置两个并行槽位。日志显示本次每槽实际可用上下文为 2048 token。
- `-fa off` 是本轮对照配置。稍后只把它改成 `on`。
- `> logs/... 2>&1 &` 把日志写入文件，并让服务在后台运行。`logs/server.pid` 保存这个进程的编号，供后面准确停服。

启动后马上访问健康接口，可能先看到 `503 Loading model`。这表示文件还在加载，**不是本轮性能测试失败**。本次从工作区读取权重约用了 3 分钟。可以每隔一会儿检查：

```bash
curl -sS http://127.0.0.1:8000/health
tail -n 12 logs/server-fa-off.log
```

只有当健康接口返回 `{"status":"ok"}`，并且日志显示 `model loaded`、`listening on http://127.0.0.1:8000`，才进入下一步。若等了很久仍是 503，先运行 `ps -p "$(cat logs/server.pid)" -o pid,args`，再读 `tail -n 60 logs/server-fa-off.log`，确认进程没有退出。

## 第五步：先问一句话，再故意发一条错误请求

性能数字只有在服务确实能工作时才有意义。`smoke.py` 会发送一条正常中文问题，再发送一条格式错误的请求；两次返回都存进 `results/smoke.json`：

```bash
python3 scripts/smoke.py --output results/smoke.json
```

本次正常请求返回 HTTP **200**，错误请求把 `messages` 错写成字符串，服务返回 HTTP **400**。这说明接口能响应正常输入，也能拒绝畸形输入。若正常请求不是 200，先返回上一步检查服务；若错误请求反而返回 200，需要记录为异常处理不符合预期。

脚本运行结束会在终端打印一行摘要，例如本次的关键字段是 `"valid_status": 200`、`"valid_elapsed_s": 4.1286` 和 `"malformed_status": 400`。`valid_elapsed_s` 是这一条功能检查请求的耗时，不要把它当成后面 20 次组的 P95。

想再次查看保存的状态码，不必重发请求：

```bash
python3 -c 'import json; x=json.load(open("results/smoke.json")); print("normal",x["valid_response"]["status"],"malformed",x["malformed_response"]["status"])'
```

![smoke.json 中的正常请求 200 与畸形请求 400。](figures/03-smoke-status.png)

*图 3. 功能检查的两个状态码。截图读取的是已经保存的 `smoke.json`；完整请求和响应也在这个文件里。*

这一步也让模型先处理了一次请求。后续测试的是**已加载、预热后的服务**，不把首次加载权重的时间混进请求延迟。

## 第六步：关闭 Flash Attention 时，两个人要等多久？

现在测 `-fa off`。下列命令明确指定了输入文件、结果目录、配置名称、并发数、每组请求次数和生成上限：

```bash
python3 scripts/bench.py --workload data/workload.jsonl --output results \
  --config-id fa_off --concurrency 1 2 --requests 8 --max-tokens 64
```

`--concurrency 1 2` 表示脚本分别模拟一次“一个人提问”和“两个人同时提问”。短问题和较长问题各测一遍，因此共有 **4 组，每组 8 次**，不是总共 8 次。`--max-tokens 64` 把每次生成限制在 64 token，让两种服务配置使用相同的上限。这会截断一些回答，所以本文比较的是**服务性能**，不评价回答是否完整。

脚本运行时会打印每组摘要，并写出这些文件：

```text
results/fa_off/
  metadata.json             记录模型、配置名、并发、请求数
  long_c2.jsonl             较长问题、两路并发，每条请求一行
  long_c2_gpu.json          每秒一次的 GPU 采样
  long_c2_summary.json      这一组的成功率与延迟汇总
  ...                       其他 short/long、并发 1/2 分组
```

例如运行 `cat results/fa_off/long_c2_summary.json`，本次首次测量得到 8/8 成功，TTFT P95 为 **1.7796 秒**。若你得到的数值不同，先看 `successes` 是否等于 `requests`，再看模型哈希、硬件和服务参数。不要只拿一个最快数字判断优化效果。

想看单条请求怎样记录，可以运行：

```bash
sed -n '1p' results/fa_off/long_c2.jsonl
```

输出是一整行 JSON。`request_id` 是这次请求的编号，`prompt_id` 能回到 `data/workload.jsonl` 找到原问题；`status` 是 HTTP 状态码；`ttft_s` 是首段输出等待秒数；`total_s` 是整条请求完成秒数；`prompt_tokens` 与 `completion_tokens` 是实际输入和输出 token 数；`error` 保存失败原因。这个文件应有 8 行，可以用 `wc -l results/fa_off/long_c2.jsonl` 检查。汇总数字要能追溯到这些单条记录。

## 第七步：只打开 Flash Attention，再测相同的问题

先结束上一轮的服务，确认它已经退出：

```bash
kill "$(cat logs/server.pid)"
while kill -0 "$(cat logs/server.pid)" 2>/dev/null; do sleep 1; done
```

然后用相同模型和相同参数重新启动，**唯一改动是末尾的 `-fa on`**：

```bash
./build-cuda12/bin/llama-server \
  -m models/Qwen3.8-27B-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8000 -ngl 99 -c 4096 -np 2 -fa on \
  > logs/server-fa-on.log 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > logs/server.pid
```

同样先等待健康接口返回 `ok`：

```bash
curl -sS http://127.0.0.1:8000/health
ps -p "$(cat logs/server.pid)" -o pid,args
```

`ps` 的命令行应包含 `-fa on`。下面的截图还显示本次服务使用 `-c 4096 -np 2`，并在 `127.0.0.1:8000` 监听：

![开启 Flash Attention 后的运行参数、健康接口和加载日志。](figures/02-server-fa-on-health.png)

*图 4. 优化配置的事后核验。`/health` 返回 `ok`，日志显示模型已加载和每槽 2048 token。*

两次启动命令的历史记录也保留在本次实例中：

![Shell 历史中的 fa off 与 fa on 启动参数。](figures/05-start-command-history.png)

*图 5. 参数切换记录，重点看 `-fa off` 和 `-fa on`。历史记录用于辅助核对，不能代替服务日志和请求结果。*

先按首次测量的相同设置再跑 4 组：

```bash
python3 scripts/bench.py --workload data/workload.jsonl --output results \
  --config-id fa_on --concurrency 1 2 --requests 8 --max-tokens 64
```

本次较长问题、两路并发的 8 次组全部成功，TTFT P95 为 **1.5469 秒**。与 `fa_off` 的 1.7796 秒相比，方向上变快了。但每组只有 8 次，P95 此时等于这 8 次里最慢的一次，所以我们还要做一轮更大的复测。

## 第八步：每组改成 20 次，看看结论是否仍成立

服务现在仍是 `-fa on`。先跑开启配置的复测：

```bash
python3 scripts/bench.py --workload data/workload.jsonl --output results \
  --config-id fa_on_repeat --concurrency 2 --requests 20 --max-tokens 64
cat results/fa_on_repeat/long_c2_summary.json
```

这次只测两路并发，短档和长档各 **20 次**。本次长档结果是 20/20 成功，TTFT P95 **1.5740 秒**，总耗时 P95 **4.5937 秒**，整体输出吞吐 **28.1866 token/s**。

![Flash Attention 开启时，20 次长档请求的汇总 JSON。](figures/06-fa-on-repeat-summary.png)

*图 6. `fa_on_repeat/long_c2_summary.json` 的实际值。`requests` 和 `successes` 都是 20。*

为了避免结论只受测试先后顺序影响，接下来再关回 Flash Attention，重复同样的 20 次测试。先按第七步的 `kill` 命令停服，再按第四步的 `-fa off` 启动命令重新启动；等 `/health` 为 `ok` 后执行：

```bash
python3 scripts/bench.py --workload data/workload.jsonl --output results \
  --config-id fa_off_repeat --concurrency 2 --requests 20 --max-tokens 64
cat results/fa_off_repeat/long_c2_summary.json
```

本次长档结果为 20/20 成功，TTFT P95 **1.7893 秒**，总耗时 P95 **4.8071 秒**，整体输出吞吐 **26.8582 token/s**。

![Flash Attention 关闭时，20 次长档请求的汇总 JSON。](figures/04-fa-off-repeat-summary.png)

*图 7. `fa_off_repeat/long_c2_summary.json` 的实际值。和图 6 使用相同的输入档、并发与输出上限。*

本次真正的运行顺序是 **off 首轮 → on 首轮 → on 复测 → off 复测**。按这个顺序执行，读者才能把自己的四份结果与本文一一对应。两轮方向一致，但仍不能据此断言所有硬件或更长输入都一定有同样收益。

## 第九步：让脚本整理结果，而不是凭感觉挑配置

最后运行报告脚本：

```bash
python3 scripts/report.py results --bucket long --concurrency 2 \
  --max-ttft-p95-s 2 --max-total-p95-s 5 --min-success-rate 1
```

这条命令预先设了三个验收门槛：长档两路并发的请求**全部成功**，TTFT P95 **不超过 2 秒**，完整请求耗时 P95 **不超过 5 秒**。脚本只读取已保存的 `_summary.json`，不会猜测未测试配置的表现。它会生成：

- `results/summary.csv`：所有 12 个实测分组的汇总表。
- `results/recommendation.json`：达标配置、推荐配置及它对应的原始汇总文件。
- `results/report.md`：适合直接阅读的文字报告。

检查文件和推荐结果：

```bash
wc -l results/summary.csv
cat results/recommendation.json
sed -n '1,24p' results/report.md
```

本次 CSV 有 **13 行**，其中 1 行是表头、12 行是实测分组。四个目标配置都过了门槛；按 TTFT P95 从小到大排序，报告推荐首次测量的 `fa_on`。报告会给出它对应的 `fa_on/long_c2_summary.json`，再可从同目录的 `long_c2.jsonl` 核对逐请求记录。

![报告中的门槛、12 组数据、推荐配置和 CSV 行数。](figures/07-report-selection.png)

*图 8. 从 `recommendation.json` 读取的验收结果。截图是对已生成报告的核验。*

## 最终结果：打开以后到底快了多少？

只看较长问题、两路并发这个预先确定的目标，四次组的结果如下。表中的吞吐是**整组每秒输出的 token 数**，不是一个用户单独的生成速度：

| 测试轮次 | Flash Attention | 成功请求 | 首段输出等待 P95 | 完整请求 P95 | 整组输出吞吐 |
| --- | --- | ---: | ---: | ---: | ---: |
| 首轮，每组 8 次 | 关闭 | 8/8 | 1.7796 秒 | 4.8450 秒 | 27.1245 token/s |
| 首轮，每组 8 次 | 开启 | 8/8 | 1.5469 秒 | 4.6099 秒 | 28.4047 token/s |
| 复测，每组 20 次 | 关闭 | 20/20 | 1.7893 秒 | 4.8071 秒 | 26.8582 token/s |
| 复测，每组 20 次 | 开启 | 20/20 | 1.5740 秒 | 4.5937 秒 | 28.1866 token/s |

以 20 次复测为例，开启后 TTFT P95 下降 **0.2153 秒，约 12.0%**；整组输出吞吐提高约 **4.9%**。`nvidia-smi` 每秒采样到的显存峰值从 **16111 MiB** 变为 **16063 MiB**，相差 48 MiB。采样可能漏掉更短暂的峰值，所以不能把这 48 MiB 理解成精确节省量。

本实验回答的是“这台 A10 上、这批短输出问题、两路并发时，这项设置是否改善了服务性能”。它**没有**证明模型答得更准，也没有测试手机、个人电脑、长达 1600 token 的真实输入或更多人同时请求。较长档的问题正文中虽然提到了“约 1600 token”的场景，实际请求只有约 **199 到 229 个输入 token**；一些输出因 `max_tokens=64` 以 `finish_reason=length` 结束。不能把这些被截断的答案当作完整业务建议。

## 如何判断自己有没有复现成功？

按下面顺序检查，比只看最终表格更可靠：

1. `nvidia-smi` 能识别 GPU；模型 SHA256 与本文一致；`llama-server --help` 能成功运行。
2. 服务 `/health` 返回 `{"status":"ok"}`，`ps` 显示的 `-fa off/on` 与当前轮次一致。
3. `smoke.py` 的正常请求是 200，畸形请求是 400。
4. 四个配置目录都保存了 `metadata.json`、逐请求 `.jsonl`、GPU 采样和 `_summary.json`；每组成功数等于请求数。
5. `summary.csv` 有 12 个数据行，`recommendation.json` 能追到同目录的原始汇总文件。

速度**不必与本文小数点后四位完全一致**。GPU 时钟、温度、邻近任务、文件缓存都可能造成差异。先确认功能与输入一致，再比较两种配置的相对趋势；如果方向不同，保存原始 JSONL 和日志，说明实际观察，不要强行写成“优化成功”。

## 遇到问题怎么办？

**`nvidia-smi` 正常，编译却提示 CUDA 不兼容。** 检查驱动、`nvcc` 与实际加载的运行库。本次 CUDA 12.4 方案跑通，实例预装的 CUDA 13.0 曾无法初始化 GPU；这不表示 `nvidia-smi` 的版本字段就是已安装工具链版本。使用 `setup.sh` 的局部 CUDA 12.4，重新进入终端后记得执行前文的 `LD_LIBRARY_PATH` 设置。不要把原始失败日志当成功截图。

**模型文件已经下载，但哈希不一致。** 不要启动服务。检查文件是否下全，再用脚本的 `aria2` 续传功能处理；仍不一致时应重新取得正确文件。换了模型，本文的速度就不能直接对照。

**刚启动时健康接口是 503。** 先等待大文件加载，再看 `tail -n 60 logs/server-fa-off.log` 或 `server-fa-on.log`。进程已经退出、日志有错误时再排查；不要把冷启动等待算进 TTFT。

**提示 8000 端口已被占用。** 用 `ps -o pid,args -C llama-server` 找到旧进程。确认是本项目上轮的服务后，用 `kill "$(cat logs/server.pid)"` 停掉再启动。不要同时运行两个不同配置的服务，否则测试标签会与实际参数不符。

**显存不足。** 可以尝试减小 `-c` 或 `-np`，但这已经是新的配置。必须重新运行整套测量，不能继续引用本文 A10 的数字。本文服务仅监听 `127.0.0.1`；没有配置 API 密钥和访问控制，不适合直接公开端口。

**报告没有推荐配置。** 这意味着实测组没有同时满足所设门槛。保留报告中的 `none passed`，再根据真实需求调整目标或继续实验，不应仅挑最快的一次当结果。

## 文件、来源和投稿状态

完整代码见本目录 `scripts/`；公开输入见 `data/workload.jsonl`；8 张真实核验截图见 `figures/`；本次转录的 12 组汇总见 `results/observed-summary.csv`。详细的请求字段、P95 算法、采样口径和限制见 [技术附录](CASE_TECHNICAL.md)。模型来源见[魔搭模型页](https://www.modelscope.cn/models/Abiray/Qwen3.8-27B-Q4_K_M-GGUF)，推理程序见 [llama.cpp b10430](https://github.com/ggml-org/llama.cpp/tree/b10430)；CUDA 组件来自 [NVIDIA 官方分发目录](https://developer.download.nvidia.com/compute/cuda/redist/) 与 PyPI 的 `nvidia-*` 包。公开分发前还需核对模型仓库许可证。

云端原始逐请求 JSONL、GPU 采样和日志保存在临时工作目录 `/mnt/workspace/llm-serving-diagnosis`，并打包为 `case-evidence.tar.gz`；公开仓库目前只有汇总转录和截图，没有原始逐请求证据。网页 IDE 的下载没有提供可取得的产物。更重要的是，本次**没有保留成功编译的完整日志，也未在第二个全新实例从头重跑 `setup.sh`**。因此这是一份基于真实测量、可以继续复核的教程草稿，**尚不应声称已经满足社区投稿的全部可复现要求**。投稿前需补做全新环境复现，并在公开仓库提供脱敏后的原始证据。

实验结束后，如果服务仍在运行，可在确认 `logs/server.pid` 属于本项目服务后执行：

```bash
kill "$(cat logs/server.pid)"
```
