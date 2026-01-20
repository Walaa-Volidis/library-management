from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class CreateUserRequest(BaseModel):  
    username: str = Field(..., min_length=3, example="walaa volidis")
    password: str = Field(..., min_length=6, example="strongpassword123")



class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"