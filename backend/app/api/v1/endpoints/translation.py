"""
翻译相关API端点
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional
from ....schemas.translation import (
    TranslationRequest, TranslationResult, TranslationSuggestionsRequest,
    TranslationSuggestionsResponse, TranslationProvider, TranslationHealthCheck,
    TranslationStats, CostInfo
)
from ....services.translation_engine import TranslationEngine
from ....providers.provider_factory import provider_factory

router = APIRouter()
translation_engine = TranslationEngine()


@router.post(
    "/translate",
    response_model=TranslationResult,
    summary="批量翻译文本",
    description="使用指定的翻译服务提供商批量翻译文本"
)
async def translate_batch(request: TranslationRequest):
    """
    批量翻译文本接口
    
    - **texts**: 待翻译文本列表
    - **source_language**: 源语言代码
    - **target_language**: 目标语言代码
    - **provider**: 翻译服务提供商
    - **quality_threshold**: 质量阈值
    - **use_cache**: 是否使用缓存
    - **context**: 翻译上下文
    
    返回翻译结果和统计信息
    """
    try:
        result = await translation_engine.translate_batch(request)
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "翻译请求处理失败",
                "code": 500
            }
        )


@router.post(
    "/suggestions",
    response_model=TranslationSuggestionsResponse,
    summary="获取翻译建议",
    description="从多个翻译服务提供商获取翻译建议"
)
async def get_translation_suggestions(request: TranslationSuggestionsRequest):
    """
    获取翻译建议接口
    
    - **text**: 待翻译文本
    - **providers**: 翻译服务提供商列表
    - **source_language**: 源语言代码
    - **target_language**: 目标语言代码
    - **context**: 翻译上下文
    
    返回多个提供商的翻译建议
    """
    try:
        import time
        start_time = time.time()
        
        suggestions = await translation_engine.get_translation_suggestions(
            text=request.text,
            providers=request.providers,
            source_lang=request.source_language.value,
            target_lang=request.target_language.value,
            context=request.context
        )
        
        processing_time = time.time() - start_time
        total_cost = sum(suggestion.cost for suggestion in suggestions)
        
        return TranslationSuggestionsResponse(
            success=True,
            suggestions=suggestions,
            total_cost=total_cost,
            processing_time=processing_time,
            message=f"成功获取 {len(suggestions)} 个翻译建议"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "获取翻译建议失败",
                "code": 500
            }
        )


@router.post(
    "/jobs",
    summary="创建翻译任务",
    description="创建异步翻译任务"
)
async def create_translation_job(
    request: TranslationRequest,
    background_tasks: BackgroundTasks,
    project_id: str = Query(..., description="项目ID"),
    user_id: str = Query(..., description="用户ID")
):
    """
    创建翻译任务接口
    
    用于大批量翻译的异步处理
    """
    try:
        job_id = await translation_engine.create_translation_job(
            request=request,
            project_id=project_id,
            user_id=user_id
        )
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "翻译任务创建成功",
            "status_url": f"/api/v1/translation/jobs/{job_id}"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "创建翻译任务失败",
                "code": 500
            }
        )


@router.get(
    "/jobs/{job_id}",
    summary="获取翻译任务状态",
    description="查询翻译任务的执行状态和结果"
)
async def get_translation_job_status(job_id: str):
    """
    获取翻译任务状态接口
    """
    try:
        job = await translation_engine.get_translation_job_status(job_id)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "Job not found",
                    "message": "翻译任务不存在",
                    "code": 404
                }
            )
        
        return {
            "success": True,
            "job": job.dict(),
            "message": "获取任务状态成功"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "获取任务状态失败",
                "code": 500
            }
        )


@router.get(
    "/providers",
    summary="获取可用的翻译服务提供商",
    description="列出所有可用的翻译服务提供商及其状态"
)
async def get_available_providers():
    """
    获取可用翻译服务提供商接口
    """
    try:
        available_providers = provider_factory.get_available_providers()
        provider_health = await provider_factory.check_providers_health()
        
        providers_info = []
        for provider in available_providers:
            info = provider_factory.get_provider_info(provider)
            info["health_status"] = provider_health.get(provider, False)
            providers_info.append(info)
        
        return {
            "success": True,
            "providers": providers_info,
            "total_count": len(providers_info),
            "message": "获取提供商列表成功"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "获取提供商列表失败",
                "code": 500
            }
        )


@router.get(
    "/providers/{provider}/health",
    summary="检查翻译服务提供商健康状态",
    description="检查指定翻译服务提供商的健康状态"
)
async def check_provider_health(provider: TranslationProvider):
    """
    检查提供商健康状态接口
    """
    try:
        provider_instance = provider_factory.get_provider(provider)
        is_healthy = await provider_instance.check_health()
        
        return {
            "success": True,
            "provider": provider.value,
            "healthy": is_healthy,
            "message": f"提供商 {provider.value} {'健康' if is_healthy else '不可用'}"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": f"检查提供商 {provider.value} 健康状态失败",
                "code": 500
            }
        )


@router.get(
    "/cost",
    response_model=CostInfo,
    summary="获取翻译成本信息",
    description="获取用户或项目的翻译成本统计"
)
async def get_translation_cost(
    user_id: Optional[str] = Query(None, description="用户ID"),
    project_id: Optional[str] = Query(None, description="项目ID")
):
    """
    获取翻译成本信息接口
    """
    try:
        cost_info = await translation_engine.cost_tracker.get_cost_info(
            user_id=user_id,
            project_id=project_id
        )
        
        return cost_info
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "获取成本信息失败",
                "code": 500
            }
        )


@router.get(
    "/stats",
    summary="获取翻译统计信息",
    description="获取翻译使用统计和分析数据"
)
async def get_translation_stats(
    days: int = Query(default=30, ge=1, le=365, description="统计天数"),
    user_id: Optional[str] = Query(None, description="用户ID"),
    project_id: Optional[str] = Query(None, description="项目ID")
):
    """
    获取翻译统计信息接口
    """
    try:
        usage_stats = await translation_engine.cost_tracker.get_usage_stats(
            days=days,
            user_id=user_id,
            project_id=project_id
        )
        
        engine_stats = await translation_engine.get_engine_stats()
        
        return {
            "success": True,
            "usage_stats": usage_stats,
            "engine_stats": engine_stats,
            "message": "获取统计信息成功"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "获取统计信息失败",
                "code": 500
            }
        )


@router.get(
    "/cache/stats",
    summary="获取翻译缓存统计",
    description="获取翻译缓存的使用统计和效率分析"
)
async def get_cache_stats():
    """
    获取翻译缓存统计接口
    """
    try:
        cache_stats = await translation_engine.cache.get_cache_stats()
        efficiency_report = await translation_engine.cache.get_cache_efficiency_report()
        
        return {
            "success": True,
            "cache_stats": cache_stats,
            "efficiency_report": efficiency_report,
            "message": "获取缓存统计成功"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "获取缓存统计失败",
                "code": 500
            }
        )


@router.post(
    "/cache/clear",
    summary="清理翻译缓存",
    description="清理指定条件的翻译缓存"
)
async def clear_translation_cache(
    provider: Optional[TranslationProvider] = Query(None, description="提供商过滤"),
    older_than_days: Optional[int] = Query(None, ge=1, description="清理超过指定天数的缓存")
):
    """
    清理翻译缓存接口
    """
    try:
        await translation_engine.cache.clear_cache(
            provider=provider,
            older_than_days=older_than_days
        )
        
        return {
            "success": True,
            "message": "缓存清理成功"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "缓存清理失败",
                "code": 500
            }
        )


@router.get(
    "/health",
    response_model=TranslationHealthCheck,
    summary="翻译服务健康检查",
    description="检查翻译服务的整体健康状态"
)
async def translation_health_check():
    """
    翻译服务健康检查接口
    """
    try:
        # 检查所有提供商状态
        providers_health = await provider_factory.check_providers_health()
        
        # 获取今日统计
        daily_stats = await translation_engine.cost_tracker.get_daily_stats()
        
        # 检查缓存状态
        cache_stats = await translation_engine.cache.get_cache_stats()
        cache_healthy = cache_stats["total_items"] >= 0  # 缓存可访问即为健康
        
        # 计算错误率
        total_translations = daily_stats["today_usage"]["total_requests"]
        # 这里简化处理，实际应该统计失败的翻译数量
        error_rate = 0.0
        
        # 计算平均响应时间（模拟数据）
        average_response_time = 1.5  # 秒
        
        return TranslationHealthCheck(
            service_name="translation-service",
            status="healthy" if any(providers_health.values()) else "unhealthy",
            providers_status={p.value: status for p, status in providers_health.items()},
            cache_status=cache_healthy,
            total_translations_today=total_translations,
            error_rate=error_rate,
            average_response_time=average_response_time
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "健康检查失败",
                "code": 500
            }
        )
