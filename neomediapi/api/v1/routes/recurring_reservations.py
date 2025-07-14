from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from neomediapi.infra.db.session import get_db
from neomediapi.auth.dependencies import get_current_user
from neomediapi.auth.authenticated_user import AuthenticatedUser
from neomediapi.services.recurring_reservation_service import RecurringReservationService
from neomediapi.domain.facility.dtos.recurring_reservation_dto import (
    RecurringReservationCreateDTO,
    RecurringReservationUpdateDTO,
    RecurringReservationSearchDTO,
    RecurringReservationGenerationDTO,
    RecurringReservationResponseDTO,
    RecurringReservationListResponseDTO
)
from neomediapi.domain.facility.exceptions import (
    FacilityException,
    FacilityNotFoundError,
    FacilityPermissionError
)

router = APIRouter(prefix="/recurring-reservations", tags=["recurring-reservations"])

# Recurring Reservation Routes
@router.post("/", response_model=RecurringReservationResponseDTO, status_code=status.HTTP_201_CREATED)
def create_recurring_reservation(
    reservation_dto: RecurringReservationCreateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new recurring reservation"""
    try:
        service = RecurringReservationService(db)
        return service.create_recurring_reservation(reservation_dto, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": str(e), "error_code": "VALIDATION_ERROR"}
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

@router.get("/{reservation_id}", response_model=RecurringReservationResponseDTO)
def get_recurring_reservation(
    reservation_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recurring reservation by ID"""
    try:
        service = RecurringReservationService(db)
        return service.get_recurring_reservation(reservation_id, current_user)
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
def get_recurring_reservations(
    query: Optional[str] = Query(None, description="Search term"),
    professional_id: Optional[int] = Query(None, description="Professional ID"),
    facility_id: Optional[int] = Query(None, description="Facility ID"),
    company_id: Optional[int] = Query(None, description="Company ID"),
    day_of_week: Optional[int] = Query(None, ge=0, le=6, description="Day of week"),
    is_active: Optional[bool] = Query(True, description="Active reservations only"),
    skip: int = Query(0, ge=0, description="Skip records"),
    limit: int = Query(100, ge=1, le=1000, description="Limit records"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recurring reservations with search and filters"""
    try:
        search_dto = RecurringReservationSearchDTO(
            query=query,
            professional_id=professional_id,
            facility_id=facility_id,
            company_id=company_id,
            day_of_week=day_of_week,
            is_active=is_active
        )
        
        service = RecurringReservationService(db)
        return service.get_recurring_reservations(search_dto, current_user, skip, limit)
    except FacilityException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )

@router.put("/{reservation_id}", response_model=RecurringReservationResponseDTO)
def update_recurring_reservation(
    reservation_id: int,
    update_dto: RecurringReservationUpdateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update recurring reservation"""
    try:
        service = RecurringReservationService(db)
        return service.update_recurring_reservation(reservation_id, update_dto, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": str(e), "error_code": "VALIDATION_ERROR"}
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

@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring_reservation(
    reservation_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete recurring reservation"""
    try:
        service = RecurringReservationService(db)
        service.delete_recurring_reservation(reservation_id, current_user)
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

# Generation Routes
@router.post("/{reservation_id}/generate", response_model=dict)
def generate_appointments_from_reservation(
    reservation_id: int,
    generation_dto: RecurringReservationGenerationDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate appointments from recurring reservation"""
    try:
        service = RecurringReservationService(db)
        return service.generate_appointments_from_reservation(reservation_id, generation_dto, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": str(e), "error_code": "VALIDATION_ERROR"}
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
@router.get("/professional/my-reservations", response_model=dict)
def get_my_recurring_reservations(
    skip: int = Query(0, ge=0, description="Skip records"),
    limit: int = Query(100, ge=1, le=1000, description="Limit records"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's recurring reservations"""
    try:
        search_dto = RecurringReservationSearchDTO(professional_id=current_user.user_id)
        service = RecurringReservationService(db)
        return service.get_recurring_reservations(search_dto, current_user, skip, limit)
    except FacilityException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        ) 