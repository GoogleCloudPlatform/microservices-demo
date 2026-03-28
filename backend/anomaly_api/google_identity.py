from __future__ import annotations

from typing import Any, Dict


GOOGLE_ISSUERS = {
    "accounts.google.com",
    "https://accounts.google.com",
}


def verify_google_credential(credential: str, client_id: str) -> Dict[str, Any]:
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token

    request = google_requests.Request()
    claims = id_token.verify_oauth2_token(
        credential,
        request,
        client_id,
        clock_skew_in_seconds=30,
    )
    issuer = claims.get("iss")
    if issuer not in GOOGLE_ISSUERS:
        raise ValueError(f"Unexpected Google issuer: {issuer}")
    return claims
