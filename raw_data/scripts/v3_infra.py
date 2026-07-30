#!/usr/bin/env python3
"""
Ling-3.0-flash Deep Evaluation v3 — Shared infrastructure.
Implements the JSONL logging format required by the v3 prompt:
- uuid per log entry
- ISO 8601 timestamp
- phase, test_id, run
- provider, endpoint, model
- system_prompt, user_prompt, tools, parameters
- response (content, reasoning, tool_calls, finish_reason)
- usage (prompt/completion/reasoning/total tokens)
- latency_ms, ttft_ms, status_code, error, observations

API keys are loaded from environment variables and are never hardcoded:
  OPENROUTER_API_KEYS (comma-separated, for rotation)
  OPENROUTER_API_KEY (single key)
"""
import os, sys, json, time, uuid, hashlib, traceback
import requests
from datetime import datetime, timezone


def _load_keys_from_env():
    """Load API keys from environment variables.

    Priority:
      1. OPENROUTER_API_KEYS (comma-separated, supports multiple keys for rotation)
      2. OPENROUTER_API_KEY (single key)

    Returns:
      list[str]: API key strings. Empty list if none configured.
    """
    keys = []
    multi = os.environ.get("OPENROUTER_API_KEYS", "").strip()
    if multi:
        keys = [k.strip() for k in multi.split(",") if k.strip()]
    if not keys:
        single = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if single:
            keys = [single]
    return keys


ALL_KEYS = _load_keys_from_env()

if not ALL_KEYS:
    print(
        "WARNING: No API keys configured. Set OPENROUTER_API_KEYS or OPENROUTER_API_KEY "
        "environment variable before running tests.",
        file=sys.stderr,
    )


def key_id(k):
    """Return first 8 chars of sha256(key) — never expose the actual key."""
    return hashlib.sha256(k.encode()).hexdigest()[:8]


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
LING_MODEL = "inclusionai/ling-3.0-flash:free"

# Output directory for JSONL logs. Override with LING3_LOGS_DIR env var.
LOGS_DIR = os.environ.get("LING3_LOGS_DIR", "./logs")


class KeyRotator:
    def __init__(self, keys):
        self.keys = keys
        self.idx = 0
        self.cooldowns = {i: 0 for i in range(len(keys))}
    def next_key(self):
        now = time.time()
        for offset in range(len(self.keys)):
            i = (self.idx + offset) % len(self.keys)
            if self.cooldowns[i] <= now:
                self.idx = (i + 1) % len(self.keys)
                return i, self.keys[i]
        soonest = min(self.cooldowns.values())
        wait = max(1, soonest - now)
        time.sleep(wait)
        return self.next_key()
    def mark_rate_limited(self, idx, seconds=60):
        self.cooldowns[idx] = time.time() + seconds

ROTATOR = KeyRotator(ALL_KEYS) if ALL_KEYS else None


def call_ling_v3(user_prompt, system_prompt=None, max_tokens=8192, temperature=0, seed=42,
                 reasoning_mode="thinking", effort="medium", tools=None, tool_choice=None,
                 timeout=60, retries=3, provider="openrouter", test_id="", run=1, phase="",
                 observations=""):
    """
    Call Ling-3.0-flash with full v3 logging.
    reasoning_mode: "thinking" (default) | "non-thinking" (sets reasoning.enabled=false)
    effort: "low"|"medium"|"high" (only for thinking mode)
    Returns: (log_entry_dict, response_dict)
    """
    if ROTATOR is None:
        raise RuntimeError(
            "No API keys configured. Set OPENROUTER_API_KEYS environment variable."
        )

    log_entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
        "test_id": test_id,
        "run": run,

        "provider": provider,
        "endpoint": OPENROUTER_URL,
        "model": LING_MODEL,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "tools": tools or [],
        "parameters": {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "seed": seed,
            "reasoning": {"enabled": True, "effort": effort} if reasoning_mode == "thinking" else {"enabled": False},
        },
        "response": {
            "content": "",
            "reasoning": "",
            "tool_calls": [],
            "finish_reason": None,
        },
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "reasoning_tokens": 0,
            "total_tokens": 0,
        },
        "latency_ms": 0,
        "ttft_ms": 0,
        "status_code": 0,
        "error": None,
        "observations": observations,
    }

    last_err = None
    for attempt in range(retries):
        key_idx, key = ROTATOR.next_key()

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/frangelbarrera/Ling-3-flash-evaluation",
            "X-Title": "Ling-3 Independent Eval v3",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        payload = {
            "model": LING_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if seed is not None:
            payload["seed"] = seed
        if reasoning_mode == "non-thinking":
            payload["reasoning"] = {"enabled": False}
        else:
            payload["reasoning"] = {"enabled": True, "effort": effort}
        if tools:
            payload["tools"] = tools
        if tool_choice:
            payload["tool_choice"] = tool_choice

        try:
            t0 = time.time()
            r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=timeout)
            latency_ms = int((time.time() - t0) * 1000)
            log_entry["latency_ms"] = latency_ms
            log_entry["status_code"] = r.status_code
            if r.status_code == 429:
                ROTATOR.mark_rate_limited(key_idx, 60)
                last_err = f"429 rate_limited key#{key_idx}"
                log_entry["error"] = last_err
                time.sleep(3)
                continue
            if r.status_code == 402:
                ROTATOR.mark_rate_limited(key_idx, 120)
                last_err = f"402 payment_required key#{key_idx}"
                log_entry["error"] = last_err
                time.sleep(2)
                continue
            if r.status_code >= 500:
                last_err = f"{r.status_code} server_error"
                log_entry["error"] = last_err
                time.sleep(5)
                continue
            if r.status_code != 200:
                last_err = f"{r.status_code}: {r.text[:300]}"
                log_entry["error"] = last_err
                time.sleep(2)
                continue
            data = r.json()
            choice = (data.get("choices") or [{}])[0]
            msg = choice.get("message", {})
            log_entry["response"]["content"] = msg.get("content") or ""
            log_entry["response"]["reasoning"] = (msg.get("reasoning") or "") if isinstance(msg, dict) else ""
            log_entry["response"]["tool_calls"] = msg.get("tool_calls") or []
            log_entry["response"]["finish_reason"] = choice.get("finish_reason")
            u = data.get("usage", {}) or {}
            log_entry["usage"] = {
                "prompt_tokens": u.get("prompt_tokens", 0),
                "completion_tokens": u.get("completion_tokens", 0),
                "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens", 0),
                "total_tokens": u.get("total_tokens", 0),
            }
            log_entry["error"] = None
            return log_entry, data
        except requests.exceptions.Timeout:
            last_err = "timeout"
            log_entry["error"] = last_err
            time.sleep(3)
        except Exception as e:
            last_err = f"exc: {e}"
            log_entry["error"] = last_err
            time.sleep(2)
    log_entry["error"] = last_err
    return log_entry, None


def write_jsonl(log_entry, phase_filename):
    """Append a log entry to the JSONL file for the given phase."""
    path = os.path.join(LOGS_DIR, phase_filename)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def write_log(log_entry, phase_filename):
    """Wrapper for write_jsonl that takes a single log entry."""
    write_jsonl(log_entry, phase_filename)


def _self_check():
    """Print configuration status when run directly: python3 v3_infra.py"""
    print(f"Ling-3 v3 infrastructure")
    print(f"  Model: {LING_MODEL}")
    print(f"  Endpoint: {OPENROUTER_URL}")
    print(f"  Logs dir: {LOGS_DIR}")
    print(f"  API keys configured: {len(ALL_KEYS)} (via OPENROUTER_API_KEYS env var)")
    if not ALL_KEYS:
        print("  ⚠️  No API keys found. Set OPENROUTER_API_KEYS before running tests.")
    else:
        print(f"  Key IDs: {[key_id(k) for k in ALL_KEYS]}")


if __name__ == "__main__":
    _self_check()
