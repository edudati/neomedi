from fastapi import Cookie, Depends, Header, HTTPException, status
from typing import Optional
from .firebase import verify_firebase_token

def get_current_user(
    session: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Retorna o usuário autenticado a partir do cookie de sessão ou header Authorization.
    Prioriza o cookie (navegadores), mas aceita Bearer token como fallback (ex: mobile ou testes).
    """
    token = None

    if session:
        token = session
    elif authorization:
        try:
            scheme, bearer_token = authorization.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid token scheme")
            token = bearer_token
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Formato inválido do cabeçalho Authorization"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nenhum token de autenticação fornecido"
        )

    return verify_firebase_token(token)

