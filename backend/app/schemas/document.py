"""
文档处理相关的Pydantic模式
"""
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import UUID

from app.schemas.translation import LanguageCode, TranslationProvider


class DocumentStatus(str, Enum):
    """文档状态枚举"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


class ProcessingStatus(str, Enum):
    """处理状态枚举"""
    PENDING = "pending"
    TEXT_EXTRACTING = "text_extracting"
    TEXT_EXTRACTED = "text_extracted"
    TRANSLATING = "translating"
    TRANSLATED = "translated"
    FAILED = "failed"


class JobType(str, Enum):
    """任务类型枚举"""
    EXTRACT = "extract"
    TRANSLATE = "translate"
    OCR = "ocr"
    CONVERT = "convert"


class JobStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ShareType(str, Enum):
    """分享类型枚举"""
    PUBLIC = "public"
    PRIVATE = "private"
    PASSWORD = "password"


# 请求模式
class DocumentUploadRequest(BaseModel):
    """文档上传请求"""
    filename: str = Field(..., description="文件名")
    project_id: Optional[str] = Field(None, description="项目ID")
    tags: Optional[List[str]] = Field(None, description="文档标签")
    metadata: Optional[Dict[str, Any]] = Field(None, description="文档元数据")
    
    @validator('filename')
    def validate_filename(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('文件名不能为空')
        if len(v) > 255:
            raise ValueError('文件名长度不能超过255个字符')
        return v.strip()


class DocumentTranslationRequest(BaseModel):
    """文档翻译请求"""
    document_id: UUID = Field(..., description="文档ID")
    source_language: LanguageCode = Field(..., description="源语言")
    target_language: LanguageCode = Field(..., description="目标语言")
    provider: TranslationProvider = Field(TranslationProvider.GOOGLE, description="翻译提供商")
    chunk_size: int = Field(1000, ge=100, le=5000, description="文本分块大小")
    preserve_formatting: bool = Field(True, description="是否保持格式")
    
    @validator('source_language', 'target_language')
    def validate_languages(cls, v):
        if not v:
            raise ValueError('语言代码不能为空')
        return v
    
    @validator('target_language')
    def validate_different_languages(cls, v, values):
        if 'source_language' in values and v == values['source_language']:
            raise ValueError('源语言和目标语言不能相同')
        return v


class DocumentProcessingJobRequest(BaseModel):
    """文档处理任务请求"""
    document_id: UUID = Field(..., description="文档ID")
    job_type: JobType = Field(..., description="任务类型")
    config: Optional[Dict[str, Any]] = Field(None, description="任务配置")
    priority: int = Field(0, ge=0, le=10, description="任务优先级")


class DocumentShareRequest(BaseModel):
    """文档分享请求"""
    document_id: UUID = Field(..., description="文档ID")
    share_type: ShareType = Field(..., description="分享类型")
    password: Optional[str] = Field(None, description="访问密码")
    permissions: Dict[str, bool] = Field(..., description="权限配置")
    max_downloads: Optional[int] = Field(None, ge=1, description="最大下载次数")
    expires_hours: Optional[int] = Field(None, ge=1, le=8760, description="过期小时数")
    
    @validator('password')
    def validate_password(cls, v, values):
        if values.get('share_type') == ShareType.PASSWORD and not v:
            raise ValueError('密码分享类型必须设置密码')
        return v


class DocumentQueryRequest(BaseModel):
    """文档查询请求"""
    project_id: Optional[str] = Field(None, description="项目ID")
    status: Optional[DocumentStatus] = Field(None, description="文档状态")
    processing_status: Optional[ProcessingStatus] = Field(None, description="处理状态")
    file_type: Optional[str] = Field(None, description="文件类型")
    tags: Optional[List[str]] = Field(None, description="标签过滤")
    search_text: Optional[str] = Field(None, description="搜索文本")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页大小")
    sort_by: str = Field("created_at", description="排序字段")
    sort_order: str = Field("desc", regex="^(asc|desc)$", description="排序顺序")


# 响应模式
class DocumentInfo(BaseModel):
    """文档信息"""
    id: UUID
    original_filename: str
    file_size: int
    file_type: str
    mime_type: str
    user_id: str
    project_id: Optional[str]
    status: DocumentStatus
    processing_status: ProcessingStatus
    text_length: Optional[int]
    quality_score: Optional[float]
    translation_cost: Optional[float]
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    upload_time: datetime
    extraction_time: Optional[datetime]
    translation_time: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    document_id: UUID
    filename: str
    file_size: int
    file_type: str
    status: DocumentStatus
    upload_time: datetime
    message: str = "文档上传成功"


class DocumentTextExtractionResponse(BaseModel):
    """文本提取响应"""
    document_id: UUID
    extracted_text: str
    text_length: int
    extraction_method: str
    processing_time: float
    extraction_time: datetime
    message: str = "文本提取成功"


class DocumentTranslationResponse(BaseModel):
    """文档翻译响应"""
    document_id: UUID
    source_language: str
    target_language: str
    provider: str
    translated_text: str
    translated_file_path: Optional[str]
    translation_stats: Dict[str, Any]
    processing_time: float
    translation_time: datetime
    message: str = "文档翻译成功"


class DocumentProcessingJobInfo(BaseModel):
    """文档处理任务信息"""
    id: UUID
    document_id: UUID
    user_id: str
    job_type: JobType
    status: JobStatus
    progress: int
    config: Optional[Dict[str, Any]]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    processing_time: Optional[float]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentShareInfo(BaseModel):
    """文档分享信息"""
    id: UUID
    document_id: UUID
    share_token: str
    share_type: ShareType
    permissions: Dict[str, bool]
    max_downloads: Optional[int]
    download_count: int
    expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    last_accessed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """文档列表响应"""
    documents: List[DocumentInfo]
    total: int
    page: int
    page_size: int
    total_pages: int


class DocumentStatsResponse(BaseModel):
    """文档统计响应"""
    total_documents: int
    total_size_bytes: int
    documents_by_status: Dict[str, int]
    documents_by_type: Dict[str, int]
    processing_stats: Dict[str, Any]
    translation_stats: Dict[str, Any]
    recent_uploads: int
    storage_usage: Dict[str, Any]


class SupportedFormatsResponse(BaseModel):
    """支持格式响应"""
    formats: Dict[str, str]
    categories: Dict[str, List[str]]
    total_formats: int
    description: str = "支持的文档格式列表"


# 批量操作模式
class BatchDocumentRequest(BaseModel):
    """批量文档操作请求"""
    document_ids: List[UUID] = Field(..., min_items=1, max_items=100, description="文档ID列表")
    operation: str = Field(..., description="操作类型")
    parameters: Optional[Dict[str, Any]] = Field(None, description="操作参数")


class BatchTranslationRequest(BaseModel):
    """批量翻译请求"""
    document_ids: List[UUID] = Field(..., min_items=1, max_items=50, description="文档ID列表")
    source_language: LanguageCode = Field(..., description="源语言")
    target_language: LanguageCode = Field(..., description="目标语言")
    provider: TranslationProvider = Field(TranslationProvider.GOOGLE, description="翻译提供商")
    chunk_size: int = Field(1000, ge=100, le=5000, description="文本分块大小")


class BatchOperationResponse(BaseModel):
    """批量操作响应"""
    total_count: int
    success_count: int
    failed_count: int
    results: List[Dict[str, Any]]
    errors: List[Dict[str, str]]
    processing_time: float
    message: str


# 模板相关模式
class DocumentTemplateRequest(BaseModel):
    """文档模板请求"""
    name: str = Field(..., max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    category: str = Field(..., max_length=50, description="模板分类")
    file_types: List[str] = Field(..., min_items=1, description="支持的文件类型")
    processing_config: Dict[str, Any] = Field(..., description="处理配置")
    translation_config: Optional[Dict[str, Any]] = Field(None, description="翻译配置")
    is_public: bool = Field(False, description="是否公开")


class DocumentTemplateInfo(BaseModel):
    """文档模板信息"""
    id: UUID
    name: str
    description: Optional[str]
    category: str
    file_types: List[str]
    processing_config: Dict[str, Any]
    translation_config: Optional[Dict[str, Any]]
    created_by: str
    is_public: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
