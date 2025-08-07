# app/models/Comment.py

from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.PyObjectId import PyObjectId


class CommentBase(BaseModel):
    post_id: str  
    user_id: str 
    content: str
    creation_date: datetime = Field(default_factory=datetime.now)

class CommentUpdate(BaseModel):
    content: Optional[str] = None


class CommentCreate(CommentBase):
    pass


class CommentOut(CommentBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "from_attributes": True
    }


class PaginatedCommentResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List[CommentOut]