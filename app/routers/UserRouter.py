
from fastapi import APIRouter, HTTPException, status, Query
from typing import List

# Adicionamos 'comment_collection' para a lógica de deleção
from ..core.db import user_collection, comment_collection
from ..logs.logger import logger
# Adicionamos o novo 'UserUpdate' e o 'object_id' de utils
from ..models import UserCreate, UserOut, PaginatedUserResponse, UserUpdate
from .utils import object_id

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Cria um novo usuário no sistema.
    """
    logger.debug(f"Tentando criar usuário com email: {user.email}")
    
    # Em um projeto real, a senha seria 'hasheada' aqui
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


# --- NOVO ENDPOINT ---
@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str):
    """
    Busca um único usuário pelo seu ID.
    """
    user = await user_collection.find_one({"_id": object_id(user_id)})
    if user:
        return user
    raise HTTPException(status_code=404, detail="Usuário não encontrado")


# --- NOVO ENDPOINT ---
@router.put("/{user_id}", response_model=UserOut)
async def update_user(user_id: str, user_update: UserUpdate):
    """
    Atualiza os dados de um usuário (username, email, password).
    """
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização.")
    
    # Lógica para hashear a senha se ela for atualizada
    if "password" in update_data:
        # Em um projeto real, a senha seria hasheada aqui
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


# --- NOVO ENDPOINT ---
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    """
    Deleta um usuário e todos os seus comentários.
    """
    # Deleta o usuário
    delete_result = await user_collection.delete_one({"_id": object_id(user_id)})
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    # Deleta os comentários associados a este usuário
    comments_deleted = await comment_collection.delete_many({"user_id": user_id})
    
    logger.info(f"Usuário ID {user_id} e {comments_deleted.deleted_count} comentários associados foram deletados.")
    return