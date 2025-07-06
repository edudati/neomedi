from typing import List, Optional, Tuple
from neomediapi.domain.address.dtos.address_dto import (
    AddressCreateDTO, 
    AddressUpdateDTO, 
    AddressResponseDTO
)
from neomediapi.domain.address.exceptions import (
    AddressNotFoundError, 
    AddressValidationError
)
from neomediapi.domain.address.mappers.address_mapper import (
    map_address_create_dto_to_entity,
    map_address_update_dto_to_entity,
    map_address_entity_to_response_dto
)
from neomediapi.infra.db.models.address_model import Address
from neomediapi.infra.db.repositories.address_repository import AddressRepository

class AddressService:
    def __init__(self, address_repository: AddressRepository):
        self.address_repository = address_repository

    def create_address(self, address_data: AddressCreateDTO) -> AddressResponseDTO:
        """Create a new address"""
        try:
            # Check if address with same Google Place ID already exists
            if address_data.google_place_id:
                existing_address = self.address_repository.get_by_google_place_id(
                    address_data.google_place_id
                )
                if existing_address:
                    return map_address_entity_to_response_dto(existing_address)

            # Create new address
            address_entity = map_address_create_dto_to_entity(address_data)
            saved_address = self.address_repository.save(address_entity)
            
            return map_address_entity_to_response_dto(saved_address)
            
        except Exception as e:
            raise AddressValidationError(f"Failed to create address: {str(e)}")

    def get_address_by_id(self, address_id: int) -> AddressResponseDTO:
        """Get address by ID"""
        address = self.address_repository.get_by_id(address_id)
        if not address:
            raise AddressNotFoundError(f"Address with ID {address_id} not found")
        
        return map_address_entity_to_response_dto(address)

    def update_address(self, address_id: int, address_data: AddressUpdateDTO) -> AddressResponseDTO:
        """Update an existing address"""
        address = self.address_repository.get_by_id(address_id)
        if not address:
            raise AddressNotFoundError(f"Address with ID {address_id} not found")
        
        try:
            updated_address = map_address_update_dto_to_entity(address_data, address)
            saved_address = self.address_repository.update(updated_address)
            
            return map_address_entity_to_response_dto(saved_address)
            
        except Exception as e:
            raise AddressValidationError(f"Failed to update address: {str(e)}")

    def delete_address(self, address_id: int) -> bool:
        """Delete an address"""
        address = self.address_repository.get_by_id(address_id)
        if not address:
            raise AddressNotFoundError(f"Address with ID {address_id} not found")
        
        return self.address_repository.delete(address)

    def search_addresses(self, query: str) -> List[AddressResponseDTO]:
        """Search addresses by query"""
        addresses = self.address_repository.search_addresses(query)
        return [map_address_entity_to_response_dto(addr) for addr in addresses]

    def get_addresses_by_postal_code(self, postal_code: str) -> List[AddressResponseDTO]:
        """Get addresses by postal code"""
        addresses = self.address_repository.get_by_postal_code(postal_code)
        return [map_address_entity_to_response_dto(addr) for addr in addresses]

    def get_addresses_by_city_state(self, city: str, state: str) -> List[AddressResponseDTO]:
        """Get addresses by city and state"""
        addresses = self.address_repository.get_by_city_state(city, state)
        return [map_address_entity_to_response_dto(addr) for addr in addresses]

    def get_addresses_by_country(self, country: str) -> List[AddressResponseDTO]:
        """Get addresses by country"""
        addresses = self.address_repository.get_by_country(country)
        return [map_address_entity_to_response_dto(addr) for addr in addresses]

    def get_addresses_with_coordinates(self) -> List[AddressResponseDTO]:
        """Get addresses that have coordinates"""
        addresses = self.address_repository.get_with_coordinates()
        return [map_address_entity_to_response_dto(addr) for addr in addresses]

    def get_all_addresses(self, skip: int = 0, limit: int = 100) -> List[AddressResponseDTO]:
        """Get all addresses with pagination"""
        addresses = self.address_repository.get_all(skip, limit)
        return [map_address_entity_to_response_dto(addr) for addr in addresses]