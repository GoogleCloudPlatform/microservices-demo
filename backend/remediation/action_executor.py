from __future__ import annotations

import logging
import time
from typing import List

from remediation.models import ActionDecision, ActionExecutionRecord, utcnow_iso
from remediation.orchestrator import OrchestratorAdapter

logger = logging.getLogger(__name__)


class ActionExecutor:
    def __init__(self, orchestrator: OrchestratorAdapter) -> None:
        self.orchestrator = orchestrator

    def execute(self, decision: ActionDecision) -> List[ActionExecutionRecord]:
        action = decision.action
        if action == "restart_dependency_chain":
            chain = decision.parameters.get("chain", [])
            records: List[ActionExecutionRecord] = []
            for target in chain:
                chained = ActionDecision(
                    action="restart_service",
                    target=target,
                    parameters={"reason": "dependency_chain"},
                    confidence=decision.confidence,
                    rationale=decision.rationale,
                    source=decision.source,
                )
                records.extend(self.execute(chained))
            return records

        if action == "noop":
            ts = utcnow_iso()
            return [
                ActionExecutionRecord(
                    action=action,
                    target=decision.target,
                    success=True,
                    started_at=ts,
                    finished_at=ts,
                    duration_s=0.0,
                    message="No action required",
                    details={"parameters": decision.parameters},
                )
            ]

        if action == "escalate_incident":
            ts = utcnow_iso()
            return [
                ActionExecutionRecord(
                    action=action,
                    target=decision.target,
                    success=True,
                    started_at=ts,
                    finished_at=ts,
                    duration_s=0.0,
                    message=decision.parameters.get("reason", "Escalated to operator"),
                    details={"parameters": decision.parameters},
                )
            ]

        return [self._execute_single(decision)]

    def _execute_single(self, decision: ActionDecision) -> ActionExecutionRecord:
        started = time.time()
        started_at = utcnow_iso()
        success = False
        message = ""
        details = {}
        error = ""

        try:
            action = decision.action
            target = decision.target

            if action == "restart_service":
                success, message, details = self.orchestrator.restart_service(target)
            elif action == "stop_service":
                success, message, details = self.orchestrator.stop_service(target)
            elif action == "start_service":
                success, message, details = self.orchestrator.start_service(target)
            elif action == "isolate_service":
                success, message, details = self.orchestrator.isolate_service(target)
            elif action == "reroute_service":
                alternatives = self.orchestrator.discover_healthy_alternatives(target)
                if alternatives:
                    success = True
                    message = f"Rerouted traffic to {alternatives[0]}"
                    details = {"alternative": alternatives[0], "alternatives": alternatives}
                else:
                    message = "No healthy alternative available for reroute"
                    details = {"alternatives": []}
            else:
                message = f"Unsupported action: {action}"
        except Exception as exc:
            error = str(exc)
            message = f"Execution failed: {exc}"
            logger.exception("Action execution failed")

        finished = time.time()
        return ActionExecutionRecord(
            action=decision.action,
            target=decision.target,
            success=success,
            started_at=started_at,
            finished_at=utcnow_iso(),
            duration_s=round(finished - started, 3),
            message=message,
            error=error,
            details=details,
        )
