from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date
from neomediapi.enums.user_roles import UserRole
from neomediapi.enums.document_types import DocumentType
from neomediapi.enums.gender_types import Gender
from neomediapi.domain.address.dtos.address_dto import AddressResponseDTO

class UserCreateDTO(BaseModel):
    name: str
    email: EmailStr
    role: UserRole


class UserResponseDTO(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole

    class Config:
        orm_mode = True  # allows Pydantic to read data from ORM models


class SessionVerifyResponseDTO(BaseModel):
    user_id: str
    email: str
    role: UserRole
    email_verified: bool


class SessionCreateResponseDTO(BaseModel):
    message: str
    user_id: str
    email: str
    role: UserRole
    email_verified: bool

# New DTOs for complete user profile
class UserProfileCreateDTO(BaseModel):
    """DTO for creating a complete user profile"""
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name of the user")
    document_type: DocumentType = Field(..., description="Type of identification document")
    document_id: str = Field(..., min_length=1, max_length=50, description="Document ID number")
    date_of_birth: date = Field(..., description="Date of birth")
    gender: Gender = Field(..., description="Gender")
    phone_number: str = Field(..., min_length=1, max_length=20, description="Phone number")
    secondary_email: Optional[EmailStr] = Field(None, description="Secondary email address")
    address_id: Optional[int] = Field(None, description="ID of the associated address")
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        """Validate that user is at least 18 years old"""
        from datetime import date
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("User must be at least 18 years old")
        if age > 120:
            raise ValueError("Invalid date of birth")
        return v
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Basic phone number validation"""
        # Remove non-digit characters
        digits = ''.join(filter(str.isdigit, v))
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Phone number must have between 10 and 15 digits")
        return v

class UserProfileUpdateDTO(BaseModel):
    """DTO for updating user profile (all fields optional)"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    document_type: Optional[DocumentType] = None
    document_id: Optional[str] = Field(None, min_length=1, max_length=50)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    phone_number: Optional[str] = Field(None, min_length=1, max_length=20)
    secondary_email: Optional[EmailStr] = None
    address_id: Optional[int] = None
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if v is None:
            return v
        from datetime import date
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("User must be at least 18 years old")
        if age > 120:
            raise ValueError("Invalid date of birth")
        return v
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is None:
            return v
        digits = ''.join(filter(str.isdigit, v))
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Phone number must have between 10 and 15 digits")
        return v

class UserProfileResponseDTO(BaseModel):
    """DTO for user profile responses"""
    id: int
    email: EmailStr
    role: UserRole
    full_name: str
    document_type: Optional[DocumentType]
    document_id: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[Gender]
    phone_number: Optional[str]
    secondary_email: Optional[EmailStr]
    address: Optional[AddressResponseDTO]
    is_active: bool
    is_deleted: bool
    profile_completed: bool
    created_at: str
    updated_at: str
    
    class Config:
        orm_mode = True

class UserSimpleResponseDTO(BaseModel):
    """Simplified user DTO for basic information"""
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    profile_completed: bool
    
    class Config:
        orm_mode = True

class UserListResponseDTO(BaseModel):
    """DTO for user list responses with pagination"""
    users: list[UserSimpleResponseDTO]
    total: int
    skip: int
    limit: int
    
    class Config:
        orm_mode = True
