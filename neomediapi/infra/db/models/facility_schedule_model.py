from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func, Time, Date
from sqlalchemy.orm import relationship
from neomediapi.infra.db.base_class import Base

class FacilitySchedule(Base):
    __tablename__ = "facility_schedules"

    id = Column(Integer, primary_key=True, index=True)
    
    # Dados de horário
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False, index=True)
    facility = relationship("Facility", backref="schedules")
    
    # Horário regular (semanal)
    day_of_week = Column(Integer, nullable=False, index=True)  # 0=Segunda, 1=Terça, 2=Quarta, 3=Quinta, 4=Sexta, 5=Sábado, 6=Domingo
    start_time = Column(Time, nullable=False)  # Horário de início (ex: 08:00)
    end_time = Column(Time, nullable=False)    # Horário de fim (ex: 18:00)
    is_available = Column(Boolean, default=True, nullable=False, index=True)
    
    # Exceções (feriados, manutenção, etc.)
    exception_date = Column(Date, nullable=True, index=True)  # Data específica de exceção
    exception_start_time = Column(Time, nullable=True)  # Horário de início da exceção
    exception_end_time = Column(Time, nullable=True)    # Horário de fim da exceção
    exception_reason = Column(String(255), nullable=True)  # Motivo da exceção
    
    # Relacionamento com empresa
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    company = relationship("Company", backref="facility_schedules")
    
    # Controle
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<FacilitySchedule(id={self.id}, facility_id={self.facility_id}, day={self.day_of_week})>"
    
    def soft_delete(self):
        """Soft delete schedule by setting is_deleted=True"""
        self.is_deleted = True
        self.is_active = False
    
    def restore(self):
        """Restore soft deleted schedule"""
        self.is_deleted = False
        self.is_active = True
    
    def deactivate(self):
        """Deactivate schedule without deleting"""
        self.is_active = False
    
    def activate(self):
        """Activate schedule"""
        self.is_active = True 