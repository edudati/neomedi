from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from neomediapi.enums.user_profiles import UserProfile

class CompanyUserBase(BaseModel):
    id: int
    full_name: str
    email: str
    profile: UserProfile
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CompanyProfessional(CompanyUserBase):
    """Professional user in a company"""
    clients_count: int = 0

class CompanyManager(CompanyUserBase):
    """Manager user in a company"""
    professionals_count: int = 0

class CompanyClient(CompanyUserBase):
    """Client user in a company"""
    professional_id: Optional[int] = None
    professional_name: Optional[str] = None

class CompanyUsersSummary(BaseModel):
    """Summary of users in a company"""
    company_id: int
    company_name: str
    total_users: int
    active_users: int
    managers_count: int
    professionals_count: int
    clients_count: int

    class Config:
        from_attributes = True

class CompanyUsersList(BaseModel):
    """Complete list of users in a company"""
    company: CompanyUsersSummary
    managers: List[CompanyManager]
    professionals: List[CompanyProfessional]
    clients: List[CompanyClient]

    class Config:
        from_attributes = True

class AssignProfessionalRequest(BaseModel):
    """Request to assign a professional to a client"""
    client_id: int
    professional_id: int

class UnassignProfessionalRequest(BaseModel):
    """Request to unassign a professional from a client"""
    client_id: int 