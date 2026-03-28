from __future__ import annotations

import secrets

from fastapi import Header, HTTPException

from anomaly_api.settings import Settings


def require_operator_token(settings: Settings, x_aegis_token: str = Header(default="")) -> None:
    if not settings.auth_enabled:
        return
    if not settings.api_token:
        raise HTTPException(status_code=503, detail="Operator API token is not configured")
    if not secrets.compare_digest(x_aegis_token or "", settings.api_token):
        raise HTTPException(status_code=401, detail="Invalid operator token")


def is_operator_user(settings: Settings, user: dict | None) -> bool:
    if user is None:
        return False
    if not settings.operator_emails:
        return True
    email = (user.get("email") or "").strip().lower()
    allowed = {item.strip().lower() for item in settings.operator_emails if item.strip()}
    return bool(email and email in allowed)
