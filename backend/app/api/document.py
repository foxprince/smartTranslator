"""
文档处理API路由
"""
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from uuid import UUID
import logging
import io
import zipfile
from pathlib import Path

from app.services.document_processor import document_processor
from app.schemas.document import (
    DocumentUploadRequest, DocumentUploadResponse,
    DocumentTranslationRequest, DocumentTranslationResponse,
    DocumentTextExtractionResponse, DocumentInfo,
    DocumentQueryRequest, DocumentListResponse,
    DocumentStatsResponse, SupportedFormatsResponse,
    BatchTranslationRequest, BatchOperationResponse,
    DocumentProcessingJobRequest, DocumentProcessingJobInfo,
    DocumentShareRequest, DocumentShareInfo
)
from app.schemas.translation import LanguageCode, TranslationProvider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/document", tags=["文档处理"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    project_id: Optional[str] = None,
    user_id: str = "default_user"  # 实际应用中从认证中获取
):
    """
    上传文档
    
    支持多种文档格式：
    - 文本文档: .txt, .md, .rtf
    - Office文档: .doc, .docx, .xls, .xlsx, .ppt, .pptx
    - PDF文档: .pdf
    - 网页文档: .html, .htm, .xml
    - 数据格式: .json, .csv
    - 图像文档: .jpg, .jpeg, .png, .bmp, .tiff (OCR)
    """
    try:
        # 读取文件内容
        file_content = await file.read()
        
        # 上传文档
        document_info = await document_processor.upload_document(
            file_content=file_content,
            filename=file.filename,
            user_id=user_id,
            project_id=project_id
        )
        
        # 后台任务：自动提取文本
        background_tasks.add_task(
            auto_extract_text,
            document_info
        )
        
        return DocumentUploadResponse(
            document_id=document_info["id"],
            filename=document_info["original_filename"],
            file_size=document_info["file_size"],
            file_type=document_info["file_type"],
            status=document_info["status"],
            upload_time=document_info["upload_time"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"文档上传失败: {e}")
        raise HTTPException(status_code=500, detail="文档上传失败")


@router.post("/extract-text/{document_id}", response_model=DocumentTextExtractionResponse)
async def extract_text(
    document_id: UUID,
    user_id: str = "default_user"
):
    """提取文档文本内容"""
    try:
        # 获取文档信息
        document_info = await document_processor.get_document_info(str(document_id))
        if not document_info:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 检查权限
        if document_info["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="无权限访问此文档")
        
        # 提取文本
        result = await document_processor.extract_text_from_document(document_info)
        
        return DocumentTextExtractionResponse(
            document_id=document_id,
            extracted_text=result["extracted_text"],
            text_length=result["text_length"],
            extraction_method=result.get("extraction_method", "auto"),
            processing_time=0.0,  # 实际应该记录处理时间
            extraction_time=result["extraction_time"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文本提取失败: {e}")
        raise HTTPException(status_code=500, detail="文本提取失败")


@router.post("/translate", response_model=DocumentTranslationResponse)
async def translate_document(
    request: DocumentTranslationRequest,
    background_tasks: BackgroundTasks,
    user_id: str = "default_user"
):
    """翻译文档"""
    try:
        # 获取文档信息
        document_info = await document_processor.get_document_info(str(request.document_id))
        if not document_info:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 检查权限
        if document_info["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="无权限访问此文档")
        
        # 检查是否已提取文本
        if not document_info.get("extracted_text"):
            # 先提取文本
            document_info = await document_processor.extract_text_from_document(document_info)
        
        # 执行翻译
        result = await document_processor.translate_document(
            document_info=document_info,
            source_language=request.source_language,
            target_language=request.target_language,
            provider=request.provider,
            chunk_size=request.chunk_size
        )
        
        translation_result = result["translation_result"]
        
        return DocumentTranslationResponse(
            document_id=request.document_id,
            source_language=translation_result["source_language"],
            target_language=translation_result["target_language"],
            provider=translation_result["provider"],
            translated_text=translation_result["translated_text"],
            translated_file_path=translation_result.get("translated_file_path"),
            translation_stats=translation_result["translation_stats"],
            processing_time=translation_result["translation_stats"]["processing_time"],
            translation_time=result["translation_time"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文档翻译失败: {e}")
        raise HTTPException(status_code=500, detail="文档翻译失败")


@router.post("/batch-translate", response_model=BatchOperationResponse)
async def batch_translate_documents(
    request: BatchTranslationRequest,
    background_tasks: BackgroundTasks,
    user_id: str = "default_user"
):
    """批量翻译文档"""
    try:
        results = []
        errors = []
        success_count = 0
        
        for document_id in request.document_ids:
            try:
                # 创建单个翻译请求
                translation_request = DocumentTranslationRequest(
                    document_id=document_id,
                    source_language=request.source_language,
                    target_language=request.target_language,
                    provider=request.provider,
                    chunk_size=request.chunk_size
                )
                
                # 添加到后台任务
                background_tasks.add_task(
                    process_single_translation,
                    translation_request,
                    user_id
                )
                
                results.append({
                    "document_id": str(document_id),
                    "status": "queued",
                    "message": "已加入翻译队列"
                })
                success_count += 1
                
            except Exception as e:
                errors.append({
                    "document_id": str(document_id),
                    "error": str(e)
                })
        
        return BatchOperationResponse(
            total_count=len(request.document_ids),
            success_count=success_count,
            failed_count=len(errors),
            results=results,
            errors=errors,
            processing_time=0.0,
            message=f"批量翻译任务已创建，成功 {success_count}/{len(request.document_ids)} 个"
        )
        
    except Exception as e:
        logger.error(f"批量翻译失败: {e}")
        raise HTTPException(status_code=500, detail="批量翻译失败")


@router.get("/list", response_model=DocumentListResponse)
async def list_documents(
    project_id: Optional[str] = Query(None, description="项目ID"),
    status: Optional[str] = Query(None, description="文档状态"),
    file_type: Optional[str] = Query(None, description="文件类型"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    user_id: str = "default_user"
):
    """获取文档列表"""
    try:
        documents = await document_processor.list_documents(
            user_id=user_id,
            project_id=project_id,
            status=status,
            limit=page_size,
            offset=(page - 1) * page_size
        )
        
        # 计算总数（实际应该从数据库查询）
        total = len(documents)  # 简化实现
        total_pages = (total + page_size - 1) // page_size
        
        return DocumentListResponse(
            documents=[DocumentInfo(**doc) for doc in documents],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"获取文档列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取文档列表失败")


@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document_info(
    document_id: UUID,
    user_id: str = "default_user"
):
    """获取文档详细信息"""
    try:
        document_info = await document_processor.get_document_info(str(document_id))
        if not document_info:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 检查权限
        if document_info["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="无权限访问此文档")
        
        return DocumentInfo(**document_info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文档信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取文档信息失败")


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    file_type: str = Query("original", description="文件类型: original, translated, text"),
    user_id: str = "default_user"
):
    """下载文档"""
    try:
        document_info = await document_processor.get_document_info(str(document_id))
        if not document_info:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 检查权限
        if document_info["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="无权限访问此文档")
        
        if file_type == "original":
            file_path = Path(document_info["file_path"])
            filename = document_info["original_filename"]
        elif file_type == "translated":
            translation_result = document_info.get("translation_result")
            if not translation_result or not translation_result.get("translated_file_path"):
                raise HTTPException(status_code=404, detail="翻译文件不存在")
            file_path = Path(translation_result["translated_file_path"])
            filename = file_path.name
        elif file_type == "text":
            # 返回提取的文本内容
            extracted_text = document_info.get("extracted_text", "")
            if not extracted_text:
                raise HTTPException(status_code=404, detail="文本内容不存在")
            
            filename = f"{Path(document_info['original_filename']).stem}_extracted.txt"
            return StreamingResponse(
                io.BytesIO(extracted_text.encode('utf-8')),
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:
            raise HTTPException(status_code=400, detail="不支持的文件类型")
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载文档失败: {e}")
        raise HTTPException(status_code=500, detail="下载文档失败")


@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    user_id: str = "default_user"
):
    """删除文档"""
    try:
        success = await document_processor.delete_document(str(document_id), user_id)
        if not success:
            raise HTTPException(status_code=404, detail="文档不存在或无权限删除")
        
        return {"message": "文档删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文档失败: {e}")
        raise HTTPException(status_code=500, detail="删除文档失败")


@router.get("/formats/supported", response_model=SupportedFormatsResponse)
async def get_supported_formats():
    """获取支持的文档格式"""
    try:
        formats = document_processor.get_supported_formats()
        
        # 按类别分组
        categories = {
            "文本文档": [".txt", ".md", ".rtf"],
            "Office文档": [".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"],
            "PDF文档": [".pdf"],
            "网页文档": [".html", ".htm", ".xml"],
            "数据格式": [".json", ".csv"],
            "图像文档": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"]
        }
        
        return SupportedFormatsResponse(
            formats=formats,
            categories=categories,
            total_formats=len(formats)
        )
        
    except Exception as e:
        logger.error(f"获取支持格式失败: {e}")
        raise HTTPException(status_code=500, detail="获取支持格式失败")


@router.get("/stats/processing", response_model=DocumentStatsResponse)
async def get_processing_stats(
    user_id: str = "default_user"
):
    """获取文档处理统计信息"""
    try:
        stats = await document_processor.get_processing_stats()
        
        return DocumentStatsResponse(
            total_documents=stats.get("total_files", 0),
            total_size_bytes=stats.get("total_size_bytes", 0),
            documents_by_status={"uploaded": stats.get("total_files", 0)},
            documents_by_type={},
            processing_stats=stats,
            translation_stats={},
            recent_uploads=0,
            storage_usage={
                "used_bytes": stats.get("total_size_bytes", 0),
                "processed_bytes": stats.get("processed_size_bytes", 0)
            }
        )
        
    except Exception as e:
        logger.error(f"获取处理统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取处理统计失败")


# 后台任务函数
async def auto_extract_text(document_info: dict):
    """自动提取文本的后台任务"""
    try:
        await document_processor.extract_text_from_document(document_info)
        logger.info(f"自动文本提取完成: {document_info['id']}")
    except Exception as e:
        logger.error(f"自动文本提取失败: {e}")


async def process_single_translation(request: DocumentTranslationRequest, user_id: str):
    """处理单个翻译任务的后台函数"""
    try:
        document_info = await document_processor.get_document_info(str(request.document_id))
        if not document_info or document_info["user_id"] != user_id:
            return
        
        if not document_info.get("extracted_text"):
            document_info = await document_processor.extract_text_from_document(document_info)
        
        await document_processor.translate_document(
            document_info=document_info,
            source_language=request.source_language,
            target_language=request.target_language,
            provider=request.provider,
            chunk_size=request.chunk_size
        )
        
        logger.info(f"后台翻译完成: {request.document_id}")
        
    except Exception as e:
        logger.error(f"后台翻译失败: {e}")


# 批量下载
@router.post("/batch-download")
async def batch_download_documents(
    document_ids: List[UUID],
    file_type: str = Query("original", description="文件类型"),
    user_id: str = "default_user"
):
    """批量下载文档"""
    try:
        if len(document_ids) > 50:
            raise HTTPException(status_code=400, detail="批量下载数量不能超过50个")
        
        # 创建ZIP文件
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for document_id in document_ids:
                try:
                    document_info = await document_processor.get_document_info(str(document_id))
                    if not document_info or document_info["user_id"] != user_id:
                        continue
                    
                    if file_type == "original":
                        file_path = Path(document_info["file_path"])
                        filename = document_info["original_filename"]
                    elif file_type == "translated":
                        translation_result = document_info.get("translation_result")
                        if not translation_result or not translation_result.get("translated_file_path"):
                            continue
                        file_path = Path(translation_result["translated_file_path"])
                        filename = file_path.name
                    else:
                        continue
                    
                    if file_path.exists():
                        zip_file.write(file_path, filename)
                        
                except Exception as e:
                    logger.warning(f"添加文件到ZIP失败: {document_id}, {e}")
                    continue
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.read()),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=documents.zip"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量下载失败: {e}")
        raise HTTPException(status_code=500, detail="批量下载失败")
