from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class BookBase(BaseModel):  
    title: str = Field(..., example="The Great Gatsby")
    author: str = Field(..., example="F. Scott Fitzgerald")
    isbn: str = Field(..., example="978-0743273565")
    total_copies: int = Field(..., example=5, gt=0)

class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, example="The Great Gatsby")
    author: Optional[str] = Field(None, example="F. Scott Fitzgerald")
    isbn: Optional[str] = Field(None, example="978-0743273565")
    total_copies: Optional[int] = Field(None, example=5, gt=0)

class BookResponse(BookBase):
    id: int
    available_copies: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

