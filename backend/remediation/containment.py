from __future__ import annotations

from remediation.models import ActionDecision, ContainmentState, Incident, IncidentEvaluation
from remediation.orchestrator import OrchestratorAdapter


class ContainmentController:
    def __init__(self, orchestrator: OrchestratorAdapter) -> None:
        self.orchestrator = orchestrator

    def decide(self, incident: Incident, decision: ActionDecision, evaluation: IncidentEvaluation) -> ContainmentState:
        if evaluation.success:
            return ContainmentState(active=False, containment_mode="none", reason="No containment required")

        if incident.retry_count < decision.retry_budget:
            return ContainmentState(
                active=True,
                containment_mode="retry",
                next_action="retry",
                reason=f"Attempt {incident.retry_count + 1} of {decision.retry_budget}",
                notes=["Retry budget not exhausted"],
            )

        if decision.action == "start_service" and self.orchestrator.platform == "kubernetes":
            return ContainmentState(
                active=True,
                containment_mode="escalate",
                next_action="escalate_incident",
                escalated=True,
                manual_required=True,
                reason="Kubernetes workload did not become ready after bounded recovery attempts",
                notes=["Escalating instead of re-isolating a service that is already recovering"],
            )

        if "isolate_service" in decision.containment_actions:
            return ContainmentState(
                active=True,
                containment_mode="isolate",
                next_action="isolate_service",
                reason="Retries exhausted; isolating failing workload",
                notes=["Service will be quarantined by stopping the workload"],
            )

        if "reroute_service" in decision.containment_actions:
            alternatives = self.orchestrator.discover_healthy_alternatives(incident.root_cause_service)
            if alternatives:
                return ContainmentState(
                    active=True,
                    containment_mode="reroute",
                    next_action="reroute_service",
                    parameters={"alternative": alternatives[0], "alternatives": alternatives},
                    reason="Retries exhausted; rerouting to healthy alternative",
                )
            return ContainmentState(
                active=True,
                containment_mode="reroute",
                next_action="escalate_incident",
                escalated=True,
                manual_required=True,
                reason="Reroute requested but no healthy alternative exists",
                notes=["Best-effort reroute unavailable in the current Docker topology"],
            )

        return ContainmentState(
            active=True,
            containment_mode="escalate",
            next_action="escalate_incident",
            escalated=True,
            manual_required=True,
            reason="No safe automated action remains",
        )
