#!/usr/bin/env python3
"""Deterministically summarize the published JSONL evaluation logs.

This tool is intentionally offline: it reads local files only and never imports
or calls an API client. Missing fields are reported as ``Not documented`` rather
than inferred.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_CORE_FIELDS = ("phase", "model", "timestamp")


def summarize_logs(logs_dir: Path) -> dict[str, Any]:
    """Return a reproducible summary of JSONL records under *logs_dir*."""
    files = sorted(logs_dir.glob("*.jsonl"))
    phase_counts: Counter[str] = Counter()
    model_counts: Counter[str] = Counter()
    provider_counts: Counter[str] = Counter()
    endpoint_counts: Counter[str] = Counter()
    missing_counts: Counter[str] = Counter()
    file_counts: dict[str, int] = {}
    parse_errors: list[dict[str, Any]] = []
    total = 0

    for path in files:
        count = 0
        with path.open(encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, 1):
                if not raw_line.strip():
                    continue
                try:
                    record = json.loads(raw_line)
                except json.JSONDecodeError as exc:
                    parse_errors.append(
                        {"file": str(path), "line": line_number, "error": str(exc)}
                    )
                    continue
                if not isinstance(record, dict):
                    parse_errors.append(
                        {"file": str(path), "line": line_number, "error": "record is not an object"}
                    )
                    continue
                count += 1
                total += 1
                for field in REQUIRED_CORE_FIELDS:
                    if record.get(field) in (None, ""):
                        missing_counts[field] += 1
                phase_counts[str(record.get("phase") or "Not documented")] += 1
                model_counts[str(record.get("model") or "Not documented")] += 1
                provider_counts[str(record.get("provider") or "Not documented")] += 1
                endpoint_counts[str(record.get("endpoint") or "Not documented")] += 1
        file_counts[str(path)] = count

    return {
        "logs_dir": str(logs_dir),
        "files": len(files),
        "records": total,
        "parse_errors": parse_errors,
        "files_by_record_count": file_counts,
        "phase_counts": dict(sorted(phase_counts.items())),
        "model_counts": dict(sorted(model_counts.items())),
        "provider_counts": dict(sorted(provider_counts.items())),
        "endpoint_counts": dict(sorted(endpoint_counts.items())),
        "missing_core_fields": dict(sorted(missing_counts.items())),
        "retry_policy": "Not documented in the published JSONL schema",
        "call_status": "Not documented consistently; inspect status_code/error per record",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs_dir", type=Path, nargs="?", default=Path("raw_data/ling3_v3/logs"))
    args = parser.parse_args()
    summary = summarize_logs(args.logs_dir)
    print(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True))
    return 1 if summary["parse_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
