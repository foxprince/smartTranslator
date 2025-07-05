# 翻译系统测试指南

本文档介绍如何运行和管理翻译系统的测试套件。

## 📁 测试结构

```
tests/
├── conftest.py                 # 测试配置和fixtures
├── test_translation_engine.py  # 翻译引擎单元测试
├── test_translation_api.py     # API集成测试
├── performance/
│   └── locustfile.py           # 性能测试
└── README.md                   # 本文档
```

## 🚀 快速开始

### 1. 安装测试依赖

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 或使用Makefile
make install
```

### 2. 运行所有测试

```bash
# 使用测试脚本
python run_tests.py

# 或使用Makefile
make test

# 或直接使用pytest
pytest tests/
```

## 🧪 测试类型

### 单元测试

测试单个组件的功能，使用模拟对象隔离依赖。

```bash
# 运行单元测试
python run_tests.py --type unit
make test-unit

# 运行特定测试文件
python run_tests.py --file test_translation_engine.py

# 运行特定测试函数
python run_tests.py --test test_translate_batch_success
```

### 集成测试

测试多个组件之间的交互。

```bash
# 运行集成测试
python run_tests.py --type integration
make test-integration
```

### API测试

测试REST API端点的功能。

```bash
# 运行API测试
python run_tests.py --type api
make test-api
```

## 📊 覆盖率报告

生成代码覆盖率报告：

```bash
# 生成覆盖率报告
python run_tests.py --coverage
make test-coverage

# 查看HTML报告
open htmlcov/index.html
```

覆盖率目标：
- 总体覆盖率：≥ 80%
- 核心业务逻辑：≥ 90%
- API端点：≥ 85%

## ⚡ 性能测试

使用Locust进行负载测试：

```bash
# 启动应用服务器
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 运行性能测试
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# 或使用Makefile
make perf
```

性能测试场景：
- **TranslationUser**: 模拟普通用户的翻译请求
- **AdminUser**: 模拟管理员操作
- **StressTestUser**: 高频率压力测试

## 🔧 测试配置

### 环境变量

测试需要以下环境变量：

```bash
# 数据库
DATABASE_URL=postgresql://user:pass@localhost:5432/test_db

# Redis缓存
REDIS_URL=redis://localhost:6379

# API密钥（可选，用于真实API测试）
GOOGLE_TRANSLATE_API_KEY=your_google_key
OPENAI_API_KEY=your_openai_key

# 测试标志
TESTING=true
```

### pytest配置

主要配置在 `pytest.ini` 中：

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --tb=short --cov=app --cov-report=html
markers = 
    slow: 慢速测试
    integration: 集成测试
    unit: 单元测试
```

## 🏷️ 测试标记

使用pytest标记来分类测试：

```python
@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration
def test_integration_function():
    pass

@pytest.mark.slow
def test_slow_function():
    pass
```

运行特定标记的测试：

```bash
# 只运行单元测试
pytest -m unit

# 跳过慢速测试
pytest -m "not slow"

# 运行单元测试但跳过慢速测试
pytest -m "unit and not slow"
```

## 🔍 调试测试

### 详细输出

```bash
# 详细输出
python run_tests.py --verbose

# 显示所有输出（包括print语句）
pytest -s tests/

# 在第一个失败时停止
pytest -x tests/
```

### 调试特定测试

```bash
# 运行特定测试并进入调试器
pytest --pdb tests/test_translation_engine.py::TestTranslationEngine::test_translate_batch_success

# 使用ipdb调试器
pytest --pdbcls=IPython.terminal.debugger:Pdb tests/
```

## 📈 持续集成

### GitHub Actions

项目配置了GitHub Actions工作流：

- **测试矩阵**: Python 3.9, 3.10, 3.11
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **检查项目**: 
  - 代码风格检查
  - 类型检查
  - 单元测试
  - 集成测试
  - 安全扫描
  - 性能测试

### 本地CI检查

运行完整的CI检查：

```bash
make ci
```

这将执行：
1. 清理临时文件
2. 安装依赖
3. 代码风格检查
4. 运行测试并生成覆盖率报告
5. 安全扫描

## 🛠️ 测试工具

### 主要工具

- **pytest**: 测试框架
- **pytest-asyncio**: 异步测试支持
- **pytest-cov**: 覆盖率报告
- **httpx**: HTTP客户端测试
- **locust**: 性能测试

### 代码质量工具

- **flake8**: 代码风格检查
- **black**: 代码格式化
- **mypy**: 类型检查
- **bandit**: 安全扫描

## 📝 编写测试

### 测试命名规范

```python
class TestTranslationEngine:
    def test_translate_batch_success(self):
        """测试批量翻译成功场景"""
        pass
    
    def test_translate_batch_failure(self):
        """测试批量翻译失败场景"""
        pass
    
    def test_translate_batch_empty_input(self):
        """测试空输入的边界情况"""
        pass
```

### 使用Fixtures

```python
def test_translation_with_cache(translation_engine, sample_translation_request):
    """使用fixtures进行测试"""
    result = await translation_engine.translate_batch(sample_translation_request)
    assert result.success_count > 0
```

### 模拟外部依赖

```python
@patch('app.providers.google_translate.GoogleTranslateProvider')
async def test_with_mock_provider(mock_provider):
    """使用模拟对象测试"""
    mock_provider.translate_batch.return_value = mock_translations
    # 测试逻辑
```

## 🚨 常见问题

### 测试失败排查

1. **数据库连接失败**
   ```bash
   # 检查数据库服务
   pg_isready -h localhost -p 5432
   
   # 检查环境变量
   echo $DATABASE_URL
   ```

2. **Redis连接失败**
   ```bash
   # 检查Redis服务
   redis-cli ping
   
   # 检查环境变量
   echo $REDIS_URL
   ```

3. **API密钥问题**
   ```bash
   # 检查API密钥设置
   echo $GOOGLE_TRANSLATE_API_KEY
   echo $OPENAI_API_KEY
   ```

### 性能问题

1. **测试运行缓慢**
   ```bash
   # 使用并行测试
   python run_tests.py --parallel 4
   
   # 跳过慢速测试
   python run_tests.py --fast
   ```

2. **内存使用过高**
   ```bash
   # 监控内存使用
   pytest --memray tests/
   ```

## 📚 最佳实践

### 测试设计原则

1. **独立性**: 每个测试应该独立运行
2. **可重复性**: 测试结果应该一致
3. **快速性**: 单元测试应该快速执行
4. **清晰性**: 测试意图应该明确

### 测试数据管理

1. **使用Fixtures**: 共享测试数据
2. **工厂模式**: 动态生成测试数据
3. **清理机制**: 测试后清理数据

### 异步测试

```python
@pytest.mark.asyncio
async def test_async_function():
    """异步函数测试"""
    result = await async_function()
    assert result is not None
```

## 🔄 测试维护

### 定期任务

1. **更新依赖**: 定期更新测试依赖
2. **清理测试**: 删除过时的测试
3. **优化性能**: 优化慢速测试
4. **增加覆盖率**: 为新功能添加测试

### 监控指标

- 测试通过率
- 代码覆盖率
- 测试执行时间
- 失败测试趋势

---

## 📞 获取帮助

如果遇到测试相关问题：

1. 查看测试日志和错误信息
2. 检查环境配置
3. 参考本文档的常见问题部分
4. 在项目仓库提交Issue

**记住**: 好的测试是高质量软件的基础！ 🎯
