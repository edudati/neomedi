from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from neomediapi.infra.db.repositories.facility_repository import FacilityRepository, FacilityScheduleRepository
from neomediapi.infra.db.repositories.user_repository import UserRepository
from neomediapi.domain.facility.dtos.facility_dto import (
    FacilityCreateDTO,
    FacilityUpdateDTO,
    FacilitySearchDTO,
    FacilityScheduleCreateDTO,
    FacilityScheduleUpdateDTO,
    FacilityAvailableSlotsResponseDTO,
    FacilityAvailableSlotDTO
)
from neomediapi.domain.facility.mappers.facility_mapper import (
    FacilityMapper,
    FacilityScheduleMapper,
    FacilityAvailableSlotMapper
)
from neomediapi.domain.facility.exceptions import (
    FacilityNotFoundError,
    FacilityAlreadyExistsError,
    FacilityPermissionError,
    FacilityScheduleNotFoundError,
    FacilityScheduleConflictError,
    FacilityScheduleInvalidTimeError,
    NoAvailableFacilitySlotsError,
    FacilityOccupiedError
)
from neomediapi.enums.user_profiles import UserProfile
from neomediapi.auth.authenticated_user import AuthenticatedUser

class FacilityService:
    """Service for facility operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.facility_repo = FacilityRepository(db)
        self.schedule_repo = FacilityScheduleRepository(db)
        self.user_repo = UserRepository(db)
    
    def create_facility(self, facility_dto: FacilityCreateDTO, current_user: AuthenticatedUser) -> dict:
        """Create new facility"""
        # Validate permissions
        self._validate_facility_permissions(current_user, facility_dto.company_id, "criar")
        
        # Check if facility already exists with same name in company
        existing = self.facility_repo.get_by_name_and_company(facility_dto.name, facility_dto.company_id)
        if existing:
            raise FacilityAlreadyExistsError(facility_dto.name, facility_dto.company_id)
        
        # Create facility
        facility = FacilityMapper.to_entity(facility_dto)
        created_facility = self.facility_repo.create(facility)
        
        return FacilityMapper.to_response_dto(created_facility).model_dump()
    
    def get_facility(self, facility_id: int, current_user: AuthenticatedUser) -> dict:
        """Get facility by ID"""
        facility = self.facility_repo.get_by_id_with_relations(facility_id)
        if not facility:
            raise FacilityNotFoundError(facility_id)
        
        # Validate permissions
        self._validate_facility_permissions(current_user, facility.company_id, "visualizar")
        
        return FacilityMapper.to_response_dto(facility).model_dump()
    
    def get_facilities(
        self, 
        search_dto: FacilitySearchDTO, 
        current_user: AuthenticatedUser,
        skip: int = 0, 
        limit: int = 100
    ) -> dict:
        """Get facilities with search and filters"""
        # Apply user-based filters based on profile
        if current_user.profile == UserProfile.MANAGER:
            # Managers can only see facilities from their company
            if current_user.company_id:
                search_dto.company_id = current_user.company_id
        elif current_user.profile == UserProfile.PROFESSIONAL:
            # Professionals can see facilities from their company
            if current_user.company_id:
                search_dto.company_id = current_user.company_id
        elif current_user.profile == UserProfile.ADMIN:
            # Admins can see all facilities
            pass
        else:
            # Patients cannot access facilities directly
            return {"facilities": [], "total": 0, "skip": skip, "limit": limit}
        
        facilities = self.facility_repo.search(search_dto, skip, limit)
        facility_dtos = FacilityMapper.to_list_response_dtos(facilities)
        
        return {
            "facilities": [dto.model_dump() for dto in facility_dtos],
            "total": len(facility_dtos),
            "skip": skip,
            "limit": limit
        }
    
    def update_facility(
        self, 
        facility_id: int, 
        update_dto: FacilityUpdateDTO, 
        current_user: AuthenticatedUser
    ) -> dict:
        """Update facility"""
        facility = self.facility_repo.get_by_id(facility_id)
        if not facility:
            raise FacilityNotFoundError(facility_id)
        
        # Validate permissions
        self._validate_facility_permissions(current_user, facility.company_id, "editar")
        
        # Check name uniqueness if name is being updated
        if update_dto.name and update_dto.name != facility.name:
            existing = self.facility_repo.get_by_name_and_company(update_dto.name, facility.company_id)
            if existing:
                raise FacilityAlreadyExistsError(update_dto.name, facility.company_id)
        
        # Update facility
        updated_facility = FacilityMapper.update_entity_from_dto(facility, update_dto)
        saved_facility = self.facility_repo.update(updated_facility)
        
        return FacilityMapper.to_response_dto(saved_facility).model_dump()
    
    def delete_facility(self, facility_id: int, current_user: AuthenticatedUser) -> bool:
        """Delete facility"""
        facility = self.facility_repo.get_by_id(facility_id)
        if not facility:
            raise FacilityNotFoundError(facility_id)
        
        # Validate permissions
        self._validate_facility_permissions(current_user, facility.company_id, "excluir")
        
        return self.facility_repo.delete(facility_id)
    
    def create_facility_schedule(
        self, 
        schedule_dto: FacilityScheduleCreateDTO, 
        current_user: AuthenticatedUser
    ) -> dict:
        """Create facility schedule"""
        # Get facility to validate company
        facility = self.facility_repo.get_by_id(schedule_dto.facility_id)
        if not facility:
            raise FacilityNotFoundError(schedule_dto.facility_id)
        
        # Validate permissions
        self._validate_facility_permissions(current_user, facility.company_id, "criar horário")
        
        # Validate time range
        if schedule_dto.start_time >= schedule_dto.end_time:
            raise FacilityScheduleInvalidTimeError(
                str(schedule_dto.start_time), 
                str(schedule_dto.end_time)
            )
        
        # Check for conflicts
        existing = self.schedule_repo.get_by_facility_and_day(
            schedule_dto.facility_id, 
            schedule_dto.day_of_week
        )
        if existing:
            raise FacilityScheduleConflictError(
                schedule_dto.facility_id, 
                schedule_dto.day_of_week
            )
        
        # Create schedule
        schedule = FacilityScheduleMapper.to_entity(schedule_dto)
        created_schedule = self.schedule_repo.create(schedule)
        
        return FacilityScheduleMapper.to_response_dto(created_schedule).model_dump()
    
    def get_facility_schedules(
        self, 
        facility_id: int, 
        current_user: AuthenticatedUser
    ) -> dict:
        """Get facility schedules"""
        # Get facility to validate company
        facility = self.facility_repo.get_by_id(facility_id)
        if not facility:
            raise FacilityNotFoundError(facility_id)
        
        # Validate permissions
        self._validate_facility_permissions(current_user, facility.company_id, "visualizar horários")
        
        schedules = self.schedule_repo.get_by_facility(facility_id)
        schedule_dtos = FacilityScheduleMapper.to_response_dtos(schedules)
        
        return {
            "schedules": [dto.model_dump() for dto in schedule_dtos],
            "total": len(schedule_dtos)
        }
    
    def update_facility_schedule(
        self, 
        schedule_id: int, 
        update_dto: FacilityScheduleUpdateDTO, 
        current_user: AuthenticatedUser
    ) -> dict:
        """Update facility schedule"""
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule:
            raise FacilityScheduleNotFoundError(schedule_id)
        
        # Get facility to validate company
        facility = self.facility_repo.get_by_id(schedule.facility_id)
        if not facility:
            raise FacilityNotFoundError(schedule.facility_id)
        
        # Validate permissions
        self._validate_facility_permissions(current_user, facility.company_id, "editar horário")
        
        # Validate time range if being updated
        if update_dto.start_time and update_dto.end_time:
            if update_dto.start_time >= update_dto.end_time:
                raise FacilityScheduleInvalidTimeError(
                    str(update_dto.start_time), 
                    str(update_dto.end_time)
                )
        
        # Update schedule
        updated_schedule = FacilityScheduleMapper.update_entity_from_dto(schedule, update_dto)
        saved_schedule = self.schedule_repo.update(updated_schedule)
        
        return FacilityScheduleMapper.to_response_dto(saved_schedule).model_dump()
    
    def delete_facility_schedule(self, schedule_id: int, current_user: AuthenticatedUser) -> bool:
        """Delete facility schedule"""
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule:
            raise FacilityScheduleNotFoundError(schedule_id)
        
        # Get facility to validate company
        facility = self.facility_repo.get_by_id(schedule.facility_id)
        if not facility:
            raise FacilityNotFoundError(schedule.facility_id)
        
        # Validate permissions
        self._validate_facility_permissions(current_user, facility.company_id, "excluir horário")
        
        return self.schedule_repo.delete(schedule_id)
    
    def get_available_facility_slots(
        self, 
        facility_id: int, 
        target_date: date,
        duration_minutes: int = 60,
        current_user: AuthenticatedUser
    ) -> dict:
        """Get available time slots for a facility"""
        # Get facility to validate company
        facility = self.facility_repo.get_by_id(facility_id)
        if not facility:
            raise FacilityNotFoundError(facility_id)
        
        # Validate permissions
        self._validate_facility_permissions(current_user, facility.company_id, "consultar disponibilidade")
        
        # Get available slots
        slots = self.schedule_repo.get_available_slots(facility_id, target_date, duration_minutes)
        
        if not slots:
            raise NoAvailableFacilitySlotsError(facility_id, str(target_date))
        
        # Filter out slots that conflict with existing appointments
        available_slots = []
        for start_time, end_time in slots:
            conflicts = self.schedule_repo.get_facility_conflicts(
                facility_id, start_time, duration_minutes
            )
            if not conflicts:
                slot_dto = FacilityAvailableSlotMapper.to_available_slot_dto(
                    start_time, end_time, duration_minutes, facility_id, facility.name
                )
                available_slots.append(slot_dto)
        
        if not available_slots:
            raise NoAvailableFacilitySlotsError(facility_id, str(target_date))
        
        response_dto = FacilityAvailableSlotMapper.to_available_slots_response_dto(
            target_date, facility_id, facility.name, available_slots
        )
        
        return response_dto.model_dump()
    
    def get_facilities_for_professional(
        self, 
        current_user: AuthenticatedUser,
        target_date: Optional[date] = None
    ) -> dict:
        """Get available facilities for professional to select"""
        if current_user.profile not in [UserProfile.PROFESSIONAL, UserProfile.MANAGER, UserProfile.ADMIN]:
            return {"facilities": [], "total": 0}
        
        # Get facilities from user's company
        company_id = current_user.company_id
        if not company_id:
            return {"facilities": [], "total": 0}
        
        search_dto = FacilitySearchDTO(company_id=company_id, is_active=True)
        facilities = self.facility_repo.search(search_dto)
        
        # If target_date is provided, filter by availability
        if target_date:
            available_facilities = []
            for facility in facilities:
                try:
                    slots = self.schedule_repo.get_available_slots(facility.id, target_date)
                    if slots:
                        available_facilities.append(facility)
                except:
                    continue
            facilities = available_facilities
        
        facility_dtos = FacilityMapper.to_list_response_dtos(facilities)
        
        return {
            "facilities": [dto.model_dump() for dto in facility_dtos],
            "total": len(facility_dtos)
        }
    
    def check_facility_availability(
        self, 
        facility_id: int, 
        appointment_date: datetime, 
        duration_minutes: int,
        exclude_appointment_id: Optional[int] = None,
        current_user: Optional[AuthenticatedUser] = None
    ) -> bool:
        """Check if facility is available for appointment"""
        # Get facility
        facility = self.facility_repo.get_by_id(facility_id)
        if not facility:
            raise FacilityNotFoundError(facility_id)
        
        # Validate permissions if user is provided
        if current_user:
            self._validate_facility_permissions(current_user, facility.company_id, "verificar disponibilidade")
        
        # Check conflicts
        conflicts = self.schedule_repo.get_facility_conflicts(
            facility_id, appointment_date, duration_minutes, exclude_appointment_id
        )
        
        return len(conflicts) == 0
    
    def _validate_facility_permissions(
        self, 
        current_user: AuthenticatedUser, 
        company_id: int, 
        action: str
    ):
        """Validate user permissions for facility actions"""
        # Admins can do everything
        if current_user.profile == UserProfile.ADMIN:
            return
        
        # Managers can manage facilities in their company
        if current_user.profile == UserProfile.MANAGER:
            if current_user.company_id == company_id:
                return
        
        # Professionals can only view facilities
        if current_user.profile == UserProfile.PROFESSIONAL:
            if action in ["visualizar", "consultar disponibilidade", "verificar disponibilidade"]:
                if current_user.company_id == company_id:
                    return
        
        raise FacilityPermissionError(action, 0) 