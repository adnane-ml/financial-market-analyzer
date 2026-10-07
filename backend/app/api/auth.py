from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.models import User
from app.db.session import get_db
from app.schemas.auth import Token, UserCreate, UserLogin

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["auth"])

def set_refresh_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,       # True en prod (HTTPS)
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/auth/refresh",
    )

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, response: Response, body: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(User).where(User.email == body.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    user = User(email=body.email, hashed_password=hash_password(body.password))
    db.add(user)
    await db.commit()
    refresh_token = create_refresh_token(body.email)
    set_refresh_cookie(response, refresh_token)
    return Token(access_token=create_access_token(body.email))

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, response: Response, body: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == body.email))
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    refresh_token = create_refresh_token(user.email)
    set_refresh_cookie(response, refresh_token)
    return Token(access_token=create_access_token(user.email))

@router.post("/refresh", response_model=Token)
async def refresh(response: Response, refresh_token: str = Cookie(default=None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token manquant")
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token invalide")
    new_refresh = create_refresh_token(payload["sub"])
    set_refresh_cookie(response, new_refresh)
    return Token(access_token=create_access_token(payload["sub"]))

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="refresh_token", path="/auth/refresh")
    return {"message": "Déconnecté"}