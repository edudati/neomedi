from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from neomediapi.infra.db.session import get_db
from neomediapi.auth.dependencies import get_current_user
from neomediapi.auth.authenticated_user import AuthenticatedUser
from neomediapi.services.facility_service import FacilityService
from neomediapi.domain.facility.dtos.facility_dto import (
    FacilityCreateDTO,
    FacilityUpdateDTO,
    FacilitySearchDTO,
    FacilityResponseDTO,
    FacilityListResponseDTO,
    FacilityScheduleCreateDTO,
    FacilityScheduleUpdateDTO,
    FacilityScheduleResponseDTO,
    FacilityAvailableSlotsResponseDTO
)
from neomediapi.domain.facility.exceptions import (
    FacilityException,
    FacilityNotFoundError,
    FacilityAlreadyExistsError,
    FacilityPermissionError,
    FacilityScheduleNotFoundError,
    FacilityScheduleConflictError,
    FacilityScheduleInvalidTimeError,
    NoAvailableFacilitySlotsError
)

router = APIRouter(prefix="/facilities", tags=["facilities"])

# Facility Routes
@router.post("/", response_model=FacilityResponseDTO, status_code=status.HTTP_201_CREATED)
def create_facility(
    facility_dto: FacilityCreateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new facility"""
    try:
        service = FacilityService(db)
        return service.create_facility(facility_dto, current_user)
    except (FacilityAlreadyExistsError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except FacilityPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.get("/{facility_id}", response_model=FacilityResponseDTO)
def get_facility(
    facility_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get facility by ID"""
    try:
        service = FacilityService(db)
        return service.get_facility(facility_id, current_user)
    except FacilityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except FacilityPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.get("/", response_model=dict)
def get_facilities(
    query: Optional[str] = Query(None, description="Search term"),
    facility_type: Optional[str] = Query(None, description="Facility type"),
    company_id: Optional[int] = Query(None, description="Company ID"),
    is_accessible: Optional[bool] = Query(None, description="Accessible for PCD"),
    has_equipment: Optional[bool] = Query(None, description="Has equipment"),
    is_active: Optional[bool] = Query(True, description="Active facilities only"),
    skip: int = Query(0, ge=0, description="Skip records"),
    limit: int = Query(100, ge=1, le=1000, description="Limit records"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get facilities with search and filters"""
    try:
        search_dto = FacilitySearchDTO(
            query=query,
            facility_type=facility_type,
            company_id=company_id,
            is_accessible=is_accessible,
            has_equipment=has_equipment,
            is_active=is_active
        )
        
        service = FacilityService(db)
        return service.get_facilities(search_dto, current_user, skip, limit)
    except FacilityException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.put("/{facility_id}", response_model=FacilityResponseDTO)
def update_facility(
    facility_id: int,
    update_dto: FacilityUpdateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update facility"""
    try:
        service = FacilityService(db)
        return service.update_facility(facility_id, update_dto, current_user)
    except FacilityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except FacilityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except FacilityPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.delete("/{facility_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_facility(
    facility_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete facility"""
    try:
        service = FacilityService(db)
        service.delete_facility(facility_id, current_user)
    except FacilityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except FacilityPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

# Facility Schedule Routes
@router.post("/schedule", response_model=FacilityScheduleResponseDTO, status_code=status.HTTP_201_CREATED)
def create_facility_schedule(
    schedule_dto: FacilityScheduleCreateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create facility schedule"""
    try:
        service = FacilityService(db)
        return service.create_facility_schedule(schedule_dto, current_user)
    except (FacilityScheduleConflictError, FacilityScheduleInvalidTimeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except FacilityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except FacilityPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.get("/schedule/{facility_id}", response_model=dict)
def get_facility_schedules(
    facility_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get facility schedules"""
    try:
        service = FacilityService(db)
        return service.get_facility_schedules(facility_id, current_user)
    except FacilityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except FacilityPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.put("/schedule/{schedule_id}", response_model=FacilityScheduleResponseDTO)
def update_facility_schedule(
    schedule_id: int,
    update_dto: FacilityScheduleUpdateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update facility schedule"""
    try:
        service = FacilityService(db)
        return service.update_facility_schedule(schedule_id, update_dto, current_user)
    except FacilityScheduleNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except FacilityScheduleInvalidTimeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except FacilityPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.delete("/schedule/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_facility_schedule(
    schedule_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete facility schedule"""
    try:
        service = FacilityService(db)
        service.delete_facility_schedule(schedule_id, current_user)
    except FacilityScheduleNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except FacilityPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

# Available Slots Routes
@router.get("/slots/{facility_id}", response_model=FacilityAvailableSlotsResponseDTO)
def get_available_facility_slots(
    facility_id: int,
    date: date = Query(..., description="Target date"),
    duration_minutes: int = Query(60, ge=15, le=480, description="Duration in minutes"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available time slots for a facility"""
    try:
        service = FacilityService(db)
        return service.get_available_facility_slots(facility_id, date, duration_minutes, current_user)
    except NoAvailableFacilitySlotsError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except FacilityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except FacilityPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

# Professional Routes
@router.get("/professional/available", response_model=dict)
def get_facilities_for_professional(
    date: Optional[date] = Query(None, description="Filter by available date"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available facilities for professional to select"""
    try:
        service = FacilityService(db)
        return service.get_facilities_for_professional(current_user, date)
    except FacilityException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.get("/check-availability/{facility_id}")
def check_facility_availability(
    facility_id: int,
    appointment_date: datetime = Query(..., description="Appointment date and time"),
    duration_minutes: int = Query(60, ge=15, le=480, description="Duration in minutes"),
    exclude_appointment_id: Optional[int] = Query(None, description="Exclude appointment ID"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if facility is available for appointment"""
    try:
        service = FacilityService(db)
        is_available = service.check_facility_availability(
            facility_id, appointment_date, duration_minutes, exclude_appointment_id, current_user
        )
        return {
            "facility_id": facility_id,
            "appointment_date": appointment_date,
            "duration_minutes": duration_minutes,
            "is_available": is_available
        }
    except FacilityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except FacilityPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        ) 