from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password : str) -> str :
    return pwd_context.hash(password)

def verify_password(plain : str, hashed : str) -> bool :
    return pwd_context.verify(plain,hashed)

def create_access_token(subject : str) -> str :
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": subject, "exp": expire, "type": "access"},
                      settings.SECRET_KEY,
                      algorithm=settings.ALGORITHM)

def create_refresh_token(subject : str ) -> str :
    expire = datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode({"sub" : subject, "exp" : expire, "type" : "refresh"},
                      settings.SECRET_KEY,algorithm = settings.ALGORITHM)

def decode_token(token : str) -> dict :
    try : 
        return jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
    except JWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")
    return payload["sub"]