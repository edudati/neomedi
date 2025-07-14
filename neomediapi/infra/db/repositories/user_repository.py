from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from neomediapi.infra.db.models.user_model import User
from neomediapi.enums.user_profiles import UserProfile
from neomediapi.enums.document_types import DocumentType
from neomediapi.enums.gender_types import Gender

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(
            and_(User.id == user_id, User.is_deleted == False)
        ).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(
            and_(User.email == email, User.is_deleted == False)
        ).first()

    def get_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        """Get user by Firebase UID"""
        return self.db.query(User).filter(
            and_(User.firebase_uid == firebase_uid, User.is_deleted == False)
        ).first()

    def get_by_document_id(self, document_id: str) -> Optional[User]:
        """Get user by document ID"""
        return self.db.query(User).filter(
            and_(User.document_id == document_id, User.is_deleted == False)
        ).first()

    def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        """Get user by phone number"""
        return self.db.query(User).filter(
            and_(User.phone_number == phone_number, User.is_deleted == False)
        ).first()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users with pagination"""
        return self.db.query(User).filter(
            and_(User.is_active == True, User.is_deleted == False)
        ).offset(skip).limit(limit).all()

    def get_users_by_profile(self, profile: UserProfile, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by profile"""
        return self.db.query(User).filter(
            and_(User.profile == profile, User.is_deleted == False)
        ).offset(skip).limit(limit).all()

    def get_users_by_document_type(self, document_type: DocumentType) -> List[User]:
        """Get users by document type"""
        return self.db.query(User).filter(
            and_(User.document_type == document_type, User.is_deleted == False)
        ).all()

    def get_users_by_gender(self, gender: Gender) -> List[User]:
        """Get users by gender"""
        return self.db.query(User).filter(
            and_(User.gender == gender, User.is_deleted == False)
        ).all()

    def get_users_with_complete_profile(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users with complete profile"""
        return self.db.query(User).filter(
            and_(User.profile_completed == True, User.is_deleted == False)
        ).offset(skip).limit(limit).all()

    def get_users_with_incomplete_profile(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users with incomplete profile"""
        return self.db.query(User).filter(
            and_(User.profile_completed == False, User.is_deleted == False)
        ).offset(skip).limit(limit).all()

    def search_users(self, query: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Search users by name, email, or document ID"""
        return self.db.query(User).filter(
            and_(
                User.is_deleted == False,
                or_(
                    User.full_name.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                    User.document_id.ilike(f"%{query}%")
                )
            )
        ).offset(skip).limit(limit).all()

    def get_users_by_address_city(self, city: str) -> List[User]:
        """Get users by address city"""
        return self.db.query(User).join(User.address).filter(
            and_(User.address.has(city=city), User.is_deleted == False)
        ).all()

    def get_users_by_address_state(self, state: str) -> List[User]:
        """Get users by address state"""
        return self.db.query(User).join(User.address).filter(
            and_(User.address.has(state=state), User.is_deleted == False)
        ).all()

    def get_users_with_address(self) -> List[User]:
        """Get users that have an address"""
        return self.db.query(User).filter(
            and_(User.address_id.isnot(None), User.is_deleted == False)
        ).all()

    def get_users_without_address(self) -> List[User]:
        """Get users that don't have an address"""
        return self.db.query(User).filter(
            and_(User.address_id.is_(None), User.is_deleted == False)
        ).all()

    def save(self, user: User) -> User:
        """Save user to database"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        """Update user in database"""
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> bool:
        """Hard delete user from database"""
        self.db.delete(user)
        self.db.commit()
        return True

    def soft_delete(self, user: User) -> bool:
        """Soft delete user"""
        user.soft_delete()
        self.db.commit()
        return True

    def restore(self, user: User) -> bool:
        """Restore soft deleted user"""
        user.restore()
        self.db.commit()
        return True

    def deactivate(self, user: User) -> bool:
        """Deactivate user"""
        user.deactivate()
        self.db.commit()
        return True

    def activate(self, user: User) -> bool:
        """Activate user"""
        user.activate()
        self.db.commit()
        return True

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination (including deleted)"""
        return self.db.query(User).offset(skip).limit(limit).all()

    def count_active_users(self) -> int:
        """Count active users"""
        return self.db.query(User).filter(
            and_(User.is_active == True, User.is_deleted == False)
        ).count()

    def count_users_by_profile(self, profile: UserProfile) -> int:
        """Count users by profile"""
        return self.db.query(User).filter(
            and_(User.profile == profile, User.is_deleted == False)
        ).count()

    def count_users_with_complete_profile(self) -> int:
        """Count users with complete profile"""
        return self.db.query(User).filter(
            and_(User.profile_completed == True, User.is_deleted == False)
        ).count()

