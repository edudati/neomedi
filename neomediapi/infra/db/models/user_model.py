# infra/db/models/user_model.py

from sqlalchemy import Column, DateTime, Integer, String, Enum, Boolean, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from neomediapi.infra.db.base_class import Base
from neomediapi.enums.user_roles import UserRole
from neomediapi.enums.document_types import DocumentType
from neomediapi.enums.gender_types import Gender

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic authentication fields (existing)
    email = Column(String, nullable=False, unique=True, index=True)
    firebase_uid = Column(String, unique=True, nullable=False, index=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CLIENT)
    
    # Personal information (new)
    full_name = Column(String(255), nullable=False, index=True)
    document_type = Column(Enum(DocumentType), nullable=True)
    document_id = Column(String(50), nullable=True, unique=True, index=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(Enum(Gender), nullable=True)
    
    # Contact information (new)
    phone_number = Column(String(20), nullable=True, index=True)
    secondary_email = Column(String, nullable=True, index=True)
    
    # Address relationship (new)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=True)
    address = relationship("Address", back_populates="user", uselist=False)
    
    # Control fields (new)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    profile_completed = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps (existing + new)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}')>"
    
    @property
    def is_profile_complete(self) -> bool:
        """Check if user profile is complete"""
        required_fields = [
            self.full_name,
            self.document_type,
            self.document_id,
            self.date_of_birth,
            self.phone_number
        ]
        return all(field is not None for field in required_fields)
    
    @property
    def age(self) -> int | None:
        """Calculate user age from date_of_birth"""
        if not self.date_of_birth:
            return None
        
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def soft_delete(self):
        """Soft delete user by setting is_deleted=True"""
        self.is_deleted = True
        self.is_active = False
    
    def restore(self):
        """Restore soft deleted user"""
        self.is_deleted = False
        self.is_active = True
    
    def deactivate(self):
        """Deactivate user without deleting"""
        self.is_active = False
    
    def activate(self):
        """Activate user"""
        self.is_active = True