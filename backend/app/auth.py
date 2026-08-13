"""Shared-password site gate.

Not a real user-accounts system -- one household password (SITE_PASSWORD),
verified via a signed cookie. The cookie's value is derived from the current
password, so changing SITE_PASSWORD invalidates every existing session.
"""

import hashlib
import hmac

from fastapi import Cookie, HTTPException

from shared.config import settings

COOKIE_NAME = "session"
_MARKER = b"authenticated"


def _signing_key() -> bytes:
    return hashlib.sha256(settings.site_password.encode()).digest()


def create_session_token() -> str:
    return hmac.new(_signing_key(), _MARKER, hashlib.sha256).hexdigest()


def verify_session_token(token: str | None) -> bool:
    if not token:
        return False
    return hmac.compare_digest(token, create_session_token())


def require_auth(session: str | None = Cookie(default=None)) -> None:
    if not verify_session_token(session):
        raise HTTPException(status_code=401, detail="not authenticated")
