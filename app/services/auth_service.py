import os
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.models.users import Users
from app.schemas.users import CreateUserRequest
from dotenv import load_dotenv

load_dotenv()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:    
    @staticmethod
    def create_user(db: Session, user_details: CreateUserRequest) -> dict:
        existing_user = db.query(Users).filter(Users.username == user_details.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        hashed_password = bcrypt_context.hash(user_details.password)
        
        new_user = Users(
            username=user_details.username,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"msg": "User created successfully"}
    
   