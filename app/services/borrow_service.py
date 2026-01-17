from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta
from app import models, schemas

class BorrowService:
    @staticmethod
    def borrow_book(db: Session, borrow_in: schemas.BorrowCreate):
        db_book = db.query(models.book.Book).filter(models.book.Book.id == borrow_in.book_id).first()
        if not db_book or db_book.available_copies < 1:
            raise HTTPException(status_code=409, detail="The book is not available for borrowing")

        db_member = db.query(models.member.Member).filter(models.member.Member.id == borrow_in.member_id).first()
        if not db_member:
            raise HTTPException(status_code=404, detail="Member not found")
        db_book.available_copies -= 1
        due_date = datetime.now() + timedelta(days=14)
        new_record = models.borrow.BorrowRecord(
            **borrow_in.model_dump(),
            due_date=due_date
        )
        
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record

    @staticmethod
    def return_book(db: Session, borrow_id: int, return_in: schemas.BorrowReturn):
        db_borrow = db.query(models.borrow.BorrowRecord).filter(models.borrow.BorrowRecord.id == borrow_id).first()
        if not db_borrow:
            raise HTTPException(status_code=404, detail="Borrow record not found")
        
        if db_borrow.returned_at:
            raise HTTPException(status_code=409, detail="Book has already been returned")

        db_borrow.returned_at = return_in.return_date
        db_book = db.query(models.book.Book).filter(models.book.Book.id == db_borrow.book_id).first()
        if not db_book:  
            raise HTTPException(status_code=404, detail="Book not found")  
        db_book.available_copies += 1
        db.commit()
        db.refresh(db_borrow)
        return db_borrow

    @staticmethod
    def get_member_history(db: Session, member_id: int):
        return db.query(models.borrow.BorrowRecord).filter(models.borrow.BorrowRecord.member_id == member_id).all()