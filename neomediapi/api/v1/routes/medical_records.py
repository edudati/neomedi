from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from neomediapi.infra.db.session import get_db
from neomediapi.auth.dependencies import get_current_user
from neomediapi.auth.authenticated_user import AuthenticatedUser
from neomediapi.services.medical_record_service import MedicalRecordService
from neomediapi.domain.medical_record.dtos.medical_record_dto import (
    MedicalRecordCreateDTO,
    MedicalRecordUpdateDTO,
    MedicalRecordResponseDTO,
    MedicalRecordListResponseDTO,
    MedicalRecordSearchDTO,
    MedicalRecordStatusUpdateDTO,
    MedicalRecordConfidentialityUpdateDTO
)
from neomediapi.domain.medical_record.exceptions import (
    MedicalRecordError,
    MedicalRecordNotFoundError,
    MedicalRecordValidationError,
    MedicalRecordAlreadyExistsError,
    MedicalRecordPermissionError,
    MedicalRecordConfidentialityError,
    MedicalRecordStatusError,
    MedicalRecordNumberGenerationError,
    MedicalRecordPatientNotFoundError,
    MedicalRecordProfessionalNotFoundError,
    MedicalRecordCompanyNotFoundError
)
from neomediapi.enums.medical_record_types import MedicalRecordType
from neomediapi.enums.medical_record_status import MedicalRecordStatus

router = APIRouter()

@router.post("/", response_model=MedicalRecordResponseDTO, status_code=201)
async def create_medical_record(
    create_dto: MedicalRecordCreateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new medical record"""
    try:
        medical_record_service = MedicalRecordService(db)
        return medical_record_service.create_medical_record(create_dto, current_user.user_id)
    except MedicalRecordError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{medical_record_id}", response_model=MedicalRecordResponseDTO)
async def get_medical_record(
    medical_record_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get medical record by ID"""
    try:
        medical_record_service = MedicalRecordService(db)
        return medical_record_service.get_medical_record(medical_record_id, current_user.user_id)
    except MedicalRecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MedicalRecordPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except MedicalRecordConfidentialityError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except MedicalRecordError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/patient/{patient_id}", response_model=List[MedicalRecordListResponseDTO])
async def get_medical_records_by_patient(
    patient_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get medical records by patient ID"""
    try:
        medical_record_service = MedicalRecordService(db)
        return medical_record_service.get_medical_records_by_patient(
            patient_id, current_user.user_id, skip, limit
        )
    except MedicalRecordPatientNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MedicalRecordPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except MedicalRecordError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/professional/{professional_id}", response_model=List[MedicalRecordListResponseDTO])
async def get_medical_records_by_professional(
    professional_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get medical records by professional ID"""
    try:
        medical_record_service = MedicalRecordService(db)
        return medical_record_service.get_medical_records_by_professional(
            professional_id, current_user.user_id, skip, limit
        )
    except MedicalRecordProfessionalNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MedicalRecordPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except MedicalRecordError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/search/", response_model=List[MedicalRecordListResponseDTO])
async def search_medical_records(
    query: str = Query(None, description="Search term"),
    record_type: MedicalRecordType = Query(None, description="Filter by record type"),
    status: MedicalRecordStatus = Query(None, description="Filter by status"),
    patient_id: int = Query(None, gt=0, description="Filter by patient ID"),
    professional_id: int = Query(None, gt=0, description="Filter by professional ID"),
    company_id: int = Query(None, gt=0, description="Filter by company ID"),
    consultation_date_from: str = Query(None, description="Filter by consultation date from (YYYY-MM-DD)"),
    consultation_date_to: str = Query(None, description="Filter by consultation date to (YYYY-MM-DD)"),
    is_confidential: bool = Query(None, description="Filter by confidentiality"),
    is_active: bool = Query(True, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search medical records with filters"""
    try:
        # Parse date strings
        from datetime import datetime
        parsed_date_from = None
        parsed_date_to = None
        
        if consultation_date_from:
            try:
                parsed_date_from = datetime.strptime(consultation_date_from, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid consultation_date_from format. Use YYYY-MM-DD")
        
        if consultation_date_to:
            try:
                parsed_date_to = datetime.strptime(consultation_date_to, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid consultation_date_to format. Use YYYY-MM-DD")
        
        search_dto = MedicalRecordSearchDTO(
            query=query,
            record_type=record_type,
            status=status,
            patient_id=patient_id,
            professional_id=professional_id,
            company_id=company_id,
            consultation_date_from=parsed_date_from,
            consultation_date_to=parsed_date_to,
            is_confidential=is_confidential,
            is_active=is_active
        )
        
        medical_record_service = MedicalRecordService(db)
        return medical_record_service.search_medical_records(
            search_dto, current_user.user_id, skip, limit
        )
    except MedicalRecordPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except MedicalRecordError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/{medical_record_id}", response_model=MedicalRecordResponseDTO)
async def update_medical_record(
    medical_record_id: int,
    update_dto: MedicalRecordUpdateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update medical record"""
    try:
        medical_record_service = MedicalRecordService(db)
        return medical_record_service.update_medical_record(
            medical_record_id, update_dto, current_user.user_id
        )
    except MedicalRecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MedicalRecordPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except MedicalRecordStatusError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MedicalRecordError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/{medical_record_id}/status", response_model=MedicalRecordResponseDTO)
async def update_medical_record_status(
    medical_record_id: int,
    status_dto: MedicalRecordStatusUpdateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update medical record status"""
    try:
        medical_record_service = MedicalRecordService(db)
        return medical_record_service.update_medical_record_status(
            medical_record_id, status_dto, current_user.user_id
        )
    except MedicalRecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MedicalRecordPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except MedicalRecordStatusError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MedicalRecordError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/{medical_record_id}/confidentiality", response_model=MedicalRecordResponseDTO)
async def update_medical_record_confidentiality(
    medical_record_id: int,
    confidentiality_dto: MedicalRecordConfidentialityUpdateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update medical record confidentiality"""
    try:
        medical_record_service = MedicalRecordService(db)
        return medical_record_service.update_medical_record_confidentiality(
            medical_record_id, confidentiality_dto, current_user.user_id
        )
    except MedicalRecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MedicalRecordPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except MedicalRecordError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{medical_record_id}", status_code=204)
async def delete_medical_record(
    medical_record_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete medical record"""
    try:
        medical_record_service = MedicalRecordService(db)
        success = medical_record_service.soft_delete_medical_record(
            medical_record_id, current_user.user_id
        )
        if not success:
            raise HTTPException(status_code=404, detail="Medical record not found")
    except MedicalRecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MedicalRecordPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except MedicalRecordError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{medical_record_id}/restore", response_model=MedicalRecordResponseDTO)
async def restore_medical_record(
    medical_record_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restore soft deleted medical record"""
    try:
        medical_record_service = MedicalRecordService(db)
        success = medical_record_service.restore_medical_record(
            medical_record_id, current_user.user_id
        )
        if not success:
            raise HTTPException(status_code=404, detail="Medical record not found")
        
        # Return the restored record
        return medical_record_service.get_medical_record(medical_record_id, current_user.user_id)
    except MedicalRecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MedicalRecordPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except MedicalRecordError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/types/", response_model=List[str])
async def get_medical_record_types():
    """Get all available medical record types"""
    return [record_type.value for record_type in MedicalRecordType]

@router.get("/statuses/", response_model=List[str])
async def get_medical_record_statuses():
    """Get all available medical record statuses"""
    return [status.value for status in MedicalRecordStatus] 