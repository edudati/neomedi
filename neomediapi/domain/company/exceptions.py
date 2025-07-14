class CompanyException(Exception):
    """Base exception for company domain"""
    pass

class CompanyNotFoundError(CompanyException):
    """Raised when company is not found"""
    pass

class CompanyAlreadyExistsError(CompanyException):
    """Raised when trying to create a company that already exists"""
    pass

class CompanyNotActiveError(CompanyException):
    """Raised when trying to perform operations on inactive company"""
    pass

class CompanyDeletedError(CompanyException):
    """Raised when trying to perform operations on deleted company"""
    pass

class AdminUserAlreadyHasCompanyError(CompanyException):
    """Raised when admin user already has a company"""
    pass

class OnlyAdminCanManageCompanyError(CompanyException):
    """Raised when non-admin user tries to manage company"""
    pass

class InvalidCNPJError(CompanyException):
    """Raised when CNPJ format is invalid"""
    pass

class UserNotInCompanyError(CompanyException):
    """Raised when user is not part of the company"""
    pass

class ProfessionalNotActiveError(CompanyException):
    """Raised when professional is not active"""
    pass

class ClientAlreadyAssignedError(CompanyException):
    """Raised when client is already assigned to a professional"""
    pass

class ClientNotAssignedError(CompanyException):
    """Raised when client is not assigned to any professional"""
    pass

class InvalidUserProfileError(CompanyException):
    """Raised when user profile is not valid for the operation"""
    pass 