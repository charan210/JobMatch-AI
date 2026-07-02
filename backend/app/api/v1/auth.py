from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_auth_service
from app.db.database import get_db
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    """
    Register a new user.
    """
    # Using register() as specified in the prompt since there's no existing alternative.
    user = await auth_service.register(db, request)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    request: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """
    Authenticate user and return access and refresh tokens.
    """
    user = await auth_service.authenticate_user(db, request.email, request.password)
    access_token = auth_service.create_access_token_for_user(user)
    refresh_token = auth_service.create_refresh_token_for_user(user)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh(
    request: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """
    Refresh access token using a valid refresh token.
    """
    access_token = await auth_service.refresh_access_token(db, request.refresh_token)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,
    )
