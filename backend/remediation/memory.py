from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

from remediation.models import MemoryRecord


class IncidentMemoryStore:
    def save(self, record: MemoryRecord) -> None:
        raise NotImplementedError

    def find_similar(
        self,
        service: str,
        failure_type: str,
        feature_flags: Optional[List[str]] = None,
        metric_signature: Optional[Dict[str, float]] = None,
        evidence_summary: str = "",
        limit: int = 5,
    ) -> List[Dict]:
        raise NotImplementedError


class SQLiteIncidentMemoryStore(IncidentMemoryStore):
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS incident_memory (
                    incident_id TEXT PRIMARY KEY,
                    service TEXT NOT NULL,
                    failure_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    feature_flags_json TEXT NOT NULL,
                    evidence_summary TEXT NOT NULL,
                    metric_signature_json TEXT NOT NULL,
                    selected_action TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    recurrence_count INTEGER NOT NULL DEFAULT 0,
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                )
                """
            )
            try:
                conn.execute(
                    """
                    CREATE VIRTUAL TABLE IF NOT EXISTS incident_memory_fts
                    USING fts5(
                        incident_id UNINDEXED,
                        evidence_summary,
                        notes,
                        feature_flags
                    )
                    """
                )
            except sqlite3.OperationalError:
                # FTS5 is optional on some sqlite builds; hybrid retrieval still works.
                pass

    def save(self, record: MemoryRecord) -> None:
        row = record.to_dict()
        feature_flags = row.get("feature_flags", [])
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO incident_memory (
                    incident_id, service, failure_type, severity,
                    feature_flags_json, evidence_summary, metric_signature_json,
                    selected_action, outcome, recurrence_count, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["incident_id"],
                    row["service"],
                    row["failure_type"],
                    row["severity"],
                    json.dumps(feature_flags),
                    row["evidence_summary"],
                    json.dumps(row.get("metric_signature", {})),
                    row["selected_action"],
                    row["outcome"],
                    row["recurrence_count"],
                    row["notes"],
                    row["created_at"],
                ),
            )
            try:
                conn.execute("DELETE FROM incident_memory_fts WHERE incident_id = ?", (row["incident_id"],))
                conn.execute(
                    """
                    INSERT INTO incident_memory_fts (incident_id, evidence_summary, notes, feature_flags)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        row["incident_id"],
                        row["evidence_summary"],
                        row["notes"],
                        " ".join(feature_flags),
                    ),
                )
            except sqlite3.OperationalError:
                pass

    def list_recent(self, limit: int = 20) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM incident_memory
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def find_similar(
        self,
        service: str,
        failure_type: str,
        feature_flags: Optional[List[str]] = None,
        metric_signature: Optional[Dict[str, float]] = None,
        evidence_summary: str = "",
        limit: int = 5,
    ) -> List[Dict]:
        feature_flags = feature_flags or []
        metric_signature = metric_signature or {}
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM incident_memory
                ORDER BY created_at DESC
                LIMIT 200
                """
            ).fetchall()

        scored = []
        for row in rows:
            item = self._row_to_dict(row)
            score = self._hybrid_score(item, service, failure_type, feature_flags, metric_signature, evidence_summary)
            item["similarity_score"] = round(score, 3)
            scored.append(item)

        scored.sort(key=lambda item: item["similarity_score"], reverse=True)
        return scored[:limit]

    def _hybrid_score(
        self,
        item: Dict,
        service: str,
        failure_type: str,
        feature_flags: List[str],
        metric_signature: Dict[str, float],
        evidence_summary: str,
    ) -> float:
        score = 0.0
        if item["service"] == service:
            score += 4.0
        if item["failure_type"] == failure_type:
            score += 4.0

        stored_flags = set(item.get("feature_flags", []))
        incoming_flags = set(feature_flags)
        if stored_flags or incoming_flags:
            intersection = len(stored_flags & incoming_flags)
            union = len(stored_flags | incoming_flags) or 1
            score += 3.0 * (intersection / union)

        stored_metrics = item.get("metric_signature", {})
        if stored_metrics and metric_signature:
            distance = 0.0
            dims = 0
            for key in set(stored_metrics) | set(metric_signature):
                dims += 1
                distance += abs(float(stored_metrics.get(key, 0.0)) - float(metric_signature.get(key, 0.0)))
            score += max(0.0, 3.0 - (distance / max(dims, 1)))

        evidence_text = f"{item.get('evidence_summary', '')} {item.get('notes', '')}".lower()
        for token in evidence_summary.lower().split():
            if token and token in evidence_text:
                score += 0.2

        return score

    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        item = dict(row)
        item["feature_flags"] = json.loads(item.pop("feature_flags_json", "[]"))
        item["metric_signature"] = json.loads(item.pop("metric_signature_json", "{}"))
        return item
