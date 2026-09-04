from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from .models import (
    ActivityType,
    ClaimRecord,
    ContradictionRecord,
    EvidenceRecord,
    GraphEdge,
    GraphNode,
    PaperRecord,
    ResearchEvent,
)


class ResearchStore:
    """Shared paper/evidence/claim registry and append-only replay log."""

    def __init__(self) -> None:
        self.papers: Dict[str, PaperRecord] = {}
        self.evidence: Dict[str, EvidenceRecord] = {}
        self.claims: Dict[str, ClaimRecord] = {}
        self.contradictions: Dict[str, ContradictionRecord] = {}
        self.graph_nodes: Dict[str, GraphNode] = {}
        self.graph_edges: List[GraphEdge] = []
        self.events: List[ResearchEvent] = []

    def append_event(self, event_type: ActivityType, actor: str, payload: dict) -> ResearchEvent:
        event = ResearchEvent.create(len(self.events) + 1, event_type, actor, payload)
        self.events.append(event)
        return event

    def add_paper(self, paper: PaperRecord) -> None:
        key = self._paper_dedup_key(paper)
        for current in self.papers.values():
            if self._paper_dedup_key(current) == key:
                raise ValueError(f"duplicate paper: {paper.paper_id} conflicts with {current.paper_id}")
        self.papers[paper.paper_id] = paper

    def add_evidence(self, evidence: EvidenceRecord) -> None:
        if evidence.paper_id not in self.papers:
            raise ValueError(f"unknown paper_id: {evidence.paper_id}")
        self.evidence[evidence.evidence_id] = evidence

    def add_claim(self, claim: ClaimRecord) -> None:
        self.claims[claim.claim_id] = claim

    def add_contradiction(self, contradiction: ContradictionRecord) -> None:
        self.contradictions[contradiction.contradiction_id] = contradiction

    def add_graph_node(self, node: GraphNode) -> None:
        self.graph_nodes[node.node_id] = node

    def add_graph_edge(self, edge: GraphEdge) -> None:
        self.graph_edges.append(edge)

    def replay(self) -> List[ResearchEvent]:
        return list(sorted(self.events, key=lambda item: item.sequence))

    def to_dict(self) -> dict:
        return {
            "papers": {k: asdict(v) for k, v in self.papers.items()},
            "evidence": {k: asdict(v) for k, v in self.evidence.items()},
            "claims": {k: asdict(v) for k, v in self.claims.items()},
            "contradictions": {k: asdict(v) for k, v in self.contradictions.items()},
            "graph_nodes": {k: asdict(v) for k, v in self.graph_nodes.items()},
            "graph_edges": [asdict(v) for v in self.graph_edges],
            "events": [asdict(v) for v in self.events],
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _paper_dedup_key(paper: PaperRecord) -> str:
        if paper.doi:
            return "doi:" + paper.doi.strip().lower().removeprefix("https://doi.org/")
        normalized = " ".join(paper.title.lower().split())
        return f"title:{normalized}|year:{paper.year or 'unknown'}"
