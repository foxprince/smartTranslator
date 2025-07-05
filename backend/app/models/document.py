"""
文档相关数据模型
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Document(Base):
    """文档模型"""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 基本信息
    original_filename = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(500), nullable=False, comment="文件存储路径")
    file_size = Column(Integer, nullable=False, comment="文件大小（字节）")
    file_type = Column(String(10), nullable=False, comment="文件类型扩展名")
    mime_type = Column(String(100), nullable=False, comment="MIME类型")
    
    # 用户和项目信息
    user_id = Column(String(50), nullable=False, comment="上传用户ID")
    project_id = Column(String(50), nullable=True, comment="所属项目ID")
    
    # 处理状态
    status = Column(String(20), nullable=False, default="uploaded", comment="文档状态")
    processing_status = Column(String(30), nullable=False, default="pending", comment="处理状态")
    
    # 文本提取信息
    extracted_text = Column(Text, nullable=True, comment="提取的文本内容")
    text_length = Column(Integer, nullable=True, comment="文本长度")
    extraction_method = Column(String(50), nullable=True, comment="文本提取方法")
    
    # 翻译信息
    translation_config = Column(JSON, nullable=True, comment="翻译配置")
    translation_result = Column(JSON, nullable=True, comment="翻译结果")
    translated_file_path = Column(String(500), nullable=True, comment="翻译文件路径")
    
    # 质量和成本信息
    quality_score = Column(Float, nullable=True, comment="翻译质量评分")
    translation_cost = Column(Float, nullable=True, comment="翻译成本")
    
    # 元数据
    metadata = Column(JSON, nullable=True, comment="文档元数据")
    tags = Column(JSON, nullable=True, comment="文档标签")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    upload_time = Column(DateTime(timezone=True), server_default=func.now(), comment="上传时间")
    extraction_time = Column(DateTime(timezone=True), nullable=True, comment="文本提取时间")
    translation_time = Column(DateTime(timezone=True), nullable=True, comment="翻译完成时间")
    
    # 软删除
    is_deleted = Column(Boolean, default=False, comment="是否已删除")
    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="删除时间")

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.original_filename}, status={self.status})>"


class DocumentProcessingJob(Base):
    """文档处理任务模型"""
    __tablename__ = "document_processing_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联信息
    document_id = Column(UUID(as_uuid=True), nullable=False, comment="文档ID")
    user_id = Column(String(50), nullable=False, comment="用户ID")
    
    # 任务信息
    job_type = Column(String(30), nullable=False, comment="任务类型")  # extract, translate, ocr
    status = Column(String(20), nullable=False, default="pending", comment="任务状态")
    progress = Column(Integer, default=0, comment="处理进度（0-100）")
    
    # 配置参数
    config = Column(JSON, nullable=True, comment="任务配置参数")
    
    # 结果信息
    result = Column(JSON, nullable=True, comment="处理结果")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 性能指标
    processing_time = Column(Float, nullable=True, comment="处理耗时（秒）")
    memory_usage = Column(Integer, nullable=True, comment="内存使用（MB）")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    started_at = Column(DateTime(timezone=True), nullable=True, comment="开始时间")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")

    def __repr__(self):
        return f"<DocumentProcessingJob(id={self.id}, type={self.job_type}, status={self.status})>"


class DocumentTemplate(Base):
    """文档模板模型"""
    __tablename__ = "document_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 模板信息
    name = Column(String(100), nullable=False, comment="模板名称")
    description = Column(Text, nullable=True, comment="模板描述")
    category = Column(String(50), nullable=False, comment="模板分类")
    
    # 模板配置
    file_types = Column(JSON, nullable=False, comment="支持的文件类型")
    processing_config = Column(JSON, nullable=False, comment="处理配置")
    translation_config = Column(JSON, nullable=True, comment="翻译配置")
    
    # 用户信息
    created_by = Column(String(50), nullable=False, comment="创建者ID")
    is_public = Column(Boolean, default=False, comment="是否公开")
    
    # 使用统计
    usage_count = Column(Integer, default=0, comment="使用次数")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<DocumentTemplate(id={self.id}, name={self.name}, category={self.category})>"


class DocumentShare(Base):
    """文档分享模型"""
    __tablename__ = "document_shares"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 关联信息
    document_id = Column(UUID(as_uuid=True), nullable=False, comment="文档ID")
    owner_id = Column(String(50), nullable=False, comment="文档所有者ID")
    
    # 分享信息
    share_token = Column(String(100), nullable=False, unique=True, comment="分享令牌")
    share_type = Column(String(20), nullable=False, comment="分享类型")  # public, private, password
    password = Column(String(100), nullable=True, comment="访问密码")
    
    # 权限设置
    permissions = Column(JSON, nullable=False, comment="权限配置")
    
    # 访问限制
    max_downloads = Column(Integer, nullable=True, comment="最大下载次数")
    download_count = Column(Integer, default=0, comment="已下载次数")
    expires_at = Column(DateTime(timezone=True), nullable=True, comment="过期时间")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否激活")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    last_accessed_at = Column(DateTime(timezone=True), nullable=True, comment="最后访问时间")

    def __repr__(self):
        return f"<DocumentShare(id={self.id}, token={self.share_token}, type={self.share_type})>"
