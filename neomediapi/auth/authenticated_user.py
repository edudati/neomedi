# auth/authenticated_user.py

class AuthenticatedUser:
    def __init__(self, uid: str, email: str, name: str):
        self.uid = uid
        self.email = email
        self.name = name
