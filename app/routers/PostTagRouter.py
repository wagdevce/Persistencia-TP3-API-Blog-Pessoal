
from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from datetime import datetime


from app.models import PostTagCreate, PostTagOut, PaginatedPostTagResponse
from app.core.db import post_collection, tag_collection, post_tag_collection
from ..logs.logger import logger
from .utils import object_id

router = APIRouter(prefix="/post-tags", tags=["Post-Tag Associations"])

@router.post("/", response_model=PostTagOut, status_code=status.HTTP_201_CREATED, summary="Associar uma Tag a um Post")
async def create_post_tag_association(association: PostTagCreate):
    """
    Cria uma associação (link) entre um post e uma tag existentes.

    - Valida se o `post_id` e o `tag_id` fornecidos são válidos.
    - Adiciona a `tag_id` à lista `tags_id` do documento do post.
    - Cria um novo documento na coleção `post_tags` para registrar a associação.
    """
    logger.debug(f"Associando post {association.post_id} com tag {association.tag_id}")
    try:
        # Validar se o post e a tag existem
        post = await post_collection.find_one({"_id": object_id(association.post_id)})
        if not post:
            raise HTTPException(status_code=404, detail=f"Post com ID {association.post_id} não encontrado.")
        
        tag = await tag_collection.find_one({"_id": object_id(association.tag_id)})
        if not tag:
            raise HTTPException(status_code=404, detail=f"Tag com ID {association.tag_id} não encontrada.")

        # Cria a associação
        association_dict = association.model_dump()
        result = await post_tag_collection.insert_one(association_dict)
        
        # Adiciona a referência da tag no documento do post
        await post_collection.update_one(
            {"_id": object_id(association.post_id)},
            {"$addToSet": {"tags_id": association.tag_id}} # $addToSet evita duplicatas
        )

        created = await post_tag_collection.find_one({"_id": result.inserted_id})
        created["_id"] = str(created["_id"])
        logger.info(f"Associação criada com sucesso: {created}")
        return created

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao criar associação Post-Tag: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao criar associação")

@router.get("/", response_model=PaginatedPostTagResponse, summary="Listar Todas as Associações")
async def list_post_tag_associations(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    """
    Retorna uma lista paginada de todas as associações entre posts e tags.
    """
    logger.debug(f"Listando associações post-tag com skip={skip}, limit={limit}")
    try:
        total = await post_tag_collection.count_documents({})
        associations = await post_tag_collection.find().skip(skip).limit(limit).to_list(length=limit)
        
        for assoc in associations:
            assoc["_id"] = str(assoc["_id"])
            
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": associations
        }
    except Exception as e:
        logger.exception(f"Erro ao listar associações: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar associações")

@router.delete("/{association_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desassociar uma Tag de um Post")
async def delete_post_tag_association(association_id: str):
    """
    Remove a associação (link) entre um post e uma tag pelo ID da associação.

    - Remove o documento da coleção `post_tags`.
    - Remove a `tag_id` da lista `tags_id` do documento do post correspondente.
    """
    logger.debug(f"Deletando associação com ID {association_id}")
    try:
        oid = object_id(association_id)
        
        # Encontra a associação para saber qual post e tag desconectar
        association_to_delete = await post_tag_collection.find_one({"_id": oid})
        if not association_to_delete:
            raise HTTPException(status_code=404, detail="Associação não encontrada")

        # Remove a referência da tag do documento do post
        post_id = association_to_delete["post_id"]
        tag_id = association_to_delete["tag_id"]
        await post_collection.update_one(
            {"_id": object_id(post_id)},
            {"$pull": {"tags_id": tag_id}} # $pull remove o item da lista
        )

        # Deleta o documento da associação
        await post_tag_collection.delete_one({"_id": oid})
        
        logger.info(f"Associação ID {association_id} (Post: {post_id}, Tag: {tag_id}) deletada.")
        return

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao deletar associação: {e}")
        raise HTTPException(status_code=500, detail="Erro ao deletar associação")