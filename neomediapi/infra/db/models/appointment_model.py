from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func, Text, Time, Date
from sqlalchemy.orm import relationship
from neomediapi.infra.db.base_class import Base
from neomediapi.enums.appointment_types import AppointmentType
from neomediapi.enums.appointment_status import AppointmentStatus

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    
    # Dados básicos
    title = Column(String(255), nullable=False, index=True)  # Título do agendamento
    appointment_date = Column(DateTime, nullable=False, index=True)  # Data e hora
    duration_minutes = Column(Integer, default=60, nullable=False)  # Duração em minutos
    appointment_type = Column(String(50), nullable=False, default=AppointmentType.CONSULTATION, index=True)
    status = Column(String(50), nullable=False, default=AppointmentStatus.SCHEDULED, index=True)
    
    # Dados adicionais
    notes = Column(Text, nullable=True)  # Observações
    location = Column(String(255), nullable=True)  # Local da consulta
    description = Column(Text, nullable=True)  # Descrição detalhada
    
    # Relacionamentos
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    patient = relationship("User", foreign_keys=[patient_id], backref="appointments_as_patient")
    
    professional_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    professional = relationship("User", foreign_keys=[professional_id], backref="appointments_as_professional")
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    company = relationship("Company", backref="appointments")
    
    # Relacionamento com prontuário (opcional)
    medical_record_id = Column(Integer, ForeignKey("medical_records.id"), nullable=True, index=True)
    medical_record = relationship("MedicalRecord", backref="appointments")
    
    # Relacionamento com instalação (opcional)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=True, index=True)
    facility = relationship("Facility", backref="appointments")
    
    # Controle
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, title='{self.title}', date='{self.appointment_date}')>"
    
    def soft_delete(self):
        """Soft delete appointment by setting is_deleted=True"""
        self.is_deleted = True
        self.is_active = False
    
    def restore(self):
        """Restore soft deleted appointment"""
        self.is_deleted = False
        self.is_active = True
    
    def deactivate(self):
        """Deactivate appointment without deleting"""
        self.is_active = False
    
    def activate(self):
        """Activate appointment"""
        self.is_active = True
    

    
    def is_confirmed(self):
        """Check if appointment is confirmed"""
        return self.status in [AppointmentStatus.CONFIRMED, AppointmentStatus.IN_PROGRESS, AppointmentStatus.WAITING]
    
    def is_completed(self):
        """Check if appointment is completed"""
        return self.status in [AppointmentStatus.COMPLETED, AppointmentStatus.FINISHED]
    
    def is_cancelled(self):
        """Check if appointment is cancelled"""
        return self.status in [AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW] 