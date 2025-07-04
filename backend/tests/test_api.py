"""
API接口集成测试
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestDocumentAPI:
    """测试文档处理API"""
    
    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_document_health_check(self):
        """测试文档服务健康检查"""
        response = client.get("/api/v1/documents/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["service"] == "document-processor"
    
    def test_preprocess_document_success(self):
        """测试文档预处理成功"""
        request_data = {
            "file_content": "第一行内容\n\n第二行内容\n短行\n这是一个正常长度的行",
            "filename": "test.txt"
        }
        
        response = client.post("/api/v1/documents/preprocess", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["code"] == 200
        assert "data" in data
        assert "cleaned_content" in data["data"]
        assert "processing_report" in data["data"]
        
        # 检查处理报告
        report = data["data"]["processing_report"]
        assert "original_stats" in report
        assert "cleaned_stats" in report
        assert "processing_time" in report
        assert "changes_made" in report
    
    def test_preprocess_document_invalid_format(self):
        """测试无效文件格式"""
        request_data = {
            "file_content": "测试内容",
            "filename": "test.doc"  # 不支持的格式
        }
        
        response = client.post("/api/v1/documents/preprocess", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "不支持的文件格式" in data["detail"]["error"]
    
    def test_preprocess_document_empty_filename(self):
        """测试空文件名"""
        request_data = {
            "file_content": "测试内容",
            "filename": ""
        }
        
        response = client.post("/api/v1/documents/preprocess", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "文件名不能为空" in data["detail"]["error"]
    
    def test_preprocess_document_with_encoding(self):
        """测试指定编码的文档预处理"""
        request_data = {
            "file_content": "测试中文内容\n第二行内容",
            "filename": "test.txt",
            "encoding": "utf-8"
        }
        
        response = client.post("/api/v1/documents/preprocess", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        report = data["data"]["processing_report"]
        assert report["original_stats"]["encoding"] == "utf-8"
    
    def test_preprocess_complex_document(self):
        """测试复杂文档预处理"""
        # 创建包含各种格式问题的复杂文档
        complex_content = """第一章 测试文档

这是第一段正常内容。这段内容有适当的长度。

短

这是一个超级超级超级长的行内容""" + "非常长的内容" * 15 + """

"第一个对话内容""第二个对话内容"

第二章 另一个章节

这里是第二章的内容。



多个空行上面。

结束。
"""
        
        request_data = {
            "file_content": complex_content,
            "filename": "complex_test.txt"
        }
        
        response = client.post("/api/v1/documents/preprocess", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        
        # 检查是否检测到各种问题
        issues = data["data"]["processing_report"]["issues_found"]
        issue_types = [issue["issue_type"] for issue in issues]
        
        assert "short_line" in issue_types
        assert "long_line" in issue_types
        assert "dialogue_merge" in issue_types
        
        # 检查是否有修改摘要
        changes = data["data"]["processing_report"]["changes_made"]
        assert len(changes) > 0
        
        # 检查清理后的内容
        cleaned_content = data["data"]["cleaned_content"]
        assert len(cleaned_content) > 0
        assert "第一章" in cleaned_content
        assert "第二章" in cleaned_content
