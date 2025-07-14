from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func, Time, Date
from sqlalchemy.orm import relationship
from neomediapi.infra.db.base_class import Base

class ProfessionalAvailability(Base):
    __tablename__ = "professional_availabilities"

    id = Column(Integer, primary_key=True, index=True)
    
    # Dados de disponibilidade
    professional_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    professional = relationship("User", backref="availabilities")
    
    # Disponibilidade regular (semanal)
    day_of_week = Column(Integer, nullable=False, index=True)  # 0=Segunda, 1=Terça, 2=Quarta, 3=Quinta, 4=Sexta, 5=Sábado, 6=Domingo
    start_time = Column(Time, nullable=False)  # Horário de início (ex: 09:00)
    end_time = Column(Time, nullable=False)    # Horário de fim (ex: 17:00)
    is_available = Column(Boolean, default=True, nullable=False, index=True)
    
    # Exceções (feriados, férias, etc.)
    exception_date = Column(Date, nullable=True, index=True)  # Data específica de exceção
    exception_start_time = Column(Time, nullable=True)  # Horário de início da exceção
    exception_end_time = Column(Time, nullable=True)    # Horário de fim da exceção
    exception_reason = Column(String(255), nullable=True)  # Motivo da exceção (férias, feriado, etc.)
    
    # Relacionamento com empresa (opcional)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    company = relationship("Company", backref="professional_availabilities")
    
    # Controle
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<ProfessionalAvailability(id={self.id}, professional_id={self.professional_id}, day={self.day_of_week})>"
    
    def soft_delete(self):
        """Soft delete availability by setting is_deleted=True"""
        self.is_deleted = True
        self.is_active = False
    
    def restore(self):
        """Restore soft deleted availability"""
        self.is_deleted = False
        self.is_active = True
    
    def deactivate(self):
        """Deactivate availability without deleting"""
        self.is_active = False
    
    def activate(self):
        """Activate availability"""
        self.is_active = True
    
    @property
    def day_name(self):
        """Get day name in Portuguese"""
        days = {
            0: "Segunda-feira",
            1: "Terça-feira", 
            2: "Quarta-feira",
            3: "Quinta-feira",
            4: "Sexta-feira",
            5: "Sábado",
            6: "Domingo"
        }
        return days.get(self.day_of_week, "Desconhecido")
    
    @property
    def duration_hours(self):
        """Calculate duration in hours"""
        if self.start_time and self.end_time:
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute
            return (end_minutes - start_minutes) / 60
        return 0 