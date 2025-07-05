"""
翻译服务提供商基础类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio
import time
from ..schemas.translation import TranslationItem, TranslationProvider


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, requests_per_second: float):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0.0
    
    async def acquire(self):
        """获取请求许可"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()


class TranslationError(Exception):
    """翻译异常"""
    
    def __init__(self, message: str, provider: str, error_code: Optional[str] = None):
        self.message = message
        self.provider = provider
        self.error_code = error_code
        super().__init__(self.message)


class BaseTranslationProvider(ABC):
    """翻译服务提供商基础类"""
    
    def __init__(self, provider_name: TranslationProvider):
        self.provider_name = provider_name
        self.max_batch_size = 100
        self.rate_limiter = RateLimiter(requests_per_second=10)
        self.retry_attempts = 3
        self.retry_delay = 1.0
    
    @abstractmethod
    async def translate_batch(
        self, 
        texts: List[str], 
        source_lang: str, 
        target_lang: str,
        context: Optional[str] = None
    ) -> List[TranslationItem]:
        """
        批量翻译文本
        
        Args:
            texts: 待翻译文本列表
            source_lang: 源语言代码
            target_lang: 目标语言代码
            context: 翻译上下文
            
        Returns:
            List[TranslationItem]: 翻译结果列表
        """
        pass
    
    @abstractmethod
    async def translate_single(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        context: Optional[str] = None
    ) -> TranslationItem:
        """
        单个文本翻译
        
        Args:
            text: 待翻译文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
            context: 翻译上下文
            
        Returns:
            TranslationItem: 翻译结果
        """
        pass
    
    @abstractmethod
    async def check_health(self) -> bool:
        """
        检查服务健康状态
        
        Returns:
            bool: 服务是否健康
        """
        pass
    
    @abstractmethod
    def estimate_cost(self, texts: List[str]) -> float:
        """
        估算翻译成本
        
        Args:
            texts: 待翻译文本列表
            
        Returns:
            float: 预估成本
        """
        pass
    
    def _create_batches(self, texts: List[str], batch_size: int) -> List[List[str]]:
        """
        将文本列表分批
        
        Args:
            texts: 文本列表
            batch_size: 批次大小
            
        Returns:
            List[List[str]]: 分批后的文本列表
        """
        batches = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batches.append(batch)
        return batches
    
    async def _retry_on_failure(self, func, *args, **kwargs):
        """
        失败重试装饰器
        
        Args:
            func: 要重试的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
        """
        last_exception = None
        
        for attempt in range(self.retry_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # 指数退避
                    continue
                else:
                    break
        
        # 所有重试都失败了
        raise TranslationError(
            f"Translation failed after {self.retry_attempts} attempts: {str(last_exception)}",
            self.provider_name.value,
            getattr(last_exception, 'error_code', None)
        )
    
    def _handle_translation_error(self, error: Exception, texts: List[str]) -> List[TranslationItem]:
        """
        处理翻译错误，返回错误结果
        
        Args:
            error: 异常对象
            texts: 原始文本列表
            
        Returns:
            List[TranslationItem]: 错误结果列表
        """
        error_results = []
        for text in texts:
            error_results.append(TranslationItem(
                original_text=text,
                translated_text=f"[翻译失败: {str(error)}]",
                confidence=0.0,
                provider=self.provider_name,
                quality_score=0.0
            ))
        return error_results
    
    def _validate_language_codes(self, source_lang: str, target_lang: str) -> bool:
        """
        验证语言代码
        
        Args:
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            bool: 是否有效
        """
        # 基础验证，子类可以重写
        valid_codes = ['en', 'zh', 'zh-CN', 'zh-TW', 'ja', 'ko', 'fr', 'de', 'es']
        return source_lang in valid_codes and target_lang in valid_codes
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 原始文本
            
        Returns:
            str: 清理后的文本
        """
        if not text or not text.strip():
            return ""
        
        # 移除多余的空白字符
        cleaned = ' '.join(text.split())
        
        # 移除特殊控制字符
        cleaned = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\t')
        
        return cleaned.strip()
    
    def _calculate_confidence(self, original: str, translated: str) -> float:
        """
        计算翻译置信度
        
        Args:
            original: 原文
            translated: 译文
            
        Returns:
            float: 置信度分数
        """
        # 基础置信度计算，子类可以重写
        if not translated or translated.startswith('[翻译失败'):
            return 0.0
        
        # 基于长度比例的简单置信度计算
        if len(original) == 0:
            return 0.5
        
        length_ratio = len(translated) / len(original)
        
        # 合理的长度比例范围
        if 0.3 <= length_ratio <= 3.0:
            return 0.8
        elif 0.1 <= length_ratio <= 5.0:
            return 0.6
        else:
            return 0.4
