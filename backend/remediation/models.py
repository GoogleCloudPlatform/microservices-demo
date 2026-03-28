from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class WorkloadState:
    service: str
    exists: bool = False
    running: bool = False
    healthy: bool = False
    status: str = "unknown"
    restart_count: int = 0
    exit_code: Optional[int] = None
    oom_killed: bool = False
    message: str = ""
    alternatives: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ActionProposal:
    source: str = "rule"
    proposed_action: str = "restart_service"
    target: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    rationale: str = ""
    containment_preference: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ActionDecision:
    action: str
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    rationale: str = ""
    source: str = "rule"
    retry_budget: int = 1
    evaluation_window_s: float = 2.0
    backoff_s: float = 1.0
    allowed_actions: List[str] = field(default_factory=list)
    containment_actions: List[str] = field(default_factory=list)
    manual_only: bool = False
    rollback_action: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ActionExecutionRecord:
    action: str
    target: str
    success: bool
    started_at: str
    finished_at: str
    duration_s: float
    message: str = ""
    stdout: str = ""
    stderr: str = ""
    error: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class IncidentEvaluation:
    success: bool
    verdict: str
    before_snapshot: Dict[str, Any] = field(default_factory=dict)
    after_snapshot: Dict[str, Any] = field(default_factory=dict)
    score_delta: float = 0.0
    remaining_affected_services: List[str] = field(default_factory=list)
    next_step: str = ""
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContainmentState:
    active: bool = False
    containment_mode: str = "none"
    next_action: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    escalated: bool = False
    manual_required: bool = False
    reason: str = ""
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MemoryRecord:
    incident_id: str
    service: str
    failure_type: str
    severity: str
    feature_flags: List[str] = field(default_factory=list)
    evidence_summary: str = ""
    metric_signature: Dict[str, float] = field(default_factory=dict)
    selected_action: str = ""
    outcome: str = ""
    recurrence_count: int = 0
    notes: str = ""
    similarity_score: float = 0.0
    created_at: str = field(default_factory=utcnow_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Incident:
    id: str
    detected_at: str
    root_cause_service: str
    affected_services: List[str]
    failure_type: str
    severity: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    current_phase: str = "decision"
    status: str = "active"
    retry_count: int = 0
    proposal: Optional[ActionProposal] = None
    decision: Optional[ActionDecision] = None
    execution_history: List[ActionExecutionRecord] = field(default_factory=list)
    evaluation: Optional[IncidentEvaluation] = None
    containment: ContainmentState = field(default_factory=ContainmentState)
    memory_matches: List[Dict[str, Any]] = field(default_factory=list)
    operator_summary: str = ""

    @classmethod
    def create(
        cls,
        service: str,
        failure_type: str,
        severity: str = "warning",
        affected_services: Optional[List[str]] = None,
        evidence: Optional[Dict[str, Any]] = None,
        proposal: Optional[ActionProposal] = None,
    ) -> "Incident":
        return cls(
            id=str(uuid4()),
            detected_at=utcnow_iso(),
            root_cause_service=service,
            affected_services=affected_services or [service],
            failure_type=failure_type,
            severity=severity,
            evidence=evidence or {},
            proposal=proposal,
        )

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data
