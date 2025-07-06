from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import relationship
from neomediapi.infra.db.base_class import Base

class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic address fields
    street = Column(String(255), nullable=False, index=True)
    number = Column(String(20), nullable=False)
    complement = Column(String(100), nullable=True)
    neighborhood = Column(String(100), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)  # State/Province/Region
    postal_code = Column(String(20), nullable=False, index=True)  # Postal/ZIP code
    country = Column(String(100), nullable=False, default="Brasil", index=True)
    
    # Google Maps specific fields (optional)
    latitude = Column(Float, nullable=True, index=True)
    longitude = Column(Float, nullable=True, index=True)
    google_place_id = Column(String(255), nullable=True, unique=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="address", uselist=False)
    # company = relationship("Company", back_populates="address", uselist=False)
    
    def __repr__(self):
        return f"<Address(id={self.id}, street='{self.street}', city='{self.city}', country='{self.country}')>"
    
    @property
    def full_address(self) -> str:
        """Return formatted full address"""
        parts = [
            f"{self.street}, {self.number}",
            self.complement,
            self.neighborhood,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ", ".join(filter(None, parts))
    
    @property
    def coordinates(self) -> tuple[float, float] | None:
        """Return coordinates as tuple if available"""
        if self.latitude is not None and self.longitude is not None:
            return (self.latitude, self.longitude)
        return None
    
    @property
    def has_coordinates(self) -> bool:
        """Check if address has coordinates"""
        return self.latitude is not None and self.longitude is not None 