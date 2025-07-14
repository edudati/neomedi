from typing import Optional
from neomediapi.enums.user_profiles import UserProfile
from neomediapi.auth.authenticated_user import AuthenticatedUser

class PermissionManager:
    """Manager for user permissions based on profile hierarchy"""
    
    @staticmethod
    def has_permission(user: AuthenticatedUser, required_profile: UserProfile) -> bool:
        """Check if user has permission for required profile level"""
        return user.profile.has_permission_for(required_profile)
    
    @staticmethod
    def can_manage_company(user: AuthenticatedUser) -> bool:
        """Check if user can manage company (create, edit, delete)"""
        return user.profile.can_manage_company()
    
    @staticmethod
    def can_nominate_managers(user: AuthenticatedUser) -> bool:
        """Check if user can nominate managers"""
        return user.profile.can_nominate_managers()
    
    @staticmethod
    def can_nominate_professionals(user: AuthenticatedUser) -> bool:
        """Check if user can nominate professionals"""
        return user.profile.can_nominate_professionals()
    
    @staticmethod
    def can_access_professional_features(user: AuthenticatedUser) -> bool:
        """Check if user can access professional features"""
        return user.profile.can_access_professional_features()
    
    @staticmethod
    def can_access_manager_features(user: AuthenticatedUser) -> bool:
        """Check if user can access manager features"""
        return user.profile.can_access_manager_features()
    
    @staticmethod
    def can_access_admin_features(user: AuthenticatedUser) -> bool:
        """Check if user can access admin features"""
        return user.profile.can_access_admin_features()
    
    @staticmethod
    def get_available_features(user: AuthenticatedUser) -> list[str]:
        """Get list of available features for user based on profile"""
        features = []
        
        if user.profile == UserProfile.SUPER:
            features.extend([
                "super_admin",
                "company_management",
                "nominate_managers",
                "nominate_professionals",
                "manager_features",
                "professional_features"
            ])
        elif user.profile == UserProfile.ADMIN:
            features.extend([
                "company_management",
                "nominate_managers", 
                "nominate_professionals",
                "manager_features",
                "professional_features"
            ])
        elif user.profile == UserProfile.MANAGER:
            features.extend([
                "nominate_professionals",
                "manager_features", 
                "professional_features"
            ])
        elif user.profile == UserProfile.PROFESSIONAL:
            features.extend([
                "professional_features"
            ])
        elif user.profile == UserProfile.ASSISTANT:
            features.extend([
                "assistant_features"
            ])
        elif user.profile == UserProfile.CLIENT:
            features.extend([
                "client_features"
            ])
        elif user.profile == UserProfile.TUTOR:
            features.extend([
                "tutor_features"
            ])
        
        return features
    
    @staticmethod
    def validate_profile_transition(current_profile: UserProfile, new_profile: UserProfile) -> bool:
        """Validate if profile transition is allowed"""
        # Super can change to any profile
        if current_profile == UserProfile.SUPER:
            return True
        
        # Admin can only be changed by Super
        if current_profile == UserProfile.ADMIN:
            return False
        
        # Manager can be changed by Admin or Super
        if current_profile == UserProfile.MANAGER:
            return new_profile in [UserProfile.PROFESSIONAL, UserProfile.ASSISTANT]
        
        # Professional can be changed by Manager, Admin or Super
        if current_profile == UserProfile.PROFESSIONAL:
            return new_profile in [UserProfile.ASSISTANT, UserProfile.CLIENT]
        
        # Other profiles can be changed freely
        return True
    
    @staticmethod
    def get_allowed_profile_changes(current_profile: UserProfile) -> list[UserProfile]:
        """Get list of profiles that current profile can be changed to"""
        if current_profile == UserProfile.SUPER:
            return list(UserProfile)
        elif current_profile == UserProfile.ADMIN:
            return []  # Only Super can change Admin
        elif current_profile == UserProfile.MANAGER:
            return [UserProfile.PROFESSIONAL, UserProfile.ASSISTANT]
        elif current_profile == UserProfile.PROFESSIONAL:
            return [UserProfile.ASSISTANT, UserProfile.CLIENT]
        else:
            return list(UserProfile)  # Other profiles can be changed freely 