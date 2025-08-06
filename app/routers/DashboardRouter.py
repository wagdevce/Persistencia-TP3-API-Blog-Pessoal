
from fastapi import APIRouter, HTTPException
from typing import Any, Dict

from ..core.db import post_collection, comment_collection, category_collection
from ..logs.logger import logger

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=Dict[str, Any], summary="Obter Estatísticas Gerais do Blog")
async def get_dashboard_stats():
    """
    **Consulta Complexa 2 (Agregação):** Retorna uma visão geral com estatísticas
    consolidadas de todo o blog.

    Esta consulta utiliza o Pipeline de Agregação do MongoDB para calcular de
    forma eficiente os seguintes dados:
    - Número total de posts.
    - Número total de comentários.
    - A categoria mais popular (com base na contagem de posts).
    """
    logger.debug("Calculando estatísticas do dashboard")
    try:
        top_category_pipeline = [
            {"$match": {"category_id": {"$ne": None}}},
            {"$group": {"_id": "$category_id", "post_count": {"$sum": 1}}},
            {"$sort": {"post_count": -1}},
            {"$limit": 1},
            {
                "$addFields": {
                    "category_oid": { "$toObjectId": "$_id" }
                }
            },
            {
                "$lookup": {
                    "from": "categories",
                    "localField": "category_oid",
                    "foreignField": "_id",
                    "as": "category_details"
                }
            },
            {"$unwind": "$category_details"},
            {"$project": {"_id": 0, "category_name": "$category_details.name", "post_count": 1}}
        ]

        total_posts = await post_collection.count_documents({})
        total_comments = await comment_collection.count_documents({})
        
        top_category_cursor = post_collection.aggregate(top_category_pipeline)
        top_category_list = await top_category_cursor.to_list(length=1)
        top_category = top_category_list[0] if top_category_list else None

        stats = {
            "total_posts": total_posts,
            "total_comments": total_comments,
            "most_popular_category": top_category
        }
        
        logger.info(f"Estatísticas geradas com sucesso: {stats}")
        return stats

    except Exception as e:
        logger.exception(f"Erro ao gerar estatísticas do dashboard: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao gerar estatísticas")