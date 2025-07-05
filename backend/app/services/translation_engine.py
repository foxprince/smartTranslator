"""
智能翻译引擎核心服务
"""
import uuid
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from ..schemas.translation import (
    TranslationRequest, TranslationResult, TranslationItem, TranslationJob,
    TranslationProvider, TranslationStatus, QualityLevel, TranslationSuggestion
)
from ..providers.provider_factory import provider_factory
from .translation_cache import TranslationCache
from .translation_quality import QualityAssessor
from .cost_tracker import CostTracker


class TranslationEngine:
    """智能翻译引擎"""
    
    def __init__(self):
        self.cache = TranslationCache()
        self.quality_assessor = QualityAssessor()
        self.cost_tracker = CostTracker()
        self.active_jobs: Dict[str, TranslationJob] = {}
    
    async def translate_batch(self, request: TranslationRequest) -> TranslationResult:
        """
        批量翻译文本
        
        Args:
            request: 翻译请求
            
        Returns:
            TranslationResult: 翻译结果
        """
        start_time = time.time()
        
        # 1. 预处理文本
        cleaned_texts = self._preprocess_texts(request.texts)
        
        # 2. 检查缓存
        cached_results, uncached_texts = await self._check_cache(
            cleaned_texts, request
        ) if request.use_cache else ([], cleaned_texts)
        
        # 3. 翻译未缓存的文本
        new_translations = []
        if uncached_texts:
            new_translations = await self._translate_uncached_texts(
                uncached_texts, request
            )
            
            # 4. 质量评估
            quality_scores = await self.quality_assessor.assess_batch(
                uncached_texts, [t.translated_text for t in new_translations]
            )
            
            # 更新质量分数
            for translation, quality in zip(new_translations, quality_scores):
                translation.quality_score = quality.overall_score
            
            # 5. 缓存新翻译
            if request.use_cache:
                await self.cache.cache_translations(new_translations)
        
        # 6. 合并结果
        all_translations = self._merge_translation_results(
            cached_results, new_translations, cleaned_texts
        )
        
        # 7. 成本跟踪
        total_cost = await self.cost_tracker.track_translation_usage(
            request.provider, len(uncached_texts), 
            sum(len(t) for t in uncached_texts)
        )
        
        # 8. 生成结果
        processing_time = time.time() - start_time
        
        return TranslationResult(
            translations=all_translations,
            total_count=len(all_translations),
            success_count=len([t for t in all_translations if t.confidence > 0]),
            cache_hit_count=len(cached_results),
            cache_hit_rate=len(cached_results) / len(cleaned_texts) if cleaned_texts else 0,
            provider_used=request.provider,
            total_cost=total_cost,
            processing_time=processing_time,
            quality_summary=self._generate_quality_summary(all_translations)
        )
    
    async def get_translation_suggestions(
        self, 
        text: str,
        providers: List[TranslationProvider],
        source_lang: str = "en",
        target_lang: str = "zh",
        context: Optional[str] = None
    ) -> List[TranslationSuggestion]:
        """
        获取多个提供商的翻译建议
        
        Args:
            text: 待翻译文本
            providers: 提供商列表
            source_lang: 源语言
            target_lang: 目标语言
            context: 翻译上下文
            
        Returns:
            List[TranslationSuggestion]: 翻译建议列表
        """
        suggestions = []
        
        for provider in providers:
            try:
                # 检查缓存
                cached_result = await self.cache.get_cached_translation(
                    text, source_lang, target_lang, provider
                )
                
                if cached_result:
                    # 使用缓存结果
                    suggestion = TranslationSuggestion(
                        original_text=text,
                        translated_text=cached_result.translated_text,
                        provider=provider,
                        confidence=cached_result.confidence,
                        quality_score=cached_result.quality_score or 0.8,
                        quality_level=self._get_quality_level(cached_result.quality_score or 0.8),
                        is_cached=True,
                        cost=0.0
                    )
                else:
                    # 调用翻译服务
                    provider_instance = provider_factory.get_provider(provider)
                    translation_item = await provider_instance.translate_single(
                        text, source_lang, target_lang, context
                    )
                    
                    # 质量评估
                    quality_score = await self.quality_assessor.assess_single(
                        text, translation_item.translated_text
                    )
                    
                    # 估算成本
                    cost = provider_instance.estimate_cost([text])
                    
                    suggestion = TranslationSuggestion(
                        original_text=text,
                        translated_text=translation_item.translated_text,
                        provider=provider,
                        confidence=translation_item.confidence,
                        quality_score=quality_score.overall_score,
                        quality_level=quality_score.confidence_level,
                        is_cached=False,
                        cost=cost
                    )
                    
                    # 缓存结果
                    await self.cache.cache_translation(translation_item)
                
                suggestions.append(suggestion)
                
            except Exception as e:
                # 记录错误但继续处理其他提供商
                print(f"Error getting suggestion from {provider}: {str(e)}")
                continue
        
        # 按质量分数排序
        suggestions.sort(key=lambda x: x.quality_score, reverse=True)
        
        return suggestions
    
    async def create_translation_job(
        self, 
        request: TranslationRequest,
        project_id: str,
        user_id: str
    ) -> str:
        """
        创建翻译任务
        
        Args:
            request: 翻译请求
            project_id: 项目ID
            user_id: 用户ID
            
        Returns:
            str: 任务ID
        """
        job_id = str(uuid.uuid4())
        
        job = TranslationJob(
            id=job_id,
            project_id=project_id,
            user_id=user_id,
            status=TranslationStatus.PENDING,
            request=request,
            created_at=datetime.now()
        )
        
        self.active_jobs[job_id] = job
        
        # 异步执行翻译任务
        import asyncio
        asyncio.create_task(self._execute_translation_job(job_id))
        
        return job_id
    
    async def get_translation_job_status(self, job_id: str) -> Optional[TranslationJob]:
        """
        获取翻译任务状态
        
        Args:
            job_id: 任务ID
            
        Returns:
            Optional[TranslationJob]: 任务信息
        """
        return self.active_jobs.get(job_id)
    
    async def _execute_translation_job(self, job_id: str):
        """执行翻译任务"""
        job = self.active_jobs.get(job_id)
        if not job:
            return
        
        try:
            # 更新状态
            job.status = TranslationStatus.IN_PROGRESS
            job.started_at = datetime.now()
            
            # 执行翻译
            result = await self.translate_batch(job.request)
            
            # 更新结果
            job.result = result
            job.status = TranslationStatus.COMPLETED
            job.completed_at = datetime.now()
            
        except Exception as e:
            # 处理错误
            job.status = TranslationStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
    
    def _preprocess_texts(self, texts: List[str]) -> List[str]:
        """预处理文本"""
        cleaned_texts = []
        
        for text in texts:
            if not text or not text.strip():
                cleaned_texts.append("")
                continue
            
            # 清理文本
            cleaned = ' '.join(text.split())
            cleaned = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\t')
            cleaned_texts.append(cleaned.strip())
        
        return cleaned_texts
    
    async def _check_cache(
        self, 
        texts: List[str], 
        request: TranslationRequest
    ) -> Tuple[List[TranslationItem], List[str]]:
        """检查缓存"""
        cached_results = []
        uncached_texts = []
        
        for text in texts:
            if not text:
                # 空文本直接返回空翻译
                cached_results.append(TranslationItem(
                    original_text=text,
                    translated_text="",
                    confidence=1.0,
                    provider=request.provider,
                    quality_score=1.0
                ))
                continue
            
            cached_item = await self.cache.get_cached_translation(
                text, 
                request.source_language.value,
                request.target_language.value,
                request.provider
            )
            
            if cached_item and cached_item.quality_score >= request.quality_threshold:
                cached_results.append(cached_item)
            else:
                uncached_texts.append(text)
                cached_results.append(None)  # 占位符
        
        return cached_results, uncached_texts
    
    async def _translate_uncached_texts(
        self, 
        texts: List[str], 
        request: TranslationRequest
    ) -> List[TranslationItem]:
        """翻译未缓存的文本"""
        provider_instance = provider_factory.get_provider(request.provider)
        
        return await provider_instance.translate_batch(
            texts,
            request.source_language.value,
            request.target_language.value,
            request.context
        )
    
    def _merge_translation_results(
        self,
        cached_results: List[Optional[TranslationItem]],
        new_translations: List[TranslationItem],
        original_texts: List[str]
    ) -> List[TranslationItem]:
        """合并翻译结果"""
        merged_results = []
        new_translation_index = 0
        
        for i, cached_item in enumerate(cached_results):
            if cached_item is not None:
                merged_results.append(cached_item)
            else:
                if new_translation_index < len(new_translations):
                    merged_results.append(new_translations[new_translation_index])
                    new_translation_index += 1
                else:
                    # 创建错误结果
                    merged_results.append(TranslationItem(
                        original_text=original_texts[i],
                        translated_text="[翻译失败]",
                        confidence=0.0,
                        provider=TranslationProvider.GOOGLE,
                        quality_score=0.0
                    ))
        
        return merged_results
    
    def _generate_quality_summary(self, translations: List[TranslationItem]) -> Dict[str, int]:
        """生成质量统计摘要"""
        summary = {
            "excellent": 0,
            "good": 0,
            "fair": 0,
            "poor": 0
        }
        
        for translation in translations:
            quality_level = self._get_quality_level(translation.quality_score or 0.0)
            summary[quality_level.value] += 1
        
        return summary
    
    def _get_quality_level(self, score: float) -> QualityLevel:
        """根据分数获取质量等级"""
        if score >= 0.9:
            return QualityLevel.EXCELLENT
        elif score >= 0.7:
            return QualityLevel.GOOD
        elif score >= 0.5:
            return QualityLevel.FAIR
        else:
            return QualityLevel.POOR
    
    async def get_engine_stats(self) -> Dict[str, any]:
        """获取引擎统计信息"""
        provider_health = await provider_factory.check_providers_health()
        cache_stats = await self.cache.get_cache_stats()
        cost_stats = await self.cost_tracker.get_daily_stats()
        
        return {
            "providers_health": {p.value: status for p, status in provider_health.items()},
            "cache_stats": cache_stats,
            "cost_stats": cost_stats,
            "active_jobs": len(self.active_jobs),
            "available_providers": [p.value for p in provider_factory.get_available_providers()]
        }
