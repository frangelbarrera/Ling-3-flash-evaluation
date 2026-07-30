# Ling-3.0-flash Deep Evaluation v3 — Raw Data Package

**Evaluator:** Frangel Barrera (the author)
**Target repo:** https://github.com/frangelbarrera/Ling-3-flash-evaluation
**Model under test:** inclusionai/ling-3.0-flash:free (Ant Group / inclusionAI)
**Evaluation date:** 2026-07-28/29 (UTC)
**API:** OpenRouter (free tier)

## Package Contents

### `/logs/` — Raw JSONL (692 entries total, all valid)
- `phase1_logs.jsonl` (288) — Reasoning bug: boundary sweep + Thinking vs Non-thinking + 5 languages
- `phase2_logs.jsonl` (75) — Benchmarks: MMLU (25q), GPQA (10q), AIME (5p), HumanEval+MBPP (20p), BBH (10p)
- `phase6_logs.jsonl` (50) — Security: 20 DAN jailbreaks, 10 indirect injection, 10 sysprompt extraction, 5 sensitive exfil, 5 adversarial encoding
- `phase7_logs.jsonl` (70) — Code Review: 20 security bugs, 10 SAFE snippets, 10 crypto, 10 logic bugs
- `phase8_logs.jsonl` (57) — Head-to-Head vs DeepSeek V4 Flash (29 prompts × 2 models)
- `phase11_logs.jsonl` (50) — Hallucination: 25 real Q + 25 trap Q (fabricated premises)
- `phase12_logs.jsonl` (32) — Format Following: 5 JSON, 5 XML, 5 YAML, 5 CSV, 5 Markdown, 5 length constraints
- `phase13_logs.jsonl` (50) — Output Variance: 5 prompts × 10 runs (seed=42, temp=0, non-thinking)
- `phase16_logs.jsonl` (20) — Edge Cases: 20 adversarial prompts (empty, Unicode, paradoxes, harmful)

### `/prompts/` — All prompts in Markdown
- `phase1_prompts.md` — Test Set A + boundary levels + 5 languages
- `phase2_prompts.md` — MMLU + GPQA + AIME + HumanEval + MBPP + BBH prompts
- `phase6_prompts.md` — 50 security prompts (jailbreak + injection + extraction + exfil + encoding)
- `phase7_prompts.md` — 50 code snippets (security + safe + crypto + logic)
- `phase8_prompts.md` — 20 head-to-head prompts
- `phase11_prompts.md` — 50 hallucination prompts (25 real + 25 trap)
- `phase12_prompts.md` — 30 format following prompts
- `phase13_prompts.md` — 5 variance prompts
- `phase16_prompts.md` — 20 edge case prompts

### Main report
- `Ling_3.0_flash_Deep_Evaluation_v3.md` — Consolidated final report (48 KB, 672 lines)

## JSONL Schema

Each line in the JSONL follows this format:

```json
{
  "id": "uuid-v4",
  "timestamp": "ISO 8601",
  "phase": "phaseN_xxx",
  "test_id": "string",
  "run": 1,
  "provider": "openrouter",
  "endpoint": "https://openrouter.ai/api/v1/chat/completions",
  "model": "inclusionai/ling-3.0-flash:free",
  "system_prompt": null,
  "user_prompt": "...",
  "tools": [],
  "parameters": {"max_tokens": N, "temperature": 0, "seed": 42, "reasoning": {"enabled": true/false, "effort": "medium"}},
  "response": {"content": "...", "reasoning": "", "tool_calls": [], "finish_reason": "stop|length"},
  "usage": {"prompt_tokens": N, "completion_tokens": N, "reasoning_tokens": N, "total_tokens": N},
  "latency_ms": N,
  "ttft_ms": 0,
  "status_code": 200,
  "error": null,
  "observations": "string"
}
```

## Reproducibility

Scripts in `scripts/`:
- `v3_infra.py` — API client with key rotation, JSONL format
- `v6_gap1_toolcalling.py` — Tool calling tests (GAP 1)
- `v6_gap2_longcontext.py` / `v6_gap2_longcontext_fix.py` — Long context tests (GAP 2)
- `v6_gap3_multiturn.py` — Multi-turn coding tests (GAP 3)
- `generate_v6_report.py` — Generates the Markdown report from JSONL

To reproduce:
```bash
export OPENROUTER_API_KEYS="sk-or-v1-key-1,sk-or-v1-key-2,..."  # see REPRODUCING.md
# Phase scripts are invoked from v3_infra.py — see REPRODUCING.md for details
python3 scripts/v6_gap1_toolcalling.py    # Tool calling
python3 scripts/v6_gap2_longcontext_fix.py # Long context (corrected)
python3 scripts/v6_gap3_multiturn.py      # Multi-turn coding
python3 scripts/generate_v6_report.py
```

## Top Findings

1. **Reasoning-budget behavior fully characterized**: mt≤128 = 100% failure, mt≥2048 = 0% failure
2. **MMLU+GPQA 100%** (35/35 on small subset)
3. **AIME 100%** (5/5 — aime_1 expected was wrong, Ling correct)
4. **Jailbreak resistance 20/20** — excellent
5. **Hallucination 16% on traps** (4/25) — Ling picks up some fabricated premises (Lincoln 3rd term, HTTP 999)
6. **Code review 16/16 detection** of real bugs, BUT 8/11 false positives on SAFE code
7. **100% deterministic** with seed=42+temp=0+non-thinking (5 prompts × 10 runs identical)
8. **`reasoning.enabled=false`** eliminates the 0-char behavior 100% (definitive workaround)
9. **Chinese triggers ~5× more reasoning tokens** than English
10. **Loop degeneration** in haiku at mt=8000 (4762 r_tk in syllable-counting loop)
