from fastapi import APIRouter, HTTPException
from src.core.security import create_jwt_token

router = APIRouter()

@router.post("/login")
def login(username: str, password: str):
    if username == "admin" and password == "admin":
        token = create_jwt_token({"sub": username})
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")
