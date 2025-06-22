from pydantic import BaseModel, EmailStr
from neomediapi.enums.user_roles import UserRole

class UserCreateDTO(BaseModel):
    name: str
    email: EmailStr
    role: UserRole


class UserResponseDTO(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole

    class Config:
        orm_mode = True  # allows Pydantic to read data from ORM models