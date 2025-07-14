from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from neomediapi.infra.db.repositories.appointment_repository import AppointmentRepository, ProfessionalAvailabilityRepository
from neomediapi.infra.db.repositories.user_repository import UserRepository
from neomediapi.domain.appointment.dtos.appointment_dto import (
    AppointmentCreateDTO,
    AppointmentUpdateDTO,
    AppointmentSearchDTO,
    AppointmentStatusUpdateDTO,
    ProfessionalAvailabilityCreateDTO,
    ProfessionalAvailabilityUpdateDTO,
    AvailableSlotsResponseDTO,
    AvailableSlotDTO
)
from neomediapi.domain.appointment.mappers.appointment_mapper import (
    AppointmentMapper,
    ProfessionalAvailabilityMapper,
    AvailableSlotMapper
)
from neomediapi.domain.appointment.exceptions import (
    AppointmentNotFoundError,
    AppointmentAlreadyExistsError,
    AppointmentTimeConflictError,
    AppointmentInvalidStatusTransitionError,
    AppointmentOutsideAvailabilityError,
    AppointmentInvalidDurationError,
    AppointmentPastDateError,
    AppointmentPermissionError,
    ProfessionalAvailabilityNotFoundError,
    ProfessionalAvailabilityConflictError,
    ProfessionalAvailabilityInvalidTimeError,
    NoAvailableSlotsError
)
from neomediapi.enums.appointment_status import AppointmentStatus
from neomediapi.enums.user_profiles import UserProfile
from neomediapi.auth.authenticated_user import AuthenticatedUser
from neomediapi.infra.db.models.professional_availability_model import ProfessionalAvailability

class AppointmentService:
    """Service for appointment operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.appointment_repo = AppointmentRepository(db)
        self.availability_repo = ProfessionalAvailabilityRepository(db)
        self.user_repo = UserRepository(db)
    
    def create_appointment(self, appointment_dto: AppointmentCreateDTO, current_user: AuthenticatedUser) -> dict:
        """Create new appointment"""
        # Validate permissions
        self._validate_appointment_permissions(current_user, appointment_dto.professional_id, "criar")
        
        # Validate appointment date is not in the past
        if appointment_dto.appointment_date <= datetime.now():
            raise AppointmentPastDateError(str(appointment_dto.appointment_date))
        
        # Validate duration
        if not (15 <= appointment_dto.duration_minutes <= 480):
            raise AppointmentInvalidDurationError(appointment_dto.duration_minutes)
        
        # Check for conflicts
        conflicts = self.appointment_repo.get_conflicts(
            appointment_dto.professional_id,
            appointment_dto.appointment_date,
            appointment_dto.duration_minutes
        )
        
        if conflicts:
            raise AppointmentTimeConflictError(
                appointment_dto.professional_id,
                str(appointment_dto.appointment_date),
                appointment_dto.duration_minutes
            )
        
        # Check if professional is available at this time
        self._validate_professional_availability(
            appointment_dto.professional_id,
            appointment_dto.appointment_date,
            appointment_dto.duration_minutes
        )
        
        # Create appointment
        appointment = AppointmentMapper.to_entity(appointment_dto)
        created_appointment = self.appointment_repo.create(appointment)
        
        return AppointmentMapper.to_response_dto(created_appointment).model_dump()
    
    def get_appointment(self, appointment_id: int, current_user: AuthenticatedUser) -> dict:
        """Get appointment by ID"""
        appointment = self.appointment_repo.get_by_id_with_relations(appointment_id)
        if not appointment:
            raise AppointmentNotFoundError(appointment_id)
        
        # Validate permissions
        self._validate_appointment_permissions(current_user, appointment.professional_id, "visualizar", appointment)
        
        return AppointmentMapper.to_response_dto(appointment).model_dump()
    
    def get_appointments(
        self, 
        search_dto: AppointmentSearchDTO, 
        current_user: AuthenticatedUser,
        skip: int = 0, 
        limit: int = 100
    ) -> dict:
        """Get appointments with search and filters"""
        # Apply user-based filters based on profile
        if current_user.profile == UserProfile.PROFESSIONAL:
            search_dto.professional_id = current_user.user_id
        elif current_user.profile == UserProfile.PATIENT:
            search_dto.patient_id = current_user.user_id
        elif current_user.profile == UserProfile.MANAGER:
            # Managers can see appointments from their company
            if current_user.company_id:
                search_dto.company_id = current_user.company_id
        elif current_user.profile == UserProfile.ADMIN:
            # Admins can see all appointments
            pass
        
        appointments = self.appointment_repo.search(search_dto, skip, limit)
        appointment_dtos = AppointmentMapper.to_list_response_dtos(appointments)
        
        return {
            "appointments": [dto.model_dump() for dto in appointment_dtos],
            "total": len(appointment_dtos),
            "skip": skip,
            "limit": limit
        }
    
    def update_appointment(
        self, 
        appointment_id: int, 
        update_dto: AppointmentUpdateDTO, 
        current_user: AuthenticatedUser
    ) -> dict:
        """Update appointment"""
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFoundError(appointment_id)
        
        # Validate permissions
        self._validate_appointment_permissions(current_user, appointment.professional_id, "editar", appointment)
        
        # Validate status transition if status is being updated
        if update_dto.status and update_dto.status != appointment.status:
            self._validate_status_transition(appointment.status, update_dto.status)
        
        # Validate new appointment date if being updated
        if update_dto.appointment_date:
            if update_dto.appointment_date <= datetime.now():
                raise AppointmentPastDateError(str(update_dto.appointment_date))
            
            # Check for conflicts with new time
            conflicts = self.appointment_repo.get_conflicts(
                appointment.professional_id,
                update_dto.appointment_date,
                update_dto.duration_minutes or appointment.duration_minutes,
                exclude_appointment_id=appointment_id
            )
            
            if conflicts:
                raise AppointmentTimeConflictError(
                    appointment.professional_id,
                    str(update_dto.appointment_date),
                    update_dto.duration_minutes or appointment.duration_minutes
                )
            
            # Check availability for new time
            self._validate_professional_availability(
                appointment.professional_id,
                update_dto.appointment_date,
                update_dto.duration_minutes or appointment.duration_minutes
            )
        
        # Update appointment
        updated_appointment = AppointmentMapper.update_entity_from_dto(appointment, update_dto)
        saved_appointment = self.appointment_repo.update(updated_appointment)
        
        return AppointmentMapper.to_response_dto(saved_appointment).model_dump()
    
    def update_appointment_status(
        self, 
        appointment_id: int, 
        status_dto: AppointmentStatusUpdateDTO, 
        current_user: AuthenticatedUser
    ) -> dict:
        """Update appointment status"""
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFoundError(appointment_id)
        
        # Validate permissions
        self._validate_appointment_permissions(current_user, appointment.professional_id, "alterar status", appointment)
        
        # Validate status transition
        self._validate_status_transition(appointment.status, status_dto.status)
        
        # Update status
        appointment.status = status_dto.status
        updated_appointment = self.appointment_repo.update(appointment)
        
        return AppointmentMapper.to_response_dto(updated_appointment).model_dump()
    
    def delete_appointment(self, appointment_id: int, current_user: AuthenticatedUser) -> bool:
        """Delete appointment"""
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFoundError(appointment_id)
        
        # Validate permissions
        self._validate_appointment_permissions(current_user, appointment.professional_id, "excluir", appointment)
        
        return self.appointment_repo.delete(appointment_id)
    
    def get_upcoming_appointments(self, current_user: AuthenticatedUser, limit: int = 10) -> dict:
        """Get upcoming appointments for current user"""
        appointments = self.appointment_repo.get_upcoming_appointments(current_user.user_id, limit)
        appointment_dtos = AppointmentMapper.to_list_response_dtos(appointments)
        
        return {
            "appointments": [dto.model_dump() for dto in appointment_dtos],
            "total": len(appointment_dtos)
        }
    
    def get_available_slots(
        self, 
        professional_id: int, 
        target_date: date,
        duration_minutes: int = 60,
        current_user: AuthenticatedUser
    ) -> dict:
        """Get available time slots for a professional"""
        # Validate permissions
        self._validate_appointment_permissions(current_user, professional_id, "consultar disponibilidade")
        
        # Get available slots
        slots = self.availability_repo.get_available_slots(professional_id, target_date, duration_minutes)
        
        if not slots:
            raise NoAvailableSlotsError(professional_id, str(target_date))
        
        # Filter out slots that conflict with existing appointments
        available_slots = []
        for start_time, end_time in slots:
            conflicts = self.appointment_repo.get_conflicts(
                professional_id, start_time, duration_minutes
            )
            if not conflicts:
                slot_dto = AvailableSlotMapper.to_available_slot_dto(
                    start_time, end_time, duration_minutes, professional_id
                )
                available_slots.append(slot_dto)
        
        if not available_slots:
            raise NoAvailableSlotsError(professional_id, str(target_date))
        
        response_dto = AvailableSlotMapper.to_available_slots_response_dto(
            target_date, professional_id, available_slots
        )
        
        return response_dto.model_dump()
    
    def create_professional_availability(
        self, 
        availability_dto: ProfessionalAvailabilityCreateDTO, 
        current_user: AuthenticatedUser
    ) -> dict:
        """Create professional availability"""
        # Validate permissions
        self._validate_availability_permissions(current_user, availability_dto.professional_id, "criar")
        
        # Validate time range
        if availability_dto.start_time >= availability_dto.end_time:
            raise ProfessionalAvailabilityInvalidTimeError(
                str(availability_dto.start_time), 
                str(availability_dto.end_time)
            )
        
        # Check for conflicts
        existing = self.availability_repo.get_by_professional_and_day(
            availability_dto.professional_id, 
            availability_dto.day_of_week
        )
        if existing:
            raise ProfessionalAvailabilityConflictError(
                availability_dto.professional_id, 
                availability_dto.day_of_week
            )
        
        # Create availability
        availability = ProfessionalAvailabilityMapper.to_entity(availability_dto)
        created_availability = self.availability_repo.create(availability)
        
        return ProfessionalAvailabilityMapper.to_response_dto(created_availability).model_dump()
    
    def get_professional_availabilities(
        self, 
        professional_id: int, 
        current_user: AuthenticatedUser
    ) -> dict:
        """Get professional availabilities"""
        # Validate permissions
        self._validate_availability_permissions(current_user, professional_id, "visualizar")
        
        availabilities = self.availability_repo.get_by_professional(professional_id)
        availability_dtos = ProfessionalAvailabilityMapper.to_response_dtos(availabilities)
        
        return {
            "availabilities": [dto.model_dump() for dto in availability_dtos],
            "total": len(availability_dtos)
        }
    
    def update_professional_availability(
        self, 
        availability_id: int, 
        update_dto: ProfessionalAvailabilityUpdateDTO, 
        current_user: AuthenticatedUser
    ) -> dict:
        """Update professional availability"""
        availability = self.availability_repo.get_by_id(availability_id)
        if not availability:
            raise ProfessionalAvailabilityNotFoundError(availability_id)
        
        # Validate permissions
        self._validate_availability_permissions(current_user, availability.professional_id, "editar")
        
        # Validate time range if being updated
        if update_dto.start_time and update_dto.end_time:
            if update_dto.start_time >= update_dto.end_time:
                raise ProfessionalAvailabilityInvalidTimeError(
                    str(update_dto.start_time), 
                    str(update_dto.end_time)
                )
        
        # Update availability
        updated_availability = ProfessionalAvailabilityMapper.update_entity_from_dto(availability, update_dto)
        saved_availability = self.availability_repo.update(updated_availability)
        
        return ProfessionalAvailabilityMapper.to_response_dto(saved_availability).model_dump()
    
    def delete_professional_availability(self, availability_id: int, current_user: AuthenticatedUser) -> bool:
        """Delete professional availability"""
        availability = self.availability_repo.get_by_id(availability_id)
        if not availability:
            raise ProfessionalAvailabilityNotFoundError(availability_id)
        
        # Validate permissions
        self._validate_availability_permissions(current_user, availability.professional_id, "excluir")
        
        return self.availability_repo.delete(availability_id)
    
    def _validate_appointment_permissions(
        self, 
        current_user: AuthenticatedUser, 
        professional_id: int, 
        action: str,
        appointment: Optional[object] = None
    ):
        """Validate user permissions for appointment actions"""
        # Admins can do everything
        if current_user.profile == UserProfile.ADMIN:
            return
        
        # Managers can manage appointments in their company
        if current_user.profile == UserProfile.MANAGER:
            if current_user.company_id:
                # Check if professional belongs to manager's company
                professional = self.user_repo.get_by_id(professional_id)
                if professional and professional.company_id == current_user.company_id:
                    return
        
        # Professionals can manage their own appointments
        if current_user.profile == UserProfile.PROFESSIONAL:
            if current_user.user_id == professional_id:
                return
            # Professionals can also manage appointments where they are the patient
            if appointment and appointment.patient_id == current_user.user_id:
                return
        
        # Patients can only view their own appointments
        if current_user.profile == UserProfile.PATIENT:
            if appointment and appointment.patient_id == current_user.user_id:
                if action == "visualizar":
                    return
        
        raise AppointmentPermissionError(action, appointment.id if appointment else 0)
    
    def _validate_availability_permissions(
        self, 
        current_user: AuthenticatedUser, 
        professional_id: int, 
        action: str
    ):
        """Validate user permissions for availability actions"""
        # Admins can do everything
        if current_user.profile == UserProfile.ADMIN:
            return
        
        # Managers can manage availabilities in their company
        if current_user.profile == UserProfile.MANAGER:
            if current_user.company_id:
                professional = self.user_repo.get_by_id(professional_id)
                if professional and professional.company_id == current_user.company_id:
                    return
        
        # Professionals can manage their own availability
        if current_user.profile == UserProfile.PROFESSIONAL:
            if current_user.user_id == professional_id:
                return
        
        raise AppointmentPermissionError(action, 0)
    
    def _validate_status_transition(self, current_status: str, new_status: str):
        """Validate appointment status transition"""
        valid_transitions = {
            AppointmentStatus.SCHEDULED: [
                AppointmentStatus.CONFIRMED, 
                AppointmentStatus.CANCELLED, 
                AppointmentStatus.RESCHEDULED
            ],
            AppointmentStatus.CONFIRMED: [
                AppointmentStatus.IN_PROGRESS, 
                AppointmentStatus.WAITING, 
                AppointmentStatus.CANCELLED
            ],
            AppointmentStatus.IN_PROGRESS: [
                AppointmentStatus.COMPLETED, 
                AppointmentStatus.FINISHED
            ],
            AppointmentStatus.WAITING: [
                AppointmentStatus.IN_PROGRESS, 
                AppointmentStatus.CANCELLED, 
                AppointmentStatus.NO_SHOW
            ],
            AppointmentStatus.COMPLETED: [
                AppointmentStatus.FINISHED
            ],
            AppointmentStatus.CANCELLED: [
                AppointmentStatus.SCHEDULED  # Can be rescheduled
            ],
            AppointmentStatus.NO_SHOW: [
                AppointmentStatus.SCHEDULED  # Can be rescheduled
            ],
            AppointmentStatus.RESCHEDULED: [
                AppointmentStatus.CONFIRMED, 
                AppointmentStatus.CANCELLED
            ]
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise AppointmentInvalidStatusTransitionError(current_status, new_status)
    
    def _validate_professional_availability(
        self, 
        professional_id: int, 
        appointment_date: datetime, 
        duration_minutes: int
    ):
        """Validate if professional is available at the given time"""
        target_date = appointment_date.date()
        day_of_week = target_date.weekday()
        
        # Get regular availability
        availability = self.availability_repo.get_by_professional_and_day(professional_id, day_of_week)
        if not availability or not availability.is_available:
            raise AppointmentOutsideAvailabilityError(professional_id, str(appointment_date))
        
        # Check for exceptions
        exception = self.db.query(ProfessionalAvailability).filter(
            ProfessionalAvailability.professional_id == professional_id,
            ProfessionalAvailability.exception_date == target_date,
            ProfessionalAvailability.is_deleted == False
        ).first()
        
        if exception:
            if not exception.is_available:
                raise AppointmentOutsideAvailabilityError(professional_id, str(appointment_date))
            
            start_time = exception.exception_start_time or availability.start_time
            end_time = exception.exception_end_time or availability.end_time
        else:
            start_time = availability.start_time
            end_time = availability.end_time
        
        # Check if appointment time is within availability
        appointment_time = appointment_date.time()
        end_appointment_time = (appointment_date + timedelta(minutes=duration_minutes)).time()
        
        if appointment_time < start_time or end_appointment_time > end_time:
            raise AppointmentOutsideAvailabilityError(professional_id, str(appointment_date)) 