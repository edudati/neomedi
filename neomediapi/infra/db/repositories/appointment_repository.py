from typing import List, Optional, Tuple
from datetime import datetime, date, time, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, extract
from neomediapi.infra.db.models.appointment_model import Appointment
from neomediapi.infra.db.models.professional_availability_model import ProfessionalAvailability
from neomediapi.domain.appointment.dtos.appointment_dto import AppointmentSearchDTO
from neomediapi.domain.appointment.exceptions import AppointmentNotFoundError

class AppointmentRepository:
    """Repository for appointment operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, appointment: Appointment) -> Appointment:
        """Create new appointment"""
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment
    
    def get_by_id(self, appointment_id: int) -> Optional[Appointment]:
        """Get appointment by ID"""
        return self.db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.is_deleted == False
        ).first()
    
    def get_by_id_with_relations(self, appointment_id: int) -> Optional[Appointment]:
        """Get appointment by ID with related data"""
        return self.db.query(Appointment).options(
            joinedload(Appointment.patient),
            joinedload(Appointment.professional),
            joinedload(Appointment.company),
            joinedload(Appointment.medical_record)
        ).filter(
            Appointment.id == appointment_id,
            Appointment.is_deleted == False
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Appointment]:
        """Get all appointments with pagination"""
        return self.db.query(Appointment).filter(
            Appointment.is_deleted == False
        ).offset(skip).limit(limit).all()
    
    def search(self, search_dto: AppointmentSearchDTO, skip: int = 0, limit: int = 100) -> List[Appointment]:
        """Search appointments with filters"""
        query = self.db.query(Appointment).filter(Appointment.is_deleted == False)
        
        # Text search
        if search_dto.query:
            search_term = f"%{search_dto.query}%"
            query = query.filter(
                or_(
                    Appointment.title.ilike(search_term),
                    Appointment.notes.ilike(search_term),
                    Appointment.description.ilike(search_term),
                    Appointment.location.ilike(search_term)
                )
            )
        
        # Filter by appointment type
        if search_dto.appointment_type:
            query = query.filter(Appointment.appointment_type == search_dto.appointment_type)
        
        # Filter by status
        if search_dto.status:
            query = query.filter(Appointment.status == search_dto.status)
        
        # Filter by patient
        if search_dto.patient_id:
            query = query.filter(Appointment.patient_id == search_dto.patient_id)
        
        # Filter by professional
        if search_dto.professional_id:
            query = query.filter(Appointment.professional_id == search_dto.professional_id)
        
        # Filter by company
        if search_dto.company_id:
            query = query.filter(Appointment.company_id == search_dto.company_id)
        
        # Filter by date range
        if search_dto.date_from:
            query = query.filter(Appointment.appointment_date >= search_dto.date_from)
        
        if search_dto.date_to:
            # Add one day to include the entire day
            next_day = search_dto.date_to + timedelta(days=1)
            query = query.filter(Appointment.appointment_date < next_day)
        
        # Filter by active status
        if search_dto.is_active is not None:
            query = query.filter(Appointment.is_active == search_dto.is_active)
        
        return query.order_by(Appointment.appointment_date.desc()).offset(skip).limit(limit).all()
    
    def get_by_patient(self, patient_id: int, skip: int = 0, limit: int = 100) -> List[Appointment]:
        """Get appointments by patient"""
        return self.db.query(Appointment).filter(
            Appointment.patient_id == patient_id,
            Appointment.is_deleted == False
        ).order_by(Appointment.appointment_date.desc()).offset(skip).limit(limit).all()
    
    def get_by_professional(self, professional_id: int, skip: int = 0, limit: int = 100) -> List[Appointment]:
        """Get appointments by professional"""
        return self.db.query(Appointment).filter(
            Appointment.professional_id == professional_id,
            Appointment.is_deleted == False
        ).order_by(Appointment.appointment_date.desc()).offset(skip).limit(limit).all()
    
    def get_by_company(self, company_id: int, skip: int = 0, limit: int = 100) -> List[Appointment]:
        """Get appointments by company"""
        return self.db.query(Appointment).filter(
            Appointment.company_id == company_id,
            Appointment.is_deleted == False
        ).order_by(Appointment.appointment_date.desc()).offset(skip).limit(limit).all()
    
    def get_conflicts(
        self, 
        professional_id: int, 
        appointment_date: datetime, 
        duration_minutes: int,
        exclude_appointment_id: Optional[int] = None
    ) -> List[Appointment]:
        """Get conflicting appointments for a time slot"""
        end_time = appointment_date + timedelta(minutes=duration_minutes)
        
        query = self.db.query(Appointment).filter(
            Appointment.professional_id == professional_id,
            Appointment.is_deleted == False,
            Appointment.is_active == True,
            or_(
                # New appointment starts during existing appointment
                and_(
                    Appointment.appointment_date <= appointment_date,
                    Appointment.appointment_date + func.cast(Appointment.duration_minutes, func.Integer) * func.interval('1 minute') > appointment_date
                ),
                # New appointment ends during existing appointment
                and_(
                    Appointment.appointment_date < end_time,
                    Appointment.appointment_date + func.cast(Appointment.duration_minutes, func.Integer) * func.interval('1 minute') >= end_time
                ),
                # New appointment completely contains existing appointment
                and_(
                    Appointment.appointment_date >= appointment_date,
                    Appointment.appointment_date + func.cast(Appointment.duration_minutes, func.Integer) * func.interval('1 minute') <= end_time
                )
            )
        )
        
        if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)
        
        return query.all()
    
    def update(self, appointment: Appointment) -> Appointment:
        """Update appointment"""
        self.db.commit()
        self.db.refresh(appointment)
        return appointment
    
    def delete(self, appointment_id: int) -> bool:
        """Soft delete appointment"""
        appointment = self.get_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFoundError(appointment_id)
        
        appointment.soft_delete()
        self.db.commit()
        return True
    
    def restore(self, appointment_id: int) -> bool:
        """Restore soft deleted appointment"""
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.is_deleted == True
        ).first()
        
        if not appointment:
            raise AppointmentNotFoundError(appointment_id)
        
        appointment.restore()
        self.db.commit()
        return True
    
    def get_upcoming_appointments(self, user_id: int, limit: int = 10) -> List[Appointment]:
        """Get upcoming appointments for a user (as patient or professional)"""
        now = datetime.now()
        return self.db.query(Appointment).filter(
            Appointment.is_deleted == False,
            Appointment.is_active == True,
            Appointment.appointment_date > now,
            or_(
                Appointment.patient_id == user_id,
                Appointment.professional_id == user_id
            )
        ).order_by(Appointment.appointment_date.asc()).limit(limit).all()

class ProfessionalAvailabilityRepository:
    """Repository for professional availability operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, availability: ProfessionalAvailability) -> ProfessionalAvailability:
        """Create new availability"""
        self.db.add(availability)
        self.db.commit()
        self.db.refresh(availability)
        return availability
    
    def get_by_id(self, availability_id: int) -> Optional[ProfessionalAvailability]:
        """Get availability by ID"""
        return self.db.query(ProfessionalAvailability).filter(
            ProfessionalAvailability.id == availability_id,
            ProfessionalAvailability.is_deleted == False
        ).first()
    
    def get_by_professional(self, professional_id: int) -> List[ProfessionalAvailability]:
        """Get all availabilities for a professional"""
        return self.db.query(ProfessionalAvailability).filter(
            ProfessionalAvailability.professional_id == professional_id,
            ProfessionalAvailability.is_deleted == False
        ).all()
    
    def get_by_professional_and_day(self, professional_id: int, day_of_week: int) -> Optional[ProfessionalAvailability]:
        """Get availability for a professional on a specific day"""
        return self.db.query(ProfessionalAvailability).filter(
            ProfessionalAvailability.professional_id == professional_id,
            ProfessionalAvailability.day_of_week == day_of_week,
            ProfessionalAvailability.is_deleted == False
        ).first()
    
    def get_by_company(self, company_id: int) -> List[ProfessionalAvailability]:
        """Get all availabilities for a company"""
        return self.db.query(ProfessionalAvailability).filter(
            ProfessionalAvailability.company_id == company_id,
            ProfessionalAvailability.is_deleted == False
        ).all()
    
    def update(self, availability: ProfessionalAvailability) -> ProfessionalAvailability:
        """Update availability"""
        self.db.commit()
        self.db.refresh(availability)
        return availability
    
    def delete(self, availability_id: int) -> bool:
        """Soft delete availability"""
        availability = self.get_by_id(availability_id)
        if not availability:
            raise AppointmentNotFoundError(availability_id)
        
        availability.soft_delete()
        self.db.commit()
        return True
    
    def get_available_slots(
        self, 
        professional_id: int, 
        target_date: date,
        duration_minutes: int = 60
    ) -> List[Tuple[datetime, datetime]]:
        """Get available time slots for a professional on a specific date"""
        # Get day of week (0=Monday, 6=Sunday)
        day_of_week = target_date.weekday()
        
        # Get regular availability for this day
        availability = self.get_by_professional_and_day(professional_id, day_of_week)
        if not availability or not availability.is_available:
            return []
        
        # Check for exceptions on this date
        exception = self.db.query(ProfessionalAvailability).filter(
            ProfessionalAvailability.professional_id == professional_id,
            ProfessionalAvailability.exception_date == target_date,
            ProfessionalAvailability.is_deleted == False
        ).first()
        
        if exception:
            if not exception.is_available:
                return []
            start_time = exception.exception_start_time or availability.start_time
            end_time = exception.exception_end_time or availability.end_time
        else:
            start_time = availability.start_time
            end_time = availability.end_time
        
        # Generate time slots
        slots = []
        current_time = datetime.combine(target_date, start_time)
        end_datetime = datetime.combine(target_date, end_time)
        
        while current_time + timedelta(minutes=duration_minutes) <= end_datetime:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            slots.append((current_time, slot_end))
            current_time = slot_end
        
        return slots 