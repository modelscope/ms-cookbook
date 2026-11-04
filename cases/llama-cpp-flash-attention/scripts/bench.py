#!/usr/bin/env python3
"""Measure a local llama-server with fixed, public request workloads."""

import argparse
import concurrent.futures
import json
import math
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request_json(url, payload=None, timeout=30):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def token_count(base_url, text):
    if not text:
        return 0
    try:
        result = request_json(f"{base_url}/tokenize", {"content": text})
        return len(result["tokens"])
    except (KeyError, HTTPError, URLError, ValueError):
        return None


def gpu_sample():
    command = [
        "nvidia-smi",
        "--query-gpu=memory.used,utilization.gpu,power.draw",
        "--format=csv,noheader,nounits",
    ]
    try:
        line = subprocess.check_output(command, text=True, timeout=10).splitlines()[0]
        values = [value.strip() for value in line.split(",")]
        return {
            "memory_used_mib": float(values[0]),
            "utilization_percent": float(values[1]),
            "power_w": float(values[2]),
        }
    except (FileNotFoundError, IndexError, ValueError, subprocess.SubprocessError):
        return None


def monitor_gpu(stop, samples):
    while not stop.is_set():
        sample = gpu_sample()
        if sample is not None:
            samples.append({"timestamp": time.time(), **sample})
        stop.wait(1)


def stream_request(base_url, model, prompt, prompt_id, max_tokens, timeout, request_id):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": f"实验编号 {request_id}\n{prompt}"}],
        "stream": True,
        "stream_options": {"include_usage": True},
        "max_tokens": max_tokens,
        "temperature": 0,
        "seed": 42,
    }
    request = Request(
        f"{base_url}/v1/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    started = time.perf_counter()
    started_utc = datetime.now(timezone.utc).isoformat()
    first_token_at = None
    chunks = []
    completion_tokens = None
    prompt_tokens = None
    finish_reason = None
    status = None
    error = ""

    try:
        with urlopen(request, timeout=timeout) as response:
            status = response.status
            for raw_line in response:
                line = raw_line.strip()
                if not line.startswith(b"data:"):
                    continue
                data = line[5:].strip()
                if data == b"[DONE]":
                    break
                event = json.loads(data.decode("utf-8"))
                if event.get("usage"):
                    completion_tokens = event["usage"].get("completion_tokens")
                    prompt_tokens = event["usage"].get("prompt_tokens")
                for choice in event.get("choices", []):
                    delta = choice.get("delta") or {}
                    content = delta.get("content") or delta.get("reasoning_content") or ""
                    if content:
                        if first_token_at is None:
                            first_token_at = time.perf_counter()
                        chunks.append(content)
                    finish_reason = choice.get("finish_reason") or finish_reason
    except HTTPError as exc:
        status = exc.code
        error = exc.read(1000).decode("utf-8", errors="replace")
    except (URLError, TimeoutError, ValueError, OSError) as exc:
        error = repr(exc)

    ended = time.perf_counter()
    text = "".join(chunks)
    token_source = "response_usage"
    if completion_tokens is None and text:
        completion_tokens = token_count(base_url, text)
        token_source = "tokenize_endpoint" if completion_tokens is not None else "unavailable"
    success = status == 200 and first_token_at is not None and not error
    return {
        "request_id": request_id,
        "prompt_id": prompt_id,
        "started_utc": started_utc,
        "ended_utc": datetime.now(timezone.utc).isoformat(),
        "success": success,
        "status": status,
        "ttft_s": round(first_token_at - started, 4) if first_token_at else None,
        "total_s": round(ended - started, 4),
        "completion_tokens": completion_tokens,
        "prompt_tokens": prompt_tokens,
        "token_source": token_source,
        "finish_reason": finish_reason,
        "output_text": text,
        "error": error,
    }


def percentile(values, percentage):
    if not values:
        return None
    ordered = sorted(values)
    index = math.ceil(percentage / 100 * len(ordered)) - 1
    return round(ordered[max(0, index)], 4)


def run_group(args, model, bucket, prompts, concurrency, output_dir):
    samples = []
    stop = threading.Event()
    monitor = threading.Thread(target=monitor_gpu, args=(stop, samples), daemon=True)
    monitor.start()
    group_started = time.perf_counter()
    group_id = f"{bucket}_c{concurrency}"
    rows = []
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
            futures = [
                pool.submit(
                    stream_request,
                    args.base_url,
                    model,
                    prompts[index % len(prompts)]["prompt"],
                    prompts[index % len(prompts)]["id"],
                    args.max_tokens,
                    args.timeout,
                    f"{group_id}_{index:03d}",
                )
                for index in range(args.requests)
            ]
            for future in concurrent.futures.as_completed(futures):
                rows.append(future.result())
    finally:
        elapsed = time.perf_counter() - group_started
        stop.set()
        monitor.join(timeout=12)

    rows.sort(key=lambda row: row["request_id"])
    with (output_dir / f"{group_id}.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    (output_dir / f"{group_id}_gpu.json").write_text(
        json.dumps(samples, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    good = [row for row in rows if row["success"]]
    tokens = [row["completion_tokens"] for row in good]
    summary = {
        "group": group_id,
        "bucket": bucket,
        "concurrency": concurrency,
        "requests": len(rows),
        "successes": len(good),
        "success_rate": round(len(good) / len(rows), 4),
        "wall_s": round(elapsed, 4),
        "ttft_p50_s": percentile([row["ttft_s"] for row in good], 50),
        "ttft_p95_s": percentile([row["ttft_s"] for row in good], 95),
        "total_p95_s": percentile([row["total_s"] for row in good], 95),
        "request_per_s": round(len(good) / elapsed, 4),
        "output_token_per_s": round(sum(tokens) / elapsed, 4)
        if tokens and all(value is not None for value in tokens)
        else None,
        "peak_gpu_memory_mib": max((sample["memory_used_mib"] for sample in samples), default=None),
        "errors": [row["error"] for row in rows if row["error"]],
    }
    (output_dir / f"{group_id}_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--workload", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--config-id", required=True)
    parser.add_argument("--concurrency", type=int, nargs="+", default=[1, 2, 4])
    parser.add_argument("--requests", type=int, default=20)
    parser.add_argument("--max-tokens", type=int, default=128)
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    if args.requests < 1 or any(value < 1 for value in args.concurrency):
        parser.error("requests and concurrency must be positive")
    args.base_url = args.base_url.rstrip("/")

    workloads = {}
    for line in args.workload.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            workloads.setdefault(row["bucket"], []).append(row)
    if not workloads:
        parser.error("workload is empty")

    models = request_json(f"{args.base_url}/v1/models")
    model = models["data"][0]["id"]
    output_dir = args.output / args.config_id
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "base_url": args.base_url,
        "config_id": args.config_id,
        "workload": str(args.workload),
        "requests_per_group": args.requests,
        "max_tokens": args.max_tokens,
        "concurrency": args.concurrency,
        "gpu_before": gpu_sample(),
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"model={model} output={output_dir}", flush=True)
    for bucket, prompts in workloads.items():
        for concurrency in args.concurrency:
            summary = run_group(args, model, bucket, prompts, concurrency, output_dir)
            if summary["successes"] == 0:
                raise SystemExit(f"All requests failed in {summary['group']}; see saved errors")


if __name__ == "__main__":
    main()
