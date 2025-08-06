from typing import List, Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from app.models.PyObjectId import PyObjectId

# Modelo base da Categoria
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None # Descrição é opcional

# Modelo usado para criar uma nova categoria
class CategoryCreate(CategoryBase):
    pass

# Modelo usado para retornar dados da API (inclui o ID)
class CategoryOut(CategoryBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True

# Modelo para respostas com paginação
class PaginatedCategoryResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List[CategoryOut]