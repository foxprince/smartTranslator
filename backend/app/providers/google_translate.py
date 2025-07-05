"""
Google Translate API集成
"""
import os
import asyncio
from typing import List, Optional
from google.cloud import translate_v2 as translate
from google.api_core import exceptions as google_exceptions
from .base_provider import BaseTranslationProvider, TranslationError
from ..schemas.translation import TranslationItem, TranslationProvider


class GoogleTranslateProvider(BaseTranslationProvider):
    """Google Translate API提供商"""
    
    def __init__(self):
        super().__init__(TranslationProvider.GOOGLE)
        
        # 初始化Google Translate客户端
        try:
            # 从环境变量获取API密钥
            api_key = os.getenv('GOOGLE_TRANSLATE_API_KEY')
            if api_key:
                self.client = translate.Client(api_key=api_key)
            else:
                # 使用服务账户认证
                self.client = translate.Client()
        except Exception as e:
            raise TranslationError(
                f"Failed to initialize Google Translate client: {str(e)}",
                self.provider_name.value
            )
        
        # Google Translate特定配置
        self.max_batch_size = 128  # Google支持更大的批次
        self.max_text_length = 5000  # 单个文本最大长度
        self.rate_limiter.requests_per_second = 100  # Google有更高的速率限制
        
        # 成本配置
        self.cost_per_char = 0.00002  # $20 per 1M characters
        self.free_tier_chars = 500000  # 500K characters per month
    
    async def translate_single(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        context: Optional[str] = None
    ) -> TranslationItem:
        """单个文本翻译"""
        results = await self.translate_batch([text], source_lang, target_lang, context)
        return results[0]
    
    async def translate_batch(
        self, 
        texts: List[str], 
        source_lang: str, 
        target_lang: str,
        context: Optional[str] = None
    ) -> List[TranslationItem]:
        """批量翻译"""
        if not texts:
            return []
        
        # 验证语言代码
        if not self._validate_language_codes(source_lang, target_lang):
            raise TranslationError(
                f"Unsupported language pair: {source_lang} -> {target_lang}",
                self.provider_name.value
            )
        
        # 清理和验证文本
        cleaned_texts = []
        for text in texts:
            cleaned = self._clean_text(text)
            if len(cleaned) > self.max_text_length:
                cleaned = cleaned[:self.max_text_length]
            cleaned_texts.append(cleaned)
        
        # 分批处理
        all_results = []
        batches = self._create_batches(cleaned_texts, self.max_batch_size)
        
        for batch in batches:
            batch_results = await self._translate_batch_internal(
                batch, source_lang, target_lang
            )
            all_results.extend(batch_results)
        
        return all_results
    
    async def _translate_batch_internal(
        self, 
        texts: List[str], 
        source_lang: str, 
        target_lang: str
    ) -> List[TranslationItem]:
        """内部批量翻译实现"""
        
        async def _do_translate():
            # 速率限制
            await self.rate_limiter.acquire()
            
            # 调用Google Translate API
            # 注意：google-cloud-translate是同步的，我们需要在线程池中运行
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._sync_translate,
                texts,
                source_lang,
                target_lang
            )
            return result
        
        try:
            return await self._retry_on_failure(_do_translate)
        except Exception as e:
            return self._handle_translation_error(e, texts)
    
    def _sync_translate(self, texts: List[str], source_lang: str, target_lang: str) -> List[TranslationItem]:
        """同步翻译调用"""
        try:
            # 调用Google Translate API
            results = self.client.translate(
                texts,
                source_language=source_lang,
                target_language=target_lang
            )
            
            # 处理结果
            translation_items = []
            for i, result in enumerate(results):
                # Google返回的结果格式
                translated_text = result['translatedText']
                detected_language = result.get('detectedSourceLanguage', source_lang)
                
                # 计算置信度
                confidence = self._calculate_google_confidence(texts[i], translated_text, result)
                
                translation_items.append(TranslationItem(
                    original_text=texts[i],
                    translated_text=translated_text,
                    confidence=confidence,
                    provider=self.provider_name,
                    detected_language=detected_language,
                    quality_score=confidence  # Google没有单独的质量分数
                ))
            
            return translation_items
            
        except google_exceptions.GoogleAPIError as e:
            raise TranslationError(
                f"Google Translate API error: {str(e)}",
                self.provider_name.value,
                str(e.code) if hasattr(e, 'code') else None
            )
        except Exception as e:
            raise TranslationError(
                f"Unexpected error in Google Translate: {str(e)}",
                self.provider_name.value
            )
    
    def _calculate_google_confidence(self, original: str, translated: str, api_result: dict) -> float:
        """计算Google翻译的置信度"""
        # Google API有时会返回置信度信息
        if 'confidence' in api_result:
            return float(api_result['confidence'])
        
        # 基于启发式规则计算置信度
        base_confidence = self._calculate_confidence(original, translated)
        
        # Google Translate通常质量较高，给予额外加分
        google_bonus = 0.1
        
        # 检查是否有明显的翻译错误标志
        if any(marker in translated.lower() for marker in ['[翻译失败', 'translation failed', 'error']):
            return 0.0
        
        # 检查是否保持了原文（可能是专有名词）
        if original == translated and len(original) > 1:
            return 0.9  # 专有名词保持原样通常是正确的
        
        return min(1.0, base_confidence + google_bonus)
    
    async def check_health(self) -> bool:
        """检查Google Translate服务健康状态"""
        try:
            # 执行一个简单的翻译测试
            test_result = await self.translate_single("Hello", "en", "zh")
            return test_result.confidence > 0.0
        except Exception:
            return False
    
    def estimate_cost(self, texts: List[str]) -> float:
        """估算Google Translate成本"""
        total_chars = sum(len(text) for text in texts)
        
        # 考虑免费额度
        if hasattr(self, '_monthly_usage'):
            remaining_free = max(0, self.free_tier_chars - self._monthly_usage)
            billable_chars = max(0, total_chars - remaining_free)
        else:
            # 保守估计，假设没有免费额度
            billable_chars = total_chars
        
        return billable_chars * self.cost_per_char
    
    def _validate_language_codes(self, source_lang: str, target_lang: str) -> bool:
        """验证Google Translate支持的语言代码"""
        # Google Translate支持的主要语言代码
        supported_languages = {
            'en', 'zh', 'zh-CN', 'zh-TW', 'ja', 'ko', 'fr', 'de', 'es', 'it', 
            'pt', 'ru', 'ar', 'hi', 'th', 'vi', 'id', 'ms', 'tl', 'nl', 'sv',
            'da', 'no', 'fi', 'pl', 'cs', 'sk', 'hu', 'ro', 'bg', 'hr', 'sl',
            'et', 'lv', 'lt', 'mt', 'ga', 'cy', 'is', 'mk', 'sq', 'sr', 'bs',
            'hr', 'me', 'bg', 'uk', 'be', 'kk', 'ky', 'uz', 'tg', 'mn', 'ka',
            'hy', 'az', 'tr', 'he', 'fa', 'ur', 'ps', 'sd', 'ne', 'si', 'my',
            'km', 'lo', 'ka', 'am', 'sw', 'zu', 'xh', 'af', 'sq', 'eu', 'ca',
            'gl', 'mt', 'cy', 'ga', 'gd', 'br', 'co', 'eo', 'la', 'jw', 'mg',
            'sm', 'sn', 'so', 'st', 'su', 'tl', 'ty', 'yo', 'zu'
        }
        
        return source_lang in supported_languages and target_lang in supported_languages
    
    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        try:
            # 调用Google API获取支持的语言
            languages = self.client.get_languages()
            return [lang['language'] for lang in languages]
        except Exception:
            # 返回常用语言作为后备
            return ['en', 'zh', 'zh-CN', 'zh-TW', 'ja', 'ko', 'fr', 'de', 'es']
