# llama.cpp Flash Attention 部署性能对照

> Cookbook 投稿材料（Draft）：收录讨论见 [Issue #15](https://github.com/modelscope/ms-cookbook/issues/15)，证据状态与验收清单见 [SUBMISSION.md](SUBMISSION.md)。

从 [新手教程](CASE.md) 开始；[技术附录](CASE_TECHNICAL.md)解释指标口径和实验限制。需要先了解术语，可读[部署基础知识](https://github.com/qiyuefffs/llm-serving-diagnosis/blob/7c3aae64d367e3a5ad5fceb687f4d7204e78d06e/docs/01-deployment-foundations/README.md)。

```bash
cd /mnt/workspace
git clone https://github.com/qiyuefffs/llm-serving-diagnosis.git
cd llm-serving-diagnosis/cases/llama-cpp-flash-attention
```

以上仅获取文件。检查 GPU、安装依赖、下载与编译、启动和测试请按 `CASE.md` 的顺序执行。若已经克隆仓库，直接进入 Case 目录；已有旧版工作区时，先保存运行证据，不要覆盖原始结果。

| 路径 | 内容 |
| --- | --- |
| `scripts/` | 环境与模型准备、功能检查、压测、报告生成 |
| `data/workload.jsonl` | 8 条可公开的部署问题 |
| `figures/` | 8 张实测后的核验截图 |
| `results/observed-summary.csv` | 12 组汇总转录，不是逐请求原始数据 |

原始实验工作区为 `/mnt/workspace/llm-serving-diagnosis`。仓库整理后，新复现的工作目录改为上述 Case 子目录；历史截图中的旧路径保留。`setup.sh` 默认使用自身所在的 Case 目录，仍可通过 `PROJECT` 环境变量指定工作目录。

当前状态：教程草稿。成功构建的完整日志、第二个全新实例从头复现，以及可公开访问的原始 JSONL / GPU 采样 / 日志仍需补齐。此次目录整理不代表又运行了一轮 GPU 实验。
