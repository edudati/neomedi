from typing import List, Optional
from datetime import datetime, date, time
from neomediapi.infra.db.models.facility_model import Facility
from neomediapi.infra.db.models.facility_schedule_model import FacilitySchedule
from neomediapi.domain.facility.dtos.facility_dto import (
    FacilityCreateDTO,
    FacilityUpdateDTO,
    FacilityResponseDTO,
    FacilityListResponseDTO,
    FacilityScheduleCreateDTO,
    FacilityScheduleUpdateDTO,
    FacilityScheduleResponseDTO,
    FacilityAvailableSlotDTO,
    FacilityAvailableSlotsResponseDTO
)

class FacilityMapper:
    """Mapper for facility entities"""
    
    @staticmethod
    def to_entity(dto: FacilityCreateDTO) -> Facility:
        """Convert DTO to entity"""
        return Facility(
            name=dto.name,
            facility_type=dto.facility_type,
            description=dto.description,
            capacity=dto.capacity,
            floor=dto.floor,
            wing=dto.wing,
            room_number=dto.room_number,
            is_accessible=dto.is_accessible,
            has_equipment=dto.has_equipment,
            equipment_description=dto.equipment_description,
            company_id=dto.company_id
        )
    
    @staticmethod
    def to_response_dto(entity: Facility) -> FacilityResponseDTO:
        """Convert entity to response DTO"""
        return FacilityResponseDTO(
            id=entity.id,
            name=entity.name,
            facility_type=entity.facility_type,
            description=entity.description,
            capacity=entity.capacity,
            floor=entity.floor,
            wing=entity.wing,
            room_number=entity.room_number,
            is_accessible=entity.is_accessible,
            has_equipment=entity.has_equipment,
            equipment_description=entity.equipment_description,
            company_id=entity.company_id,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    @staticmethod
    def to_list_response_dto(entity: Facility) -> FacilityListResponseDTO:
        """Convert entity to list response DTO"""
        return FacilityListResponseDTO(
            id=entity.id,
            name=entity.name,
            facility_type=entity.facility_type,
            capacity=entity.capacity,
            floor=entity.floor,
            wing=entity.wing,
            room_number=entity.room_number,
            is_accessible=entity.is_accessible,
            has_equipment=entity.has_equipment,
            is_active=entity.is_active,
            created_at=entity.created_at
        )
    
    @staticmethod
    def to_list_response_dtos(entities: List[Facility]) -> List[FacilityListResponseDTO]:
        """Convert list of entities to list response DTOs"""
        return [FacilityMapper.to_list_response_dto(entity) for entity in entities]
    
    @staticmethod
    def update_entity_from_dto(entity: Facility, dto: FacilityUpdateDTO) -> Facility:
        """Update entity from DTO"""
        if dto.name is not None:
            entity.name = dto.name
        if dto.facility_type is not None:
            entity.facility_type = dto.facility_type
        if dto.description is not None:
            entity.description = dto.description
        if dto.capacity is not None:
            entity.capacity = dto.capacity
        if dto.floor is not None:
            entity.floor = dto.floor
        if dto.wing is not None:
            entity.wing = dto.wing
        if dto.room_number is not None:
            entity.room_number = dto.room_number
        if dto.is_accessible is not None:
            entity.is_accessible = dto.is_accessible
        if dto.has_equipment is not None:
            entity.has_equipment = dto.has_equipment
        if dto.equipment_description is not None:
            entity.equipment_description = dto.equipment_description
        
        return entity

class FacilityScheduleMapper:
    """Mapper for facility schedule entities"""
    
    @staticmethod
    def to_entity(dto: FacilityScheduleCreateDTO) -> FacilitySchedule:
        """Convert DTO to entity"""
        return FacilitySchedule(
            facility_id=dto.facility_id,
            day_of_week=dto.day_of_week,
            start_time=dto.start_time,
            end_time=dto.end_time,
            is_available=dto.is_available,
            company_id=dto.company_id
        )
    
    @staticmethod
    def to_response_dto(entity: FacilitySchedule) -> FacilityScheduleResponseDTO:
        """Convert entity to response DTO"""
        return FacilityScheduleResponseDTO(
            id=entity.id,
            facility_id=entity.facility_id,
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
    def to_response_dtos(entities: List[FacilitySchedule]) -> List[FacilityScheduleResponseDTO]:
        """Convert list of entities to response DTOs"""
        return [FacilityScheduleMapper.to_response_dto(entity) for entity in entities]
    
    @staticmethod
    def update_entity_from_dto(entity: FacilitySchedule, dto: FacilityScheduleUpdateDTO) -> FacilitySchedule:
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

class FacilityAvailableSlotMapper:
    """Mapper for facility available slots"""
    
    @staticmethod
    def to_available_slot_dto(
        start_time: datetime,
        end_time: datetime,
        duration_minutes: int,
        facility_id: int,
        facility_name: str
    ) -> FacilityAvailableSlotDTO:
        """Convert slot data to DTO"""
        return FacilityAvailableSlotDTO(
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            facility_id=facility_id,
            facility_name=facility_name
        )
    
    @staticmethod
    def to_available_slots_response_dto(
        date: date,
        facility_id: int,
        facility_name: str,
        slots: List[FacilityAvailableSlotDTO]
    ) -> FacilityAvailableSlotsResponseDTO:
        """Convert slots data to response DTO"""
        return FacilityAvailableSlotsResponseDTO(
            date=date,
            facility_id=facility_id,
            facility_name=facility_name,
            slots=slots
        ) 