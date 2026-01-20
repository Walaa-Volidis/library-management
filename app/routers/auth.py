import os
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from app.database import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
from app.schemas import users
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth", 
    tags=["Auth"]
)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_bearer =Annotated[OAuth2PasswordRequestForm, Depends()]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_details: users.CreateUserRequest, db: db_dependency):
    return AuthService.create_user(db, user_details)

@router.post("/token", response_model=users.Token)
def login(form_data: oauth2_bearer, db: db_dependency):
    return AuthService.login_user(db, form_data.username, form_data.password, SECRET_KEY, ALGORITHM)