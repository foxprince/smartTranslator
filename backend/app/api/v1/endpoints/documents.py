"""
文档处理API端点
"""
from fastapi import APIRouter, HTTPException, status
from ....schemas.document import (
    DocumentPreprocessRequest,
    DocumentPreprocessResponse,
    ProcessingResult
)
from ....services.document_processor import DocumentProcessor, DocumentProcessingError

router = APIRouter()
document_processor = DocumentProcessor()


@router.post(
    "/preprocess",
    response_model=DocumentPreprocessResponse,
    summary="文档预处理",
    description="对上传的txt文档进行格式检查、清理和标准化处理"
)
async def preprocess_document(request: DocumentPreprocessRequest):
    """
    文档预处理接口
    
    - **file_content**: 文件内容
    - **filename**: 文件名（必须是.txt格式）
    - **encoding**: 文件编码（可选，自动检测）
    
    返回处理后的清洁文本和详细的处理报告
    """
    try:
        # 处理文档
        result = document_processor.preprocess_document(request)
        
        return DocumentPreprocessResponse(
            success=True,
            data=result,
            message="文档预处理成功",
            code=200
        )
    
    except DocumentProcessingError as e:
        raise HTTPException(
            status_code=e.code,
            detail={
                "success": False,
                "error": e.message,
                "message": "文档预处理失败",
                "code": e.code
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": str(e),
                "message": "服务器内部错误",
                "code": 500
            }
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查文档处理服务状态"
)
async def health_check():
    """
    健康检查接口
    """
    return {
        "success": True,
        "message": "文档处理服务运行正常",
        "service": "document-processor",
        "version": "1.0.0"
    }
