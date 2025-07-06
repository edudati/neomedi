from typing import List, Optional
from neomediapi.domain.user.dtos.user_dto import (
    UserCreateDTO, 
    UserResponseDTO,
    UserProfileCreateDTO,
    UserProfileUpdateDTO,
    UserProfileResponseDTO,
    UserSimpleResponseDTO,
    UserListResponseDTO
)
from neomediapi.domain.user.exceptions import (
    UserNotFoundError, 
    UserValidationError,
    UserAlreadyExistsError
)
from neomediapi.domain.user.mappers.user_mapper import (
    map_user_create_dto_to_entity,
    map_user_profile_create_dto_to_entity,
    map_user_profile_update_dto_to_entity,
    map_user_entity_to_response_dto,
    map_user_entity_to_profile_response_dto,
    map_user_entity_to_simple_response_dto
)
from neomediapi.infra.db.models.user_model import User
from neomediapi.infra.db.repositories.user_repository import UserRepository
from neomediapi.enums.user_roles import UserRole
from neomediapi.enums.document_types import DocumentType
from neomediapi.enums.gender_types import Gender

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    # Authentication methods (existing)
    def create_user(self, user_data: UserCreateDTO, firebase_uid: str) -> UserResponseDTO:
        """Create a new user for authentication"""
        try:
            # Check if user already exists
            existing_user = self.user_repository.get_by_email(user_data.email)
            if existing_user:
                raise UserAlreadyExistsError(f"User with email {user_data.email} already exists")
            
            # Create user entity
            user_entity = map_user_create_dto_to_entity(user_data)
            user_entity.firebase_uid = firebase_uid
            
            # Save to database
            saved_user = self.user_repository.save(user_entity)
            
            return map_user_entity_to_response_dto(saved_user)
            
        except Exception as e:
            raise UserValidationError(f"Failed to create user: {str(e)}")

    def get_user_by_firebase_uid(self, firebase_uid: str) -> UserResponseDTO:
        """Get user by Firebase UID for authentication"""
        user = self.user_repository.get_by_firebase_uid(firebase_uid)
        if not user:
            raise UserNotFoundError(f"User with Firebase UID {firebase_uid} not found")
        
        return map_user_entity_to_response_dto(user)

    # Profile management methods (new)
    def create_user_profile(self, user_id: int, profile_data: UserProfileCreateDTO) -> UserProfileResponseDTO:
        """Create complete user profile"""
        try:
            # Get existing user
            user = self.user_repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"User with ID {user_id} not found")
            
            # Check if document_id is already in use
            if profile_data.document_id:
                existing_user = self.user_repository.get_by_document_id(profile_data.document_id)
                if existing_user and existing_user.id != user_id:
                    raise UserAlreadyExistsError(f"Document ID {profile_data.document_id} already in use")
            
            # Check if phone_number is already in use
            if profile_data.phone_number:
                existing_user = self.user_repository.get_by_phone_number(profile_data.phone_number)
                if existing_user and existing_user.id != user_id:
                    raise UserAlreadyExistsError(f"Phone number {profile_data.phone_number} already in use")
            
            # Update user with profile data
            updated_user = map_user_profile_create_dto_to_entity(profile_data, user)
            saved_user = self.user_repository.update(updated_user)
            
            return map_user_entity_to_profile_response_dto(saved_user)
            
        except Exception as e:
            raise UserValidationError(f"Failed to create user profile: {str(e)}")

    def update_user_profile(self, user_id: int, profile_data: UserProfileUpdateDTO) -> UserProfileResponseDTO:
        """Update user profile"""
        try:
            # Get existing user
            user = self.user_repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"User with ID {user_id} not found")
            
            # Check if document_id is already in use (if being updated)
            if profile_data.document_id:
                existing_user = self.user_repository.get_by_document_id(profile_data.document_id)
                if existing_user and existing_user.id != user_id:
                    raise UserAlreadyExistsError(f"Document ID {profile_data.document_id} already in use")
            
            # Check if phone_number is already in use (if being updated)
            if profile_data.phone_number:
                existing_user = self.user_repository.get_by_phone_number(profile_data.phone_number)
                if existing_user and existing_user.id != user_id:
                    raise UserAlreadyExistsError(f"Phone number {profile_data.phone_number} already in use")
            
            # Update user with profile data
            updated_user = map_user_profile_update_dto_to_entity(profile_data, user)
            saved_user = self.user_repository.update(updated_user)
            
            return map_user_entity_to_profile_response_dto(saved_user)
            
        except Exception as e:
            raise UserValidationError(f"Failed to update user profile: {str(e)}")

    def get_user_profile(self, user_id: int) -> UserProfileResponseDTO:
        """Get complete user profile"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        return map_user_entity_to_profile_response_dto(user)

    def get_user_by_id(self, user_id: int) -> UserResponseDTO:
        """Get user by ID (for authentication compatibility)"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        return map_user_entity_to_response_dto(user)

    # User management methods
    def get_all_users(self, skip: int = 0, limit: int = 100) -> UserListResponseDTO:
        """Get all active users with pagination"""
        users = self.user_repository.get_active_users(skip, limit)
        total = self.user_repository.count_active_users()
        
        return UserListResponseDTO(
            users=[map_user_entity_to_simple_response_dto(user) for user in users],
            total=total,
            skip=skip,
            limit=limit
        )

    def search_users(self, query: str, skip: int = 0, limit: int = 100) -> UserListResponseDTO:
        """Search users by name, email, or document ID"""
        users = self.user_repository.search_users(query, skip, limit)
        total = len(users)  # This is approximate, could be improved with count query
        
        return UserListResponseDTO(
            users=[map_user_entity_to_simple_response_dto(user) for user in users],
            total=total,
            skip=skip,
            limit=limit
        )

    def get_users_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> UserListResponseDTO:
        """Get users by role"""
        users = self.user_repository.get_users_by_role(role, skip, limit)
        total = self.user_repository.count_users_by_role(role)
        
        return UserListResponseDTO(
            users=[map_user_entity_to_simple_response_dto(user) for user in users],
            total=total,
            skip=skip,
            limit=limit
        )

    def get_users_by_document_type(self, document_type: DocumentType) -> List[UserSimpleResponseDTO]:
        """Get users by document type"""
        users = self.user_repository.get_users_by_document_type(document_type)
        return [map_user_entity_to_simple_response_dto(user) for user in users]

    def get_users_by_gender(self, gender: Gender) -> List[UserSimpleResponseDTO]:
        """Get users by gender"""
        users = self.user_repository.get_users_by_gender(gender)
        return [map_user_entity_to_simple_response_dto(user) for user in users]

    def get_users_with_complete_profile(self, skip: int = 0, limit: int = 100) -> UserListResponseDTO:
        """Get users with complete profile"""
        users = self.user_repository.get_users_with_complete_profile(skip, limit)
        total = self.user_repository.count_users_with_complete_profile()
        
        return UserListResponseDTO(
            users=[map_user_entity_to_simple_response_dto(user) for user in users],
            total=total,
            skip=skip,
            limit=limit
        )

    def get_users_with_incomplete_profile(self, skip: int = 0, limit: int = 100) -> UserListResponseDTO:
        """Get users with incomplete profile"""
        users = self.user_repository.get_users_with_incomplete_profile(skip, limit)
        total = len(users)  # This is approximate
        
        return UserListResponseDTO(
            users=[map_user_entity_to_simple_response_dto(user) for user in users],
            total=total,
            skip=skip,
            limit=limit
        )

    def get_users_by_address_city(self, city: str) -> List[UserSimpleResponseDTO]:
        """Get users by address city"""
        users = self.user_repository.get_users_by_address_city(city)
        return [map_user_entity_to_simple_response_dto(user) for user in users]

    def get_users_by_address_state(self, state: str) -> List[UserSimpleResponseDTO]:
        """Get users by address state"""
        users = self.user_repository.get_users_by_address_state(state)
        return [map_user_entity_to_simple_response_dto(user) for user in users]

    def get_users_with_address(self) -> List[UserSimpleResponseDTO]:
        """Get users that have an address"""
        users = self.user_repository.get_users_with_address()
        return [map_user_entity_to_simple_response_dto(user) for user in users]

    def get_users_without_address(self) -> List[UserSimpleResponseDTO]:
        """Get users that don't have an address"""
        users = self.user_repository.get_users_without_address()
        return [map_user_entity_to_simple_response_dto(user) for user in users]

    # User status management
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        return self.user_repository.deactivate(user)

    def activate_user(self, user_id: int) -> bool:
        """Activate user"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        return self.user_repository.activate(user)

    def soft_delete_user(self, user_id: int) -> bool:
        """Soft delete user"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        return self.user_repository.soft_delete(user)

    def restore_user(self, user_id: int) -> bool:
        """Restore soft deleted user"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        return self.user_repository.restore(user)

    def hard_delete_user(self, user_id: int) -> bool:
        """Hard delete user"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        return self.user_repository.delete(user)

    # Statistics methods
    def get_user_statistics(self) -> dict:
        """Get user statistics"""
        stats = {
            "total_active_users": self.user_repository.count_active_users(),
            "users_by_role": {},
            "users_with_complete_profile": self.user_repository.count_users_with_complete_profile(),
            "users_with_address": len(self.user_repository.get_users_with_address()),
            "users_without_address": len(self.user_repository.get_users_without_address())
        }
        
        # Count by role
        for role in UserRole:
            stats["users_by_role"][role.value] = self.user_repository.count_users_by_role(role)
        
        return stats
