"""
协作管理服务
处理协作会话的创建、管理和状态维护
"""
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from ..schemas.collaboration import (
    CollaborationSession,
    CollaborationSessionRequest,
    SessionResult,
    UserInfo,
    UserRole,
    SessionStatus,
    CollaborationState,
    EditEvent,
    CommentEvent,
    EditHistory,
    Comment,
    UserPermissions
)


class CollaborationError(Exception):
    """协作异常"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)


class CollaborationManager:
    """协作管理器"""
    
    def __init__(self):
        # 内存存储（生产环境应使用数据库）
        self.sessions: Dict[str, CollaborationSession] = {}
        self.session_content: Dict[str, Dict[str, List[str]]] = {}  # session_id -> {en: [], cn: []}
        self.active_connections: Dict[str, List[str]] = {}  # session_id -> [user_ids]
        self.edit_history: Dict[str, List[EditHistory]] = {}  # session_id -> [history]
        self.comments: Dict[str, List[Comment]] = {}  # session_id -> [comments]
        self.user_permissions: Dict[str, UserPermissions] = {}  # user_id -> permissions
    
    def create_session(self, request: CollaborationSessionRequest) -> SessionResult:
        """
        创建协作会话
        
        Args:
            request: 创建会话请求
            
        Returns:
            SessionResult: 会话创建结果
            
        Raises:
            CollaborationError: 创建失败
        """
        try:
            # 生成会话ID
            session_id = str(uuid.uuid4())
            
            # 验证内容长度一致性
            if len(request.en_content) != len(request.cn_content):
                raise CollaborationError("英文和中文内容行数不一致")
            
            # 创建会话
            session = CollaborationSession(
                id=session_id,
                document_id=request.document_id,
                creator_id=request.creator_id,
                status=SessionStatus.ACTIVE,
                metadata=request.metadata,
                active_users=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 存储会话和内容
            self.sessions[session_id] = session
            self.session_content[session_id] = {
                "en": request.en_content.copy(),
                "cn": request.cn_content.copy()
            }
            self.active_connections[session_id] = []
            self.edit_history[session_id] = []
            self.comments[session_id] = []
            
            # 生成URLs
            webapp_url = f"/collaboration/{session_id}"
            websocket_url = f"/ws/collaboration/{session_id}"
            
            # 设置创建者权限
            creator_permissions = UserPermissions(
                can_edit_english=True,
                can_edit_chinese=True,
                can_add_comments=True,
                can_resolve_comments=True,
                can_view_history=True
            )
            self.user_permissions[request.creator_id] = creator_permissions
            
            return SessionResult(
                session_id=session_id,
                webapp_url=webapp_url,
                websocket_url=websocket_url,
                permissions=creator_permissions.dict()
            )
        
        except Exception as e:
            raise CollaborationError(f"创建协作会话失败: {str(e)}")
    
    def get_session(self, session_id: str) -> Optional[CollaborationSession]:
        """获取协作会话"""
        return self.sessions.get(session_id)
    
    def get_session_content(self, session_id: str) -> Optional[Dict[str, List[str]]]:
        """获取会话内容"""
        return self.session_content.get(session_id)
    
    def join_session(self, session_id: str, user: UserInfo) -> bool:
        """
        用户加入会话
        
        Args:
            session_id: 会话ID
            user: 用户信息
            
        Returns:
            bool: 是否成功加入
        """
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # 检查用户是否已在会话中
        existing_user = next((u for u in session.active_users if u.id == user.id), None)
        if existing_user:
            existing_user.is_online = True
        else:
            user.is_online = True
            session.active_users.append(user)
        
        # 添加到活跃连接
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        
        if user.id not in self.active_connections[session_id]:
            self.active_connections[session_id].append(user.id)
        
        # 设置默认权限
        if user.id not in self.user_permissions:
            if user.role == UserRole.TRANSLATOR:
                self.user_permissions[user.id] = UserPermissions(
                    can_edit_english=False,
                    can_edit_chinese=True,
                    can_add_comments=True,
                    can_resolve_comments=False,
                    can_view_history=True
                )
            elif user.role == UserRole.REVIEWER:
                self.user_permissions[user.id] = UserPermissions(
                    can_edit_english=False,
                    can_edit_chinese=False,
                    can_add_comments=True,
                    can_resolve_comments=True,
                    can_view_history=True
                )
        
        session.updated_at = datetime.now()
        return True
    
    def leave_session(self, session_id: str, user_id: str) -> bool:
        """
        用户离开会话
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            
        Returns:
            bool: 是否成功离开
        """
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # 更新用户在线状态
        for user in session.active_users:
            if user.id == user_id:
                user.is_online = False
                break
        
        # 从活跃连接中移除
        if session_id in self.active_connections:
            if user_id in self.active_connections[session_id]:
                self.active_connections[session_id].remove(user_id)
        
        session.updated_at = datetime.now()
        return True
    
    def apply_edit(self, edit_event: EditEvent) -> bool:
        """
        应用编辑操作
        
        Args:
            edit_event: 编辑事件
            
        Returns:
            bool: 是否成功应用
        """
        session_id = edit_event.session_id
        
        if session_id not in self.session_content:
            return False
        
        content = self.session_content[session_id]
        line_number = edit_event.line_number
        
        # 验证行号有效性
        if edit_event.edit_type.value == "en":
            if line_number >= len(content["en"]):
                return False
            old_content = content["en"][line_number]
            content["en"][line_number] = edit_event.content
        else:
            if line_number >= len(content["cn"]):
                return False
            old_content = content["cn"][line_number]
            content["cn"][line_number] = edit_event.content
        
        # 记录编辑历史
        history_item = EditHistory(
            id=str(uuid.uuid4()),
            session_id=session_id,
            line_number=line_number,
            old_content=old_content,
            new_content=edit_event.content,
            edit_type=edit_event.edit_type,
            user_id=edit_event.user_id,
            user_name=self._get_user_name(session_id, edit_event.user_id),
            timestamp=edit_event.timestamp
        )
        
        if session_id not in self.edit_history:
            self.edit_history[session_id] = []
        self.edit_history[session_id].append(history_item)
        
        # 更新会话时间
        if session_id in self.sessions:
            self.sessions[session_id].updated_at = datetime.now()
        
        return True
    
    def add_comment(self, comment_event: CommentEvent) -> Comment:
        """
        添加批注
        
        Args:
            comment_event: 批注事件
            
        Returns:
            Comment: 创建的批注
        """
        comment = Comment(
            id=str(uuid.uuid4()),
            session_id=comment_event.session_id,
            line_number=comment_event.line_number,
            content=comment_event.comment_content,
            comment_type=comment_event.comment_type,
            author_id=comment_event.author_id,
            author_name=self._get_user_name(comment_event.session_id, comment_event.author_id),
            is_resolved=False,
            created_at=comment_event.timestamp,
            updated_at=comment_event.timestamp
        )
        
        if comment_event.session_id not in self.comments:
            self.comments[comment_event.session_id] = []
        self.comments[comment_event.session_id].append(comment)
        
        return comment
    
    def get_collaboration_state(self, session_id: str) -> Optional[CollaborationState]:
        """
        获取协作状态
        
        Args:
            session_id: 会话ID
            
        Returns:
            CollaborationState: 协作状态
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        pending_comments = len([c for c in self.comments.get(session_id, []) if not c.is_resolved])
        
        return CollaborationState(
            session_id=session_id,
            active_users=session.active_users,
            current_editors={},  # TODO: 实现当前编辑者追踪
            pending_comments=pending_comments,
            last_activity=session.updated_at
        )
    
    def get_edit_history(self, session_id: str, limit: int = 100) -> List[EditHistory]:
        """
        获取编辑历史
        
        Args:
            session_id: 会话ID
            limit: 限制数量
            
        Returns:
            List[EditHistory]: 编辑历史列表
        """
        history = self.edit_history.get(session_id, [])
        return sorted(history, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_comments(self, session_id: str) -> List[Comment]:
        """
        获取批注列表
        
        Args:
            session_id: 会话ID
            
        Returns:
            List[Comment]: 批注列表
        """
        return self.comments.get(session_id, [])
    
    def check_user_permission(self, user_id: str, permission: str) -> bool:
        """
        检查用户权限
        
        Args:
            user_id: 用户ID
            permission: 权限名称
            
        Returns:
            bool: 是否有权限
        """
        user_perms = self.user_permissions.get(user_id)
        if not user_perms:
            return False
        
        return getattr(user_perms, permission, False)
    
    def _get_user_name(self, session_id: str, user_id: str) -> str:
        """获取用户名称"""
        if session_id in self.sessions:
            for user in self.sessions[session_id].active_users:
                if user.id == user_id:
                    return user.name
        return f"User-{user_id[:8]}"
