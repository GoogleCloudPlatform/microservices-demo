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
