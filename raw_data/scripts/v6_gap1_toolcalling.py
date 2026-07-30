#!/usr/bin/env python3
"""
GAP 1: TOOL CALLING - Ling-3.0-flash Ronda Final v6
Tests:
1.1 Single tool simple (10 prompts)
1.2 Multi-tool selection (10 prompts)
1.3 Schemas anidadas (10 prompts)
1.4 tool_choice="required" (5 prompts)
1.5 Error recovery multi-turn (5 escenarios, 3 turnos cada uno = 15 requests)
1.6 Invented parameter detection (10 prompts)

Total: 60 requests (slightly more than 50 planned due to multi-turn)
"""
import os
import sys, os, time, json, uuid, hashlib, re
import requests
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v3_infra import ALL_KEYS, ROTATOR

PHASE = "v6_tool_calling"
LOG_FILE = os.environ.get("LING3_LOG_FILE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ling3_v3", "logs", "v6_phase_tool_calling.jsonl"))
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
LING_MODEL = "inclusionai/ling-3.0-flash:free"

def log(m): print(m, flush=True)

def call_with_tools(messages, tools=None, tool_choice=None, max_tokens=8192,
                    temperature=0, seed=42, reasoning_enabled=True, test_id="", observations=None):
    """Call Ling with tools. Returns log_entry dict."""
    log_entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": PHASE,
        "test_id": test_id,
        "run": 1,

        "provider": "openrouter",
        "model": LING_MODEL,
        "messages": messages,
        "tools_sent": tools or [],
        "tool_choice": tool_choice or "auto",
        "parameters": {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "seed": seed,
            "reasoning": {"enabled": reasoning_enabled, "effort": "medium"} if reasoning_enabled else {"enabled": False}
        },
        "response": {"content": "", "tool_calls": [], "finish_reason": None},
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0, "total_tokens": 0},
        "latency_ms": 0,
        "status_code": 0,
        "error": None,
        "observations": observations or {}
    }
    last_err = None
    for attempt in range(4):
        key_idx, key = ROTATOR.next_key()

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/frangelbarrera/Ling-3-flash-evaluation",
            "X-Title": "Ling-3 Independent Eval v6 - Final Round",
        }
        payload = {
            "model": LING_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "seed": seed,
        }
        if reasoning_enabled:
            payload["reasoning"] = {"enabled": True, "effort": "medium"}
        else:
            payload["reasoning"] = {"enabled": False}
        if tools:
            payload["tools"] = tools
        if tool_choice:
            payload["tool_choice"] = tool_choice
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
            log_entry["response"]["tool_calls"] = msg.get("tool_calls") or []
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

# ---------- Tool definitions ----------
EXCHANGE_RATE_TOOL = {
    "type": "function",
    "function": {
        "name": "lookup_exchange_rate",
        "description": "Get the exchange rate between two currencies on a specific date",
        "parameters": {
            "type": "object",
            "properties": {
                "base": {"type": "string", "description": "Base currency code (e.g., USD, EUR)"},
                "quote": {"type": "string", "description": "Quote currency code"},
                "date": {"type": "string", "format": "date"}
            },
            "required": ["base", "quote", "date"]
        }
    }
}

WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather forecast for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "date": {"type": "string"},
                "units": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["location", "date"]
        }
    }
}

NEWS_TOOL = {
    "type": "function",
    "function": {
        "name": "search_news",
        "description": "Search recent news articles",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "date_range": {"type": "string"},
                "max_results": {"type": "integer"}
            },
            "required": ["query"]
        }
    }
}

CREATE_PROFILE_TOOL = {
    "type": "function",
    "function": {
        "name": "create_user_profile",
        "description": "Create a user profile",
        "parameters": {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "age": {"type": "integer", "minimum": 0, "maximum": 150}
                    },
                    "required": ["name", "email"]
                },
                "preferences": {
                    "type": "object",
                    "properties": {
                        "language": {"type": "string", "enum": ["en", "es", "fr", "de", "zh"]},
                        "notifications": {"type": "boolean"},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "required": ["user"]
        }
    }
}

PROCESS_INFO_TOOL = {
    "type": "function",
    "function": {
        "name": "get_process_info",
        "description": "Get information about a running process",
        "parameters": {
            "type": "object",
            "properties": {
                "process_name": {"type": "string"},
                "include_metrics": {"type": "boolean"}
            },
            "required": ["process_name"]
        }
    }
}

# ---------- Test 1.1: Single tool simple (10 prompts) ----------
TEST_1_1 = [
    "What's the EUR to JPY rate today (2026-07-29)?",
    "Convert 100 USD to GBP using the rate from 2026-07-25.",
    "I need the CHF to USD exchange rate for July 20, 2026.",
    "Get me the CAD to MXN rate for yesterday (2026-07-28).",
    "What's 500 AUD worth in NZD at today's rate?",
    "Find the EUR to USD rate for 2026-07-01.",
    "I'm converting 1000 SEK to NOK, what's the rate today?",
    "What's the HKD to CNY rate for 2026-07-15?",
    "Get the SGD to MYR exchange rate for today.",
    "What's the BTC to USD rate on 2026-07-29?",
]

# ---------- Test 1.2: Multi-tool selection (10 prompts) ----------
TEST_1_2 = [
    ("What's the weather in Tokyo today?", "get_weather"),
    ("Get me the latest news about AI from the past week.", "search_news"),
    ("What's the EUR to JPY rate today?", "lookup_exchange_rate"),
    ("Is it raining in London right now?", "get_weather"),
    ("Find news about Tesla stock from July 2026.", "search_news"),
    ("Convert 100 USD to EUR using today's rate.", "lookup_exchange_rate"),
    ("What's the weather forecast for New York tomorrow?", "get_weather"),
    ("Search for recent news about climate change.", "search_news"),
    ("What's the GBP to AUD rate for 2026-07-20?", "lookup_exchange_rate"),
    ("Get me news about OpenAI from the last 3 days.", "search_news"),
]

# ---------- Test 1.3: Schemas anidadas (10 prompts) ----------
TEST_1_3 = [
    "Create a profile for John Doe (john@example.com, age 30) with English language and notifications on.",
    "Make a user profile for María García (maria@test.org) with Spanish language and tags ['vip', 'early-adopter'].",
    "Register a new user: Pierre Dupont (pierre@french.fr, age 25), French, no notifications.",
    "Add user Hans Schmidt (hans@german.de) with German language and tag 'beta-tester'.",
    "Create profile for Wei Zhang (wei@chinese.cn, age 28), Chinese, notifications on, tags ['premium'].",
    "Make a profile for someone named Alex (alex@alex.io), no preferences specified.",
    "Register user Bob Smith (bob@bob.com, age 45) with all defaults.",
    "Create a profile for Alice Johnson (alice@alice.com, age 35) with English, notifications off, empty tags.",
    "Add user Carlos López (carlos@es.es) with Spanish language, notifications on, tags ['new', 'free-trial'].",
    "Register Eve (eve@evil.com, age 99) with all preferences enabled.",
]

# ---------- Test 1.4: tool_choice=required (5 prompts) ----------
TEST_1_4 = [
    "What's the EUR to USD rate today?",
    "Convert 100 GBP to JPY.",
    "I need the CHF to EUR rate for 2026-07-20.",
    "Get me the AUD to NZD rate.",
    "What's 50 USD worth in CAD?",
]

# ---------- Test 1.5: Error recovery (5 escenarios × 3 turnos = 15 requests) ----------
TEST_1_5 = [
    ("What's the EUR to XYZ rate today?", "EUR->XYZ", "What's the EUR to USD rate today?"),
    ("Convert 100 USD to BTC.", "USD->BTC", "Convert 100 USD to EUR."),
    ("What's the EUR to JPY rate for 2026-13-45?", "invalid_date", "What's the EUR to JPY rate for 2026-07-15?"),
    ("What's the AAA to BBB rate?", "both_invalid", "What's the EUR to GBP rate today?"),
    ("What's the USD to USD rate today?", "same_currency", "What's the USD to EUR rate today?"),
]

# ---------- Test 1.6: Invented parameter detection (10 prompts) ----------
TEST_1_6 = [
    "Get process info for 'chrome' including the Owner property.",
    "Get process info for 'node' with its ApplyTo setting.",
    "Get process info for 'python' and its ParentProcessID.",
    "Get process info for 'java' with CommandLine.",
    "Get process info for 'nginx' including Threads count.",
    "Get process info for 'redis' with HandleCount.",
    "Get process info for 'postgres' with StartTime.",
    "Get process info for 'mongodb' with CPU usage.",
    "Get process info for 'docker' with Memory usage.",
    "Get process info for 'kubectl' with Path.",
]

def validate_tool_call(tool_call, expected_tool_name, tools_sent):
    """Validate that a tool call matches the schema."""
    obs = {
        "called_correct_tool": False,
        "arguments_valid_json": False,
        "arguments_match_schema": False,
        "hallucinated_parameters": [],
        "respects_tool_choice": False,
    }
    if not tool_call:
        return obs
    func = tool_call.get("function", {})
    name = func.get("name")
    args_str = func.get("arguments", "{}")
    # Check if called the right tool
    if name == expected_tool_name:
        obs["called_correct_tool"] = True
    # Check arguments is valid JSON
    try:
        args = json.loads(args_str) if isinstance(args_str, str) else args_str
        obs["arguments_valid_json"] = True
    except:
        args = {}
        return obs
    # Get the tool definition
    tool_def = None
    for t in tools_sent:
        if t.get("function", {}).get("name") == name:
            tool_def = t
            break
    if not tool_def:
        return obs
    # Check that all args are in the schema
    schema_props = tool_def["function"]["parameters"].get("properties", {})
    required_props = tool_def["function"]["parameters"].get("required", [])
    # Check each provided arg against schema
    obs["arguments_match_schema"] = True
    for arg_name in args:
        if arg_name not in schema_props:
            obs["hallucinated_parameters"].append(arg_name)
            obs["arguments_match_schema"] = False
    # Check required
    for req in required_props:
        if req not in args:
            obs["arguments_match_schema"] = False
    obs["respects_tool_choice"] = True
    return obs

def run_test_1_1():
    log("\n=== TEST 1.1 — Single tool (lookup_exchange_rate) ===")
    for i, prompt in enumerate(TEST_1_1, 1):
        test_id = f"1.1_exchange_prompt_{i}"
        if already_logged(test_id):
            log(f"  [skip] {test_id}")
            continue
        messages = [{"role": "user", "content": prompt}]
        log_entry = call_with_tools(messages, tools=[EXCHANGE_RATE_TOOL],
                                    test_id=test_id,
                                    observations={"test_type": "single_tool"})
        # Analyze
        tcs = log_entry["response"]["tool_calls"]
        if tcs:
            obs = validate_tool_call(tcs[0], "lookup_exchange_rate", [EXCHANGE_RATE_TOOL])
            log_entry["observations"].update(obs)
        else:
            log_entry["observations"]["called_correct_tool"] = False
            log_entry["observations"]["arguments_valid_json"] = False
        log(f"  {test_id}: tool_calls={len(tcs)} called_correct={log_entry['observations'].get('called_correct_tool')}")
        write_jsonl(log_entry)
        time.sleep(0.5)

def run_test_1_2():
    log("\n=== TEST 1.2 — Multi-tool selection ===")
    multi_tools = [EXCHANGE_RATE_TOOL, WEATHER_TOOL, NEWS_TOOL]
    for i, (prompt, expected) in enumerate(TEST_1_2, 1):
        test_id = f"1.2_multitool_prompt_{i}"
        if already_logged(test_id):
            log(f"  [skip] {test_id}")
            continue
        messages = [{"role": "user", "content": prompt}]
        log_entry = call_with_tools(messages, tools=multi_tools,
                                    test_id=test_id,
                                    observations={"test_type": "multi_tool", "expected_tool": expected})
        tcs = log_entry["response"]["tool_calls"]
        if tcs:
            obs = validate_tool_call(tcs[0], expected, multi_tools)
            log_entry["observations"].update(obs)
        else:
            log_entry["observations"]["called_correct_tool"] = False
        log(f"  {test_id}: tool_calls={len(tcs)} called_correct={log_entry['observations'].get('called_correct_tool')}")
        write_jsonl(log_entry)
        time.sleep(0.5)

def run_test_1_3():
    log("\n=== TEST 1.3 — Nested schemas ===")
    for i, prompt in enumerate(TEST_1_3, 1):
        test_id = f"1.3_nested_prompt_{i}"
        if already_logged(test_id):
            log(f"  [skip] {test_id}")
            continue
        messages = [{"role": "user", "content": prompt}]
        log_entry = call_with_tools(messages, tools=[CREATE_PROFILE_TOOL],
                                    test_id=test_id,
                                    observations={"test_type": "nested_schema"})
        tcs = log_entry["response"]["tool_calls"]
        if tcs:
            obs = validate_tool_call(tcs[0], "create_user_profile", [CREATE_PROFILE_TOOL])
            log_entry["observations"].update(obs)
        else:
            log_entry["observations"]["called_correct_tool"] = False
        log(f"  {test_id}: tool_calls={len(tcs)} called_correct={log_entry['observations'].get('called_correct_tool')}")
        write_jsonl(log_entry)
        time.sleep(0.5)

def run_test_1_4():
    log("\n=== TEST 1.4 — tool_choice=required ===")
    for i, prompt in enumerate(TEST_1_4, 1):
        test_id = f"1.4_required_prompt_{i}"
        if already_logged(test_id):
            log(f"  [skip] {test_id}")
            continue
        messages = [{"role": "user", "content": prompt}]
        log_entry = call_with_tools(messages, tools=[EXCHANGE_RATE_TOOL],
                                    tool_choice="required",
                                    test_id=test_id,
                                    observations={"test_type": "tool_choice_required"})
        tcs = log_entry["response"]["tool_calls"]
        if tcs:
            obs = validate_tool_call(tcs[0], "lookup_exchange_rate", [EXCHANGE_RATE_TOOL])
            obs["respects_tool_choice"] = True
            log_entry["observations"].update(obs)
        else:
            log_entry["observations"]["respects_tool_choice"] = False
        log(f"  {test_id}: tool_calls={len(tcs)} respects_required={log_entry['observations'].get('respects_tool_choice')}")
        write_jsonl(log_entry)
        time.sleep(0.5)

def run_test_1_5():
    log("\n=== TEST 1.5 — Error recovery (multi-turn) ===")
    for i, (turn1_prompt, error_type, turn3_retry) in enumerate(TEST_1_5, 1):
        test_id = f"1.5_error_recovery_{i}"
        if already_logged(f"{test_id}_turn1"):
            log(f"  [skip] {test_id}")
            continue
        # Turn 1: initial prompt
        messages_t1 = [{"role": "user", "content": turn1_prompt}]
        log_t1 = call_with_tools(messages_t1, tools=[EXCHANGE_RATE_TOOL],
                                  test_id=f"{test_id}_turn1",
                                  observations={"test_type": "error_recovery", "turn": 1, "error_type": error_type})
        tcs_t1 = log_t1["response"]["tool_calls"]
        if tcs_t1:
            obs = validate_tool_call(tcs_t1[0], "lookup_exchange_rate", [EXCHANGE_RATE_TOOL])
            log_t1["observations"].update(obs)
        log(f"  {test_id}_turn1: tool_calls={len(tcs_t1)}")
        write_jsonl(log_t1)
        time.sleep(0.5)
        # Turn 2: simulate tool error
        if tcs_t1:
            tool_call_id = tcs_t1[0].get("id", "call_1")
            tool_call_args = tcs_t1[0].get("function", {}).get("arguments", "{}")
            messages_t2 = messages_t1 + [
                {"role": "assistant", "content": None, "tool_calls": tcs_t1},
                {"role": "tool", "tool_call_id": tool_call_id, "content": json.dumps({"error": f"Currency code or date invalid: {error_type}"})}
            ]
            log_t2 = call_with_tools(messages_t2, tools=[EXCHANGE_RATE_TOOL],
                                     test_id=f"{test_id}_turn2",
                                     observations={"test_type": "error_recovery", "turn": 2, "error_type": error_type})
            log(f"  {test_id}_turn2: chars={len(log_t2['response']['content'])} tool_calls={len(log_t2['response']['tool_calls'])}")
            log_t2["observations"]["error_received"] = True
            write_jsonl(log_t2)
            time.sleep(0.5)
            # Turn 3: ask for retry
            messages_t3 = messages_t2 + [
                {"role": "user", "content": f"The previous call failed. Please retry with: {turn3_retry}"}
            ]
            log_t3 = call_with_tools(messages_t3, tools=[EXCHANGE_RATE_TOOL],
                                     test_id=f"{test_id}_turn3",
                                     observations={"test_type": "error_recovery", "turn": 3, "error_type": error_type})
            tcs_t3 = log_t3["response"]["tool_calls"]
            if tcs_t3:
                obs = validate_tool_call(tcs_t3[0], "lookup_exchange_rate", [EXCHANGE_RATE_TOOL])
                log_t3["observations"].update(obs)
                log_t3["observations"]["error_recovery_success"] = obs["called_correct_tool"]
            log(f"  {test_id}_turn3: tool_calls={len(tcs_t3)} recovered={log_t3['observations'].get('error_recovery_success')}")
            write_jsonl(log_t3)
            time.sleep(0.5)

def run_test_1_6():
    log("\n=== TEST 1.6 — Invented parameter detection ===")
    invented_params = ["Owner", "ApplyTo", "ParentProcessID", "CommandLine", "Threads",
                       "HandleCount", "StartTime", "CPU", "Memory", "Path"]
    for i, prompt in enumerate(TEST_1_6, 1):
        test_id = f"1.6_invented_param_{i}"
        if already_logged(test_id):
            log(f"  [skip] {test_id}")
            continue
        messages = [{"role": "user", "content": prompt}]
        log_entry = call_with_tools(messages, tools=[PROCESS_INFO_TOOL],
                                    test_id=test_id,
                                    observations={"test_type": "invented_param",
                                                   "prompted_param": invented_params[i-1] if i <= len(invented_params) else "?"})
        tcs = log_entry["response"]["tool_calls"]
        if tcs:
            obs = validate_tool_call(tcs[0], "get_process_info", [PROCESS_INFO_TOOL])
            log_entry["observations"].update(obs)
        else:
            log_entry["observations"]["hallucinated_parameters"] = []
        log(f"  {test_id}: tool_calls={len(tcs)} hallucinated={log_entry['observations'].get('hallucinated_parameters', [])}")
        write_jsonl(log_entry)
        time.sleep(0.5)

def main():
    log("START v6 GAP 1: TOOL CALLING")
    log(f"Time: {datetime.now(timezone.utc).isoformat()}")
    t0 = time.time()
    budget = 1500  # 25 min budget
    # Run all subtests
    run_test_1_1()
    if time.time() - t0 < budget: run_test_1_2()
    if time.time() - t0 < budget: run_test_1_3()
    if time.time() - t0 < budget: run_test_1_4()
    if time.time() - t0 < budget: run_test_1_5()
    if time.time() - t0 < budget: run_test_1_6()
    log(f"\nDONE GAP 1. Elapsed: {time.time()-t0:.1f}s")
    # Count logs
    if os.path.exists(LOG_FILE):
        n = sum(1 for _ in open(LOG_FILE))
        log(f"Total log entries: {n}")

if __name__ == "__main__":
    main()
