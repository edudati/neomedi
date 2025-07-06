from pydantic import BaseModel, Field, validator
from typing import Optional

class AddressDTO(BaseModel):
    """Base address DTO with all fields"""
    street: str = Field(..., min_length=1, max_length=255, description="Street name")
    number: str = Field(..., min_length=1, max_length=20, description="House/building number")
    complement: Optional[str] = Field(None, max_length=100, description="Apartment, suite, etc.")
    neighborhood: str = Field(..., min_length=1, max_length=100, description="Neighborhood/District")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    state: str = Field(..., min_length=1, max_length=100, description="State/Province/Region")
    postal_code: str = Field(..., min_length=1, max_length=20, description="Postal/ZIP code")
    country: str = Field(default="Brasil", max_length=100, description="Country name")
    
    # Google Maps specific fields (optional)
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude coordinate")
    google_place_id: Optional[str] = Field(None, max_length=255, description="Google Places API place_id")
    
    @validator('postal_code')
    def validate_postal_code(cls, v):
        """Basic postal code validation - remove non-alphanumeric characters"""
        if v is None:
            return v
        # Remove non-alphanumeric characters but keep hyphens and spaces
        cleaned = ''.join(c for c in v if c.isalnum() or c in ['-', ' '])
        return cleaned
    
    @validator('state')
    def validate_state(cls, v):
        """Basic state validation - trim whitespace"""
        if v is None:
            return v
        return v.strip()

class AddressCreateDTO(AddressDTO):
    """DTO for creating a new address"""
    pass

class AddressUpdateDTO(BaseModel):
    """DTO for updating an address (all fields optional)"""
    street: Optional[str] = Field(None, min_length=1, max_length=255)
    number: Optional[str] = Field(None, min_length=1, max_length=20)
    complement: Optional[str] = Field(None, max_length=100)
    neighborhood: Optional[str] = Field(None, min_length=1, max_length=100)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    google_place_id: Optional[str] = Field(None, max_length=255)

class AddressResponseDTO(AddressDTO):
    """DTO for address responses"""
    id: int
    created_at: str
    updated_at: str
    
    class Config:
        orm_mode = True

class AddressSimpleDTO(BaseModel):
    """Simplified address DTO for basic information"""
    id: int
    street: str
    number: str
    city: str
    state: str
    postal_code: str
    
    class Config:
        orm_mode = True 