class UserNotFoundError(Exception):
    """Raised when a user is not found"""
    pass

class UserValidationError(Exception):
    """Raised when user validation fails"""
    pass

class UserAlreadyExistsError(Exception):
    """Raised when trying to create a user that already exists"""
    pass 