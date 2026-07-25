"""Authentication endpoints — login, refresh, me, logout."""

from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr
from loguru import logger

from app.core.auth import create_access_token, create_refresh_token, decode_token, verify_catalyst_token, get_current_user
from app.core.exceptions import AuthenticationError
from app.utils.response import ApiResponse

router = APIRouter()


class CatalystLoginRequest(BaseModel):
    catalyst_token: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login", response_model=ApiResponse[LoginResponse], summary="Login with Catalyst Auth token")
async def login(body: CatalystLoginRequest):
    """
    Exchange a Zoho Catalyst Auth access token for Prahari AI JWT tokens.

    The frontend should:
    1. Redirect user to Catalyst Auth login page
    2. Receive the Catalyst access_token on callback
    3. POST it here to receive a scoped JWT
    """
    # Validate with Catalyst
    try:
        user_info = await verify_catalyst_token(body.catalyst_token)
    except Exception as e:
        raise AuthenticationError(f"Catalyst token validation failed: {str(e)}")

    # In production: load user from DB by catalyst_user_id
    # For now, construct minimal payload
    catalyst_id = user_info.get("ZPUID") or user_info.get("user_id")
    email = user_info.get("Email") or user_info.get("email", "")
    name = user_info.get("Display_Name") or user_info.get("name", "")

    token_payload = {
        "sub": catalyst_id,
        "email": email,
        "full_name": name,
        "role": "IO",  # Will be loaded from DB in production
    }

    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token({"sub": catalyst_id})

    return ApiResponse.ok(
        data=LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={"id": catalyst_id, "email": email, "name": name},
        ),
        message="Login successful.",
    )


@router.post("/refresh", response_model=ApiResponse[dict], summary="Refresh JWT access token")
async def refresh_token(body: RefreshRequest):
    """Exchange a refresh token for a new access token."""
    payload = decode_token(body.refresh_token)
    new_access = create_access_token({"sub": payload["sub"]})
    return ApiResponse.ok(data={"access_token": new_access})


@router.get("/me", response_model=ApiResponse[dict], summary="Get current user profile")
async def get_me(current_user=Depends(get_current_user)):
    """Return the authenticated user's profile and role."""
    return ApiResponse.ok(data={
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "station_id": current_user.station_id,
        "district_id": current_user.district_id,
    })


@router.post("/logout", response_model=ApiResponse[dict], summary="Invalidate session")
async def logout(current_user=Depends(get_current_user)):
    """
    Logout endpoint — instructs the frontend to discard its tokens.
    In production, tokens can be invalidated via Catalyst Cache blocklist.
    """
    return ApiResponse.ok(data={}, message="Logged out successfully.")
