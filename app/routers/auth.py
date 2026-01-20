import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.dependencies import db_dependency
from app.schemas import users
from app.services.auth_service import AuthService

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_details: users.CreateUserRequest, db: db_dependency):
    return AuthService.create_user(db, user_details)

@router.post("/token", response_model=users.Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency
):
    """Login and get access token"""
    return AuthService.login_user(
        db, form_data.username, form_data.password, SECRET_KEY, ALGORITHM
    )