from enum import Enum

class DocumentType(str, Enum):
    """Types of identification documents"""
    DRIVE_LICENSE = "drive_license"
    PERSONAL_ID = "personal_id"
    PASSPORT = "passport" 