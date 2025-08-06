
from fastapi import APIRouter, HTTPException, Query, status
from typing import List
from bson import ObjectId

# modelos e coleções
from app.models import CommentOut, CommentCreate, CommentUpdate, PaginatedCommentResponse
from ..core.db import comment_collection, post_collection, user_collection
from ..logs.logger import logger
from .utils import object_id

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED, summary="Criar um Novo Comentário")
async def create_comment(comment: CommentCreate):
    """
    Cria um novo comentário e o associa a um post e a um usuário existente.

    - **post_id**: O ID do post que está sendo comentado.
    - **user_id**: O ID do usuário que está fazendo o comentário.
    - **content**: O texto do comentário.
    """
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

@router.get("/", response_model=PaginatedCommentResponse, summary="Listar Todos os Comentários")
async def list_comments(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    """
    Retorna uma lista paginada de todos os comentários do sistema.
    """
    logger.debug(f"Listando todos os comentários com skip={skip}, limit={limit}")
    try:
        total = await comment_collection.count_documents({})
        comments = await comment_collection.find().skip(skip).limit(limit).to_list(length=limit)

        for comment in comments:
            comment["_id"] = str(comment["_id"])

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": comments
        }
    except Exception as e:
        logger.exception(f"Erro ao listar comentários: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar comentários")

@router.get("/by_post/{post_id}", response_model=List[CommentOut], summary="Listar Comentários de um Post")
async def get_comments_by_post(post_id: str):
    """
    Retorna uma lista de todos os comentários associados a um post específico.
    """
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

@router.get("/{comment_id}", response_model=CommentOut, summary="Buscar um Comentário por ID")
async def get_comment(comment_id: str):
    """
    Busca e retorna um único comentário pelo seu ID.
    """
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

@router.put("/{comment_id}", response_model=CommentOut, summary="Atualizar um Comentário")
async def update_comment(comment_id: str, comment_update: CommentUpdate):
    """
    Atualiza o conteúdo de um comentário existente.
    """
    logger.debug(f"Atualizando comentário ID {comment_id}")
    
    update_data = comment_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização.")
    
    updated_comment = await comment_collection.find_one_and_update(
        {"_id": object_id(comment_id)},
        {"$set": update_data},
        return_document=True
    )

    if not updated_comment:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")

    logger.info(f"Comentário ID {comment_id} atualizado com sucesso.")
    return updated_comment

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deletar um Comentário")
async def delete_comment(comment_id: str):
    """
    Deleta um comentário do banco de dados pelo seu ID.
    """
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