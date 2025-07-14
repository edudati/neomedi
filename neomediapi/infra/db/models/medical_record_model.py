from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func, Text, Date
from sqlalchemy.orm import relationship
from neomediapi.infra.db.base_class import Base
from neomediapi.enums.medical_record_types import MedicalRecordType
from neomediapi.enums.medical_record_status import MedicalRecordStatus

class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    record_number = Column(String(50), nullable=False, unique=True, index=True)  # Número do prontuário
    title = Column(String(255), nullable=False, index=True)  # Título do prontuário
    description = Column(Text, nullable=True)  # Descrição detalhada
    
    # Medical information
    chief_complaint = Column(Text, nullable=True)  # Queixa principal
    present_illness = Column(Text, nullable=True)  # História da doença atual
    past_medical_history = Column(Text, nullable=True)  # Histórico médico anterior
    family_history = Column(Text, nullable=True)  # Histórico familiar
    social_history = Column(Text, nullable=True)  # Histórico social
    medications = Column(Text, nullable=True)  # Medicamentos em uso
    allergies = Column(Text, nullable=True)  # Alergias
    vital_signs = Column(Text, nullable=True)  # Sinais vitais
    physical_examination = Column(Text, nullable=True)  # Exame físico
    diagnosis = Column(Text, nullable=True)  # Diagnóstico
    treatment_plan = Column(Text, nullable=True)  # Plano de tratamento
    prescriptions = Column(Text, nullable=True)  # Prescrições
    notes = Column(Text, nullable=True)  # Observações adicionais
    
    # Record details
    record_type = Column(String(50), nullable=False, default=MedicalRecordType.OTHER, index=True)
    status = Column(String(50), nullable=False, default=MedicalRecordStatus.DRAFT, index=True)
    consultation_date = Column(Date, nullable=True, index=True)  # Data da consulta
    next_appointment = Column(Date, nullable=True, index=True)  # Próxima consulta
    
    # Relationships
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    patient = relationship("User", foreign_keys=[patient_id], backref="medical_records")
    
    professional_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    professional = relationship("User", foreign_keys=[professional_id], backref="created_medical_records")
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    company = relationship("Company", backref="medical_records")
    
    # Control fields
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    is_confidential = Column(Boolean, default=False, nullable=False, index=True)  # Prontuário confidencial
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<MedicalRecord(id={self.id}, record_number='{self.record_number}', patient_id={self.patient_id})>"
    
    def soft_delete(self):
        """Soft delete medical record by setting is_deleted=True"""
        self.is_deleted = True
        self.is_active = False
    
    def restore(self):
        """Restore soft deleted medical record"""
        self.is_deleted = False
        self.is_active = True
    
    def deactivate(self):
        """Deactivate medical record without deleting"""
        self.is_active = False
    
    def activate(self):
        """Activate medical record"""
        self.is_active = True
    
    def mark_as_confidential(self):
        """Mark medical record as confidential"""
        self.is_confidential = True
    
    def mark_as_public(self):
        """Mark medical record as public"""
        self.is_confidential = False 