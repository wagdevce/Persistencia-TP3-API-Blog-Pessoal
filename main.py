
import uvicorn
from fastapi import FastAPI
from pymongo import ASCENDING, DESCENDING
from app.core.db import (
    post_collection,
    category_collection,
    tag_collection,
    comment_collection,
)

# Importando nossos routers do sistema de Blog
from app.routers.CategoryRouter import router as CategoryRouter
from app.routers.PostRouter import router as PostRouter
from app.routers.TagRouter import router as TagRouter
from app.routers.CommentRouter import router as CommentRouter
from app.routers.PostTagRouter import router as PostTagRouter
from app.routers.DashboardRouter import router as DashboardRouter
from app.routers.UserRouter import router as UserRouter


app = FastAPI(
    title="Blog API",
    description="API para um sistema de gerenciamento de conteúdo de um blog.",
    version="1.2.3"
)

# --- INÍCIO DO CÓDIGO PARA CRIAR ÍNDICES ---
@app.on_event("startup")
async def create_indexes():
    """
    Esta função é executada na inicialização do app e garante
    que os índices essenciais existam no MongoDB.
    """
    # Índice para buscar comentários por post rapidamente
    await comment_collection.create_index([("post_id", ASCENDING)])
    
    # Índices para buscar posts por categoria e tags
    await post_collection.create_index([("category_id", ASCENDING)])
    await post_collection.create_index([("tags_id", ASCENDING)]) # MongoDB cria um "multikey index" para arrays

    # Índice para ordenar posts por data de publicação
    await post_collection.create_index([("publication_date", DESCENDING)])



# Incluindo os novos routers na aplicação FastAPI
app.include_router(UserRouter)
app.include_router(CategoryRouter)
app.include_router(PostRouter)
app.include_router(TagRouter)
app.include_router(CommentRouter)
app.include_router(PostTagRouter)
app.include_router(DashboardRouter)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)