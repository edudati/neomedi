class MedicalRecordError(Exception):
    """Base exception for medical record errors"""
    pass

class MedicalRecordNotFoundError(MedicalRecordError):
    """Raised when medical record is not found"""
    pass

class MedicalRecordValidationError(MedicalRecordError):
    """Raised when medical record validation fails"""
    pass

class MedicalRecordAlreadyExistsError(MedicalRecordError):
    """Raised when medical record already exists"""
    pass

class MedicalRecordPermissionError(MedicalRecordError):
    """Raised when user doesn't have permission to access medical record"""
    pass

class MedicalRecordConfidentialityError(MedicalRecordError):
    """Raised when trying to access confidential medical record without permission"""
    pass

class MedicalRecordStatusError(MedicalRecordError):
    """Raised when medical record status transition is invalid"""
    pass

class MedicalRecordNumberGenerationError(MedicalRecordError):
    """Raised when medical record number generation fails"""
    pass

class MedicalRecordPatientNotFoundError(MedicalRecordError):
    """Raised when patient is not found"""
    pass

class MedicalRecordProfessionalNotFoundError(MedicalRecordError):
    """Raised when professional is not found"""
    pass

class MedicalRecordCompanyNotFoundError(MedicalRecordError):
    """Raised when company is not found"""
    pass 