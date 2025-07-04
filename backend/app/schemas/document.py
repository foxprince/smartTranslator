"""
文档处理相关的Pydantic模式定义
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class TextStats(BaseModel):
    """文本统计信息"""
    total_lines: int = Field(..., description="总行数")
    empty_lines: int = Field(..., description="空行数")
    content_lines: int = Field(..., description="内容行数")
    short_lines: int = Field(..., description="短行数(<10字符)")
    long_lines: int = Field(..., description="长行数(>200字符)")
    average_line_length: float = Field(..., description="平均行长度")
    encoding: str = Field(..., description="文件编码")


class TextIssue(BaseModel):
    """文本问题"""
    line_number: int = Field(..., description="问题行号")
    issue_type: str = Field(..., description="问题类型")
    description: str = Field(..., description="问题描述")
    suggestion: Optional[str] = Field(None, description="修复建议")


class ProcessingReport(BaseModel):
    """处理报告"""
    original_stats: TextStats
    cleaned_stats: TextStats
    issues_found: List[TextIssue]
    processing_time: float = Field(..., description="处理耗时(秒)")
    changes_made: List[str] = Field(..., description="执行的修改操作")


class DocumentPreprocessRequest(BaseModel):
    """文档预处理请求"""
    file_content: str = Field(..., description="文件内容")
    filename: str = Field(..., description="文件名")
    encoding: Optional[str] = Field(None, description="指定编码，为空则自动检测")


class ProcessingResult(BaseModel):
    """处理结果"""
    cleaned_content: str = Field(..., description="清理后的内容")
    processing_report: ProcessingReport = Field(..., description="处理报告")


class DocumentPreprocessResponse(BaseModel):
    """文档预处理响应"""
    success: bool = Field(..., description="处理是否成功")
    data: Optional[ProcessingResult] = Field(None, description="处理结果")
    message: str = Field(..., description="响应消息")
    code: int = Field(..., description="响应代码")
