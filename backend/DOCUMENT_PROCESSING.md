# 文档处理系统

## 📄 功能概述

文档处理系统是翻译系统的重要组成部分，支持多种文档格式的上传、文本提取、翻译和下载。

## 🎯 主要功能

### ✅ 文档上传
- **多格式支持**: 支持20+种文档格式
- **大文件处理**: 支持最大50MB文件上传
- **格式验证**: 自动验证文件格式和大小
- **安全检查**: 文件类型和内容安全检查

### ✅ 文本提取
- **智能识别**: 根据文件类型自动选择提取方法
- **OCR支持**: 图像文档的文字识别
- **结构保持**: 尽可能保持原文档结构
- **批量处理**: 支持批量文本提取

### ✅ 文档翻译
- **多语言支持**: 支持100+种语言互译
- **分块处理**: 长文档智能分块翻译
- **质量评估**: 翻译质量实时评估
- **格式保持**: 保持原文档格式

### ✅ 文档管理
- **版本控制**: 原文档和翻译文档版本管理
- **批量操作**: 批量上传、翻译、下载
- **搜索过滤**: 多维度文档搜索和过滤
- **权限控制**: 用户权限和文档访问控制

## 📁 支持的文档格式

### 文本文档
- `.txt` - 纯文本文件
- `.md` - Markdown文档
- `.rtf` - 富文本格式

### Office文档
- `.doc/.docx` - Microsoft Word文档
- `.xls/.xlsx` - Microsoft Excel表格
- `.ppt/.pptx` - Microsoft PowerPoint演示文稿

### PDF文档
- `.pdf` - PDF文档（支持文本提取和OCR）

### 网页文档
- `.html/.htm` - HTML网页文档
- `.xml` - XML结构化文档

### 数据格式
- `.json` - JSON数据文件
- `.csv` - CSV表格数据

### 图像文档（OCR）
- `.jpg/.jpeg` - JPEG图像
- `.png` - PNG图像
- `.bmp` - BMP位图
- `.tiff` - TIFF图像
- `.gif` - GIF图像

## 🏗️ 系统架构

```
文档处理系统架构
├── 上传层          │  文件上传和验证
├── 存储层          │  文件存储和管理
├── 提取层          │  文本内容提取
├── 翻译层          │  文档翻译处理
├── 缓存层          │  处理结果缓存
└── API层           │  RESTful API接口
```

## 🔧 核心组件

### DocumentProcessor
文档处理核心服务，负责：
- 文档上传和存储
- 文本内容提取
- 文档翻译处理
- 文件格式转换

### 文本提取器
针对不同格式的专用提取器：
- `PDFExtractor` - PDF文档提取
- `WordExtractor` - Word文档提取
- `ExcelExtractor` - Excel表格提取
- `OCRExtractor` - 图像OCR提取
- `HTMLExtractor` - HTML文档提取

### 翻译引擎集成
与现有翻译引擎无缝集成：
- 支持Google Translate和OpenAI GPT
- 智能分块和批量处理
- 质量评估和成本控制

## 📊 API接口

### 文档上传
```http
POST /api/document/upload
Content-Type: multipart/form-data

{
  "file": <文件数据>,
  "project_id": "项目ID",
  "tags": ["标签1", "标签2"]
}
```

### 文本提取
```http
POST /api/document/extract-text/{document_id}

Response:
{
  "document_id": "文档ID",
  "extracted_text": "提取的文本内容",
  "text_length": 5000,
  "extraction_method": "pdf",
  "processing_time": 2.5
}
```

### 文档翻译
```http
POST /api/document/translate

{
  "document_id": "文档ID",
  "source_language": "en",
  "target_language": "zh",
  "provider": "google",
  "chunk_size": 1000
}
```

### 文档下载
```http
GET /api/document/{document_id}/download?file_type=translated

Response: 文件流
```

### 批量操作
```http
POST /api/document/batch-translate

{
  "document_ids": ["id1", "id2", "id3"],
  "source_language": "en",
  "target_language": "zh",
  "provider": "google"
}
```

## 🚀 使用示例

### Python客户端示例
```python
import requests

# 上传文档
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/document/upload',
        files={'file': f},
        data={'project_id': 'my-project'}
    )
    document_id = response.json()['document_id']

# 翻译文档
translate_response = requests.post(
    'http://localhost:8000/api/document/translate',
    json={
        'document_id': document_id,
        'source_language': 'en',
        'target_language': 'zh',
        'provider': 'google'
    }
)

# 下载翻译结果
download_response = requests.get(
    f'http://localhost:8000/api/document/{document_id}/download',
    params={'file_type': 'translated'}
)
```

### JavaScript客户端示例
```javascript
// 上传文档
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('project_id', 'my-project');

const uploadResponse = await fetch('/api/document/upload', {
  method: 'POST',
  body: formData
});
const { document_id } = await uploadResponse.json();

// 翻译文档
const translateResponse = await fetch('/api/document/translate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    document_id,
    source_language: 'en',
    target_language: 'zh',
    provider: 'google'
  })
});
```

## ⚙️ 配置说明

### 环境变量
```bash
# 文档存储配置
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=52428800  # 50MB

# OCR配置
TESSERACT_CMD=/usr/bin/tesseract
OCR_LANGUAGES=chi_sim+eng

# 处理限制
MAX_BATCH_SIZE=50
PROCESSING_TIMEOUT=300  # 5分钟
```

### 依赖安装
```bash
# 安装文档处理依赖
pip install -r requirements-document.txt

# 安装Tesseract OCR
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# macOS
brew install tesseract tesseract-lang

# Windows
# 下载并安装 https://github.com/UB-Mannheim/tesseract/wiki
```

## 📈 性能优化

### 处理性能
- **并发处理**: 使用线程池并发处理多个文档
- **内存优化**: 大文件分块处理，避免内存溢出
- **缓存机制**: 提取结果缓存，避免重复处理
- **异步处理**: 长时间任务异步后台处理

### 存储优化
- **文件压缩**: 自动压缩存储文件
- **清理机制**: 定期清理临时文件
- **分层存储**: 热数据和冷数据分层存储
- **备份策略**: 重要文档自动备份

## 🔒 安全考虑

### 文件安全
- **格式验证**: 严格的文件格式验证
- **大小限制**: 文件大小和数量限制
- **病毒扫描**: 集成病毒扫描引擎
- **内容过滤**: 敏感内容检测和过滤

### 访问控制
- **用户权限**: 基于用户的文档访问控制
- **项目隔离**: 项目级别的文档隔离
- **审计日志**: 完整的操作审计日志
- **数据加密**: 敏感文档加密存储

## 🧪 测试

### 单元测试
```bash
# 运行文档处理测试
pytest tests/test_document_processor.py -v

# 测试特定格式
pytest tests/test_document_processor.py::test_pdf_extraction -v
```

### 集成测试
```bash
# 运行API集成测试
pytest tests/test_document_api.py -v

# 端到端测试
pytest tests/test_document_e2e.py -v
```

### 性能测试
```bash
# 批量文档处理性能测试
python tests/performance/test_batch_processing.py

# 大文件处理测试
python tests/performance/test_large_files.py
```

## 📊 监控指标

### 处理指标
- 文档上传成功率
- 文本提取成功率
- 翻译完成率
- 平均处理时间

### 系统指标
- 存储空间使用率
- 处理队列长度
- 内存使用情况
- CPU使用率

### 质量指标
- 文本提取准确率
- OCR识别准确率
- 翻译质量评分
- 用户满意度

## 🔮 未来规划

### 短期目标 (1-2个月)
- [ ] 支持更多文档格式（.epub, .mobi等）
- [ ] 增强OCR识别准确率
- [ ] 优化大文件处理性能
- [ ] 添加文档预览功能

### 中期目标 (3-6个月)
- [ ] 智能文档分类和标签
- [ ] 文档版本控制系统
- [ ] 协作编辑功能
- [ ] 文档模板系统

### 长期目标 (6-12个月)
- [ ] AI驱动的文档理解
- [ ] 多模态文档处理
- [ ] 实时协作翻译
- [ ] 智能文档推荐

## 🚨 常见问题

### Q: 支持哪些OCR语言？
A: 默认支持中文和英文，可通过配置添加更多语言支持。

### Q: 如何处理大文件？
A: 系统自动将大文件分块处理，避免内存溢出。

### Q: 翻译质量如何保证？
A: 集成了多维度质量评估算法，实时评估翻译质量。

### Q: 如何批量处理文档？
A: 支持批量上传、提取和翻译，提供批量操作API。

### Q: 文档安全如何保障？
A: 多层安全机制，包括格式验证、权限控制、审计日志等。

---

## 🎉 总结

文档处理系统作为翻译系统的重要补充，提供了完整的文档处理解决方案。通过支持多种格式、智能文本提取、高质量翻译和便捷的管理界面，大大提升了用户的文档翻译体验。

基于我们之前完成的Story 2机器翻译集成，文档处理系统完美地扩展了翻译能力，使系统能够处理各种实际的文档翻译需求！ 🚀
