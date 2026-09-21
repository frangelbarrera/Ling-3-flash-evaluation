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

### Deferred

- A narrow Gitleaks allowlist for the two synthetic private-key fixtures:
  deferred because the available fingerprint format depends on the Gitleaks
  version and on the scan mode, so a portable allowlist was not demonstrated.
  The synthetic fixtures are documented in `SECURITY.md`, and no broad
  exclusion was added.
