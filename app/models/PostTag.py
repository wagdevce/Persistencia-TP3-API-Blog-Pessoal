# app/models/PostTag.py

from typing import Optional, List
from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.PyObjectId import PyObjectId

# Modelo base da ligação Post-Tag
class PostTagBase(BaseModel):
    post_id: str
    tag_id: str

# Modelo para criar uma nova ligação
class PostTagCreate(PostTagBase):
    pass

# Modelo para retornar dados da ligação pela API
class PostTagOut(PostTagBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "from_attributes": True
    }

# Modelo para respostas com paginação de ligações
class PaginatedPostTagResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List[PostTagOut]