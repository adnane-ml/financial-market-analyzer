from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_token

bearer_scheme = HTTPBearer()

def get_current_user(credentials : HTTPAuthorizationCredentials = Depends(bearer_scheme) ) -> str:
    token  = credentials.credentials
    payload = decode_token(token)

    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail = "Token invalide ou expiré", )
    return payload["sub"]