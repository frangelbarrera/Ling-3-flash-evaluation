#!/usr/bin/env python3
"""Fix GAP 2: Run long context tests with CORRECT lengths (in actual tokens)."""
import os
import sys, os, time, json, uuid, hashlib, random
import requests
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v3_infra import ALL_KEYS, ROTATOR

PHASE = "v6_long_context"
LOG_FILE = os.environ.get("LING3_LOG_FILE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ling3_v3", "logs", "v6_phase_long_context.jsonl"))
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
LING_MODEL = "inclusionai/ling-3.0-flash:free"

def log(m): print(m, flush=True)

random.seed(42)
WORDS = """the quick brown fox jumps over the lazy dog hello world foo bar
the quick brown fox jumps over the lazy dog hello world foo bar the quick brown fox jumps over the lazy dog""".split()

def generate_filler(num_sentences):
    """Generate filler with N sentences."""
    out = []
    for _ in range(num_sentences):
        sentence = " ".join(random.choice(WORDS) for _ in range(15)) + "."
        out.append(sentence)
    return " ".join(out)

# CORRECT lengths: we know 3000 sentences = ~33K tokens, so:
# 4K target -> 400 sentences (~4K tokens)
# 16K -> 1500 sentences (~16K tokens)
# 32K -> 3000 sentences (~33K tokens)
# 64K -> 6000 sentences (~66K tokens)
# 128K -> 12000 sentences (~132K tokens)
# 256K -> 24000 sentences (~264K tokens) — will fail (max 262K)
LENGTHS = {
    "4K_actual": 400,
    "16K_actual": 1500,
    "32K_actual": 3000,
    "64K_actual": 6000,
    "128K_actual": 12000,
    "256K_actual": 20000,  # aim ~220K tokens (under the 262K limit)
}
POSITIONS = [0.10, 0.30, 0.50, 0.70, 0.90]
NEEDLE = "The magic number is 4271."
QUESTION = "What is the magic number mentioned in the text?"
EXPECTED = "4271"

NEEDLE_9999 = "The magic number is 9999."

def call_with_context(context, question, max_tokens=200, test_id="", observations=None):
    log_entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": PHASE, "test_id": test_id, "run": 1,
        "provider": "openrouter", "model": LING_MODEL,
        "messages": [
            {"role": "system", "content": "You will be given a long text. Answer questions about it precisely."},
            {"role": "user", "content": f"{context}\n\nQuestion: {question}\n\nAnswer with only the answer, no explanation."}
        ],
        "tools_sent": [], "tool_choice": "none",
        "parameters": {"max_tokens": max_tokens, "temperature": 0, "seed": 42, "reasoning": {"enabled": False}},
        "response": {"content": "", "tool_calls": [], "finish_reason": None},
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0, "total_tokens": 0},
        "latency_ms": 0, "status_code": 0, "error": None,
        "observations": observations or {}
    }
    last_err = None
    for attempt in range(2):
        key_idx, key = ROTATOR.next_key()

        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                   "HTTP-Referer": "https://github.com/frangelbarrera/Ling-3-flash-evaluation",
                   "X-Title": "Ling-3 Independent Eval v6"}
        payload = {"model": LING_MODEL, "messages": log_entry["messages"],
                   "max_tokens": max_tokens, "temperature": 0, "seed": 42,
                   "reasoning": {"enabled": False}}
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
                last_err = f"{r.status_code}: {r.text[:300]}"; log_entry["error"] = last_err
                # Don't retry 400s — they're real errors
                if r.status_code == 400: break
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
            time.sleep(3)
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

def insert_needle(filler, needle, position_pct):
    pos = int(len(filler) * position_pct)
    boundary = filler.find(". ", pos)
    if boundary == -1: boundary = pos
    else: boundary += 2
    return filler[:boundary] + " " + needle + " " + filler[boundary:]

def run_test_2_1():
    log("\n=== TEST 2.1 FIXED — Single needle (6 longitudes × 5 posiciones = 30 req) ===")
    done = 0; skipped = 0
    for length_name, num_sentences in LENGTHS.items():
        filler = generate_filler(num_sentences)
        for pos in POSITIONS:
            test_id = f"2.1_{length_name}_pos{int(pos*100)}"
            if already_logged(test_id):
                skipped += 1; log(f"  [skip] {test_id}"); continue
            context = insert_needle(filler, NEEDLE, pos)
            log_entry = call_with_context(context, QUESTION, max_tokens=200,
                                          test_id=test_id,
                                          observations={"test_type": "single_needle",
                                                         "length_target": length_name,
                                                         "position_pct": pos,
                                                         "expected": EXPECTED})
            content = log_entry["response"]["content"].strip()
            found = EXPECTED in content
            log_entry["observations"]["needle_found"] = found
            log_entry["observations"]["actual_answer"] = content[:100]
            log(f"  {test_id}: status={log_entry['status_code']} found={found} prompt_tk={log_entry['usage']['prompt_tokens']} content={content[:50]!r}")
            write_jsonl(log_entry)
            done += 1
            time.sleep(0.5)
    log(f"Test 2.1: {done} new, {skipped} skipped")

def run_test_2_2():
    log("\n=== TEST 2.2 FIXED — Multi-needle conflicto (5 longitudes × 2 runs = 10 req) ===")
    LENGTHS_2_2 = {k: v for k, v in LENGTHS.items() if k != "256K_actual"}
    done = 0; skipped = 0
    for length_name, num_sentences in LENGTHS_2_2.items():
        filler = generate_filler(num_sentences)
        context_30 = insert_needle(filler, NEEDLE, 0.30)
        context_70 = insert_needle(context_30, NEEDLE_9999, 0.70)
        for run in range(1, 3):
            test_id = f"2.2_{length_name}_run{run}"
            if already_logged(test_id):
                skipped += 1; log(f"  [skip] {test_id}"); continue
            log_entry = call_with_context(context_70, QUESTION, max_tokens=200,
                                          test_id=test_id,
                                          observations={"test_type": "multi_needle_conflict",
                                                         "length_target": length_name,
                                                         "needle_30pct": "4271",
                                                         "needle_70pct": "9999"})
            content = log_entry["response"]["content"].strip()
            log_entry["observations"]["actual_answer"] = content[:100]
            log_entry["observations"]["chose_4271"] = "4271" in content and "9999" not in content
            log_entry["observations"]["chose_9999"] = "9999" in content and "4271" not in content
            log_entry["observations"]["mentions_both"] = "4271" in content and "9999" in content
            log(f"  {test_id}: status={log_entry['status_code']} content={content[:60]!r}")
            write_jsonl(log_entry)
            done += 1
            time.sleep(0.5)
    log(f"Test 2.2: {done} new, {skipped} skipped")

def main():
    log("START v6 GAP 2 FIXED: LONG CONTEXT (correct lengths)")
    t0 = time.time()
    budget = 1500
    run_test_2_1()
    if time.time() - t0 < budget: run_test_2_2()
    log(f"\nDONE. Elapsed: {time.time()-t0:.1f}s")
    if os.path.exists(LOG_FILE):
        n = sum(1 for _ in open(LOG_FILE))
        log(f"Total log entries: {n}")

if __name__ == "__main__":
    main()
