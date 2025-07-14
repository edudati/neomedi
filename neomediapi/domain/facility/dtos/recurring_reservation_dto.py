from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field

# Base DTOs
class RecurringReservationBaseDTO(BaseModel):
    """Base DTO for recurring reservation"""
    title: str = Field(..., min_length=1, max_length=255, description="Título da reserva")
    description: Optional[str] = Field(None, max_length=500, description="Descrição")
    day_of_week: int = Field(..., ge=0, le=6, description="Dia da semana (0=Segunda, 6=Domingo)")
    start_time: str = Field(..., description="Horário de início (HH:MM)")
    end_time: str = Field(..., description="Horário de fim (HH:MM)")
    duration_minutes: int = Field(60, ge=15, le=480, description="Duração em minutos")
    start_date: date = Field(..., description="Data de início da recorrência")
    end_date: Optional[date] = Field(None, description="Data de fim (opcional)")

# Create DTOs
class RecurringReservationCreateDTO(RecurringReservationBaseDTO):
    """DTO for creating recurring reservation"""
    professional_id: int = Field(..., gt=0, description="ID do profissional")
    facility_id: int = Field(..., gt=0, description="ID da instalação")
    company_id: Optional[int] = Field(None, gt=0, description="ID da empresa")

# Update DTOs
class RecurringReservationUpdateDTO(BaseModel):
    """DTO for updating recurring reservation"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Título da reserva")
    description: Optional[str] = Field(None, max_length=500, description="Descrição")
    day_of_week: Optional[int] = Field(None, ge=0, le=6, description="Dia da semana")
    start_time: Optional[str] = Field(None, description="Horário de início (HH:MM)")
    end_time: Optional[str] = Field(None, description="Horário de fim (HH:MM)")
    duration_minutes: Optional[int] = Field(None, ge=15, le=480, description="Duração em minutos")
    start_date: Optional[date] = Field(None, description="Data de início da recorrência")
    end_date: Optional[date] = Field(None, description="Data de fim")
    is_active: Optional[bool] = Field(None, description="Reserva ativa")

# Response DTOs
class RecurringReservationResponseDTO(RecurringReservationBaseDTO):
    """DTO for recurring reservation response"""
    id: int = Field(..., description="ID da reserva")
    professional_id: int = Field(..., description="ID do profissional")
    facility_id: int = Field(..., description="ID da instalação")
    company_id: Optional[int] = Field(None, description="ID da empresa")
    is_active: bool = Field(..., description="Reserva ativa")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    class Config:
        from_attributes = True

class RecurringReservationListResponseDTO(BaseModel):
    """DTO for recurring reservation list response"""
    id: int = Field(..., description="ID da reserva")
    title: str = Field(..., description="Título da reserva")
    day_of_week: int = Field(..., description="Dia da semana")
    start_time: str = Field(..., description="Horário de início")
    end_time: str = Field(..., description="Horário de fim")
    duration_minutes: int = Field(..., description="Duração em minutos")
    start_date: date = Field(..., description="Data de início")
    end_date: Optional[date] = Field(None, description="Data de fim")
    professional_id: int = Field(..., description="ID do profissional")
    facility_id: int = Field(..., description="ID da instalação")
    is_active: bool = Field(..., description="Reserva ativa")
    created_at: datetime = Field(..., description="Data de criação")
    
    class Config:
        from_attributes = True

# Search DTOs
class RecurringReservationSearchDTO(BaseModel):
    """DTO for recurring reservation search"""
    query: Optional[str] = Field(None, description="Termo de busca")
    professional_id: Optional[int] = Field(None, gt=0, description="ID do profissional")
    facility_id: Optional[int] = Field(None, gt=0, description="ID da instalação")
    company_id: Optional[int] = Field(None, gt=0, description="ID da empresa")
    day_of_week: Optional[int] = Field(None, ge=0, le=6, description="Dia da semana")
    is_active: Optional[bool] = Field(True, description="Reserva ativa")

# Generated Appointments DTOs
class GeneratedAppointmentDTO(BaseModel):
    """DTO for generated appointment from recurring reservation"""
    appointment_date: datetime = Field(..., description="Data e hora do agendamento")
    title: str = Field(..., description="Título do agendamento")
    professional_id: int = Field(..., description="ID do profissional")
    facility_id: int = Field(..., description="ID da instalação")
    duration_minutes: int = Field(..., description="Duração em minutos")

class RecurringReservationGenerationDTO(BaseModel):
    """DTO for generating appointments from recurring reservation"""
    start_date: date = Field(..., description="Data de início para geração")
    end_date: date = Field(..., description="Data de fim para geração")
    create_appointments: bool = Field(True, description="Criar agendamentos automaticamente")

class RecurringReservationGenerationResponseDTO(BaseModel):
    """DTO for recurring reservation generation response"""
    reservation_id: int = Field(..., description="ID da reserva recorrente")
    generated_appointments: List[GeneratedAppointmentDTO] = Field(..., description="Agendamentos gerados")
    total_generated: int = Field(..., description="Total de agendamentos gerados")
    conflicts: List[str] = Field(..., description="Conflitos encontrados") 