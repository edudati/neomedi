from fastapi import APIRouter, Request, Response, HTTPException, status
from pydantic import BaseModel
from firebase_admin import auth as firebase_auth
import firebase_admin

router = APIRouter()


class FirebaseTokenRequest(BaseModel):
    id_token: str


@router.post("")
def create_secure_session(
    body: FirebaseTokenRequest,
    response: Response
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
        samesite="Lax",
        max_age=3600,
        path="/"
    )

    return {
        "message": "Session created succefully.",
        "user_id": decoded["user_id"],
        "email": decoded["email"],
        "email_verified": decoded.get("email_verified", False)
    }


@router.get("/verify")
def verify_session(request: Request):
    """
    Verify if there are a valid session and return data from user.
    """
    session_token = request.cookies.get("session")
    
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No sessions found"
        )
    
    try:
        decoded = firebase_auth.verify_id_token(session_token)
        return {
            "user_id": decoded["user_id"],
            "email": decoded["email"],
            "email_verified": decoded.get("email_verified", False)
        }
    except Exception:
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
