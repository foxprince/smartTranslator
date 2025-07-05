# 贡献指南

感谢您对 SmartTranslator 项目的兴趣！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题
- 使用 GitHub Issues 报告 bug
- 提供详细的复现步骤
- 包含系统环境信息
- 添加相关的错误日志

### 功能建议
- 在 Issues 中提出功能需求
- 描述使用场景和预期效果
- 讨论实现方案的可行性

### 代码贡献
1. Fork 项目到您的账户
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 编写代码和相应的测试
4. 确保所有测试通过
5. 提交代码 (`git commit -m 'Add amazing feature'`)
6. 推送到分支 (`git push origin feature/amazing-feature`)
7. 创建 Pull Request

## 📋 开发规范

### 后端代码规范
- 遵循 PEP 8 Python 代码风格
- 使用类型注解 (Type Hints)
- 编写完整的文档字符串
- 单元测试覆盖率 > 80%
- 使用 `black` 进行代码格式化
- 使用 `flake8` 进行代码检查

### 前端代码规范
- 使用 ESLint 和 Prettier
- 遵循 React 最佳实践
- 编写完整的 TypeScript 类型定义
- 组件需要有 PropTypes 或 TypeScript 接口
- 使用 Hooks 而非 Class 组件

### 提交信息规范
使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**类型说明：**
- `feat`: 新功能
- `fix`: 错误修复
- `docs`: 文档更新
- `style`: 代码格式化（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建工具或辅助工具的变动
- `perf`: 性能优化

**示例：**
```
feat(translation): 添加 OpenAI GPT 翻译支持

- 集成 OpenAI API
- 添加配置选项
- 更新测试用例

Closes #123
```

## 🏗️ 开发环境设置

### 后端开发
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 前端开发
```bash
cd frontend
npm install --legacy-peer-deps
npm start
```

### 数据库设置
```bash
# 启动 PostgreSQL 和 Redis
docker-compose up -d postgres redis

# 运行数据库迁移
cd backend
alembic upgrade head
```

## 🧪 测试

### 运行后端测试
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

### 运行前端测试
```bash
cd frontend
npm test
npm run test:coverage
```

## 📖 文档

### 更新文档
- API 文档会自动生成，访问 `/docs`
- 更新 README.md 中的功能说明
- 在 `docs/` 目录下添加详细文档

### 代码注释
- 重要的业务逻辑需要注释
- 复杂的算法需要详细说明
- API 接口需要完整的文档字符串

## 🔒 安全

### 报告安全问题
- 不要在公开的 Issue 中报告安全漏洞
- 发送邮件到 security@smarttranslator.com
- 我们会在 24 小时内回复

### 安全最佳实践
- 不要在代码中硬编码敏感信息
- 使用环境变量存储配置
- 定期更新依赖包

## 🎯 Pull Request 检查清单

在提交 PR 之前，请确保：

- [ ] 代码符合项目的编码规范
- [ ] 所有测试都通过
- [ ] 添加了新功能的测试用例
- [ ] 更新了相关文档
- [ ] 提交信息符合规范
- [ ] 没有合并冲突
- [ ] 已经在本地充分测试

## 📞 获取帮助

如果您在贡献过程中遇到任何问题，可以通过以下方式获取帮助：

- 创建 GitHub Issue
- 在 Pull Request 中留言
- 发送邮件到 support@smarttranslator.com

## 🙏 感谢

感谢所有为 SmartTranslator 项目做出贡献的开发者们！

您的贡献让这个项目变得更好！ 🚀