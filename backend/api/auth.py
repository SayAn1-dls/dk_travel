"""Authentication API routes."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from backend.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    user_id: str
    token: str
    expires_at: str


@router.post("/register", status_code=201)
async def register(request: RegisterRequest):
    """Register a new user account."""
    try:
        user = await auth_service.register(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            phone=request.phone,
        )
        return {"message": "Registration successful", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(request: LoginRequest):
    """Log in and receive an auth token."""
    result = await auth_service.login(request.email, request.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(**result)


@router.post("/logout")
async def logout(token: str):
    """Invalidate the current session."""
    success = await auth_service.logout(token)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"message": "Logged out successfully"}
