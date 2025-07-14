from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, Field
from neomediapi.enums.facility_types import FacilityType

# Base DTOs
class FacilityBaseDTO(BaseModel):
    """Base DTO for facility"""
    name: str = Field(..., min_length=1, max_length=255, description="Nome da sala")
    facility_type: FacilityType = Field(FacilityType.CONSULTATION_ROOM, description="Tipo de instalação")
    description: Optional[str] = Field(None, description="Descrição da sala")
    capacity: Optional[int] = Field(None, ge=1, description="Capacidade (número de pessoas)")
    floor: Optional[str] = Field(None, max_length=50, description="Andar")
    wing: Optional[str] = Field(None, max_length=50, description="Ala")
    room_number: Optional[str] = Field(None, max_length=50, description="Número da sala")
    is_accessible: bool = Field(True, description="Acessível para PCD")
    has_equipment: bool = Field(False, description="Possui equipamentos")
    equipment_description: Optional[str] = Field(None, description="Descrição dos equipamentos")

# Create DTOs
class FacilityCreateDTO(FacilityBaseDTO):
    """DTO for creating facility"""
    company_id: int = Field(..., gt=0, description="ID da empresa")

# Update DTOs
class FacilityUpdateDTO(BaseModel):
    """DTO for updating facility"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Nome da sala")
    facility_type: Optional[FacilityType] = Field(None, description="Tipo de instalação")
    description: Optional[str] = Field(None, description="Descrição da sala")
    capacity: Optional[int] = Field(None, ge=1, description="Capacidade")
    floor: Optional[str] = Field(None, max_length=50, description="Andar")
    wing: Optional[str] = Field(None, max_length=50, description="Ala")
    room_number: Optional[str] = Field(None, max_length=50, description="Número da sala")
    is_accessible: Optional[bool] = Field(None, description="Acessível para PCD")
    has_equipment: Optional[bool] = Field(None, description="Possui equipamentos")
    equipment_description: Optional[str] = Field(None, description="Descrição dos equipamentos")

# Response DTOs
class FacilityResponseDTO(FacilityBaseDTO):
    """DTO for facility response"""
    id: int = Field(..., description="ID da instalação")
    company_id: int = Field(..., description="ID da empresa")
    is_active: bool = Field(..., description="Instalação ativa")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    class Config:
        from_attributes = True

class FacilityListResponseDTO(BaseModel):
    """DTO for facility list response"""
    id: int = Field(..., description="ID da instalação")
    name: str = Field(..., description="Nome da sala")
    facility_type: FacilityType = Field(..., description="Tipo de instalação")
    capacity: Optional[int] = Field(None, description="Capacidade")
    floor: Optional[str] = Field(None, description="Andar")
    wing: Optional[str] = Field(None, description="Ala")
    room_number: Optional[str] = Field(None, description="Número da sala")
    is_accessible: bool = Field(..., description="Acessível para PCD")
    has_equipment: bool = Field(..., description="Possui equipamentos")
    is_active: bool = Field(..., description="Instalação ativa")
    created_at: datetime = Field(..., description="Data de criação")
    
    class Config:
        from_attributes = True

# Search DTOs
class FacilitySearchDTO(BaseModel):
    """DTO for facility search"""
    query: Optional[str] = Field(None, description="Termo de busca")
    facility_type: Optional[FacilityType] = Field(None, description="Tipo de instalação")
    company_id: Optional[int] = Field(None, gt=0, description="ID da empresa")
    is_accessible: Optional[bool] = Field(None, description="Acessível para PCD")
    has_equipment: Optional[bool] = Field(None, description="Possui equipamentos")
    is_active: Optional[bool] = Field(True, description="Instalação ativa")

# Schedule DTOs
class FacilityScheduleBaseDTO(BaseModel):
    """Base DTO for facility schedule"""
    day_of_week: int = Field(..., ge=0, le=6, description="Dia da semana (0=Segunda, 6=Domingo)")
    start_time: time = Field(..., description="Horário de início")
    end_time: time = Field(..., description="Horário de fim")
    is_available: bool = Field(True, description="Disponível")

class FacilityScheduleCreateDTO(FacilityScheduleBaseDTO):
    """DTO for creating facility schedule"""
    facility_id: int = Field(..., gt=0, description="ID da instalação")
    company_id: Optional[int] = Field(None, gt=0, description="ID da empresa")

class FacilityScheduleUpdateDTO(BaseModel):
    """DTO for updating facility schedule"""
    start_time: Optional[time] = Field(None, description="Horário de início")
    end_time: Optional[time] = Field(None, description="Horário de fim")
    is_available: Optional[bool] = Field(None, description="Disponível")
    exception_date: Optional[date] = Field(None, description="Data de exceção")
    exception_start_time: Optional[time] = Field(None, description="Horário de início da exceção")
    exception_end_time: Optional[time] = Field(None, description="Horário de fim da exceção")
    exception_reason: Optional[str] = Field(None, max_length=255, description="Motivo da exceção")

class FacilityScheduleResponseDTO(FacilityScheduleBaseDTO):
    """DTO for facility schedule response"""
    id: int = Field(..., description="ID do horário")
    facility_id: int = Field(..., description="ID da instalação")
    company_id: Optional[int] = Field(None, description="ID da empresa")
    exception_date: Optional[date] = Field(None, description="Data de exceção")
    exception_start_time: Optional[time] = Field(None, description="Horário de início da exceção")
    exception_end_time: Optional[time] = Field(None, description="Horário de fim da exceção")
    exception_reason: Optional[str] = Field(None, description="Motivo da exceção")
    is_active: bool = Field(..., description="Horário ativo")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    class Config:
        from_attributes = True

# Available Slots DTOs
class FacilityAvailableSlotDTO(BaseModel):
    """DTO for available facility slot"""
    start_time: datetime = Field(..., description="Horário de início")
    end_time: datetime = Field(..., description="Horário de fim")
    duration_minutes: int = Field(..., description="Duração em minutos")
    facility_id: int = Field(..., description="ID da instalação")
    facility_name: str = Field(..., description="Nome da instalação")

class FacilityAvailableSlotsResponseDTO(BaseModel):
    """DTO for available facility slots response"""
    date: date = Field(..., description="Data")
    facility_id: int = Field(..., description="ID da instalação")
    facility_name: str = Field(..., description="Nome da instalação")
    slots: List[FacilityAvailableSlotDTO] = Field(..., description="Slots disponíveis") 