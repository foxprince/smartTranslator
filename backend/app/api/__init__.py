from fastapi import APIRouter

from app.api import translation, document

api_router = APIRouter()

# 包含翻译相关路由
api_router.include_router(translation.router, prefix="/translation", tags=["翻译"])

# 包含文档处理路由
api_router.include_router(document.router, prefix="/document", tags=["文档处理"])
