from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

from digital_twin.research.models import ComplexityInputs, ResearchTask
from digital_twin.research.orchestration import AdaptiveOrchestrationPlanner, OrchestrationPolicy
from digital_twin.research.validators import validate_plan


def _task_from_json(data: Dict[str, Any]) -> ResearchTask:
    complexity = ComplexityInputs(**data.get("complexity", {}))
    return ResearchTask(
        task_id=data["task_id"],
        question=data["question"],
        profile=data.get("profile", "literature-review"),
        date_range=data.get("date_range"),
        languages=data.get("languages", ["en"]),
        paper_type_constraints=data.get("paper_type_constraints", []),
        inclusion_criteria=data.get("inclusion_criteria", []),
        exclusion_criteria=data.get("exclusion_criteria", []),
        complexity=complexity,
    )


def cmd_plan(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.task).read_text(encoding="utf-8"))
    task = _task_from_json(data)
    planner = AdaptiveOrchestrationPlanner(
        OrchestrationPolicy(max_subagents=args.max_subagents, max_parallelism=args.max_parallelism)
    )
    plan = planner.plan(task)
    issues = validate_plan(plan)
    payload = {
        "plan": asdict(plan),
        "validation": [asdict(issue) for issue in issues],
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, default=lambda o: o.value)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 1 if any(issue.severity.value in ("major", "critical") for issue in issues) else 0


def cmd_example(_: argparse.Namespace) -> int:
    example = {
        "task_id": "RQ-EXAMPLE-001",
        "question": "What evidence compares single-agent and multi-agent systems on software engineering benchmarks?",
        "profile": "literature-review",
        "date_range": "2024-2026",
        "languages": ["en"],
        "inclusion_criteria": ["original comparative research", "shared benchmark"],
        "exclusion_criteria": ["marketing pages", "papers without direct comparison"],
        "complexity": {
            "breadth": 2,
            "topic_count": 2,
            "discipline_count": 2,
            "expected_paper_count": 20,
            "recency_requirement": 2,
            "methodology_diversity": 2,
            "mixed_evidence_types": 1,
            "evidence_conflict": 2,
            "source_quality_requirement": 3,
            "statistical_comparison": 1,
            "independent_review_need": 2,
            "uncertainty": 2,
        },
    }
    print(json.dumps(example, ensure_ascii=False, indent=2))
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Research Adaptive Orchestration CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", help="Build and validate a deterministic orchestration plan")
    plan.add_argument("task", help="Path to a research task JSON file")
    plan.add_argument("--output")
    plan.add_argument("--max-subagents", type=int, default=5)
    plan.add_argument("--max-parallelism", type=int, default=3)
    plan.set_defaults(func=cmd_plan)

    example = sub.add_parser("example-task", help="Print an example task schema")
    example.set_defaults(func=cmd_example)

    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
