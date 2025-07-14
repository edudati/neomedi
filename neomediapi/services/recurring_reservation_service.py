from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from neomediapi.infra.db.repositories.facility_repository import FacilityRepository, FacilityScheduleRepository
from neomediapi.infra.db.repositories.appointment_repository import AppointmentRepository
from neomediapi.infra.db.repositories.user_repository import UserRepository
from neomediapi.infra.db.models.recurring_reservation_model import RecurringReservation
from neomediapi.domain.facility.dtos.recurring_reservation_dto import (
    RecurringReservationCreateDTO,
    RecurringReservationUpdateDTO,
    RecurringReservationSearchDTO,
    RecurringReservationGenerationDTO,
    GeneratedAppointmentDTO,
    RecurringReservationGenerationResponseDTO
)
from neomediapi.domain.facility.exceptions import (
    FacilityNotFoundError,
    FacilityPermissionError,
    FacilityOccupiedError
)
from neomediapi.domain.appointment.exceptions import (
    AppointmentTimeConflictError
)
from neomediapi.enums.user_profiles import UserProfile
from neomediapi.auth.authenticated_user import AuthenticatedUser

class RecurringReservationService:
    """Service for recurring reservation operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.facility_repo = FacilityRepository(db)
        self.schedule_repo = FacilityScheduleRepository(db)
        self.appointment_repo = AppointmentRepository(db)
        self.user_repo = UserRepository(db)
    
    def create_recurring_reservation(
        self, 
        reservation_dto: RecurringReservationCreateDTO, 
        current_user: AuthenticatedUser
    ) -> dict:
        """Create new recurring reservation"""
        # Validate permissions
        self._validate_reservation_permissions(current_user, reservation_dto.professional_id, "criar")
        
        # Validate facility exists
        facility = self.facility_repo.get_by_id(reservation_dto.facility_id)
        if not facility:
            raise FacilityNotFoundError(reservation_dto.facility_id)
        
        # Validate professional exists
        professional = self.user_repo.get_by_id(reservation_dto.professional_id)
        if not professional:
            raise FacilityNotFoundError(reservation_dto.professional_id)
        
        # Validate time format
        self._validate_time_format(reservation_dto.start_time, reservation_dto.end_time)
        
        # Validate date range
        if reservation_dto.end_date and reservation_dto.start_date > reservation_dto.end_date:
            raise ValueError("Data de início deve ser anterior à data de fim")
        
        # Create reservation
        reservation = RecurringReservation(
            title=reservation_dto.title,
            description=reservation_dto.description,
            day_of_week=reservation_dto.day_of_week,
            start_time=reservation_dto.start_time,
            end_time=reservation_dto.end_time,
            duration_minutes=reservation_dto.duration_minutes,
            start_date=reservation_dto.start_date,
            end_date=reservation_dto.end_date,
            professional_id=reservation_dto.professional_id,
            facility_id=reservation_dto.facility_id,
            company_id=reservation_dto.company_id
        )
        
        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        
        return self._to_response_dict(reservation)
    
    def get_recurring_reservation(self, reservation_id: int, current_user: AuthenticatedUser) -> dict:
        """Get recurring reservation by ID"""
        reservation = self.db.query(RecurringReservation).filter(
            RecurringReservation.id == reservation_id,
            RecurringReservation.is_deleted == False
        ).first()
        
        if not reservation:
            raise FacilityNotFoundError(reservation_id)
        
        # Validate permissions
        self._validate_reservation_permissions(current_user, reservation.professional_id, "visualizar")
        
        return self._to_response_dict(reservation)
    
    def get_recurring_reservations(
        self, 
        search_dto: RecurringReservationSearchDTO, 
        current_user: AuthenticatedUser,
        skip: int = 0, 
        limit: int = 100
    ) -> dict:
        """Get recurring reservations with search and filters"""
        query = self.db.query(RecurringReservation).filter(RecurringReservation.is_deleted == False)
        
        # Apply user-based filters
        if current_user.profile == UserProfile.PROFESSIONAL:
            search_dto.professional_id = current_user.user_id
        elif current_user.profile == UserProfile.MANAGER:
            if current_user.company_id:
                search_dto.company_id = current_user.company_id
        elif current_user.profile == UserProfile.ADMIN:
            pass
        else:
            return {"reservations": [], "total": 0, "skip": skip, "limit": limit}
        
        # Apply filters
        if search_dto.query:
            search_term = f"%{search_dto.query}%"
            query = query.filter(RecurringReservation.title.ilike(search_term))
        
        if search_dto.professional_id:
            query = query.filter(RecurringReservation.professional_id == search_dto.professional_id)
        
        if search_dto.facility_id:
            query = query.filter(RecurringReservation.facility_id == search_dto.facility_id)
        
        if search_dto.company_id:
            query = query.filter(RecurringReservation.company_id == search_dto.company_id)
        
        if search_dto.day_of_week is not None:
            query = query.filter(RecurringReservation.day_of_week == search_dto.day_of_week)
        
        if search_dto.is_active is not None:
            query = query.filter(RecurringReservation.is_active == search_dto.is_active)
        
        reservations = query.order_by(RecurringReservation.start_date.desc()).offset(skip).limit(limit).all()
        
        return {
            "reservations": [self._to_list_response_dict(r) for r in reservations],
            "total": len(reservations),
            "skip": skip,
            "limit": limit
        }
    
    def update_recurring_reservation(
        self, 
        reservation_id: int, 
        update_dto: RecurringReservationUpdateDTO, 
        current_user: AuthenticatedUser
    ) -> dict:
        """Update recurring reservation"""
        reservation = self.db.query(RecurringReservation).filter(
            RecurringReservation.id == reservation_id,
            RecurringReservation.is_deleted == False
        ).first()
        
        if not reservation:
            raise FacilityNotFoundError(reservation_id)
        
        # Validate permissions
        self._validate_reservation_permissions(current_user, reservation.professional_id, "editar")
        
        # Update fields
        if update_dto.title is not None:
            reservation.title = update_dto.title
        if update_dto.description is not None:
            reservation.description = update_dto.description
        if update_dto.day_of_week is not None:
            reservation.day_of_week = update_dto.day_of_week
        if update_dto.start_time is not None:
            reservation.start_time = update_dto.start_time
        if update_dto.end_time is not None:
            reservation.end_time = update_dto.end_time
        if update_dto.duration_minutes is not None:
            reservation.duration_minutes = update_dto.duration_minutes
        if update_dto.start_date is not None:
            reservation.start_date = update_dto.start_date
        if update_dto.end_date is not None:
            reservation.end_date = update_dto.end_date
        if update_dto.is_active is not None:
            reservation.is_active = update_dto.is_active
        
        # Validate time format if updated
        if update_dto.start_time or update_dto.end_time:
            self._validate_time_format(reservation.start_time, reservation.end_time)
        
        self.db.commit()
        self.db.refresh(reservation)
        
        return self._to_response_dict(reservation)
    
    def delete_recurring_reservation(self, reservation_id: int, current_user: AuthenticatedUser) -> bool:
        """Delete recurring reservation"""
        reservation = self.db.query(RecurringReservation).filter(
            RecurringReservation.id == reservation_id,
            RecurringReservation.is_deleted == False
        ).first()
        
        if not reservation:
            raise FacilityNotFoundError(reservation_id)
        
        # Validate permissions
        self._validate_reservation_permissions(current_user, reservation.professional_id, "excluir")
        
        reservation.soft_delete()
        self.db.commit()
        return True
    
    def generate_appointments_from_reservation(
        self, 
        reservation_id: int, 
        generation_dto: RecurringReservationGenerationDTO, 
        current_user: AuthenticatedUser
    ) -> dict:
        """Generate appointments from recurring reservation"""
        reservation = self.db.query(RecurringReservation).filter(
            RecurringReservation.id == reservation_id,
            RecurringReservation.is_deleted == False
        ).first()
        
        if not reservation:
            raise FacilityNotFoundError(reservation_id)
        
        # Validate permissions
        self._validate_reservation_permissions(current_user, reservation.professional_id, "gerar agendamentos")
        
        # Validate date range
        if generation_dto.start_date < reservation.start_date:
            raise ValueError("Data de início para geração deve ser posterior à data de início da reserva")
        
        if reservation.end_date and generation_dto.end_date > reservation.end_date:
            raise ValueError("Data de fim para geração deve ser anterior à data de fim da reserva")
        
        # Generate appointments
        generated_appointments = []
        conflicts = []
        current_date = generation_dto.start_date
        
        while current_date <= generation_dto.end_date:
            if current_date.weekday() == reservation.day_of_week:
                # Create appointment datetime
                start_time_parts = reservation.start_time.split(':')
                appointment_datetime = datetime.combine(
                    current_date, 
                    datetime.min.time().replace(
                        hour=int(start_time_parts[0]), 
                        minute=int(start_time_parts[1])
                    )
                )
                
                # Check for conflicts
                try:
                    conflicts_check = self.schedule_repo.get_facility_conflicts(
                        reservation.facility_id, 
                        appointment_datetime, 
                        reservation.duration_minutes
                    )
                    
                    if not conflicts_check:
                        generated_appointment = GeneratedAppointmentDTO(
                            appointment_date=appointment_datetime,
                            title=reservation.title,
                            professional_id=reservation.professional_id,
                            facility_id=reservation.facility_id,
                            duration_minutes=reservation.duration_minutes
                        )
                        generated_appointments.append(generated_appointment)
                        
                        # Create actual appointment if requested
                        if generation_dto.create_appointments:
                            from neomediapi.infra.db.models.appointment_model import Appointment
                            from neomediapi.enums.appointment_types import AppointmentType
                            from neomediapi.enums.appointment_status import AppointmentStatus
                            
                            appointment = Appointment(
                                title=reservation.title,
                                appointment_date=appointment_datetime,
                                duration_minutes=reservation.duration_minutes,
                                appointment_type=AppointmentType.CONSULTATION,
                                status=AppointmentStatus.SCHEDULED,
                                notes=f"Gerado automaticamente da reserva recorrente {reservation.id}",
                                professional_id=reservation.professional_id,
                                facility_id=reservation.facility_id,
                                company_id=reservation.company_id
                            )
                            self.db.add(appointment)
                    else:
                        conflicts.append(f"Conflito em {appointment_datetime.strftime('%d/%m/%Y %H:%M')}")
                        
                except Exception as e:
                    conflicts.append(f"Erro ao verificar disponibilidade em {appointment_datetime.strftime('%d/%m/%Y %H:%M')}: {str(e)}")
            
            current_date += timedelta(days=1)
        
        if generation_dto.create_appointments:
            self.db.commit()
        
        return RecurringReservationGenerationResponseDTO(
            reservation_id=reservation_id,
            generated_appointments=generated_appointments,
            total_generated=len(generated_appointments),
            conflicts=conflicts
        ).model_dump()
    
    def _validate_reservation_permissions(
        self, 
        current_user: AuthenticatedUser, 
        professional_id: int, 
        action: str
    ):
        """Validate user permissions for reservation actions"""
        # Admins can do everything
        if current_user.profile == UserProfile.ADMIN:
            return
        
        # Managers can manage reservations in their company
        if current_user.profile == UserProfile.MANAGER:
            if current_user.company_id:
                professional = self.user_repo.get_by_id(professional_id)
                if professional and professional.company_id == current_user.company_id:
                    return
        
        # Professionals can manage their own reservations
        if current_user.profile == UserProfile.PROFESSIONAL:
            if current_user.user_id == professional_id:
                return
        
        raise FacilityPermissionError(action, 0)
    
    def _validate_time_format(self, start_time: str, end_time: str):
        """Validate time format (HH:MM)"""
        try:
            start_parts = start_time.split(':')
            end_parts = end_time.split(':')
            
            start_hour = int(start_parts[0])
            start_minute = int(start_parts[1])
            end_hour = int(end_parts[0])
            end_minute = int(end_parts[1])
            
            if not (0 <= start_hour <= 23 and 0 <= start_minute <= 59):
                raise ValueError("Horário de início inválido")
            
            if not (0 <= end_hour <= 23 and 0 <= end_minute <= 59):
                raise ValueError("Horário de fim inválido")
            
            if start_hour > end_hour or (start_hour == end_hour and start_minute >= end_minute):
                raise ValueError("Horário de início deve ser anterior ao horário de fim")
                
        except (ValueError, IndexError):
            raise ValueError("Formato de horário inválido. Use HH:MM")
    
    def _to_response_dict(self, reservation: RecurringReservation) -> dict:
        """Convert reservation to response dict"""
        return {
            "id": reservation.id,
            "title": reservation.title,
            "description": reservation.description,
            "day_of_week": reservation.day_of_week,
            "start_time": reservation.start_time,
            "end_time": reservation.end_time,
            "duration_minutes": reservation.duration_minutes,
            "start_date": reservation.start_date,
            "end_date": reservation.end_date,
            "professional_id": reservation.professional_id,
            "facility_id": reservation.facility_id,
            "company_id": reservation.company_id,
            "is_active": reservation.is_active,
            "created_at": reservation.created_at,
            "updated_at": reservation.updated_at
        }
    
    def _to_list_response_dict(self, reservation: RecurringReservation) -> dict:
        """Convert reservation to list response dict"""
        return {
            "id": reservation.id,
            "title": reservation.title,
            "day_of_week": reservation.day_of_week,
            "start_time": reservation.start_time,
            "end_time": reservation.end_time,
            "duration_minutes": reservation.duration_minutes,
            "start_date": reservation.start_date,
            "end_date": reservation.end_date,
            "professional_id": reservation.professional_id,
            "facility_id": reservation.facility_id,
            "is_active": reservation.is_active,
            "created_at": reservation.created_at
        } 