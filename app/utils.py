import jwt
import time
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import Config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_jwt_token(username: str):
    expiration = int(time.time()) + Config.TOKEN_EXPIRATION
    payload = {"sub": username, "exp": expiration}
    return jwt.encode(payload, Config.SECRET_KEY, algorithm=Config.ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
