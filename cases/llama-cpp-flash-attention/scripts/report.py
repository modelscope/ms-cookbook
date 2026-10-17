#!/usr/bin/env python3
"""Build a report from measured benchmark summaries only."""

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


FIELDS = [
    "config_id", "bucket", "concurrency", "requests", "successes", "success_rate",
    "wall_s", "ttft_p50_s", "ttft_p95_s", "total_p95_s", "request_per_s",
    "output_token_per_s", "peak_gpu_memory_mib", "source_file",
]


def fmt(value):
    return "未取得" if value is None else str(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--bucket", default="long")
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--max-ttft-p95-s", type=float, default=None)
    parser.add_argument("--max-total-p95-s", type=float, default=None)
    parser.add_argument("--min-success-rate", type=float, default=1.0)
    args = parser.parse_args()
    paths = sorted(args.results.glob("*/**/*_summary.json"))
    if not paths:
        parser.error("No measured group summaries found")

    rows = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        rows.append({
            **{key: data.get(key) for key in FIELDS},
            "config_id": path.relative_to(args.results).parts[0],
            "source_file": str(path.relative_to(args.results)),
        })
    args.results.mkdir(parents=True, exist_ok=True)
    with (args.results / "summary.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    candidates = [
        row for row in rows
        if row["bucket"] == args.bucket and row["concurrency"] == args.concurrency
    ]
    passing = [
        row for row in candidates
        if row["success_rate"] is not None
        and row["success_rate"] >= args.min_success_rate
        and (args.max_ttft_p95_s is None or (row["ttft_p95_s"] is not None and row["ttft_p95_s"] <= args.max_ttft_p95_s))
        and (args.max_total_p95_s is None or (row["total_p95_s"] is not None and row["total_p95_s"] <= args.max_total_p95_s))
    ]
    passing.sort(key=lambda row: (row["ttft_p95_s"] or float("inf"), row["total_p95_s"] or float("inf")))
    recommendation = passing[0] if passing else None
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "target": {
            "bucket": args.bucket,
            "concurrency": args.concurrency,
            "max_ttft_p95_s": args.max_ttft_p95_s,
            "max_total_p95_s": args.max_total_p95_s,
            "min_success_rate": args.min_success_rate,
        },
        "measured_groups": len(rows),
        "passing_configurations": [row["config_id"] for row in passing],
        "recommendation": recommendation,
    }
    (args.results / "recommendation.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# llama.cpp 部署性能验收报告",
        "",
        f"生成时间（UTC）：{summary['generated_utc']}",
        f"已测分组：{len(rows)}。目标工作负载：{args.bucket}，并发：{args.concurrency}。",
        f"通过门槛：成功率 >= {args.min_success_rate}，TTFT P95 <= {fmt(args.max_ttft_p95_s)} 秒，完整耗时 P95 <= {fmt(args.max_total_p95_s)} 秒。",
        "",
        "| 配置 | 输入档 | 并发 | 成功率 | TTFT P95(s) | 完整耗时 P95(s) | 输出 tokens/s | 显存峰值(MiB) |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(fmt(row[key]) for key in (
            "config_id", "bucket", "concurrency", "success_rate", "ttft_p95_s",
            "total_p95_s", "output_token_per_s", "peak_gpu_memory_mib",
        )) + " |")
    lines += ["", "## 结论", ""]
    if recommendation:
        lines.append(
            f"在已实测配置中，`{recommendation['config_id']}` 满足所设门槛。"
            f"对应原始汇总：`{recommendation['source_file']}`。"
        )
    else:
        lines.append("已实测配置没有满足全部门槛的方案；需要调整目标或继续测试，不能推断未测试配置达标。")
    lines += [
        "",
        "## 统计口径与限制",
        "",
        "- TTFT 为客户端发送请求到收到第一个非空流式内容的时间，包含本机 HTTP 与排队时间。",
        "- P95 使用最近秩法；每组样本量和逐请求记录保存在同名 JSONL 文件中。",
        "- 输出吞吐率使用服务端 usage 或 `/tokenize` 返回的实际 token 数；缺失时标记为未取得。",
        "- 显存由 `nvidia-smi` 每秒采样，峰值可能漏掉采样间隔内的瞬时尖峰。",
        "- 本报告只比较同一模型与固定提示、采样参数下的已测配置，不代表其他硬件的性能。",
        "",
    ]
    (args.results / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.results / 'summary.csv'} and {args.results / 'report.md'}")
    print("Recommendation:", recommendation["config_id"] if recommendation else "none passed")


if __name__ == "__main__":
    main()
