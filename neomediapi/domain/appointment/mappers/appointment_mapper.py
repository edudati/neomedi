from typing import List, Optional
from datetime import datetime, date, time
from neomediapi.infra.db.models.appointment_model import Appointment
from neomediapi.infra.db.models.professional_availability_model import ProfessionalAvailability
from neomediapi.domain.appointment.dtos.appointment_dto import (
    AppointmentCreateDTO,
    AppointmentUpdateDTO,
    AppointmentResponseDTO,
    AppointmentListResponseDTO,
    ProfessionalAvailabilityCreateDTO,
    ProfessionalAvailabilityUpdateDTO,
    ProfessionalAvailabilityResponseDTO,
    AvailableSlotDTO,
    AvailableSlotsResponseDTO
)

class AppointmentMapper:
    """Mapper for appointment entities"""
    
    @staticmethod
    def to_entity(dto: AppointmentCreateDTO) -> Appointment:
        """Convert DTO to entity"""
        return Appointment(
            title=dto.title,
            appointment_date=dto.appointment_date,
            duration_minutes=dto.duration_minutes,
            appointment_type=dto.appointment_type,
            notes=dto.notes,
            location=dto.location,
            description=dto.description,
            patient_id=dto.patient_id,
            professional_id=dto.professional_id,
            company_id=dto.company_id,
            facility_id=dto.facility_id
        )
    
    @staticmethod
    def to_response_dto(entity: Appointment) -> AppointmentResponseDTO:
        """Convert entity to response DTO"""
        return AppointmentResponseDTO(
            id=entity.id,
            title=entity.title,
            appointment_date=entity.appointment_date,
            duration_minutes=entity.duration_minutes,
            appointment_type=entity.appointment_type,
            status=entity.status,
            notes=entity.notes,
            location=entity.location,
            description=entity.description,
            patient_id=entity.patient_id,
            professional_id=entity.professional_id,
            company_id=entity.company_id,
            medical_record_id=entity.medical_record_id,
            facility_id=entity.facility_id,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    @staticmethod
    def to_list_response_dto(entity: Appointment) -> AppointmentListResponseDTO:
        """Convert entity to list response DTO"""
        return AppointmentListResponseDTO(
            id=entity.id,
            title=entity.title,
            appointment_date=entity.appointment_date,
            duration_minutes=entity.duration_minutes,
            appointment_type=entity.appointment_type,
            status=entity.status,
            patient_id=entity.patient_id,
            professional_id=entity.professional_id,
            facility_id=entity.facility_id,
            location=entity.location,
            created_at=entity.created_at
        )
    
    @staticmethod
    def to_list_response_dtos(entities: List[Appointment]) -> List[AppointmentListResponseDTO]:
        """Convert list of entities to list response DTOs"""
        return [AppointmentMapper.to_list_response_dto(entity) for entity in entities]
    
    @staticmethod
    def update_entity_from_dto(entity: Appointment, dto: AppointmentUpdateDTO) -> Appointment:
        """Update entity from DTO"""
        if dto.title is not None:
            entity.title = dto.title
        if dto.appointment_date is not None:
            entity.appointment_date = dto.appointment_date
        if dto.duration_minutes is not None:
            entity.duration_minutes = dto.duration_minutes
        if dto.appointment_type is not None:
            entity.appointment_type = dto.appointment_type
        if dto.status is not None:
            entity.status = dto.status
        if dto.notes is not None:
            entity.notes = dto.notes
        if dto.location is not None:
            entity.location = dto.location
        if dto.description is not None:
            entity.description = dto.description
        
        return entity

class ProfessionalAvailabilityMapper:
    """Mapper for professional availability entities"""
    
    @staticmethod
    def to_entity(dto: ProfessionalAvailabilityCreateDTO) -> ProfessionalAvailability:
        """Convert DTO to entity"""
        return ProfessionalAvailability(
            professional_id=dto.professional_id,
            day_of_week=dto.day_of_week,
            start_time=dto.start_time,
            end_time=dto.end_time,
            is_available=dto.is_available,
            company_id=dto.company_id
        )
    
    @staticmethod
    def to_response_dto(entity: ProfessionalAvailability) -> ProfessionalAvailabilityResponseDTO:
        """Convert entity to response DTO"""
        return ProfessionalAvailabilityResponseDTO(
            id=entity.id,
            professional_id=entity.professional_id,
            day_of_week=entity.day_of_week,
            start_time=entity.start_time,
            end_time=entity.end_time,
            is_available=entity.is_available,
            company_id=entity.company_id,
            exception_date=entity.exception_date,
            exception_start_time=entity.exception_start_time,
            exception_end_time=entity.exception_end_time,
            exception_reason=entity.exception_reason,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    @staticmethod
    def to_response_dtos(entities: List[ProfessionalAvailability]) -> List[ProfessionalAvailabilityResponseDTO]:
        """Convert list of entities to response DTOs"""
        return [ProfessionalAvailabilityMapper.to_response_dto(entity) for entity in entities]
    
    @staticmethod
    def update_entity_from_dto(entity: ProfessionalAvailability, dto: ProfessionalAvailabilityUpdateDTO) -> ProfessionalAvailability:
        """Update entity from DTO"""
        if dto.start_time is not None:
            entity.start_time = dto.start_time
        if dto.end_time is not None:
            entity.end_time = dto.end_time
        if dto.is_available is not None:
            entity.is_available = dto.is_available
        if dto.exception_date is not None:
            entity.exception_date = dto.exception_date
        if dto.exception_start_time is not None:
            entity.exception_start_time = dto.exception_start_time
        if dto.exception_end_time is not None:
            entity.exception_end_time = dto.exception_end_time
        if dto.exception_reason is not None:
            entity.exception_reason = dto.exception_reason
        
        return entity

class AvailableSlotMapper:
    """Mapper for available slots"""
    
    @staticmethod
    def to_available_slot_dto(
        start_time: datetime,
        end_time: datetime,
        duration_minutes: int,
        professional_id: int
    ) -> AvailableSlotDTO:
        """Convert slot data to DTO"""
        return AvailableSlotDTO(
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            professional_id=professional_id
        )
    
    @staticmethod
    def to_available_slots_response_dto(
        date: date,
        professional_id: int,
        slots: List[AvailableSlotDTO]
    ) -> AvailableSlotsResponseDTO:
        """Convert slots data to response DTO"""
        return AvailableSlotsResponseDTO(
            date=date,
            professional_id=professional_id,
            slots=slots
        ) 