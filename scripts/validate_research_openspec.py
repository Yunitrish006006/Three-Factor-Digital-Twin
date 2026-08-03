from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence


ROOT = Path(__file__).resolve().parents[1]
OPENSPEC = ROOT / "openspec"
SCHEMA_DIR = OPENSPEC / "schemas" / "research-first"
TEMPLATE_DIR = SCHEMA_DIR / "templates"
ARCHIVE_DIR = OPENSPEC / "changes" / "archive"

REQUIREMENT_HEADING = re.compile(
    r"^### Requirement:\s+([A-Z][A-Z0-9]{2,7}-\d{3})\b.*$",
    re.MULTILINE,
)
SCENARIO_HEADING = re.compile(r"^#### Scenario:\s+.+$", re.MULTILINE)
ARTIFACT_ID = re.compile(r"^\s{2}- id:\s+([a-z][a-z0-9-]*)\s*$", re.MULTILINE)
TEMPLATE_REF = re.compile(r"^\s+template:\s+([A-Za-z0-9_.-]+)\s*$", re.MULTILINE)
REQUIRES_REF = re.compile(r"^\s+requires:\s+\[([^\]]*)\]\s*$", re.MULTILINE)


@dataclass(frozen=True)
class ValidationSummary:
    spec_files: int
    requirements: int
    scenarios: int
    active_changes: int


def main() -> None:
    errors, summary = validate_repository()
    if errors:
        print("Research OpenSpec validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(
        "Research OpenSpec validation passed: "
        f"{summary.spec_files} spec files, "
        f"{summary.requirements} requirements, "
        f"{summary.scenarios} scenarios, "
        f"{summary.active_changes} active changes."
    )


def validate_repository() -> tuple[List[str], ValidationSummary]:
    errors: List[str] = []
    _validate_required_layout(errors)
    _validate_config(errors)
    _validate_schema(errors)

    spec_files = sorted((OPENSPEC / "specs").glob("*/spec.md"))
    requirement_ids: dict[str, Path] = {}
    requirement_count = 0
    scenario_count = 0
    for path in spec_files:
        counts = _validate_spec(path, errors, requirement_ids=requirement_ids)
        requirement_count += counts[0]
        scenario_count += counts[1]

    change_dirs = _active_change_dirs()
    for path in change_dirs:
        _validate_change(path, errors)
    for path in _archived_change_dirs():
        _validate_archived_change(path, errors)

    summary = ValidationSummary(
        spec_files=len(spec_files),
        requirements=requirement_count,
        scenarios=scenario_count,
        active_changes=len(change_dirs),
    )
    return errors, summary


def _validate_required_layout(errors: List[str]) -> None:
    required_files = [
        OPENSPEC / "README.md",
        OPENSPEC / "config.yaml",
        SCHEMA_DIR / "schema.yaml",
        OPENSPEC / "changes" / "README.md",
        OPENSPEC / "changes" / "archive" / "README.md",
    ]
    template_names = [
        "proposal.md",
        "research.md",
        "protocol.md",
        "specs.md",
        "design.md",
        "reproducibility.md",
        "tasks.md",
        "evidence.md",
    ]
    required_files.extend(TEMPLATE_DIR / name for name in template_names)
    for path in required_files:
        if not path.is_file():
            errors.append(f"missing required file: {_relative(path)}")

    spec_root = OPENSPEC / "specs"
    if not spec_root.is_dir():
        errors.append("missing required directory: openspec/specs")
    elif not any(spec_root.glob("*/spec.md")):
        errors.append("openspec/specs contains no capability spec.md files")


def _validate_config(errors: List[str]) -> None:
    path = OPENSPEC / "config.yaml"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if not re.search(r"^schema:\s+research-first\s*$", text, re.MULTILINE):
        errors.append("openspec/config.yaml must set schema: research-first")
    if not re.search(r"^context:\s*\|?\s*$", text, re.MULTILINE):
        errors.append("openspec/config.yaml is missing context:")
    if not re.search(r"^rules:\s*$", text, re.MULTILINE):
        errors.append("openspec/config.yaml is missing rules:")


def _validate_schema(errors: List[str]) -> None:
    path = SCHEMA_DIR / "schema.yaml"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if not re.search(r"^name:\s+research-first\s*$", text, re.MULTILINE):
        errors.append("research-first/schema.yaml has the wrong schema name")

    artifact_ids = ARTIFACT_ID.findall(text)
    expected_order = [
        "proposal",
        "research",
        "protocol",
        "specs",
        "design",
        "reproducibility",
        "tasks",
        "evidence",
    ]
    if artifact_ids != expected_order:
        errors.append(
            "research-first artifact order must be "
            + " -> ".join(expected_order)
            + f"; found {artifact_ids}"
        )

    for template in TEMPLATE_REF.findall(text):
        if not (TEMPLATE_DIR / template).is_file():
            errors.append(f"schema references missing template: {template}")

    known = set(artifact_ids)
    for raw_requires in REQUIRES_REF.findall(text):
        for dependency in _split_inline_list(raw_requires):
            if dependency and dependency not in known:
                errors.append(f"schema references unknown artifact dependency: {dependency}")

    apply_match = re.search(
        r"^apply:\s*$.*?^\s+requires:\s+\[([^\]]*)\]\s*$.*?^\s+tracks:\s+tasks\.md\s*$",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if apply_match is None or "tasks" not in _split_inline_list(apply_match.group(1)):
        errors.append("schema apply block must require tasks and track tasks.md")


def _validate_spec(
    path: Path,
    errors: List[str],
    requirement_ids: dict[str, Path] | None = None,
) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8")
    is_delta = "## ADDED Requirements" in text
    if not text.startswith("# "):
        errors.append(f"{_relative(path)} must start with a level-1 title")
    if not is_delta and "## Purpose" not in text:
        errors.append(f"{_relative(path)} is missing ## Purpose")
    if "## Requirements" not in text and not is_delta:
        errors.append(f"{_relative(path)} has no requirements section")

    matches = list(REQUIREMENT_HEADING.finditer(text))
    if not matches:
        errors.append(f"{_relative(path)} has no valid requirement headings")
        return 0, 0

    scenario_total = 0
    for index, match in enumerate(matches):
        requirement_id = match.group(1)
        if requirement_ids is not None:
            previous = requirement_ids.get(requirement_id)
            if previous is not None:
                errors.append(
                    f"duplicate requirement ID {requirement_id}: "
                    f"{_relative(previous)} and {_relative(path)}"
                )
            else:
                requirement_ids[requirement_id] = path

        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.end() : end]
        statement = block.split("#### Scenario:", 1)[0]
        if not re.search(r"\bSHALL\b", statement):
            errors.append(
                f"{_relative(path)} requirement {requirement_id} lacks a SHALL statement"
            )

        scenarios = list(SCENARIO_HEADING.finditer(block))
        if not scenarios:
            errors.append(
                f"{_relative(path)} requirement {requirement_id} has no scenarios"
            )
            continue
        scenario_total += len(scenarios)
        for scenario_index, scenario in enumerate(scenarios):
            scenario_end = (
                scenarios[scenario_index + 1].start()
                if scenario_index + 1 < len(scenarios)
                else len(block)
            )
            scenario_block = block[scenario.end() : scenario_end]
            if "**WHEN**" not in scenario_block:
                errors.append(
                    f"{_relative(path)} scenario '{scenario.group(0)}' lacks **WHEN**"
                )
            if "**THEN**" not in scenario_block:
                errors.append(
                    f"{_relative(path)} scenario '{scenario.group(0)}' lacks **THEN**"
                )
    return len(matches), scenario_total


def _active_change_dirs() -> List[Path]:
    changes = OPENSPEC / "changes"
    if not changes.is_dir():
        return []
    return sorted(
        path
        for path in changes.iterdir()
        if path.is_dir() and path.name != "archive"
    )


def _archived_change_dirs() -> List[Path]:
    if not ARCHIVE_DIR.is_dir():
        return []
    return sorted(path for path in ARCHIVE_DIR.iterdir() if path.is_dir())


def _validate_change(path: Path, errors: List[str]) -> None:
    metadata = path / ".openspec.yaml"
    if not metadata.is_file():
        errors.append(f"{_relative(path)} is missing .openspec.yaml")
    elif not re.search(
        r"^schema:\s+research-first\s*$",
        metadata.read_text(encoding="utf-8"),
        re.MULTILINE,
    ):
        errors.append(f"{_relative(metadata)} must set schema: research-first")

    planning_files = [
        "proposal.md",
        "research.md",
        "protocol.md",
        "design.md",
        "reproducibility.md",
        "tasks.md",
    ]
    for name in planning_files:
        if not (path / name).is_file():
            errors.append(f"{_relative(path / name)} is missing from active change")

    delta_specs = sorted((path / "specs").glob("*/spec.md"))
    if not delta_specs:
        errors.append(f"{_relative(path)} has no delta specs")
    for delta_spec in delta_specs:
        _validate_spec(delta_spec, errors)

    tasks = path / "tasks.md"
    if tasks.is_file():
        task_text = tasks.read_text(encoding="utf-8")
        checkboxes = re.findall(r"^\s*-\s+\[([ xX])\]\s+", task_text, re.MULTILINE)
        if not checkboxes:
            errors.append(f"{_relative(tasks)} has no checkbox tasks")
        if checkboxes and all(value.lower() == "x" for value in checkboxes):
            evidence = path / "evidence.md"
            if not evidence.is_file():
                errors.append(
                    f"{_relative(path)} has all tasks complete but no evidence.md"
                )


def _validate_archived_change(path: Path, errors: List[str]) -> None:
    required_files = [
        ".openspec.yaml",
        "proposal.md",
        "research.md",
        "protocol.md",
        "design.md",
        "reproducibility.md",
        "tasks.md",
        "evidence.md",
    ]
    for name in required_files:
        if not (path / name).is_file():
            errors.append(f"{_relative(path / name)} is missing from archived change")

    metadata = path / ".openspec.yaml"
    if metadata.is_file() and not re.search(
        r"^schema:\s+research-first\s*$",
        metadata.read_text(encoding="utf-8"),
        re.MULTILINE,
    ):
        errors.append(f"{_relative(metadata)} must set schema: research-first")

    delta_specs = sorted((path / "specs").glob("*/spec.md"))
    if not delta_specs:
        errors.append(f"{_relative(path)} has no delta specs")
    for delta_spec in delta_specs:
        _validate_spec(delta_spec, errors)

    tasks = path / "tasks.md"
    if tasks.is_file():
        task_states = _checkbox_states(tasks.read_text(encoding="utf-8"))
        if not task_states:
            errors.append(f"{_relative(tasks)} has no checkbox tasks")
        elif any(value.lower() != "x" for value in task_states):
            errors.append(f"{_relative(tasks)} has unchecked tasks after archival")

    proposal = path / "proposal.md"
    if proposal.is_file():
        proposal_states = _checkbox_states(proposal.read_text(encoding="utf-8"))
        if any(value.lower() != "x" for value in proposal_states):
            errors.append(
                f"{_relative(proposal)} has unchecked completion criteria after archival"
            )


def _checkbox_states(text: str) -> List[str]:
    return re.findall(r"^\s*-\s+\[([ xX])\]\s+", text, re.MULTILINE)


def _split_inline_list(raw: str) -> List[str]:
    return [item.strip().strip("'\"") for item in raw.split(",") if item.strip()]


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    main()
