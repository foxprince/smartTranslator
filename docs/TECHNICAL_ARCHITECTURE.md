# SmartTranslator 技术架构详解

## 📋 文档信息
- **创建日期**: 2024-07-05
- **最后更新**: 2024-07-05
- **维护者**: 技术团队
- **版本**: v1.0

## 🎯 架构概述

SmartTranslator采用现代化的前后端分离架构，结合微服务理念设计了可扩展的翻译服务平台。系统以FastAPI为核心构建后端服务，React为基础构建前端界面，通过RESTful API进行通信。

## 🏗️ 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    SmartTranslator 系统架构                 │
├─────────────────────────────────────────────────────────────┤
│  用户层           │  Web浏览器 + 移动端 + API客户端         │
├─────────────────────────────────────────────────────────────┤
│  负载均衡层       │  Nginx + SSL终端 + 静态资源服务         │
├─────────────────────────────────────────────────────────────┤
│  前端层           │  React 18 + TypeScript + Ant Design    │
├─────────────────────────────────────────────────────────────┤
│  API网关层        │  FastAPI + 路由管理 + 中间件           │
├─────────────────────────────────────────────────────────────┤
│  业务逻辑层       │  翻译引擎 + 文档处理 + 质量评估         │
├─────────────────────────────────────────────────────────────┤
│  服务集成层       │  Google Translate + OpenAI + OCR       │
├─────────────────────────────────────────────────────────────┤
│  缓存层           │  Redis + 内存缓存 + 查询优化            │
├─────────────────────────────────────────────────────────────┤
│  数据持久层       │  PostgreSQL + 文件存储 + 备份          │
├─────────────────────────────────────────────────────────────┤
│  基础设施层       │  Docker + 监控 + 日志 + CI/CD          │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 核心组件架构

### 1. 后端架构 (FastAPI)

#### 目录结构
```
backend/
├── app/
│   ├── api/                    # API路由层
│   │   ├── __init__.py
│   │   ├── translation.py      # 翻译相关API
│   │   └── document.py         # 文档处理API
│   ├── core/                   # 核心配置
│   │   ├── config.py           # 应用配置
│   │   ├── database.py         # 数据库连接
│   │   └── security.py         # 安全配置
│   ├── models/                 # 数据模型
│   │   ├── translation.py      # 翻译数据模型
│   │   └── document.py         # 文档数据模型
│   ├── schemas/                # Pydantic模式
│   │   ├── translation.py      # 翻译请求/响应模式
│   │   └── document.py         # 文档处理模式
│   ├── services/               # 业务服务层
│   │   ├── translation_engine.py    # 翻译引擎
│   │   ├── document_processor.py    # 文档处理器
│   │   ├── quality_assessment.py   # 质量评估
│   │   ├── translation_cache.py    # 翻译缓存
│   │   └── cost_tracking.py        # 成本跟踪
│   ├── providers/              # 外部服务提供商
│   │   ├── base.py             # 基础提供商类
│   │   ├── google_translate.py # Google翻译
│   │   └── openai_translator.py # OpenAI翻译
│   └── utils/                  # 工具函数
│       ├── text_processing.py  # 文本处理
│       └── file_handling.py    # 文件处理
├── tests/                      # 测试代码
├── alembic/                    # 数据库迁移
└── requirements.txt            # 依赖管理
```

#### 核心设计模式

**1. 工厂模式 - 翻译提供商管理**
```python
class TranslationProviderFactory:
    @staticmethod
    def create_provider(provider_type: str) -> BaseTranslationProvider:
        if provider_type == "google":
            return GoogleTranslateProvider()
        elif provider_type == "openai":
            return OpenAITranslator()
        else:
            raise ValueError(f"Unknown provider: {provider_type}")
```

**2. 策略模式 - 质量评估算法**
```python
class QualityAssessmentStrategy:
    def assess(self, original: str, translated: str) -> QualityScore:
        pass

class LengthReasonablenessStrategy(QualityAssessmentStrategy):
    def assess(self, original: str, translated: str) -> QualityScore:
        # 长度合理性评估逻辑
        pass
```

**3. 观察者模式 - 翻译进度通知**
```python
class TranslationObserver:
    def update(self, progress: int, status: str):
        pass

class TranslationEngine:
    def __init__(self):
        self.observers = []
    
    def notify_observers(self, progress: int, status: str):
        for observer in self.observers:
            observer.update(progress, status)
```

### 2. 前端架构 (React + TypeScript)

#### 目录结构
```
frontend/
├── src/
│   ├── components/             # 通用组件
│   │   ├── Layout/            # 布局组件
│   │   ├── Charts/            # 图表组件
│   │   └── Common/            # 通用UI组件
│   ├── pages/                 # 页面组件
│   │   ├── Dashboard/         # 仪表盘
│   │   ├── TranslationManagement/  # 翻译管理
│   │   ├── DocumentManagement/     # 文档管理
│   │   ├── ProviderManagement/     # 提供商管理
│   │   ├── CacheManagement/        # 缓存管理
│   │   ├── CostManagement/         # 成本管理
│   │   ├── QualityAnalysis/        # 质量分析
│   │   ├── SystemMonitoring/       # 系统监控
│   │   └── Settings/               # 系统设置
│   ├── services/              # API服务
│   │   ├── api.ts             # API客户端
│   │   ├── translation.ts     # 翻译服务
│   │   └── document.ts        # 文档服务
│   ├── store/                 # 状态管理
│   │   ├── index.ts           # Store配置
│   │   ├── translation.ts     # 翻译状态
│   │   └── document.ts        # 文档状态
│   ├── types/                 # 类型定义
│   │   ├── translation.ts     # 翻译类型
│   │   └── document.ts        # 文档类型
│   ├── utils/                 # 工具函数
│   │   ├── format.ts          # 格式化工具
│   │   └── validation.ts      # 验证工具
│   └── App.tsx                # 应用入口
├── public/                    # 静态资源
└── package.json               # 依赖管理
```

#### 状态管理架构
使用React Context + useReducer实现轻量级状态管理：

```typescript
// 翻译状态管理
interface TranslationState {
  tasks: TranslationTask[];
  currentTask: TranslationTask | null;
  loading: boolean;
  error: string | null;
}

const TranslationContext = createContext<{
  state: TranslationState;
  dispatch: Dispatch<TranslationAction>;
}>();
```

## 📊 数据架构

### 数据库设计 (PostgreSQL)

#### 核心数据表

**1. 翻译任务表 (translation_tasks)**
```sql
CREATE TABLE translation_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(50) NOT NULL,
    source_text TEXT NOT NULL,
    translated_text TEXT,
    source_language VARCHAR(10) NOT NULL,
    target_language VARCHAR(10) NOT NULL,
    provider VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    quality_score FLOAT,
    cost DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

**2. 文档表 (documents)**
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(50) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'uploaded',
    processing_status VARCHAR(30) DEFAULT 'pending',
    extracted_text TEXT,
    text_length INTEGER,
    translation_result JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**3. 翻译缓存表 (translation_cache)**
```sql
CREATE TABLE translation_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key VARCHAR(64) UNIQUE NOT NULL,
    source_text_hash VARCHAR(64) NOT NULL,
    source_language VARCHAR(10) NOT NULL,
    target_language VARCHAR(10) NOT NULL,
    provider VARCHAR(20) NOT NULL,
    translated_text TEXT NOT NULL,
    quality_score FLOAT,
    hit_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);
```

#### 索引优化策略
```sql
-- 翻译任务查询优化
CREATE INDEX idx_translation_tasks_user_status ON translation_tasks(user_id, status);
CREATE INDEX idx_translation_tasks_created_at ON translation_tasks(created_at DESC);

-- 文档查询优化
CREATE INDEX idx_documents_user_type ON documents(user_id, file_type);
CREATE INDEX idx_documents_status ON documents(status, processing_status);

-- 缓存查询优化
CREATE INDEX idx_translation_cache_key ON translation_cache(cache_key);
CREATE INDEX idx_translation_cache_hash ON translation_cache(source_text_hash);
CREATE INDEX idx_translation_cache_expires ON translation_cache(expires_at);
```

### 缓存架构 (Redis)

#### 缓存层次结构
```
L1 Cache (应用内存)
├── 配置缓存 (5分钟TTL)
├── 用户会话 (30分钟TTL)
└── 热点数据 (10分钟TTL)

L2 Cache (Redis)
├── 翻译结果缓存 (24小时TTL)
├── 文档处理结果 (12小时TTL)
├── API响应缓存 (5分钟TTL)
└── 统计数据缓存 (1小时TTL)
```

#### Redis数据结构设计
```python
# 翻译缓存
translation:{hash} -> {
    "source_text": "原文",
    "translated_text": "译文",
    "quality_score": 0.95,
    "provider": "google",
    "created_at": "2024-07-05T10:00:00Z"
}

# 用户会话
session:{user_id} -> {
    "user_info": {...},
    "permissions": [...],
    "last_activity": "2024-07-05T10:00:00Z"
}

# 统计数据
stats:daily:{date} -> {
    "translation_count": 1000,
    "document_count": 50,
    "total_cost": 25.50,
    "avg_quality": 0.92
}
```

## 🔌 服务集成架构

### 翻译服务提供商集成

#### 1. Google Translate API集成
```python
class GoogleTranslateProvider(BaseTranslationProvider):
    def __init__(self):
        self.client = translate.Client(credentials=self.get_credentials())
        self.rate_limiter = RateLimiter(requests_per_second=10)
        self.cost_calculator = GoogleCostCalculator()
    
    async def translate(self, request: TranslationRequest) -> TranslationResult:
        # 速率限制
        await self.rate_limiter.acquire()
        
        # 成本预估
        estimated_cost = self.cost_calculator.estimate(request.texts)
        
        # 执行翻译
        results = await self._batch_translate(request.texts)
        
        # 质量评估
        quality_scores = await self._assess_quality(request.texts, results)
        
        return TranslationResult(
            translations=results,
            quality_scores=quality_scores,
            total_cost=estimated_cost,
            provider="google"
        )
```

#### 2. OpenAI GPT集成
```python
class OpenAITranslator(BaseTranslationProvider):
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-3.5-turbo"
        self.context_manager = TranslationContextManager()
    
    async def translate(self, request: TranslationRequest) -> TranslationResult:
        # 构建上下文感知的提示
        prompt = self._build_context_prompt(request)
        
        # 批量处理
        results = []
        for text_chunk in self._chunk_texts(request.texts):
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text_chunk}
                ],
                temperature=0.3
            )
            results.append(response.choices[0].message.content)
        
        return TranslationResult(
            translations=results,
            provider="openai",
            confidence_scores=self._calculate_confidence(results)
        )
```

### 文档处理服务集成

#### OCR服务集成 (Tesseract)
```python
class OCRProcessor:
    def __init__(self):
        self.tesseract_config = '--oem 3 --psm 6'
        self.supported_languages = ['chi_sim', 'eng']
    
    async def extract_text_from_image(self, image_path: str) -> str:
        # 图像预处理
        processed_image = await self._preprocess_image(image_path)
        
        # OCR识别
        text = pytesseract.image_to_string(
            processed_image,
            lang='+'.join(self.supported_languages),
            config=self.tesseract_config
        )
        
        # 后处理清理
        cleaned_text = self._clean_ocr_text(text)
        
        return cleaned_text
```

## 🚀 性能优化架构

### 1. 异步处理架构

#### 任务队列设计
```python
from celery import Celery

# Celery配置
celery_app = Celery(
    'smarttranslator',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@celery_app.task(bind=True)
def process_document_async(self, document_id: str):
    """异步文档处理任务"""
    try:
        # 更新任务状态
        self.update_state(state='PROCESSING', meta={'progress': 0})
        
        # 执行文档处理
        processor = DocumentProcessor()
        result = processor.process_document(document_id)
        
        # 更新进度
        self.update_state(state='SUCCESS', meta={'result': result})
        
        return result
    except Exception as exc:
        self.update_state(
            state='FAILURE',
            meta={'error': str(exc)}
        )
        raise
```

#### 批量处理优化
```python
class BatchTranslationProcessor:
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(5)  # 并发限制
    
    async def process_batch(self, texts: List[str]) -> List[TranslationResult]:
        # 分批处理
        batches = [texts[i:i+self.batch_size] 
                  for i in range(0, len(texts), self.batch_size)]
        
        # 并发执行
        tasks = []
        for batch in batches:
            task = self._process_single_batch(batch)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并结果
        return self._merge_results(results)
    
    async def _process_single_batch(self, batch: List[str]):
        async with self.semaphore:
            return await self.translation_engine.translate_batch(batch)
```

### 2. 缓存优化策略

#### 多级缓存架构
```python
class MultiLevelCache:
    def __init__(self):
        self.l1_cache = {}  # 内存缓存
        self.l2_cache = redis.Redis()  # Redis缓存
        self.l3_cache = DatabaseCache()  # 数据库缓存
    
    async def get(self, key: str) -> Optional[Any]:
        # L1缓存查找
        if key in self.l1_cache:
            return self.l1_cache[key]
        
        # L2缓存查找
        value = await self.l2_cache.get(key)
        if value:
            # 回填L1缓存
            self.l1_cache[key] = value
            return value
        
        # L3缓存查找
        value = await self.l3_cache.get(key)
        if value:
            # 回填上级缓存
            await self.l2_cache.set(key, value, ex=3600)
            self.l1_cache[key] = value
            return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        # 写入所有缓存层
        self.l1_cache[key] = value
        await self.l2_cache.set(key, value, ex=ttl)
        await self.l3_cache.set(key, value, ttl)
```

#### 智能缓存策略
```python
class IntelligentCacheManager:
    def __init__(self):
        self.cache_stats = CacheStatistics()
        self.eviction_policy = LRUEvictionPolicy()
    
    def should_cache(self, request: TranslationRequest) -> bool:
        # 基于文本长度决定是否缓存
        if len(request.source_text) < 10:
            return False  # 短文本不缓存
        
        # 基于历史命中率决定
        hit_rate = self.cache_stats.get_hit_rate(request.language_pair)
        if hit_rate < 0.3:
            return False  # 低命中率不缓存
        
        return True
    
    def generate_cache_key(self, request: TranslationRequest) -> str:
        # 生成稳定的缓存键
        content = f"{request.source_text}|{request.source_language}|{request.target_language}|{request.provider}"
        return hashlib.sha256(content.encode()).hexdigest()
```

## 🔒 安全架构

### 1. 认证和授权

#### JWT认证实现
```python
class JWTAuthenticator:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.expire_minutes = 1440  # 24小时
    
    def create_access_token(self, user_id: str, permissions: List[str]) -> str:
        payload = {
            "user_id": user_id,
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(minutes=self.expire_minutes),
            "iat": datetime.utcnow(),
            "type": "access"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
```

#### 权限控制中间件
```python
class PermissionMiddleware:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission
    
    async def __call__(self, request: Request, call_next):
        # 提取JWT令牌
        token = self._extract_token(request)
        
        # 验证令牌
        payload = self.jwt_authenticator.verify_token(token)
        
        # 检查权限
        user_permissions = payload.get("permissions", [])
        if self.required_permission not in user_permissions:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # 添加用户信息到请求
        request.state.user_id = payload["user_id"]
        request.state.permissions = user_permissions
        
        response = await call_next(request)
        return response
```

### 2. 数据安全

#### 敏感数据加密
```python
class DataEncryption:
    def __init__(self):
        self.cipher_suite = Fernet(settings.ENCRYPTION_KEY)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """加密敏感数据"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """解密敏感数据"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
```

#### API密钥管理
```python
class APIKeyManager:
    def __init__(self):
        self.key_store = SecureKeyStore()
    
    def get_provider_key(self, provider: str) -> str:
        """安全获取提供商API密钥"""
        encrypted_key = self.key_store.get(f"{provider}_api_key")
        return self.decrypt_key(encrypted_key)
    
    def rotate_keys(self):
        """定期轮换API密钥"""
        for provider in ["google", "openai"]:
            old_key = self.get_provider_key(provider)
            new_key = self.generate_new_key(provider)
            self.key_store.update(f"{provider}_api_key", new_key)
```

## 📊 监控和日志架构

### 1. 应用监控

#### 性能指标收集
```python
class MetricsCollector:
    def __init__(self):
        self.metrics_store = MetricsStore()
        self.alert_manager = AlertManager()
    
    @contextmanager
    def measure_execution_time(self, operation: str):
        start_time = time.time()
        try:
            yield
        finally:
            execution_time = time.time() - start_time
            self.record_metric(f"{operation}_duration", execution_time)
            
            # 检查是否需要告警
            if execution_time > self.get_threshold(operation):
                self.alert_manager.send_alert(
                    f"Slow operation detected: {operation} took {execution_time:.2f}s"
                )
    
    def record_metric(self, metric_name: str, value: float):
        self.metrics_store.record(metric_name, value, timestamp=time.time())
```

#### 健康检查系统
```python
class HealthChecker:
    def __init__(self):
        self.checks = [
            DatabaseHealthCheck(),
            RedisHealthCheck(),
            ExternalAPIHealthCheck(),
            DiskSpaceHealthCheck()
        ]
    
    async def check_system_health(self) -> HealthStatus:
        results = {}
        overall_status = "healthy"
        
        for check in self.checks:
            try:
                result = await check.perform_check()
                results[check.name] = result
                
                if result.status != "healthy":
                    overall_status = "unhealthy"
                    
            except Exception as e:
                results[check.name] = HealthCheckResult(
                    status="error",
                    message=str(e)
                )
                overall_status = "unhealthy"
        
        return HealthStatus(
            overall_status=overall_status,
            checks=results,
            timestamp=datetime.utcnow()
        )
```

### 2. 结构化日志

#### 日志格式标准化
```python
import structlog

# 配置结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

class TranslationLogger:
    def __init__(self):
        self.logger = structlog.get_logger()
    
    def log_translation_request(self, request: TranslationRequest, user_id: str):
        self.logger.info(
            "translation_request",
            user_id=user_id,
            source_language=request.source_language,
            target_language=request.target_language,
            provider=request.provider,
            text_length=len(request.source_text),
            request_id=request.request_id
        )
    
    def log_translation_result(self, result: TranslationResult, processing_time: float):
        self.logger.info(
            "translation_completed",
            request_id=result.request_id,
            success_count=result.success_count,
            failed_count=result.failed_count,
            total_cost=result.total_cost,
            avg_quality_score=result.avg_quality_score,
            processing_time=processing_time
        )
```

## 🚀 部署架构

### 1. 容器化部署

#### Docker配置
```dockerfile
# 后端Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose配置
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/smarttranslator
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_BASE_URL=http://localhost:8000

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=smarttranslator
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
```

### 2. CI/CD流水线

#### GitHub Actions配置
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        cd backend
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        # 部署脚本
        ./scripts/deploy.sh
```

## 📈 扩展性设计

### 1. 水平扩展策略

#### 负载均衡配置
```nginx
upstream backend_servers {
    server backend1:8000 weight=3;
    server backend2:8000 weight=3;
    server backend3:8000 weight=2;
    
    # 健康检查
    health_check interval=30s fails=3 passes=2;
}

server {
    listen 80;
    server_name api.smarttranslator.com;
    
    location / {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # 连接池配置
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

#### 数据库分片策略
```python
class DatabaseSharding:
    def __init__(self):
        self.shards = {
            'shard1': 'postgresql://user:pass@db1:5432/smarttranslator',
            'shard2': 'postgresql://user:pass@db2:5432/smarttranslator',
            'shard3': 'postgresql://user:pass@db3:5432/smarttranslator'
        }
    
    def get_shard_for_user(self, user_id: str) -> str:
        # 基于用户ID的一致性哈希
        hash_value = hashlib.md5(user_id.encode()).hexdigest()
        shard_index = int(hash_value, 16) % len(self.shards)
        return list(self.shards.keys())[shard_index]
    
    def get_connection(self, user_id: str):
        shard_name = self.get_shard_for_user(user_id)
        return create_engine(self.shards[shard_name])
```

### 2. 微服务演进路径

#### 服务拆分策略
```
当前单体架构 → 微服务架构演进路径

Phase 1: 提取独立服务
├── Translation Service (翻译服务)
├── Document Service (文档服务)
└── User Service (用户服务)

Phase 2: 细化业务服务
├── Provider Management Service (提供商管理)
├── Quality Assessment Service (质量评估)
├── Cost Tracking Service (成本跟踪)
└── Cache Management Service (缓存管理)

Phase 3: 支撑服务
├── Notification Service (通知服务)
├── Analytics Service (分析服务)
├── Audit Service (审计服务)
└── Configuration Service (配置服务)
```

---

**技术架构维护说明**: 此文档详细描述了SmartTranslator的技术架构设计，应随系统演进持续更新，为开发团队提供架构指导和技术决策参考。
