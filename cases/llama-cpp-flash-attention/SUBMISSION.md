# Cookbook 投稿说明：llama.cpp Flash Attention 性能对照

状态：**Draft，供收录方向与材料审阅；尚未完成复现验收。**

收录讨论：[modelscope/ms-cookbook#15](https://github.com/modelscope/ms-cookbook/issues/15)。本目录提供独立的 Case 材料包；正文从 [CASE.md](CASE.md) 开始阅读，指标定义见 [CASE_TECHNICAL.md](CASE_TECHNICAL.md)。

## 1. 来源与范围

材料来自作者仓库 [qiyuefffs/llm-serving-diagnosis](https://github.com/qiyuefffs/llm-serving-diagnosis)，原始投稿快照为提交 `7c3aae64d367e3a5ad5fceb687f4d7204e78d06e` 的 `cases/llama-cpp-flash-attention/`。脚本、输入、汇总转录和 8 张截图随此目录提供。教程中的获取命令使用该作者仓库；复核本次快照时，在克隆后执行：

```bash
git -C /mnt/workspace/llm-serving-diagnosis checkout 7c3aae64d367e3a5ad5fceb687f4d7204e78d06e
```

本贡献聚焦单卡推理服务的性能测量，不包含作者仓库中另一个部署基础知识章节。当前材料未加入书籍目录或网站路由；收录位置在 Issue 中讨论。若按正式章节接入，正文将放入 `content/source-html/`，再按官方流程生成 Markdown 和站点数据。

## 2. 实测问题与结果

问题：同一张 24GB GPU 加载同一份量化权重时，只切换 Flash Attention，能否改善两路并发的首次非空流式输出等待时间？

完整链路：公开问题 → 下载与哈希校验 → 编译 llama.cpp → 本机推理服务 → 正常/畸形请求 → 固定负载压测 → 汇总与门槛验收。

长档、并发 2、每组 20 请求的已记录结果：

| 配置 | 成功数 | TTFT P95 | 完整请求 P95 | 整组输出吞吐 |
| --- | ---: | ---: | ---: | ---: |
| FA off | 20/20 | 1.7893 s | 4.8071 s | 26.8582 token/s |
| FA on | 20/20 | 1.5740 s | 4.5937 s | 28.1866 token/s |

本次观察到 TTFT P95 约下降 12.0%，吞吐约增加 4.9%。这些数字来自已完成实验的汇总转录与核验截图，本次投稿准备没有重跑 GPU 测试。公开材料暂缺逐请求原始记录，审核者目前不能独立重算这些历史指标。

## 3. 环境与材料核对

| 项目 | 已有记录 | 尚需补充 |
| --- | --- | --- |
| 平台 | 魔搭 GPU Notebook，Linux x86_64 | OS 完整版本、CPU 型号/核数、可用内存 |
| Python | 原始终端记录为 3.12.13；客户端脚本仅使用标准库 | 新复现的环境快照 |
| GPU | NVIDIA A10，24564 MiB，驱动 550.54.15 | 新复现时的 GPU 状态与独占情况 |
| CUDA | 局部 12.4；NVCC 12.4.131、CUDART 12.4.127、cuBLAS 12.4.5.8、CCCL 12.4.127 | 成功构建的完整日志与系统编译工具版本 |
| 引擎 | llama.cpp b10430；A10 架构参数 86 | 从整理后脚本进行一次全新环境复核 |
| 权重 | Abiray/Qwen3.8-27B-Q4_K_M-GGUF，16,810,714,400 字节 | 模型卡、上游来源及许可证确认 |
| 输入 | 作者编写的 8 条公开中文部署问题，short/long 各 4 条 | 无客户数据；不冒充生产流量 |
| 服务 | 127.0.0.1:8000，-ngl 99 -c 4096 -np 2；仅切换 -fa off/on | 公开原始服务日志 |
| 请求 | temperature=0、seed=42、max_tokens=64；首轮 8 次/组，复测 20 次/组 | 公开逐请求 JSONL、GPU 采样和 smoke.json |

固定 SHA256：

- 模型：`6a96cc760fc65cc6b9ea7f1922e3ff8b2a48c09f209456f23bbae9ef7032c867`。
- llama.cpp 源码包：`c93fdbe93170b1cf93027e1a945c66a70bcdfbd272eeedbe8c90afe0a5d55e1`。
- 输入：`18de6bb66f8cfe3e5dcad5df776cc200728c564aa781516dd5670007d73571f3`。

## 4. 证据状态与合并前检查

- [x] 提供按执行顺序组织的教程、完整脚本、公开输入、异常请求处理说明。
- [x] 提供 12 组汇总转录，以及 8 张真实保存状态的核验截图和图注。
- [x] 明确 TTFT、P95、整组吞吐及显存采样口径，限定为 A10 云端实测。
- [ ] 取得并脱敏公开逐请求 JSONL、GPU 采样、服务日志与功能检查响应。
- [ ] 从全新环境执行整理后的 setup.sh，记录完整环境和成功构建日志；现有早期失败日志不能代替成功证明。
- [ ] 核实模型卡、上游及许可证；模型权重不随本目录分发。
- [ ] 若转为 Notebook 展示，按序实际执行并保留输出；不填入虚构的 execution_count 或模型输出。
- [ ] 与维护者确定收录目录、正文 HTML 源文件及网站接入方式；接入后检查桌面与移动端。

复现时的功能门槛：健康接口 ok、正常请求 200、畸形 messages 类型返回 400；每组请求均成功；四个配置目录和报告文件完整。性能门槛：长档并发 2，成功率 100%、TTFT P95 ≤ 2 s、完整请求 P95 ≤ 5 s。即使硬件相同，也应报告实际测量，不以加速比必须相同作为成功条件。

重要边界：所谓长档实际约 199–229 输入 token；64-token 输出上限可能截断回答；未评价答案质量；每秒 GPU 采样不能精确代表瞬时峰值；样本较少，不宣称统计显著。原始云端绝对路径不是公开证据链接。

## 5. 归属与公开范围

脚本、公开样例问题、教程与实验截图由本 Case 整理形成，随作者授权的 Cookbook 贡献提交。截图是对保存状态的真实核验，已隐藏临时实例主机名；不包含账号凭据或客户数据。

外部资源分别适用其自身许可证和分发条款：

- [llama.cpp b10430](https://github.com/ggml-org/llama.cpp/tree/b10430)，[MIT 许可证](https://github.com/ggml-org/llama.cpp/blob/b10430/LICENSE)。
- [量化模型页面](https://www.modelscope.cn/models/Abiray/Qwen3.8-27B-Q4_K_M-GGUF)：许可证与上游归属尚待核实，不据文件名推断官方发布身份或许可证。
- [NVIDIA CUDA Redistributable](https://developer.download.nvidia.com/compute/cuda/redist/) 及相应 PyPI nvidia-* 包：按 NVIDIA 条款获取，不随本贡献附带工具链二进制。

本目录只提交小型代码、文本、截图和汇总转录。生成的模型、缓存、构建目录与未经审阅的运行日志默认忽略。待公开的原始证据应脱敏后显式放入可审阅目录，保留其真实来源和校验信息。
