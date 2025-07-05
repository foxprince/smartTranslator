# SmartTranslator - 智能翻译系统

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green.svg)
![React](https://img.shields.io/badge/react-18.0+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 项目概述

SmartTranslator是一个企业级智能翻译系统，支持多种翻译服务提供商、实时质量评估、成本控制和协作翻译等功能。系统采用现代化的前后端分离架构，提供了完整的Web管理界面和RESTful API。

## ✨ 核心特性

### 🔧 翻译引擎
- **多提供商支持**: 集成Google Translate和OpenAI GPT
- **智能缓存**: Redis + LRU算法，支持TTL管理
- **质量评估**: 多维度翻译质量评分系统
- **成本控制**: 预算管理和使用统计
- **批量处理**: 高效的批量翻译功能

### 🎯 文本预处理
- **编码检测**: 自动识别文本编码格式
- **格式标准化**: 智能段落合并和空行处理
- **章节识别**: 自动识别文档结构
- **质量检测**: 识别文本格式问题

### 🖥️ 管理界面
- **现代化设计**: 基于Ant Design的响应式界面
- **实时监控**: 系统状态和性能指标监控
- **成本分析**: 详细的成本统计和趋势分析
- **质量管理**: 翻译质量评估和优化建议

### 🤝 协作功能
- **实时协作**: WebSocket支持的实时编辑
- **双语对照**: 原文和译文对照编辑
- **版本控制**: 翻译历史记录和回滚
- **权限管理**: 多用户协作权限控制

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        智能翻译系统架构                      │
├─────────────────────────────────────────────────────────────┤
│  前端层           │  React + TypeScript + Ant Design      │
├─────────────────────────────────────────────────────────────┤
│  API层            │  FastAPI + Pydantic + OpenAPI         │
├─────────────────────────────────────────────────────────────┤
│  业务逻辑层       │  翻译引擎 + 质量评估 + 成本控制        │
├─────────────────────────────────────────────────────────────┤
│  提供商层         │  Google Translate + OpenAI GPT        │
├─────────────────────────────────────────────────────────────┤
│  缓存层           │  Redis + LRU算法 + TTL管理             │
├─────────────────────────────────────────────────────────────┤
│  数据层           │  PostgreSQL + 索引优化                 │
├─────────────────────────────────────────────────────────────┤
│  基础设施层       │  Docker + Nginx + 监控 + 日志          │
└─────────────────────────────────────────────────────────────┘
```

## 📁 项目结构

```
smartTranslator/
├── backend/                    # 后端服务
│   ├── app/                   # 核心应用代码
│   │   ├── api/              # API路由
│   │   ├── core/             # 核心配置
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # Pydantic模式
│   │   ├── services/         # 业务服务
│   │   ├── providers/        # 翻译提供商
│   │   └── utils/            # 工具函数
│   ├── tests/                # 测试代码
│   ├── scripts/              # 运维脚本
│   ├── docker-compose.yml    # 容器编排
│   └── requirements.txt      # Python依赖
├── frontend/                  # 前端应用
│   ├── src/                  # 源代码
│   │   ├── components/       # React组件
│   │   ├── pages/           # 页面组件
│   │   ├── services/        # API服务
│   │   ├── store/           # 状态管理
│   │   └── types/           # 类型定义
│   ├── public/              # 静态资源
│   └── package.json         # 前端依赖
├── docs/                     # 项目文档
│   ├── product/             # 产品需求文档
│   └── development/         # 开发指南
├── sample/                   # 示例文件
└── .github/                  # GitHub Actions
    └── workflows/           # CI/CD工作流
```

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 16.0+
- PostgreSQL 13+
- Redis 6.0+
- Docker (可选)

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置数据库和API密钥

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install --legacy-peer-deps

# 启动开发服务器
npm start
```

### Docker部署

```bash
# 使用Docker Compose启动所有服务
cd backend
docker-compose up -d

# 访问应用
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
# 前端应用: http://localhost:3000
```

## 📊 功能模块

### 1. 文档管理
- 文档上传和预处理
- 格式检测和标准化
- 批量文档处理

### 2. 翻译管理
- 多提供商翻译服务
- 实时翻译任务监控
- 翻译历史记录

### 3. 缓存管理
- 智能缓存策略
- 缓存统计和监控
- 手动缓存清理

### 4. 成本控制
- 预算设置和监控
- 成本分析和优化
- 详细的使用报告

### 5. 质量分析
- 翻译质量评估
- 质量趋势分析
- 改进建议

### 6. 系统监控
- 实时性能监控
- 告警和通知
- 系统健康检查

## 🧪 测试

### 后端测试
```bash
cd backend

# 运行所有测试
make test

# 运行单元测试
make test-unit

# 运行集成测试
make test-integration

# 测试覆盖率
make coverage
```

### 前端测试
```bash
cd frontend

# 运行测试
npm test

# 测试覆盖率
npm run test:coverage
```

## 📈 性能指标

- **API响应时间**: < 2秒
- **翻译准确率**: > 90%
- **缓存命中率**: > 80%
- **系统可用性**: > 99.9%

## 🔧 配置说明

### 后端配置
主要配置文件：`backend/app/core/config.py`

```python
# 数据库配置
DATABASE_URL = "postgresql://user:password@localhost/db"

# Redis配置
REDIS_URL = "redis://localhost:6379"

# API密钥
GOOGLE_TRANSLATE_API_KEY = "your-google-api-key"
OPENAI_API_KEY = "your-openai-api-key"
```

### 前端配置
环境变量配置：`frontend/.env`

```bash
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_TITLE=智能翻译系统
REACT_APP_VERSION=1.0.0
```

## 🛠️ 开发指南

### 代码规范
- 后端遵循PEP 8代码规范
- 前端使用ESLint和Prettier
- 使用TypeScript进行类型检查
- 100%的测试覆盖率目标

### 提交规范
```bash
feat: 新功能
fix: 错误修复
docs: 文档更新
style: 代码格式化
refactor: 代码重构
test: 测试相关
chore: 构建工具或辅助工具的变动
```

## 📄 API文档

启动后端服务后，可以访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📜 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [产品需求文档](docs/product/prd/v1.0/)
- [开发指南](docs/development/development-guidelines.md)
- [API文档](http://localhost:8000/docs)

## 📞 联系我们

如有问题或建议，请通过以下方式联系：

- 创建 [Issue](https://github.com/your-username/smartTranslator/issues)
- 邮件：support@smarttranslator.com

---

**SmartTranslator** - 让翻译更智能，让协作更高效！ 🚀