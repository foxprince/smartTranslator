# 🚀 SmartTranslator 快速启动指南

## 启动服务

```bash
cd /Users/zj/git/smartTranslator/backend
source venv/bin/activate
export OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d '=' -f2)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 测试翻译

```bash
# 单个翻译
curl -s --max-time 30 -X POST "http://localhost:8000/api/v1/translation/translate" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Hello world"], "source_language": "en", "target_language": "zh", "provider": "openai"}' \
  | python -m json.tool

# 批量翻译
curl -s --max-time 60 -X POST "http://localhost:8000/api/v1/translation/translate" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Hello", "Good morning", "Thank you"], "source_language": "en", "target_language": "zh", "provider": "openai"}' \
  | python -m json.tool
```

## API文档

- 服务地址: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 功能特性

- ✅ OpenAI高质量翻译 (gpt-4o-mini-2024-07-18)
- ✅ 批量翻译支持
- ✅ 实时成本跟踪
- ✅ 质量评估
- ✅ 缓存机制
