
from fastapi import APIRouter, HTTPException, Query, status
from typing import List

# modelos e coleções
from app.models import CommentOut, CommentCreate
# Importamos PaginatedUserResponse apenas para o tipo de retorno
from app.models.Comment import PaginatedCommentResponse 
from ..core.db import comment_collection, post_collection, user_collection # <-- Adicionamos user_collection
from ..logs.logger import logger
from .utils import object_id

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(comment: CommentCreate):
    logger.debug("Criando um novo comentário")
    try:
        # Valida se o post referenciado existe
        post = await post_collection.find_one({"_id": object_id(comment.post_id)})
        if not post:
            logger.warning(f"Post com ID {comment.post_id} não encontrado.")
            raise HTTPException(status_code=404, detail="Post não encontrado para associar o comentário.")
        # Valida se o usuário referenciado existe
        user = await user_collection.find_one({"_id": object_id(comment.user_id)})
        if not user:
            logger.warning(f"Usuário com ID {comment.user_id} não encontrado.")
            raise HTTPException(status_code=404, detail="Usuário não encontrado para criar o comentário.")

        new_comment_dict = comment.model_dump()
        result = await comment_collection.insert_one(new_comment_dict)
        created = await comment_collection.find_one({"_id": result.inserted_id})

        created["_id"] = str(created["_id"])
        logger.info(f"Comentário criado com sucesso por usuário {comment.user_id}")
        return created

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao criar comentário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao criar comentário")

@router.get("/by_post/{post_id}", response_model=List[CommentOut])
async def get_comments_by_post(post_id: str):
    logger.debug(f"Buscando todos os comentários para o post ID {post_id}")
    try:
        comments = await comment_collection.find({"post_id": post_id}).to_list(length=None)
        for comment in comments:
            comment["_id"] = str(comment["_id"])
        
        logger.info(f"{len(comments)} comentários encontrados para o post {post_id}.")
        return comments
    except Exception as e:
        logger.exception(f"Erro ao buscar comentários para o post {post_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar comentários do post")


@router.get("/{comment_id}", response_model=CommentOut)
async def get_comment(comment_id: str):
    logger.debug(f"Buscando comentário com o ID {comment_id}")
    try:
        comment = await comment_collection.find_one({"_id": object_id(comment_id)})
        if not comment:
            logger.warning(f"Comentário com o ID {comment_id} não encontrado")
            raise HTTPException(status_code=404, detail="Comentário não encontrado")

        comment["_id"] = str(comment["_id"])
        return comment
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao buscar comentário: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar comentário")


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: str):
    logger.debug(f"Deletando comentário com o ID {comment_id}")
    try:
        result = await comment_collection.delete_one({"_id": object_id(comment_id)})

        if result.deleted_count == 0:
            logger.warning(f"Comentário com ID {comment_id} não encontrado para deleção")
            raise HTTPException(status_code=404, detail="Comentário não encontrado")

        logger.info(f"Comentário com ID {comment_id} deletado com sucesso")
        return

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro interno ao deletar comentário: {e}")
        raise HTTPException(status_code=500, detail="Erro ao deletar comentário")