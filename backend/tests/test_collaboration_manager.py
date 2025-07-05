"""
协作管理器单元测试
"""
import pytest
from datetime import datetime
from app.services.collaboration_manager import CollaborationManager, CollaborationError
from app.schemas.collaboration import (
    CollaborationSessionRequest,
    DocumentMetadata,
    UserInfo,
    UserRole,
    EditEvent,
    CommentEvent,
    EditType,
    CommentType
)


class TestCollaborationManager:
    """测试协作管理器"""
    
    def setup_method(self):
        """测试前准备"""
        self.manager = CollaborationManager()
        self.sample_metadata = DocumentMetadata(
            title="测试文档",
            author="测试作者",
            description="测试描述",
            language_pair="en-zh",
            total_lines=3,
            created_at=datetime.now()
        )
    
    def test_create_session_success(self):
        """测试创建会话成功"""
        request = CollaborationSessionRequest(
            document_id="doc-123",
            en_content=["Hello", "World", "Test"],
            cn_content=["你好", "世界", "测试"],
            metadata=self.sample_metadata,
            creator_id="user-123"
        )
        
        result = self.manager.create_session(request)
        
        assert result.session_id is not None
        assert result.webapp_url == f"/collaboration/{result.session_id}"
        assert result.websocket_url == f"/ws/collaboration/{result.session_id}"
        assert result.permissions["can_edit_english"] is True
        assert result.permissions["can_edit_chinese"] is True
    
    def test_create_session_content_mismatch(self):
        """测试内容长度不匹配"""
        request = CollaborationSessionRequest(
            document_id="doc-123",
            en_content=["Hello", "World"],
            cn_content=["你好"],  # 长度不匹配
            metadata=self.sample_metadata,
            creator_id="user-123"
        )
        
        with pytest.raises(CollaborationError) as exc_info:
            self.manager.create_session(request)
        
        assert "行数不一致" in str(exc_info.value)
    
    def test_get_session(self):
        """测试获取会话"""
        request = CollaborationSessionRequest(
            document_id="doc-123",
            en_content=["Hello"],
            cn_content=["你好"],
            metadata=self.sample_metadata,
            creator_id="user-123"
        )
        
        result = self.manager.create_session(request)
        session = self.manager.get_session(result.session_id)
        
        assert session is not None
        assert session.id == result.session_id
        assert session.document_id == "doc-123"
        assert session.creator_id == "user-123"
    
    def test_join_session(self):
        """测试用户加入会话"""
        # 创建会话
        request = CollaborationSessionRequest(
            document_id="doc-123",
            en_content=["Hello"],
            cn_content=["你好"],
            metadata=self.sample_metadata,
            creator_id="user-123"
        )
        result = self.manager.create_session(request)
        
        # 用户加入
        user = UserInfo(
            id="user-456",
            name="测试用户",
            role=UserRole.TRANSLATOR
        )
        
        success = self.manager.join_session(result.session_id, user)
        assert success is True
        
        # 检查会话状态
        session = self.manager.get_session(result.session_id)
        assert len(session.active_users) == 1
        assert session.active_users[0].id == "user-456"
        assert session.active_users[0].is_online is True
    
    def test_leave_session(self):
        """测试用户离开会话"""
        # 创建会话并加入用户
        request = CollaborationSessionRequest(
            document_id="doc-123",
            en_content=["Hello"],
            cn_content=["你好"],
            metadata=self.sample_metadata,
            creator_id="user-123"
        )
        result = self.manager.create_session(request)
        
        user = UserInfo(
            id="user-456",
            name="测试用户",
            role=UserRole.TRANSLATOR
        )
        self.manager.join_session(result.session_id, user)
        
        # 用户离开
        success = self.manager.leave_session(result.session_id, "user-456")
        assert success is True
        
        # 检查用户状态
        session = self.manager.get_session(result.session_id)
        user_in_session = next((u for u in session.active_users if u.id == "user-456"), None)
        assert user_in_session is not None
        assert user_in_session.is_online is False
    
    def test_apply_edit(self):
        """测试应用编辑"""
        # 创建会话
        request = CollaborationSessionRequest(
            document_id="doc-123",
            en_content=["Hello", "World"],
            cn_content=["你好", "世界"],
            metadata=self.sample_metadata,
            creator_id="user-123"
        )
        result = self.manager.create_session(request)
        
        # 应用编辑
        edit_event = EditEvent(
            session_id=result.session_id,
            line_number=0,
            content="Hi there",
            edit_type=EditType.ENGLISH,
            user_id="user-123"
        )
        
        success = self.manager.apply_edit(edit_event)
        assert success is True
        
        # 检查内容变化
        content = self.manager.get_session_content(result.session_id)
        assert content["en"][0] == "Hi there"
        assert content["cn"][0] == "你好"  # 中文内容不变
        
        # 检查编辑历史
        history = self.manager.get_edit_history(result.session_id)
        assert len(history) == 1
        assert history[0].old_content == "Hello"
        assert history[0].new_content == "Hi there"
    
    def test_apply_edit_invalid_line(self):
        """测试编辑无效行号"""
        request = CollaborationSessionRequest(
            document_id="doc-123",
            en_content=["Hello"],
            cn_content=["你好"],
            metadata=self.sample_metadata,
            creator_id="user-123"
        )
        result = self.manager.create_session(request)
        
        # 编辑超出范围的行号
        edit_event = EditEvent(
            session_id=result.session_id,
            line_number=10,  # 超出范围
            content="Invalid",
            edit_type=EditType.ENGLISH,
            user_id="user-123"
        )
        
        success = self.manager.apply_edit(edit_event)
        assert success is False
    
    def test_add_comment(self):
        """测试添加批注"""
        # 创建会话
        request = CollaborationSessionRequest(
            document_id="doc-123",
            en_content=["Hello"],
            cn_content=["你好"],
            metadata=self.sample_metadata,
            creator_id="user-123"
        )
        result = self.manager.create_session(request)
        
        # 添加用户
        user = UserInfo(
            id="user-456",
            name="审核员",
            role=UserRole.REVIEWER
        )
        self.manager.join_session(result.session_id, user)
        
        # 添加批注
        comment_event = CommentEvent(
            session_id=result.session_id,
            line_number=0,
            comment_content="这个翻译需要改进",
            comment_type=CommentType.SUGGESTION,
            author_id="user-456"
        )
        
        comment = self.manager.add_comment(comment_event)
        
        assert comment.id is not None
        assert comment.content == "这个翻译需要改进"
        assert comment.comment_type == CommentType.SUGGESTION
        assert comment.author_name == "审核员"
        assert comment.is_resolved is False
        
        # 检查批注列表
        comments = self.manager.get_comments(result.session_id)
        assert len(comments) == 1
        assert comments[0].id == comment.id
    
    def test_get_collaboration_state(self):
        """测试获取协作状态"""
        # 创建会话
        request = CollaborationSessionRequest(
            document_id="doc-123",
            en_content=["Hello"],
            cn_content=["你好"],
            metadata=self.sample_metadata,
            creator_id="user-123"
        )
        result = self.manager.create_session(request)
        
        # 添加用户和批注
        user = UserInfo(
            id="user-456",
            name="测试用户",
            role=UserRole.TRANSLATOR
        )
        self.manager.join_session(result.session_id, user)
        
        comment_event = CommentEvent(
            session_id=result.session_id,
            line_number=0,
            comment_content="测试批注",
            comment_type=CommentType.QUESTION,
            author_id="user-456"
        )
        self.manager.add_comment(comment_event)
        
        # 获取协作状态
        state = self.manager.get_collaboration_state(result.session_id)
        
        assert state is not None
        assert state.session_id == result.session_id
        assert len(state.active_users) == 1
        assert state.pending_comments == 1
        assert state.last_activity is not None
    
    def test_check_user_permission(self):
        """测试用户权限检查"""
        # 创建会话
        request = CollaborationSessionRequest(
            document_id="doc-123",
            en_content=["Hello"],
            cn_content=["你好"],
            metadata=self.sample_metadata,
            creator_id="user-123"
        )
        result = self.manager.create_session(request)
        
        # 添加翻译人员
        translator = UserInfo(
            id="translator-1",
            name="翻译员",
            role=UserRole.TRANSLATOR
        )
        self.manager.join_session(result.session_id, translator)
        
        # 添加审核人员
        reviewer = UserInfo(
            id="reviewer-1",
            name="审核员",
            role=UserRole.REVIEWER
        )
        self.manager.join_session(result.session_id, reviewer)
        
        # 检查翻译人员权限
        assert self.manager.check_user_permission("translator-1", "can_edit_chinese") is True
        assert self.manager.check_user_permission("translator-1", "can_edit_english") is False
        assert self.manager.check_user_permission("translator-1", "can_resolve_comments") is False
        
        # 检查审核人员权限
        assert self.manager.check_user_permission("reviewer-1", "can_edit_chinese") is False
        assert self.manager.check_user_permission("reviewer-1", "can_add_comments") is True
        assert self.manager.check_user_permission("reviewer-1", "can_resolve_comments") is True
        
        # 检查创建者权限
        assert self.manager.check_user_permission("user-123", "can_edit_english") is True
        assert self.manager.check_user_permission("user-123", "can_edit_chinese") is True
