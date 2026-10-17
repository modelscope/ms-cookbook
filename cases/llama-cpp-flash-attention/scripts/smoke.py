#!/usr/bin/env python3
"""Save functional and malformed-request evidence for a local llama-server."""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def call(url, payload=None):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=data, headers={"Content-Type": "application/json"})
    started = time.perf_counter()
    try:
        with urlopen(request, timeout=300) as response:
            status = response.status
            body = response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        status = exc.code
        body = exc.read().decode("utf-8", errors="replace")
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        parsed = body
    return {"status": status, "elapsed_s": round(time.perf_counter() - started, 4), "body": parsed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    models = call(f"{base}/v1/models")
    model = models["body"]["data"][0]["id"]
    valid = {
        "model": model,
        "messages": [{"role": "user", "content": "请用一句话说明首字延迟 TTFT 的含义。"}],
        "temperature": 0,
        "seed": 42,
        "max_tokens": 256,
    }
    malformed = {"model": model, "messages": "not-a-message-list", "max_tokens": 16}
    result = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "models": models,
        "valid_request": valid,
        "valid_response": call(f"{base}/v1/chat/completions", valid),
        "malformed_request": malformed,
        "malformed_response": call(f"{base}/v1/chat/completions", malformed),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    valid_response = result["valid_response"]
    malformed_response = result["malformed_response"]
    print(json.dumps({
        "model": model,
        "valid_status": valid_response["status"],
        "valid_elapsed_s": valid_response["elapsed_s"],
        "malformed_status": malformed_response["status"],
        "output": str(args.output),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
