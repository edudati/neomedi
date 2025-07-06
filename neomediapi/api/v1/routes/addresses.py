from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from neomediapi.infra.db.session import get_db
from neomediapi.infra.db.repositories.address_repository import AddressRepository
from neomediapi.services.address_service import AddressService
from neomediapi.domain.address.dtos.address_dto import (
    AddressCreateDTO,
    AddressUpdateDTO,
    AddressResponseDTO
)
from neomediapi.domain.address.exceptions import (
    AddressNotFoundError,
    AddressValidationError
)

router = APIRouter()

def get_address_service(db: Session = Depends(get_db)) -> AddressService:
    """Dependency to get address service"""
    address_repository = AddressRepository(db)
    return AddressService(address_repository)

@router.post("/", response_model=AddressResponseDTO, status_code=status.HTTP_201_CREATED)
def create_address(
    address_data: AddressCreateDTO,
    address_service: AddressService = Depends(get_address_service)
):
    """Create a new address"""
    try:
        return address_service.create_address(address_data)
    except AddressValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{address_id}", response_model=AddressResponseDTO)
def get_address(
    address_id: int,
    address_service: AddressService = Depends(get_address_service)
):
    """Get address by ID"""
    try:
        return address_service.get_address_by_id(address_id)
    except AddressNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{address_id}", response_model=AddressResponseDTO)
def update_address(
    address_id: int,
    address_data: AddressUpdateDTO,
    address_service: AddressService = Depends(get_address_service)
):
    """Update an existing address"""
    try:
        return address_service.update_address(address_id, address_data)
    except AddressNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AddressValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: int,
    address_service: AddressService = Depends(get_address_service)
):
    """Delete an address"""
    try:
        address_service.delete_address(address_id)
    except AddressNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/", response_model=List[AddressResponseDTO])
def get_addresses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    address_service: AddressService = Depends(get_address_service)
):
    """Get all addresses with pagination"""
    return address_service.get_all_addresses(skip, limit)

@router.get("/search/", response_model=List[AddressResponseDTO])
def search_addresses(
    q: str = Query(..., min_length=1, description="Search query"),
    address_service: AddressService = Depends(get_address_service)
):
    """Search addresses by street, neighborhood, or city"""
    return address_service.search_addresses(q)

@router.get("/postal-code/{postal_code}", response_model=List[AddressResponseDTO])
def get_addresses_by_postal_code(
    postal_code: str,
    address_service: AddressService = Depends(get_address_service)
):
    """Get addresses by postal code"""
    return address_service.get_addresses_by_postal_code(postal_code)

@router.get("/city/{city}/state/{state}", response_model=List[AddressResponseDTO])
def get_addresses_by_city_state(
    city: str,
    state: str,
    address_service: AddressService = Depends(get_address_service)
):
    """Get addresses by city and state"""
    return address_service.get_addresses_by_city_state(city, state)

@router.get("/country/{country}", response_model=List[AddressResponseDTO])
def get_addresses_by_country(
    country: str,
    address_service: AddressService = Depends(get_address_service)
):
    """Get addresses by country"""
    return address_service.get_addresses_by_country(country)

@router.get("/with-coordinates/", response_model=List[AddressResponseDTO])
def get_addresses_with_coordinates(
    address_service: AddressService = Depends(get_address_service)
):
    """Get addresses that have coordinates"""
    return address_service.get_addresses_with_coordinates()