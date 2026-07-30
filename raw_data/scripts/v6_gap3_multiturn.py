#!/usr/bin/env python3
"""
GAP 3: MULTI-TURN CODING LOOP - spec-driven pattern (the brief's recommendation)
5 tareas × 6 turnos = 30 requests
Pattern: spec → restate → test → fix → iterate
"""
import os
import sys, os, time, json, uuid, hashlib
import requests
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v3_infra import ALL_KEYS, ROTATOR

PHASE = "v6_multiturn"
LOG_FILE = os.environ.get("LING3_LOG_FILE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ling3_v3", "logs", "v6_phase_multiturn.jsonl"))
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
LING_MODEL = "inclusionai/ling-3.0-flash:free"

def log(m): print(m, flush=True)

def call_multi_turn(messages, max_tokens=8192, test_id="", turn=1, observations=None):
    log_entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": PHASE, "test_id": test_id, "run": 1,

        "provider": "openrouter", "model": LING_MODEL,
        "messages": messages, "tools_sent": [], "tool_choice": "none",
        "parameters": {"max_tokens": max_tokens, "temperature": 0, "seed": 42,
                       "reasoning": {"enabled": True, "effort": "medium"}},
        "response": {"content": "", "tool_calls": [], "finish_reason": None},
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0, "total_tokens": 0},
        "latency_ms": 0, "status_code": 0, "error": None,
        "observations": observations or {"turn": turn}
    }
    last_err = None
    for attempt in range(3):
        key_idx, key = ROTATOR.next_key()

        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                   "HTTP-Referer": "https://github.com/frangelbarrera/Ling-3-flash-evaluation",
                   "X-Title": "Ling-3 Independent Eval v6"}
        payload = {"model": LING_MODEL, "messages": messages,
                   "max_tokens": max_tokens, "temperature": 0, "seed": 42,
                   "reasoning": {"enabled": True, "effort": "medium"}}
        try:
            t0 = time.time()
            r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=120)
            log_entry["latency_ms"] = int((time.time() - t0) * 1000)
            log_entry["status_code"] = r.status_code
            if r.status_code == 429:
                ROTATOR.mark_rate_limited(key_idx, 60)
                last_err = f"429 key#{key_idx}"; log_entry["error"] = last_err
                time.sleep(3); continue
            if r.status_code != 200:
                last_err = f"{r.status_code}: {r.text[:200]}"; log_entry["error"] = last_err
                time.sleep(2); continue
            data = r.json()
            choice = (data.get("choices") or [{}])[0]
            msg = choice.get("message", {})
            log_entry["response"]["content"] = msg.get("content") or ""
            log_entry["response"]["finish_reason"] = choice.get("finish_reason")
            u = data.get("usage", {}) or {}
            log_entry["usage"] = {
                "prompt_tokens": u.get("prompt_tokens", 0),
                "completion_tokens": u.get("completion_tokens", 0),
                "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens", 0),
                "total_tokens": u.get("total_tokens", 0),
            }
            return log_entry
        except requests.exceptions.Timeout:
            last_err = "timeout"; log_entry["error"] = last_err
            time.sleep(5)
        except Exception as e:
            last_err = f"exc: {e}"; log_entry["error"] = last_err
            time.sleep(2)
    log_entry["error"] = last_err
    return log_entry

def write_jsonl(log_entry, path=LOG_FILE):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

def already_logged(test_id, path=LOG_FILE):
    if not os.path.exists(path): return False
    target = f'"test_id": "{test_id}"'
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if target in line:
                return True
    return False

# 5 coding tasks (spec-driven)
TASKS = [
    ("cli_todo_python", "Build a CLI todo app. Commands: add <task>, list, done <id>. Storage: JSON file at ~/.todo.json. Use argparse.",
     "Test failure: when running `python todo.py add 'buy milk'`, the script crashes with `FileNotFoundError: ~/.todo.json` because the file doesn't exist on first run. Fix this.",
     "Now refactor for cleaner code: extract storage functions to a separate TodoStore class.",
     "Summarize all changes you made across all turns."),
    ("rate_limiter_ts", "Implement a TokenBucketRateLimiter class in TypeScript. Constructor takes (rate: number, burst: number). Method: tryAcquire(): boolean. Use token bucket algorithm.",
     "Test failure: when calling tryAcquire() 100 times in a tight loop with rate=10, burst=20, all 100 succeed (should be max 20). The bucket doesn't refill correctly. Fix.",
     "Now refactor: add JSDoc, type safety, and a method to peek at available tokens without acquiring.",
     "Summarize all changes you made across all turns."),
    ("http_cache_python", "Create a WSGI middleware that caches GET responses. Cache key: URL. Eviction: LRU with max 1000 entries. Respect Cache-Control max-age. Support ETag conditional requests.",
     "Test failure: when the same URL is hit twice, both return 200 (second should return 304 with ETag). The ETag conditional check is missing. Fix.",
     "Now refactor: add thread safety with a lock, and a max_size parameter.",
     "Summarize all changes you made across all turns."),
    ("markdown_go", "Write a Go function ConvertMarkdownToHTML(input string) string. Support: # H1-H6, **bold**, *italic*, `inline code`, ```code blocks```, [text](url). Escape HTML entities.",
     "Test failure: when input is `<script>alert('xss')</script>`, the output contains the unescaped script tag. The HTML escaping is broken. Fix.",
     "Now refactor: add support for nested lists (- and 1.) and blockquotes (> text).",
     "Summarize all changes you made across all turns."),
    ("config_rust", "Create a Config struct in Rust that loads from TOML file. Support env var override (CONFIG_KEY=value). Validate types at load time. Return Result<Config, ConfigError>.",
     "Test failure: when env var CONFIG_PORT=abc (string instead of u16), the load panics instead of returning Err(ConfigError::InvalidType). Fix.",
     "Now refactor: add support for nested config (database.url, database.pool_size) and a Default impl.",
     "Summarize all changes you made across all turns."),
]

def run_task(task_id, spec, test_failure, refactor_prompt, final_prompt):
    """Run 6 turns for a task."""
    log(f"\n--- Task: {task_id} ---")
    base_id = task_id
    # Track conversation history
    messages = []
    cumulative_tokens = 0
    cumulative_latency = 0

    # Turn 1: Spec — ask for restate + file list
    if not already_logged(f"{base_id}_turn1"):
        t1_prompt = f"Here is a spec for a coding task:\n\n{spec}\n\nPlease restate the spec in your own words and list the files you would create/modify. Don't write code yet."
        messages.append({"role": "user", "content": t1_prompt})
        log_t1 = call_multi_turn(messages, test_id=f"{base_id}_turn1", turn=1,
                                 observations={"turn": 1, "task": task_id, "action": "restate_spec"})
        content = log_t1["response"]["content"]
        # Check if restated
        spec_keywords = [w for w in spec.split() if len(w) > 4][:5]
        restated = sum(1 for k in spec_keywords if k.lower() in content.lower()) >= 3
        log_t1["observations"]["spec_restateed_correctly"] = restated
        log_t1["observations"]["cumulative_tokens"] = log_t1["usage"]["total_tokens"]
        log(f"  Turn 1 (restate): chars={len(content)} restated={restated} prompt_tk={log_t1['usage']['prompt_tokens']}")
        write_jsonl(log_t1)
        messages.append({"role": "assistant", "content": content})
        cumulative_tokens += log_t1["usage"]["total_tokens"]
        cumulative_latency += log_t1["latency_ms"]
        time.sleep(0.5)
    else:
        log(f"  [skip] {base_id}_turn1")
        # Need to load previous content from log to continue
        prev = None
        with open(LOG_FILE) as f:
            for line in f:
                le = json.loads(line)
                if le["test_id"] == f"{base_id}_turn1":
                    prev = le
                    break
        if prev:
            messages.append({"role": "user", "content": prev["messages"][0]["content"]})
            messages.append({"role": "assistant", "content": prev["response"]["content"]})
            cumulative_tokens += prev["usage"]["total_tokens"]

    # Turn 2: Implementation
    if not already_logged(f"{base_id}_turn2"):
        t2_prompt = "Now please implement the code. Provide the full code in a code block."
        messages.append({"role": "user", "content": t2_prompt})
        log_t2 = call_multi_turn(messages, test_id=f"{base_id}_turn2", turn=2,
                                 observations={"turn": 2, "task": task_id, "action": "implementation"})
        content = log_t2["response"]["content"]
        # Check if has code block
        has_code = "```" in content
        log_t2["observations"]["code_syntactically_valid"] = has_code
        log_t2["observations"]["cumulative_tokens"] = cumulative_tokens + log_t2["usage"]["total_tokens"]
        log(f"  Turn 2 (impl): chars={len(content)} has_code={has_code} r_tk={log_t2['usage']['reasoning_tokens']}")
        write_jsonl(log_t2)
        messages.append({"role": "assistant", "content": content})
        cumulative_tokens += log_t2["usage"]["total_tokens"]
        cumulative_latency += log_t2["latency_ms"]
        time.sleep(0.5)
    else:
        log(f"  [skip] {base_id}_turn2")
        prev = None
        with open(LOG_FILE) as f:
            for line in f:
                le = json.loads(line)
                if le["test_id"] == f"{base_id}_turn2":
                    prev = le; break
        if prev: messages.append({"role": "assistant", "content": prev["response"]["content"]})

    # Turn 3: Test failure feedback
    if not already_logged(f"{base_id}_turn3"):
        t3_prompt = f"I ran tests on your code and got this failure:\n\n{test_failure}\n\nPlease analyze the failure and propose a fix. Don't rewrite the entire code yet, just identify the bug and describe the fix."
        messages.append({"role": "user", "content": t3_prompt})
        log_t3 = call_multi_turn(messages, test_id=f"{base_id}_turn3", turn=3,
                                 observations={"turn": 3, "task": task_id, "action": "test_failure_analysis"})
        content = log_t3["response"]["content"]
        log_t3["observations"]["analyzed_failure"] = len(content) > 100
        log_t3["observations"]["cumulative_tokens"] = cumulative_tokens + log_t3["usage"]["total_tokens"]
        log(f"  Turn 3 (test fail): chars={len(content)} r_tk={log_t3['usage']['reasoning_tokens']}")
        write_jsonl(log_t3)
        messages.append({"role": "assistant", "content": content})
        cumulative_tokens += log_t3["usage"]["total_tokens"]
        time.sleep(0.5)
    else:
        log(f"  [skip] {base_id}_turn3")
        prev = None
        with open(LOG_FILE) as f:
            for line in f:
                le = json.loads(line)
                if le["test_id"] == f"{base_id}_turn3":
                    prev = le; break
        if prev: messages.append({"role": "assistant", "content": prev["response"]["content"]})

    # Turn 4: Apply fix
    if not already_logged(f"{base_id}_turn4"):
        t4_prompt = "Now apply the fix. Provide the corrected code in a code block."
        messages.append({"role": "user", "content": t4_prompt})
        log_t4 = call_multi_turn(messages, test_id=f"{base_id}_turn4", turn=4,
                                 observations={"turn": 4, "task": task_id, "action": "apply_fix"})
        content = log_t4["response"]["content"]
        has_code = "```" in content
        log_t4["observations"]["fix_applied"] = has_code
        log_t4["observations"]["cumulative_tokens"] = cumulative_tokens + log_t4["usage"]["total_tokens"]
        log(f"  Turn 4 (fix): chars={len(content)} has_code={has_code} r_tk={log_t4['usage']['reasoning_tokens']}")
        write_jsonl(log_t4)
        messages.append({"role": "assistant", "content": content})
        cumulative_tokens += log_t4["usage"]["total_tokens"]
        time.sleep(0.5)
    else:
        log(f"  [skip] {base_id}_turn4")

    # Turn 5: Refactor
    if not already_logged(f"{base_id}_turn5"):
        t5_prompt = refactor_prompt
        messages.append({"role": "user", "content": t5_prompt})
        log_t5 = call_multi_turn(messages, test_id=f"{base_id}_turn5", turn=5,
                                 observations={"turn": 5, "task": task_id, "action": "refactor"})
        content = log_t5["response"]["content"]
        has_code = "```" in content
        log_t5["observations"]["refactor_provided"] = has_code
        log_t5["observations"]["cumulative_tokens"] = cumulative_tokens + log_t5["usage"]["total_tokens"]
        log(f"  Turn 5 (refactor): chars={len(content)} has_code={has_code} r_tk={log_t5['usage']['reasoning_tokens']}")
        write_jsonl(log_t5)
        messages.append({"role": "assistant", "content": content})
        cumulative_tokens += log_t5["usage"]["total_tokens"]
        time.sleep(0.5)
    else:
        log(f"  [skip] {base_id}_turn5")

    # Turn 6: Summary
    if not already_logged(f"{base_id}_turn6"):
        t6_prompt = final_prompt
        messages.append({"role": "user", "content": t6_prompt})
        log_t6 = call_multi_turn(messages, test_id=f"{base_id}_turn6", turn=6,
                                 observations={"turn": 6, "task": task_id, "action": "summary"})
        content = log_t6["response"]["content"]
        log_t6["observations"]["summary_provided"] = len(content) > 50
        log_t6["observations"]["cumulative_tokens"] = cumulative_tokens + log_t6["usage"]["total_tokens"]
        log_t6["observations"]["cumulative_latency_ms"] = cumulative_latency
        log(f"  Turn 6 (summary): chars={len(content)} total_tokens={log_t6['observations']['cumulative_tokens']}")
        write_jsonl(log_t6)
        time.sleep(0.5)
    else:
        log(f"  [skip] {base_id}_turn6")

def main():
    log("START v6 GAP 3: MULTI-TURN CODING LOOP")
    t0 = time.time()
    budget = 1500
    for task_id, spec, test_failure, refactor, summary in TASKS:
        if time.time() - t0 > budget:
            log(f"[budget] hit, stopping at {task_id}"); break
        run_task(task_id, spec, test_failure, refactor, summary)
    log(f"\nDONE GAP 3. Elapsed: {time.time()-t0:.1f}s")
    if os.path.exists(LOG_FILE):
        n = sum(1 for _ in open(LOG_FILE))
        log(f"Total log entries: {n}")

if __name__ == "__main__":
    main()
