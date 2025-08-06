
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from .PyObjectId import PyObjectId

class UserBase(BaseModel):
    username: str
    email: str
    creation_date: datetime = Field(default_factory=datetime.now)

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    """
    Modelo de saída que não expõe a senha do usuário.
    """
    id: Optional[PyObjectId] = Field(None, alias="_id")

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "from_attributes": True
    }

class PaginatedUserResponse(BaseModel):
    total: int
    data: List[UserOut]