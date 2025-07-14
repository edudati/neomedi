from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, Field
from neomediapi.enums.appointment_types import AppointmentType
from neomediapi.enums.appointment_status import AppointmentStatus

# Base DTOs
class AppointmentBaseDTO(BaseModel):
    """Base DTO for appointment"""
    title: str = Field(..., min_length=1, max_length=255, description="Título do agendamento")
    appointment_date: datetime = Field(..., description="Data e hora do agendamento")
    duration_minutes: int = Field(60, ge=15, le=480, description="Duração em minutos (15-480)")
    appointment_type: AppointmentType = Field(AppointmentType.CONSULTATION, description="Tipo do agendamento")
    notes: Optional[str] = Field(None, description="Observações")
    location: Optional[str] = Field(None, max_length=255, description="Local da consulta")
    description: Optional[str] = Field(None, description="Descrição detalhada")

# Create DTOs
class AppointmentCreateDTO(AppointmentBaseDTO):
    """DTO for creating appointment"""
    patient_id: int = Field(..., gt=0, description="ID do paciente")
    professional_id: int = Field(..., gt=0, description="ID do profissional")
    company_id: Optional[int] = Field(None, gt=0, description="ID da empresa")
    facility_id: Optional[int] = Field(None, gt=0, description="ID da instalação")

# Update DTOs
class AppointmentUpdateDTO(BaseModel):
    """DTO for updating appointment"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Título do agendamento")
    appointment_date: Optional[datetime] = Field(None, description="Data e hora do agendamento")
    duration_minutes: Optional[int] = Field(None, ge=15, le=480, description="Duração em minutos")
    appointment_type: Optional[AppointmentType] = Field(None, description="Tipo do agendamento")
    status: Optional[AppointmentStatus] = Field(None, description="Status do agendamento")
    notes: Optional[str] = Field(None, description="Observações")
    location: Optional[str] = Field(None, max_length=255, description="Local da consulta")
    description: Optional[str] = Field(None, description="Descrição detalhada")
    facility_id: Optional[int] = Field(None, gt=0, description="ID da instalação")

# Response DTOs
class AppointmentResponseDTO(AppointmentBaseDTO):
    """DTO for appointment response"""
    id: int = Field(..., description="ID do agendamento")
    status: AppointmentStatus = Field(..., description="Status do agendamento")
    patient_id: int = Field(..., description="ID do paciente")
    professional_id: int = Field(..., description="ID do profissional")
    company_id: Optional[int] = Field(None, description="ID da empresa")
    medical_record_id: Optional[int] = Field(None, description="ID do prontuário")
    facility_id: Optional[int] = Field(None, description="ID da instalação")
    is_active: bool = Field(..., description="Agendamento ativo")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    class Config:
        from_attributes = True

class AppointmentListResponseDTO(BaseModel):
    """DTO for appointment list response"""
    id: int = Field(..., description="ID do agendamento")
    title: str = Field(..., description="Título do agendamento")
    appointment_date: datetime = Field(..., description="Data e hora do agendamento")
    duration_minutes: int = Field(..., description="Duração em minutos")
    appointment_type: AppointmentType = Field(..., description="Tipo do agendamento")
    status: AppointmentStatus = Field(..., description="Status do agendamento")
    patient_id: int = Field(..., description="ID do paciente")
    professional_id: int = Field(..., description="ID do profissional")
    facility_id: Optional[int] = Field(None, description="ID da instalação")
    location: Optional[str] = Field(None, description="Local da consulta")
    created_at: datetime = Field(..., description="Data de criação")
    
    class Config:
        from_attributes = True

# Search and Filter DTOs
class AppointmentSearchDTO(BaseModel):
    """DTO for appointment search"""
    query: Optional[str] = Field(None, description="Termo de busca")
    appointment_type: Optional[AppointmentType] = Field(None, description="Tipo do agendamento")
    status: Optional[AppointmentStatus] = Field(None, description="Status do agendamento")
    patient_id: Optional[int] = Field(None, gt=0, description="ID do paciente")
    professional_id: Optional[int] = Field(None, gt=0, description="ID do profissional")
    company_id: Optional[int] = Field(None, gt=0, description="ID da empresa")
    facility_id: Optional[int] = Field(None, gt=0, description="ID da instalação")
    date_from: Optional[date] = Field(None, description="Data de início")
    date_to: Optional[date] = Field(None, description="Data de fim")
    is_active: Optional[bool] = Field(True, description="Agendamento ativo")

# Status Update DTOs
class AppointmentStatusUpdateDTO(BaseModel):
    """DTO for updating appointment status"""
    status: AppointmentStatus = Field(..., description="Novo status do agendamento")

# Availability DTOs
class ProfessionalAvailabilityBaseDTO(BaseModel):
    """Base DTO for professional availability"""
    day_of_week: int = Field(..., ge=0, le=6, description="Dia da semana (0=Segunda, 6=Domingo)")
    start_time: time = Field(..., description="Horário de início")
    end_time: time = Field(..., description="Horário de fim")
    is_available: bool = Field(True, description="Disponível")

class ProfessionalAvailabilityCreateDTO(ProfessionalAvailabilityBaseDTO):
    """DTO for creating professional availability"""
    professional_id: int = Field(..., gt=0, description="ID do profissional")
    company_id: Optional[int] = Field(None, gt=0, description="ID da empresa")

class ProfessionalAvailabilityUpdateDTO(BaseModel):
    """DTO for updating professional availability"""
    start_time: Optional[time] = Field(None, description="Horário de início")
    end_time: Optional[time] = Field(None, description="Horário de fim")
    is_available: Optional[bool] = Field(None, description="Disponível")
    exception_date: Optional[date] = Field(None, description="Data de exceção")
    exception_start_time: Optional[time] = Field(None, description="Horário de início da exceção")
    exception_end_time: Optional[time] = Field(None, description="Horário de fim da exceção")
    exception_reason: Optional[str] = Field(None, max_length=255, description="Motivo da exceção")

class ProfessionalAvailabilityResponseDTO(ProfessionalAvailabilityBaseDTO):
    """DTO for professional availability response"""
    id: int = Field(..., description="ID da disponibilidade")
    professional_id: int = Field(..., description="ID do profissional")
    company_id: Optional[int] = Field(None, description="ID da empresa")
    exception_date: Optional[date] = Field(None, description="Data de exceção")
    exception_start_time: Optional[time] = Field(None, description="Horário de início da exceção")
    exception_end_time: Optional[time] = Field(None, description="Horário de fim da exceção")
    exception_reason: Optional[str] = Field(None, description="Motivo da exceção")
    is_active: bool = Field(..., description="Disponibilidade ativa")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    class Config:
        from_attributes = True

# Available Slots DTOs
class AvailableSlotDTO(BaseModel):
    """DTO for available time slot"""
    start_time: datetime = Field(..., description="Horário de início")
    end_time: datetime = Field(..., description="Horário de fim")
    duration_minutes: int = Field(..., description="Duração em minutos")
    professional_id: int = Field(..., description="ID do profissional")

class AvailableSlotsResponseDTO(BaseModel):
    """DTO for available slots response"""
    date: date = Field(..., description="Data")
    professional_id: int = Field(..., description="ID do profissional")
    slots: List[AvailableSlotDTO] = Field(..., description="Slots disponíveis") 