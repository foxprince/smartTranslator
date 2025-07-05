/**
 * 双语协作编辑器组件
 * 支持实时编辑和协作功能
 */
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { toast } from 'react-toastify';
import { useWebSocket } from '../../../hooks/useWebSocket';
import { CollaborationIndicator } from './CollaborationIndicator';
import { CommentPanel } from './CommentPanel';
import { EditableLine } from './EditableLine';
import { User, UserRole, Comment, CommentType } from '../../../types';
import './BilingualEditor.css';

interface BilingualEditorProps {
  sessionId: string;
  initialEnContent: string[];
  initialCnContent: string[];
  currentUser: {
    id: string;
    username: string;
    role: UserRole;
  };
  onContentChange?: (lineNumber: number, content: string, type: 'en' | 'cn') => void;
}

export const BilingualEditor: React.FC<BilingualEditorProps> = ({
  sessionId,
  initialEnContent,
  initialCnContent,
  currentUser,
  onContentChange
}) => {
  // 状态管理
  const [enLines, setEnLines] = useState<string[]>(initialEnContent);
  const [cnLines, setCnLines] = useState<string[]>(initialCnContent);
  const [comments, setComments] = useState<Comment[]>([]);
  const [activeUsers, setActiveUsers] = useState<User[]>([]);
  const [selectedLine, setSelectedLine] = useState<number | null>(null);
  const [isCommentPanelOpen, setIsCommentPanelOpen] = useState(false);
  
  // WebSocket连接
  const websocketUrl = `ws://localhost:8000/api/v1/collaboration/ws/${sessionId}?user_id=${currentUser.id}&user_name=${currentUser.username}&user_role=${currentUser.role}`;
  const { socket, isConnected, sendMessage } = useWebSocket(websocketUrl);
  
  // 引用
  const editorRef = useRef<HTMLDivElement>(null);
  
  // WebSocket消息处理
  useEffect(() => {
    if (!socket) return;
    
    const handleMessage = (event: MessageEvent) => {
      try {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };
    
    socket.addEventListener('message', handleMessage);
    
    return () => {
      socket.removeEventListener('message', handleMessage);
    };
  }, [socket]);
  
  // 处理WebSocket消息
  const handleWebSocketMessage = useCallback((message: any) => {
    switch (message.type) {
      case 'edit':
        handleRemoteEdit(message.data);
        break;
      case 'comment':
        handleRemoteComment(message.data);
        break;
      case 'user_join':
        handleUserJoin(message.data);
        break;
      case 'user_leave':
        handleUserLeave(message.data);
        break;
      case 'session_state':
        handleSessionState(message.data);
        break;
      case 'content_sync':
        handleContentSync(message.data);
        break;
      case 'edit_confirmed':
        // 编辑确认，可以显示成功提示
        break;
      case 'error':
        toast.error(message.data.message);
        break;
      default:
        console.log('Unknown message type:', message.type);
    }
  }, []);
  
  // 处理远程编辑
  const handleRemoteEdit = useCallback((data: any) => {
    const { line_number, content, edit_type, user_id } = data;
    
    if (user_id === currentUser.id) return; // 忽略自己的编辑
    
    if (edit_type === 'en') {
      setEnLines(prev => prev.map((line, idx) => 
        idx === line_number ? content : line
      ));
    } else {
      setCnLines(prev => prev.map((line, idx) => 
        idx === line_number ? content : line
      ));
    }
    
    // 显示编辑指示器
    showEditIndicator(line_number, data.user_name || `User-${user_id.slice(0, 8)}`);
  }, [currentUser.id]);
  
  // 处理远程批注
  const handleRemoteComment = useCallback((data: Comment) => {
    setComments(prev => [...prev, data]);
    toast.info(`${data.author_name} 添加了批注`);
  }, []);
  
  // 处理用户加入
  const handleUserJoin = useCallback((data: any) => {
    const newUser: User = {
      id: data.user_id,
      username: data.user_name,
      role: data.user_role,
      is_online: true,
      email: '',
      created_at: new Date().toISOString(),
      last_login: new Date().toISOString(),
    };
    
    setActiveUsers(prev => {
      const existing = prev.find(u => u.id === newUser.id);
      if (existing) {
        return prev.map(u => u.id === newUser.id ? { ...u, is_online: true } : u);
      }
      return [...prev, newUser];
    });
    
    toast.success(`${data.user_name} 加入了协作`);
  }, []);
  
  // 处理用户离开
  const handleUserLeave = useCallback((data: any) => {
    setActiveUsers(prev => 
      prev.map(u => u.id === data.user_id ? { ...u, is_online: false } : u)
    );
  }, []);
  
  // 处理会话状态
  const handleSessionState = useCallback((data: any) => {
    setActiveUsers(data.active_users || []);
    // 可以处理其他状态信息
  }, []);
  
  // 处理内容同步
  const handleContentSync = useCallback((data: any) => {
    if (data.en) setEnLines(data.en);
    if (data.cn) setCnLines(data.cn);
  }, []);
  
  // 显示编辑指示器
  const showEditIndicator = (lineNumber: number, userName: string) => {
    const lineElement = document.getElementById(`line-${lineNumber}`);
    if (lineElement) {
      lineElement.classList.add('recently-edited');
      lineElement.setAttribute('data-editor', userName);
      
      // 3秒后移除指示器
      setTimeout(() => {
        lineElement.classList.remove('recently-edited');
        lineElement.removeAttribute('data-editor');
      }, 3000);
    }
  };
  
  // 处理行编辑
  const handleLineEdit = useCallback((lineNumber: number, newContent: string, type: 'en' | 'cn') => {
    // 权限检查
    if (currentUser.role === UserRole.REVIEWER && type === 'cn') {
      toast.error('审核人员无法编辑译文');
      return;
    }
    
    if (type === 'en' && currentUser.role !== UserRole.ADMIN) {
      toast.error('只有管理员可以编辑原文');
      return;
    }
    
    // 本地更新
    if (type === 'en') {
      setEnLines(prev => prev.map((line, idx) => 
        idx === lineNumber ? newContent : line
      ));
    } else {
      setCnLines(prev => prev.map((line, idx) => 
        idx === lineNumber ? newContent : line
      ));
    }
    
    // 发送编辑事件
    if (isConnected && sendMessage) {
      sendMessage({
        type: 'edit',
        data: {
          line_number: lineNumber,
          content: newContent,
          edit_type: type
        }
      });
    }
    
    // 回调通知
    onContentChange?.(lineNumber, newContent, type);
  }, [currentUser.role, isConnected, sendMessage, onContentChange]);
  
  // 处理添加批注
  const handleAddComment = useCallback((lineNumber: number, content: string, commentType: string) => {
    if (isConnected && sendMessage) {
      sendMessage({
        type: 'comment',
        data: {
          line_number: lineNumber,
          content: content,
          comment_type: commentType as CommentType
        }
      });
    }
    
    setSelectedLine(null);
    setIsCommentPanelOpen(false);
  }, [isConnected, sendMessage]);
  
  // 处理行点击
  const handleLineClick = useCallback((lineNumber: number) => {
    setSelectedLine(lineNumber);
    setIsCommentPanelOpen(true);
  }, []);
  
  return (
    <div className="bilingual-editor" ref={editorRef}>
      {/* 协作状态指示器 */}
      <div className="editor-header">
        <CollaborationIndicator 
          users={activeUsers} 
          isConnected={isConnected}
        />
        
        <div className="editor-controls">
          <button
            onClick={() => setIsCommentPanelOpen(!isCommentPanelOpen)}
            className={`comment-toggle ${isCommentPanelOpen ? 'active' : ''}`}
          >
            批注 ({comments.filter(c => !c.is_resolved).length})
          </button>
        </div>
      </div>
      
      {/* 主编辑区域 */}
      <div className="editor-container">
        <div className="editor-content">
          <div className="english-column">
            <h3>English</h3>
            {enLines.map((line, index) => (
              <EditableLine
                key={`en-${index}`}
                id={`line-${index}`}
                content={line}
                lineNumber={index}
                type="en"
                readOnly={currentUser.role !== UserRole.ADMIN}
                onEdit={(content) => handleLineEdit(index, content, 'en')}
                onClick={() => handleLineClick(index)}
                comments={comments.filter(c => c.line_number === index)}
                isSelected={selectedLine === index}
              />
            ))}
          </div>
          
          <div className="chinese-column">
            <h3>中文</h3>
            {cnLines.map((line, index) => (
              <EditableLine
                key={`cn-${index}`}
                content={line}
                lineNumber={index}
                type="cn"
                readOnly={currentUser.role === UserRole.REVIEWER}
                onEdit={(content) => handleLineEdit(index, content, 'cn')}
                onClick={() => handleLineClick(index)}
                comments={comments.filter(c => c.line_number === index)}
                isSelected={selectedLine === index}
              />
            ))}
          </div>
        </div>
        
        {/* 批注面板 */}
        {isCommentPanelOpen && (
          <CommentPanel
            comments={comments}
            selectedLine={selectedLine}
            onAddComment={handleAddComment}
            onClose={() => setIsCommentPanelOpen(false)}
            currentUser={currentUser}
          />
        )}
      </div>
    </div>
  );
};
