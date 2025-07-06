from enum import Enum

class Gender(str, Enum):
    """Gender options"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say" 