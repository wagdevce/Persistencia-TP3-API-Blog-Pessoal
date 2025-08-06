# app/routers/UserRouter.py

from fastapi import APIRouter, HTTPException, status, Query
from typing import List

from ..core.db import user_collection
from ..logs.logger import logger
from ..models import UserCreate, UserOut, PaginatedUserResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Cria um novo usuário no sistema.
    """
    logger.debug(f"Tentando criar usuário com email: {user.email}")
    
    # Em um projeto real, a senha seria 'hasheada' aqui antes de salvar
    # Ex: from passlib.context import CryptContext
    # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # hashed_password = pwd_context.hash(user.password)
    
    user_dict = user.model_dump()
    
    # Verifica se o email ou username já existe
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