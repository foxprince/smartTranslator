"""
翻译API性能测试
使用Locust进行负载测试
"""
from locust import HttpUser, task, between
import json
import random


class TranslationUser(HttpUser):
    """翻译API用户模拟"""
    
    wait_time = between(1, 3)  # 用户请求间隔1-3秒
    
    def on_start(self):
        """用户开始时的初始化"""
        self.test_texts = [
            "Hello, world!",
            "How are you today?",
            "This is a test sentence.",
            "Machine translation is improving rapidly.",
            "Thank you for your help.",
            "The weather is nice today.",
            "I love programming and technology.",
            "Let's build something amazing together.",
            "Artificial intelligence is the future.",
            "Learning new languages is fun."
        ]
        
        self.language_pairs = [
            ("en", "zh"),
            ("en", "es"),
            ("en", "fr"),
            ("zh", "en")
        ]
        
        self.providers = ["google", "openai"]
    
    @task(3)
    def translate_single_text(self):
        """单文本翻译测试 - 权重3（最常用）"""
        text = random.choice(self.test_texts)
        source_lang, target_lang = random.choice(self.language_pairs)
        provider = random.choice(self.providers)
        
        payload = {
            "texts": [text],
            "source_language": source_lang,
            "target_language": target_lang,
            "provider": provider
        }
        
        with self.client.post(
            "/api/translation/translate",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success_count", 0) > 0:
                    response.success()
                else:
                    response.failure("Translation failed")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)
    def translate_batch_texts(self):
        """批量文本翻译测试 - 权重2"""
        texts = random.sample(self.test_texts, k=random.randint(2, 5))
        source_lang, target_lang = random.choice(self.language_pairs)
        provider = random.choice(self.providers)
        
        payload = {
            "texts": texts,
            "source_language": source_lang,
            "target_language": target_lang,
            "provider": provider
        }
        
        with self.client.post(
            "/api/translation/translate",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success_count", 0) == len(texts):
                    response.success()
                else:
                    response.failure("Some translations failed")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)
    def get_translation_suggestions(self):
        """获取翻译建议测试 - 权重2"""
        text = random.choice(self.test_texts)
        source_lang, target_lang = random.choice(self.language_pairs)
        providers = ",".join(random.sample(self.providers, k=random.randint(1, 2)))
        
        params = {
            "text": text,
            "providers": providers,
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        
        with self.client.get(
            "/api/translation/suggestions",
            params=params,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    response.success()
                else:
                    response.failure("No suggestions returned")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def create_translation_job(self):
        """创建翻译任务测试 - 权重1"""
        texts = random.sample(self.test_texts, k=random.randint(3, 8))
        source_lang, target_lang = random.choice(self.language_pairs)
        provider = random.choice(self.providers)
        
        payload = {
            "texts": texts,
            "source_language": source_lang,
            "target_language": target_lang,
            "provider": provider,
            "project_id": f"test-project-{random.randint(1, 100)}",
            "user_id": f"test-user-{random.randint(1, 50)}"
        }
        
        with self.client.post(
            "/api/translation/jobs",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "job_id" in data:
                    response.success()
                    # 存储job_id用于后续查询
                    if not hasattr(self, 'job_ids'):
                        self.job_ids = []
                    self.job_ids.append(data["job_id"])
                else:
                    response.failure("No job_id returned")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def get_job_status(self):
        """查询任务状态测试 - 权重1"""
        if hasattr(self, 'job_ids') and self.job_ids:
            job_id = random.choice(self.job_ids)
            
            with self.client.get(
                f"/api/translation/jobs/{job_id}",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    response.success()
                elif response.status_code == 404:
                    # 任务可能已过期，从列表中移除
                    if job_id in self.job_ids:
                        self.job_ids.remove(job_id)
                    response.success()  # 404是预期的
                else:
                    response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def get_providers_health(self):
        """检查提供商健康状态 - 权重1"""
        with self.client.get(
            "/api/translation/providers/health",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    response.success()
                else:
                    response.failure("Invalid health data format")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def get_engine_stats(self):
        """获取引擎统计 - 权重1"""
        with self.client.get(
            "/api/translation/stats",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "providers_health" in data:
                    response.success()
                else:
                    response.failure("Invalid stats data format")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def get_cache_stats(self):
        """获取缓存统计 - 权重1"""
        with self.client.get(
            "/api/translation/cache/stats",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    response.success()
                else:
                    response.failure("Invalid cache stats format")
            else:
                response.failure(f"HTTP {response.status_code}")


class AdminUser(HttpUser):
    """管理员用户模拟（较少的并发）"""
    
    wait_time = between(5, 10)  # 管理员操作间隔较长
    weight = 1  # 较低的权重
    
    @task
    def clear_cache(self):
        """清空缓存操作"""
        with self.client.delete(
            "/api/translation/cache",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task
    def get_cost_stats(self):
        """获取成本统计"""
        with self.client.get(
            "/api/translation/costs/stats",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")


# 自定义性能测试场景
class StressTestUser(HttpUser):
    """压力测试用户 - 高频率请求"""
    
    wait_time = between(0.1, 0.5)  # 极短的等待时间
    weight = 2
    
    @task
    def rapid_translation_requests(self):
        """快速连续翻译请求"""
        text = "Quick test"
        payload = {
            "texts": [text],
            "source_language": "en",
            "target_language": "zh",
            "provider": "google"
        }
        
        self.client.post("/api/translation/translate", json=payload)
