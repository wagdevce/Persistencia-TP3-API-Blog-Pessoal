# app/routers/DashboardRouter.py

from fastapi import APIRouter, HTTPException
from typing import Any, Dict

from ..core.db import post_collection, comment_collection, category_collection
from ..logs.logger import logger

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=Dict[str, Any])
async def get_dashboard_stats():
    logger.debug("Calculando estatísticas do dashboard")
    try:
        # --- INÍCIO DA VERSÃO CORRIGIDA DO PIPELINE ---
        top_category_pipeline = [
            {"$match": {"category_id": {"$ne": None}}},
            {"$group": {"_id": "$category_id", "post_count": {"$sum": 1}}},
            {"$sort": {"post_count": -1}},
            {"$limit": 1},
            # ETAPA ADICIONAL: Converte o campo _id (que é uma string) para um ObjectId
            {
                "$addFields": {
                    "category_oid": { "$toObjectId": "$_id" }
                }
            },
            # O lookup agora usa o novo campo convertido para a junção
            {
                "$lookup": {
                    "from": "categories",
                    "localField": "category_oid", # <-- MUDANÇA AQUI
                    "foreignField": "_id",
                    "as": "category_details"
                }
            },
            {"$unwind": "$category_details"},
            {"$project": {"_id": 0, "category_name": "$category_details.name", "post_count": 1}}
        ]
        # --- FIM DA VERSÃO CORRIGIDA DO PIPELINE ---

        # ... (o resto da função continua igual) ...
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