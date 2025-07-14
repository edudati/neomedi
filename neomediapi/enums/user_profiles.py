from enum import Enum

class UserProfile(str, Enum):
    SUPER = "super"
    ADMIN = "admin"
    MANAGER = "manager"
    ASSISTANT = "assistant"
    PROFESSIONAL = "professional"
    CLIENT = "client"
    TUTOR = "tutor"
    
    @classmethod
    def get_hierarchy_level(cls, profile: 'UserProfile') -> int:
        """Get hierarchy level for permission checking"""
        hierarchy = {
            cls.SUPER: 7,
            cls.ADMIN: 6,
            cls.MANAGER: 5,
            cls.PROFESSIONAL: 4,
            cls.ASSISTANT: 3,
            cls.CLIENT: 2,
            cls.TUTOR: 1
        }
        return hierarchy.get(profile, 0)
    
    def has_permission_for(self, required_profile: 'UserProfile') -> bool:
        """Check if current profile has permission for required profile level"""
        return UserProfile.get_hierarchy_level(self) >= UserProfile.get_hierarchy_level(required_profile)
    
    def get_level(self) -> int:
        """Get hierarchy level for current profile"""
        return UserProfile.get_hierarchy_level(self)
    
    def can_manage_company(self) -> bool:
        """Check if profile can manage company (create, edit, delete)"""
        return self in [self.SUPER, self.ADMIN]
    
    def can_nominate_managers(self) -> bool:
        """Check if profile can nominate managers"""
        return self in [self.SUPER, self.ADMIN]
    
    def can_nominate_professionals(self) -> bool:
        """Check if profile can nominate professionals"""
        return self in [self.SUPER, self.ADMIN, self.MANAGER]
    
    def can_access_professional_features(self) -> bool:
        """Check if profile can access professional features"""
        return self in [self.SUPER, self.ADMIN, self.MANAGER, self.PROFESSIONAL]
    
    def can_access_manager_features(self) -> bool:
        """Check if profile can access manager features"""
        return self in [self.SUPER, self.ADMIN, self.MANAGER]
    
    def can_access_admin_features(self) -> bool:
        """Check if profile can access admin features"""
        return self in [self.SUPER, self.ADMIN]
