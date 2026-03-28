from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from remediation.models import ActionDecision, ActionProposal, Incident, WorkloadState

DEPENDENCY_GRAPH: Dict[str, List[str]] = {
    "frontend": [
        "productcatalogservice",
        "cartservice",
        "recommendationservice",
        "currencyservice",
        "checkoutservice",
        "shippingservice",
        "adservice",
    ],
    "checkoutservice": [
        "cartservice",
        "emailservice",
        "paymentservice",
        "productcatalogservice",
        "shippingservice",
        "currencyservice",
    ],
    "productcatalogservice": [],
    "cartservice": ["redis-cart"],
    "recommendationservice": ["productcatalogservice"],
    "paymentservice": [],
    "shippingservice": [],
    "emailservice": [],
    "currencyservice": [],
    "adservice": [],
    "redis-cart": [],
}

CRITICAL_SHARED_SERVICES = {"redis-cart", "productcatalogservice", "currencyservice"}


@dataclass
class ActionPolicy:
    default_action: str
    allowed_actions: List[str]
    retry_budget: int
    evaluation_window_s: float = 2.0
    backoff_s: float = 1.0
    containment_actions: List[str] = field(default_factory=lambda: ["retry", "isolate_service", "escalate_incident"])
    manual_only: bool = False


DEFAULT_POLICIES: Dict[str, ActionPolicy] = {
    "service_unhealthy": ActionPolicy(
        default_action="restart_service",
        allowed_actions=["restart_service", "start_service", "isolate_service", "escalate_incident"],
        retry_budget=2,
        evaluation_window_s=2.0,
    ),
    "memory_leak": ActionPolicy(
        default_action="restart_service",
        allowed_actions=["restart_service", "isolate_service", "escalate_incident"],
        retry_budget=2,
        evaluation_window_s=2.0,
        backoff_s=1.5,
    ),
    "cpu_starvation": ActionPolicy(
        default_action="restart_service",
        allowed_actions=["restart_service", "isolate_service", "escalate_incident"],
        retry_budget=1,
        evaluation_window_s=2.0,
    ),
    "network_latency": ActionPolicy(
        default_action="restart_dependency_chain",
        allowed_actions=["restart_dependency_chain", "restart_service", "reroute_service", "isolate_service", "escalate_incident"],
        retry_budget=1,
        evaluation_window_s=2.0,
    ),
    "dependency_failure": ActionPolicy(
        default_action="restart_dependency_chain",
        allowed_actions=["restart_dependency_chain", "restart_service", "isolate_service", "escalate_incident"],
        retry_budget=1,
        evaluation_window_s=2.0,
    ),
    "log_exception_storm": ActionPolicy(
        default_action="restart_service",
        allowed_actions=["restart_service", "isolate_service", "escalate_incident"],
        retry_budget=1,
        evaluation_window_s=2.0,
    ),
    "generic_anomaly": ActionPolicy(
        default_action="restart_service",
        allowed_actions=["restart_service", "isolate_service", "escalate_incident"],
        retry_budget=1,
        evaluation_window_s=2.0,
    ),
    "none": ActionPolicy(
        default_action="noop",
        allowed_actions=["noop"],
        retry_budget=0,
        evaluation_window_s=0.0,
        containment_actions=[],
    ),
}


class ActionPolicyEngine:
    def __init__(self, dependency_graph: Optional[Dict[str, List[str]]] = None) -> None:
        self.dependency_graph = dependency_graph or DEPENDENCY_GRAPH

    def build_decision(
        self,
        incident: Incident,
        runtime_state: WorkloadState,
        similar_incidents: Optional[List[Dict]] = None,
        proposal: Optional[ActionProposal] = None,
    ) -> ActionDecision:
        failure_type = self._normalize_failure_type(incident, runtime_state)
        incident.failure_type = failure_type
        policy = DEFAULT_POLICIES.get(failure_type, DEFAULT_POLICIES["generic_anomaly"])

        proposed_action = self._pick_action(policy, incident, runtime_state, similar_incidents or [], proposal)
        target = proposal.target if proposal and proposal.target else incident.root_cause_service
        rationale_parts = [
            f"policy:{failure_type}",
            runtime_state.status,
        ]

        parameters: Dict[str, object] = {}
        if proposed_action == "restart_dependency_chain":
            chain = self.dependency_graph.get(target, [])
            chain = [svc for svc in chain if svc] + [target]
            parameters["chain"] = chain
            rationale_parts.append(f"chain:{'->'.join(chain)}")

        if proposed_action == "start_service" and runtime_state.exists:
            rationale_parts.append("workload_exists_but_is_not_running")
        if runtime_state.oom_killed:
            rationale_parts.append("detected_oom_killed")

        retry_budget = policy.retry_budget
        containment_actions = list(policy.containment_actions)

        if target in CRITICAL_SHARED_SERVICES:
            retry_budget = min(retry_budget, 1)
            if "escalate_incident" not in containment_actions:
                containment_actions.append("escalate_incident")
            rationale_parts.append("critical_shared_service")

        decision = ActionDecision(
            action=proposed_action,
            target=target,
            parameters=parameters,
            confidence=proposal.confidence if proposal else 0.72,
            rationale="; ".join(rationale_parts + ([proposal.rationale] if proposal and proposal.rationale else [])),
            source=proposal.source if proposal else "rule",
            retry_budget=retry_budget,
            evaluation_window_s=policy.evaluation_window_s,
            backoff_s=policy.backoff_s,
            allowed_actions=policy.allowed_actions,
            containment_actions=containment_actions,
            manual_only=policy.manual_only,
        )
        return decision

    def _normalize_failure_type(self, incident: Incident, runtime_state: WorkloadState) -> str:
        failure_type = incident.failure_type or "generic_anomaly"
        flags = incident.evidence.get("feature_flags") or []
        if not runtime_state.exists or runtime_state.status in {"not_found", "exited", "dead"}:
            return "service_unhealthy"
        if runtime_state.oom_killed or "memory_high" in flags or failure_type in {"oom_killed", "memory_pressure"}:
            return "memory_leak"
        if "cpu_spike" in flags or "cpu_trending_up" in flags:
            return "cpu_starvation"
        if "exceptions_detected" in flags or "error_rate_high" in flags:
            return "log_exception_storm"
        if len(incident.affected_services) > 1 and incident.root_cause_service in CRITICAL_SHARED_SERVICES:
            return "dependency_failure"
        if failure_type in DEFAULT_POLICIES:
            return failure_type
        return "generic_anomaly"

    def _pick_action(
        self,
        policy: ActionPolicy,
        incident: Incident,
        runtime_state: WorkloadState,
        similar_incidents: List[Dict],
        proposal: Optional[ActionProposal],
    ) -> str:
        if proposal and proposal.proposed_action in policy.allowed_actions:
            return proposal.proposed_action

        if proposal and proposal.proposed_action not in policy.allowed_actions:
            # Unsupported AI suggestion falls back to rules.
            pass

        if similar_incidents:
            for match in similar_incidents:
                action = match.get("selected_action")
                if action in policy.allowed_actions and match.get("outcome") in {"resolved", "contained"}:
                    return action

        if policy.default_action == "restart_service" and not runtime_state.running and runtime_state.exists:
            if "start_service" in policy.allowed_actions:
                return "start_service"

        return policy.default_action
