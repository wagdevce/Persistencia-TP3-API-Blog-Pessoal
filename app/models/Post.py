
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from pydantic import BaseModel
from app.models.PyObjectId import PyObjectId


class AuthorProfile(BaseModel):
    """
    Este é o nosso documento embutido (embedded document).
    Ele não terá uma coleção própria no banco, viverá apenas dentro de um Post.
    """
    name: str
    bio: Optional[str] = None



class PostBase(BaseModel):
    title: str
    content: str
    author: AuthorProfile
    publication_date: datetime
    category_id: str
    tags_id: List[str] = []
    likes: int = 0

    model_config = {
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
        "from_attributes": True
    }

class PostCreate(PostBase):
    pass


class PostOut(PostBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "from_attributes": True
    }


class PaginatedPostResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List[PostOut]

class PopularPostOut(PostOut):
    """
    Modelo de saída para posts populares, incluindo campos calculados.
    """
    comment_count: int
    popularity_score: float

class PaginatedPopularPostResponse(BaseModel):
    total: int
    data: List[PopularPostOut]    