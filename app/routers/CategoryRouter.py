
from fastapi import APIRouter, HTTPException, Query, status
from typing import List
from bson import ObjectId

from app.models import CategoryOut, CategoryCreate, PaginatedCategoryResponse, PostOut
from app.core.db import category_collection, post_collection
from ..logs.logger import logger
from .utils import object_id

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED, summary="Criar uma Nova Categoria")
async def create_category(category: CategoryCreate):
    """
    Cria uma nova categoria no banco de dados.

    - **name**: O nome da categoria (obrigatório).
    - **description**: Uma breve descrição sobre a categoria (opcional).
    """
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

@router.get("/", response_model=PaginatedCategoryResponse, summary="Listar Todas as Categorias")
async def list_categories(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    """
    Retorna uma lista paginada de todas as categorias cadastradas no sistema.
    """
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

@router.get("/count", response_model=dict, summary="Contar Total de Categorias")
async def count_categories():
    """
    Retorna a quantidade total de categorias cadastradas.
    """
    try:
        count = await category_collection.count_documents({})
        logger.info(f"Total de categorias: {count}")
        return {"total": count}
    except Exception as e:
        logger.exception("Erro ao contar categorias: " + str(e))
        raise HTTPException(status_code=500, detail="Erro interno ao contar categorias")

@router.get("/{identifier}", response_model=CategoryOut, summary="Buscar Categoria por ID ou Nome")
async def get_category(identifier: str):
    """
    Busca uma única categoria no banco de dados.

    A busca pode ser feita de duas formas:
    - Pelo **ID** da categoria (ex: `689efb3f24f2c56fb436b16a`).
    - Pelo **nome exato** da categoria (ex: `Tecnologia`).

    A busca por nome não diferencia maiúsculas de minúsculas.
    """
    logger.debug(f"Buscando categoria com o identificador: {identifier}")
    
    if ObjectId.is_valid(identifier):
        query = {"_id": ObjectId(identifier)}
    else:
        query = {"name": {"$regex": f"^{identifier}$", "$options": "i"}}

    category = await category_collection.find_one(query)
    
    if category:
        logger.info(f"Categoria encontrada com o identificador '{identifier}'.")
        category["_id"] = str(category["_id"])
        return category
        
    logger.warning(f"Categoria com o identificador '{identifier}' não encontrada.")
    raise HTTPException(status_code=404, detail="Categoria não encontrada")

@router.put("/{category_id}", response_model=CategoryOut, summary="Atualizar uma Categoria")
async def update_category(category_id: str, update_data: CategoryCreate):
    """
    Atualiza os dados de uma categoria existente, buscando-a pelo seu ID.
    """
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

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deletar uma Categoria")
async def delete_category(category_id: str):
    """
    Deleta uma categoria do banco de dados pelo seu ID.

    Ao deletar uma categoria, todos os posts que pertenciam a ela terão seu campo `category_id` definido como nulo.
    """
    logger.debug(f"Tentando deletar categoria ID {category_id}")
    try:
        oid = object_id(category_id)

        result_update = await post_collection.update_many(
            {"category_id": category_id},
            {"$set": {"category_id": None}}
        )
        logger.info(f"{result_update.modified_count} posts tiveram o campo category_id removido")

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

@router.get("/{category_id}/posts", response_model=List[PostOut], summary="Listar Posts de uma Categoria")
async def get_posts_by_category(category_id: str):
    """
    Retorna uma lista de todos os posts que pertencem a uma categoria específica,
    identificada pelo seu ID.
    """
    logger.debug(f"Buscando posts na categoria {category_id}")
    try:
        oid = object_id(category_id)
        category = await category_collection.find_one({"_id": oid})
        if not category:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")

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