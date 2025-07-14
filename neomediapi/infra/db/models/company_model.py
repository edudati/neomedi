from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from neomediapi.infra.db.base_class import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic company information
    name = Column(String(255), nullable=False, index=True)
    trade_name = Column(String(255), nullable=True, index=True)
    cnpj = Column(String(18), nullable=False, unique=True, index=True)  # XX.XXX.XXX/XXXX-XX
    corporate_name = Column(String(255), nullable=False)
    
    # Contact information
    phone_number = Column(String(20), nullable=True, index=True)
    email = Column(String, nullable=True, index=True)
    website = Column(String(255), nullable=True)
    
    # Relationships
    admin_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    admin_user = relationship("User", back_populates="company", uselist=False, foreign_keys="User.company_id")
    
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    address = relationship("Address", back_populates="company", uselist=False)
    
    # Company users relationships
    users = relationship("User", back_populates="company", foreign_keys="User.company_id")
    
    # Control fields
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', cnpj='{self.cnpj}')>"
    
    def soft_delete(self):
        """Soft delete company by setting is_deleted=True"""
        self.is_deleted = True
        self.is_active = False
    
    def restore(self):
        """Restore soft deleted company"""
        self.is_deleted = False
        self.is_active = True
    
    def deactivate(self):
        """Deactivate company without deleting"""
        self.is_active = False
    
    def activate(self):
        """Activate company"""
        self.is_active = True 