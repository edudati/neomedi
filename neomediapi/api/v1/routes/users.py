from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from neomediapi.auth.authenticated_user import AuthenticatedUser
from neomediapi.auth.dependencies import get_current_user
from neomediapi.domain.user.exeptions import UserAlreadyExistsError, UserNotFoundError
from neomediapi.infra.db.repositories.user_repository import UserRepository
from neomediapi.services.user_service import UserService
from neomediapi.enums.user_roles import UserRole
from neomediapi.domain.user.dtos.user_dto import (
    UserResponseDTO,
    UserCreateDTO,
    UserProfileCreateDTO,
    UserProfileUpdateDTO,
    UserProfileResponseDTO,
    UserSimpleResponseDTO,
    UserListResponseDTO
)
from neomediapi.domain.user.exceptions import (
    UserValidationError,
)
from neomediapi.enums.document_types import DocumentType
from neomediapi.enums.gender_types import Gender
from neomediapi.infra.db.session import get_db

router = APIRouter()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get user service"""
    user_repository = UserRepository(db)
    return UserService(user_repository)

@router.post("/", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreateDTO,
    user_service: UserService = Depends(get_user_service)
):
    """Create a new user for authentication"""
    try:
        # This would typically get firebase_uid from the authenticated request
        # For now, we'll use a placeholder
        firebase_uid = "placeholder_firebase_uid"
        return user_service.create_user(user_data, firebase_uid)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except UserValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{user_id}", response_model=UserResponseDTO)
def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID (for authentication compatibility)"""
    try:
        return user_service.get_user_by_id(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/{user_id}/profile", response_model=UserProfileResponseDTO, status_code=status.HTTP_201_CREATED)
def create_user_profile(
    user_id: int,
    profile_data: UserProfileCreateDTO,
    user_service: UserService = Depends(get_user_service)
):
    """Create complete user profile"""
    try:
        return user_service.create_user_profile(user_id, profile_data)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except UserValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{user_id}/profile", response_model=UserProfileResponseDTO)
def get_user_profile(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Get complete user profile"""
    try:
        return user_service.get_user_profile(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{user_id}/profile", response_model=UserProfileResponseDTO)
def update_user_profile(
    user_id: int,
    profile_data: UserProfileUpdateDTO,
    user_service: UserService = Depends(get_user_service)
):
    """Update user profile"""
    try:
        return user_service.update_user_profile(user_id, profile_data)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except UserValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=UserListResponseDTO)
def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    user_service: UserService = Depends(get_user_service)
):
    """Get all active users with pagination"""
    return user_service.get_all_users(skip, limit)

@router.get("/search/", response_model=UserListResponseDTO)
def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    user_service: UserService = Depends(get_user_service)
):
    """Search users by name, email, or document ID"""
    return user_service.search_users(q, skip, limit)

@router.get("/role/{role}", response_model=UserListResponseDTO)
def get_users_by_role(
    role: UserRole,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    user_service: UserService = Depends(get_user_service)
):
    """Get users by role"""
    return user_service.get_users_by_role(role, skip, limit)

@router.get("/document-type/{document_type}", response_model=List[UserSimpleResponseDTO])
def get_users_by_document_type(
    document_type: DocumentType,
    user_service: UserService = Depends(get_user_service)
):
    """Get users by document type"""
    return user_service.get_users_by_document_type(document_type)

@router.get("/gender/{gender}", response_model=List[UserSimpleResponseDTO])
def get_users_by_gender(
    gender: Gender,
    user_service: UserService = Depends(get_user_service)
):
    """Get users by gender"""
    return user_service.get_users_by_gender(gender)

@router.get("/complete-profiles/", response_model=UserListResponseDTO)
def get_users_with_complete_profile(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    user_service: UserService = Depends(get_user_service)
):
    """Get users with complete profile"""
    return user_service.get_users_with_complete_profile(skip, limit)

@router.get("/incomplete-profiles/", response_model=UserListResponseDTO)
def get_users_with_incomplete_profile(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    user_service: UserService = Depends(get_user_service)
):
    """Get users with incomplete profile"""
    return user_service.get_users_with_incomplete_profile(skip, limit)

@router.get("/address/city/{city}", response_model=List[UserSimpleResponseDTO])
def get_users_by_address_city(
    city: str,
    user_service: UserService = Depends(get_user_service)
):
    """Get users by address city"""
    return user_service.get_users_by_address_city(city)

@router.get("/address/state/{state}", response_model=List[UserSimpleResponseDTO])
def get_users_by_address_state(
    state: str,
    user_service: UserService = Depends(get_user_service)
):
    """Get users by address state"""
    return user_service.get_users_by_address_state(state)

@router.get("/with-address/", response_model=List[UserSimpleResponseDTO])
def get_users_with_address(
    user_service: UserService = Depends(get_user_service)
):
    """Get users that have an address"""
    return user_service.get_users_with_address()

@router.get("/without-address/", response_model=List[UserSimpleResponseDTO])
def get_users_without_address(
    user_service: UserService = Depends(get_user_service)
):
    """Get users that don't have an address"""
    return user_service.get_users_without_address()

@router.patch("/{user_id}/deactivate", status_code=status.HTTP_200_OK)
def deactivate_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Deactivate user"""
    try:
        user_service.deactivate_user(user_id)
        return {"message": "User deactivated successfully"}
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.patch("/{user_id}/activate", status_code=status.HTTP_200_OK)
def activate_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Activate user"""
    try:
        user_service.activate_user(user_id)
        return {"message": "User activated successfully"}
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Soft delete user"""
    try:
        user_service.soft_delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.patch("/{user_id}/restore", status_code=status.HTTP_200_OK)
def restore_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Restore soft deleted user"""
    try:
        user_service.restore_user(user_id)
        return {"message": "User restored successfully"}
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete("/{user_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Hard delete user (permanent)"""
    try:
        user_service.hard_delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/statistics/")
def get_user_statistics(
    user_service: UserService = Depends(get_user_service)
):
    """Get user statistics"""
    return user_service.get_user_statistics()
