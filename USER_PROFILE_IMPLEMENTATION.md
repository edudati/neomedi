# User Profile Implementation

## Overview

This implementation provides a comprehensive user management system that extends the existing authentication system with complete user profile information. The system maintains backward compatibility with the existing authentication flow while adding rich profile management capabilities.

## Architecture

The implementation follows Clean Architecture principles with the following layers:

```
Domain Layer (Business Logic)
├── DTOs (Data Transfer Objects)
├── Exceptions
└── Mappers

Service Layer (Business Operations)
├── UserService

Infrastructure Layer (Data Access)
├── User Model
└── User Repository

API Layer (HTTP Interface)
└── User Routes
```

## Features

### 🔐 Authentication Compatibility
- **Backward Compatible**: Existing authentication endpoints remain unchanged
- **Firebase Integration**: Maintains Firebase UID for authentication
- **Role Management**: Existing role system preserved and enhanced
- **Session Management**: Existing session verification works with new profile

### 👤 Complete User Profile
- **Personal Information**: Full name, document details, birth date, gender
- **Contact Information**: Phone number, secondary email
- **Address Integration**: 1:1 relationship with Address entity
- **Profile Completion**: Automatic tracking of profile completion status

### 🛡️ Data Validation & Security
- **Document Validation**: Unique document ID validation
- **Phone Validation**: Unique phone number validation
- **Age Validation**: Minimum age requirement (18 years)
- **Soft Delete**: Users can be deactivated without data loss

### 🔍 Advanced Search & Filtering
- **Full-text Search**: Search by name, email, or document ID
- **Role-based Filtering**: Filter users by role
- **Profile Status**: Filter by complete/incomplete profiles
- **Geographic Filtering**: Filter by address location
- **Document Type**: Filter by document type
- **Gender**: Filter by gender

## Database Schema

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    
    -- Authentication fields
    email VARCHAR NOT NULL UNIQUE,
    firebase_uid VARCHAR NOT NULL UNIQUE,
    role VARCHAR(20) NOT NULL DEFAULT 'client',
    
    -- Personal information
    full_name VARCHAR(255) NOT NULL,
    document_type VARCHAR(20),
    document_id VARCHAR(50) UNIQUE,
    date_of_birth DATE,
    gender VARCHAR(20),
    
    -- Contact information
    phone_number VARCHAR(20),
    secondary_email VARCHAR,
    
    -- Address relationship
    address_id INTEGER REFERENCES addresses(id),
    
    -- Control fields
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    profile_completed BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_firebase_uid ON users(firebase_uid);
CREATE INDEX idx_users_full_name ON users(full_name);
CREATE INDEX idx_users_document_id ON users(document_id);
CREATE INDEX idx_users_phone_number ON users(phone_number);
CREATE INDEX idx_users_secondary_email ON users(secondary_email);
CREATE INDEX idx_users_address_id ON users(address_id);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_is_deleted ON users(is_deleted);
CREATE INDEX idx_users_profile_completed ON users(profile_completed);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_document_type ON users(document_type);
CREATE INDEX idx_users_gender ON users(gender);
```

## Enums

### DocumentType
```python
class DocumentType(str, Enum):
    DRIVE_LICENSE = "drive_license"
    PERSONAL_ID = "personal_id"
    PASSPORT = "passport"
```

### Gender
```python
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
```

### UserRole (existing)
```python
class UserRole(str, Enum):
    SUPER = "super"
    ADMIN = "admin"
    MANAGER = "manager"
    ASSISTANT = "assistant"
    PROFESSIONAL = "professional"
    CLIENT = "client"
    TUTOR = "tutor"
```

## API Endpoints

### Authentication Endpoints (Existing)

#### Create User (Authentication)
```http
POST /api/v1/users/
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "client"
}
```

#### Get User by ID
```http
GET /api/v1/users/{user_id}
```

### Profile Management Endpoints (New)

#### Create User Profile
```http
POST /api/v1/users/{user_id}/profile
Content-Type: application/json

{
  "full_name": "John Doe",
  "document_type": "personal_id",
  "document_id": "12345678901",
  "date_of_birth": "1990-01-15",
  "gender": "male",
  "phone_number": "+5511999999999",
  "secondary_email": "john.work@example.com",
  "address_id": 1
}
```

#### Get User Profile
```http
GET /api/v1/users/{user_id}/profile
```

#### Update User Profile
```http
PUT /api/v1/users/{user_id}/profile
Content-Type: application/json

{
  "full_name": "John Smith",
  "phone_number": "+5511888888888"
}
```

### User Management Endpoints

#### Get All Users (Paginated)
```http
GET /api/v1/users/?skip=0&limit=100
```

#### Search Users
```http
GET /api/v1/users/search/?q=John&skip=0&limit=100
```

#### Get Users by Role
```http
GET /api/v1/users/role/client?skip=0&limit=100
```

#### Get Users by Document Type
```http
GET /api/v1/users/document-type/personal_id
```

#### Get Users by Gender
```http
GET /api/v1/users/gender/male
```

#### Get Users with Complete Profile
```http
GET /api/v1/users/complete-profiles/?skip=0&limit=100
```

#### Get Users with Incomplete Profile
```http
GET /api/v1/users/incomplete-profiles/?skip=0&limit=100
```

### Address-Related Endpoints

#### Get Users by Address City
```http
GET /api/v1/users/address/city/São Paulo
```

#### Get Users by Address State
```http
GET /api/v1/users/address/state/São Paulo
```

#### Get Users with Address
```http
GET /api/v1/users/with-address/
```

#### Get Users without Address
```http
GET /api/v1/users/without-address/
```

### User Status Management

#### Deactivate User
```http
PATCH /api/v1/users/{user_id}/deactivate
```

#### Activate User
```http
PATCH /api/v1/users/{user_id}/activate
```

#### Soft Delete User
```http
DELETE /api/v1/users/{user_id}
```

#### Restore User
```http
PATCH /api/v1/users/{user_id}/restore
```

#### Hard Delete User
```http
DELETE /api/v1/users/{user_id}/hard
```

### Statistics

#### Get User Statistics
```http
GET /api/v1/users/statistics/
```

## Data Transfer Objects (DTOs)

### UserCreateDTO (Authentication)
```python
{
  "name": str,
  "email": EmailStr,
  "role": UserRole
}
```

### UserProfileCreateDTO
```python
{
  "full_name": str,           # Required
  "document_type": DocumentType,  # Required
  "document_id": str,         # Required
  "date_of_birth": date,      # Required
  "gender": Gender,           # Required
  "phone_number": str,        # Required
  "secondary_email": EmailStr, # Optional
  "address_id": int           # Optional
}
```

### UserProfileUpdateDTO
```python
{
  "full_name": str,           # Optional
  "document_type": DocumentType,  # Optional
  "document_id": str,         # Optional
  "date_of_birth": date,      # Optional
  "gender": Gender,           # Optional
  "phone_number": str,        # Optional
  "secondary_email": EmailStr, # Optional
  "address_id": int           # Optional
}
```

### UserProfileResponseDTO
```python
{
  "id": int,
  "email": EmailStr,
  "role": UserRole,
  "full_name": str,
  "document_type": DocumentType,
  "document_id": str,
  "date_of_birth": date,
  "gender": Gender,
  "phone_number": str,
  "secondary_email": EmailStr,
  "address": AddressResponseDTO,
  "is_active": bool,
  "is_deleted": bool,
  "profile_completed": bool,
  "created_at": str,
  "updated_at": str
}
```

### UserSimpleResponseDTO
```python
{
  "id": int,
  "full_name": str,
  "email": EmailStr,
  "role": UserRole,
  "is_active": bool,
  "profile_completed": bool
}
```

### UserListResponseDTO
```python
{
  "users": List[UserSimpleResponseDTO],
  "total": int,
  "skip": int,
  "limit": int
}
```

## Usage Examples

### Creating a User with Authentication
```python
from neomediapi.services.user_service import UserService
from neomediapi.domain.user.dtos.user_dto import UserCreateDTO
from neomediapi.enums.user_roles import UserRole

# Create user for authentication
user_data = UserCreateDTO(
    name="John Doe",
    email="john@example.com",
    role=UserRole.CLIENT
)

user_service = UserService(user_repository)
user = user_service.create_user(user_data, firebase_uid="firebase_uid_here")
```

### Creating a Complete User Profile
```python
from neomediapi.domain.user.dtos.user_dto import UserProfileCreateDTO
from neomediapi.enums.document_types import DocumentType
from neomediapi.enums.gender_types import Gender
from datetime import date

# Create complete profile
profile_data = UserProfileCreateDTO(
    full_name="John Doe",
    document_type=DocumentType.PERSONAL_ID,
    document_id="12345678901",
    date_of_birth=date(1990, 1, 15),
    gender=Gender.MALE,
    phone_number="+5511999999999",
    secondary_email="john.work@example.com",
    address_id=1  # ID of existing address
)

profile = user_service.create_user_profile(user_id=1, profile_data=profile_data)
```

### Updating User Profile
```python
from neomediapi.domain.user.dtos.user_dto import UserProfileUpdateDTO

# Update profile
update_data = UserProfileUpdateDTO(
    full_name="John Smith",
    phone_number="+5511888888888"
)

updated_profile = user_service.update_user_profile(user_id=1, profile_data=update_data)
```

### Searching Users
```python
# Search by name, email, or document ID
results = user_service.search_users("John", skip=0, limit=100)

# Get users by role
clients = user_service.get_users_by_role(UserRole.CLIENT, skip=0, limit=100)

# Get users with complete profile
complete_profiles = user_service.get_users_with_complete_profile(skip=0, limit=100)

# Get users by address city
users_in_sp = user_service.get_users_by_address_city("São Paulo")
```

### User Status Management
```python
# Deactivate user
user_service.deactivate_user(user_id=1)

# Activate user
user_service.activate_user(user_id=1)

# Soft delete user
user_service.soft_delete_user(user_id=1)

# Restore user
user_service.restore_user(user_id=1)

# Hard delete user (permanent)
user_service.hard_delete_user(user_id=1)
```

## Validation Rules

### Required Fields for Complete Profile
- `full_name`: Required, 1-255 characters
- `document_type`: Required, must be valid DocumentType
- `document_id`: Required, 1-50 characters, must be unique
- `date_of_birth`: Required, user must be at least 18 years old
- `gender`: Required, must be valid Gender
- `phone_number`: Required, 10-15 digits, must be unique

### Optional Fields
- `secondary_email`: Optional, must be valid email format
- `address_id`: Optional, must reference existing address

### Validation Logic
- **Document ID**: Must be unique across all users
- **Phone Number**: Must be unique across all users
- **Age**: Must be at least 18 years old
- **Email**: Must be valid email format
- **Address**: Must reference existing address if provided

## Profile Completion Logic

A user profile is considered complete when all required fields are filled:
- `full_name` is not null
- `document_type` is not null
- `document_id` is not null
- `date_of_birth` is not null
- `phone_number` is not null

The `profile_completed` field is automatically updated when the profile is created or updated.

## Error Handling

The implementation includes comprehensive error handling:

- `UserNotFoundError`: User not found in database
- `UserValidationError`: User validation failed
- `UserAlreadyExistsError`: User with same email/document/phone already exists

## Integration with Address Entity

### Creating User with Address
```python
# First, create address
address_data = AddressCreateDTO(
    street="Rua das Flores",
    number="123",
    complement="Apto 45",
    neighborhood="Centro",
    city="São Paulo",
    state="São Paulo",
    postal_code="01234-567",
    country="Brasil"
)

address_service = AddressService(address_repository)
address = address_service.create_address(address_data)

# Then, create user profile with address
profile_data = UserProfileCreateDTO(
    full_name="John Doe",
    document_type=DocumentType.PERSONAL_ID,
    document_id="12345678901",
    date_of_birth=date(1990, 1, 15),
    gender=Gender.MALE,
    phone_number="+5511999999999",
    address_id=address.id
)

profile = user_service.create_user_profile(user_id=1, profile_data=profile_data)
```

### Getting User with Address
```python
# Get complete user profile including address
profile = user_service.get_user_profile(user_id=1)
print(f"User: {profile.full_name}")
print(f"Address: {profile.address.full_address if profile.address else 'No address'}")
```

## Benefits of This Approach

1. **Backward Compatibility**: Existing authentication system remains unchanged
2. **Gradual Migration**: Users can complete their profile over time
3. **Rich Data Model**: Comprehensive user information for business needs
4. **Flexible Search**: Multiple ways to find and filter users
5. **Data Integrity**: Proper validation and unique constraints
6. **Soft Delete**: Users can be deactivated without data loss
7. **Address Integration**: Seamless integration with address management
8. **Profile Tracking**: Automatic tracking of profile completion status

## Future Enhancements

1. **Profile Picture**: Add profile picture upload functionality
2. **Document Upload**: Add document verification upload
3. **Address History**: Track address changes over time
4. **Profile Verification**: Add verification status for documents
5. **Notification Preferences**: Add notification settings
6. **Privacy Settings**: Add privacy control options
7. **Activity Log**: Track user activity and changes
8. **Bulk Operations**: Import/export user data
9. **Advanced Analytics**: User behavior and engagement analytics
10. **Multi-language Support**: Profile fields in multiple languages 