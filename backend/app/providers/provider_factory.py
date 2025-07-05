"""
翻译服务提供商工厂
"""
from typing import Dict, Type, Optional
from .base_provider import BaseTranslationProvider
from .mock_provider import MockTranslationProvider
from .google_translate import GoogleTranslateProvider
from .openai_translator import OpenAITranslateProvider
from ..schemas.translation import TranslationProvider


class ProviderFactory:
    """翻译服务提供商工厂"""
    
    _providers: Dict[TranslationProvider, Type[BaseTranslationProvider]] = {
        TranslationProvider.GOOGLE: GoogleTranslateProvider,
        TranslationProvider.OPENAI: OpenAITranslateProvider,
        TranslationProvider.MOCK: MockTranslationProvider,
    }
    
    _instances: Dict[TranslationProvider, BaseTranslationProvider] = {}
    
    @classmethod
    def get_provider(cls, provider_type: TranslationProvider) -> BaseTranslationProvider:
        """
        获取翻译服务提供商实例
        
        Args:
            provider_type: 提供商类型
            
        Returns:
            BaseTranslationProvider: 提供商实例
            
        Raises:
            ValueError: 不支持的提供商类型
        """
        if provider_type not in cls._providers:
            raise ValueError(f"Unsupported translation provider: {provider_type}")
        
        # 使用单例模式，避免重复创建实例
        if provider_type not in cls._instances:
            provider_class = cls._providers[provider_type]
            cls._instances[provider_type] = provider_class()
        
        return cls._instances[provider_type]
    
    @classmethod
    def get_available_providers(cls) -> list[TranslationProvider]:
        """
        获取可用的翻译服务提供商列表
        
        Returns:
            List[TranslationProvider]: 可用提供商列表
        """
        available = []
        
        for provider_type in cls._providers.keys():
            try:
                provider = cls.get_provider(provider_type)
                # 这里可以添加健康检查，但为了性能考虑，暂时跳过
                available.append(provider_type)
            except Exception:
                # 如果提供商初始化失败，跳过
                continue
        
        return available
    
    @classmethod
    async def check_providers_health(cls) -> Dict[TranslationProvider, bool]:
        """
        检查所有提供商的健康状态
        
        Returns:
            Dict[TranslationProvider, bool]: 提供商健康状态映射
        """
        health_status = {}
        
        for provider_type in cls._providers.keys():
            try:
                provider = cls.get_provider(provider_type)
                health_status[provider_type] = await provider.check_health()
            except Exception:
                health_status[provider_type] = False
        
        return health_status
    
    @classmethod
    def register_provider(
        cls, 
        provider_type: TranslationProvider, 
        provider_class: Type[BaseTranslationProvider]
    ):
        """
        注册新的翻译服务提供商
        
        Args:
            provider_type: 提供商类型
            provider_class: 提供商类
        """
        cls._providers[provider_type] = provider_class
        
        # 清除可能存在的实例缓存
        if provider_type in cls._instances:
            del cls._instances[provider_type]
    
    @classmethod
    def get_provider_info(cls, provider_type: TranslationProvider) -> Dict[str, any]:
        """
        获取提供商信息
        
        Args:
            provider_type: 提供商类型
            
        Returns:
            Dict[str, any]: 提供商信息
        """
        if provider_type not in cls._providers:
            raise ValueError(f"Unsupported translation provider: {provider_type}")
        
        try:
            provider = cls.get_provider(provider_type)
            
            info = {
                "name": provider_type.value,
                "class": provider.__class__.__name__,
                "max_batch_size": provider.max_batch_size,
                "rate_limit": provider.rate_limiter.requests_per_second,
                "retry_attempts": provider.retry_attempts,
            }
            
            # 添加特定提供商的信息
            if hasattr(provider, 'model'):
                info["model"] = provider.model
            if hasattr(provider, 'cost_per_char'):
                info["cost_per_char"] = provider.cost_per_char
            if hasattr(provider, 'cost_per_1k_tokens'):
                info["cost_per_1k_tokens"] = provider.cost_per_1k_tokens
            
            return info
            
        except Exception as e:
            return {
                "name": provider_type.value,
                "error": str(e),
                "available": False
            }
    
    @classmethod
    def get_best_provider_for_task(
        cls, 
        text_length: int, 
        text_type: str = "general",
        budget_priority: bool = False
    ) -> TranslationProvider:
        """
        根据任务特点推荐最佳提供商
        
        Args:
            text_length: 文本长度
            text_type: 文本类型 ("general", "literary", "technical")
            budget_priority: 是否优先考虑成本
            
        Returns:
            TranslationProvider: 推荐的提供商
        """
        available_providers = cls.get_available_providers()
        
        if not available_providers:
            raise ValueError("No translation providers available")
        
        # 如果只有一个可用提供商，直接返回
        if len(available_providers) == 1:
            return available_providers[0]
        
        # 根据不同条件选择提供商
        if budget_priority or text_length > 10000:
            # 大文本或预算优先，选择Google Translate
            if TranslationProvider.GOOGLE in available_providers:
                return TranslationProvider.GOOGLE
        
        if text_type == "literary":
            # 文学文本，优先选择OpenAI
            if TranslationProvider.OPENAI in available_providers:
                return TranslationProvider.OPENAI
        
        # 默认选择Google Translate（速度快，成本低）
        if TranslationProvider.GOOGLE in available_providers:
            return TranslationProvider.GOOGLE
        
        # 如果Google不可用，选择第一个可用的
        return available_providers[0]
    
    @classmethod
    def clear_instances(cls):
        """清除所有提供商实例缓存"""
        cls._instances.clear()


# 创建全局工厂实例
provider_factory = ProviderFactory()
