import os
from pathlib import Path
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from fastapi import HTTPException, status
from neomediapi.auth.authenticated_user import AuthenticatedUser



# Load .env
load_dotenv()

# Get credentials path from .env
cred_path = Path(os.getenv("FIREBASE_CREDENTIALS", "firebase_service_account.json"))

# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

def verify_firebase_token(id_token: str) -> AuthenticatedUser:
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return AuthenticatedUser(
            uid=decoded["uid"],
            email=decoded.get("email"),
            name=decoded.get("name"),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase token"
        )
