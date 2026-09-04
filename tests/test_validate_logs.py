import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_logs import summarize_logs


class ValidateLogsTests(unittest.TestCase):
    def write_jsonl(self, path: Path, records: list[object]) -> None:
        path.write_text(
            "\n".join(json.dumps(record) for record in records) + "\n",
            encoding="utf-8",
        )

    def test_summary_counts_records_and_missing_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            logs_dir = Path(directory)
            self.write_jsonl(
                logs_dir / "phase.jsonl",
                [
                    {
                        "phase": "phase_demo",
                        "model": "demo/model",
                        "timestamp": "2026-01-01T00:00:00Z",
                        "provider": "local",
                        "endpoint": "https://example.invalid",
                    },
                    {"phase": "phase_demo", "model": "demo/model"},
                ],
            )

            summary = summarize_logs(logs_dir)

            self.assertEqual(summary["records"], 2)
            self.assertEqual(summary["files"], 1)
            self.assertEqual(summary["phase_counts"], {"phase_demo": 2})
            self.assertEqual(summary["model_counts"], {"demo/model": 2})
            self.assertEqual(summary["missing_core_fields"], {"timestamp": 1})
            self.assertEqual(summary["parse_errors"], [])

    def test_summary_reports_malformed_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            logs_dir = Path(directory)
            (logs_dir / "bad.jsonl").write_text(
                '{"phase": "ok"}\nnot-json\n', encoding="utf-8"
            )

            summary = summarize_logs(logs_dir)

            self.assertEqual(summary["records"], 1)
            self.assertEqual(len(summary["parse_errors"]), 1)
            self.assertEqual(summary["parse_errors"][0]["line"], 2)


if __name__ == "__main__":
    unittest.main()
