from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import date
from neomediapi.infra.db.models.medical_record_model import MedicalRecord
from neomediapi.domain.medical_record.dtos.medical_record_dto import MedicalRecordSearchDTO
from neomediapi.enums.medical_record_types import MedicalRecordType
from neomediapi.enums.medical_record_status import MedicalRecordStatus

class MedicalRecordRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, medical_record_data: dict) -> MedicalRecord:
        """Create a new medical record"""
        medical_record = MedicalRecord(**medical_record_data)
        self.db.add(medical_record)
        self.db.commit()
        self.db.refresh(medical_record)
        return medical_record
    
    def get_by_id(self, medical_record_id: int) -> Optional[MedicalRecord]:
        """Get medical record by ID"""
        return self.db.query(MedicalRecord).filter(
            and_(
                MedicalRecord.id == medical_record_id,
                MedicalRecord.is_deleted == False
            )
        ).first()
    
    def get_by_record_number(self, record_number: str) -> Optional[MedicalRecord]:
        """Get medical record by record number"""
        return self.db.query(MedicalRecord).filter(
            and_(
                MedicalRecord.record_number == record_number,
                MedicalRecord.is_deleted == False
            )
        ).first()
    
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[MedicalRecord]:
        """Get all medical records with pagination"""
        query = self.db.query(MedicalRecord).filter(MedicalRecord.is_deleted == False)
        
        if active_only:
            query = query.filter(MedicalRecord.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    def get_by_patient(
        self, 
        patient_id: int, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[MedicalRecord]:
        """Get medical records by patient ID"""
        query = self.db.query(MedicalRecord).filter(
            and_(
                MedicalRecord.patient_id == patient_id,
                MedicalRecord.is_deleted == False
            )
        )
        
        if active_only:
            query = query.filter(MedicalRecord.is_active == True)
        
        return query.order_by(desc(MedicalRecord.created_at)).offset(skip).limit(limit).all()
    
    def get_by_professional(
        self, 
        professional_id: int, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[MedicalRecord]:
        """Get medical records by professional ID"""
        query = self.db.query(MedicalRecord).filter(
            and_(
                MedicalRecord.professional_id == professional_id,
                MedicalRecord.is_deleted == False
            )
        )
        
        if active_only:
            query = query.filter(MedicalRecord.is_active == True)
        
        return query.order_by(desc(MedicalRecord.created_at)).offset(skip).limit(limit).all()
    
    def get_by_company(
        self, 
        company_id: int, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[MedicalRecord]:
        """Get medical records by company ID"""
        query = self.db.query(MedicalRecord).filter(
            and_(
                MedicalRecord.company_id == company_id,
                MedicalRecord.is_deleted == False
            )
        )
        
        if active_only:
            query = query.filter(MedicalRecord.is_active == True)
        
        return query.order_by(desc(MedicalRecord.created_at)).offset(skip).limit(limit).all()
    
    def search(
        self, 
        search_dto: MedicalRecordSearchDTO,
        skip: int = 0, 
        limit: int = 100
    ) -> List[MedicalRecord]:
        """Search medical records with filters"""
        query = self.db.query(MedicalRecord).filter(MedicalRecord.is_deleted == False)
        
        # Text search
        if search_dto.query:
            search_term = f"%{search_dto.query}%"
            query = query.filter(
                or_(
                    MedicalRecord.title.ilike(search_term),
                    MedicalRecord.description.ilike(search_term),
                    MedicalRecord.record_number.ilike(search_term),
                    MedicalRecord.chief_complaint.ilike(search_term),
                    MedicalRecord.diagnosis.ilike(search_term),
                    MedicalRecord.notes.ilike(search_term)
                )
            )
        
        # Filter by record type
        if search_dto.record_type:
            query = query.filter(MedicalRecord.record_type == search_dto.record_type)
        
        # Filter by status
        if search_dto.status:
            query = query.filter(MedicalRecord.status == search_dto.status)
        
        # Filter by patient
        if search_dto.patient_id:
            query = query.filter(MedicalRecord.patient_id == search_dto.patient_id)
        
        # Filter by professional
        if search_dto.professional_id:
            query = query.filter(MedicalRecord.professional_id == search_dto.professional_id)
        
        # Filter by company
        if search_dto.company_id:
            query = query.filter(MedicalRecord.company_id == search_dto.company_id)
        
        # Filter by consultation date range
        if search_dto.consultation_date_from:
            query = query.filter(MedicalRecord.consultation_date >= search_dto.consultation_date_from)
        
        if search_dto.consultation_date_to:
            query = query.filter(MedicalRecord.consultation_date <= search_dto.consultation_date_to)
        
        # Filter by confidentiality
        if search_dto.is_confidential is not None:
            query = query.filter(MedicalRecord.is_confidential == search_dto.is_confidential)
        
        # Filter by active status
        if search_dto.is_active is not None:
            query = query.filter(MedicalRecord.is_active == search_dto.is_active)
        
        return query.order_by(desc(MedicalRecord.created_at)).offset(skip).limit(limit).all()
    
    def get_by_type(
        self, 
        record_type: MedicalRecordType,
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[MedicalRecord]:
        """Get medical records by type"""
        query = self.db.query(MedicalRecord).filter(
            and_(
                MedicalRecord.record_type == record_type,
                MedicalRecord.is_deleted == False
            )
        )
        
        if active_only:
            query = query.filter(MedicalRecord.is_active == True)
        
        return query.order_by(desc(MedicalRecord.created_at)).offset(skip).limit(limit).all()
    
    def get_by_status(
        self, 
        status: MedicalRecordStatus,
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[MedicalRecord]:
        """Get medical records by status"""
        query = self.db.query(MedicalRecord).filter(
            and_(
                MedicalRecord.status == status,
                MedicalRecord.is_deleted == False
            )
        )
        
        if active_only:
            query = query.filter(MedicalRecord.is_active == True)
        
        return query.order_by(desc(MedicalRecord.created_at)).offset(skip).limit(limit).all()
    
    def get_confidential_records(
        self,
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[MedicalRecord]:
        """Get confidential medical records"""
        query = self.db.query(MedicalRecord).filter(
            and_(
                MedicalRecord.is_confidential == True,
                MedicalRecord.is_deleted == False
            )
        )
        
        if active_only:
            query = query.filter(MedicalRecord.is_active == True)
        
        return query.order_by(desc(MedicalRecord.created_at)).offset(skip).limit(limit).all()
    
    def update(self, medical_record_id: int, update_data: dict) -> Optional[MedicalRecord]:
        """Update medical record"""
        medical_record = self.get_by_id(medical_record_id)
        if not medical_record:
            return None
        
        for key, value in update_data.items():
            setattr(medical_record, key, value)
        
        self.db.commit()
        self.db.refresh(medical_record)
        return medical_record
    
    def soft_delete(self, medical_record_id: int) -> bool:
        """Soft delete medical record"""
        medical_record = self.get_by_id(medical_record_id)
        if not medical_record:
            return False
        
        medical_record.soft_delete()
        self.db.commit()
        return True
    
    def restore(self, medical_record_id: int) -> bool:
        """Restore soft deleted medical record"""
        medical_record = self.db.query(MedicalRecord).filter(
            and_(
                MedicalRecord.id == medical_record_id,
                MedicalRecord.is_deleted == True
            )
        ).first()
        
        if not medical_record:
            return False
        
        medical_record.restore()
        self.db.commit()
        return True
    
    def hard_delete(self, medical_record_id: int) -> bool:
        """Hard delete medical record"""
        medical_record = self.get_by_id(medical_record_id)
        if not medical_record:
            return False
        
        self.db.delete(medical_record)
        self.db.commit()
        return True
    
    def count_by_patient(self, patient_id: int, active_only: bool = True) -> int:
        """Count medical records by patient"""
        query = self.db.query(MedicalRecord).filter(
            and_(
                MedicalRecord.patient_id == patient_id,
                MedicalRecord.is_deleted == False
            )
        )
        
        if active_only:
            query = query.filter(MedicalRecord.is_active == True)
        
        return query.count()
    
    def count_by_professional(self, professional_id: int, active_only: bool = True) -> int:
        """Count medical records by professional"""
        query = self.db.query(MedicalRecord).filter(
            and_(
                MedicalRecord.professional_id == professional_id,
                MedicalRecord.is_deleted == False
            )
        )
        
        if active_only:
            query = query.filter(MedicalRecord.is_active == True)
        
        return query.count()
    
    def count_by_company(self, company_id: int, active_only: bool = True) -> int:
        """Count medical records by company"""
        query = self.db.query(MedicalRecord).filter(
            and_(
                MedicalRecord.company_id == company_id,
                MedicalRecord.is_deleted == False
            )
        )
        
        if active_only:
            query = query.filter(MedicalRecord.is_active == True)
        
        return query.count()
    
    def get_next_record_number(self) -> str:
        """Generate next record number"""
        # Get the last record number and increment it
        last_record = self.db.query(MedicalRecord).order_by(
            desc(MedicalRecord.record_number)
        ).first()
        
        if not last_record:
            return "MR000001"
        
        try:
            # Extract number from record number (e.g., "MR000001" -> 1)
            number_part = last_record.record_number[2:]  # Remove "MR" prefix
            next_number = int(number_part) + 1
            return f"MR{next_number:06d}"
        except (ValueError, IndexError):
            # Fallback if record number format is invalid
            return f"MR{1:06d}" 