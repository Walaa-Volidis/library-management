from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated, List
from app import schemas
from app.database import SessionLocal
from app.services.borrow_service import BorrowService

router = APIRouter(
    prefix="/borrows",
    tags=["Borrows"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/", response_model=schemas.BorrowResponse)
def borrow_book(borrow_in: schemas.BorrowCreate, db: db_dependency):
    return BorrowService.borrow_book(db, borrow_in)

@router.post("/{borrow_id}/return", response_model=schemas.BorrowResponse)
def return_book(borrow_id: int, return_in: schemas.BorrowReturn, db: db_dependency):
    return BorrowService.return_book(db, borrow_id, return_in)

@router.get("/members/{member_id}/borrows", response_model=List[schemas.BorrowResponse])
def get_borrows_for_member(member_id: int, db: db_dependency):
    return BorrowService.get_member_history(db, member_id)