# auth/authenticated_user.py
from typing import Optional
from neomediapi.enums.user_profiles import UserProfile

class AuthenticatedUser:
    def __init__(self, uid: str, email: str, name: str, user_id: int, profile: Optional[UserProfile] = None):
        self.uid = uid
        self.email = email
        self.name = name
        self.id = user_id
        self.profile = profile
