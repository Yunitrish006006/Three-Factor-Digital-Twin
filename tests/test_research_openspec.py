from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import validate_research_openspec


ROOT = Path(__file__).resolve().parents[1]


class ResearchOpenSpecTests(unittest.TestCase):
    def test_research_openspec_structure_is_valid(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_research_openspec.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        self.assertIn("Research OpenSpec validation passed", completed.stdout)

    def test_archived_change_rejects_unchecked_completion_criteria(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            change = Path(temporary_dir) / "2026-08-03-example"
            (change / "specs" / "research-governance").mkdir(parents=True)
            (change / ".openspec.yaml").write_text(
                "schema: research-first\n", encoding="utf-8"
            )
            for name in [
                "research.md",
                "protocol.md",
                "design.md",
                "reproducibility.md",
                "evidence.md",
            ]:
                (change / name).write_text(f"# {name}\n", encoding="utf-8")
            (change / "tasks.md").write_text(
                "# Tasks\n\n- [x] Complete the work.\n", encoding="utf-8"
            )
            proposal = change / "proposal.md"
            proposal.write_text(
                "# Proposal\n\n## Completion Criteria\n\n- [ ] Verify the result.\n",
                encoding="utf-8",
            )
            (change / "specs" / "research-governance" / "spec.md").write_text(
                "# Delta\n\n"
                "## ADDED Requirements\n\n"
                "### Requirement: TST-001 Archive fixture\n\n"
                "The fixture SHALL remain valid.\n\n"
                "#### Scenario: Validate the fixture\n\n"
                "- **WHEN** the fixture is checked\n"
                "- **THEN** validation SHALL complete\n",
                encoding="utf-8",
            )

            errors: list[str] = []
            validate_research_openspec._validate_archived_change(change, errors)
            self.assertTrue(
                any("unchecked completion criteria" in error for error in errors),
                msg=errors,
            )

            proposal.write_text(
                "# Proposal\n\n## Completion Criteria\n\n- [x] Verify the result.\n",
                encoding="utf-8",
            )
            errors = []
            validate_research_openspec._validate_archived_change(change, errors)
            self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
