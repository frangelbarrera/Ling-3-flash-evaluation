# Results Summary

## Aggregated Scorecard

| Category | Tests | Pass | Fail | Partial | Success Rate |
|----------|:-----:|:----:|:----:|:-------:|:------------:|
| Math and Finance | 8 | 8 | 0 | 0 | 100% |
| Logic | 3 | 2 | 0 | 1 | 67% |
| Coding | 5 | 4 | 1 | 0 | 80% |
| Security Code Review | 2 | 2 | 0 | 0 | 100% |
| Prompt Injection | 3 | 2 | 0 | 1 | 67% |
| Phishing Detection | 5 | 5 | 0 | 0 | 100% |
| Multilingual | 5 | 3 | 0 | 2 | 60% |
| Cybersec Operations | 5 | 3 | 1 | 1 | 60% |
| Hallucination | 1 | 1 | 0 | 0 | 100% |
| Instruction Following | 1 | 1 | 0 | 0 | 100% |
| Creative | 1 | 0 | 1 | 0 | 0% |
| OSINT Planning | 1 | 1 | 0 | 0 | 100% |
| **Total** | **40** | **32** | **2** | **5** | **80%** |

## Jury Scores (Chat 3 — multi-perspective panel)

| Juror | Score | Verdict |
|-------|:-----:|---------|
| Cybersecurity Engineer | 78/100 | Suitable with supervision |
| Sysadmin / Console Expert | 67/100 | Competent copilot, not for live IR |
| Network Engineer | 84.8/100 | Suitable with restrictions |
| Principal Software Engineer | 80/100 | Solid in coding, bugs in JS debounce |
| Linguist / Creative Writer | 84/100 | Robust multilingual, typos in fr/de |
| QA Engineer (consistency) | 55/100 | Conditional use — severe bug |
| **Weighted average** | **74/100** | **Suitable for production with safeguards** |

## Raw Data Locations

- `results/raw_data/chat1/` — 60 JSON files from Session 1 (25 phases)
- `results/raw_data/chat3/` — 140+ JSON files from Session 3 (115+ test IDs)
- `raw_data/ling3_v3/logs/` — 12 consolidated JSONL logs (845 entries total)
- `raw_data/scripts/` — 6 Python scripts for reproducibility
- `raw_data/ling3_v3/prompts/` — 9 phase prompt files
