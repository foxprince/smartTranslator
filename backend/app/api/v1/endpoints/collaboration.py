"""
协作相关API端点
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from typing import List
from ....schemas.collaboration import (
    CollaborationSessionRequest,
    CollaborationSessionResponse,
    SessionResult,
    EditHistoryResponse,
    CollaborationState
)
from ....services.collaboration_manager import CollaborationManager, CollaborationError
from ....websocket.collaboration_ws import connection_manager

router = APIRouter()
collaboration_manager = CollaborationManager()


@router.post(
    "/create-session",
    response_model=CollaborationSessionResponse,
    summary="创建协作会话",
    description="创建新的双语协作编辑会话"
)
async def create_collaboration_session(request: CollaborationSessionRequest):
    """
    创建协作会话接口
    
    - **document_id**: 文档ID
    - **en_content**: 英文内容行列表
    - **cn_content**: 中文内容行列表
    - **metadata**: 文档元数据
    - **creator_id**: 创建者ID
    
    返回协作会话信息和访问URLs
    """
    try:
        # 创建协作会话
        result = collaboration_manager.create_session(request)
        
        return CollaborationSessionResponse(
            success=True,
            data=result.model_dump(),
            message="协作会话创建成功",
            code=200
        )
    
    except CollaborationError as e:
        raise HTTPException(
            status_code=e.code,
            detail={
                "success": False,
                "error": e.message,
                "message": "协作会话创建失败",
                "code": e.code
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "服务器内部错误",
                "code": 500
            }
        )


@router.get(
    "/{session_id}/state",
    summary="获取协作状态",
    description="获取指定会话的协作状态信息"
)
async def get_collaboration_state(session_id: str):
    """
    获取协作状态接口
    """
    try:
        state = collaboration_manager.get_collaboration_state(session_id)
        if not state:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "Session not found",
                    "message": "协作会话不存在",
                    "code": 404
                }
            )
        
        return {
            "success": True,
            "data": state.model_dump(),
            "message": "获取协作状态成功",
            "code": 200
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "服务器内部错误",
                "code": 500
            }
        )


@router.get(
    "/{session_id}/history",
    response_model=EditHistoryResponse,
    summary="获取编辑历史",
    description="获取指定会话的编辑历史记录"
)
async def get_edit_history(
    session_id: str,
    limit: int = Query(default=100, ge=1, le=1000, description="限制返回数量")
):
    """
    获取编辑历史接口
    """
    try:
        # 检查会话是否存在
        session = collaboration_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "Session not found",
                    "message": "协作会话不存在",
                    "code": 404
                }
            )
        
        # 获取编辑历史
        history = collaboration_manager.get_edit_history(session_id, limit)
        
        return EditHistoryResponse(
            success=True,
            data=history,
            total_count=len(history),
            message="获取编辑历史成功"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "服务器内部错误",
                "code": 500
            }
        )


@router.get(
    "/{session_id}/comments",
    summary="获取批注列表",
    description="获取指定会话的所有批注"
)
async def get_comments(session_id: str):
    """
    获取批注列表接口
    """
    try:
        # 检查会话是否存在
        session = collaboration_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "Session not found",
                    "message": "协作会话不存在",
                    "code": 404
                }
            )
        
        # 获取批注列表
        comments = collaboration_manager.get_comments(session_id)
        
        return {
            "success": True,
            "data": [comment.model_dump() for comment in comments],
            "total_count": len(comments),
            "message": "获取批注列表成功",
            "code": 200
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "服务器内部错误",
                "code": 500
            }
        )


@router.get(
    "/{session_id}/content",
    summary="获取会话内容",
    description="获取指定会话的双语内容"
)
async def get_session_content(session_id: str):
    """
    获取会话内容接口
    """
    try:
        # 检查会话是否存在
        session = collaboration_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "Session not found",
                    "message": "协作会话不存在",
                    "code": 404
                }
            )
        
        # 获取会话内容
        content = collaboration_manager.get_session_content(session_id)
        if not content:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "Content not found",
                    "message": "会话内容不存在",
                    "code": 404
                }
            )
        
        return {
            "success": True,
            "data": content,
            "message": "获取会话内容成功",
            "code": 200
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "message": "服务器内部错误",
                "code": 500
            }
        )


@router.websocket("/ws/{session_id}")
async def websocket_collaboration(
    websocket: WebSocket,
    session_id: str,
    user_id: str = Query(..., description="用户ID"),
    user_name: str = Query(..., description="用户名"),
    user_role: str = Query(..., description="用户角色")
):
    """
    协作WebSocket端点
    
    - **session_id**: 会话ID
    - **user_id**: 用户ID
    - **user_name**: 用户名
    - **user_role**: 用户角色 (translator/reviewer/admin)
    
    支持的消息类型:
    - edit: 编辑事件
    - comment: 批注事件
    - cursor: 光标位置事件
    """
    try:
        # 建立连接
        await connection_manager.connect(websocket, session_id, user_id, user_name, user_role)
        
        while True:
            # 接收消息
            message = await websocket.receive_text()
            await connection_manager.handle_message(websocket, message)
    
    except WebSocketDisconnect:
        # 处理连接断开
        await connection_manager.disconnect(websocket)
    except Exception as e:
        # 处理其他异常
        print(f"WebSocket error: {str(e)}")
        await connection_manager.disconnect(websocket)


@router.get(
    "/health",
    summary="协作服务健康检查",
    description="检查协作服务状态"
)
async def collaboration_health_check():
    """
    协作服务健康检查接口
    """
    return {
        "success": True,
        "message": "协作服务运行正常",
        "service": "collaboration-service",
        "version": "1.0.0",
        "active_sessions": len(collaboration_manager.sessions),
        "active_connections": sum(len(conns) for conns in connection_manager.active_connections.values())
    }
