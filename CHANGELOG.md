# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project does not currently publish version numbers, tags, or releases;
entries are recorded under [Unreleased] until a release process is defined.

## [Unreleased]

### Added

- Security policy (`SECURITY.md`): vulnerability reporting guidance, scope,
  secrets-handling rules, and documentation of the synthetic security-test
  fixtures.
- Citation metadata in Citation File Format (`CITATION.cff`).
- Contribution guidelines (`CONTRIBUTING.md`).
- Code of conduct (`CODE_OF_CONDUCT.md`), adapted from Contributor Covenant
  2.1.
- Narrow Gitleaks allowlist for synthetic test fixtures in `raw_data/ling3_v3/`
  and `results/raw_data/chat3/` (see `.gitleaksignore`). Covers the
  synthetic API-key, GitHub-token, and OpenSSH private-key fixtures
  documented in `SECURITY.md`.
