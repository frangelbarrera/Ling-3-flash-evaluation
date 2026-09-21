# Security Policy

## Purpose

This policy explains how to report security issues that affect this repository.
The repository is an independent, reproducible evaluation of Ling-3.0-flash
based on published data and on calls made through OpenRouter. It is a research
artifact, not a production system, and it has no operational infrastructure.

## Reporting a vulnerability

If GitHub's private vulnerability reporting is enabled for this repository, use the
Security tab and choose 'Report a vulnerability'. If that option is unavailable,
contact the maintainer through https://github.com/frangelbarrera.

Please do not open public issues for security reports.

This project is maintained by a single maintainer on a best-effort basis. There
is no dedicated security team, no bug bounty program, and no guaranteed
response time.

## Scope

In scope:

- The validation scripts in `scripts/` and `raw_data/scripts/`.
- The GitHub Actions workflow in `.github/workflows/`.
- Executable documentation (commands and code snippets in `README.md`,
  `REPRODUCING.md`, and `methodology.md`).
- The files published in this repository (logs, prompts, analysis, tests,
  configuration).

Out of scope:

- Vulnerabilities in OpenRouter or its API.
- Vulnerabilities in Ant Group / inclusionAI, in Ling-3.0-flash, or in any
  other model.
- Vulnerabilities in external APIs or third-party services referenced by the
  evaluation (for example, SecurityTrails).
- Issues in third-party systems that this repository merely links to.

Reports about out-of-scope systems should be sent to the corresponding vendor.

## Secrets handling

Do not publish real secrets in issues, pull requests, test fixtures, logs, or
any other file in this repository. If a real credential is accidentally
published, report it privately as described above so it can be removed and
revoked. Note that anything committed to Git history remains retrievable until
the history is rewritten; removal from the tip of the branch does not erase it
from past commits.

## Security vulnerabilities vs. scientific or methodological errors

This repository documents an evaluation. Reports about its scientific or
methodological content — for example, a disputed score, a suspected
measurement error, a sample-size concern, or a disagreement with an
interpretation — are not security vulnerabilities. Please raise those as
regular issues so they can be discussed publicly and traced to the raw JSONL
records in `raw_data/ling3_v3/logs/`.

## Synthetic security-test fixtures

This repository contains deliberately synthetic values that were used to test
how the evaluated model handles user-supplied secrets. They originate in the
security tests of the evaluation and also appear in files that document those
tests:

- `sk-test-12345` — a synthetic API-key-shaped string used in secret-handling
  tests (`raw_data/ling3_v3/prompts/phase6_prompts.md`,
  `raw_data/ling3_v3/logs/phase6_logs.jsonl`).
- `ghp_abc123def456` — a synthetic GitHub-token-shaped string used in the same
  tests (same files).
- `[FREE_SECURITYTRAILS_API_KEY]` — a bracketed placeholder used in a
  reconnaissance-planning test (`results/raw_data/chat3/`).
- A synthetic OpenSSH private-key block whose body is the placeholder
  `[test-key]` (`raw_data/ling3_v3/prompts/phase6_prompts.md`,
  `raw_data/ling3_v3/logs/phase6_logs.jsonl`).

These are evaluation fixtures, not operational credentials: they do not belong
to any account, they are not valid for any service, and no real API key,
token, or private key is published in this repository. They are kept because
they are part of the evaluated prompts and of the recorded model responses.

Some secret scanners may flag these strings; for example, older versions of
Gitleaks report the OpenSSH fixture under the `private-key` rule. This file
documents what the values are; it does not change how any scanner behaves.
