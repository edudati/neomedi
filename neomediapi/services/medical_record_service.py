from typing import List, Optional
from sqlalchemy.orm import Session
from neomediapi.infra.db.repositories.medical_record_repository import MedicalRecordRepository
from neomediapi.infra.db.repositories.user_repository import UserRepository
from neomediapi.infra.db.repositories.company_repository import CompanyRepository
from neomediapi.domain.medical_record.dtos.medical_record_dto import (
    MedicalRecordCreateDTO,
    MedicalRecordUpdateDTO,
    MedicalRecordResponseDTO,
    MedicalRecordListResponseDTO,
    MedicalRecordSearchDTO,
    MedicalRecordStatusUpdateDTO,
    MedicalRecordConfidentialityUpdateDTO
)
from neomediapi.domain.medical_record.mappers.medical_record_mapper import (
    map_medical_record_create_dto_to_model,
    map_medical_record_update_dto_to_model,
    map_medical_record_model_to_response_dto,
    map_medical_record_model_to_list_response_dto,
    map_medical_record_models_to_list_response_dtos
)
from neomediapi.domain.medical_record.exceptions import (
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
from neomediapi.enums.user_profiles import UserProfile
from neomediapi.enums.medical_record_status import MedicalRecordStatus

class MedicalRecordService:
    def __init__(self, db: Session):
        self.db = db
        self.medical_record_repository = MedicalRecordRepository(db)
        self.user_repository = UserRepository(db)
        self.company_repository = CompanyRepository(db)
    
    def create_medical_record(
        self, 
        create_dto: MedicalRecordCreateDTO,
        current_user_id: int
    ) -> MedicalRecordResponseDTO:
        """Create a new medical record"""
        # Validate patient exists and is a client
        patient = self.user_repository.get_by_id(create_dto.patient_id)
        if not patient:
            raise MedicalRecordPatientNotFoundError(f"Patient with ID {create_dto.patient_id} not found")
        
        if patient.profile != UserProfile.CLIENT:
            raise MedicalRecordValidationError("Patient must have CLIENT profile")
        
        # Validate professional exists and is a professional
        professional = self.user_repository.get_by_id(create_dto.professional_id)
        if not professional:
            raise MedicalRecordProfessionalNotFoundError(f"Professional with ID {create_dto.professional_id} not found")
        
        if not professional.profile in [UserProfile.PROFESSIONAL, UserProfile.MANAGER, UserProfile.ADMIN, UserProfile.SUPER]:
            raise MedicalRecordValidationError("Professional must have PROFESSIONAL, MANAGER, ADMIN, or SUPER profile")
        
        # Validate company if provided
        if create_dto.company_id:
            company = self.company_repository.get_by_id(create_dto.company_id)
            if not company:
                raise MedicalRecordCompanyNotFoundError(f"Company with ID {create_dto.company_id} not found")
        
        # Check permissions
        current_user = self.user_repository.get_by_id(current_user_id)
        if not current_user:
            raise MedicalRecordPermissionError("Current user not found")
        
        # Only professionals, managers, admins, and super can create medical records
        if not current_user.profile in [UserProfile.PROFESSIONAL, UserProfile.MANAGER, UserProfile.ADMIN, UserProfile.SUPER]:
            raise MedicalRecordPermissionError("Only professionals, managers, admins, and super can create medical records")
        
        # Generate record number
        try:
            record_number = self.medical_record_repository.get_next_record_number()
        except Exception as e:
            raise MedicalRecordNumberGenerationError(f"Failed to generate record number: {str(e)}")
        
        # Create medical record data
        medical_record_data = map_medical_record_create_dto_to_model(create_dto)
        medical_record_data["record_number"] = record_number
        
        # Create medical record
        medical_record = self.medical_record_repository.create(medical_record_data)
        
        return map_medical_record_model_to_response_dto(medical_record)
    
    def get_medical_record(
        self, 
        medical_record_id: int,
        current_user_id: int
    ) -> MedicalRecordResponseDTO:
        """Get medical record by ID with permission check"""
        medical_record = self.medical_record_repository.get_by_id(medical_record_id)
        if not medical_record:
            raise MedicalRecordNotFoundError(f"Medical record with ID {medical_record_id} not found")
        
        # Check permissions
        current_user = self.user_repository.get_by_id(current_user_id)
        if not current_user:
            raise MedicalRecordPermissionError("Current user not found")
        
        # Check if user can access this medical record
        if not self._can_access_medical_record(current_user, medical_record):
            raise MedicalRecordPermissionError("User does not have permission to access this medical record")
        
        # Check confidentiality
        if medical_record.is_confidential and not self._can_access_confidential_record(current_user):
            raise MedicalRecordConfidentialityError("User does not have permission to access confidential medical records")
        
        return map_medical_record_model_to_response_dto(medical_record)
    
    def get_medical_records_by_patient(
        self, 
        patient_id: int,
        current_user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[MedicalRecordListResponseDTO]:
        """Get medical records by patient with permission check"""
        # Check permissions
        current_user = self.user_repository.get_by_id(current_user_id)
        if not current_user:
            raise MedicalRecordPermissionError("Current user not found")
        
        # Validate patient exists
        patient = self.user_repository.get_by_id(patient_id)
        if not patient:
            raise MedicalRecordPatientNotFoundError(f"Patient with ID {patient_id} not found")
        
        # Check if user can access patient's records
        if not self._can_access_patient_records(current_user, patient):
            raise MedicalRecordPermissionError("User does not have permission to access patient's medical records")
        
        medical_records = self.medical_record_repository.get_by_patient(patient_id, skip, limit)
        
        # Filter confidential records if user doesn't have permission
        if not self._can_access_confidential_record(current_user):
            medical_records = [record for record in medical_records if not record.is_confidential]
        
        return map_medical_record_models_to_list_response_dtos(medical_records)
    
    def get_medical_records_by_professional(
        self, 
        professional_id: int,
        current_user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[MedicalRecordListResponseDTO]:
        """Get medical records by professional with permission check"""
        # Check permissions
        current_user = self.user_repository.get_by_id(current_user_id)
        if not current_user:
            raise MedicalRecordPermissionError("Current user not found")
        
        # Validate professional exists
        professional = self.user_repository.get_by_id(professional_id)
        if not professional:
            raise MedicalRecordProfessionalNotFoundError(f"Professional with ID {professional_id} not found")
        
        # Check if user can access professional's records
        if not self._can_access_professional_records(current_user, professional):
            raise MedicalRecordPermissionError("User does not have permission to access professional's medical records")
        
        medical_records = self.medical_record_repository.get_by_professional(professional_id, skip, limit)
        
        # Filter confidential records if user doesn't have permission
        if not self._can_access_confidential_record(current_user):
            medical_records = [record for record in medical_records if not record.is_confidential]
        
        return map_medical_record_models_to_list_response_dtos(medical_records)
    
    def search_medical_records(
        self,
        search_dto: MedicalRecordSearchDTO,
        current_user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[MedicalRecordListResponseDTO]:
        """Search medical records with permission check"""
        # Check permissions
        current_user = self.user_repository.get_by_id(current_user_id)
        if not current_user:
            raise MedicalRecordPermissionError("Current user not found")
        
        # Only professionals, managers, admins, and super can search medical records
        if not current_user.profile in [UserProfile.PROFESSIONAL, UserProfile.MANAGER, UserProfile.ADMIN, UserProfile.SUPER]:
            raise MedicalRecordPermissionError("Only professionals, managers, admins, and super can search medical records")
        
        medical_records = self.medical_record_repository.search(search_dto, skip, limit)
        
        # Filter confidential records if user doesn't have permission
        if not self._can_access_confidential_record(current_user):
            medical_records = [record for record in medical_records if not record.is_confidential]
        
        return map_medical_record_models_to_list_response_dtos(medical_records)
    
    def update_medical_record(
        self,
        medical_record_id: int,
        update_dto: MedicalRecordUpdateDTO,
        current_user_id: int
    ) -> MedicalRecordResponseDTO:
        """Update medical record with permission check"""
        medical_record = self.medical_record_repository.get_by_id(medical_record_id)
        if not medical_record:
            raise MedicalRecordNotFoundError(f"Medical record with ID {medical_record_id} not found")
        
        # Check permissions
        current_user = self.user_repository.get_by_id(current_user_id)
        if not current_user:
            raise MedicalRecordPermissionError("Current user not found")
        
        # Check if user can update this medical record
        if not self._can_update_medical_record(current_user, medical_record):
            raise MedicalRecordPermissionError("User does not have permission to update this medical record")
        
        # Validate status transition if status is being updated
        if update_dto.status and update_dto.status != medical_record.status:
            if not self._is_valid_status_transition(medical_record.status, update_dto.status):
                raise MedicalRecordStatusError(f"Invalid status transition from {medical_record.status} to {update_dto.status}")
        
        # Update medical record
        update_data = map_medical_record_update_dto_to_model(update_dto)
        updated_record = self.medical_record_repository.update(medical_record_id, update_data)
        
        if not updated_record:
            raise MedicalRecordNotFoundError(f"Medical record with ID {medical_record_id} not found")
        
        return map_medical_record_model_to_response_dto(updated_record)
    
    def update_medical_record_status(
        self,
        medical_record_id: int,
        status_dto: MedicalRecordStatusUpdateDTO,
        current_user_id: int
    ) -> MedicalRecordResponseDTO:
        """Update medical record status with permission check"""
        medical_record = self.medical_record_repository.get_by_id(medical_record_id)
        if not medical_record:
            raise MedicalRecordNotFoundError(f"Medical record with ID {medical_record_id} not found")
        
        # Check permissions
        current_user = self.user_repository.get_by_id(current_user_id)
        if not current_user:
            raise MedicalRecordPermissionError("Current user not found")
        
        # Check if user can update this medical record
        if not self._can_update_medical_record(current_user, medical_record):
            raise MedicalRecordPermissionError("User does not have permission to update this medical record")
        
        # Validate status transition
        if not self._is_valid_status_transition(medical_record.status, status_dto.status):
            raise MedicalRecordStatusError(f"Invalid status transition from {medical_record.status} to {status_dto.status}")
        
        # Update status
        update_data = {"status": status_dto.status}
        updated_record = self.medical_record_repository.update(medical_record_id, update_data)
        
        if not updated_record:
            raise MedicalRecordNotFoundError(f"Medical record with ID {medical_record_id} not found")
        
        return map_medical_record_model_to_response_dto(updated_record)
    
    def update_medical_record_confidentiality(
        self,
        medical_record_id: int,
        confidentiality_dto: MedicalRecordConfidentialityUpdateDTO,
        current_user_id: int
    ) -> MedicalRecordResponseDTO:
        """Update medical record confidentiality with permission check"""
        medical_record = self.medical_record_repository.get_by_id(medical_record_id)
        if not medical_record:
            raise MedicalRecordNotFoundError(f"Medical record with ID {medical_record_id} not found")
        
        # Check permissions
        current_user = self.user_repository.get_by_id(current_user_id)
        if not current_user:
            raise MedicalRecordPermissionError("Current user not found")
        
        # Only managers, admins, and super can change confidentiality
        if not current_user.profile in [UserProfile.MANAGER, UserProfile.ADMIN, UserProfile.SUPER]:
            raise MedicalRecordPermissionError("Only managers, admins, and super can change medical record confidentiality")
        
        # Update confidentiality
        update_data = {"is_confidential": confidentiality_dto.is_confidential}
        updated_record = self.medical_record_repository.update(medical_record_id, update_data)
        
        if not updated_record:
            raise MedicalRecordNotFoundError(f"Medical record with ID {medical_record_id} not found")
        
        return map_medical_record_model_to_response_dto(updated_record)
    
    def soft_delete_medical_record(
        self,
        medical_record_id: int,
        current_user_id: int
    ) -> bool:
        """Soft delete medical record with permission check"""
        medical_record = self.medical_record_repository.get_by_id(medical_record_id)
        if not medical_record:
            raise MedicalRecordNotFoundError(f"Medical record with ID {medical_record_id} not found")
        
        # Check permissions
        current_user = self.user_repository.get_by_id(current_user_id)
        if not current_user:
            raise MedicalRecordPermissionError("Current user not found")
        
        # Only managers, admins, and super can delete medical records
        if not current_user.profile in [UserProfile.MANAGER, UserProfile.ADMIN, UserProfile.SUPER]:
            raise MedicalRecordPermissionError("Only managers, admins, and super can delete medical records")
        
        return self.medical_record_repository.soft_delete(medical_record_id)
    
    def restore_medical_record(
        self,
        medical_record_id: int,
        current_user_id: int
    ) -> bool:
        """Restore soft deleted medical record with permission check"""
        # Check permissions
        current_user = self.user_repository.get_by_id(current_user_id)
        if not current_user:
            raise MedicalRecordPermissionError("Current user not found")
        
        # Only managers, admins, and super can restore medical records
        if not current_user.profile in [UserProfile.MANAGER, UserProfile.ADMIN, UserProfile.SUPER]:
            raise MedicalRecordPermissionError("Only managers, admins, and super can restore medical records")
        
        return self.medical_record_repository.restore(medical_record_id)
    
    # Permission helper methods
    def _can_access_medical_record(self, user, medical_record) -> bool:
        """Check if user can access medical record"""
        # Super, admin, manager can access all records
        if user.profile in [UserProfile.SUPER, UserProfile.ADMIN, UserProfile.MANAGER]:
            return True
        
        # Professional can access records they created or records of their patients
        if user.profile == UserProfile.PROFESSIONAL:
            return (medical_record.professional_id == user.id or 
                   medical_record.patient_id in [client.id for client in user.clients])
        
        # Client can only access their own records
        if user.profile == UserProfile.CLIENT:
            return medical_record.patient_id == user.id
        
        return False
    
    def _can_access_patient_records(self, user, patient) -> bool:
        """Check if user can access patient's records"""
        # Super, admin, manager can access all patient records
        if user.profile in [UserProfile.SUPER, UserProfile.ADMIN, UserProfile.MANAGER]:
            return True
        
        # Professional can access records of their patients
        if user.profile == UserProfile.PROFESSIONAL:
            return patient.id in [client.id for client in user.clients]
        
        # Client can only access their own records
        if user.profile == UserProfile.CLIENT:
            return patient.id == user.id
        
        return False
    
    def _can_access_professional_records(self, user, professional) -> bool:
        """Check if user can access professional's records"""
        # Super, admin, manager can access all professional records
        if user.profile in [UserProfile.SUPER, UserProfile.ADMIN, UserProfile.MANAGER]:
            return True
        
        # Professional can access their own records
        if user.profile == UserProfile.PROFESSIONAL:
            return professional.id == user.id
        
        return False
    
    def _can_update_medical_record(self, user, medical_record) -> bool:
        """Check if user can update medical record"""
        # Super, admin, manager can update all records
        if user.profile in [UserProfile.SUPER, UserProfile.ADMIN, UserProfile.MANAGER]:
            return True
        
        # Professional can update records they created
        if user.profile == UserProfile.PROFESSIONAL:
            return medical_record.professional_id == user.id
        
        return False
    
    def _can_access_confidential_record(self, user) -> bool:
        """Check if user can access confidential records"""
        return user.profile in [UserProfile.SUPER, UserProfile.ADMIN, UserProfile.MANAGER]
    
    def _is_valid_status_transition(self, current_status: MedicalRecordStatus, new_status: MedicalRecordStatus) -> bool:
        """Check if status transition is valid"""
        valid_transitions = {
            MedicalRecordStatus.DRAFT: [MedicalRecordStatus.IN_PROGRESS, MedicalRecordStatus.CANCELLED],
            MedicalRecordStatus.IN_PROGRESS: [MedicalRecordStatus.COMPLETED, MedicalRecordStatus.CANCELLED, MedicalRecordStatus.PENDING_REVIEW],
            MedicalRecordStatus.PENDING_REVIEW: [MedicalRecordStatus.APPROVED, MedicalRecordStatus.REJECTED, MedicalRecordStatus.IN_PROGRESS],
            MedicalRecordStatus.APPROVED: [MedicalRecordStatus.ARCHIVED],
            MedicalRecordStatus.REJECTED: [MedicalRecordStatus.IN_PROGRESS, MedicalRecordStatus.CANCELLED],
            MedicalRecordStatus.COMPLETED: [MedicalRecordStatus.ARCHIVED],
            MedicalRecordStatus.CANCELLED: [MedicalRecordStatus.DRAFT, MedicalRecordStatus.IN_PROGRESS],
            MedicalRecordStatus.ARCHIVED: [MedicalRecordStatus.IN_PROGRESS]  # Can be reactivated
        }
        
        return new_status in valid_transitions.get(current_status, []) 