

from fastapi import APIRouter, HTTPException, Query, status
from typing import List
from bson import ObjectId

#  modelos da camada de dados
from app.models import TagOut, TagCreate, PaginatedTagResponse

# coleções necessárias para a deleção em cascata
from app.core.db import tag_collection, post_collection, post_tag_collection
from ..logs.logger import logger
from .utils import object_id

router = APIRouter(prefix="/tags", tags=["Tags"])

@router.post("/", response_model=TagOut, status_code=status.HTTP_201_CREATED, summary="Criar uma Nova Tag")
async def create_tag(tag: TagCreate):
    """
    Cria uma nova tag no banco de dados.
    A tag consiste em um nome único que pode ser associado a múltiplos posts.
    """
    logger.debug(f"Tentando criar tag: {tag}")
    try:
        # Verifica se já existe uma tag com o mesmo nome (case-insensitive)
        existing_tag = await tag_collection.find_one({"name": {"$regex": f"^{tag.name}$", "$options": "i"}})
        if existing_tag:
            raise HTTPException(status_code=409, detail="Uma tag com este nome já existe.")

        tag_dict = tag.model_dump()
        result = await tag_collection.insert_one(tag_dict)
        created = await tag_collection.find_one({"_id": result.inserted_id})
        
        created["_id"] = str(created["_id"])
        logger.info(f"Tag criada com sucesso: {created}")
        return created
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao criar tag: {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar tag")


@router.get("/", response_model=PaginatedTagResponse, summary="Listar Todas as Tags")
async def list_tags(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    """
    Retorna uma lista paginada de todas as tags cadastradas no sistema.
    """
    try:
        logger.debug(f"Listando tags com skip={skip}, limit={limit}")
        total = await tag_collection.count_documents({})
        tags = await tag_collection.find().skip(skip).limit(limit).to_list(length=limit)
        
        for tag in tags:
            tag["_id"] = str(tag["_id"])
            
        logger.info(f"{len(tags)} tags listadas com sucesso.")
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": tags
        }
    except Exception as e:
        logger.exception(f"Erro ao listar tags: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar tags")

@router.get("/count", response_model=dict, summary="Contar Total de Tags")
async def count_tags():
    """
    Retorna a quantidade total de tags cadastradas.
    """
    try:
        count = await tag_collection.count_documents({})
        logger.info(f"Total de tags: {count}")
        return {"total": count}
    except Exception as e:
        logger.exception("Erro ao contar tags: " + str(e))
        raise HTTPException(status_code=500, detail="Erro interno ao contar tags")    

@router.get("/{identifier}", response_model=TagOut, summary="Buscar Tag por ID ou Nome")
async def get_tag(identifier: str):
    """
    Busca uma única tag no banco de dados.

    A busca pode ser feita de duas formas:
    - Pelo **ID** da tag.
    - Pelo **nome exato** da tag (não diferencia maiúsculas de minúsculas).
    """
    logger.debug(f"Buscando tag com o identificador: {identifier}")
    
    if ObjectId.is_valid(identifier):
        query = {"_id": ObjectId(identifier)}
    else:
        query = {"name": {"$regex": f"^{identifier}$", "$options": "i"}}
        
    tag = await tag_collection.find_one(query)
    
    if not tag:
        logger.warning(f"Tag com identificador '{identifier}' não encontrada.")
        raise HTTPException(status_code=404, detail="Tag não encontrada")

    tag["_id"] = str(tag["_id"])
    logger.info(f"Tag recuperada com sucesso: {tag}")
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deletar uma Tag")
async def delete_tag(tag_id: str):
    """
    Deleta uma tag do banco de dados e remove sua associação de todos os posts.
    """
    logger.debug(f"Tentando deletar tag ID {tag_id}")
    try:
        oid = object_id(tag_id)
        
        # Deleta a tag da coleção de tags
        result_delete = await tag_collection.delete_one({"_id": oid})
        
        if result_delete.deleted_count == 0:
            logger.warning(f"Tag com ID {tag_id} não encontrada para deleção.")
            raise HTTPException(status_code=404, detail="Tag não encontrada")

        # Remove a referência da tag de todos os posts que a continham
        update_result = await post_collection.update_many(
            {"tags_id": tag_id},
            {"$pull": {"tags_id": tag_id}}
        )
        
        # Remove as associações da coleção PostTag
        assoc_delete_result = await post_tag_collection.delete_many({"tag_id": tag_id})

        logger.info(f"Tag ID {tag_id} deletada. {update_result.modified_count} posts atualizados. {assoc_delete_result.deleted_count} associações removidas.")
        return

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao deletar tag ID {tag_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao deletar tag")