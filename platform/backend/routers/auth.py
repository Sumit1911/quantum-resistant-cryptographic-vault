from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(payload: LoginRequest) -> dict:
    return {
        "success": True,
        "message": "Auth scaffold ready",
        "username": payload.username,
        "token": "demo-token",
    }

