from __future__ import annotations

import unittest

from scripts.verify_thesis_results import _exit_code, _summarize


class ThesisResultVerifierTests(unittest.TestCase):
    def test_summary_and_exit_code_pass_when_all_rows_pass(self) -> None:
        summary = _summarize([{"status": "PASS"}, {"status": "PASS"}])
        self.assertEqual(summary, {"PASS": 2, "FAIL": 0, "MISSING": 0, "TOTAL": 2})
        self.assertEqual(_exit_code(summary), 0)

    def test_exit_code_fails_for_failed_or_missing_rows(self) -> None:
        self.assertEqual(_exit_code({"PASS": 1, "FAIL": 1, "MISSING": 0, "TOTAL": 2}), 1)
        self.assertEqual(_exit_code({"PASS": 1, "FAIL": 0, "MISSING": 1, "TOTAL": 2}), 1)


if __name__ == "__main__":
    unittest.main()
