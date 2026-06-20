"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.api.deps import require_auth
from rudra.auth.service import AuthService
from rudra.core.database import get_db

router = APIRouter()


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=256)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    display_name: str | None = None


class UserResponse(BaseModel):
    user_id: str
    username: str
    display_name: str | None = None
    is_owner: bool = False


@router.post("/auth/login", response_model=LoginResponse)
async def login(request: Request, body: LoginRequest, db: AsyncSession = Depends(get_db)):
    auth = AuthService(db)
    ip = request.client.host if request.client else None
    result = await auth.login(body.username, body.password, ip_address=ip)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token, user = result
    return LoginResponse(
        access_token=token,
        user_id=auth.user_id(user),
        username=user.username,
        display_name=user.display_name,
    )


@router.post("/auth/logout")
async def logout(
    request: Request,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    auth = AuthService(db)
    ip = request.client.host if request.client else None
    await auth.logout(user_id, ip_address=ip)
    return {"status": "ok"}


@router.get("/auth/me", response_model=UserResponse)
async def me(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    auth = AuthService(db)
    user = await auth.get_by_external_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        user_id=user.external_id,
        username=user.username,
        display_name=user.display_name,
        is_owner=user.is_owner,
    )
