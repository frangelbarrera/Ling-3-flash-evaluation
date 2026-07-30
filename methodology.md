# Methodology

## API Configuration

All tests were conducted via the OpenRouter API using the following configuration:

```
Endpoint: https://openrouter.ai/api/v1/chat/completions
Model: inclusionai/ling-3.0-flash:free
Provider observed: Novita
API Keys: OpenRouter free-tier keys
```

## Test Parameters

| Parameter | Default | Exceptions |
|-----------|---------|------------|
| `max_tokens` | varies by phase (128-32768) | Phase 1 sweep: 128-32768; v6 phases: 8192; standard: 4096 |
| `temperature` | 0 (deterministic) | v6 JSONL tests use temp=0 with seed=42; earlier chat1/chat3 tests use temp=0.3 with seed=42 |
| `reasoning.enabled` | true (default) | Bug verification: tested with false |
| `reasoning.effort` | not set (default) | Tested: low, minimal, medium |

## Evaluation Sessions

This evaluation was conducted across 3 independent sessions:

### Session 1 (Chat 1) — Initial Evaluation
- **Session:** Initial evaluation
- **API Keys:** OpenRouter free-tier
- **Tests:** 25 phases, 50+ API calls
- **Scope:** Security code review, prompt injection, phishing, OSINT, multilingual, math, logic, coding, financial, hallucination
- **Comparison models:** Gemma-4-31b, GPT-OSS-20b
- **Output:** 60 JSON files + comprehensive report

### Session 2 (Chat 2) — Verification Road
- **Session:** Verification round
- **API Keys:** OpenRouter free-tier
- **Tests:** 25 phases planned, 8 completed (rate-limited)
- **Scope:** Re-verification of Session 1 findings + Phase 25 bug verification
- **Key finding:** Confirmed reasoning bug is model-side via PONG test (97 reasoning tokens for 4-char answer)

### Session 3 (Chat 3) — Comprehensive Evaluation
- **Session:** Comprehensive evaluation
- **API Keys:** OpenRouter free-tier
- **Tests:** 145+ API calls, 115 unique test IDs
- **Scope:** All previous tests + cybersecurity operations, PowerShell, network, shell, stress tests (40+ PONG tests), reasoning toggle tests, cross-model comparisons (6 models)
- **Comparison models:** Gemma, GPT-OSS, Nemotron, DeepSeek v4, MiniMax M2.7, Step 3.7
- **Output:** 140+ JSON files + final consolidated report
- **Key findings:** Bug threshold exact (mt=200), `reasoning.enabled=false` eliminates bug, `reasoning.effort` is inert, Step 3.7 has worse bug

## Data Format

### Session 1 JSON Schema
```json
{
  "phase": "phase08_security_codereview",
  "model": "inclusionai/ling-3.0-flash:free",
  "prompt": "...",
  "max_tokens": 8192,
  "temperature": 0,
  "ok": true,
  "content": "...visible response...",
  "reasoning": "...internal reasoning...",
  "content_len": 5874,
  "reasoning_len": 3808,
  "completion_tokens": 2559,
  "prompt_tokens": 150,
  "total_tokens": 2709,
  "finish_reason": "stop",
  "latency_s": 7.47
}
```

### Session 3 JSON Schema
```json
{
  "phase": "cy01_recon_plan",
  "model_label": "ling",
  "model_id": "inclusionai/ling-3.0-flash:free",
  "prompt": "...",
  "timestamp": "2026-07-27T20:18:57",
  "result": {
    "ok": true,
    "content": "...response..."
  },
  "extra": {
    "phase_meta": {
      "title": "Recon plan for blackbox pentest",
      "category": "Cybersec/Pentest",
      "max_tokens": 8192,
      "temperature": 0
    }
  }
}
```

## Limitations

1. **Rate limiting:** OpenRouter free-tier rate limits applied. Some tests could not be completed due to rate limits (see Phase 8 confound disclosure in README).
2. **Sample size:** 5-288 entries per phase (see README Test Coverage table). Small samples yield wide confidence intervals (see Wilson CIs in README Top 5 Strengths table). Results are directional findings and behaviour characterizations, not definitive benchmarks.
3. **API proxy:** OpenRouter acts as a proxy (provider: Novita). Latency measurements include proxy overhead.
4. **Model version:** The `:free` suffix on OpenRouter may point to a different quantization than the paid version.
5. **No local inference:** All tests were API-based. No local model weights were tested.
6. **Reasoning visibility:** The `reasoning` field is visible in OpenRouter API responses. This may not be available via direct API access from Ant Group.


### Schema Variations

The JSONL logs use slightly different schemas across phases:

**Standard schema (v3 phases 1, 2, 6, 7, 8, 11, 12, 13, 16):**
- Full `system_prompt`, `user_prompt`, `tools` fields
- `observations` as string (e.g., "code review, expected=['X'] | detected=['Y']")

**v6 tool calling schema (v6_phase_tool_calling.jsonl):**
- Same as standard, plus `tools_sent` and `tool_choice` fields
- `observations` as JSON object with structured fields

**v6 long context schema (v6_phase_long_context.jsonl):**
- `messages` field may be `"TRUNCATED_FOR_SPACE"` string for large prompts
- `messages_summary` field provides a count
- `observations` as JSON object with `test_type`, `length_target`, `position_pct`, `needle_found`, `actual_answer`

**v6 multi-turn schema (v6_phase_multiturn.jsonl):**
- Full `messages` array preserved (multi-turn conversation history)
- `observations` as JSON object

All schemas share the core fields: `id`, `timestamp`, `phase`, `test_id`, `model`, `parameters`, `response`, `usage`, `latency_ms`, `status_code`, `error`.
