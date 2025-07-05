"""
翻译相关的Pydantic模式定义
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class TranslationProvider(str, Enum):
    """翻译服务提供商"""
    GOOGLE = "google"
    OPENAI = "openai"
    AZURE = "azure"


class LanguageCode(str, Enum):
    """语言代码"""
    ENGLISH = "en"
    CHINESE = "zh"
    CHINESE_SIMPLIFIED = "zh-CN"
    CHINESE_TRADITIONAL = "zh-TW"


class TranslationStatus(str, Enum):
    """翻译状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"


class QualityLevel(str, Enum):
    """质量等级"""
    EXCELLENT = "excellent"  # 0.9+
    GOOD = "good"           # 0.7-0.9
    FAIR = "fair"           # 0.5-0.7
    POOR = "poor"           # <0.5


class TranslationItem(BaseModel):
    """单个翻译项"""
    original_text: str = Field(..., description="原文")
    translated_text: str = Field(..., description="译文")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")
    provider: TranslationProvider = Field(..., description="翻译提供商")
    model_used: Optional[str] = Field(None, description="使用的模型")
    detected_language: Optional[str] = Field(None, description="检测到的源语言")
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="质量分数")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class QualityScore(BaseModel):
    """质量评分"""
    overall_score: float = Field(..., ge=0.0, le=1.0, description="综合评分")
    length_score: float = Field(..., ge=0.0, le=1.0, description="长度合理性评分")
    consistency_score: float = Field(..., ge=0.0, le=1.0, description="一致性评分")
    language_score: float = Field(..., ge=0.0, le=1.0, description="语言准确性评分")
    confidence_level: QualityLevel = Field(..., description="置信度等级")
    issues: List[str] = Field(default=[], description="发现的问题")


class TranslationRequest(BaseModel):
    """翻译请求"""
    texts: List[str] = Field(..., description="待翻译文本列表")
    source_language: LanguageCode = Field(default=LanguageCode.ENGLISH, description="源语言")
    target_language: LanguageCode = Field(default=LanguageCode.CHINESE, description="目标语言")
    provider: TranslationProvider = Field(default=TranslationProvider.GOOGLE, description="翻译提供商")
    quality_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="质量阈值")
    use_cache: bool = Field(default=True, description="是否使用缓存")
    context: Optional[str] = Field(None, description="翻译上下文")


class TranslationResult(BaseModel):
    """翻译结果"""
    translations: List[TranslationItem] = Field(..., description="翻译结果列表")
    total_count: int = Field(..., description="总数量")
    success_count: int = Field(..., description="成功数量")
    cache_hit_count: int = Field(..., description="缓存命中数量")
    cache_hit_rate: float = Field(..., ge=0.0, le=1.0, description="缓存命中率")
    provider_used: TranslationProvider = Field(..., description="使用的提供商")
    total_cost: float = Field(..., description="总成本")
    processing_time: float = Field(..., description="处理时间(秒)")
    quality_summary: Dict[str, int] = Field(..., description="质量统计")


class TranslationJob(BaseModel):
    """翻译任务"""
    id: str = Field(..., description="任务ID")
    project_id: str = Field(..., description="项目ID")
    user_id: str = Field(..., description="用户ID")
    status: TranslationStatus = Field(..., description="任务状态")
    request: TranslationRequest = Field(..., description="翻译请求")
    result: Optional[TranslationResult] = Field(None, description="翻译结果")
    error_message: Optional[str] = Field(None, description="错误信息")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class CostInfo(BaseModel):
    """成本信息"""
    current_cost: float = Field(..., description="当前成本")
    monthly_total: float = Field(..., description="月度总成本")
    daily_total: float = Field(..., description="日总成本")
    remaining_budget: float = Field(..., description="剩余预算")
    free_tier_remaining: int = Field(..., description="免费额度剩余")
    cost_breakdown: Dict[str, float] = Field(..., description="成本分解")


class UsageRecord(BaseModel):
    """使用记录"""
    id: str = Field(..., description="记录ID")
    provider: TranslationProvider = Field(..., description="提供商")
    user_id: str = Field(..., description="用户ID")
    project_id: Optional[str] = Field(None, description="项目ID")
    request_count: int = Field(..., description="请求数量")
    character_count: int = Field(..., description="字符数量")
    token_count: Optional[int] = Field(None, description="Token数量")
    estimated_cost: float = Field(..., description="预估成本")
    actual_cost: Optional[float] = Field(None, description="实际成本")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class TranslationSuggestion(BaseModel):
    """翻译建议"""
    original_text: str = Field(..., description="原文")
    translated_text: str = Field(..., description="译文")
    provider: TranslationProvider = Field(..., description="提供商")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="质量分数")
    quality_level: QualityLevel = Field(..., description="质量等级")
    is_cached: bool = Field(..., description="是否来自缓存")
    cost: float = Field(..., description="成本")


class TranslationSuggestionsRequest(BaseModel):
    """翻译建议请求"""
    text: str = Field(..., description="待翻译文本")
    providers: List[TranslationProvider] = Field(default=[TranslationProvider.GOOGLE], description="提供商列表")
    source_language: LanguageCode = Field(default=LanguageCode.ENGLISH, description="源语言")
    target_language: LanguageCode = Field(default=LanguageCode.CHINESE, description="目标语言")
    context: Optional[str] = Field(None, description="上下文")


class TranslationSuggestionsResponse(BaseModel):
    """翻译建议响应"""
    success: bool = Field(..., description="是否成功")
    suggestions: List[TranslationSuggestion] = Field(..., description="翻译建议列表")
    total_cost: float = Field(..., description="总成本")
    processing_time: float = Field(..., description="处理时间")
    message: str = Field(..., description="响应消息")


class TranslationCache(BaseModel):
    """翻译缓存"""
    id: str = Field(..., description="缓存ID")
    source_text: str = Field(..., description="源文本")
    translated_text: str = Field(..., description="译文")
    source_language: LanguageCode = Field(..., description="源语言")
    target_language: LanguageCode = Field(..., description="目标语言")
    provider: TranslationProvider = Field(..., description="提供商")
    quality_score: float = Field(..., description="质量分数")
    hit_count: int = Field(default=1, description="命中次数")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    last_used_at: datetime = Field(default_factory=datetime.now, description="最后使用时间")


class TranslationStats(BaseModel):
    """翻译统计"""
    total_translations: int = Field(..., description="总翻译数")
    successful_translations: int = Field(..., description="成功翻译数")
    failed_translations: int = Field(..., description="失败翻译数")
    cache_hits: int = Field(..., description="缓存命中数")
    cache_hit_rate: float = Field(..., description="缓存命中率")
    total_cost: float = Field(..., description="总成本")
    average_quality: float = Field(..., description="平均质量")
    provider_usage: Dict[str, int] = Field(..., description="提供商使用统计")
    quality_distribution: Dict[str, int] = Field(..., description="质量分布")


class TranslationHealthCheck(BaseModel):
    """翻译服务健康检查"""
    service_name: str = Field(..., description="服务名称")
    status: str = Field(..., description="状态")
    providers_status: Dict[str, bool] = Field(..., description="提供商状态")
    cache_status: bool = Field(..., description="缓存状态")
    total_translations_today: int = Field(..., description="今日翻译总数")
    error_rate: float = Field(..., description="错误率")
    average_response_time: float = Field(..., description="平均响应时间")
    last_check_time: datetime = Field(default_factory=datetime.now, description="最后检查时间")
