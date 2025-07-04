"""
协作WebSocket处理器
处理实时协作通信
"""
import json
import logging
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect
from ..services.collaboration_manager import CollaborationManager
from ..schemas.collaboration import (
    EditEvent,
    CommentEvent,
    UserInfo,
    UserRole,
    EventType,
    WebSocketMessage
)

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # session_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # websocket -> user_id
        self.connection_users: Dict[WebSocket, str] = {}
        # websocket -> session_id
        self.connection_sessions: Dict[WebSocket, str] = {}
        
        self.collaboration_manager = CollaborationManager()
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str, user_name: str, user_role: str):
        """
        建立WebSocket连接
        
        Args:
            websocket: WebSocket连接
            session_id: 会话ID
            user_id: 用户ID
            user_name: 用户名
            user_role: 用户角色
        """
        await websocket.accept()
        
        # 记录连接信息
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        
        self.active_connections[session_id].append(websocket)
        self.connection_users[websocket] = user_id
        self.connection_sessions[websocket] = session_id
        
        # 用户加入会话
        user_info = UserInfo(
            id=user_id,
            name=user_name,
            role=UserRole(user_role),
            is_online=True
        )
        
        success = self.collaboration_manager.join_session(session_id, user_info)
        if not success:
            await websocket.close(code=4004, reason="Session not found")
            return
        
        # 通知其他用户有新用户加入
        await self.broadcast_to_session(session_id, {
            "type": "user_join",
            "data": {
                "user_id": user_id,
                "user_name": user_name,
                "user_role": user_role
            }
        }, exclude_websocket=websocket)
        
        # 发送当前会话状态给新用户
        collaboration_state = self.collaboration_manager.get_collaboration_state(session_id)
        if collaboration_state:
            await self.send_to_websocket(websocket, {
                "type": "session_state",
                "data": collaboration_state.dict()
            })
        
        # 发送当前内容给新用户
        content = self.collaboration_manager.get_session_content(session_id)
        if content:
            await self.send_to_websocket(websocket, {
                "type": "content_sync",
                "data": content
            })
        
        logger.info(f"User {user_id} connected to session {session_id}")
    
    async def disconnect(self, websocket: WebSocket):
        """
        断开WebSocket连接
        
        Args:
            websocket: WebSocket连接
        """
        user_id = self.connection_users.get(websocket)
        session_id = self.connection_sessions.get(websocket)
        
        if session_id and session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            
            # 如果会话没有其他连接，清理会话连接列表
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        
        # 清理连接记录
        if websocket in self.connection_users:
            del self.connection_users[websocket]
        if websocket in self.connection_sessions:
            del self.connection_sessions[websocket]
        
        # 用户离开会话
        if user_id and session_id:
            self.collaboration_manager.leave_session(session_id, user_id)
            
            # 通知其他用户有用户离开
            await self.broadcast_to_session(session_id, {
                "type": "user_leave",
                "data": {
                    "user_id": user_id
                }
            })
        
        logger.info(f"User {user_id} disconnected from session {session_id}")
    
    async def handle_message(self, websocket: WebSocket, message: str):
        """
        处理WebSocket消息
        
        Args:
            websocket: WebSocket连接
            message: 消息内容
        """
        try:
            data = json.loads(message)
            event_type = data.get("type")
            event_data = data.get("data", {})
            
            user_id = self.connection_users.get(websocket)
            session_id = self.connection_sessions.get(websocket)
            
            if not user_id or not session_id:
                await self.send_error(websocket, "Invalid connection state")
                return
            
            if event_type == "edit":
                await self.handle_edit_event(websocket, session_id, user_id, event_data)
            elif event_type == "comment":
                await self.handle_comment_event(websocket, session_id, user_id, event_data)
            elif event_type == "cursor":
                await self.handle_cursor_event(websocket, session_id, user_id, event_data)
            else:
                await self.send_error(websocket, f"Unknown event type: {event_type}")
        
        except json.JSONDecodeError:
            await self.send_error(websocket, "Invalid JSON message")
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            await self.send_error(websocket, "Internal server error")
    
    async def handle_edit_event(self, websocket: WebSocket, session_id: str, user_id: str, event_data: dict):
        """
        处理编辑事件
        
        Args:
            websocket: WebSocket连接
            session_id: 会话ID
            user_id: 用户ID
            event_data: 事件数据
        """
        try:
            # 验证权限
            edit_type = event_data.get("edit_type")
            if edit_type == "en" and not self.collaboration_manager.check_user_permission(user_id, "can_edit_english"):
                await self.send_error(websocket, "No permission to edit English content")
                return
            elif edit_type == "cn" and not self.collaboration_manager.check_user_permission(user_id, "can_edit_chinese"):
                await self.send_error(websocket, "No permission to edit Chinese content")
                return
            
            # 创建编辑事件
            edit_event = EditEvent(
                session_id=session_id,
                line_number=event_data.get("line_number"),
                content=event_data.get("content"),
                edit_type=event_data.get("edit_type"),
                user_id=user_id
            )
            
            # 应用编辑
            success = self.collaboration_manager.apply_edit(edit_event)
            if not success:
                await self.send_error(websocket, "Failed to apply edit")
                return
            
            # 广播编辑事件给其他用户
            await self.broadcast_to_session(session_id, {
                "type": "edit",
                "data": {
                    "line_number": edit_event.line_number,
                    "content": edit_event.content,
                    "edit_type": edit_event.edit_type.value,
                    "user_id": user_id,
                    "timestamp": edit_event.timestamp.isoformat()
                }
            }, exclude_websocket=websocket)
            
            # 确认编辑成功
            await self.send_to_websocket(websocket, {
                "type": "edit_confirmed",
                "data": {
                    "line_number": edit_event.line_number,
                    "edit_type": edit_event.edit_type.value
                }
            })
        
        except Exception as e:
            logger.error(f"Error handling edit event: {str(e)}")
            await self.send_error(websocket, "Failed to process edit event")
    
    async def handle_comment_event(self, websocket: WebSocket, session_id: str, user_id: str, event_data: dict):
        """
        处理批注事件
        
        Args:
            websocket: WebSocket连接
            session_id: 会话ID
            user_id: 用户ID
            event_data: 事件数据
        """
        try:
            # 验证权限
            if not self.collaboration_manager.check_user_permission(user_id, "can_add_comments"):
                await self.send_error(websocket, "No permission to add comments")
                return
            
            # 创建批注事件
            comment_event = CommentEvent(
                session_id=session_id,
                line_number=event_data.get("line_number"),
                comment_content=event_data.get("content"),
                comment_type=event_data.get("comment_type"),
                author_id=user_id
            )
            
            # 添加批注
            comment = self.collaboration_manager.add_comment(comment_event)
            
            # 广播批注事件给所有用户
            await self.broadcast_to_session(session_id, {
                "type": "comment",
                "data": comment.dict()
            })
        
        except Exception as e:
            logger.error(f"Error handling comment event: {str(e)}")
            await self.send_error(websocket, "Failed to process comment event")
    
    async def handle_cursor_event(self, websocket: WebSocket, session_id: str, user_id: str, event_data: dict):
        """
        处理光标位置事件
        
        Args:
            websocket: WebSocket连接
            session_id: 会话ID
            user_id: 用户ID
            event_data: 事件数据
        """
        # 广播光标位置给其他用户
        await self.broadcast_to_session(session_id, {
            "type": "cursor",
            "data": {
                "user_id": user_id,
                "line_number": event_data.get("line_number"),
                "position": event_data.get("position")
            }
        }, exclude_websocket=websocket)
    
    async def send_to_websocket(self, websocket: WebSocket, message: dict):
        """
        发送消息到指定WebSocket
        
        Args:
            websocket: WebSocket连接
            message: 消息内容
        """
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message to websocket: {str(e)}")
    
    async def broadcast_to_session(self, session_id: str, message: dict, exclude_websocket: WebSocket = None):
        """
        广播消息到会话中的所有WebSocket连接
        
        Args:
            session_id: 会话ID
            message: 消息内容
            exclude_websocket: 排除的WebSocket连接
        """
        if session_id not in self.active_connections:
            return
        
        disconnected_websockets = []
        
        for websocket in self.active_connections[session_id]:
            if websocket == exclude_websocket:
                continue
            
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to websocket: {str(e)}")
                disconnected_websockets.append(websocket)
        
        # 清理断开的连接
        for websocket in disconnected_websockets:
            await self.disconnect(websocket)
    
    async def send_error(self, websocket: WebSocket, error_message: str):
        """
        发送错误消息
        
        Args:
            websocket: WebSocket连接
            error_message: 错误消息
        """
        await self.send_to_websocket(websocket, {
            "type": "error",
            "data": {
                "message": error_message
            }
        })


# 全局连接管理器实例
connection_manager = ConnectionManager()
