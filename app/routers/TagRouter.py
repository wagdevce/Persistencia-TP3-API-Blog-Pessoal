# app/routers/TagRouter.py

from fastapi import APIRouter, HTTPException, Query, status
from typing import List

# Importando nossos novos modelos da camada de dados
from app.models import TagOut, TagCreate, PaginatedTagResponse

# Precisaremos definir 'tag_collection' no nosso arquivo de DB depois
from app.core.db import tag_collection 
from ..logs.logger import logger
from .utils import object_id # Importando a função utilitária

router = APIRouter(prefix="/tags", tags=["Tags"])


# Endpoint para criar uma nova Tag
@router.post("/", response_model=TagOut, status_code=status.HTTP_201_CREATED)
async def create_tag(tag: TagCreate):
    logger.debug(f"Tentando criar tag: {tag}")
    try:
        tag_dict = tag.model_dump()
        result = await tag_collection.insert_one(tag_dict)
        created = await tag_collection.find_one({"_id": result.inserted_id})
        
        created["_id"] = str(created["_id"])
        logger.info(f"Tag criada com sucesso: {created}")
        return created
    except Exception as e:
        logger.exception(f"Erro ao criar tag: {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar tag")


# Endpoint para listar todas as Tags com paginação
@router.get("/", response_model=PaginatedTagResponse)
async def list_tags(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
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

@router.get("/count", response_model=dict)
async def count_tags():
    try:
        count = await tag_collection.count_documents({})
        logger.info(f"Total de tags: {count}")
        return {"total": count}
    except Exception as e:
        logger.exception("Erro ao contar tags: " + str(e))
        raise HTTPException(status_code=500, detail="Erro interno ao contar tags")    

# Endpoint para buscar uma Tag pelo ID
@router.get("/{tag_id}", response_model=TagOut)
async def get_tag(tag_id: str):
    logger.debug(f"Buscando tag por ID {tag_id}")
    try:
        oid = object_id(tag_id) # Usando a função utilitária para validar o ID
        tag = await tag_collection.find_one({"_id": oid})
        
        if not tag:
            logger.warning(f"Tag com ID {tag_id} não encontrada.")
            raise HTTPException(status_code=404, detail="Tag não encontrada")

        tag["_id"] = str(tag["_id"])
        logger.info(f"Tag recuperada com sucesso: {tag}")
        return tag
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao buscar tag ID {tag_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar tag")


# Endpoint para deletar uma Tag
@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: str):
    logger.debug(f"Tentando deletar tag ID {tag_id}")
    try:
        oid = object_id(tag_id)
        
        # Nota: Lógica simplificada. Em uma versão futura, precisaríamos também
        # deletar as associações em 'PostTag' que usam este tag_id.
        
        result_delete = await tag_collection.delete_one({"_id": oid})
        
        if result_delete.deleted_count == 0:
            logger.warning(f"Tag com ID {tag_id} não encontrada para deleção.")
            raise HTTPException(status_code=404, detail="Tag não encontrada")

        logger.info(f"Tag ID {tag_id} deletada com sucesso.")
        return # Retorna uma resposta vazia com status 204

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao deletar tag ID {tag_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao deletar tag")

