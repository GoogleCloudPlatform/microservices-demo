"""
Correlation Engine for Online Boutique microservices.

Analyzes anomaly scores across services, identifies root cause
using dependency graph traversal.
"""

from typing import Dict, List, Optional

# Service dependency graph for Online Boutique
# key: service, value: list of services it depends on (calls)
DEPENDENCY_GRAPH = {
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

# Reverse: upstream_of[s] = list of services that depend on s
def _build_reverse_graph():
    rev = {s: [] for s in DEPENDENCY_GRAPH}
    for svc, deps in DEPENDENCY_GRAPH.items():
        for dep in deps:
            if dep in rev:
                rev[dep].append(svc)
            else:
                rev[dep] = [svc]
    return rev


REVERSE_GRAPH = _build_reverse_graph()

ANOMALY_THRESHOLD = 0.6
HIGH_CONFIDENCE_THRESHOLD = 0.75

# Failure type heuristics based on which service is anomalous
FAILURE_TYPE_HINTS = {
    "redis-cart": "memory_leak",
    "cartservice": "memory_leak",
    "productcatalogservice": "cpu_starvation",
    "recommendationservice": "cpu_starvation",
    "checkoutservice": "network_latency",
    "paymentservice": "network_latency",
    "shippingservice": "network_latency",
    "emailservice": "network_latency",
    "currencyservice": "cpu_starvation",
    "adservice": "cpu_starvation",
    "frontend": "network_latency",
}


class CorrelationEngine:
    """
    Analyzes anomaly scores to find root cause in a microservice graph.
    """

    def analyze(self, anomaly_scores: Dict[str, float]) -> Dict:
        """
        Analyze anomaly scores and return root cause analysis.

        Args:
            anomaly_scores: dict mapping service_name -> score [0-1]

        Returns:
            {
                "root_cause": str | None,
                "confidence": float,
                "affected_services": list[str],
                "propagation_path": list[str],
                "failure_type": str,
            }
        """
        if not anomaly_scores:
            return self._no_anomaly()

        # Step 1: Find anomalous services (score > threshold)
        anomalous = {
            svc: score
            for svc, score in anomaly_scores.items()
            if score >= ANOMALY_THRESHOLD
        }

        if not anomalous:
            return self._no_anomaly()

        # Step 2: Find root cause
        # Root = anomalous service whose upstream dependencies are NOT anomalous
        # (i.e., it is the origin, not a victim of propagation)
        root_candidates = []
        for svc in anomalous:
            deps = DEPENDENCY_GRAPH.get(svc, [])
            anomalous_deps = [d for d in deps if d in anomalous]
            root_candidates.append((svc, anomalous_scores[svc], len(anomalous_deps)))

        # Sort: prefer services with fewer anomalous upstream dependencies
        # then by score descending
        root_candidates.sort(key=lambda x: (x[2], -x[1]))

        if not root_candidates:
            return self._no_anomaly()

        root_service, root_score, n_anomalous_deps = root_candidates[0]

        # Step 3: Calculate confidence
        # Reduce confidence if root has anomalous upstream deps (might be a victim)
        confidence = root_score * (1.0 - 0.1 * n_anomalous_deps)
        confidence = max(0.0, min(1.0, confidence))

        # Step 4: Trace propagation path from root to most affected downstream
        propagation_path = self._trace_propagation(root_service, anomalous)

        # Step 5: Determine failure type
        failure_type = FAILURE_TYPE_HINTS.get(root_service, "generic_anomaly")

        # Step 6: Find all affected services (root + downstream that are anomalous)
        affected = set(anomalous.keys())

        return {
            "root_cause": root_service,
            "confidence": round(confidence, 3),
            "affected_services": sorted(affected),
            "propagation_path": propagation_path,
            "failure_type": failure_type,
        }

    def _trace_propagation(
        self, root: str, anomalous: Dict[str, float]
    ) -> List[str]:
        """
        Trace how an anomaly in root propagates through the graph.
        Returns a list of services in propagation order.
        """
        path = [root]
        visited = {root}
        queue = [root]

        while queue:
            current = queue.pop(0)
            # Look at services that depend on current (downstream)
            dependents = REVERSE_GRAPH.get(current, [])
            for dep in dependents:
                if dep not in visited and dep in anomalous:
                    path.append(dep)
                    visited.add(dep)
                    queue.append(dep)

        return path

    def _no_anomaly(self) -> Dict:
        return {
            "root_cause": None,
            "confidence": 0.0,
            "affected_services": [],
            "propagation_path": [],
            "failure_type": "none",
        }

    def get_dependency_graph(self) -> Dict:
        return DEPENDENCY_GRAPH.copy()

    def get_service_list(self) -> List[str]:
        return list(DEPENDENCY_GRAPH.keys())


# Fix: reference anomaly_scores in analyze (use local var)
# Patch the analyze method to use correct variable name
_orig_analyze = CorrelationEngine.analyze


def _patched_analyze(self, anomaly_scores: Dict[str, float]) -> Dict:
    if not anomaly_scores:
        return self._no_anomaly()

    anomalous = {
        svc: score
        for svc, score in anomaly_scores.items()
        if score >= ANOMALY_THRESHOLD
    }

    if not anomalous:
        return self._no_anomaly()

    root_candidates = []
    for svc in anomalous:
        deps = DEPENDENCY_GRAPH.get(svc, [])
        anomalous_deps = [d for d in deps if d in anomalous]
        root_candidates.append((svc, anomalous[svc], len(anomalous_deps)))

    root_candidates.sort(key=lambda x: (x[2], -x[1]))

    if not root_candidates:
        return self._no_anomaly()

    root_service, root_score, n_anomalous_deps = root_candidates[0]

    confidence = root_score * (1.0 - 0.1 * n_anomalous_deps)
    confidence = max(0.0, min(1.0, confidence))

    propagation_path = self._trace_propagation(root_service, anomalous)
    failure_type = FAILURE_TYPE_HINTS.get(root_service, "generic_anomaly")
    affected = set(anomalous.keys())

    return {
        "root_cause": root_service,
        "confidence": round(confidence, 3),
        "affected_services": sorted(affected),
        "propagation_path": propagation_path,
        "failure_type": failure_type,
    }


CorrelationEngine.analyze = _patched_analyze


if __name__ == "__main__":
    engine = CorrelationEngine()

    # Test 1: No anomalies
    result = engine.analyze({"frontend": 0.3, "cartservice": 0.2})
    print("No anomalies:", result)

    # Test 2: Redis anomaly propagates to cartservice -> frontend
    result = engine.analyze({
        "redis-cart": 0.9,
        "cartservice": 0.75,
        "frontend": 0.65,
        "productcatalogservice": 0.2,
    })
    print("Redis anomaly:", result)

    # Test 3: Payment service anomaly
    result = engine.analyze({
        "paymentservice": 0.8,
        "checkoutservice": 0.7,
        "frontend": 0.65,
    })
    print("Payment anomaly:", result)
