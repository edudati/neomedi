from datetime import datetime
from typing import List
from neomediapi.infra.db.models.medical_record_model import MedicalRecord
from neomediapi.domain.medical_record.dtos.medical_record_dto import (
    MedicalRecordCreateDTO,
    MedicalRecordUpdateDTO,
    MedicalRecordResponseDTO,
    MedicalRecordListResponseDTO
)

def map_medical_record_create_dto_to_model(dto: MedicalRecordCreateDTO) -> dict:
    """Map MedicalRecordCreateDTO to MedicalRecord model attributes"""
    return {
        "title": dto.title,
        "description": dto.description,
        "record_type": dto.record_type,
        "consultation_date": dto.consultation_date,
        "next_appointment": dto.next_appointment,
        "is_confidential": dto.is_confidential,
        "chief_complaint": dto.chief_complaint,
        "present_illness": dto.present_illness,
        "past_medical_history": dto.past_medical_history,
        "family_history": dto.family_history,
        "social_history": dto.social_history,
        "medications": dto.medications,
        "allergies": dto.allergies,
        "vital_signs": dto.vital_signs,
        "physical_examination": dto.physical_examination,
        "diagnosis": dto.diagnosis,
        "treatment_plan": dto.treatment_plan,
        "prescriptions": dto.prescriptions,
        "notes": dto.notes,
        "patient_id": dto.patient_id,
        "professional_id": dto.professional_id,
        "company_id": dto.company_id
    }

def map_medical_record_update_dto_to_model(dto: MedicalRecordUpdateDTO) -> dict:
    """Map MedicalRecordUpdateDTO to MedicalRecord model attributes"""
    update_data = {}
    
    if dto.title is not None:
        update_data["title"] = dto.title
    if dto.description is not None:
        update_data["description"] = dto.description
    if dto.record_type is not None:
        update_data["record_type"] = dto.record_type
    if dto.status is not None:
        update_data["status"] = dto.status
    if dto.consultation_date is not None:
        update_data["consultation_date"] = dto.consultation_date
    if dto.next_appointment is not None:
        update_data["next_appointment"] = dto.next_appointment
    if dto.is_confidential is not None:
        update_data["is_confidential"] = dto.is_confidential
    
    # Medical information fields
    if dto.chief_complaint is not None:
        update_data["chief_complaint"] = dto.chief_complaint
    if dto.present_illness is not None:
        update_data["present_illness"] = dto.present_illness
    if dto.past_medical_history is not None:
        update_data["past_medical_history"] = dto.past_medical_history
    if dto.family_history is not None:
        update_data["family_history"] = dto.family_history
    if dto.social_history is not None:
        update_data["social_history"] = dto.social_history
    if dto.medications is not None:
        update_data["medications"] = dto.medications
    if dto.allergies is not None:
        update_data["allergies"] = dto.allergies
    if dto.vital_signs is not None:
        update_data["vital_signs"] = dto.vital_signs
    if dto.physical_examination is not None:
        update_data["physical_examination"] = dto.physical_examination
    if dto.diagnosis is not None:
        update_data["diagnosis"] = dto.diagnosis
    if dto.treatment_plan is not None:
        update_data["treatment_plan"] = dto.treatment_plan
    if dto.prescriptions is not None:
        update_data["prescriptions"] = dto.prescriptions
    if dto.notes is not None:
        update_data["notes"] = dto.notes
    
    return update_data

def map_medical_record_model_to_response_dto(model: MedicalRecord) -> MedicalRecordResponseDTO:
    """Map MedicalRecord model to MedicalRecordResponseDTO"""
    return MedicalRecordResponseDTO(
        id=model.id,
        record_number=model.record_number,
        title=model.title,
        description=model.description,
        record_type=model.record_type,
        status=model.status,
        consultation_date=model.consultation_date,
        next_appointment=model.next_appointment,
        is_confidential=model.is_confidential,
        chief_complaint=model.chief_complaint,
        present_illness=model.present_illness,
        past_medical_history=model.past_medical_history,
        family_history=model.family_history,
        social_history=model.social_history,
        medications=model.medications,
        allergies=model.allergies,
        vital_signs=model.vital_signs,
        physical_examination=model.physical_examination,
        diagnosis=model.diagnosis,
        treatment_plan=model.treatment_plan,
        prescriptions=model.prescriptions,
        notes=model.notes,
        patient_id=model.patient_id,
        professional_id=model.professional_id,
        company_id=model.company_id,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at
    )

def map_medical_record_model_to_list_response_dto(model: MedicalRecord) -> MedicalRecordListResponseDTO:
    """Map MedicalRecord model to MedicalRecordListResponseDTO"""
    return MedicalRecordListResponseDTO(
        id=model.id,
        record_number=model.record_number,
        title=model.title,
        record_type=model.record_type,
        status=model.status,
        consultation_date=model.consultation_date,
        patient_id=model.patient_id,
        professional_id=model.professional_id,
        is_confidential=model.is_confidential,
        created_at=model.created_at
    )

def map_medical_record_models_to_list_response_dtos(models: List[MedicalRecord]) -> List[MedicalRecordListResponseDTO]:
    """Map list of MedicalRecord models to list of MedicalRecordListResponseDTO"""
    return [map_medical_record_model_to_list_response_dto(model) for model in models] 