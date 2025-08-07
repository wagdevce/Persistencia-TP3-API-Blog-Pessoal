
from typing import List, Optional
from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.PyObjectId import PyObjectId


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagOut(TagBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "from_attributes": True
    }


class PaginatedTagResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List[TagOut]