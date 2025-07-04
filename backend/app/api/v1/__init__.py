"""
API v1 路由配置
"""
from fastapi import APIRouter
from .endpoints import documents

api_router = APIRouter()

# 注册文档处理路由
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)
