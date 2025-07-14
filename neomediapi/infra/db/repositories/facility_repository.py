from typing import List, Optional, Tuple
from datetime import datetime, date, time, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from neomediapi.infra.db.models.facility_model import Facility
from neomediapi.infra.db.models.facility_schedule_model import FacilitySchedule
from neomediapi.infra.db.models.appointment_model import Appointment
from neomediapi.domain.facility.dtos.facility_dto import FacilitySearchDTO
from neomediapi.domain.facility.exceptions import FacilityNotFoundError

class FacilityRepository:
    """Repository for facility operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, facility: Facility) -> Facility:
        """Create new facility"""
        self.db.add(facility)
        self.db.commit()
        self.db.refresh(facility)
        return facility
    
    def get_by_id(self, facility_id: int) -> Optional[Facility]:
        """Get facility by ID"""
        return self.db.query(Facility).filter(
            Facility.id == facility_id,
            Facility.is_deleted == False
        ).first()
    
    def get_by_id_with_relations(self, facility_id: int) -> Optional[Facility]:
        """Get facility by ID with related data"""
        return self.db.query(Facility).options(
            joinedload(Facility.company),
            joinedload(Facility.schedules)
        ).filter(
            Facility.id == facility_id,
            Facility.is_deleted == False
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Facility]:
        """Get all facilities with pagination"""
        return self.db.query(Facility).filter(
            Facility.is_deleted == False
        ).offset(skip).limit(limit).all()
    
    def search(self, search_dto: FacilitySearchDTO, skip: int = 0, limit: int = 100) -> List[Facility]:
        """Search facilities with filters"""
        query = self.db.query(Facility).filter(Facility.is_deleted == False)
        
        # Text search
        if search_dto.query:
            search_term = f"%{search_dto.query}%"
            query = query.filter(
                or_(
                    Facility.name.ilike(search_term),
                    Facility.description.ilike(search_term),
                    Facility.room_number.ilike(search_term)
                )
            )
        
        # Filter by facility type
        if search_dto.facility_type:
            query = query.filter(Facility.facility_type == search_dto.facility_type)
        
        # Filter by company
        if search_dto.company_id:
            query = query.filter(Facility.company_id == search_dto.company_id)
        
        # Filter by accessibility
        if search_dto.is_accessible is not None:
            query = query.filter(Facility.is_accessible == search_dto.is_accessible)
        
        # Filter by equipment
        if search_dto.has_equipment is not None:
            query = query.filter(Facility.has_equipment == search_dto.has_equipment)
        
        # Filter by active status
        if search_dto.is_active is not None:
            query = query.filter(Facility.is_active == search_dto.is_active)
        
        return query.order_by(Facility.name.asc()).offset(skip).limit(limit).all()
    
    def get_by_company(self, company_id: int, skip: int = 0, limit: int = 100) -> List[Facility]:
        """Get facilities by company"""
        return self.db.query(Facility).filter(
            Facility.company_id == company_id,
            Facility.is_deleted == False
        ).order_by(Facility.name.asc()).offset(skip).limit(limit).all()
    
    def get_by_name_and_company(self, name: str, company_id: int) -> Optional[Facility]:
        """Get facility by name and company"""
        return self.db.query(Facility).filter(
            Facility.name == name,
            Facility.company_id == company_id,
            Facility.is_deleted == False
        ).first()
    
    def update(self, facility: Facility) -> Facility:
        """Update facility"""
        self.db.commit()
        self.db.refresh(facility)
        return facility
    
    def delete(self, facility_id: int) -> bool:
        """Soft delete facility"""
        facility = self.get_by_id(facility_id)
        if not facility:
            raise FacilityNotFoundError(facility_id)
        
        facility.soft_delete()
        self.db.commit()
        return True
    
    def restore(self, facility_id: int) -> bool:
        """Restore soft deleted facility"""
        facility = self.db.query(Facility).filter(
            Facility.id == facility_id,
            Facility.is_deleted == True
        ).first()
        
        if not facility:
            raise FacilityNotFoundError(facility_id)
        
        facility.restore()
        self.db.commit()
        return True

class FacilityScheduleRepository:
    """Repository for facility schedule operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, schedule: FacilitySchedule) -> FacilitySchedule:
        """Create new schedule"""
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule
    
    def get_by_id(self, schedule_id: int) -> Optional[FacilitySchedule]:
        """Get schedule by ID"""
        return self.db.query(FacilitySchedule).filter(
            FacilitySchedule.id == schedule_id,
            FacilitySchedule.is_deleted == False
        ).first()
    
    def get_by_facility(self, facility_id: int) -> List[FacilitySchedule]:
        """Get all schedules for a facility"""
        return self.db.query(FacilitySchedule).filter(
            FacilitySchedule.facility_id == facility_id,
            FacilitySchedule.is_deleted == False
        ).all()
    
    def get_by_facility_and_day(self, facility_id: int, day_of_week: int) -> Optional[FacilitySchedule]:
        """Get schedule for a facility on a specific day"""
        return self.db.query(FacilitySchedule).filter(
            FacilitySchedule.facility_id == facility_id,
            FacilitySchedule.day_of_week == day_of_week,
            FacilitySchedule.is_deleted == False
        ).first()
    
    def get_by_company(self, company_id: int) -> List[FacilitySchedule]:
        """Get all schedules for a company"""
        return self.db.query(FacilitySchedule).filter(
            FacilitySchedule.company_id == company_id,
            FacilitySchedule.is_deleted == False
        ).all()
    
    def update(self, schedule: FacilitySchedule) -> FacilitySchedule:
        """Update schedule"""
        self.db.commit()
        self.db.refresh(schedule)
        return schedule
    
    def delete(self, schedule_id: int) -> bool:
        """Soft delete schedule"""
        schedule = self.get_by_id(schedule_id)
        if not schedule:
            raise FacilityNotFoundError(schedule_id)
        
        schedule.soft_delete()
        self.db.commit()
        return True
    
    def get_available_slots(
        self, 
        facility_id: int, 
        target_date: date,
        duration_minutes: int = 60
    ) -> List[Tuple[datetime, datetime]]:
        """Get available time slots for a facility on a specific date"""
        # Get day of week (0=Monday, 6=Sunday)
        day_of_week = target_date.weekday()
        
        # Get regular schedule for this day
        schedule = self.get_by_facility_and_day(facility_id, day_of_week)
        if not schedule or not schedule.is_available:
            return []
        
        # Check for exceptions on this date
        exception = self.db.query(FacilitySchedule).filter(
            FacilitySchedule.facility_id == facility_id,
            FacilitySchedule.exception_date == target_date,
            FacilitySchedule.is_deleted == False
        ).first()
        
        if exception:
            if not exception.is_available:
                return []
            start_time = exception.exception_start_time or schedule.start_time
            end_time = exception.exception_end_time or schedule.end_time
        else:
            start_time = schedule.start_time
            end_time = schedule.end_time
        
        # Generate time slots
        slots = []
        current_time = datetime.combine(target_date, start_time)
        end_datetime = datetime.combine(target_date, end_time)
        
        while current_time + timedelta(minutes=duration_minutes) <= end_datetime:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            slots.append((current_time, slot_end))
            current_time = slot_end
        
        return slots
    
    def get_facility_conflicts(
        self, 
        facility_id: int, 
        appointment_date: datetime, 
        duration_minutes: int,
        exclude_appointment_id: Optional[int] = None
    ) -> List[Appointment]:
        """Get conflicting appointments for a facility time slot"""
        end_time = appointment_date + timedelta(minutes=duration_minutes)
        
        query = self.db.query(Appointment).filter(
            Appointment.facility_id == facility_id,
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