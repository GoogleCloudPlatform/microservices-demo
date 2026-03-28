from __future__ import annotations

import time
from typing import Callable, Dict

from remediation.models import ActionDecision, Incident, IncidentEvaluation
from remediation.orchestrator import OrchestratorAdapter


class PostActionEvaluator:
    def __init__(self, score_provider: Callable[[], Dict[str, Dict]], orchestrator: OrchestratorAdapter) -> None:
        self.score_provider = score_provider
        self.orchestrator = orchestrator

    def evaluate(
        self,
        incident: Incident,
        decision: ActionDecision,
        before_scores: Dict[str, Dict],
    ) -> IncidentEvaluation:
        wait_s = max(0.0, float(decision.evaluation_window_s))
        if decision.action in {"start_service", "restart_service", "restart_dependency_chain"} and self.orchestrator.platform == "kubernetes":
            wait_s = max(wait_s, 10.0)

        service = incident.root_cause_service
        before_snapshot = before_scores.get(service, {})
        before_score = float(before_snapshot.get("combined_score", 0.0) or 0.0)
        workload = self.orchestrator.inspect_service(service)
        deadline = time.time() + wait_s

        while time.time() < deadline:
            if decision.action in {"isolate_service", "stop_service"}:
                if not workload.running:
                    break
            elif decision.action == "reroute_service":
                break
            elif workload.running and workload.healthy:
                break
            time.sleep(1.0)
            workload = self.orchestrator.inspect_service(service)

        after_scores = self.score_provider() or {}
        after_snapshot = after_scores.get(service, {})
        after_score = float(after_snapshot.get("combined_score", 0.0) or 0.0)
        score_delta = round(after_score - before_score, 3)

        if decision.action in {"isolate_service", "stop_service"}:
            success = not workload.running
            verdict = "contained" if success else "containment_failed"
            next_step = "observe" if success else "escalate"
        elif decision.action == "reroute_service":
            success = bool(decision.parameters.get("alternative"))
            verdict = "rerouted" if success else "reroute_unavailable"
            next_step = "monitor" if success else "escalate"
        else:
            workload_healthy = workload.running and workload.healthy
            score_improved = after_score <= before_score + 0.02 or after_score < 0.7
            success = workload_healthy and (score_improved or before_score == 0.0)
            verdict = "resolved" if success else "degraded"
            next_step = "close" if success else "contain"

        message = (
            f"before={before_score:.3f}, after={after_score:.3f}, "
            f"workload={workload.status}, healthy={workload.healthy}"
        )

        return IncidentEvaluation(
            success=success,
            verdict=verdict,
            before_snapshot=before_snapshot,
            after_snapshot={
                **after_snapshot,
                "workload": workload.to_dict(),
            },
            score_delta=score_delta,
            remaining_affected_services=[] if success else list(incident.affected_services),
            next_step=next_step,
            message=message,
        )
