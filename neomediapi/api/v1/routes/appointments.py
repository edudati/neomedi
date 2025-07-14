from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from neomediapi.infra.db.session import get_db
from neomediapi.auth.dependencies import get_current_user
from neomediapi.auth.authenticated_user import AuthenticatedUser
from neomediapi.services.appointment_service import AppointmentService
from neomediapi.domain.appointment.dtos.appointment_dto import (
    AppointmentCreateDTO,
    AppointmentUpdateDTO,
    AppointmentSearchDTO,
    AppointmentStatusUpdateDTO,
    AppointmentResponseDTO,
    AppointmentListResponseDTO,
    ProfessionalAvailabilityCreateDTO,
    ProfessionalAvailabilityUpdateDTO,
    ProfessionalAvailabilityResponseDTO,
    AvailableSlotsResponseDTO
)
from neomediapi.domain.appointment.exceptions import (
    AppointmentException,
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

router = APIRouter(prefix="/appointments", tags=["appointments"])

# Appointment Routes
@router.post("/", response_model=AppointmentResponseDTO, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_dto: AppointmentCreateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new appointment"""
    try:
        service = AppointmentService(db)
        return service.create_appointment(appointment_dto, current_user)
    except AppointmentException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.get("/{appointment_id}", response_model=AppointmentResponseDTO)
def get_appointment(
    appointment_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get appointment by ID"""
    try:
        service = AppointmentService(db)
        return service.get_appointment(appointment_id, current_user)
    except AppointmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except AppointmentPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.get("/", response_model=dict)
def get_appointments(
    query: Optional[str] = Query(None, description="Search term"),
    appointment_type: Optional[str] = Query(None, description="Appointment type"),
    status: Optional[str] = Query(None, description="Appointment status"),
    patient_id: Optional[int] = Query(None, description="Patient ID"),
    professional_id: Optional[int] = Query(None, description="Professional ID"),
    company_id: Optional[int] = Query(None, description="Company ID"),
    date_from: Optional[date] = Query(None, description="Start date"),
    date_to: Optional[date] = Query(None, description="End date"),
    is_active: Optional[bool] = Query(True, description="Active appointments only"),
    skip: int = Query(0, ge=0, description="Skip records"),
    limit: int = Query(100, ge=1, le=1000, description="Limit records"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get appointments with search and filters"""
    try:
        search_dto = AppointmentSearchDTO(
            query=query,
            appointment_type=appointment_type,
            status=status,
            patient_id=patient_id,
            professional_id=professional_id,
            company_id=company_id,
            date_from=date_from,
            date_to=date_to,
            is_active=is_active
        )
        
        service = AppointmentService(db)
        return service.get_appointments(search_dto, current_user, skip, limit)
    except AppointmentException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.put("/{appointment_id}", response_model=AppointmentResponseDTO)
def update_appointment(
    appointment_id: int,
    update_dto: AppointmentUpdateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update appointment"""
    try:
        service = AppointmentService(db)
        return service.update_appointment(appointment_id, update_dto, current_user)
    except AppointmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except (AppointmentTimeConflictError, AppointmentPastDateError, AppointmentInvalidDurationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except AppointmentPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.patch("/{appointment_id}/status", response_model=AppointmentResponseDTO)
def update_appointment_status(
    appointment_id: int,
    status_dto: AppointmentStatusUpdateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update appointment status"""
    try:
        service = AppointmentService(db)
        return service.update_appointment_status(appointment_id, status_dto, current_user)
    except AppointmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except AppointmentInvalidStatusTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except AppointmentPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete appointment"""
    try:
        service = AppointmentService(db)
        service.delete_appointment(appointment_id, current_user)
    except AppointmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except AppointmentPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.get("/upcoming/me", response_model=dict)
def get_my_upcoming_appointments(
    limit: int = Query(10, ge=1, le=100, description="Limit records"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's upcoming appointments"""
    try:
        service = AppointmentService(db)
        return service.get_upcoming_appointments(current_user, limit)
    except AppointmentException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )

# Professional Availability Routes
@router.post("/availability", response_model=ProfessionalAvailabilityResponseDTO, status_code=status.HTTP_201_CREATED)
def create_professional_availability(
    availability_dto: ProfessionalAvailabilityCreateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create professional availability"""
    try:
        service = AppointmentService(db)
        return service.create_professional_availability(availability_dto, current_user)
    except (ProfessionalAvailabilityConflictError, ProfessionalAvailabilityInvalidTimeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except AppointmentPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.get("/availability/{professional_id}", response_model=dict)
def get_professional_availabilities(
    professional_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get professional availabilities"""
    try:
        service = AppointmentService(db)
        return service.get_professional_availabilities(professional_id, current_user)
    except AppointmentPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.put("/availability/{availability_id}", response_model=ProfessionalAvailabilityResponseDTO)
def update_professional_availability(
    availability_id: int,
    update_dto: ProfessionalAvailabilityUpdateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update professional availability"""
    try:
        service = AppointmentService(db)
        return service.update_professional_availability(availability_id, update_dto, current_user)
    except ProfessionalAvailabilityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except ProfessionalAvailabilityInvalidTimeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except AppointmentPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.delete("/availability/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_professional_availability(
    availability_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete professional availability"""
    try:
        service = AppointmentService(db)
        service.delete_professional_availability(availability_id, current_user)
    except ProfessionalAvailabilityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except AppointmentPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        )

# Available Slots Routes
@router.get("/slots/{professional_id}", response_model=AvailableSlotsResponseDTO)
def get_available_slots(
    professional_id: int,
    date: date = Query(..., description="Target date"),
    duration_minutes: int = Query(60, ge=15, le=480, description="Duration in minutes"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available time slots for a professional"""
    try:
        service = AppointmentService(db)
        return service.get_available_slots(professional_id, date, duration_minutes, current_user)
    except NoAvailableSlotsError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except AppointmentPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "error_code": e.error_code}
        ) 