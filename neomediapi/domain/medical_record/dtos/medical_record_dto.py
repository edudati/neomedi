from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field
from neomediapi.enums.medical_record_types import MedicalRecordType
from neomediapi.enums.medical_record_status import MedicalRecordStatus

# Base DTOs
class MedicalRecordBaseDTO(BaseModel):
    """Base DTO for medical record"""
    title: str = Field(..., min_length=1, max_length=255, description="Título do prontuário")
    description: Optional[str] = Field(None, description="Descrição detalhada")
    record_type: MedicalRecordType = Field(MedicalRecordType.OTHER, description="Tipo do prontuário")
    consultation_date: Optional[date] = Field(None, description="Data da consulta")
    next_appointment: Optional[date] = Field(None, description="Próxima consulta")
    is_confidential: bool = Field(False, description="Prontuário confidencial")

# Medical Information DTOs
class MedicalInformationDTO(BaseModel):
    """DTO for medical information"""
    chief_complaint: Optional[str] = Field(None, description="Queixa principal")
    present_illness: Optional[str] = Field(None, description="História da doença atual")
    past_medical_history: Optional[str] = Field(None, description="Histórico médico anterior")
    family_history: Optional[str] = Field(None, description="Histórico familiar")
    social_history: Optional[str] = Field(None, description="Histórico social")
    medications: Optional[str] = Field(None, description="Medicamentos em uso")
    allergies: Optional[str] = Field(None, description="Alergias")
    vital_signs: Optional[str] = Field(None, description="Sinais vitais")
    physical_examination: Optional[str] = Field(None, description="Exame físico")
    diagnosis: Optional[str] = Field(None, description="Diagnóstico")
    treatment_plan: Optional[str] = Field(None, description="Plano de tratamento")
    prescriptions: Optional[str] = Field(None, description="Prescrições")
    notes: Optional[str] = Field(None, description="Observações adicionais")

# Create DTOs
class MedicalRecordCreateDTO(MedicalRecordBaseDTO, MedicalInformationDTO):
    """DTO for creating medical record"""
    patient_id: int = Field(..., gt=0, description="ID do paciente")
    professional_id: int = Field(..., gt=0, description="ID do profissional")
    company_id: Optional[int] = Field(None, gt=0, description="ID da empresa")

# Update DTOs
class MedicalRecordUpdateDTO(BaseModel):
    """DTO for updating medical record"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Título do prontuário")
    description: Optional[str] = Field(None, description="Descrição detalhada")
    record_type: Optional[MedicalRecordType] = Field(None, description="Tipo do prontuário")
    status: Optional[MedicalRecordStatus] = Field(None, description="Status do prontuário")
    consultation_date: Optional[date] = Field(None, description="Data da consulta")
    next_appointment: Optional[date] = Field(None, description="Próxima consulta")
    is_confidential: Optional[bool] = Field(None, description="Prontuário confidencial")
    
    # Medical information fields
    chief_complaint: Optional[str] = Field(None, description="Queixa principal")
    present_illness: Optional[str] = Field(None, description="História da doença atual")
    past_medical_history: Optional[str] = Field(None, description="Histórico médico anterior")
    family_history: Optional[str] = Field(None, description="Histórico familiar")
    social_history: Optional[str] = Field(None, description="Histórico social")
    medications: Optional[str] = Field(None, description="Medicamentos em uso")
    allergies: Optional[str] = Field(None, description="Alergias")
    vital_signs: Optional[str] = Field(None, description="Sinais vitais")
    physical_examination: Optional[str] = Field(None, description="Exame físico")
    diagnosis: Optional[str] = Field(None, description="Diagnóstico")
    treatment_plan: Optional[str] = Field(None, description="Plano de tratamento")
    prescriptions: Optional[str] = Field(None, description="Prescrições")
    notes: Optional[str] = Field(None, description="Observações adicionais")

# Response DTOs
class MedicalRecordResponseDTO(MedicalRecordBaseDTO, MedicalInformationDTO):
    """DTO for medical record response"""
    id: int = Field(..., description="ID do prontuário")
    record_number: str = Field(..., description="Número do prontuário")
    status: MedicalRecordStatus = Field(..., description="Status do prontuário")
    patient_id: int = Field(..., description="ID do paciente")
    professional_id: int = Field(..., description="ID do profissional")
    company_id: Optional[int] = Field(None, description="ID da empresa")
    is_active: bool = Field(..., description="Prontuário ativo")
    is_confidential: bool = Field(..., description="Prontuário confidencial")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    class Config:
        from_attributes = True

class MedicalRecordListResponseDTO(BaseModel):
    """DTO for medical record list response"""
    id: int = Field(..., description="ID do prontuário")
    record_number: str = Field(..., description="Número do prontuário")
    title: str = Field(..., description="Título do prontuário")
    record_type: MedicalRecordType = Field(..., description="Tipo do prontuário")
    status: MedicalRecordStatus = Field(..., description="Status do prontuário")
    consultation_date: Optional[date] = Field(None, description="Data da consulta")
    patient_id: int = Field(..., description="ID do paciente")
    professional_id: int = Field(..., description="ID do profissional")
    is_confidential: bool = Field(..., description="Prontuário confidencial")
    created_at: datetime = Field(..., description="Data de criação")
    
    class Config:
        from_attributes = True

# Search and Filter DTOs
class MedicalRecordSearchDTO(BaseModel):
    """DTO for medical record search"""
    query: Optional[str] = Field(None, description="Termo de busca")
    record_type: Optional[MedicalRecordType] = Field(None, description="Tipo do prontuário")
    status: Optional[MedicalRecordStatus] = Field(None, description="Status do prontuário")
    patient_id: Optional[int] = Field(None, gt=0, description="ID do paciente")
    professional_id: Optional[int] = Field(None, gt=0, description="ID do profissional")
    company_id: Optional[int] = Field(None, gt=0, description="ID da empresa")
    consultation_date_from: Optional[date] = Field(None, description="Data da consulta (início)")
    consultation_date_to: Optional[date] = Field(None, description="Data da consulta (fim)")
    is_confidential: Optional[bool] = Field(None, description="Prontuário confidencial")
    is_active: Optional[bool] = Field(True, description="Prontuário ativo")

# Status Update DTOs
class MedicalRecordStatusUpdateDTO(BaseModel):
    """DTO for updating medical record status"""
    status: MedicalRecordStatus = Field(..., description="Novo status do prontuário")

class MedicalRecordConfidentialityUpdateDTO(BaseModel):
    """DTO for updating medical record confidentiality"""
    is_confidential: bool = Field(..., description="Prontuário confidencial") 