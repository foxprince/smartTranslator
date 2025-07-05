"""
协作API集成测试
"""
import pytest
import json
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestCollaborationAPI:
    """测试协作API"""
    
    def test_collaboration_health_check(self):
        """测试协作服务健康检查"""
        response = client.get("/api/v1/collaboration/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["service"] == "collaboration-service"
        assert "active_sessions" in data
        assert "active_connections" in data
    
    def test_create_collaboration_session_success(self):
        """测试创建协作会话成功"""
        request_data = {
            "document_id": "doc-test-123",
            "en_content": ["Hello world", "This is a test", "End of document"],
            "cn_content": ["你好世界", "这是一个测试", "文档结束"],
            "metadata": {
                "title": "测试文档",
                "author": "测试作者",
                "description": "测试描述",
                "language_pair": "en-zh",
                "total_lines": 3,
                "created_at": datetime.now().isoformat()
            },
            "creator_id": "user-creator-123"
        }
        
        response = client.post("/api/v1/collaboration/create-session", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["code"] == 200
        assert "data" in data
        
        session_data = data["data"]
        assert "session_id" in session_data
        assert session_data["webapp_url"].startswith("/collaboration/")
        assert session_data["websocket_url"].startswith("/ws/collaboration/")
        assert "permissions" in session_data
        
        # 保存session_id用于后续测试
        self.session_id = session_data["session_id"]
    
    def test_create_session_content_mismatch(self):
        """测试内容长度不匹配"""
        request_data = {
            "document_id": "doc-test-456",
            "en_content": ["Hello", "World"],
            "cn_content": ["你好"],  # 长度不匹配
            "metadata": {
                "title": "测试文档",
                "total_lines": 2,
                "created_at": datetime.now().isoformat()
            },
            "creator_id": "user-creator-456"
        }
        
        response = client.post("/api/v1/collaboration/create-session", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "行数不一致" in data["detail"]["error"]
    
    def test_get_collaboration_state(self):
        """测试获取协作状态"""
        # 先创建会话
        request_data = {
            "document_id": "doc-state-test",
            "en_content": ["Test line"],
            "cn_content": ["测试行"],
            "metadata": {
                "title": "状态测试文档",
                "total_lines": 1,
                "created_at": datetime.now().isoformat()
            },
            "creator_id": "user-state-test"
        }
        
        create_response = client.post("/api/v1/collaboration/create-session", json=request_data)
        session_id = create_response.json()["data"]["session_id"]
        
        # 获取协作状态
        response = client.get(f"/api/v1/collaboration/{session_id}/state")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        
        state_data = data["data"]
        assert state_data["session_id"] == session_id
        assert "active_users" in state_data
        assert "pending_comments" in state_data
        assert "last_activity" in state_data
    
    def test_get_state_nonexistent_session(self):
        """测试获取不存在会话的状态"""
        response = client.get("/api/v1/collaboration/nonexistent-session/state")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["success"] is False
        assert "不存在" in data["detail"]["message"]
    
    def test_get_session_content(self):
        """测试获取会话内容"""
        # 先创建会话
        request_data = {
            "document_id": "doc-content-test",
            "en_content": ["First line", "Second line"],
            "cn_content": ["第一行", "第二行"],
            "metadata": {
                "title": "内容测试文档",
                "total_lines": 2,
                "created_at": datetime.now().isoformat()
            },
            "creator_id": "user-content-test"
        }
        
        create_response = client.post("/api/v1/collaboration/create-session", json=request_data)
        session_id = create_response.json()["data"]["session_id"]
        
        # 获取会话内容
        response = client.get(f"/api/v1/collaboration/{session_id}/content")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        
        content_data = data["data"]
        assert "en" in content_data
        assert "cn" in content_data
        assert content_data["en"] == ["First line", "Second line"]
        assert content_data["cn"] == ["第一行", "第二行"]
    
    def test_get_edit_history_empty(self):
        """测试获取空编辑历史"""
        # 先创建会话
        request_data = {
            "document_id": "doc-history-test",
            "en_content": ["Test"],
            "cn_content": ["测试"],
            "metadata": {
                "title": "历史测试文档",
                "total_lines": 1,
                "created_at": datetime.now().isoformat()
            },
            "creator_id": "user-history-test"
        }
        
        create_response = client.post("/api/v1/collaboration/create-session", json=request_data)
        session_id = create_response.json()["data"]["session_id"]
        
        # 获取编辑历史
        response = client.get(f"/api/v1/collaboration/{session_id}/history")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"] == []
        assert data["total_count"] == 0
    
    def test_get_comments_empty(self):
        """测试获取空批注列表"""
        # 先创建会话
        request_data = {
            "document_id": "doc-comments-test",
            "en_content": ["Test"],
            "cn_content": ["测试"],
            "metadata": {
                "title": "批注测试文档",
                "total_lines": 1,
                "created_at": datetime.now().isoformat()
            },
            "creator_id": "user-comments-test"
        }
        
        create_response = client.post("/api/v1/collaboration/create-session", json=request_data)
        session_id = create_response.json()["data"]["session_id"]
        
        # 获取批注列表
        response = client.get(f"/api/v1/collaboration/{session_id}/comments")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"] == []
        assert data["total_count"] == 0
    
    def test_get_history_with_limit(self):
        """测试带限制的历史查询"""
        # 先创建会话
        request_data = {
            "document_id": "doc-limit-test",
            "en_content": ["Test"],
            "cn_content": ["测试"],
            "metadata": {
                "title": "限制测试文档",
                "total_lines": 1,
                "created_at": datetime.now().isoformat()
            },
            "creator_id": "user-limit-test"
        }
        
        create_response = client.post("/api/v1/collaboration/create-session", json=request_data)
        session_id = create_response.json()["data"]["session_id"]
        
        # 测试不同的限制参数
        response = client.get(f"/api/v1/collaboration/{session_id}/history?limit=50")
        assert response.status_code == 200
        
        response = client.get(f"/api/v1/collaboration/{session_id}/history?limit=1")
        assert response.status_code == 200
        
        # 测试无效限制参数
        response = client.get(f"/api/v1/collaboration/{session_id}/history?limit=0")
        assert response.status_code == 422  # 验证错误
        
        response = client.get(f"/api/v1/collaboration/{session_id}/history?limit=2000")
        assert response.status_code == 422  # 超出最大限制
    
    def test_api_error_handling(self):
        """测试API错误处理"""
        # 测试无效的JSON数据
        response = client.post(
            "/api/v1/collaboration/create-session",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        
        # 测试缺少必需字段
        response = client.post("/api/v1/collaboration/create-session", json={})
        assert response.status_code == 422
        
        # 测试不存在的会话
        response = client.get("/api/v1/collaboration/invalid-session-id/content")
        assert response.status_code == 404
