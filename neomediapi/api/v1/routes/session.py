from fastapi import APIRouter, Request, Response, HTTPException, status, Depends
from pydantic import BaseModel
from firebase_admin import auth as firebase_auth
import firebase_admin
from sqlalchemy.orm import Session

from neomediapi.infra.db.session import get_db
from neomediapi.infra.db.repositories.user_repository import UserRepository
from neomediapi.services.user_service import UserService
from neomediapi.domain.user.dtos.user_dto import SessionVerifyResponseDTO, SessionCreateResponseDTO
from neomediapi.domain.user.exeptions import UserNotFoundError

router = APIRouter()


class FirebaseTokenRequest(BaseModel):
    id_token: str


@router.post("", response_model=SessionCreateResponseDTO)
def create_secure_session(
    body: FirebaseTokenRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Receive the idToken from Firebase, validate it and create a secure session cookie (HttpOnly, Secure).
    """
    try:
        decoded = firebase_auth.verify_id_token(body.id_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase token"
        )

    session_token = body.id_token  # TODO IMPORTANT In production, it is ideal to use your own token or session store.
    
    print("✅ Setando cookie de sessão!")
    response.set_cookie(
        key="session",
        value=session_token,
        httponly=True,
        secure=False,  # TODO IMPORTANT In production, uses True and HTTPS
        samesite="lax",
        max_age=3600,
        path="/"
    )

    # Extract user data
    user_id = decoded["user_id"]
    email = decoded["email"]
    email_verified = decoded.get("email_verified", False)

    print(f"🔍 Criando sessão para user_id: {user_id}")
    print(f"📧 Email: {email}")

    # Use Clean Architecture layers to get user data with role
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    
    try:
        session_data = user_service.get_session_verify_data(user_id, email, email_verified)
        print(f"✅ Sessão criada com role: {session_data.role}")
        
        # Return with success message
        return SessionCreateResponseDTO(
            message="Session created successfully.",
            user_id=session_data.user_id,
            email=session_data.email,
            role=session_data.role,
            email_verified=session_data.email_verified
        )
    except UserNotFoundError:
        print(f"❌ Usuário não encontrado no banco para firebase_uid: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.get("/verify", response_model=SessionVerifyResponseDTO)
def verify_session(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Verify if there is a valid session and return user data including role.
    """
    session_token = request.cookies.get("session")
    
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No session found"
        )
    
    try:
        decoded = firebase_auth.verify_id_token(session_token)
        user_id = decoded["user_id"]
        email = decoded["email"]
        email_verified = decoded.get("email_verified", False)

        print(f"🔍 Verificando sessão para user_id: {user_id}")
        print(f"📧 Email: {email}")

        # Use Clean Architecture layers
        user_repository = UserRepository(db)
        user_service = UserService(user_repository)
        
        try:
            session_data = user_service.get_session_verify_data(user_id, email, email_verified)
            print(f"✅ Usuário encontrado com role: {session_data.role}")
            return session_data
        except UserNotFoundError:
            print(f"❌ Usuário não encontrado no banco para firebase_uid: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

    except Exception as e:
        print(f"❌ Erro na verificação de sessão: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )



@router.post("/logout")
def logout(response: Response):
    """
    Remove the session cookie.
    """
    response.delete_cookie(key="session", path="/")
    return {"message": "Session ended successfully."}
