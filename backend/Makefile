# 翻译系统 Makefile
# 提供常用的开发和测试命令

.PHONY: help install test test-unit test-integration test-api test-coverage test-fast clean lint format check-deps run dev

# 默认目标
help:
	@echo "翻译系统开发工具"
	@echo ""
	@echo "可用命令:"
	@echo "  install        - 安装依赖"
	@echo "  test           - 运行所有测试"
	@echo "  test-unit      - 运行单元测试"
	@echo "  test-integration - 运行集成测试"
	@echo "  test-api       - 运行API测试"
	@echo "  test-coverage  - 运行测试并生成覆盖率报告"
	@echo "  test-fast      - 快速测试（跳过慢速测试）"
	@echo "  lint           - 代码风格检查"
	@echo "  format         - 代码格式化"
	@echo "  check-deps     - 检查依赖"
	@echo "  clean          - 清理临时文件"
	@echo "  run            - 运行开发服务器"
	@echo "  dev            - 开发模式（自动重载）"

# 安装依赖
install:
	@echo "📦 安装Python依赖..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# 检查依赖
check-deps:
	@echo "🔍 检查依赖..."
	pip check
	@echo "✅ 依赖检查完成"

# 运行所有测试
test:
	@echo "🧪 运行所有测试..."
	python run_tests.py --type all

# 运行单元测试
test-unit:
	@echo "🧪 运行单元测试..."
	python run_tests.py --type unit

# 运行集成测试
test-integration:
	@echo "🧪 运行集成测试..."
	python run_tests.py --type integration

# 运行API测试
test-api:
	@echo "🧪 运行API测试..."
	python run_tests.py --type api

# 运行测试并生成覆盖率报告
test-coverage:
	@echo "🧪 运行测试并生成覆盖率报告..."
	python run_tests.py --coverage --report

# 快速测试
test-fast:
	@echo "🧪 运行快速测试..."
	python run_tests.py --fast

# 并行测试
test-parallel:
	@echo "🧪 运行并行测试..."
	python run_tests.py --parallel 4

# 代码风格检查
lint:
	@echo "🔍 代码风格检查..."
	flake8 app/ --max-line-length=100 --ignore=E203,W503
	@echo "🔍 类型检查..."
	mypy app/ --ignore-missing-imports
	@echo "✅ 代码检查完成"

# 代码格式化
format:
	@echo "🎨 代码格式化..."
	black app/ tests/ --line-length=100
	isort app/ tests/ --profile black
	@echo "✅ 代码格式化完成"

# 安全检查
security:
	@echo "🔒 安全检查..."
	bandit -r app/ -f json -o reports/security_report.json || true
	safety check --json --output reports/safety_report.json || true
	@echo "✅ 安全检查完成"

# 清理临时文件
clean:
	@echo "🧹 清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf reports/
	rm -rf .coverage
	@echo "✅ 清理完成"

# 运行开发服务器
run:
	@echo "🚀 启动开发服务器..."
	uvicorn app.main:app --host 0.0.0.0 --port 8000

# 开发模式（自动重载）
dev:
	@echo "🚀 启动开发服务器（自动重载）..."
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
prod:
	@echo "🚀 启动生产服务器..."
	gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 数据库迁移
migrate:
	@echo "🗄️ 运行数据库迁移..."
	alembic upgrade head

# 创建新迁移
migration:
	@echo "🗄️ 创建新迁移..."
	@read -p "迁移描述: " desc; \
	alembic revision --autogenerate -m "$$desc"

# 重置数据库
reset-db:
	@echo "🗄️ 重置数据库..."
	alembic downgrade base
	alembic upgrade head

# 生成API文档
docs:
	@echo "📚 生成API文档..."
	python -c "import app.main; print('API文档: http://localhost:8000/docs')"

# 构建Docker镜像
docker-build:
	@echo "🐳 构建Docker镜像..."
	docker build -t translation-backend .

# 运行Docker容器
docker-run:
	@echo "🐳 运行Docker容器..."
	docker run -p 8000:8000 translation-backend

# 完整的CI检查
ci: clean install lint test-coverage security
	@echo "✅ CI检查完成"

# 发布前检查
pre-release: clean install lint test-coverage security docs
	@echo "🚀 发布前检查完成"

# 性能测试
perf:
	@echo "⚡ 运行性能测试..."
	locust -f tests/performance/locustfile.py --host=http://localhost:8000

# 监控服务状态
health:
	@echo "💓 检查服务健康状态..."
	curl -f http://localhost:8000/health || echo "服务未运行"

# 查看日志
logs:
	@echo "📋 查看应用日志..."
	tail -f logs/app.log

# 备份数据库
backup:
	@echo "💾 备份数据库..."
	pg_dump translation_db > backups/db_backup_$(shell date +%Y%m%d_%H%M%S).sql

# 恢复数据库
restore:
	@echo "🔄 恢复数据库..."
	@read -p "备份文件路径: " file; \
	psql translation_db < "$$file"

# 环境信息
env-info:
	@echo "🔧 环境信息:"
	@echo "Python版本: $(shell python --version)"
	@echo "Pip版本: $(shell pip --version)"
	@echo "当前目录: $(shell pwd)"
	@echo "Git分支: $(shell git branch --show-current 2>/dev/null || echo 'N/A')"
	@echo "Git提交: $(shell git rev-parse --short HEAD 2>/dev/null || echo 'N/A')"
