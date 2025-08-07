
from typing import Optional, List
from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.PyObjectId import PyObjectId


class PostTagBase(BaseModel):
    post_id: str
    tag_id: str


class PostTagCreate(PostTagBase):
    pass


class PostTagOut(PostTagBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "from_attributes": True
    }


class PaginatedPostTagResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List[PostTagOut]