from sqlalchemy.orm import Session
from typing import List, Optional
import re

from neomediapi.infra.db.repositories.company_repository import CompanyRepository
from neomediapi.infra.db.repositories.user_repository import UserRepository
from neomediapi.infra.db.repositories.address_repository import AddressRepository
from neomediapi.domain.company.dtos.company_dto import CompanyCreate, CompanyUpdate, CompanyResponse, CompanyWithRelations
from neomediapi.domain.company.mappers.company_mapper import CompanyMapper
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

class CompanyService:
    def __init__(self, db: Session):
        self.db = db
        self.company_repository = CompanyRepository(db)
        self.user_repository = UserRepository(db)
        self.address_repository = AddressRepository(db)
    
    def _validate_cnpj(self, cnpj: str) -> bool:
        """Validate CNPJ format"""
        # Remove non-numeric characters
        cnpj_clean = re.sub(r'[^\d]', '', cnpj)
        
        # Check if it has 14 digits
        if len(cnpj_clean) != 14:
            return False
        
        # Check if all digits are not the same
        if len(set(cnpj_clean)) == 1:
            return False
        
        # CNPJ validation algorithm
        def calculate_digit(cnpj: str, position: int) -> int:
            weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            if position == 2:
                weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            
            total = sum(int(cnpj[i]) * weights[i] for i in range(len(weights)))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder
        
        # Validate first digit
        if int(cnpj_clean[12]) != calculate_digit(cnpj_clean[:12], 1):
            return False
        
        # Validate second digit
        if int(cnpj_clean[13]) != calculate_digit(cnpj_clean[:13], 2):
            return False
        
        return True
    
    def _validate_company_management_permission(self, user_id: int) -> None:
        """Validate if user can manage companies (Admin or Super)"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise CompanyNotFoundError("User not found")
        
        if not user.profile.can_manage_company():
            raise OnlyAdminCanManageCompanyError("Only admin and super users can manage companies")
        
        if not user.is_active or user.is_deleted:
            raise CompanyNotActiveError("User is not active")
    
    def create_company(self, company_create: CompanyCreate, admin_user_id: int) -> CompanyResponse:
        """Create a new company (only for admin users)"""
        # Validate admin user
        self._validate_company_management_permission(admin_user_id)
        
        # Check if admin user already has a company
        if self.company_repository.exists_by_admin_user_id(admin_user_id):
            raise AdminUserAlreadyHasCompanyError("Admin user already has a company")
        
        # Validate CNPJ
        if not self._validate_cnpj(company_create.cnpj):
            raise InvalidCNPJError("Invalid CNPJ format")
        
        # Check if CNPJ already exists
        if self.company_repository.exists_by_cnpj(company_create.cnpj):
            raise CompanyAlreadyExistsError(f"Company with CNPJ {company_create.cnpj} already exists")
        
        # Validate address exists
        address = self.address_repository.get_by_id(company_create.address_id)
        if not address:
            raise CompanyNotFoundError("Address not found")
        
        # Create company
        company = CompanyMapper.to_entity(company_create, admin_user_id)
        created_company = self.company_repository.create(company)
        
        return CompanyMapper.to_response(created_company)
    
    def get_company_by_id(self, company_id: int, user_id: int) -> CompanyResponse:
        """Get company by ID (only for admin users)"""
        # Validate admin user
        self._validate_company_management_permission(user_id)
        
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company with ID {company_id} not found")
        
        return CompanyMapper.to_response(company)
    
    def get_company_by_admin_user(self, admin_user_id: int) -> CompanyResponse:
        """Get company by admin user ID"""
        # Validate admin user
        self._validate_company_management_permission(admin_user_id)
        
        company = self.company_repository.get_by_admin_user_id(admin_user_id)
        if not company:
            raise CompanyNotFoundError(f"Company for admin user {admin_user_id} not found")
        
        return CompanyMapper.to_response(company)
    
    def get_company_with_relations(self, company_id: int, user_id: int) -> CompanyWithRelations:
        """Get company with relations by ID (only for admin users)"""
        # Validate admin user
        self._validate_company_management_permission(user_id)
        
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company with ID {company_id} not found")
        
        return CompanyMapper.to_response_with_relations(company)
    
    def get_all_companies(self, user_id: int) -> List[CompanyResponse]:
        """Get all companies (only for admin users)"""
        # Validate admin user
        self._validate_company_management_permission(user_id)
        
        companies = self.company_repository.get_all()
        return [CompanyMapper.to_response(company) for company in companies]
    
    def get_all_active_companies(self, user_id: int) -> List[CompanyResponse]:
        """Get all active companies (only for admin users)"""
        # Validate admin user
        self._validate_company_management_permission(user_id)
        
        companies = self.company_repository.get_all_active()
        return [CompanyMapper.to_response(company) for company in companies]
    
    def update_company(self, company_id: int, company_update: CompanyUpdate, user_id: int) -> CompanyResponse:
        """Update company (only for admin users)"""
        # Validate admin user
        self._validate_company_management_permission(user_id)
        
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company with ID {company_id} not found")
        
        if company.is_deleted:
            raise CompanyDeletedError("Cannot update deleted company")
        
        # Validate CNPJ if being updated
        if company_update.cnpj:
            if not self._validate_cnpj(company_update.cnpj):
                raise InvalidCNPJError("Invalid CNPJ format")
            
            if self.company_repository.exists_by_cnpj(company_update.cnpj, exclude_id=company_id):
                raise CompanyAlreadyExistsError(f"Company with CNPJ {company_update.cnpj} already exists")
        
        # Validate address if being updated
        if company_update.address_id:
            address = self.address_repository.get_by_id(company_update.address_id)
            if not address:
                raise CompanyNotFoundError("Address not found")
        
        # Update company
        updated_company = CompanyMapper.update_entity(company, company_update)
        saved_company = self.company_repository.update(updated_company)
        
        return CompanyMapper.to_response(saved_company)
    
    def delete_company(self, company_id: int, user_id: int) -> None:
        """Delete company (only for admin users)"""
        # Validate admin user
        self._validate_company_management_permission(user_id)
        
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company with ID {company_id} not found")
        
        if company.is_deleted:
            raise CompanyDeletedError("Company is already deleted")
        
        self.company_repository.delete(company)
    
    def restore_company(self, company_id: int, user_id: int) -> CompanyResponse:
        """Restore deleted company (only for admin users)"""
        # Validate admin user
        self._validate_company_management_permission(user_id)
        
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company with ID {company_id} not found")
        
        if not company.is_deleted:
            raise CompanyDeletedError("Company is not deleted")
        
        restored_company = self.company_repository.restore(company)
        return CompanyMapper.to_response(restored_company)
    
    def deactivate_company(self, company_id: int, user_id: int) -> CompanyResponse:
        """Deactivate company (only for admin users)"""
        # Validate admin user
        self._validate_company_management_permission(user_id)
        
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company with ID {company_id} not found")
        
        if company.is_deleted:
            raise CompanyDeletedError("Cannot deactivate deleted company")
        
        if not company.is_active:
            raise CompanyNotActiveError("Company is already inactive")
        
        deactivated_company = self.company_repository.deactivate(company)
        return CompanyMapper.to_response(deactivated_company)
    
    def activate_company(self, company_id: int, user_id: int) -> CompanyResponse:
        """Activate company (only for admin users)"""
        # Validate admin user
        self._validate_company_management_permission(user_id)
        
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company with ID {company_id} not found")
        
        if company.is_deleted:
            raise CompanyDeletedError("Cannot activate deleted company")
        
        if company.is_active:
            raise CompanyNotActiveError("Company is already active")
        
        activated_company = self.company_repository.activate(company)
        return CompanyMapper.to_response(activated_company) 