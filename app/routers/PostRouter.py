
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, status
from typing import Any, Dict, List

from app.models import PostCreate, PostOut, PaginatedPostResponse, PopularPostOut, PaginatedPopularPostResponse
from ..core.db import post_collection, tag_collection, category_collection, comment_collection, post_tag_collection, post_like_collection, user_collection
from ..logs.logger import logger
from .utils import object_id

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED, summary="Criar um Novo Post")
async def create_post(post: PostCreate):
    """
    Cria um novo post no banco de dados.

    - Valida a existência da `category_id`.
    - Valida a existência de todas as `tags_id` fornecidas.
    - O objeto `author` é embutido diretamente no documento do post.
    """
   
    if post.category_id:
        category = await category_collection.find_one({"_id": object_id(post.category_id)})
        if not category:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")

    
    for tag_id in post.tags_id:
        if not await tag_collection.find_one({"_id": object_id(tag_id)}):
            raise HTTPException(status_code=404, detail=f"Tag {tag_id} não encontrada")

    new_post_dict = post.model_dump()
    result = await post_collection.insert_one(new_post_dict)
    
    created = await post_collection.find_one({"_id": result.inserted_id})
    created["_id"] = str(created["_id"])
    logger.info(f"Post criado com sucesso: {created}")
    return created

@router.put("/{post_id}", response_model=PostOut, summary="Atualizar um Post Existente")
async def update_post(post_id: str, post_update: PostCreate):
    """
    Atualiza os dados de um post existente, buscando-o pelo seu ID.

    Apenas os campos fornecidos no corpo da requisição serão atualizados.
    """
    oid = object_id(post_id)
    if not await post_collection.find_one({"_id": oid}):
        raise HTTPException(status_code=404, detail="Post não encontrado")

    if post_update.category_id and not await category_collection.find_one({"_id": object_id(post_update.category_id)}):
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    for tag_id in post_update.tags_id:
        if not await tag_collection.find_one({"_id": object_id(tag_id)}):
            raise HTTPException(status_code=404, detail=f"Tag {tag_id} não encontrada")

    update_data = post_update.model_dump(exclude_unset=True)
    await post_collection.update_one({"_id": oid}, {"$set": update_data})
    
    updated = await post_collection.find_one({"_id": oid})
    updated["_id"] = str(updated["_id"])
    logger.info(f"Post ID {post_id} atualizado com sucesso.")
    return updated


@router.post("/{post_id}/like/{user_id}", response_model=PostOut, summary="Curtir um Post")
async def like_post(post_id: str, user_id: str):
    """
    Registra um like de um usuário específico em um post.
    
    - Incrementa o contador `likes` no documento do post.
    - Cria um registro na coleção `post_likes` para impedir likes duplicados.
    - Retorna o post com a contagem de likes atualizada.
    """
    logger.debug(f"Usuário {user_id} tentando curtir o post {post_id}")
    oid_post = object_id(post_id)
    oid_user = object_id(user_id)

    if not await post_collection.find_one({"_id": oid_post}):
        raise HTTPException(status_code=404, detail="Post não encontrado")
    if not await user_collection.find_one({"_id": oid_user}):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    existing_like = await post_like_collection.find_one({"post_id": post_id, "user_id": user_id})
    if existing_like:
        raise HTTPException(status_code=409, detail="Você já curtiu este post.")

    like_document = {"post_id": post_id, "user_id": user_id, "created_at": datetime.now()}
    await post_like_collection.insert_one(like_document)
    
    updated_post = await post_collection.find_one_and_update(
        {"_id": oid_post},
        {"$inc": {"likes": 1}},
        return_document=True
    )
    
    logger.info(f"Like do usuário {user_id} registrado com sucesso no post {post_id}.")
    return updated_post

@router.delete("/{post_id}/like/{user_id}", response_model=PostOut, summary="Remover Curtida (Dislike)")
async def dislike_post(post_id: str, user_id: str):
    """
    Remove um like de um usuário específico de um post.
    
    - Decrementa o contador `likes` no documento do post.
    - Remove o registro da coleção `post_likes`.
    """
    logger.debug(f"Usuário {user_id} tentando descurtir o post {post_id}")
    oid_post = object_id(post_id)

    delete_result = await post_like_collection.delete_one({"post_id": post_id, "user_id": user_id})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Você não curtiu este post para poder descurtir.")

    updated_post = await post_collection.find_one_and_update(
        {"_id": oid_post},
        {"$inc": {"likes": -1}},
        return_document=True
    )

    logger.info(f"Like do usuário {user_id} removido com sucesso do post {post_id}.")
    return updated_post

@router.get("/", response_model=PaginatedPostResponse, summary="Listar Todos os Posts")
async def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    publication_date: str = Query(None, description="Filtrar por data de publicação (formato: AAAA-MM-DD)"),
    sort_by: str = Query("likes", description="Campo para ordenação (ex: likes, publication_date)"),
    order: str = Query("desc", regex="^(asc|desc)$", description="Ordem ascendente (asc) ou descendente (desc)")
):
    """
    Retorna uma lista paginada de todos os posts. Permite filtros e ordenação.

    - **publication_date**: Filtra posts de um dia específico.
    - **sort_by**: Campo para ordenar os resultados (padrão: `likes`).
    - **order**: Direção da ordenação, `asc` ou `desc` (padrão: `desc`).
    """
    logger.debug(f"Listando posts com skip={skip}, limit={limit}")
    try:
        query = {}
        if publication_date:
            try:
                start_date = datetime.strptime(publication_date, "%Y-%m-%d")
                end_date = start_date.replace(hour=23, minute=59, second=59)
                query["publication_date"] = {"$gte": start_date, "$lte": end_date}
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de data inválido. Use AAAA-MM-DD.")
        total = await post_collection.count_documents(query)
        sort_direction = 1 if order == "asc" else -1
        posts = (
            await post_collection.find(query)
            .sort(sort_by, sort_direction)
            .skip(skip)
            .limit(limit)
            .to_list(length=limit)
        )
        for post in posts:
            post["_id"] = str(post["_id"])
        logger.info(f"{len(posts)} posts encontrados")
        return { "total": total, "skip": skip, "limit": limit, "data": posts }
    except Exception as e:
        logger.exception(f"Erro ao listar posts: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao listar posts")

@router.get("/{post_id}", response_model=PostOut, summary="Buscar um Post por ID")
async def get_post(post_id: str):
    """
    Busca e retorna um único post pelo seu ID.
    """
    try:
        post = await post_collection.find_one({"_id": object_id(post_id)})
        if not post:
            logger.warning(f"Post com ID {post_id} não encontrado.")
            raise HTTPException(status_code=404, detail="Post não encontrado")
        post["_id"] = str(post["_id"])
        return post
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao buscar post {post_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar post")

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deletar um Post")
async def delete_post(post_id: str):
    """
    Deleta um post e todos os seus dados associados (comentários e tags).
    """
    oid = object_id(post_id)
    if not await post_collection.find_one({"_id": oid}):
        raise HTTPException(status_code=404, detail="Post não encontrado")
    await comment_collection.delete_many({"post_id": post_id})
    await post_tag_collection.delete_many({"post_id": post_id})
    await post_collection.delete_one({"_id": oid})
    logger.info(f"Post ID {post_id} e seus dados associados foram deletados.")
    return

@router.get("/search/by_title", response_model=List[PostOut], summary="Buscar Posts por Título")
async def get_posts_by_title(title: str = Query(..., min_length=3)):
    """
    Busca posts por texto parcial no título (case-insensitive).
    """
    logger.debug(f"Buscando posts com título contendo '{title}'")
    try:
        posts = await post_collection.find(
            {"title": {"$regex": title, "$options": "i"}}
        ).to_list(length=None)
        for post in posts:
            post["_id"] = str(post["_id"])
        return posts
    except Exception as e:
        logger.exception(f"Erro ao buscar posts por título: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar posts por título")

@router.get("/filter/by_tag/{tag_id}", response_model=List[PostOut], summary="Filtrar Posts por Tag")
async def get_posts_by_tag(tag_id: str):
    """
    Retorna uma lista de todos os posts que foram associados a uma tag específica.
    """
    logger.debug(f"Buscando posts com a tag {tag_id}")
    try:
        if not await tag_collection.find_one({"_id": object_id(tag_id)}):
            raise HTTPException(status_code=404, detail="Tag não encontrada")
        posts = await post_collection.find({"tags_id": tag_id}).to_list(length=None)
        for post in posts:
            post["_id"] = str(post["_id"])
        return posts
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao buscar posts por tag: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar posts por tag")
        
@router.get("/{post_id}/full_details", response_model=Dict[str, Any], summary="Buscar Detalhes Completos de um Post")
async def get_post_full_details(post_id: str):
    """
    **Consulta Complexa 1:** Busca um post e agrega todas as informações
    relacionadas a ele de outras coleções (categoria, tags e comentários).
    """
    logger.debug(f"Buscando perfil completo do post {post_id}")
    try:
        post = await post_collection.find_one({"_id": object_id(post_id)})
        if not post:
            raise HTTPException(status_code=404, detail="Post não encontrado")
        post["_id"] = str(post["_id"])
        category = None
        if post.get("category_id"):
            category = await category_collection.find_one({"_id": object_id(post["category_id"])})
            if category:
                category["_id"] = str(category["_id"])
        tags = []
        if post.get("tags_id"):
            tag_oids = [object_id(tid) for tid in post["tags_id"]]
            tags = await tag_collection.find({"_id": {"$in": tag_oids}}).to_list(length=None)
            for tag in tags:
                tag["_id"] = str(tag["_id"])
        comments = await comment_collection.find({"post_id": post_id}).to_list(length=None)
        for comment in comments:
            comment["_id"] = str(comment["_id"])
        full_details = {
            "post": post,
            "category": category,
            "tags": tags,
            "comments": comments
        }
        logger.info(f"Detalhes completos do post {post_id} recuperados.")
        return full_details
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao buscar detalhes do post {post_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar detalhes do post")