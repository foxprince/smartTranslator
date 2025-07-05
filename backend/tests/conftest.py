"""
测试配置文件
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from app.services.translation_engine import TranslationEngine
from app.providers.provider_factory import ProviderFactory
from app.services.translation_cache import TranslationCache
from app.services.cost_tracker import CostTracker
from app.services.translation_quality import QualityAssessor


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_translation_cache():
    """模拟翻译缓存"""
    cache = Mock(spec=TranslationCache)
    cache.get_cached_translation = AsyncMock(return_value=None)
    cache.cache_translation = AsyncMock()
    cache.get_cache_stats = Mock(return_value={
        "total_items": 100,
        "hit_rate": 0.8,
        "memory_usage": "10MB"
    })
    cache.clear_cache = Mock(return_value={"cleared_items": 100})
    return cache


@pytest.fixture
def mock_cost_tracker():
    """模拟成本跟踪器"""
    tracker = Mock(spec=CostTracker)
    tracker.track_translation_usage = Mock(return_value=0.01)
    tracker.get_daily_stats = Mock(return_value={
        "daily_cost": 5.0,
        "monthly_cost": 150.0,
        "total_translations": 1000
    })
    tracker.check_budget_limit = Mock(return_value=True)
    return tracker


@pytest.fixture
def mock_quality_assessor():
    """模拟质量评估器"""
    assessor = Mock(spec=QualityAssessor)
    assessor.assess_single = Mock(return_value=Mock(
        overall_score=0.8,
        length_score=0.9,
        consistency_score=0.8,
        language_score=0.7,
        structure_score=0.8
    ))
    assessor.assess_batch = Mock(return_value=[
        Mock(overall_score=0.8),
        Mock(overall_score=0.9)
    ])
    return assessor


@pytest.fixture
def mock_provider_factory():
    """模拟提供商工厂"""
    factory = Mock(spec=ProviderFactory)
    
    # 模拟Google提供商
    google_provider = AsyncMock()
    google_provider.translate_single = AsyncMock()
    google_provider.translate_batch = AsyncMock()
    google_provider.estimate_cost = Mock(return_value=0.001)
    google_provider.check_health = AsyncMock(return_value=True)
    
    # 模拟OpenAI提供商
    openai_provider = AsyncMock()
    openai_provider.translate_single = AsyncMock()
    openai_provider.translate_batch = AsyncMock()
    openai_provider.estimate_cost = Mock(return_value=0.002)
    openai_provider.check_health = AsyncMock(return_value=True)
    
    factory.get_provider = Mock(side_effect=lambda provider: {
        "google": google_provider,
        "openai": openai_provider
    }.get(provider))
    
    factory.check_providers_health = AsyncMock(return_value={
        "google": True,
        "openai": True
    })
    
    return factory


@pytest.fixture
def translation_engine(
    mock_translation_cache,
    mock_cost_tracker,
    mock_quality_assessor,
    mock_provider_factory
):
    """创建翻译引擎实例"""
    engine = TranslationEngine()
    engine.cache = mock_translation_cache
    engine.cost_tracker = mock_cost_tracker
    engine.quality_assessor = mock_quality_assessor
    
    # 注入模拟的提供商工厂
    with pytest.MonkeyPatch().context() as m:
        m.setattr('app.providers.provider_factory.provider_factory', mock_provider_factory)
        yield engine


@pytest.fixture
def sample_translation_request():
    """示例翻译请求"""
    from app.schemas.translation import TranslationRequest, LanguageCode, TranslationProvider
    
    return TranslationRequest(
        texts=["Hello", "World", "How are you?"],
        source_language=LanguageCode.ENGLISH,
        target_language=LanguageCode.CHINESE,
        provider=TranslationProvider.GOOGLE
    )


@pytest.fixture
def sample_translation_items():
    """示例翻译项目"""
    from app.schemas.translation import TranslationItem, TranslationProvider
    
    return [
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
            confidence=0.95,
            provider=TranslationProvider.GOOGLE,
            quality_score=0.9
        ),
        TranslationItem(
            original_text="How are you?",
            translated_text="你好吗？",
            confidence=0.85,
            provider=TranslationProvider.GOOGLE,
            quality_score=0.75
        )
    ]


@pytest.fixture
def test_config():
    """测试配置"""
    return {
        "GOOGLE_TRANSLATE_API_KEY": "test-google-key",
        "OPENAI_API_KEY": "test-openai-key",
        "TRANSLATION_CACHE_SIZE": 1000,
        "TRANSLATION_CACHE_TTL": 3600,
        "COST_BUDGET_DAILY": 100.0,
        "COST_BUDGET_MONTHLY": 3000.0
    }


# 测试数据常量
TEST_TEXTS = [
    "Hello, world!",
    "How are you today?",
    "This is a test sentence.",
    "Machine translation is improving rapidly.",
    "Thank you for your help."
]

TEST_LANGUAGE_PAIRS = [
    ("en", "zh"),
    ("en", "es"),
    ("zh", "en"),
    ("es", "en")
]

TEST_PROVIDERS = ["google", "openai"]


class TestDataFactory:
    """测试数据工厂"""
    
    @staticmethod
    def create_translation_request(
        texts=None,
        source_lang="en",
        target_lang="zh",
        provider="google"
    ):
        """创建翻译请求"""
        from app.schemas.translation import TranslationRequest, LanguageCode, TranslationProvider
        
        if texts is None:
            texts = TEST_TEXTS[:3]
        
        return TranslationRequest(
            texts=texts,
            source_language=LanguageCode(source_lang),
            target_language=LanguageCode(target_lang),
            provider=TranslationProvider(provider)
        )
    
    @staticmethod
    def create_translation_item(
        original="Hello",
        translated="你好",
        confidence=0.9,
        provider="google",
        quality_score=0.8
    ):
        """创建翻译项目"""
        from app.schemas.translation import TranslationItem, TranslationProvider
        
        return TranslationItem(
            original_text=original,
            translated_text=translated,
            confidence=confidence,
            provider=TranslationProvider(provider),
            quality_score=quality_score
        )


@pytest.fixture
def test_data_factory():
    """测试数据工厂实例"""
    return TestDataFactory()


# 测试标记
pytest_plugins = []

# 慢速测试标记
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# 测试收集钩子
def pytest_collection_modifyitems(config, items):
    """修改测试项目收集"""
    for item in items:
        # 为集成测试添加标记
        if "test_translation_api" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        # 为单元测试添加标记
        elif "test_translation_engine" in item.nodeid:
            item.add_marker(pytest.mark.unit)
