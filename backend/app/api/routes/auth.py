from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from app.auth import COOKIE_NAME, create_session_token, require_auth
from shared.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

THIRTY_DAYS = 60 * 60 * 24 * 30


class LoginRequest(BaseModel):
    password: str


@router.post("/login")
def login(payload: LoginRequest, response: Response):
    if payload.password != settings.site_password:
        raise HTTPException(status_code=401, detail="incorrect password")
    response.set_cookie(
        key=COOKIE_NAME,
        value=create_session_token(),
        max_age=THIRTY_DAYS,
        httponly=True,
        samesite="lax",
    )
    return {"authenticated": True}


@router.get("/status")
def status(_: None = Depends(require_auth)):
    return {"authenticated": True}
