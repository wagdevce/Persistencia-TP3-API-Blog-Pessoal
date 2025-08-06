
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from .PyObjectId import PyObjectId

class PostLikeBase(BaseModel):
    post_id: str
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)

class PostLikeCreate(PostLikeBase):
    pass

class PostLikeOut(PostLikeBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "from_attributes": True
    }