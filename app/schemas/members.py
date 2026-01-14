from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class MemberBase(BaseModel):  
    full_name: str = Field(..., min_length=3, example="Walaa Volidis")
    email: str = Field(..., example="walaa@example.com")

class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=3, example="Walaa Volidis")
    email: Optional[str] = Field(None, example="walaa@example.com")

class MemberResponse(MemberBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

