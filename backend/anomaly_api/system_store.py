from __future__ import annotations

import json
import hashlib
import logging
import secrets
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
    SCHEMA_VERSION = 2

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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS demo_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    service TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    started_by TEXT NOT NULL,
                    attack_action TEXT NOT NULL,
                    fix_action TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    incident_id TEXT,
                    summary_text TEXT NOT NULL DEFAULT '',
                    summary_json TEXT NOT NULL DEFAULT '{}',
                    report_markdown TEXT NOT NULL DEFAULT '',
                    report_json TEXT NOT NULL DEFAULT '{}'
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    google_sub TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL,
                    name TEXT NOT NULL,
                    picture_url TEXT NOT NULL DEFAULT '',
                    verified_email INTEGER NOT NULL DEFAULT 0,
                    role TEXT NOT NULL DEFAULT 'viewer',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_login_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_sessions (
                    token_hash TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    user_agent TEXT NOT NULL DEFAULT '',
                    ip_address TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY(user_id) REFERENCES user_accounts(id)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_user_accounts_email ON user_accounts(email)"
            )
            conn.execute(
                "UPDATE schema_version SET version = ?",
                (self.SCHEMA_VERSION,),
            )
            self._prune_expired_sessions(conn)

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

    def list_events_since(
        self,
        since_iso: str,
        *,
        limit: int = 200,
        service: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        clauses = ["created_at >= ?"]
        params: List[Any] = [since_iso]
        if service:
            clauses.append("(service = ? OR service IS NULL)")
            params.append(service)
        if category:
            clauses.append("category = ?")
            params.append(category)
        params.append(limit)
        sql = f"""
            SELECT * FROM system_events
            WHERE {' AND '.join(clauses)}
            ORDER BY created_at DESC, id DESC
            LIMIT ?
        """
        with self._connect() as conn:
            rows = conn.execute(sql, tuple(params)).fetchall()
        return [self._event_row_to_dict(row) for row in rows]

    def list_logs_since(
        self,
        since_iso: str,
        *,
        limit: int = 300,
        query: str = "",
    ) -> List[Dict[str, Any]]:
        clauses = ["created_at >= ?"]
        params: List[Any] = [since_iso]
        if query:
            clauses.append("(message LIKE ? OR logger LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        params.append(limit)
        sql = f"""
            SELECT * FROM system_logs
            WHERE {' AND '.join(clauses)}
            ORDER BY created_at DESC, id DESC
            LIMIT ?
        """
        with self._connect() as conn:
            rows = conn.execute(sql, tuple(params)).fetchall()
        return [self._log_row_to_dict(row) for row in rows]

    def start_demo_run(
        self,
        *,
        service: str,
        platform: str,
        started_by: str,
        attack_action: str,
    ) -> Dict[str, Any]:
        created_at = utcnow_iso()
        row = {
            "created_at": created_at,
            "updated_at": created_at,
            "service": service,
            "platform": platform,
            "started_by": started_by,
            "attack_action": attack_action,
            "fix_action": "",
            "status": "running",
            "stage": "initiated",
            "incident_id": None,
            "summary_text": "",
            "summary_json": {},
            "report_markdown": "",
            "report_json": {},
        }
        with self._lock:
            with self._connect() as conn:
                cur = conn.execute(
                    """
                    INSERT INTO demo_runs (
                        created_at, updated_at, service, platform, started_by, attack_action,
                        fix_action, status, stage, incident_id, summary_text, summary_json,
                        report_markdown, report_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["created_at"],
                        row["updated_at"],
                        row["service"],
                        row["platform"],
                        row["started_by"],
                        row["attack_action"],
                        row["fix_action"],
                        row["status"],
                        row["stage"],
                        row["incident_id"],
                        row["summary_text"],
                        json.dumps(row["summary_json"]),
                        row["report_markdown"],
                        json.dumps(row["report_json"]),
                    ),
                )
                row["id"] = cur.lastrowid
        return row

    def update_demo_run(self, run_id: int, **fields: Any) -> Dict[str, Any]:
        allowed = {
            "updated_at",
            "fix_action",
            "status",
            "stage",
            "incident_id",
            "summary_text",
            "summary_json",
            "report_markdown",
            "report_json",
        }
        payload = {key: value for key, value in fields.items() if key in allowed}
        if not payload:
            demo = self.get_demo_run(run_id)
            if demo is None:
                raise KeyError(f"Demo run {run_id} not found")
            return demo
        payload["updated_at"] = utcnow_iso()
        assignments = []
        params: List[Any] = []
        for key, value in payload.items():
            assignments.append(f"{key} = ?")
            if key in {"summary_json", "report_json"}:
                params.append(json.dumps(value or {}))
            else:
                params.append(value)
        params.append(run_id)
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE demo_runs SET {', '.join(assignments)} WHERE id = ?",
                    tuple(params),
                )
        demo = self.get_demo_run(run_id)
        if demo is None:
            raise KeyError(f"Demo run {run_id} not found")
        return demo

    def get_demo_run(self, run_id: int) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM demo_runs WHERE id = ? LIMIT 1",
                (run_id,),
            ).fetchone()
        return self._demo_row_to_dict(row) if row else None

    def latest_demo_run(self) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM demo_runs ORDER BY created_at DESC, id DESC LIMIT 1"
            ).fetchone()
        return self._demo_row_to_dict(row) if row else None

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

    def upsert_user_account(
        self,
        *,
        google_sub: str,
        email: str,
        name: str,
        picture_url: str = "",
        verified_email: bool = False,
        role: str = "viewer",
    ) -> Dict[str, Any]:
        now = utcnow_iso()
        with self._lock:
            with self._connect() as conn:
                existing = conn.execute(
                    "SELECT id FROM user_accounts WHERE google_sub = ? LIMIT 1",
                    (google_sub,),
                ).fetchone()
                if existing:
                    conn.execute(
                        """
                        UPDATE user_accounts
                        SET email = ?, name = ?, picture_url = ?, verified_email = ?, role = ?, updated_at = ?, last_login_at = ?
                        WHERE google_sub = ?
                        """,
                        (
                            email,
                            name,
                            picture_url,
                            1 if verified_email else 0,
                            role,
                            now,
                            now,
                            google_sub,
                        ),
                    )
                    user_id = int(existing["id"])
                else:
                    cur = conn.execute(
                        """
                        INSERT INTO user_accounts (
                            google_sub, email, name, picture_url, verified_email, role,
                            created_at, updated_at, last_login_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            google_sub,
                            email,
                            name,
                            picture_url,
                            1 if verified_email else 0,
                            role,
                            now,
                            now,
                            now,
                        ),
                    )
                    user_id = int(cur.lastrowid)
                row = conn.execute(
                    "SELECT * FROM user_accounts WHERE id = ? LIMIT 1",
                    (user_id,),
                ).fetchone()
        return self._user_row_to_dict(row) if row else {}

    def create_user_session(
        self,
        *,
        user_id: int,
        ttl_seconds: int,
        user_agent: str = "",
        ip_address: str = "",
    ) -> Dict[str, Any]:
        created_at = utcnow_iso()
        expires_epoch = time.time() + max(ttl_seconds, 300)
        expires_at = datetime_from_epoch(expires_epoch)
        raw_token = secrets.token_urlsafe(32)
        token_hash = self._hash_session_token(raw_token)
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO user_sessions (
                        token_hash, user_id, created_at, updated_at, expires_at, user_agent, ip_address
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        token_hash,
                        user_id,
                        created_at,
                        created_at,
                        expires_at,
                        user_agent,
                        ip_address,
                    ),
                )
                row = conn.execute(
                    """
                    SELECT s.*, u.google_sub, u.email, u.name, u.picture_url, u.verified_email, u.role
                    FROM user_sessions s
                    JOIN user_accounts u ON u.id = s.user_id
                    WHERE s.token_hash = ?
                    LIMIT 1
                    """,
                    (token_hash,),
                ).fetchone()
        session = self._session_row_to_dict(row) if row else {}
        session["token"] = raw_token
        return session

    def get_user_session(self, raw_token: str) -> Optional[Dict[str, Any]]:
        if not raw_token:
            return None
        token_hash = self._hash_session_token(raw_token)
        now = utcnow_iso()
        with self._lock:
            with self._connect() as conn:
                row = conn.execute(
                    """
                    SELECT s.*, u.google_sub, u.email, u.name, u.picture_url, u.verified_email, u.role
                    FROM user_sessions s
                    JOIN user_accounts u ON u.id = s.user_id
                    WHERE s.token_hash = ?
                    LIMIT 1
                    """,
                    (token_hash,),
                ).fetchone()
                if row is None:
                    return None
                if row["expires_at"] <= now:
                    conn.execute("DELETE FROM user_sessions WHERE token_hash = ?", (token_hash,))
                    return None
                conn.execute(
                    "UPDATE user_sessions SET updated_at = ? WHERE token_hash = ?",
                    (now, token_hash),
                )
                refreshed = conn.execute(
                    """
                    SELECT s.*, u.google_sub, u.email, u.name, u.picture_url, u.verified_email, u.role
                    FROM user_sessions s
                    JOIN user_accounts u ON u.id = s.user_id
                    WHERE s.token_hash = ?
                    LIMIT 1
                    """,
                    (token_hash,),
                ).fetchone()
        return self._session_row_to_dict(refreshed) if refreshed else None

    def revoke_user_session(self, raw_token: str) -> None:
        if not raw_token:
            return
        token_hash = self._hash_session_token(raw_token)
        with self._lock:
            with self._connect() as conn:
                conn.execute("DELETE FROM user_sessions WHERE token_hash = ?", (token_hash,))

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

    def _prune_expired_sessions(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            "DELETE FROM user_sessions WHERE expires_at <= ?",
            (utcnow_iso(),),
        )

    def _event_row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        item = dict(row)
        item["payload"] = json.loads(item.pop("payload_json", "{}"))
        return item

    def _log_row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        item = dict(row)
        item["context"] = json.loads(item.pop("context_json", "{}"))
        return item

    def _demo_row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        item = dict(row)
        item["summary_json"] = json.loads(item.pop("summary_json", "{}"))
        item["report_json"] = json.loads(item.pop("report_json", "{}"))
        item["download_ready"] = bool(item.get("report_markdown") or item.get("report_json"))
        return item

    def _user_row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": int(row["id"]),
            "google_sub": row["google_sub"],
            "email": row["email"],
            "name": row["name"],
            "picture_url": row["picture_url"],
            "verified_email": bool(row["verified_email"]),
            "role": row["role"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "last_login_at": row["last_login_at"],
        }

    def _session_row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "user_id": int(row["user_id"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "expires_at": row["expires_at"],
            "user_agent": row["user_agent"],
            "ip_address": row["ip_address"],
            "user": {
                "google_sub": row["google_sub"],
                "email": row["email"],
                "name": row["name"],
                "picture_url": row["picture_url"],
                "verified_email": bool(row["verified_email"]),
                "role": row["role"],
            },
        }

    @staticmethod
    def _hash_session_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def datetime_from_epoch(epoch_seconds: float) -> str:
    from datetime import datetime, timezone

    return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).isoformat()


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
