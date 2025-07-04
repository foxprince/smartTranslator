"""
协作相关的Pydantic模式定义
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """用户角色"""
    TRANSLATOR = "translator"
    REVIEWER = "reviewer"
    ADMIN = "admin"


class EditType(str, Enum):
    """编辑类型"""
    ENGLISH = "en"
    CHINESE = "cn"


class EventType(str, Enum):
    """事件类型"""
    EDIT = "edit"
    COMMENT = "comment"
    CURSOR = "cursor"
    USER_JOIN = "user_join"
    USER_LEAVE = "user_leave"


class CommentType(str, Enum):
    """批注类型"""
    SUGGESTION = "suggestion"
    QUESTION = "question"
    APPROVAL = "approval"
    CORRECTION = "correction"


class SessionStatus(str, Enum):
    """会话状态"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class UserInfo(BaseModel):
    """用户信息"""
    id: str = Field(..., description="用户ID")
    name: str = Field(..., description="用户名")
    role: UserRole = Field(..., description="用户角色")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    is_online: bool = Field(default=False, description="是否在线")


class DocumentMetadata(BaseModel):
    """文档元数据"""
    title: str = Field(..., description="文档标题")
    author: Optional[str] = Field(None, description="作者")
    description: Optional[str] = Field(None, description="描述")
    language_pair: str = Field(default="en-zh", description="语言对")
    total_lines: int = Field(..., description="总行数")
    created_at: datetime = Field(..., description="创建时间")


class CollaborationSessionRequest(BaseModel):
    """创建协作会话请求"""
    document_id: str = Field(..., description="文档ID")
    en_content: List[str] = Field(..., description="英文内容行列表")
    cn_content: List[str] = Field(..., description="中文内容行列表")
    metadata: DocumentMetadata = Field(..., description="文档元数据")
    creator_id: str = Field(..., description="创建者ID")


class CollaborationSession(BaseModel):
    """协作会话"""
    id: str = Field(..., description="会话ID")
    document_id: str = Field(..., description="文档ID")
    creator_id: str = Field(..., description="创建者ID")
    status: SessionStatus = Field(..., description="会话状态")
    metadata: DocumentMetadata = Field(..., description="文档元数据")
    active_users: List[UserInfo] = Field(default=[], description="活跃用户列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class EditEvent(BaseModel):
    """编辑事件"""
    event_type: EventType = Field(default=EventType.EDIT, description="事件类型")
    session_id: str = Field(..., description="会话ID")
    line_number: int = Field(..., description="行号")
    content: str = Field(..., description="编辑内容")
    edit_type: EditType = Field(..., description="编辑类型")
    user_id: str = Field(..., description="用户ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class CommentEvent(BaseModel):
    """批注事件"""
    event_type: EventType = Field(default=EventType.COMMENT, description="事件类型")
    session_id: str = Field(..., description="会话ID")
    line_number: int = Field(..., description="行号")
    comment_content: str = Field(..., description="批注内容")
    comment_type: CommentType = Field(..., description="批注类型")
    author_id: str = Field(..., description="作者ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class Comment(BaseModel):
    """批注"""
    id: str = Field(..., description="批注ID")
    session_id: str = Field(..., description="会话ID")
    line_number: int = Field(..., description="行号")
    content: str = Field(..., description="批注内容")
    comment_type: CommentType = Field(..., description="批注类型")
    author_id: str = Field(..., description="作者ID")
    author_name: str = Field(..., description="作者名称")
    is_resolved: bool = Field(default=False, description="是否已解决")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class EditHistory(BaseModel):
    """编辑历史"""
    id: str = Field(..., description="历史记录ID")
    session_id: str = Field(..., description="会话ID")
    line_number: int = Field(..., description="行号")
    old_content: str = Field(..., description="原内容")
    new_content: str = Field(..., description="新内容")
    edit_type: EditType = Field(..., description="编辑类型")
    user_id: str = Field(..., description="用户ID")
    user_name: str = Field(..., description="用户名")
    timestamp: datetime = Field(..., description="时间戳")


class CollaborationSessionResponse(BaseModel):
    """协作会话响应"""
    success: bool = Field(..., description="是否成功")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    message: str = Field(..., description="响应消息")
    code: int = Field(..., description="响应代码")


class SessionResult(BaseModel):
    """会话创建结果"""
    session_id: str = Field(..., description="会话ID")
    webapp_url: str = Field(..., description="协作网页URL")
    websocket_url: str = Field(..., description="WebSocket连接URL")
    permissions: Dict[str, bool] = Field(..., description="用户权限")


class UserPermissions(BaseModel):
    """用户权限"""
    can_edit_english: bool = Field(default=False, description="可编辑英文")
    can_edit_chinese: bool = Field(default=True, description="可编辑中文")
    can_add_comments: bool = Field(default=True, description="可添加批注")
    can_resolve_comments: bool = Field(default=False, description="可解决批注")
    can_view_history: bool = Field(default=True, description="可查看历史")


class CollaborationState(BaseModel):
    """协作状态"""
    session_id: str = Field(..., description="会话ID")
    active_users: List[UserInfo] = Field(..., description="活跃用户")
    current_editors: Dict[int, str] = Field(default={}, description="当前编辑者(行号->用户ID)")
    pending_comments: int = Field(default=0, description="待处理批注数")
    last_activity: datetime = Field(..., description="最后活动时间")


class WebSocketMessage(BaseModel):
    """WebSocket消息"""
    type: str = Field(..., description="消息类型")
    data: Dict[str, Any] = Field(..., description="消息数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class EditHistoryResponse(BaseModel):
    """编辑历史响应"""
    success: bool = Field(..., description="是否成功")
    data: List[EditHistory] = Field(..., description="历史记录列表")
    total_count: int = Field(..., description="总记录数")
    message: str = Field(..., description="响应消息")
