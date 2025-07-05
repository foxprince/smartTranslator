"""
翻译API集成测试
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.schemas.translation import TranslationProvider, LanguageCode


client = TestClient(app)


class TestTranslationAPI:
    """测试翻译API"""
    
    def test_translate_batch_endpoint(self):
        """测试批量翻译端点"""
        # 模拟翻译引擎
        with patch('app.api.translation.translation_engine') as mock_engine:
            mock_result = AsyncMock()
            mock_result.total_count = 2
            mock_result.success_count = 2
            mock_result.provider_used = TranslationProvider.GOOGLE
            mock_result.translations = [
                {
                    "original_text": "Hello",
                    "translated_text": "你好",
                    "confidence": 0.9,
                    "provider": "google",
                    "quality_score": 0.8
                },
                {
                    "original_text": "World",
                    "translated_text": "世界",
                    "confidence": 0.9,
                    "provider": "google",
                    "quality_score": 0.8
                }
            ]
            mock_result.quality_summary = {
                "excellent": 0,
                "good": 2,
                "fair": 0,
                "poor": 0
            }
            mock_result.total_cost = 0.01
            
            mock_engine.translate_batch.return_value = mock_result
            
            # 发送请求
            response = client.post(
                "/api/translation/translate",
                json={
                    "texts": ["Hello", "World"],
                    "source_language": "en",
                    "target_language": "zh",
                    "provider": "google"
                }
            )
            
            # 验证响应
            assert response.status_code == 200
            data = response.json()
            assert data["total_count"] == 2
            assert data["success_count"] == 2
            assert data["provider_used"] == "google"
            assert len(data["translations"]) == 2
    
    def test_get_translation_suggestions_endpoint(self):
        """测试获取翻译建议端点"""
        with patch('app.api.translation.translation_engine') as mock_engine:
            mock_suggestions = [
                {
                    "original_text": "Hello",
                    "translated_text": "你好",
                    "confidence": 0.9,
                    "provider": "google",
                    "quality_score": 0.8,
                    "is_cached": False,
                    "estimated_cost": 0.001
                },
                {
                    "original_text": "Hello",
                    "translated_text": "您好",
                    "confidence": 0.85,
                    "provider": "openai",
                    "quality_score": 0.9,
                    "is_cached": False,
                    "estimated_cost": 0.002
                }
            ]
            
            mock_engine.get_translation_suggestions.return_value = mock_suggestions
            
            # 发送请求
            response = client.get(
                "/api/translation/suggestions",
                params={
                    "text": "Hello",
                    "providers": "google,openai",
                    "source_lang": "en",
                    "target_lang": "zh"
                }
            )
            
            # 验证响应
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["provider"] == "google"
            assert data[1]["provider"] == "openai"
    
    def test_create_translation_job_endpoint(self):
        """测试创建翻译任务端点"""
        with patch('app.api.translation.translation_engine') as mock_engine:
            mock_job_id = "job-123"
            mock_engine.create_translation_job.return_value = mock_job_id
            
            # 发送请求
            response = client.post(
                "/api/translation/jobs",
                json={
                    "texts": ["Hello", "World"],
                    "source_language": "en",
                    "target_language": "zh",
                    "provider": "google",
                    "project_id": "test-project",
                    "user_id": "test-user"
                }
            )
            
            # 验证响应
            assert response.status_code == 200
            data = response.json()
            assert data["job_id"] == mock_job_id
            assert data["status"] == "created"
    
    def test_get_translation_job_status_endpoint(self):
        """测试获取翻译任务状态端点"""
        with patch('app.api.translation.translation_engine') as mock_engine:
            mock_job = AsyncMock()
            mock_job.id = "job-123"
            mock_job.status = "completed"
            mock_job.progress = 100
            mock_job.project_id = "test-project"
            mock_job.user_id = "test-user"
            mock_job.created_at = "2024-01-01T00:00:00Z"
            mock_job.completed_at = "2024-01-01T00:01:00Z"
            
            mock_engine.get_translation_job_status.return_value = mock_job
            
            # 发送请求
            response = client.get("/api/translation/jobs/job-123")
            
            # 验证响应
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "job-123"
            assert data["status"] == "completed"
            assert data["progress"] == 100
    
    def test_get_providers_health_endpoint(self):
        """测试获取提供商健康状态端点"""
        with patch('app.providers.provider_factory.provider_factory') as mock_factory:
            mock_factory.check_providers_health.return_value = {
                TranslationProvider.GOOGLE: True,
                TranslationProvider.OPENAI: False
            }
            
            # 发送请求
            response = client.get("/api/translation/providers/health")
            
            # 验证响应
            assert response.status_code == 200
            data = response.json()
            assert data["google"] == True
            assert data["openai"] == False
    
    def test_get_cost_stats_endpoint(self):
        """测试获取成本统计端点"""
        with patch('app.api.translation.translation_engine') as mock_engine:
            mock_stats = {
                "daily_cost": 5.0,
                "monthly_cost": 150.0,
                "total_translations": 1000,
                "cost_by_provider": {
                    "google": 3.0,
                    "openai": 2.0
                }
            }
            
            mock_engine.cost_tracker.get_daily_stats.return_value = mock_stats
            
            # 发送请求
            response = client.get("/api/translation/costs/stats")
            
            # 验证响应
            assert response.status_code == 200
            data = response.json()
            assert data["daily_cost"] == 5.0
            assert data["monthly_cost"] == 150.0
    
    def test_get_cache_stats_endpoint(self):
        """测试获取缓存统计端点"""
        with patch('app.api.translation.translation_engine') as mock_engine:
            mock_stats = {
                "total_items": 500,
                "hit_rate": 0.85,
                "memory_usage": "50MB",
                "oldest_entry": "2024-01-01T00:00:00Z"
            }
            
            mock_engine.cache.get_cache_stats.return_value = mock_stats
            
            # 发送请求
            response = client.get("/api/translation/cache/stats")
            
            # 验证响应
            assert response.status_code == 200
            data = response.json()
            assert data["total_items"] == 500
            assert data["hit_rate"] == 0.85
    
    def test_clear_cache_endpoint(self):
        """测试清空缓存端点"""
        with patch('app.api.translation.translation_engine') as mock_engine:
            mock_engine.cache.clear_cache.return_value = {"cleared_items": 100}
            
            # 发送请求
            response = client.delete("/api/translation/cache")
            
            # 验证响应
            assert response.status_code == 200
            data = response.json()
            assert data["cleared_items"] == 100
    
    def test_get_engine_stats_endpoint(self):
        """测试获取引擎统计端点"""
        with patch('app.api.translation.translation_engine') as mock_engine:
            mock_stats = {
                "providers_health": {
                    "google": True,
                    "openai": False
                },
                "cache_stats": {
                    "total_items": 500,
                    "hit_rate": 0.85
                },
                "cost_stats": {
                    "daily_cost": 5.0,
                    "monthly_cost": 150.0
                },
                "active_jobs": 3
            }
            
            mock_engine.get_engine_stats.return_value = mock_stats
            
            # 发送请求
            response = client.get("/api/translation/stats")
            
            # 验证响应
            assert response.status_code == 200
            data = response.json()
            assert "providers_health" in data
            assert "cache_stats" in data
            assert "cost_stats" in data
            assert "active_jobs" in data
    
    def test_invalid_translation_request(self):
        """测试无效的翻译请求"""
        # 缺少必需字段
        response = client.post(
            "/api/translation/translate",
            json={
                "texts": [],  # 空文本列表
                "source_language": "en"
                # 缺少 target_language
            }
        )
        
        assert response.status_code == 422  # 验证错误
    
    def test_unsupported_language_pair(self):
        """测试不支持的语言对"""
        response = client.post(
            "/api/translation/translate",
            json={
                "texts": ["Hello"],
                "source_language": "invalid_lang",
                "target_language": "zh",
                "provider": "google"
            }
        )
        
        assert response.status_code == 422  # 验证错误
    
    def test_job_not_found(self):
        """测试任务不存在"""
        with patch('app.api.translation.translation_engine') as mock_engine:
            mock_engine.get_translation_job_status.return_value = None
            
            response = client.get("/api/translation/jobs/nonexistent-job")
            
            assert response.status_code == 404
