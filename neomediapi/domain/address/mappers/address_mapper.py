from neomediapi.domain.address.dtos.address_dto import AddressCreateDTO, AddressUpdateDTO, AddressResponseDTO
from neomediapi.infra.db.models.address_model import Address
from typing import Optional

def map_address_create_dto_to_entity(dto: AddressCreateDTO) -> Address:
    """Map AddressCreateDTO to Address entity"""
    return Address(
        street=dto.street,
        number=dto.number,
        complement=dto.complement,
        neighborhood=dto.neighborhood,
        city=dto.city,
        state=dto.state,
        postal_code=dto.postal_code,
        country=dto.country,
        latitude=dto.latitude,
        longitude=dto.longitude,
        google_place_id=dto.google_place_id
    )

def map_address_update_dto_to_entity(dto: AddressUpdateDTO, address: Address) -> Address:
    """Map AddressUpdateDTO to existing Address entity"""
    if dto.street is not None:
        address.street = dto.street
    if dto.number is not None:
        address.number = dto.number
    if dto.complement is not None:
        address.complement = dto.complement
    if dto.neighborhood is not None:
        address.neighborhood = dto.neighborhood
    if dto.city is not None:
        address.city = dto.city
    if dto.state is not None:
        address.state = dto.state
    if dto.postal_code is not None:
        address.postal_code = dto.postal_code
    if dto.country is not None:
        address.country = dto.country
    if dto.latitude is not None:
        address.latitude = dto.latitude
    if dto.longitude is not None:
        address.longitude = dto.longitude
    if dto.google_place_id is not None:
        address.google_place_id = dto.google_place_id
    
    return address

def map_address_entity_to_response_dto(address: Address) -> AddressResponseDTO:
    """Map Address entity to AddressResponseDTO"""
    return AddressResponseDTO(
        id=address.id,
        street=address.street,
        number=address.number,
        complement=address.complement,
        neighborhood=address.neighborhood,
        city=address.city,
        state=address.state,
        postal_code=address.postal_code,
        country=address.country,
        latitude=address.latitude,
        longitude=address.longitude,
        google_place_id=address.google_place_id,
        created_at=address.created_at.isoformat() if address.created_at else "",
        updated_at=address.updated_at.isoformat() if address.updated_at else ""
    ) 