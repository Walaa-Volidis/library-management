from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, List
from app import schemas, models
from app.database import SessionLocal

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
    existing_member = db.query(models.member.Member).filter(models.member.Member.email == member_in.email).first()
    if existing_member:
        raise HTTPException(status_code=409, detail="Email already registered")
    member_data = member_in.model_dump()
    db_member = models.member.Member(**member_data)    
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

@router.get("/", response_model=List[schemas.MemberResponse])
def get_all_members(db: db_dependency):
    return db.query(models.member.Member).all()

@router.get("/{member_id}", response_model=schemas.MemberResponse)
def get_member(member_id: int, db: db_dependency):
    db_member = db.query(models.member.Member).filter(models.member.Member.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member

@router.delete("/{member_id}")
def delete_member(member_id: int, db: db_dependency):
    db_member = db.query(models.member.Member).filter(models.member.Member.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    db.delete(db_member)
    db.commit()
    return {"message": f"Member with id {member_id} has been deleted successfully"}

