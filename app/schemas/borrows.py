from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class BorrowBase(BaseModel):
    book_id: int = Field(..., example="550e8400-e29b-41d4-a716-446655440000")
    member_id: int = Field(..., example="123e4567-e89b-12d3-a456-426614174000")

class BorrowCreate(BorrowBase):
    pass 

class BorrowReturn(BaseModel):
    return_date: datetime = Field(default_factory=datetime.utcnow)

class BorrowResponse(BorrowBase):
    id: int
    borrowed_at: datetime
    due_date: datetime
    returned_at: Optional[datetime] = None 
    model_config = ConfigDict(from_attributes=True)