# app/routers/PostTagRouter.py

from fastapi import APIRouter, HTTPException, status
from typing import List

# Nossos novos modelos e coleções
from app.models import PostTagCreate, PostTagOut, PaginatedPostTagResponse
from app.core.db import post_collection, tag_collection, post_tag_collection
from ..logs.logger import logger
from .utils import object_id

router = APIRouter(prefix="/post-tags", tags=["Post-Tag Associations"])

@router.post("/", response_model=PostTagOut, status_code=status.HTTP_201_CREATED)
async def create_post_tag_association(association: PostTagCreate):
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

@router.delete("/{association_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_tag_association(association_id: str):
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