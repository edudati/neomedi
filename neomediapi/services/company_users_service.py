from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func

from neomediapi.infra.db.repositories.company_repository import CompanyRepository
from neomediapi.infra.db.repositories.user_repository import UserRepository
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
from neomediapi.auth.permissions import PermissionManager

class CompanyUsersService:
    def __init__(self, db: Session):
        self.db = db
        self.company_repository = CompanyRepository(db)
        self.user_repository = UserRepository(db)
    
    def _validate_user_in_company(self, user_id: int, company_id: int) -> None:
        """Validate if user belongs to the company"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotInCompanyError("User not found")
        
        if user.company_id != company_id:
            raise UserNotInCompanyError("User does not belong to this company")
    
    def _validate_professional_active(self, professional_id: int, company_id: int) -> None:
        """Validate if professional is active and belongs to company"""
        self._validate_user_in_company(professional_id, company_id)
        
        professional = self.user_repository.get_by_id(professional_id)
        if professional.profile != UserProfile.PROFESSIONAL:
            raise InvalidUserProfileError("User is not a professional")
        
        if not professional.is_active:
            raise ProfessionalNotActiveError("Professional is not active")
    
    def get_company_users_summary(self, company_id: int, user_id: int) -> CompanyUsersSummary:
        """Get summary of users in a company"""
        # Validate company exists
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company with ID {company_id} not found")
        
        # Get all users in company
        users = self.company_repository.get_users_by_company_id(company_id)
        
        # Count by profile
        managers = [u for u in users if u.profile == UserProfile.MANAGER]
        professionals = [u for u in users if u.profile == UserProfile.PROFESSIONAL]
        clients = [u for u in users if u.profile == UserProfile.CLIENT]
        
        active_users = [u for u in users if u.is_active]
        
        return CompanyUsersSummary(
            company_id=company_id,
            company_name=company.name,
            total_users=len(users),
            active_users=len(active_users),
            managers_count=len(managers),
            professionals_count=len(professionals),
            clients_count=len(clients)
        )
    
    def get_company_managers(self, company_id: int, user_id: int) -> List[CompanyManager]:
        """Get managers in a company"""
        # Validate company exists
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company with ID {company_id} not found")
        
        # Get managers
        managers = self.company_repository.get_users_by_company_id_and_profile(
            company_id, UserProfile.MANAGER
        )
        
        result = []
        for manager in managers:
            # Count professionals under this manager
            professionals_count = len([
                u for u in self.company_repository.get_users_by_company_id(company_id)
                if u.profile == UserProfile.PROFESSIONAL and u.is_active
            ])
            
            result.append(CompanyManager(
                id=manager.id,
                full_name=manager.full_name,
                email=manager.email,
                profile=manager.profile,
                is_active=manager.is_active,
                created_at=manager.created_at,
                professionals_count=professionals_count
            ))
        
        return result
    
    def get_company_professionals(self, company_id: int, user_id: int) -> List[CompanyProfessional]:
        """Get professionals in a company"""
        # Validate company exists
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company with ID {company_id} not found")
        
        # Get active professionals
        professionals = self.company_repository.get_active_professionals_by_company_id(company_id)
        
        result = []
        for professional in professionals:
            # Count clients assigned to this professional
            clients_count = len([
                u for u in self.company_repository.get_users_by_company_id(company_id)
                if u.profile == UserProfile.CLIENT and u.professional_id == professional.id
            ])
            
            result.append(CompanyProfessional(
                id=professional.id,
                full_name=professional.full_name,
                email=professional.email,
                profile=professional.profile,
                is_active=professional.is_active,
                created_at=professional.created_at,
                clients_count=clients_count
            ))
        
        return result
    
    def get_company_clients(self, company_id: int, user_id: int) -> List[CompanyClient]:
        """Get clients in a company with their assigned professionals"""
        # Validate company exists
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company with ID {company_id} not found")
        
        # Get clients
        clients = self.company_repository.get_users_by_company_id_and_profile(
            company_id, UserProfile.CLIENT
        )
        
        result = []
        for client in clients:
            professional_name = None
            if client.professional_id:
                professional = self.user_repository.get_by_id(client.professional_id)
                if professional:
                    professional_name = professional.full_name
            
            result.append(CompanyClient(
                id=client.id,
                full_name=client.full_name,
                email=client.email,
                profile=client.profile,
                is_active=client.is_active,
                created_at=client.created_at,
                professional_id=client.professional_id,
                professional_name=professional_name
            ))
        
        return result
    
    def get_company_users_list(self, company_id: int, user_id: int) -> CompanyUsersList:
        """Get complete list of users in a company"""
        summary = self.get_company_users_summary(company_id, user_id)
        managers = self.get_company_managers(company_id, user_id)
        professionals = self.get_company_professionals(company_id, user_id)
        clients = self.get_company_clients(company_id, user_id)
        
        return CompanyUsersList(
            company=summary,
            managers=managers,
            professionals=professionals,
            clients=clients
        )
    
    def assign_professional_to_client(
        self, 
        company_id: int, 
        request: AssignProfessionalRequest, 
        user_id: int
    ) -> CompanyClient:
        """Assign a professional to a client"""
        # Validate company exists
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company with ID {company_id} not found")
        
        # Validate client belongs to company
        self._validate_user_in_company(request.client_id, company_id)
        
        # Validate professional is active and belongs to company
        self._validate_professional_active(request.professional_id, company_id)
        
        # Get client
        client = self.user_repository.get_by_id(request.client_id)
        if client.profile != UserProfile.CLIENT:
            raise InvalidUserProfileError("User is not a client")
        
        # Check if client is already assigned
        if client.professional_id:
            raise ClientAlreadyAssignedError("Client is already assigned to a professional")
        
        # Assign professional
        client.professional_id = request.professional_id
        self.user_repository.update(client)
        
        # Return updated client
        return self.get_company_clients(company_id, user_id)[0]
    
    def unassign_professional_from_client(
        self, 
        company_id: int, 
        request: UnassignProfessionalRequest, 
        user_id: int
    ) -> CompanyClient:
        """Unassign a professional from a client"""
        # Validate company exists
        company = self.company_repository.get_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company with ID {company_id} not found")
        
        # Validate client belongs to company
        self._validate_user_in_company(request.client_id, company_id)
        
        # Get client
        client = self.user_repository.get_by_id(request.client_id)
        if client.profile != UserProfile.CLIENT:
            raise InvalidUserProfileError("User is not a client")
        
        # Check if client is assigned
        if not client.professional_id:
            raise ClientNotAssignedError("Client is not assigned to any professional")
        
        # Unassign professional
        client.professional_id = None
        self.user_repository.update(client)
        
        # Return updated client
        return self.get_company_clients(company_id, user_id)[0]
    
    def get_professional_clients(self, professional_id: int, company_id: int) -> List[CompanyClient]:
        """Get all clients assigned to a specific professional"""
        # Validate professional
        self._validate_professional_active(professional_id, company_id)
        
        # Get clients assigned to this professional
        clients = [
            u for u in self.company_repository.get_users_by_company_id(company_id)
            if u.profile == UserProfile.CLIENT and u.professional_id == professional_id
        ]
        
        result = []
        for client in clients:
            result.append(CompanyClient(
                id=client.id,
                full_name=client.full_name,
                email=client.email,
                profile=client.profile,
                is_active=client.is_active,
                created_at=client.created_at,
                professional_id=client.professional_id,
                professional_name=None  # We know it's the current professional
            ))
        
        return result 