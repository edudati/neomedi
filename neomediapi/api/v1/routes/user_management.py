from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from neomediapi.infra.db.session import get_db
from neomediapi.auth.dependencies import get_current_user
from neomediapi.auth.authenticated_user import AuthenticatedUser
from neomediapi.auth.permissions import PermissionManager
from neomediapi.services.user_service import UserService
from neomediapi.domain.user.dtos.user_dto import UserUpdate, UserResponse
from neomediapi.domain.user.exceptions import UserNotFoundError
from neomediapi.enums.user_profiles import UserProfile

router = APIRouter(prefix="/user-management", tags=["user-management"])

@router.get("/available-features", response_model=List[str])
def get_available_features(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get available features for current user based on profile"""
    return PermissionManager.get_available_features(current_user)

@router.get("/profile-hierarchy", response_model=dict)
def get_profile_hierarchy():
    """Get profile hierarchy information"""
    return {
        "hierarchy": {
            "SUPER": 7,
            "ADMIN": 6,
            "MANAGER": 5,
            "PROFESSIONAL": 4,
            "ASSISTANT": 3,
            "CLIENT": 2,
            "TUTOR": 1
        },
        "permissions": {
            "SUPER": ["super_admin", "company_management", "nominate_managers", "nominate_professionals", "manager_features", "professional_features"],
            "ADMIN": ["company_management", "nominate_managers", "nominate_professionals", "manager_features", "professional_features"],
            "MANAGER": ["nominate_professionals", "manager_features", "professional_features"],
            "PROFESSIONAL": ["professional_features"],
            "ASSISTANT": ["assistant_features"],
            "CLIENT": ["client_features"],
            "TUTOR": ["tutor_features"]
        }
    }

@router.put("/users/{user_id}/profile", response_model=UserResponse)
def update_user_profile(
    user_id: int,
    new_profile: UserProfile,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile (with permission validation)"""
    user_service = UserService(db)
    
    # Check if current user can change profiles
    if not PermissionManager.can_nominate_managers(current_user) and new_profile == UserProfile.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and super users can nominate managers"
        )
    
    if not PermissionManager.can_nominate_professionals(current_user) and new_profile == UserProfile.PROFESSIONAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin, super, and manager users can nominate professionals"
        )
    
    # Validate profile transition
    try:
        target_user = user_service.get_user_by_id(user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not UserProfile.validate_profile_transition(target_user.profile, new_profile):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot change profile from {target_user.profile} to {new_profile}"
            )
        
        # Update profile
        user_update = UserUpdate(profile=new_profile)
        updated_user = user_service.update_user(user_id, user_update, current_user.id)
        return updated_user
        
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/users/{user_id}/allowed-profiles", response_model=List[str])
def get_allowed_profile_changes(
    user_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get allowed profile changes for a specific user"""
    user_service = UserService(db)
    
    try:
        target_user = user_service.get_user_by_id(user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        allowed_profiles = UserProfile.get_allowed_profile_changes(target_user.profile)
        return [profile.value for profile in allowed_profiles]
        
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/permissions/check", response_model=dict)
def check_user_permissions(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Check current user permissions"""
    return {
        "user_id": current_user.id,
        "profile": current_user.profile.value if current_user.profile else None,
        "permissions": {
            "can_manage_company": PermissionManager.can_manage_company(current_user),
            "can_nominate_managers": PermissionManager.can_nominate_managers(current_user),
            "can_nominate_professionals": PermissionManager.can_nominate_professionals(current_user),
            "can_access_professional_features": PermissionManager.can_access_professional_features(current_user),
            "can_access_manager_features": PermissionManager.can_access_manager_features(current_user),
            "can_access_admin_features": PermissionManager.can_access_admin_features(current_user),
        },
        "available_features": PermissionManager.get_available_features(current_user)
    } 