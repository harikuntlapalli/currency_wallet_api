from fastapi import APIRouter, HTTPException, status
from app.models import User, Token
from app.utils import create_jwt_token

router = APIRouter()

@router.post("/login", response_model=Token)
def login(user: User):
    if user.username == "admin" and user.password == "password123":
        token = create_jwt_token(user.username)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
