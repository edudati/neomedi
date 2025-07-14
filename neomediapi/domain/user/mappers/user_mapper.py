from neomediapi.domain.user.dtos.user_dto import (
    UserCreateDTO, 
    UserResponseDTO,
    UserProfileCreateDTO,
    UserProfileUpdateDTO,
    UserProfileResponseDTO,
    UserSimpleResponseDTO,
    SessionVerifyResponseDTO
)
from neomediapi.domain.address.mappers.address_mapper import map_address_entity_to_response_dto
from neomediapi.infra.db.models.user_model import User
from neomediapi.enums.user_profiles import UserProfile
from typing import Optional

def map_user_create_dto_to_entity(dto: UserCreateDTO) -> User:
    """Map UserCreateDTO to User entity (for authentication)"""
    return User(
        name=dto.name,
        email=dto.email,
        profile=dto.profile,
        full_name=dto.name  # Use name as full_name initially
    )

def map_user_profile_create_dto_to_entity(dto: UserProfileCreateDTO, user: User) -> User:
    """Map UserProfileCreateDTO to existing User entity"""
    user.full_name = dto.full_name
    user.document_type = dto.document_type
    user.document_id = dto.document_id
    user.date_of_birth = dto.date_of_birth
    user.gender = dto.gender
    user.phone_number = dto.phone_number
    user.secondary_email = dto.secondary_email
    user.address_id = dto.address_id
    
    # Update profile_completed based on required fields
    user.profile_completed = user.is_profile_complete
    
    return user

def map_user_profile_update_dto_to_entity(dto: UserProfileUpdateDTO, user: User) -> User:
    """Map UserProfileUpdateDTO to existing User entity"""
    if dto.full_name is not None:
        user.full_name = dto.full_name
    if dto.document_type is not None:
        user.document_type = dto.document_type
    if dto.document_id is not None:
        user.document_id = dto.document_id
    if dto.date_of_birth is not None:
        user.date_of_birth = dto.date_of_birth
    if dto.gender is not None:
        user.gender = dto.gender
    if dto.phone_number is not None:
        user.phone_number = dto.phone_number
    if dto.secondary_email is not None:
        user.secondary_email = dto.secondary_email
    if dto.address_id is not None:
        user.address_id = dto.address_id
    
    # Update profile_completed based on required fields
    user.profile_completed = user.is_profile_complete
    
    return user

def map_user_entity_to_response_dto(user: User) -> UserResponseDTO:
    """Map User entity to UserResponseDTO (for authentication)"""
    return UserResponseDTO(
        id=user.id,
        name=user.full_name,  # Use full_name as name for backward compatibility
        email=user.email,
        profile=user.profile
    )

def map_user_entity_to_profile_response_dto(user: User) -> UserProfileResponseDTO:
    """Map User entity to UserProfileResponseDTO"""
    return UserProfileResponseDTO(
        id=user.id,
        email=user.email,
        profile=user.profile,
        full_name=user.full_name,
        document_type=user.document_type,
        document_id=user.document_id,
        date_of_birth=user.date_of_birth,
        gender=user.gender,
        phone_number=user.phone_number,
        secondary_email=user.secondary_email,
        address=map_address_entity_to_response_dto(user.address) if user.address else None,
        is_active=user.is_active,
        is_deleted=user.is_deleted,
        profile_completed=user.profile_completed,
        created_at=user.created_at.isoformat() if user.created_at else "",
        updated_at=user.updated_at.isoformat() if user.updated_at else ""
    )

def map_user_entity_to_simple_response_dto(user: User) -> UserSimpleResponseDTO:
    """Map User entity to UserSimpleResponseDTO"""
    return UserSimpleResponseDTO(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        profile=user.profile,
        is_active=user.is_active,
        profile_completed=user.profile_completed
    )

def map_user_to_session_verify_dto(
    user: User,
    email: str,
    email_verified: bool
) -> SessionVerifyResponseDTO:
    return SessionVerifyResponseDTO(
        user_id=str(user.firebase_uid),
        email=email,
        profile=user.profile,
        email_verified=email_verified
    )
