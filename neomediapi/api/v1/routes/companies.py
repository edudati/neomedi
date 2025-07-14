from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from neomediapi.infra.db.session import get_db
from neomediapi.auth.dependencies import get_current_user
from neomediapi.auth.authenticated_user import AuthenticatedUser
from neomediapi.services.company_service import CompanyService
from neomediapi.domain.company.dtos.company_dto import (
    CompanyCreate, 
    CompanyUpdate, 
    CompanyResponse, 
    CompanyWithRelations
)
from neomediapi.domain.company.exceptions import (
    CompanyNotFoundError,
    CompanyAlreadyExistsError,
    CompanyNotActiveError,
    CompanyDeletedError,
    AdminUserAlreadyHasCompanyError,
    OnlyAdminCanManageCompanyError,
    InvalidCNPJError
)
from neomediapi.enums.user_profiles import UserProfile

router = APIRouter(prefix="/companies", tags=["companies"])

def _validate_company_management_permission(current_user: AuthenticatedUser) -> None:
    """Validate if current user can manage companies (Admin or Super)"""
    if not current_user.profile.can_manage_company():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and super users can manage companies"
        )

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    company_create: CompanyCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new company (only for admin users)"""
    _validate_company_management_permission(current_user)
    
    company_service = CompanyService(db)
    
    try:
        company = company_service.create_company(company_create, current_user.id)
        return company
    except AdminUserAlreadyHasCompanyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidCNPJError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except CompanyAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/", response_model=List[CompanyResponse])
def get_all_companies(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all companies (only for admin users)"""
    _validate_company_management_permission(current_user)
    
    company_service = CompanyService(db)
    companies = company_service.get_all_companies(current_user.id)
    return companies

@router.get("/active", response_model=List[CompanyResponse])
def get_all_active_companies(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active companies (only for admin users)"""
    _validate_company_management_permission(current_user)
    
    company_service = CompanyService(db)
    companies = company_service.get_all_active_companies(current_user.id)
    return companies

@router.get("/my-company", response_model=CompanyResponse)
def get_my_company(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's company (only for admin users)"""
    _validate_company_management_permission(current_user)
    
    company_service = CompanyService(db)
    
    try:
        company = company_service.get_company_by_admin_user(current_user.id)
        return company
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/{company_id}", response_model=CompanyResponse)
def get_company_by_id(
    company_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get company by ID (only for admin users)"""
    _validate_company_management_permission(current_user)
    
    company_service = CompanyService(db)
    
    try:
        company = company_service.get_company_by_id(company_id, current_user.id)
        return company
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/{company_id}/with-relations", response_model=CompanyWithRelations)
def get_company_with_relations(
    company_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get company with relations by ID (only for admin users)"""
    _validate_company_management_permission(current_user)
    
    company_service = CompanyService(db)
    
    try:
        company = company_service.get_company_with_relations(company_id, current_user.id)
        return company
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update company (only for admin users)"""
    _validate_company_management_permission(current_user)
    
    company_service = CompanyService(db)
    
    try:
        company = company_service.update_company(company_id, company_update, current_user.id)
        return company
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except CompanyDeletedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidCNPJError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except CompanyAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete company (only for admin users)"""
    _validate_company_management_permission(current_user)
    
    company_service = CompanyService(db)
    
    try:
        company_service.delete_company(company_id, current_user.id)
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except CompanyDeletedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{company_id}/restore", response_model=CompanyResponse)
def restore_company(
    company_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restore deleted company (only for admin users)"""
    _validate_company_management_permission(current_user)
    
    company_service = CompanyService(db)
    
    try:
        company = company_service.restore_company(company_id, current_user.id)
        return company
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except CompanyDeletedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{company_id}/deactivate", response_model=CompanyResponse)
def deactivate_company(
    company_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate company (only for admin users)"""
    _validate_company_management_permission(current_user)
    
    company_service = CompanyService(db)
    
    try:
        company = company_service.deactivate_company(company_id, current_user.id)
        return company
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except CompanyDeletedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except CompanyNotActiveError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{company_id}/activate", response_model=CompanyResponse)
def activate_company(
    company_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activate company (only for admin users)"""
    _validate_company_management_permission(current_user)
    
    company_service = CompanyService(db)
    
    try:
        company = company_service.activate_company(company_id, current_user.id)
        return company
    except CompanyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except CompanyDeletedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except CompanyNotActiveError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 
