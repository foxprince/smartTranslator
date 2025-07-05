"""
模拟翻译提供商
用于测试和演示，提供基本的翻译功能
"""
import asyncio
from typing import List, Optional
from .base_provider import BaseTranslationProvider, TranslationError
from ..schemas.translation import TranslationItem, TranslationProvider

class MockTranslationProvider(BaseTranslationProvider):
    """模拟翻译提供商"""
    
    def __init__(self):
        super().__init__(TranslationProvider.MOCK)  # 使用MOCK枚举值
        self.name = "mock"
        self.display_name = "模拟翻译"
        
        # 简单的翻译字典
        self.translations = {
            "hello": "你好",
            "world": "世界", 
            "hello world": "你好世界",
            "good morning": "早上好",
            "good evening": "晚上好",
            "thank you": "谢谢",
            "goodbye": "再见",
            "yes": "是",
            "no": "不",
            "please": "请",
            "sorry": "对不起",
            "how are you": "你好吗",
            "what is your name": "你叫什么名字",
            "nice to meet you": "很高兴见到你",
            "i love you": "我爱你",
            "welcome": "欢迎"
        }
    
    async def translate_single(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "zh",
        context: Optional[str] = None
    ) -> TranslationItem:
        """翻译单个文本"""
        
        # 模拟处理时间
        await asyncio.sleep(0.1)
        
        # 简单翻译逻辑
        text_lower = text.lower().strip()
        
        if text_lower in self.translations:
            translated_text = self.translations[text_lower]
            confidence = 0.9
        else:
            # 简单的单词替换
            words = text_lower.split()
            translated_words = []
            
            for word in words:
                if word in self.translations:
                    translated_words.append(self.translations[word])
                else:
                    translated_words.append(f"[{word}]")
            
            translated_text = " ".join(translated_words)
            confidence = 0.6
        
        return TranslationItem(
            original_text=text,
            translated_text=translated_text,
            confidence=confidence,
            provider=TranslationProvider.MOCK,
            model_used="mock-translator-v1",
            detected_language=source_lang,
            quality_score=confidence
        )
    
    async def translate_batch(
        self,
        texts: List[str],
        source_lang: str = "en",
        target_lang: str = "zh",
        context: Optional[str] = None
    ) -> List[TranslationItem]:
        """批量翻译"""
        results = []
        for text in texts:
            try:
                result = await self.translate_single(text, source_lang, target_lang, context)
                results.append(result)
            except Exception as e:
                # 创建失败结果
                results.append(TranslationItem(
                    original_text=text,
                    translated_text=f"[翻译失败: {e}]",
                    confidence=0.0,
                    provider=TranslationProvider.MOCK,
                    quality_score=0.0
                ))
        return results
    
    async def check_health(self) -> bool:
        """健康检查"""
        return True
    
    def estimate_cost(self, texts: List[str]) -> float:
        """估算成本"""
        return 0.0  # 免费
    
    async def get_supported_languages(self) -> List[str]:
        """获取支持的语言"""
        return ["en", "zh"]
