from typing import List

from fastapi import APIRouter

from app import schemas
from app.dependencies import db_dependency, user_dependency
from app.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("/", response_model=schemas.BookResponse)
def create_book(
    book_in: schemas.BookCreate,
    db: db_dependency,
    current_user: user_dependency
):
    return BookService.create(db, book_in)

@router.get("/", response_model=List[schemas.BookResponse])
def get_all_books(
    db: db_dependency,
    author: str = None,
    title: str = None,
    available_only: bool = None,
    skip: int = 0,
    limit: int = 10
):
    return BookService.get_all(db, author, title, available_only, skip, limit)

@router.get("/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: db_dependency):
    return BookService.get_one(db, book_id)

@router.patch("/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int,
    book_in: schemas.BookUpdate,
    db: db_dependency,
    current_user: user_dependency
):
    return BookService.update(db, book_id, book_in)

@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    db: db_dependency,
    current_user: user_dependency
):
    return BookService.delete(db, book_id)