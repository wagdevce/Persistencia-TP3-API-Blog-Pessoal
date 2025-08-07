
from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from bson import ObjectId

from ..core.db import user_collection, comment_collection
from ..logs.logger import logger

from ..models import UserCreate, UserOut, PaginatedUserResponse, UserUpdate
from .utils import object_id

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Cria um novo usuário no sistema.
    """
    logger.debug(f"Tentando criar usuário com email: {user.email}")
    
   
    user_dict = user.model_dump()
    
    existing_user = await user_collection.find_one({"$or": [{"email": user.email}, {"username": user.username}]})
    if existing_user:
        logger.warning(f"Tentativa de criar usuário com email ou username já existente: {user.email}/{user.username}")
        raise HTTPException(status_code=409, detail="Email ou nome de usuário já cadastrado.")

    result = await user_collection.insert_one(user_dict)
    created = await user_collection.find_one({"_id": result.inserted_id})
    
    logger.info(f"Usuário criado com sucesso: {created['email']}")
    return created


@router.get("/", response_model=PaginatedUserResponse)
async def list_users(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    """
    Lista os usuários cadastrados.
    """
    total = await user_collection.count_documents({})
    users = await user_collection.find().skip(skip).limit(limit).to_list(length=limit)
    
    return {
        "total": total,
        "data": users
    }



@router.get("/{identifier}", response_model=UserOut)
async def get_user(identifier: str):
    """
    Busca um único usuário pelo seu ID ou pelo seu username (exato, case-insensitive).
    """
    logger.debug(f"Buscando usuário com o identificador: {identifier}")
    
   
    if ObjectId.is_valid(identifier):
        query = {"_id": ObjectId(identifier)}
    else:
        
        query = {"username": {"$regex": f"^{identifier}$", "$options": "i"}}

    user = await user_collection.find_one(query)
    
    if user:
        logger.info(f"Usuário encontrado com o identificador '{identifier}'.")
        return user
        
    logger.warning(f"Usuário com o identificador '{identifier}' não encontrado.")
    raise HTTPException(status_code=404, detail="Usuário não encontrado")


@router.put("/{user_id}", response_model=UserOut)
async def update_user(user_id: str, user_update: UserUpdate):
    """
    Atualiza os dados de um usuário (username, email, password).
    """
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização.")
    
    
    if "password" in update_data:
        pass 
    
    updated_user = await user_collection.find_one_and_update(
        {"_id": object_id(user_id)},
        {"$set": update_data},
        return_document=True
    )

    if updated_user:
        logger.info(f"Usuário ID {user_id} atualizado com sucesso.")
        return updated_user
    
    raise HTTPException(status_code=404, detail="Usuário não encontrado")



@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    """
    Deleta um usuário e todos os seus comentários.
    """
    delete_result = await user_collection.delete_one({"_id": object_id(user_id)})
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    comments_deleted = await comment_collection.delete_many({"user_id": user_id})
    
    logger.info(f"Usuário ID {user_id} e {comments_deleted.deleted_count} comentários associados foram deletados.")
    return