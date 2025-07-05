"""
翻译引擎单元测试
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.translation_engine import TranslationEngine
from app.schemas.translation import (
    TranslationRequest, TranslationProvider, LanguageCode,
    TranslationItem, QualityLevel
)


class TestTranslationEngine:
    """测试翻译引擎"""
    
    def setup_method(self):
        """测试前准备"""
        self.engine = TranslationEngine()
    
    @pytest.mark.asyncio
    async def test_translate_batch_success(self):
        """测试批量翻译成功"""
        # 模拟翻译请求
        request = TranslationRequest(
            texts=["Hello", "World"],
            source_language=LanguageCode.ENGLISH,
            target_language=LanguageCode.CHINESE,
            provider=TranslationProvider.GOOGLE
        )
        
        # 模拟翻译结果
        mock_translation_items = [
            TranslationItem(
                original_text="Hello",
                translated_text="你好",
                confidence=0.9,
                provider=TranslationProvider.GOOGLE,
                quality_score=0.8
            ),
            TranslationItem(
                original_text="World",
                translated_text="世界",
                confidence=0.9,
                provider=TranslationProvider.GOOGLE,
                quality_score=0.8
            )
        ]
        
        # 模拟提供商
        with patch('app.providers.provider_factory.provider_factory.get_provider') as mock_get_provider:
            mock_provider = AsyncMock()
            mock_provider.translate_batch.return_value = mock_translation_items
            mock_get_provider.return_value = mock_provider
            
            # 模拟质量评估
            with patch.object(self.engine.quality_assessor, 'assess_batch') as mock_assess:
                mock_assess.return_value = [
                    Mock(overall_score=0.8, confidence_level=QualityLevel.GOOD),
                    Mock(overall_score=0.8, confidence_level=QualityLevel.GOOD)
                ]
                
                # 模拟成本跟踪
                with patch.object(self.engine.cost_tracker, 'track_translation_usage') as mock_cost:
                    mock_cost.return_value = 0.01
                    
                    # 执行翻译
                    result = await self.engine.translate_batch(request)
                    
                    # 验证结果
                    assert result.total_count == 2
                    assert result.success_count == 2
                    assert result.provider_used == TranslationProvider.GOOGLE
                    assert len(result.translations) == 2
                    assert result.translations[0].translated_text == "你好"
                    assert result.translations[1].translated_text == "世界"
    
    @pytest.mark.asyncio
    async def test_get_translation_suggestions(self):
        """测试获取翻译建议"""
        # 模拟缓存未命中
        with patch.object(self.engine.cache, 'get_cached_translation') as mock_cache:
            mock_cache.return_value = None
            
            # 模拟提供商翻译
            with patch('app.providers.provider_factory.provider_factory.get_provider') as mock_get_provider:
                mock_provider = AsyncMock()
                mock_provider.translate_single.return_value = TranslationItem(
                    original_text="Hello",
                    translated_text="你好",
                    confidence=0.9,
                    provider=TranslationProvider.GOOGLE,
                    quality_score=0.8
                )
                mock_provider.estimate_cost.return_value = 0.001
                mock_get_provider.return_value = mock_provider
                
                # 模拟质量评估
                with patch.object(self.engine.quality_assessor, 'assess_single') as mock_assess:
                    mock_assess.return_value = Mock(
                        overall_score=0.8,
                        confidence_level=QualityLevel.GOOD
                    )
                    
                    # 模拟缓存存储
                    with patch.object(self.engine.cache, 'cache_translation') as mock_cache_store:
                        mock_cache_store.return_value = None
                        
                        # 执行获取建议
                        suggestions = await self.engine.get_translation_suggestions(
                            text="Hello",
                            providers=[TranslationProvider.GOOGLE],
                            source_lang="en",
                            target_lang="zh"
                        )
                        
                        # 验证结果
                        assert len(suggestions) == 1
                        assert suggestions[0].original_text == "Hello"
                        assert suggestions[0].translated_text == "你好"
                        assert suggestions[0].provider == TranslationProvider.GOOGLE
                        assert suggestions[0].is_cached == False
    
    @pytest.mark.asyncio
    async def test_create_translation_job(self):
        """测试创建翻译任务"""
        request = TranslationRequest(
            texts=["Hello"],
            source_language=LanguageCode.ENGLISH,
            target_language=LanguageCode.CHINESE,
            provider=TranslationProvider.GOOGLE
        )
        
        job_id = await self.engine.create_translation_job(
            request=request,
            project_id="test-project",
            user_id="test-user"
        )
        
        # 验证任务创建
        assert job_id is not None
        assert job_id in self.engine.active_jobs
        
        job = self.engine.active_jobs[job_id]
        assert job.project_id == "test-project"
        assert job.user_id == "test-user"
        assert job.request == request
    
    @pytest.mark.asyncio
    async def test_get_translation_job_status(self):
        """测试获取翻译任务状态"""
        # 先创建一个任务
        request = TranslationRequest(
            texts=["Hello"],
            source_language=LanguageCode.ENGLISH,
            target_language=LanguageCode.CHINESE,
            provider=TranslationProvider.GOOGLE
        )
        
        job_id = await self.engine.create_translation_job(
            request=request,
            project_id="test-project",
            user_id="test-user"
        )
        
        # 获取任务状态
        job = await self.engine.get_translation_job_status(job_id)
        
        assert job is not None
        assert job.id == job_id
        assert job.project_id == "test-project"
    
    def test_preprocess_texts(self):
        """测试文本预处理"""
        texts = [
            "  Hello  World  ",
            "",
            "Test\n\nText",
            None
        ]
        
        # 注意：_preprocess_texts是私有方法，这里直接测试
        cleaned = self.engine._preprocess_texts(texts)
        
        assert cleaned[0] == "Hello World"
        assert cleaned[1] == ""
        assert cleaned[2] == "Test Text"
        assert cleaned[3] == ""
    
    def test_generate_quality_summary(self):
        """测试质量统计摘要生成"""
        translations = [
            TranslationItem(
                original_text="test1",
                translated_text="测试1",
                confidence=0.9,
                provider=TranslationProvider.GOOGLE,
                quality_score=0.95
            ),
            TranslationItem(
                original_text="test2",
                translated_text="测试2",
                confidence=0.8,
                provider=TranslationProvider.GOOGLE,
                quality_score=0.75
            ),
            TranslationItem(
                original_text="test3",
                translated_text="测试3",
                confidence=0.6,
                provider=TranslationProvider.GOOGLE,
                quality_score=0.55
            )
        ]
        
        summary = self.engine._generate_quality_summary(translations)
        
        assert summary["excellent"] == 1  # score >= 0.9
        assert summary["good"] == 1       # 0.7 <= score < 0.9
        assert summary["fair"] == 1       # 0.5 <= score < 0.7
        assert summary["poor"] == 0       # score < 0.5
    
    def test_get_quality_level(self):
        """测试质量等级判断"""
        assert self.engine._get_quality_level(0.95) == QualityLevel.EXCELLENT
        assert self.engine._get_quality_level(0.85) == QualityLevel.GOOD
        assert self.engine._get_quality_level(0.65) == QualityLevel.FAIR
        assert self.engine._get_quality_level(0.35) == QualityLevel.POOR
    
    @pytest.mark.asyncio
    async def test_get_engine_stats(self):
        """测试获取引擎统计"""
        # 模拟各种统计数据
        with patch('app.providers.provider_factory.provider_factory.check_providers_health') as mock_health:
            mock_health.return_value = {
                TranslationProvider.GOOGLE: True,
                TranslationProvider.OPENAI: False
            }
            
            with patch.object(self.engine.cache, 'get_cache_stats') as mock_cache_stats:
                mock_cache_stats.return_value = {"total_items": 100}
                
                with patch.object(self.engine.cost_tracker, 'get_daily_stats') as mock_cost_stats:
                    mock_cost_stats.return_value = {"total_cost": 5.0}
                    
                    stats = await self.engine.get_engine_stats()
                    
                    assert "providers_health" in stats
                    assert "cache_stats" in stats
                    assert "cost_stats" in stats
                    assert "active_jobs" in stats
                    assert stats["providers_health"]["google"] == True
                    assert stats["providers_health"]["openai"] == False
