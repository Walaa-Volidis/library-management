import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.users import Users
from app.schemas.users import CreateUserRequest

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class AuthService:
    @staticmethod
    def create_user(db: Session, user_details: CreateUserRequest) -> dict:
        existing_user = db.query(Users).filter(
            Users.username == user_details.username
        ).first()
        
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
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Users | None:
        user = db.query(Users).filter(Users.username == username).first()
        if not user:
            return None
        if not bcrypt_context.verify(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def create_access_token(
        data: dict,
        secret_key: str,
        algorithm: str,
        expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, secret_key, algorithm=algorithm) 
    
    @staticmethod
    def login_user(
        db: Session,
        username: str,
        password: str,
        secret_key: str,
        algorithm: str
    ) -> dict:
        user = AuthService.authenticate_user(db, username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )      
        access_token = AuthService.create_access_token(
            data={"sub": user.username},
            secret_key=secret_key,
            algorithm=algorithm
        )       
        return {"access_token": access_token, "token_type": "bearer"}
    @staticmethod
    def get_current_user(token: str, db: Session) -> Users:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            
            if username is None:
                raise credentials_exception
                
        except JWTError:
            raise credentials_exception
        
        user = db.query(Users).filter(Users.username == username).first()
        
        if user is None:
            raise credentials_exception
        
        return user
