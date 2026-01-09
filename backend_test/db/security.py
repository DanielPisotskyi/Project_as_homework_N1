from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from . import shemas


SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_sheme = OAuth2PasswordBearer(tokenUrl="token")

def create_token(data: dict):
    to_encode = data.copy()
    #               21:16                +         30 хв             = 21:46
    expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
    """
    {
    "sub": "yuka_menes",
    "role": "admin",
    "exp": "21:46"
    }
    """


def get_current_user(token: Annotated[str, Depends(oauth2_sheme)]) -> shemas.TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        role: str = payload.get("role")
        if login is None:
            raise credentials_exception
        token_data = shemas.TokenData(login = login, role = role)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail = "Token expired")
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    return token_data

def get_current_admin(current_user: Annotated[shemas.TokenData, Depends(get_current_user)]) -> shemas.TokenData:
    if current_user.role != "admin":
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Not enough permissions"
        )
    
    return current_user
