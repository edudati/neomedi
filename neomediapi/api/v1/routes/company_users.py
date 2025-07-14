from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from neomediapi.infra.db.session import get_db
from neomediapi.auth.dependencies import get_current_user
from neomediapi.auth.authenticated_user import AuthenticatedUser
from neomediapi.auth.permissions import PermissionManager
from neomediapi.services.company_users_service import CompanyUsersService
from neomediapi.domain.company.dtos.company_users_dto import (
    CompanyUsersList,
    CompanyUsersSummary,
    CompanyManager,
    CompanyProfessional,
    CompanyClient,
    AssignProfessionalRequest,
    UnassignProfessionalRequest
)
from neomediapi.domain.company.exceptions import (
    CompanyNotFoundError,
    UserNotInCompanyError,
    ProfessionalNotActiveError,
    ClientAlreadyAssignedError,
    ClientNotAssignedError,
    InvalidUserProfileError
)
from neomediapi.enums.user_profiles import UserProfile

router = APIRouter(prefix="/company-users", tags=["company-users"])

def _validate_company_access(current_user: AuthenticatedUser, company_id: int) -> None:
    """Validate if user has access to company"""
    # Super users can access any company
    if current_user.profile == UserProfile.SUPER:
        return
    
    # Admin users can access their own company
    if current_user.profile == UserProfile.ADMIN:
        # TODO: Check if user's company_id matches company_id
        return
    
    # Manager and Professional users can access their company
    if current_user.profile in [UserProfile.MANAGER, UserProfile.PROFESSIONAL]:
        # TODO: Check if user's company_id matches company_id
        return
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied to company"
    )

@router.get("/{company_id}/summary", response_model=CompanyUsersSummary)
def get_company_users_summary(
    company_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary of users in a company"""
    _validate_company_access(current_user, company_id)
    
    company_users_service = CompanyUsersService(db)
    
    try:
        summary = company_users_service.get_company_users_summary(company_id, current_user.id)
        return summary
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/{company_id}/managers", response_model=List[CompanyManager])
def get_company_managers(
    company_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get managers in a company"""
    _validate_company_access(current_user, company_id)
    
    company_users_service = CompanyUsersService(db)
    
    try:
        managers = company_users_service.get_company_managers(company_id, current_user.id)
        return managers
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/{company_id}/professionals", response_model=List[CompanyProfessional])
def get_company_professionals(
    company_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get professionals in a company"""
    _validate_company_access(current_user, company_id)
    
    company_users_service = CompanyUsersService(db)
    
    try:
        professionals = company_users_service.get_company_professionals(company_id, current_user.id)
        return professionals
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/{company_id}/clients", response_model=List[CompanyClient])
def get_company_clients(
    company_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get clients in a company with their assigned professionals"""
    _validate_company_access(current_user, company_id)
    
    company_users_service = CompanyUsersService(db)
    
    try:
        clients = company_users_service.get_company_clients(company_id, current_user.id)
        return clients
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/{company_id}/users", response_model=CompanyUsersList)
def get_company_users_list(
    company_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete list of users in a company"""
    _validate_company_access(current_user, company_id)
    
    company_users_service = CompanyUsersService(db)
    
    try:
        users_list = company_users_service.get_company_users_list(company_id, current_user.id)
        return users_list
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/{company_id}/assign-professional", response_model=CompanyClient)
def assign_professional_to_client(
    company_id: int,
    request: AssignProfessionalRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign a professional to a client"""
    _validate_company_access(current_user, company_id)
    
    # Only managers and admins can assign professionals
    if not PermissionManager.can_nominate_professionals(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers and admins can assign professionals"
        )
    
    company_users_service = CompanyUsersService(db)
    
    try:
        client = company_users_service.assign_professional_to_client(
            company_id, request, current_user.id
        )
        return client
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except UserNotInCompanyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ProfessionalNotActiveError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ClientAlreadyAssignedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except InvalidUserProfileError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{company_id}/unassign-professional", response_model=CompanyClient)
def unassign_professional_from_client(
    company_id: int,
    request: UnassignProfessionalRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unassign a professional from a client"""
    _validate_company_access(current_user, company_id)
    
    # Only managers and admins can unassign professionals
    if not PermissionManager.can_nominate_professionals(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers and admins can unassign professionals"
        )
    
    company_users_service = CompanyUsersService(db)
    
    try:
        client = company_users_service.unassign_professional_from_client(
            company_id, request, current_user.id
        )
        return client
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except UserNotInCompanyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ClientNotAssignedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidUserProfileError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{company_id}/professionals/{professional_id}/clients", response_model=List[CompanyClient])
def get_professional_clients(
    company_id: int,
    professional_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all clients assigned to a specific professional"""
    _validate_company_access(current_user, company_id)
    
    # Professional can only see their own clients
    if current_user.profile == UserProfile.PROFESSIONAL and current_user.id != professional_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Professionals can only see their own clients"
        )
    
    company_users_service = CompanyUsersService(db)
    
    try:
        clients = company_users_service.get_professional_clients(professional_id, company_id)
        return clients
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except UserNotInCompanyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ProfessionalNotActiveError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidUserProfileError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 