from __future__ import annotations

import logging
import os
import random
import time
from collections import deque
from pathlib import Path
from typing import Callable, Dict, List, Optional

from remediation.action_executor import ActionExecutor
from remediation.containment import ContainmentController
from remediation.evaluator import PostActionEvaluator
from remediation.memory import SQLiteIncidentMemoryStore
from remediation.models import (
    ActionDecision,
    ActionProposal,
    ContainmentState,
    Incident,
    MemoryRecord,
)
from remediation.orchestrator import DockerOrchestratorAdapter, KubernetesOrchestratorAdapter, OrchestratorAdapter
from remediation.policy import ActionPolicyEngine

logger = logging.getLogger(__name__)


class RemediationEngine:
    def __init__(
        self,
        score_provider: Optional[Callable[[], Dict[str, Dict]]] = None,
        target_seconds: int = 15,
        demo_mode: bool = False,
        orchestrator: Optional[OrchestratorAdapter] = None,
        memory_store: Optional[SQLiteIncidentMemoryStore] = None,
    ) -> None:
        self.target_seconds = target_seconds
        self.demo_mode = demo_mode
        self.score_provider = score_provider or (lambda: {})
        self.orchestrator = orchestrator or self._build_orchestrator()
        db_path = Path(os.getenv("INCIDENT_MEMORY_DB", "backend/.runtime/incident_memory.db"))
        self.memory_store = memory_store or SQLiteIncidentMemoryStore(db_path)
        self.policy_engine = ActionPolicyEngine()
        self.executor = ActionExecutor(self.orchestrator)
        self.evaluator = PostActionEvaluator(self.score_provider, self.orchestrator)
        self.containment = ContainmentController(self.orchestrator)
        self.active_incidents: Dict[str, Incident] = {}
        self.incident_history: deque[Incident] = deque(maxlen=200)

    def _build_orchestrator(self) -> OrchestratorAdapter:
        docker = DockerOrchestratorAdapter()
        if docker.available and not self.demo_mode:
            return docker
        return KubernetesOrchestratorAdapter()

    def remediate(
        self,
        service: str,
        failure_type: str,
        severity: str = "warning",
        affected_services: Optional[List[str]] = None,
        evidence: Optional[Dict] = None,
        proposal: Optional[ActionProposal] = None,
    ) -> Dict:
        start = time.time()
        incident = Incident.create(
            service=service,
            failure_type=failure_type,
            severity=severity,
            affected_services=affected_services or [service],
            evidence=evidence or {},
            proposal=proposal,
        )
        self.active_incidents[incident.id] = incident

        runtime_state = self.orchestrator.inspect_service(service)
        similar = self.memory_store.find_similar(
            service=service,
            failure_type=failure_type,
            feature_flags=(evidence or {}).get("feature_flags", []),
            metric_signature=self._metric_signature((evidence or {}).get("service_snapshot", {})),
            evidence_summary=self._evidence_summary(evidence or {}),
            limit=5,
        )
        incident.memory_matches = similar
        before_scores = self.score_provider() or {}
        incident.current_phase = "decision"
        decision = self.policy_engine.build_decision(incident, runtime_state, similar, proposal)
        incident.decision = decision

        records = []
        last_evaluation = None
        final_containment = ContainmentState(active=False, containment_mode="none", reason="No containment required")

        while True:
            incident.current_phase = "execution"
            step_records = self.executor.execute(decision)
            records.extend(step_records)
            incident.execution_history.extend(step_records)

            incident.current_phase = "evaluation"
            last_evaluation = self.evaluator.evaluate(incident, decision, before_scores)
            incident.evaluation = last_evaluation
            if last_evaluation.success:
                incident.status = "resolved"
                incident.current_phase = "memory_update"
                break

            final_containment = self.containment.decide(incident, decision, last_evaluation)
            incident.containment = final_containment

            if final_containment.next_action == "retry":
                incident.retry_count += 1
                sleep_s = min(2.5, decision.backoff_s + random.uniform(0.0, 0.5))
                time.sleep(sleep_s)
                continue

            if final_containment.next_action in {"isolate_service", "reroute_service"}:
                incident.current_phase = "containment"
                containment_decision = ActionDecision(
                    action=final_containment.next_action,
                    target=service,
                    parameters=final_containment.parameters,
                    confidence=decision.confidence,
                    rationale=final_containment.reason,
                    source="policy",
                )
                containment_records = self.executor.execute(containment_decision)
                records.extend(containment_records)
                incident.execution_history.extend(containment_records)
                last_evaluation = self.evaluator.evaluate(incident, containment_decision, before_scores)
                incident.evaluation = last_evaluation
                incident.status = "contained" if last_evaluation.success else "manual_required"
                if incident.status == "manual_required":
                    final_containment.escalated = True
                    final_containment.manual_required = True
                break

            incident.current_phase = "containment"
            final_containment.escalated = True
            final_containment.manual_required = True
            incident.status = "manual_required"
            break

        elapsed = round(time.time() - start, 3)
        incident.operator_summary = self._build_operator_summary(incident, runtime_state)
        self._persist_memory(incident)
        self.incident_history.appendleft(incident)
        if incident.status != "active":
            self.active_incidents.pop(incident.id, None)

        return {
            "incident_id": incident.id,
            "status": incident.status,
            "current_phase": incident.current_phase,
            "decision": decision.to_dict(),
            "execution_steps": [record.to_dict() for record in records],
            "evaluation": last_evaluation.to_dict() if last_evaluation else None,
            "containment": final_containment.to_dict(),
            "memory_matches": similar,
            "operator_summary": incident.operator_summary,
            "elapsed_s": elapsed,
            "within_target": elapsed <= self.target_seconds,
            "platform": self.orchestrator.platform,
            "demo_mode": self.demo_mode,
        }

    def validate_proposal(
        self,
        service: str,
        failure_type: str,
        proposal: ActionProposal,
        severity: str = "warning",
        affected_services: Optional[List[str]] = None,
        evidence: Optional[Dict] = None,
    ) -> Dict:
        incident = Incident.create(
            service=service,
            failure_type=failure_type,
            severity=severity,
            affected_services=affected_services or [service],
            evidence=evidence or {},
            proposal=proposal,
        )
        runtime_state = self.orchestrator.inspect_service(service)
        similar = self.memory_store.find_similar(
            service=service,
            failure_type=failure_type,
            feature_flags=(evidence or {}).get("feature_flags", []),
            metric_signature=self._metric_signature((evidence or {}).get("service_snapshot", {})),
            evidence_summary=self._evidence_summary(evidence or {}),
            limit=5,
        )
        decision = self.policy_engine.build_decision(incident, runtime_state, similar, proposal)
        return {
            "incident": incident.to_dict(),
            "runtime_state": runtime_state.to_dict(),
            "decision": decision.to_dict(),
            "memory_matches": similar,
            "accepted": proposal.proposed_action == decision.action and proposal.proposed_action in decision.allowed_actions,
        }

    def list_active_incidents(self) -> List[Dict]:
        return [incident.to_dict() for incident in self.active_incidents.values()]

    def list_incident_history(self, limit: int = 20) -> List[Dict]:
        return [incident.to_dict() for incident in list(self.incident_history)[:limit]]

    def similar_incidents(
        self,
        service: str,
        failure_type: str,
        feature_flags: Optional[List[str]] = None,
        metric_signature: Optional[Dict[str, float]] = None,
        evidence_summary: str = "",
        limit: int = 5,
    ) -> List[Dict]:
        return self.memory_store.find_similar(
            service=service,
            failure_type=failure_type,
            feature_flags=feature_flags,
            metric_signature=metric_signature,
            evidence_summary=evidence_summary,
            limit=limit,
        )

    def _persist_memory(self, incident: Incident) -> None:
        evidence = incident.evidence or {}
        record = MemoryRecord(
            incident_id=incident.id,
            service=incident.root_cause_service,
            failure_type=incident.failure_type,
            severity=incident.severity,
            feature_flags=evidence.get("feature_flags", []),
            evidence_summary=self._evidence_summary(evidence),
            metric_signature=self._metric_signature(evidence.get("service_snapshot", {})),
            selected_action=incident.decision.action if incident.decision else "",
            outcome=incident.status,
            recurrence_count=incident.retry_count,
            notes=incident.operator_summary,
        )
        self.memory_store.save(record)

    def _metric_signature(self, service_snapshot: Dict) -> Dict[str, float]:
        keys = [
            "combined_score",
            "cpu_percent",
            "mem_percent",
            "if_score",
            "lstm_score",
            "error_rate",
            "error_rate_mean",
        ]
        signature: Dict[str, float] = {}
        for key in keys:
            value = service_snapshot.get(key)
            if isinstance(value, (int, float)):
                signature[key] = float(value)
        return signature

    def _evidence_summary(self, evidence: Dict) -> str:
        feature_flags = ", ".join(evidence.get("feature_flags", []))
        recent_logs = evidence.get("recent_logs", [])
        summary = evidence.get("summary") or ""
        parts = [summary, feature_flags, " ".join(recent_logs[:2])]
        return " ".join(part for part in parts if part).strip()

    def _build_operator_summary(self, incident: Incident, runtime_state) -> str:
        decision = incident.decision.action if incident.decision else "unknown"
        verdict = incident.evaluation.verdict if incident.evaluation else "unknown"
        return (
            f"Incident {incident.id} on {incident.root_cause_service} "
            f"({incident.failure_type}) used {decision} on {self.orchestrator.platform}; "
            f"workload status was {runtime_state.status}; final outcome: {incident.status}/{verdict}."
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = RemediationEngine(score_provider=lambda: {}, demo_mode=True)
    print(engine.remediate("recommendationservice", "memory_leak"))
