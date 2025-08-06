
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId

from app.models.PyObjectId import PyObjectId


class AuthorProfile(BaseModel):
    """
    Este é o nosso documento embutido (embedded document).
    Ele não terá uma coleção própria no banco, viverá apenas dentro de um Post.
    """
    name: str
    bio: Optional[str] = None


# Modelo base do Post
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

# Modelo para criar um novo post
class PostCreate(PostBase):
    pass

# Modelo para retornar dados do post pela API
class PostOut(PostBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "from_attributes": True
    }

# Modelo para respostas com paginação de posts
class PaginatedPostResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List[PostOut]