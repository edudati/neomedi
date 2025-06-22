from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from neomediapi.auth.authenticated_user import AuthenticatedUser
from neomediapi.auth.dependencies import get_current_user
from neomediapi.domain.user.exeptions import UserAlreadyExistsError, UserNotFoundError
from neomediapi.infra.db.repositories.user_repository import UserRepository
from neomediapi.services.user_service import UserService
from neomediapi.enums.user_roles import UserRole
from neomediapi.domain.user.dtos.user_dto import (
    UserResponseDTO,
    UserCreateDTO,
)
from neomediapi.infra.db.session import get_db

router = APIRouter()


# ============================================
# POST / - Register user with Firebase Auth
# ============================================

@router.post("/", response_model=UserResponseDTO)
def register_user(
    body: UserCreateDTO,
    auth_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Registers a new user based on Firebase UID and additional fields.

    Requires a valid Firebase token in Authorization header.
    Payload Example:
    {
        "name": "Fulano",
        "email": "fulano@example.com",
        "role": "CLIENT"
    }
    """
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)

    try:
        created_user = user_service.create_user(
            user_data=body,
            firebase_uid=auth_user.uid,
        )
    except UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="User already exists")

    return UserResponseDTO.model_validate(created_user)