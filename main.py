
import uvicorn
from fastapi import FastAPI
from pymongo import ASCENDING, DESCENDING
from app.core.db import (
    post_collection,
    category_collection,
    tag_collection,
    comment_collection,
)
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
    version="1.3.0"
)
@app.on_event("startup")
async def create_indexes():
    """
    Esta função é executada na inicialização do app e garante
    que os índices essenciais existam no MongoDB.
    """
    await comment_collection.create_index([("post_id", ASCENDING)])
    await post_collection.create_index([("category_id", ASCENDING)])
    await post_collection.create_index([("tags_id", ASCENDING)]) 
    await post_collection.create_index([("publication_date", DESCENDING)])

app.include_router(UserRouter)
app.include_router(CategoryRouter)
app.include_router(PostRouter)
app.include_router(TagRouter)
app.include_router(CommentRouter)
app.include_router(PostTagRouter)
app.include_router(DashboardRouter)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)