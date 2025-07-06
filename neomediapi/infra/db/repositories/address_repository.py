from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from neomediapi.infra.db.models.address_model import Address

class AddressRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, address_id: int) -> Optional[Address]:
        """Get address by ID"""
        return self.db.query(Address).filter(Address.id == address_id).first()

    def get_by_google_place_id(self, google_place_id: str) -> Optional[Address]:
        """Get address by Google Place ID"""
        return self.db.query(Address).filter(Address.google_place_id == google_place_id).first()

    def get_by_postal_code(self, postal_code: str) -> List[Address]:
        """Get addresses by postal code"""
        return self.db.query(Address).filter(Address.postal_code == postal_code).all()

    def get_by_city_state(self, city: str, state: str) -> List[Address]:
        """Get addresses by city and state"""
        return self.db.query(Address).filter(
            and_(Address.city == city, Address.state == state)
        ).all()

    def get_by_country(self, country: str) -> List[Address]:
        """Get addresses by country"""
        return self.db.query(Address).filter(Address.country == country).all()

    def get_with_coordinates(self) -> List[Address]:
        """Get addresses that have coordinates"""
        return self.db.query(Address).filter(
            and_(Address.latitude.isnot(None), Address.longitude.isnot(None))
        ).all()

    def search_addresses(self, query: str) -> List[Address]:
        """Search addresses by street, neighborhood, or city"""
        return self.db.query(Address).filter(
            or_(
                Address.street.ilike(f"%{query}%"),
                Address.neighborhood.ilike(f"%{query}%"),
                Address.city.ilike(f"%{query}%")
            )
        ).all()

    def get_nearby_addresses(self, latitude: float, longitude: float, radius_km: float = 10.0) -> List[Address]:
        """Get addresses within a certain radius (approximate calculation)"""
        # Simple distance calculation (for production, consider using PostGIS or similar)
        # 1 degree of latitude ≈ 111 km
        # 1 degree of longitude ≈ 111 km * cos(latitude)
        lat_radius = radius_km / 111.0
        lon_radius = radius_km / (111.0 * abs(latitude))
        
        return self.db.query(Address).filter(
            and_(
                Address.latitude.between(latitude - lat_radius, latitude + lat_radius),
                Address.longitude.between(longitude - lon_radius, longitude + lon_radius)
            )
        ).all()

    def save(self, address: Address) -> Address:
        """Save address to database"""
        self.db.add(address)
        self.db.commit()
        self.db.refresh(address)
        return address

    def update(self, address: Address) -> Address:
        """Update address in database"""
        self.db.commit()
        self.db.refresh(address)
        return address

    def delete(self, address: Address) -> bool:
        """Delete address from database"""
        self.db.delete(address)
        self.db.commit()
        return True

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Address]:
        """Get all addresses with pagination"""
        return self.db.query(Address).offset(skip).limit(limit).all() 