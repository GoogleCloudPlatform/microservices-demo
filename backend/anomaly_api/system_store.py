from __future__ import annotations

import json
import logging
import sqlite3
import threading
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional


def utcnow_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


class SQLiteSystemStore:
    SCHEMA_VERSION = 1

    def __init__(self, db_path: Path, max_logs: int = 10000, max_events: int = 5000) -> None:
        self.db_path = Path(db_path)
        self.max_logs = max_logs
        self.max_events = max_events
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.DatabaseError:
            backup = self.db_path.with_suffix(f".corrupt-{int(time.time())}.db")
            if self.db_path.exists():
                self.db_path.rename(backup)
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER NOT NULL
                )
                """
            )
            existing = conn.execute("SELECT version FROM schema_version LIMIT 1").fetchone()
            if existing is None:
                conn.execute("INSERT INTO schema_version (version) VALUES (?)", (self.SCHEMA_VERSION,))

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    service TEXT,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    payload_json TEXT NOT NULL DEFAULT '{}'
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    level TEXT NOT NULL,
                    logger TEXT NOT NULL,
                    message TEXT NOT NULL,
                    context_json TEXT NOT NULL DEFAULT '{}'
                )
                """
            )

    def add_event(
        self,
        *,
        event_type: str,
        category: str,
        severity: str,
        title: str,
        message: str,
        service: Optional[str] = None,
        status: str = "open",
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        created_at = utcnow_iso()
        row = {
            "created_at": created_at,
            "event_type": event_type,
            "category": category,
            "severity": severity,
            "service": service,
            "title": title,
            "message": message,
            "status": status,
            "payload": payload or {},
        }
        with self._lock:
            with self._connect() as conn:
                cur = conn.execute(
                    """
                    INSERT INTO system_events (
                        created_at, event_type, category, severity, service, title, message, status, payload_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        created_at,
                        event_type,
                        category,
                        severity,
                        service,
                        title,
                        message,
                        status,
                        json.dumps(payload or {}),
                    ),
                )
                row["id"] = cur.lastrowid
                self._prune_events(conn)
        return row

    def add_log(
        self,
        *,
        level: str,
        logger_name: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO system_logs (created_at, level, logger, message, context_json)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        utcnow_iso(),
                        level,
                        logger_name,
                        message,
                        json.dumps(context or {}),
                    ),
                )
                self._prune_logs(conn)

    def list_events(self, limit: int = 100, category: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM system_events
            {where_clause}
            ORDER BY created_at DESC, id DESC
            LIMIT ?
        """
        params: List[Any] = []
        where_clause = ""
        if category:
            where_clause = "WHERE category = ?"
            params.append(category)
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query.format(where_clause=where_clause), tuple(params)).fetchall()
        return [self._event_row_to_dict(row) for row in rows]

    def list_logs(self, limit: int = 200, level: Optional[str] = None, query: str = "") -> List[Dict[str, Any]]:
        where_clauses: List[str] = []
        params: List[Any] = []
        if level:
            where_clauses.append("level = ?")
            params.append(level.upper())
        if query:
            where_clauses.append("(message LIKE ? OR logger LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        sql = f"""
            SELECT * FROM system_logs
            {where_clause}
            ORDER BY created_at DESC, id DESC
            LIMIT ?
        """
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, tuple(params)).fetchall()
        return [self._log_row_to_dict(row) for row in rows]

    def summarize(self) -> Dict[str, Any]:
        with self._connect() as conn:
            latest_event = conn.execute(
                "SELECT * FROM system_events ORDER BY created_at DESC, id DESC LIMIT 1"
            ).fetchone()
            error_logs = conn.execute(
                """
                SELECT COUNT(*) AS count
                FROM system_logs
                WHERE level IN ('ERROR', 'CRITICAL')
                  AND julianday('now') - julianday(created_at) < (1.0 / 24.0)
                """
            ).fetchone()
        return {
            "latest_event": self._event_row_to_dict(latest_event) if latest_event else None,
            "recent_error_logs": int(error_logs["count"]) if error_logs else 0,
        }

    def build_report(self, *, event_limit: int = 120, log_limit: int = 200) -> Dict[str, Any]:
        events = self.list_events(limit=event_limit)
        logs = self.list_logs(limit=log_limit)
        severity_counts = Counter(item["severity"] for item in events)
        level_counts = Counter(
            "ERROR" if item["level"] in {"ERROR", "CRITICAL"} else item["level"]
            for item in logs
        )
        services = Counter(item["service"] for item in events if item.get("service"))
        open_events = [item for item in events if item.get("status") != "closed"]
        return {
            "generated_at": utcnow_iso(),
            "summary": {
                "event_count": len(events),
                "log_count": len(logs),
                "open_event_count": len(open_events),
                "severity_counts": dict(severity_counts),
                "log_level_counts": dict(level_counts),
                "services_with_activity": dict(services.most_common(12)),
            },
            "events": events,
            "logs": logs,
        }

    def render_markdown_report(self, *, event_limit: int = 120, log_limit: int = 200) -> str:
        report = self.build_report(event_limit=event_limit, log_limit=log_limit)
        summary = report["summary"]
        lines = [
            "# AEGIS System Activity Report",
            "",
            f"Generated at: {report['generated_at']}",
            "",
            "## Summary",
            "",
            f"- Events captured: {summary['event_count']}",
            f"- Log lines captured: {summary['log_count']}",
            f"- Open events: {summary['open_event_count']}",
            f"- Event severities: {json.dumps(summary['severity_counts'], sort_keys=True)}",
            f"- Log levels: {json.dumps(summary['log_level_counts'], sort_keys=True)}",
            "",
            "## Recent Event Timeline",
            "",
        ]
        for item in report["events"][:40]:
            lines.append(
                f"- {item['created_at']} | {item['severity'].upper()} | "
                f"{item.get('service') or 'platform'} | {item['title']} | {item['message']}"
            )
        lines.extend(["", "## Recent Backend Logs", ""])
        for item in report["logs"][:80]:
            lines.append(
                f"- {item['created_at']} | {item['level']} | {item['logger']} | {item['message']}"
            )
        return "\n".join(lines)

    def _prune_events(self, conn: sqlite3.Connection) -> None:
        if self.max_events > 0:
            conn.execute(
                """
                DELETE FROM system_events
                WHERE id IN (
                    SELECT id
                    FROM system_events
                    ORDER BY created_at DESC, id DESC
                    LIMIT -1 OFFSET ?
                )
                """,
                (self.max_events,),
            )

    def _prune_logs(self, conn: sqlite3.Connection) -> None:
        if self.max_logs > 0:
            conn.execute(
                """
                DELETE FROM system_logs
                WHERE id IN (
                    SELECT id
                    FROM system_logs
                    ORDER BY created_at DESC, id DESC
                    LIMIT -1 OFFSET ?
                )
                """,
                (self.max_logs,),
            )

    def _event_row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        item = dict(row)
        item["payload"] = json.loads(item.pop("payload_json", "{}"))
        return item

    def _log_row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        item = dict(row)
        item["context"] = json.loads(item.pop("context_json", "{}"))
        return item


class SQLiteLogHandler(logging.Handler):
    def __init__(self, store: SQLiteSystemStore) -> None:
        super().__init__()
        self.store = store
        self._local = threading.local()

    def emit(self, record: logging.LogRecord) -> None:
        if getattr(self._local, "active", False):
            return
        self._local.active = True
        try:
            message = record.getMessage()
            context: Dict[str, Any] = {}
            for key in ("service", "event_type", "incident_id"):
                value = getattr(record, key, None)
                if value is not None:
                    context[key] = value
            self.store.add_log(
                level=record.levelname,
                logger_name=record.name,
                message=message,
                context=context,
            )
        except Exception:
            pass
        finally:
            self._local.active = False
