# Ling-3.0-flash v6 Round — Raw Data Package

**Date:** 2026-07-29
**Evaluator:** Frangel Barrera (the author)
**Target repo:** https://github.com/frangelbarrera/Ling-3-flash-evaluation
**Subdir:** `raw_data/`

## v6 Round Summary

This round closes the **3 critical gaps** needed to complete the evaluation:
- **GAP 1: Tool Calling** (52 entries) — Stated #1 use case in the developer brief
- **GAP 2: Long Context Needle-in-Haystack** (66 entries) — Verifies 256K context claim
- **GAP 3: Multi-turn Coding Loop** (35 entries) — Spec-driven loop pattern from the brief

**Total v6: 153 entries** (vs 110 planned — extras are retries in GAP 2 with corrected lengths).

**Cumulative total in repo:** 692 (v1-v5) + 153 (v6) = **845 entries**

## Contents

### `/logs/`
- `v6_phase_tool_calling.jsonl` (52 entries, 92 KB) — 6 tool calling sub-tests
- `v6_phase_long_context.jsonl` (66 entries, 61 KB) — needle in there haystack + multi-needle conflict
  - **Note:** `messages` are truncated to save space (see `messages_summary` field)
- `v6_phase_multiturn.jsonl` (35 entries, 401 KB) — 5 tasks × 6 turns multi-turn coding

### Main report
- `v6_report.md` (15 KB, 213 lines) — Consolidated report for the 3 gaps

## Top v6 Findings

1. **TOOL CALLING: 45/45 on valid tests** — excellent for function calling with nested schemas
2. **INVENTED PARAMETER DETECTION: 0/10 invented** — Ling does NOT invent params when using tool calling (contrast with v2 PowerShell)
3. **CONTEXT WINDOW REAL = 262,144 tokens** (256K in IEC binary units, standard industry convention; the API enforces an explicit 262,144 token hard limit)
4. **LONG CONTEXT: Ling finds needles up to 208K tokens** at any position
5. **MULTI-NEEDLE CONFLICT: always picks the first needle** (forward recency bias, 22/22)
6. **MULTI-TURN CODING: 26% of turns fail due to reasoning-budget behavior** (chars=0, high r_tk)

## JSONL Schema

```json
{
  "id": "uuid-v4",
  "timestamp": "ISO 8601",
  "phase": "v6_tool_calling" | "v6_long_context" | "v6_multiturn",
  "test_id": "string",
  "run": 1,
  "provider": "openrouter",
  "model": "inclusionai/ling-3.0-flash:free",
  "messages": [...] | "TRUNCATED_FOR_SPACE",
  "messages_summary": "N messages, M chars total",
  "tools_sent": [...],
  "tool_choice": "auto" | "required" | "none",
  "parameters": {"max_tokens": N, "temperature": 0, "seed": 42, "reasoning": {...}},
  "response": {"content": "...", "tool_calls": [...], "finish_reason": "..."},
  "usage": {"prompt_tokens": N, "completion_tokens": N, "reasoning_tokens": N, "total_tokens": N},
  "latency_ms": N,
  "status_code": 200 | 400 | 429,
  "error": null | "string",
  "observations": {...}
}
```

## Reproducibility

Scripts in `scripts/`:
- `v6_gap1_toolcalling.py` — GAP 1
- `v6_gap2_longcontext.py` — GAP 2 (original)
- `v6_gap2_longcontext_fix.py` — GAP 2 (with corrected lengths)
- `v6_gap3_multiturn.py` — GAP 3
- `generate_v6_report.py` — Generates `v6_report.md`

To reproduce:
```bash
export OPENROUTER_API_KEYS="sk-or-v1-key-1,sk-or-v1-key-2,..."  # see REPRODUCING.md
python3 scripts/v6_gap1_toolcalling.py
python3 scripts/v6_gap2_longcontext_fix.py
python3 scripts/v6_gap3_multiturn.py
python3 scripts/generate_v6_report.py
```

All scripts are **idempotent** — re-running skips already-completed tests.

## v6 Final Scorecard

| Dimension | Score v6 | Justification |
|---|---|---|
| Reasoning | 8 | MMLU/GPQA/AIME confirmed |
| Coding | 8 | Multi-turn coding 26% bug rate |
| Tool calling | **9** | 45/45 success, 0/10 invented |
| Long context | **9** | Works to 208K, real cap 262,144 |
| Multi-turn | **6** | 26% bug rate in coding loops |
| Security | 8.5 | Phase 6 complete |
| Multi-language | 8 | Phase 1 multilingual data |
| Reliability | 5 | Reasoning bug persists |
| Hallucination | 8 | Phase 11 confirmed |
| Variance | 10 | 100% deterministic |
| Edge cases | 9.5 | 19/20 success |
| Cost-efficiency | 9 | Free |
| Documentation | 3 | No arXiv, no weights |
| **Overall** | **7.0** | Tool calling and long context raised the score |
