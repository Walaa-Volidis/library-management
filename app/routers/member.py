from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, List
from app import schemas, models
from app.database import SessionLocal
from app.services.member_service import MemberService

router = APIRouter(
    prefix="/members",
    tags=["Members"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/", response_model=schemas.MemberResponse)
def create_member(member_in: schemas.MemberCreate, db: db_dependency):
    return MemberService.create(db, member_in)

@router.get("/", response_model=List[schemas.MemberResponse])
def get_all_members(db: db_dependency):
    return MemberService.get_all(db)

@router.get("/{member_id}", response_model=schemas.MemberResponse)
def get_member(member_id: int, db: db_dependency):
    return MemberService.get_one(db, member_id)

@router.delete("/{member_id}")
def delete_member(member_id: int, db: db_dependency):
    return MemberService.delete(db, member_id)