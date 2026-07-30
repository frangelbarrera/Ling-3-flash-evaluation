#!/usr/bin/env python3
"""
GAP 2: LONG CONTEXT NEEDLE-IN-HAYSTACK
Tests:
2.1 Single needle: 4 longitudes × 5 posiciones = 20 requests
2.2 Multi-needle conflicto: 5 longitudes × 2 runs = 10 requests

Needle: "The magic number is 4271."
Question: "What is the magic number mentioned in the text?"
"""
import os
import sys, os, time, json, uuid, hashlib, re, random
import requests
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v3_infra import ALL_KEYS, ROTATOR

PHASE = "v6_long_context"
LOG_FILE = os.environ.get("LING3_LOG_FILE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ling3_v3", "logs", "v6_phase_long_context.jsonl"))
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
LING_MODEL = "inclusionai/ling-3.0-flash:free"

def log(m): print(m, flush=True)

# Generate filler text using a deterministic seed
random.seed(42)
WORDS = """the quick brown fox jumps over the lazy dog hello world foo bar
the quick brown fox jumps over the lazy dog hello world foo bar the quick brown fox jumps over the lazy dog
the quick brown fox jumps over the lazy dog hello world foo bar the quick brown fox jumps over the lazy dog
the quick brown fox jumps over the lazy dog hello world foo bar the quick brown fox jumps over the lazy dog""".split()

def generate_filler(num_words):
    """Generate filler text of approximately num_words words."""
    out = []
    for _ in range(num_words):
        # Make sentences of ~10 words
        sentence = " ".join(random.choice(WORDS) for _ in range(10)) + "."
        out.append(sentence)
    return " ".join(out)

def call_with_context(context, question, max_tokens=500, test_id="", observations=None):
    """Call Ling with a context + question."""
    log_entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": PHASE,
        "test_id": test_id,
        "run": 1,

        "provider": "openrouter",
        "model": LING_MODEL,
        "messages": [
            {"role": "system", "content": "You will be given a long text. Answer questions about it precisely."},
            {"role": "user", "content": f"{context}\n\nQuestion: {question}\n\nAnswer with only the answer, no explanation."}
        ],
        "tools_sent": [],
        "tool_choice": "none",
        "parameters": {
            "max_tokens": max_tokens, "temperature": 0, "seed": 42,
            "reasoning": {"enabled": False}
        },
        "response": {"content": "", "tool_calls": [], "finish_reason": None},
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0, "total_tokens": 0},
        "latency_ms": 0, "status_code": 0, "error": None,
        "observations": observations or {}
    }
    last_err = None
    for attempt in range(3):
        key_idx, key = ROTATOR.next_key()

        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                   "HTTP-Referer": "https://github.com/frangelbarrera/Ling-3-flash-evaluation",
                   "X-Title": "Ling-3 Independent Eval v6"}
        payload = {
            "model": LING_MODEL,
            "messages": log_entry["messages"],
            "max_tokens": max_tokens, "temperature": 0, "seed": 42,
            "reasoning": {"enabled": False}
        }
        try:
            t0 = time.time()
            r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=120)
            log_entry["latency_ms"] = int((time.time() - t0) * 1000)
            log_entry["status_code"] = r.status_code
            if r.status_code == 429:
                ROTATOR.mark_rate_limited(key_idx, 60)
                last_err = f"429 key#{key_idx}"
                log_entry["error"] = last_err
                time.sleep(3); continue
            if r.status_code != 200:
                last_err = f"{r.status_code}: {r.text[:200]}"
                log_entry["error"] = last_err
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
            last_err = "timeout"
            log_entry["error"] = last_err
            time.sleep(5)
        except Exception as e:
            last_err = f"exc: {e}"
            log_entry["error"] = last_err
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

# Test 2.1: Single needle - 4 longitudes × 5 posiciones
LENGTHS = {
    "4K": 3000,    # ~4K tokens
    "16K": 12000,  # ~16K tokens
    "64K": 48000,  # ~64K tokens
    "128K": 96000, # ~128K tokens
}
POSITIONS = [0.10, 0.30, 0.50, 0.70, 0.90]
NEEDLE = "The magic number is 4271."
QUESTION = "What is the magic number mentioned in the text?"
EXPECTED = "4271"

# Test 2.2: Multi-needle conflicto - 5 longitudes × 2 runs
LENGTHS_2_2 = {
    "4K": 3000,
    "16K": 12000,
    "64K": 48000,
    "128K": 96000,
    "180K": 135000  # extra large
}
NEEDLE_4271 = "The magic number is 4271."
NEEDLE_9999 = "The magic number is 9999."

def insert_needle(filler, needle, position_pct):
    """Insert needle at position percentage in filler text."""
    if not filler:
        return needle
    pos = int(len(filler) * position_pct)
    # Find a sentence boundary near pos
    boundary = filler.find(". ", pos)
    if boundary == -1:
        boundary = pos
    else:
        boundary += 2
    return filler[:boundary] + " " + needle + " " + filler[boundary:]

def run_test_2_1():
    log("\n=== TEST 2.1 — Single needle (4 longitudes × 5 posiciones = 20 req) ===")
    done = 0; skipped = 0
    for length_name, num_words in LENGTHS.items():
        filler = generate_filler(num_words)
        for pos in POSITIONS:
            test_id = f"2.1_{length_name}_pos{int(pos*100)}"
            if already_logged(test_id):
                skipped += 1; log(f"  [skip] {test_id}"); continue
            context = insert_needle(filler, NEEDLE, pos)
            log_entry = call_with_context(context, QUESTION, max_tokens=200,
                                          test_id=test_id,
                                          observations={"test_type": "single_needle",
                                                         "length": length_name,
                                                         "position_pct": pos,
                                                         "expected": EXPECTED})
            content = log_entry["response"]["content"].strip()
            found = EXPECTED in content
            log_entry["observations"]["needle_found"] = found
            log_entry["observations"]["actual_answer"] = content[:100]
            log(f"  {test_id}: found={found} content={content[:60]!r} prompt_tk={log_entry['usage']['prompt_tokens']}")
            write_jsonl(log_entry)
            done += 1
            time.sleep(0.5)
    log(f"Test 2.1 done: {done} new, {skipped} skipped")

def run_test_2_2():
    log("\n=== TEST 2.2 — Multi-needle conflicto (5 longitudes × 2 runs = 10 req) ===")
    done = 0; skipped = 0
    for length_name, num_words in LENGTHS_2_2.items():
        filler = generate_filler(num_words)
        # Insert 4271 at 30% and 9999 at 70%
        context_t30 = insert_needle(filler, NEEDLE_4271, 0.30)
        context_t70 = insert_needle(context_t30, NEEDLE_9999, 0.70)
        for run in range(1, 3):
            test_id = f"2.2_{length_name}_run{run}"
            if already_logged(test_id):
                skipped += 1; log(f"  [skip] {test_id}"); continue
            log_entry = call_with_context(context_t70, QUESTION, max_tokens=200,
                                          test_id=test_id,
                                          observations={"test_type": "multi_needle_conflict",
                                                         "length": length_name,
                                                         "needle_30pct": "4271",
                                                         "needle_70pct": "9999",
                                                         "expected": "either_or_conflict_detected"})
            content = log_entry["response"]["content"].strip()
            log_entry["observations"]["actual_answer"] = content[:100]
            log_entry["observations"]["chose_4271"] = "4271" in content and "9999" not in content
            log_entry["observations"]["chose_9999"] = "9999" in content and "4271" not in content
            log_entry["observations"]["mentions_both"] = "4271" in content and "9999" in content
            log(f"  {test_id}: content={content[:80]!r} chose_4271={log_entry['observations']['chose_4271']} chose_9999={log_entry['observations']['chose_9999']} both={log_entry['observations']['mentions_both']}")
            write_jsonl(log_entry)
            done += 1
            time.sleep(0.5)
    log(f"Test 2.2 done: {done} new, {skipped} skipped")

def main():
    log("START v6 GAP 2: LONG CONTEXT")
    t0 = time.time()
    budget = 1500
    run_test_2_1()
    if time.time() - t0 < budget: run_test_2_2()
    log(f"\nDONE GAP 2. Elapsed: {time.time()-t0:.1f}s")
    if os.path.exists(LOG_FILE):
        n = sum(1 for _ in open(LOG_FILE))
        log(f"Total log entries: {n}")

if __name__ == "__main__":
    main()
