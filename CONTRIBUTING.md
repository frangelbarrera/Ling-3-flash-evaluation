# Contributing

This repository documents an independent, reproducible evaluation.
Contributions that keep the evidence traceable to the raw records are welcome.
This document describes the practical steps for proposing changes.

## Before you start

This is an independent project maintained on a best-effort basis. There is no
guaranteed review time and no committed maintenance schedule.

## Required checks

Run both offline checks before opening a pull request. They make no network
requests and take a few seconds:

```bash
python3 scripts/validate_logs.py
python3 -m unittest -v tests.test_validate_logs
```

Expected results: 12 JSONL files, 845 valid records, 0 parse errors, and both
tests passing. The same checks run in the repository's continuous integration
workflow (`.github/workflows/offline-validation.yml`).

## Data provenance

- Preserve the provenance of any new data: timestamps, phase identifiers,
  test identifiers, run numbers, and provider/model identifiers must be
  recorded as produced, not reconstructed from memory.
- Do not reformat, reorder, or re-indent the published JSONL logs or per-test
  JSON artifacts; they are the evidence behind the published totals.
- If you add data from a new evaluation round, keep it in a separate file set
  with its own phase labels instead of mixing it into existing files.

## Secrets

- Never include real API keys, tokens, passwords, or private keys in
  contributions — not in code, prompts, fixtures, logs, comments, or examples.
- If a test needs a secret-shaped value, use an obviously synthetic
  placeholder. The phase 6 security tests show the convention used in this
  repository.

## Methodological changes

- Describe any methodological change (parameters, scoring, aggregation,
  sample handling) explicitly in the pull request, and trace it to the
  affected records.
- Do not alter published results without an explanation of what changed, why,
  and how the change affects the totals or conclusions.
- Keep claims consistent with what the raw records support.

## Keeping changes reviewable

- Keep changes small and focused; one logical change per pull request.
- Reference the specific files and records a change affects.
- Prefer additive changes (new files, new phases) over edits to published
  data.

## Reporting problems

For bugs and documentation errors, open an issue at
`https://github.com/frangelbarrera/Ling-3-flash-evaluation/issues`.
For security issues, follow [SECURITY.md](SECURITY.md).
