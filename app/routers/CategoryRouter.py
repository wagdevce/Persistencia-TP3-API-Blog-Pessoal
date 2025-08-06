# app/routers/CategoryRouter.py

from fastapi import APIRouter, HTTPException, Query, status
from typing import List

# Importando nossos novos modelos
from app.models import CategoryOut, CategoryCreate, PaginatedCategoryResponse, PostOut

# Precisaremos definir estas coleções no nosso arquivo de DB
from app.core.db import category_collection, post_collection
from ..logs.logger import logger
from .utils import object_id # Importando a função utilitária

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate):
    logger.debug(f"Tentando criar categoria: {category}")
    try:
        category_dict = category.model_dump()
        result = await category_collection.insert_one(category_dict)
        created = await category_collection.find_one({"_id": result.inserted_id})
        
        created["_id"] = str(created["_id"])
        logger.info(f"Categoria criada com sucesso: {created}")
        return created
    except Exception as e:
        logger.exception(f"Erro ao criar categoria: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao criar categoria")

@router.get("/", response_model=PaginatedCategoryResponse)
async def list_categories(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    logger.debug(f"Listando categorias com skip={skip}, limit={limit}")
    try:
        total = await category_collection.count_documents({})
        categories = await category_collection.find().skip(skip).limit(limit).to_list(length=limit)
        
        for cat in categories:
            cat["_id"] = str(cat["_id"])
            
        logger.info(f"{len(categories)} categorias encontradas")
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": categories
        }
    except Exception as e:
        logger.exception("Erro ao listar categorias: " + str(e))
        raise HTTPException(status_code=500, detail="Erro interno ao listar categorias")

@router.get("/{category_id}", response_model=CategoryOut)
async def get_category(category_id: str):
    logger.debug(f"Buscando categoria com ID {category_id}")
    try:
        oid = object_id(category_id)
        category = await category_collection.find_one({"_id": oid})
        
        if not category:
            logger.warning(f"Categoria ID {category_id} não encontrada")
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
            
        category["_id"] = str(category["_id"])
        return category
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao buscar categoria ID {category_id}: " + str(e))
        raise HTTPException(status_code=500, detail="Erro interno ao buscar categoria")

@router.get("/count", response_model=dict)
async def count_categories():
    try:
        count = await category_collection.count_documents({})
        logger.info(f"Total de categorias: {count}")
        return {"total": count}
    except Exception as e:
        logger.exception("Erro ao contar categorias: " + str(e))
        raise HTTPException(status_code=500, detail="Erro interno ao contar categorias")

@router.put("/{category_id}", response_model=CategoryOut)
async def update_category(category_id: str, update_data: CategoryCreate):
    logger.debug(f"Atualizando categoria ID {category_id}")
    try:
        oid = object_id(category_id)
        update_dict = update_data.model_dump(exclude_unset=True)
        result = await category_collection.update_one({"_id": oid}, {"$set": update_dict})
        
        if result.matched_count == 0:
            logger.warning(f"Categoria ID {category_id} não encontrada para atualização")
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
            
        updated = await category_collection.find_one({"_id": oid})
        updated["_id"] = str(updated["_id"])
        logger.info(f"Categoria ID {category_id} atualizada com sucesso")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao atualizar categoria ID {category_id}: " + str(e))
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar categoria")

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: str):
    logger.debug(f"Tentando deletar categoria ID {category_id}")
    try:
        oid = object_id(category_id)

        # Atualiza os posts, definindo category_id como null
        # Uma alternativa seria mover para uma categoria "Geral"
        result_update = await post_collection.update_many(
            {"category_id": category_id},
            {"$set": {"category_id": None}}
        )
        logger.info(f"{result_update.modified_count} posts tiveram o campo category_id removido")

        # Deleta a categoria
        result_delete = await category_collection.delete_one({"_id": oid})
        if result_delete.deleted_count == 0:
            logger.warning(f"Categoria ID {category_id} não encontrada para deleção")
            raise HTTPException(status_code=404, detail="Categoria não encontrada")

        logger.info(f"Categoria ID {category_id} deletada com sucesso")
        return

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao deletar categoria ID {category_id}: " + str(e))
        raise HTTPException(status_code=500, detail="Erro interno ao deletar categoria")

@router.get("/{category_id}/posts", response_model=List[PostOut])
async def get_posts_by_category(category_id: str):
    logger.debug(f"Buscando posts na categoria {category_id}")
    try:
        # Verifica se a categoria existe
        oid = object_id(category_id)
        category = await category_collection.find_one({"_id": oid})
        if not category:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")

        # Busca os posts
        posts = await post_collection.find({"category_id": category_id}).to_list(length=None)

        for post in posts:
            post["_id"] = str(post["_id"])

        logger.info(f"{len(posts)} posts encontrados na categoria {category_id}")
        return posts

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao buscar posts por categoria {category_id}: " + str(e))
        raise HTTPException(status_code=500, detail="Erro ao buscar posts por categoria")
    
