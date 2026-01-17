from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, List
from app import schemas, models
from app.database import SessionLocal

router = APIRouter(
    prefix="/books",     
    tags=["Books"]       
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/", response_model=schemas.BookResponse)
def create_book(book_in: schemas.BookCreate, db: db_dependency):
    book_data = book_in.model_dump() 
    db_book = models.book.Book(
        **book_data, 
        available_copies=book_in.total_copies
    )
    
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@router.get("/", response_model=List[schemas.BookResponse])
def get_all_books(db: db_dependency, author: str = None, title: str = None, available_only: bool = None):
    query = db.query(models.book.Book)
    if author:
        query = query.filter(models.book.Book.author.ilike(f"%{author}%"))
    if title:
        query = query.filter(models.book.Book.title.ilike(f"%{title}%"))
    if available_only:
        query = query.filter(models.book.Book.available_copies > 0)
    return query.all() 


@router.delete("/{book_id}", response_model=schemas.BookResponse)
def delete_book(book_id: int, db:db_dependency):
    db_book = db.query(models.book.Book).filter(models.book.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(db_book)
    db.commit()
    return {"message": f"Book with id {book_id} has been deleted successfully"}

@router.get("/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: db_dependency):
    db_book = db.query(models.book.Book).filter(models.book.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.patch("/{book_id}", response_model=schemas.BookResponse)
def update_book(book_id: int, book_in: schemas.BookUpdate, db: db_dependency):
    db_book = db.query(models.book.Book).filter(models.book.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = book_in.model_dump(exclude_unset=True)

    if "total_copies" in update_data:
        new_total = update_data["total_copies"] 
        currently_borrowed = db_book.total_copies - db_book.available_copies
        
        if new_total < currently_borrowed:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot reduce total copies below borrowed amount ({currently_borrowed})"
            )
        
        db_book.total_copies = new_total
        db_book.available_copies = new_total - currently_borrowed

    for key, value in update_data.items():
        if key != "total_copies":
            setattr(db_book, key, value)

    db.commit()
    db.refresh(db_book)
    return db_book
    