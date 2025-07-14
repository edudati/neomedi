from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from neomediapi.infra.db.base_class import Base
from neomediapi.enums.facility_types import FacilityType

class Facility(Base):
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    
    # Dados básicos
    name = Column(String(255), nullable=False, index=True)  # Nome da sala
    facility_type = Column(String(50), nullable=False, default=FacilityType.CONSULTATION_ROOM, index=True)
    description = Column(Text, nullable=True)  # Descrição da sala
    capacity = Column(Integer, nullable=True)  # Capacidade (número de pessoas)
    
    # Localização
    floor = Column(String(50), nullable=True)  # Andar
    wing = Column(String(50), nullable=True)   # Ala
    room_number = Column(String(50), nullable=True)  # Número da sala
    
    # Características
    is_accessible = Column(Boolean, default=True, nullable=False)  # Acessível para PCD
    has_equipment = Column(Boolean, default=False, nullable=False)  # Possui equipamentos
    equipment_description = Column(Text, nullable=True)  # Descrição dos equipamentos
    
    # Relacionamentos
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    company = relationship("Company", backref="facilities")
    
    # Controle
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(String(255), server_default=func.now(), nullable=False)
    updated_at = Column(String(255), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Facility(id={self.id}, name='{self.name}', type='{self.facility_type}')>"
    
    def soft_delete(self):
        """Soft delete facility by setting is_deleted=True"""
        self.is_deleted = True
        self.is_active = False
    
    def restore(self):
        """Restore soft deleted facility"""
        self.is_deleted = False
        self.is_active = True
    
    def deactivate(self):
        """Deactivate facility without deleting"""
        self.is_active = False
    
    def activate(self):
        """Activate facility"""
        self.is_active = True
    
    @property
    def full_name(self):
        """Get full facility name with location"""
        parts = [self.name]
        if self.room_number:
            parts.append(f"Sala {self.room_number}")
        if self.floor:
            parts.append(f"{self.floor}º andar")
        if self.wing:
            parts.append(f"Ala {self.wing}")
        return " - ".join(parts) 