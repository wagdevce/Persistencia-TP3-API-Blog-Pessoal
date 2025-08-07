from typing import List, Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from app.models.PyObjectId import PyObjectId


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None 


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True


class PaginatedCategoryResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List[CategoryOut]