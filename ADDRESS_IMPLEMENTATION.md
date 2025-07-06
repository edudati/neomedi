# Address Entity Implementation

## Overview

This implementation provides a comprehensive address management system that is flexible and international, with optional Google Maps integration. The address entity can be used in 1:1 relationships with users, companies, and other entities that need address information.

## Architecture

The implementation follows Clean Architecture principles with the following layers:

```
Domain Layer (Business Logic)
├── DTOs (Data Transfer Objects)
├── Exceptions
└── Mappers

Service Layer (Business Operations)
├── AddressService

Infrastructure Layer (Data Access)
├── Address Model
└── Address Repository

API Layer (HTTP Interface)
└── Address Routes
```

## Features

### 🌍 International Support
- **Required Fields**: Essential address fields are mandatory
- **Optional Fields**: Complement and Google Maps data are optional
- **Country Default**: Defaults to "Brasil" if no country is specified
- **No Geographic Restrictions**: Works with addresses from any country

### 🗺️ Google Maps Integration (Frontend-Driven)
- **Coordinates Storage**: Latitude and longitude coordinates
- **Place ID**: Google Places API place_id for future reference
- **Optional Integration**: Frontend handles Google Maps API calls
- **Graceful Degradation**: Works without coordinates if Google Maps fails

### 🔍 Search & Query Features
- **Full-text Search**: Search by street, neighborhood, or city
- **Postal Code Search**: Find addresses by postal code
- **City/State Search**: Filter by city and state
- **Country Search**: Filter by country
- **Geographic Search**: Find addresses within radius (if coordinates available)
- **Pagination**: Support for large datasets

## Database Schema

```sql
CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    street VARCHAR(255) NOT NULL,
    number VARCHAR(20) NOT NULL,
    complement VARCHAR(100),
    neighborhood VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'Brasil',
    
    -- Google Maps fields (optional)
    latitude FLOAT,
    longitude FLOAT,
    google_place_id VARCHAR(255) UNIQUE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_addresses_street ON addresses(street);
CREATE INDEX idx_addresses_neighborhood ON addresses(neighborhood);
CREATE INDEX idx_addresses_city ON addresses(city);
CREATE INDEX idx_addresses_state ON addresses(state);
CREATE INDEX idx_addresses_postal_code ON addresses(postal_code);
CREATE INDEX idx_addresses_country ON addresses(country);
CREATE INDEX idx_addresses_coordinates ON addresses(latitude, longitude);
CREATE INDEX idx_addresses_google_place_id ON addresses(google_place_id);
```

## API Endpoints

### Basic CRUD Operations

#### Create Address
```http
POST /api/v1/addresses/
Content-Type: application/json

{
  "street": "Rua das Flores",
  "number": "123",
  "complement": "Apto 45",
  "neighborhood": "Centro",
  "city": "São Paulo",
  "state": "São Paulo",
  "postal_code": "01234-567",
  "country": "Brasil",
  "latitude": -23.5505,
  "longitude": -46.6333,
  "google_place_id": "ChIJ0T2NLikpdTERKxE8d61a72E"
}
```

#### Get Address by ID
```http
GET /api/v1/addresses/{address_id}
```

#### Update Address
```http
PUT /api/v1/addresses/{address_id}
Content-Type: application/json

{
  "street": "Rua das Flores",
  "number": "124",
  "complement": "Apto 46"
}
```

#### Delete Address
```http
DELETE /api/v1/addresses/{address_id}
```

### Search & Query Operations

#### Search Addresses
```http
GET /api/v1/addresses/search/?q=Rua das Flores
```

#### Get by Postal Code
```http
GET /api/v1/addresses/postal-code/01234-567
```

#### Get by City/State
```http
GET /api/v1/addresses/city/São Paulo/state/São Paulo
```

#### Get by Country
```http
GET /api/v1/addresses/country/Brasil
```

#### Get Addresses with Coordinates
```http
GET /api/v1/addresses/with-coordinates/
```

#### Get Nearby Addresses
```http
GET /api/v1/addresses/nearby/?latitude=-23.5505&longitude=-46.6333&radius_km=5.0
```

#### Get All Addresses (Paginated)
```http
GET /api/v1/addresses/?skip=0&limit=100
```

### Utility Operations

#### Get Statistics
```http
GET /api/v1/addresses/statistics/
```

## Data Transfer Objects (DTOs)

### AddressCreateDTO
```python
{
  "street": str,           # Required
  "number": str,           # Required
  "complement": str,       # Optional
  "neighborhood": str,     # Required
  "city": str,            # Required
  "state": str,           # Required
  "postal_code": str,     # Required
  "country": str,         # Optional (default: "Brasil")
  "latitude": float,      # Optional
  "longitude": float,     # Optional
  "google_place_id": str  # Optional
}
```

### AddressResponseDTO
```python
{
  "id": int,
  "street": str,
  "number": str,
  "complement": str,
  "neighborhood": str,
  "city": str,
  "state": str,
  "postal_code": str,
  "country": str,
  "latitude": float,
  "longitude": float,
  "google_place_id": str,
  "created_at": str,
  "updated_at": str
}
```

## Google Maps Integration (Frontend)

### Frontend Implementation Example
```javascript
// Example of how frontend can integrate with Google Maps
async function createAddressWithGoogleMaps(addressData) {
  try {
    // Frontend calls Google Maps Geocoding API
    const geocoder = new google.maps.Geocoder();
    const addressString = `${addressData.street}, ${addressData.number}, ${addressData.city}`;
    
    const result = await geocoder.geocode({ address: addressString });
    
    if (result.results.length > 0) {
      const location = result.results[0].geometry.location;
      const placeId = result.results[0].place_id;
      
      // Extract address components from Google Maps response
      const addressComponents = result.results[0].address_components;
      
      // Parse Google Maps address components
      const parsedAddress = parseAddressComponents(addressComponents);
      
      // Add coordinates and place_id to address data
      addressData.latitude = location.lat();
      addressData.longitude = location.lng();
      addressData.google_place_id = placeId;
      
      // Update address fields with Google Maps data
      if (parsedAddress.neighborhood) addressData.neighborhood = parsedAddress.neighborhood;
      if (parsedAddress.state) addressData.state = parsedAddress.state;
      if (parsedAddress.postal_code) addressData.postal_code = parsedAddress.postal_code;
      if (parsedAddress.country) addressData.country = parsedAddress.country;
    }
    
    // Send to backend
    const response = await fetch('/api/v1/addresses/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(addressData)
    });
    
    return await response.json();
  } catch (error) {
    // If Google Maps fails, still create address without coordinates
    console.warn('Google Maps integration failed:', error);
    
    // Remove Google Maps fields and create address anyway
    delete addressData.latitude;
    delete addressData.longitude;
    delete addressData.google_place_id;
    
    const response = await fetch('/api/v1/addresses/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(addressData)
    });
    
    return await response.json();
  }
}

function parseAddressComponents(components) {
  const parsed = {};
  
  for (const component of components) {
    const types = component.types;
    const value = component.long_name;
    
    if (types.includes('street_number')) {
      parsed.street_number = value;
    } else if (types.includes('route')) {
      parsed.street = value;
    } else if (types.includes('sublocality_level_1') || types.includes('sublocality')) {
      parsed.neighborhood = value;
    } else if (types.includes('locality')) {
      parsed.city = value;
    } else if (types.includes('administrative_area_level_1')) {
      parsed.state = value;
    } else if (types.includes('postal_code')) {
      parsed.postal_code = value;
    } else if (types.includes('country')) {
      parsed.country = value;
    }
  }
  
  return parsed;
}
```

## Usage Examples

### Creating an Address (Backend)
```python
from neomediapi.services.address_service import AddressService
from neomediapi.domain.address.dtos.address_dto import AddressCreateDTO

# Create address DTO (coordinates provided by frontend)
address_data = AddressCreateDTO(
    street="Rua das Flores",
    number="123",
    complement="Apto 45",
    neighborhood="Centro",
    city="São Paulo",
    state="São Paulo",
    postal_code="01234-567",
    country="Brasil",
    latitude=-23.5505,  # Provided by frontend Google Maps integration
    longitude=-46.6333, # Provided by frontend Google Maps integration
    google_place_id="ChIJ0T2NLikpdTERKxE8d61a72E"  # Provided by frontend
)

# Save to database
address_service = AddressService(address_repository)
saved_address = address_service.create_address(address_data)
```

### Creating an Address Without Coordinates
```python
# Address without Google Maps data (still valid)
address_data = AddressCreateDTO(
    street="Rua das Flores",
    number="123",
    complement="Apto 45",
    neighborhood="Centro",
    city="São Paulo",
    state="São Paulo",
    postal_code="01234-567",
    country="Brasil"
    # No coordinates or place_id - still works!
)
```

### Finding Nearby Addresses
```python
# Find addresses within 5km of a point (only works if addresses have coordinates)
nearby = address_service.get_nearby_addresses(
    latitude=-23.5505,
    longitude=-46.6333,
    radius_km=5.0
)
```

### Search Functionality
```python
# Search by text
results = address_service.search_addresses("Rua das Flores")

# Search by postal code
results = address_service.get_addresses_by_postal_code("01234-567")

# Search by city and state
results = address_service.get_addresses_by_city_state("São Paulo", "São Paulo")

# Search by country
results = address_service.get_addresses_by_country("Brasil")

# Get addresses with coordinates
results = address_service.get_addresses_with_coordinates()
```

## Integration with Other Entities

### User Integration
```python
# In user_model.py
class User(Base):
    # ... existing fields ...
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address", back_populates="user")
```

### Company Integration
```python
# In company_model.py
class Company(Base):
    # ... existing fields ...
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address", back_populates="company")
```

## Validation Rules

### Required Fields
- `street`: Required
- `number`: Required  
- `neighborhood`: Required
- `city`: Required
- `state`: Required
- `postal_code`: Required

### Optional Fields
- `complement`: Optional (user fills manually)
- `country`: Optional (defaults to "Brasil")
- `latitude`: Optional (Google Maps)
- `longitude`: Optional (Google Maps)
- `google_place_id`: Optional (Google Maps)

### Postal Code
- Required field
- Basic cleaning (removes non-alphanumeric characters except hyphens and spaces)
- No format restrictions

### State/Province
- Required field
- Basic trimming of whitespace
- No format restrictions

### Coordinates
- Latitude: -90 to 90 degrees
- Longitude: -180 to 180 degrees
- Both optional

## Error Handling

The implementation includes comprehensive error handling:

- `AddressNotFoundError`: Address not found in database
- `AddressValidationError`: Address validation failed

## Performance Considerations

- **Indexes**: All searchable fields are indexed
- **Pagination**: Large result sets are paginated
- **Optional Coordinates**: Geographic queries only work when coordinates are available
- **Flexible Schema**: Works with or without optional fields

## Security Considerations

- **Input Validation**: All inputs are validated using Pydantic
- **SQL Injection**: Protected by SQLAlchemy ORM
- **Frontend Integration**: Google Maps API calls handled by frontend

## Benefits of This Approach

1. **Flexibility**: Works with addresses from any country
2. **Graceful Degradation**: Functions without Google Maps integration
3. **Frontend Control**: Frontend manages Google Maps API calls and costs
4. **International Support**: No geographic restrictions
5. **Required Fields**: Essential fields are mandatory for data quality
6. **Future-Proof**: Easy to extend with additional fields

## Future Enhancements

1. **PostGIS Integration**: For advanced geographic queries
2. **Address Verification**: Integration with postal services
3. **Caching Layer**: Redis for frequently accessed addresses
4. **Bulk Operations**: Import/export functionality
5. **Address History**: Track address changes over time
6. **Geofencing**: Define service areas and boundaries
7. **Multi-language Support**: Address fields in multiple languages 