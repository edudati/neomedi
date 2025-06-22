class UserAlreadyExistsError(Exception):
    """Raised when trying to create a user that already exists (by Firebase UID)."""
    pass


class UserNotFoundError(Exception):
    """Raised when a user is not found (by UID, ID, or other keys)."""
    pass


class UnauthorizedUserError(Exception):
    """Raised when a user attempts an action they are not allowed to perform."""
    pass
