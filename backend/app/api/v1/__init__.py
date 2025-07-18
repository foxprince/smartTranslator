"""
API v1 路由配置
"""
from fastapi import APIRouter
from .endpoints import documents, collaboration, translation

api_router = APIRouter()

# 注册文档处理路由
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)

# 注册协作路由
api_router.include_router(
    collaboration.router,
    prefix="/collaboration",
    tags=["collaboration"]
)

# 注册翻译路由
api_router.include_router(
    translation.router,
    prefix="/translation",
    tags=["translation"]
)
