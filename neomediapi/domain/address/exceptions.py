class AddressNotFoundError(Exception):
    """Raised when an address is not found."""
    pass

class AddressValidationError(Exception):
    """Raised when address validation fails."""
    pass

class InvalidPostalCodeError(Exception):
    """Raised when postal code format is invalid."""
    pass

class InvalidStateError(Exception):
    """Raised when state abbreviation is invalid."""
    pass

class GoogleMapsError(Exception):
    """Raised when Google Maps API integration fails."""
    pass 