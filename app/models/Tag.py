# app/models/Tag.py

from typing import List, Optional
from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.PyObjectId import PyObjectId

# Modelo base da Tag
class TagBase(BaseModel):
    name: str

# Modelo para criar uma nova Tag
class TagCreate(TagBase):
    pass

# Modelo para retornar dados da Tag pela API
class TagOut(TagBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "from_attributes": True
    }

# Modelo para respostas com paginação de Tags
class PaginatedTagResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List[TagOut]