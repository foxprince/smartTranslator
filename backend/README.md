# Strands AI翻译工具 - 后端服务

## 项目概述

Strands AI翻译工具后端服务，实现了文本预处理系统，支持txt文件的格式检查、清理和标准化处理。

## 功能特性

### 文本预处理功能
- ✅ 自动编码检测（UTF-8, GBK等）
- ✅ 文本统计分析（行数、空行、平均长度等）
- ✅ 格式问题检测（短行、长行、对话合并等）
- ✅ 自动格式标准化（空行清理、段落合并）
- ✅ 章节结构识别（中英文章节标题）
- ✅ 详细处理报告生成

### API接口
- ✅ RESTful API设计
- ✅ 完整的错误处理
- ✅ 请求验证和安全检查
- ✅ 健康检查端点

## 技术栈

- **框架**: FastAPI 0.104.1
- **Python**: 3.11+
- **数据验证**: Pydantic 2.5.0
- **编码检测**: chardet 5.2.0
- **测试**: pytest + httpx

## 项目结构

```
backend/
├── app/
│   ├── api/v1/endpoints/    # API端点
│   ├── schemas/             # Pydantic数据模式
│   ├── services/            # 业务逻辑服务
│   ├── utils/               # 工具函数
│   └── main.py             # 应用入口
├── tests/                   # 测试文件
├── requirements.txt         # 依赖管理
└── README.md               # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

### 3. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API接口

### 文档预处理

**POST** `/api/v1/documents/preprocess`

请求体：
```json
{
    "file_content": "文件内容",
    "filename": "test.txt",
    "encoding": "utf-8"  // 可选
}
```

响应：
```json
{
    "success": true,
    "data": {
        "cleaned_content": "清理后的内容",
        "processing_report": {
            "original_stats": {...},
            "cleaned_stats": {...},
            "issues_found": [...],
            "processing_time": 0.123,
            "changes_made": [...]
        }
    },
    "message": "文档预处理成功",
    "code": 200
}
```

### 健康检查

**GET** `/health` - 应用健康检查
**GET** `/api/v1/documents/health` - 文档服务健康检查

## 测试

### 运行所有测试

```bash
pytest tests/ -v
```

### 测试覆盖率

```bash
pytest tests/ --cov=app --cov-report=html
```

### 手动API测试

```bash
python test_api_manual.py
```

## 性能指标

- 处理10KB文本文件 < 1秒
- 处理100KB文本文件 < 5秒
- 内存使用 < 50MB per request
- 支持并发处理 >= 10个请求

## 安全特性

- 文件大小限制（最大10MB）
- 文件类型验证（仅支持.txt）
- 内容安全扫描
- 统一错误处理

## 开发指南

### 代码规范
- 遵循PEP 8代码风格
- 使用类型注解
- 完善的文档字符串
- 单元测试覆盖率 > 80%

### 添加新功能
1. 在`schemas/`中定义数据模式
2. 在`services/`中实现业务逻辑
3. 在`api/v1/endpoints/`中添加API端点
4. 在`tests/`中编写测试用例

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t strands-backend .

# 运行容器
docker run -p 8000:8000 strands-backend
```

### 生产环境

```bash
# 使用gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 故事完成状态

✅ **故事9: 文本预处理系统** - 已完成

**验收标准完成情况**：
- [✅] AC-1: 自动检测txt文件编码格式
- [✅] AC-2: 统计和分析文本基本信息
- [✅] AC-3: 识别和移除多余空行
- [✅] AC-4: 检测并合并错误分割段落
- [✅] AC-5: 识别过短行和过长行
- [✅] AC-6: 自动检测章节结构
- [✅] AC-7: 生成标准化清洁文本
- [✅] AC-8: 提供详细处理报告

**测试结果**：
- 单元测试: 24/24 通过 ✅
- 集成测试: 7/7 通过 ✅
- API测试: 7/7 通过 ✅

## 下一步

基于当前实现的文本预处理系统，可以继续开发：
- 故事1: 文档上传功能
- 故事2: 机器翻译集成
- 故事3: 双语编辑界面

## 联系信息

- 项目文档: `docs/product/prd/v1.0/stories/story-9-text-preprocessing-system.md`
- 开发指南: `docs/development/development-guidelines.md`
