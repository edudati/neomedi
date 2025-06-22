from enum import Enum

class UserRole(str, Enum):
    SUPER = "super"
    ADMIN = "admin"
    MANAGER = "manager"
    ASSISTANT = "assistant"
    PROFESSIONAL = "professional"
    CLIENT = "client"
    TUTOR = "tutor"
