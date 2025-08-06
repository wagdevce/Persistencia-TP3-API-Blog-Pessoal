# app/routers/__init__.py

from .CategoryRouter import router as CategoryRouter
from .PostRouter import router as PostRouter
from .TagRouter import router as TagRouter
from .CommentRouter import router as CommentRouter
from .PostTagRouter import router as PostTagRouter
from .DashboardRouter import router as DashboardRouter

__all__ = [
    "CategoryRouter",
    "PostRouter",
    "TagRouter",
    "CommentRouter",
    "PostTagRouter",
    "DashboardRouter",
]