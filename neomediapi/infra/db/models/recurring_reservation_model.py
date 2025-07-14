from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func, Date
from sqlalchemy.orm import relationship
from neomediapi.infra.db.base_class import Base

class RecurringReservation(Base):
    __tablename__ = "recurring_reservations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Dados básicos
    title = Column(String(255), nullable=False, index=True)  # Título da reserva
    description = Column(String(500), nullable=True)  # Descrição
    
    # Configuração de recorrência
    day_of_week = Column(Integer, nullable=False, index=True)  # 0=Segunda, 1=Terça, 2=Quarta, 3=Quinta, 4=Sexta, 5=Sábado, 6=Domingo
    start_time = Column(String(10), nullable=False)  # Horário de início (HH:MM)
    end_time = Column(String(10), nullable=False)    # Horário de fim (HH:MM)
    duration_minutes = Column(Integer, default=60, nullable=False)  # Duração em minutos
    
    # Período de validade
    start_date = Column(Date, nullable=False, index=True)  # Data de início da recorrência
    end_date = Column(Date, nullable=True, index=True)     # Data de fim (opcional, se None = sem fim)
    
    # Relacionamentos
    professional_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    professional = relationship("User", foreign_keys=[professional_id], backref="recurring_reservations")
    
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False, index=True)
    facility = relationship("Facility", backref="recurring_reservations")
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    company = relationship("Company", backref="recurring_reservations")
    
    # Controle
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<RecurringReservation(id={self.id}, title='{self.title}', day={self.day_of_week})>"
    
    def soft_delete(self):
        """Soft delete reservation by setting is_deleted=True"""
        self.is_deleted = True
        self.is_active = False
    
    def restore(self):
        """Restore soft deleted reservation"""
        self.is_deleted = False
        self.is_active = True
    
    def deactivate(self):
        """Deactivate reservation without deleting"""
        self.is_active = False
    
    def activate(self):
        """Activate reservation"""
        self.is_active = True
    
    def is_expired(self, current_date: Date) -> bool:
        """Check if reservation is expired"""
        if self.end_date is None:
            return False
        return current_date > self.end_date
    
    def is_valid_for_date(self, target_date: Date) -> bool:
        """Check if reservation is valid for a specific date"""
        if target_date < self.start_date:
            return False
        if self.end_date and target_date > self.end_date:
            return False
        return target_date.weekday() == self.day_of_week 