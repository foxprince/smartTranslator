"""
翻译缓存服务
"""
import hashlib
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..schemas.translation import TranslationItem, TranslationProvider, TranslationCache as CacheModel


class TranslationCache:
    """翻译缓存管理器"""
    
    def __init__(self):
        # 内存缓存（生产环境应使用Redis）
        self._cache: Dict[str, CacheModel] = {}
        self.max_cache_size = 10000
        self.cache_ttl_days = 30
        self.min_quality_for_cache = 0.6
    
    async def get_cached_translation(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        provider: TranslationProvider
    ) -> Optional[TranslationItem]:
        """
        获取缓存的翻译
        
        Args:
            text: 源文本
            source_lang: 源语言
            target_lang: 目标语言
            provider: 翻译提供商
            
        Returns:
            Optional[TranslationItem]: 缓存的翻译项，如果不存在则返回None
        """
        cache_key = self._generate_cache_key(text, source_lang, target_lang, provider)
        
        cached_item = self._cache.get(cache_key)
        if not cached_item:
            return None
        
        # 检查是否过期
        if self._is_expired(cached_item):
            del self._cache[cache_key]
            return None
        
        # 更新使用统计
        cached_item.hit_count += 1
        cached_item.last_used_at = datetime.now()
        
        # 转换为TranslationItem
        return TranslationItem(
            original_text=cached_item.source_text,
            translated_text=cached_item.translated_text,
            confidence=0.9,  # 缓存的翻译给予较高置信度
            provider=cached_item.provider,
            quality_score=cached_item.quality_score
        )
    
    async def cache_translation(self, translation: TranslationItem):
        """
        缓存单个翻译
        
        Args:
            translation: 翻译项
        """
        await self.cache_translations([translation])
    
    async def cache_translations(self, translations: List[TranslationItem]):
        """
        批量缓存翻译
        
        Args:
            translations: 翻译项列表
        """
        for translation in translations:
            # 只缓存质量足够好的翻译
            if (translation.quality_score and 
                translation.quality_score >= self.min_quality_for_cache and
                translation.confidence > 0.5):
                
                await self._store_translation(translation)
        
        # 清理过期缓存
        await self._cleanup_expired_cache()
        
        # 如果缓存过大，清理最少使用的项
        if len(self._cache) > self.max_cache_size:
            await self._cleanup_lru_cache()
    
    async def _store_translation(self, translation: TranslationItem):
        """存储翻译到缓存"""
        # 这里假设我们知道源语言和目标语言
        # 在实际实现中，这些信息应该从翻译请求中传递
        source_lang = "en"  # 默认值，实际应该从上下文获取
        target_lang = "zh"
        
        cache_key = self._generate_cache_key(
            translation.original_text,
            source_lang,
            target_lang,
            translation.provider
        )
        
        cache_item = CacheModel(
            id=cache_key,
            source_text=translation.original_text,
            translated_text=translation.translated_text,
            source_language=source_lang,
            target_language=target_lang,
            provider=translation.provider,
            quality_score=translation.quality_score or 0.8,
            hit_count=1,
            created_at=datetime.now(),
            last_used_at=datetime.now()
        )
        
        self._cache[cache_key] = cache_item
    
    def _generate_cache_key(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        provider: TranslationProvider
    ) -> str:
        """生成缓存键"""
        # 标准化文本（移除多余空格，统一换行符）
        normalized_text = ' '.join(text.split())
        
        # 创建缓存键的组合字符串
        key_components = [
            normalized_text,
            source_lang,
            target_lang,
            provider.value
        ]
        
        key_string = '|'.join(key_components)
        
        # 使用SHA256生成哈希
        return hashlib.sha256(key_string.encode('utf-8')).hexdigest()
    
    def _is_expired(self, cache_item: CacheModel) -> bool:
        """检查缓存项是否过期"""
        expiry_date = cache_item.created_at + timedelta(days=self.cache_ttl_days)
        return datetime.now() > expiry_date
    
    async def _cleanup_expired_cache(self):
        """清理过期的缓存项"""
        expired_keys = []
        
        for key, cache_item in self._cache.items():
            if self._is_expired(cache_item):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
    
    async def _cleanup_lru_cache(self):
        """清理最少使用的缓存项"""
        # 按最后使用时间排序，删除最旧的项
        sorted_items = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_used_at
        )
        
        # 删除最旧的20%
        items_to_remove = int(len(sorted_items) * 0.2)
        
        for i in range(items_to_remove):
            key = sorted_items[i][0]
            del self._cache[key]
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        if not self._cache:
            return {
                "total_items": 0,
                "cache_size_mb": 0,
                "hit_rate": 0.0,
                "average_quality": 0.0,
                "provider_distribution": {},
                "language_pairs": {}
            }
        
        total_hits = sum(item.hit_count for item in self._cache.values())
        total_quality = sum(item.quality_score for item in self._cache.values())
        
        # 提供商分布
        provider_dist = {}
        for item in self._cache.values():
            provider = item.provider.value
            provider_dist[provider] = provider_dist.get(provider, 0) + 1
        
        # 语言对分布
        language_pairs = {}
        for item in self._cache.values():
            pair = f"{item.source_language}-{item.target_language}"
            language_pairs[pair] = language_pairs.get(pair, 0) + 1
        
        # 估算缓存大小
        cache_size_bytes = sum(
            len(item.source_text.encode('utf-8')) + 
            len(item.translated_text.encode('utf-8'))
            for item in self._cache.values()
        )
        
        return {
            "total_items": len(self._cache),
            "cache_size_mb": round(cache_size_bytes / (1024 * 1024), 2),
            "total_hits": total_hits,
            "average_hits_per_item": round(total_hits / len(self._cache), 2),
            "average_quality": round(total_quality / len(self._cache), 3),
            "provider_distribution": provider_dist,
            "language_pairs": language_pairs,
            "oldest_item": min(item.created_at for item in self._cache.values()).isoformat(),
            "newest_item": max(item.created_at for item in self._cache.values()).isoformat()
        }
    
    async def search_cache(
        self,
        query: str,
        source_lang: Optional[str] = None,
        target_lang: Optional[str] = None,
        provider: Optional[TranslationProvider] = None,
        limit: int = 10
    ) -> List[CacheModel]:
        """
        搜索缓存内容
        
        Args:
            query: 搜索查询
            source_lang: 源语言过滤
            target_lang: 目标语言过滤
            provider: 提供商过滤
            limit: 结果限制
            
        Returns:
            List[CacheModel]: 匹配的缓存项
        """
        results = []
        query_lower = query.lower()
        
        for cache_item in self._cache.values():
            # 应用过滤条件
            if source_lang and cache_item.source_language != source_lang:
                continue
            if target_lang and cache_item.target_language != target_lang:
                continue
            if provider and cache_item.provider != provider:
                continue
            
            # 检查是否匹配查询
            if (query_lower in cache_item.source_text.lower() or
                query_lower in cache_item.translated_text.lower()):
                results.append(cache_item)
            
            if len(results) >= limit:
                break
        
        # 按质量分数排序
        results.sort(key=lambda x: x.quality_score, reverse=True)
        
        return results
    
    async def clear_cache(
        self,
        provider: Optional[TranslationProvider] = None,
        older_than_days: Optional[int] = None
    ):
        """
        清理缓存
        
        Args:
            provider: 只清理指定提供商的缓存
            older_than_days: 只清理超过指定天数的缓存
        """
        keys_to_remove = []
        
        for key, cache_item in self._cache.items():
            should_remove = True
            
            # 提供商过滤
            if provider and cache_item.provider != provider:
                should_remove = False
            
            # 时间过滤
            if older_than_days:
                cutoff_date = datetime.now() - timedelta(days=older_than_days)
                if cache_item.created_at > cutoff_date:
                    should_remove = False
            
            if should_remove:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._cache[key]
    
    async def get_cache_efficiency_report(self) -> Dict[str, Any]:
        """获取缓存效率报告"""
        if not self._cache:
            return {"message": "缓存为空"}
        
        # 计算各种效率指标
        items = list(self._cache.values())
        
        # 命中率分析
        hit_counts = [item.hit_count for item in items]
        high_hit_items = len([h for h in hit_counts if h > 5])
        low_hit_items = len([h for h in hit_counts if h == 1])
        
        # 质量分析
        quality_scores = [item.quality_score for item in items]
        high_quality_items = len([q for q in quality_scores if q > 0.8])
        low_quality_items = len([q for q in quality_scores if q < 0.6])
        
        # 时间分析
        now = datetime.now()
        recent_items = len([
            item for item in items 
            if (now - item.last_used_at).days < 7
        ])
        
        return {
            "total_items": len(items),
            "efficiency_metrics": {
                "high_hit_items": high_hit_items,
                "low_hit_items": low_hit_items,
                "hit_efficiency": round((high_hit_items / len(items)) * 100, 1),
                "high_quality_items": high_quality_items,
                "low_quality_items": low_quality_items,
                "quality_efficiency": round((high_quality_items / len(items)) * 100, 1),
                "recent_usage_items": recent_items,
                "usage_efficiency": round((recent_items / len(items)) * 100, 1)
            },
            "recommendations": self._generate_cache_recommendations(items)
        }
    
    def _generate_cache_recommendations(self, items: List[CacheModel]) -> List[str]:
        """生成缓存优化建议"""
        recommendations = []
        
        # 分析命中率
        low_hit_items = len([item for item in items if item.hit_count == 1])
        if low_hit_items > len(items) * 0.5:
            recommendations.append("考虑提高缓存质量阈值，减少低命中率项目")
        
        # 分析质量
        low_quality_items = len([item for item in items if item.quality_score < 0.6])
        if low_quality_items > len(items) * 0.2:
            recommendations.append("考虑清理低质量缓存项目")
        
        # 分析使用时间
        now = datetime.now()
        old_items = len([
            item for item in items 
            if (now - item.last_used_at).days > 14
        ])
        if old_items > len(items) * 0.3:
            recommendations.append("考虑清理长时间未使用的缓存项目")
        
        # 分析缓存大小
        if len(items) > self.max_cache_size * 0.8:
            recommendations.append("缓存接近容量限制，考虑扩容或清理")
        
        return recommendations
