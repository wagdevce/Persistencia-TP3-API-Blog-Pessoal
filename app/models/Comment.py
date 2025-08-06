# app/models/Comment.py

from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.PyObjectId import PyObjectId

# Modelo base do Comentário
class CommentBase(BaseModel):
    post_id: str  # ID do post ao qual o comentário pertence
    user_id: str 
    content: str
    creation_date: datetime = Field(default_factory=datetime.now)

# Modelo para criar um novo comentário
class CommentCreate(CommentBase):
    pass

# Modelo para retornar dados do comentário pela API
class CommentOut(CommentBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "from_attributes": True
    }

# Modelo para respostas com paginação de comentários
class PaginatedCommentResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List[CommentOut]