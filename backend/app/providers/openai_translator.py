"""
OpenAI GPT翻译集成
"""
import os
import json
import asyncio
from typing import List, Optional, Dict, Any
import openai
from openai import AsyncOpenAI
from .base_provider import BaseTranslationProvider, TranslationError
from ..schemas.translation import TranslationItem, TranslationProvider


class OpenAITranslateProvider(BaseTranslationProvider):
    """OpenAI GPT翻译提供商"""
    
    def __init__(self):
        super().__init__(TranslationProvider.OPENAI)
        
        # 初始化OpenAI客户端
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            
            self.client = AsyncOpenAI(api_key=api_key)
        except Exception as e:
            raise TranslationError(
                f"Failed to initialize OpenAI client: {str(e)}",
                self.provider_name.value
            )
        
        # OpenAI特定配置
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 4000
        self.temperature = 0.3  # 较低的温度以获得更一致的翻译
        self.max_batch_size = 10  # OpenAI需要逐个处理，但可以并发
        self.rate_limiter.requests_per_second = 3  # OpenAI有较严格的速率限制
        
        # 成本配置
        self.cost_per_1k_tokens = 0.002  # $2 per 1K tokens for gpt-3.5-turbo
        self.avg_chars_per_token = 4  # 平均字符数per token
    
    async def translate_single(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        context: Optional[str] = None
    ) -> TranslationItem:
        """单个文本翻译"""
        if not text or not text.strip():
            return TranslationItem(
                original_text=text,
                translated_text="",
                confidence=1.0,
                provider=self.provider_name,
                model_used=self.model,
                quality_score=1.0
            )
        
        cleaned_text = self._clean_text(text)
        
        try:
            # 构建翻译提示
            system_prompt = self._build_translation_prompt(source_lang, target_lang, context)
            
            # 速率限制
            await self.rate_limiter.acquire()
            
            # 调用OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": cleaned_text}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            # 计算置信度和质量分数
            confidence = self._calculate_openai_confidence(cleaned_text, translated_text, response)
            quality_score = self._calculate_quality_score(cleaned_text, translated_text)
            
            return TranslationItem(
                original_text=text,
                translated_text=translated_text,
                confidence=confidence,
                provider=self.provider_name,
                model_used=self.model,
                quality_score=quality_score
            )
            
        except Exception as e:
            return self._handle_single_translation_error(e, text)
    
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
        
        # 并发处理翻译请求
        semaphore = asyncio.Semaphore(self.max_batch_size)
        
        async def translate_with_semaphore(text: str) -> TranslationItem:
            async with semaphore:
                return await self.translate_single(text, source_lang, target_lang, context)
        
        # 创建并发任务
        tasks = [translate_with_semaphore(text) for text in texts]
        
        # 等待所有翻译完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果和异常
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # 处理异常情况
                error_item = self._handle_single_translation_error(result, texts[i])
                final_results.append(error_item)
            else:
                final_results.append(result)
        
        return final_results
    
    def _build_translation_prompt(
        self, 
        source_lang: str, 
        target_lang: str, 
        context: Optional[str] = None
    ) -> str:
        """构建翻译提示词"""
        
        # 语言名称映射
        lang_names = {
            'en': 'English',
            'zh': 'Chinese',
            'zh-CN': 'Simplified Chinese',
            'zh-TW': 'Traditional Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'fr': 'French',
            'de': 'German',
            'es': 'Spanish'
        }
        
        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)
        
        base_prompt = f"""You are a professional translator specializing in {source_name} to {target_name} translation.

Your task is to translate the given text accurately while maintaining:
1. Original meaning and intent
2. Natural and fluent expression in {target_name}
3. Appropriate tone and style
4. Cultural context and nuances
5. Formatting and structure

Guidelines:
- Provide only the translation, no explanations or notes
- Maintain the original formatting (line breaks, punctuation)
- For technical terms, use standard translations
- For proper nouns, keep original or use established translations
- Ensure the translation sounds natural to native speakers"""
        
        # 添加上下文信息
        if context:
            base_prompt += f"\n\nContext: {context}"
        
        # 针对特定语言对的特殊指导
        if source_lang == 'en' and target_lang in ['zh', 'zh-CN']:
            base_prompt += """

Special instructions for English to Chinese translation:
- Use appropriate Chinese punctuation (，。！？：；)
- Maintain formal/informal tone as appropriate
- Use simplified Chinese characters
- Consider Chinese reading habits and expression patterns"""
        
        elif source_lang in ['zh', 'zh-CN'] and target_lang == 'en':
            base_prompt += """

Special instructions for Chinese to English translation:
- Use natural English expressions, avoid literal translations
- Maintain the original tone (formal/informal)
- Use appropriate English punctuation
- Consider English reading patterns and idioms"""
        
        return base_prompt
    
    def _calculate_openai_confidence(
        self, 
        original: str, 
        translated: str, 
        response: Any
    ) -> float:
        """计算OpenAI翻译的置信度"""
        
        # 基础置信度
        base_confidence = self._calculate_confidence(original, translated)
        
        # OpenAI特定的置信度调整
        openai_bonus = 0.1  # GPT通常质量较高
        
        # 检查响应质量指标
        if hasattr(response, 'usage'):
            # 如果使用了合理数量的tokens，通常质量更好
            tokens_used = response.usage.total_tokens
            expected_tokens = len(original) / self.avg_chars_per_token * 1.5  # 翻译通常会稍长
            
            if 0.5 <= tokens_used / expected_tokens <= 2.0:
                openai_bonus += 0.05
        
        # 检查翻译是否完整
        if len(translated) < len(original) * 0.3:
            # 翻译过短，可能不完整
            return max(0.3, base_confidence - 0.2)
        
        # 检查是否有明显错误
        error_indicators = [
            'I cannot translate',
            'I apologize',
            'As an AI',
            '[翻译失败',
            'Translation failed'
        ]
        
        if any(indicator in translated for indicator in error_indicators):
            return 0.1
        
        return min(1.0, base_confidence + openai_bonus)
    
    def _calculate_quality_score(self, original: str, translated: str) -> float:
        """计算翻译质量分数"""
        
        # 基础质量检查
        if not translated or len(translated.strip()) == 0:
            return 0.0
        
        quality_score = 0.8  # OpenAI基础质量分数
        
        # 长度合理性检查
        length_ratio = len(translated) / len(original) if len(original) > 0 else 0
        if 0.5 <= length_ratio <= 2.0:
            quality_score += 0.1
        elif length_ratio < 0.3 or length_ratio > 3.0:
            quality_score -= 0.2
        
        # 检查是否保持了原文结构
        original_lines = original.count('\n')
        translated_lines = translated.count('\n')
        if original_lines == translated_lines:
            quality_score += 0.05
        
        # 检查标点符号使用
        if any(punct in translated for punct in ['。', '，', '！', '？']) and 'zh' in str(self.provider_name):
            quality_score += 0.05  # 正确使用中文标点
        
        return min(1.0, max(0.0, quality_score))
    
    def _handle_single_translation_error(self, error: Exception, text: str) -> TranslationItem:
        """处理单个翻译错误"""
        error_message = str(error)
        
        # 根据错误类型提供不同的错误信息
        if "rate limit" in error_message.lower():
            translated_text = "[翻译失败: API速率限制]"
        elif "quota" in error_message.lower() or "billing" in error_message.lower():
            translated_text = "[翻译失败: API配额不足]"
        elif "timeout" in error_message.lower():
            translated_text = "[翻译失败: 请求超时]"
        else:
            translated_text = f"[翻译失败: {error_message[:50]}]"
        
        return TranslationItem(
            original_text=text,
            translated_text=translated_text,
            confidence=0.0,
            provider=self.provider_name,
            model_used=self.model,
            quality_score=0.0
        )
    
    async def check_health(self) -> bool:
        """检查OpenAI服务健康状态"""
        try:
            # 执行一个简单的翻译测试
            test_result = await self.translate_single("Hello", "en", "zh")
            return test_result.confidence > 0.5 and not test_result.translated_text.startswith('[翻译失败')
        except Exception:
            return False
    
    def estimate_cost(self, texts: List[str]) -> float:
        """估算OpenAI翻译成本"""
        total_chars = sum(len(text) for text in texts)
        
        # 估算token数量（输入 + 输出）
        input_tokens = total_chars / self.avg_chars_per_token
        output_tokens = input_tokens * 1.2  # 翻译输出通常比输入稍长
        system_tokens = 200  # 系统提示的大概token数
        
        total_tokens = (input_tokens + output_tokens + system_tokens) * len(texts)
        
        return (total_tokens / 1000) * self.cost_per_1k_tokens
    
    def _validate_language_codes(self, source_lang: str, target_lang: str) -> bool:
        """验证OpenAI支持的语言代码"""
        # OpenAI GPT支持大多数主要语言
        supported_languages = {
            'en', 'zh', 'zh-CN', 'zh-TW', 'ja', 'ko', 'fr', 'de', 'es', 'it',
            'pt', 'ru', 'ar', 'hi', 'th', 'vi', 'id', 'ms', 'tl', 'nl', 'sv',
            'da', 'no', 'fi', 'pl', 'cs', 'sk', 'hu', 'ro', 'bg', 'hr', 'sl',
            'tr', 'he', 'fa', 'ur', 'bn', 'ta', 'te', 'ml', 'kn', 'gu', 'pa'
        }
        
        return source_lang in supported_languages and target_lang in supported_languages
    
    def set_model(self, model: str):
        """设置使用的模型"""
        valid_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
        if model in valid_models:
            self.model = model
            # 更新成本配置
            if model.startswith("gpt-4"):
                self.cost_per_1k_tokens = 0.03  # GPT-4更贵
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    def set_temperature(self, temperature: float):
        """设置翻译的创造性程度"""
        if 0.0 <= temperature <= 1.0:
            self.temperature = temperature
        else:
            raise ValueError("Temperature must be between 0.0 and 1.0")
