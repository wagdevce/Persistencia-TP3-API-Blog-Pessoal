# app/routers/utils.py

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from ..logs.logger import logger

def object_id(id_str: str) -> ObjectId:
    """
    Função utilitária para validar e converter uma string para ObjectId.
    Levanta uma exceção HTTPException 400 se o ID for inválido.
    """
    try:
        return ObjectId(id_str)
    except InvalidId:
        logger.warning(f"ID inválido fornecido: {id_str}")
        raise HTTPException(status_code=400, detail="ID inválido")