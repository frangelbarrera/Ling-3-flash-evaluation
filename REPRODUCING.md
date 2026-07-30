# Reproducing the Ling-3.0-flash Evaluation

This guide explains how to reproduce the 845 API calls in this repository, validate the existing JSONL logs, or re-run individual test phases.

## Prerequisites

### 1. Get an OpenRouter API key

Ling-3.0-flash is available for free on OpenRouter (until Aug 3, 2026):

1. Sign up at [openrouter.ai](https://openrouter.ai/)
2. Generate an API key in Settings → Keys
3. The free tier allows 50 requests/day per key

The free tier is rate-limited per key. For re-running individual phases, one key is generally sufficient; for the full 845-call evaluation, plan around the daily per-key quota.

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

```bash
# Single key
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"

# Optional: comma-separated list for rotation across runs
export OPENROUTER_API_KEYS="sk-or-v1-key-1,sk-or-v1-key-2,sk-or-v1-key-3"

# Output directory for logs (optional, defaults to ./logs)
export LING3_LOGS_DIR="./logs"
```

## Validating existing data

### Validate all JSONL files

The raw JSONL logs are stored in `raw_data/ling3_v3/logs/`. To validate them:

```bash
python3 -c "
import json, zipfile
from pathlib import Path

logs_dir = Path('raw_data/ling3_v3/logs')
total = 0
errors = 0

for f in sorted(logs_dir.glob('*.jsonl')):
    entries = 0
    with open(f) as fp:
        for i, line in enumerate(fp, 1):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
                entries += 1
            except json.JSONDecodeError as e:
                print(f'  ❌ {f.name} line {i}: {e}')
                errors += 1
    print(f'  ✅ {f.name}: {entries} valid entries')
    total += entries

print(f'\nTotal: {total} entries, {errors} errors')
"
```

Expected output: 845 total entries, 0 errors.

### Verify the scorecard math

```bash
python3 -c "
# Reproduce the 7.0/10 overall score calculation
scores = {
    'Reasoning': 7.0, 'Coding': 7.0, 'Tool calling': 9.0,
    'Long context': 9.0, 'Multi-turn': 6.0, 'Security': 8.5,
    'Multi-language': 8.0, 'Reliability': 5.0, 'Hallucination': 8.0,
    'Variance': 10.0, 'Edge cases': 9.5, 'Cost-efficiency': 9.0,
    'Documentation': 3.0,
}
simple_avg = sum(scores.values()) / len(scores)
print(f'Simple average: {simple_avg:.4f} (rounds to {round(simple_avg, 1)})')
print(f'Final subjective score: 7.0 (production considerations weighted)')
print(f'Difference: {simple_avg - 7.0:.2f} (weight on date hallucination, multi-needle bias, multi-turn bug)')
"
```

## Re-running individual phases

All scripts are in `raw_data/scripts/`. They can be run directly:

```bash
# Scripts are directly in raw_data/scripts/
# Set your API key first:
export OPENROUTER_API_KEYS="sk-or-v1-your-key-1,sk-or-v1-your-key-2"
```

### Phase 1: Reasoning budget bug (288 entries)

```bash
python3 scripts/v3_infra.py  # verify infrastructure loads
# The Phase 1 sweep is part of the v3 infrastructure
# See scripts/v3_infra.py for the call_ling_v3() function
```

### v6 Gap 1: Tool calling (52 entries)

```bash
python3 scripts/v6_gap1_toolcalling.py
# Output: v6_phase_tool_calling.jsonl (in LING3_LOGS_DIR)
```

### v6 Gap 2: Long context (66 entries)

```bash
# Note: v6_gap2_longcontext.py has a known overshoot bug
# Use the fixed version instead:
python3 scripts/v6_gap2_longcontext_fix.py
# Output: v6_phase_long_context.jsonl
```

### v6 Gap 3: Multi-turn coding (35 entries)

```bash
python3 scripts/v6_gap3_multiturn.py
# Output: v6_phase_multiturn.jsonl
```

## Regenerating the analysis report

```bash
python3 scripts/generate_v6_report.py
# Output: v6_report.md (in current directory or LING3_REPORT_PATH)
```

## Regenerating the README charts

The charts in `assets/` were generated from the JSONL data. To regenerate them:

```bash
# The chart generation script is not in the repo, but can be reconstructed
# from the data. Key data points:

# Chart 1: reasoning_bug_threshold.png
# Source: phase1_logs.jsonl
# X-axis: max_tokens values [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]
# Y-axis: 0-char output rate (%) and avg reasoning_tokens

# Chart 2: scorecard_radar.png
# Source: README scorecard table (13 dimensions, scores 0-10)

# Chart 3: cross_model_comparison.png
# Source: README cross-model comparison table

# Chart 4: long_context_accuracy.png
# Source: v6_phase_long_context.jsonl

# Chart 5: test_coverage_pie.png
# Source: README test coverage table (845 entries by phase)
```

## Schema notes

### Standard schema (most phases)

All JSONL entries follow this schema (documented in `methodology.md`):

```json
{
  "id": "uuid-v4",
  "timestamp": "ISO 8601",
  "phase": "phase1_reasoning_bug",
  "test_id": "1.1_A1_math_mt128_ra1",
  "run": 1,
  "provider": "openrouter",
  "endpoint": "https://openrouter.ai/api/v1/chat/completions",
  "model": "inclusionai/ling-3.0-flash:free",
  "system_prompt": "...",
  "user_prompt": "...",
  "tools": [],
  "parameters": {
    "max_tokens": 8192,
    "temperature": 0,
    "seed": 42,
    "reasoning": {"enabled": true, "effort": "medium"}
  },
  "response": {
    "content": "...",
    "reasoning": "",
    "tool_calls": [],
    "finish_reason": "stop"
  },
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "reasoning_tokens": 789,
    "total_tokens": 1368
  },
  "latency_ms": 1234,
  "ttft_ms": 0,
  "status_code": 200,
  "error": null,
  "observations": "string or object"
}
```

### Compact schema (v6 long context)

The `v6_phase_long_context.jsonl` file uses a slightly compact format to keep file size manageable:

- `messages` field may be stored as `"TRUNCATED_FOR_SPACE"` string (full prompt content is in `results/raw_data/chat3/` per-test JSONs)
- `observations` is a JSON object (not a string) with fields like `test_type`, `length_target`, `position_pct`, `expected`, `needle_found`, `actual_answer`

### Per-test JSON files (chat1, chat3)

The `results/raw_data/chat1/` and `results/raw_data/chat3/` directories contain individual JSON files (one per API call) with a slightly different schema that predates the v3 JSONL format. These are preserved for historical reference; the JSONL files in the ZIP are the canonical source.

## Cost estimate

At OpenRouter's free tier (rate-limited per key per day):
- 845 calls total across 12 phases
- Plan around the daily per-key quota when re-running the full evaluation

If you exceed the free tier, paid pricing is approximately $0.07/M input tokens and $0.28/M output tokens. The full 845-call evaluation used ~3M input + ~2M output tokens total, so paid cost would be ~$0.77.

## Troubleshooting

### HTTP 429 rate limited

OpenRouter's free tier is aggressively rate-limited. The scripts handle this with key rotation and 60-second cooldowns, but you may still see 429s. Strategies:
- Use more API keys (set `OPENROUTER_API_KEYS` with comma-separated values)
- Wait between phase runs
- Reduce `max_tokens` (faster responses, fewer tokens consumed)

### HTTP 400 "context length exceeded"

You'll see this when testing context windows > 262,144 tokens. This is expected behavior — the API explicitly enforces the 262,144 token hard limit.

### Empty content with `finish_reason=length`

This is the reasoning-budget bug documented in [`analysis/CONSOLIDATED_ANALYSIS.md`](analysis/CONSOLIDATED_ANALYSIS.md) §1 (Reasoning Budget Bug). The fix is to either:
- Increase `max_tokens` to ≥ 2048 (4096 for CJK)
- Set `reasoning.enabled=false` in the request

## Contact

For questions about this evaluation, open an issue at [github.com/frangelbarrera/Ling-3-flash-evaluation/issues](https://github.com/frangelbarrera/Ling-3-flash-evaluation/issues).

For questions about Ling-3.0-flash itself, see the [official Ant Group / inclusionAI channels](https://github.com/inclusionAI).
