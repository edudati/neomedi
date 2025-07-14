from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    trade_name: Optional[str] = None
    cnpj: str
    corporate_name: str
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None

class CompanyCreate(CompanyBase):
    address_id: int

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    trade_name: Optional[str] = None
    cnpj: Optional[str] = None
    corporate_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    address_id: Optional[int] = None

class CompanyResponse(CompanyBase):
    id: int
    admin_user_id: int
    address_id: int
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CompanyWithRelations(CompanyResponse):
    from neomediapi.domain.address.dtos.address_dto import AddressResponse
    from neomediapi.domain.user.dtos.user_dto import UserResponse
    
    address: Optional[AddressResponse] = None
    admin_user: Optional[UserResponse] = None 