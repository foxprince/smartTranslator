/**
 * 可编辑行组件
 * 支持内联编辑和批注显示
 */
import React, { useState, useRef, useEffect } from 'react';
import { Comment } from '../../../types';
import './EditableLine.css';

interface EditableLineProps {
  id?: string;
  content: string;
  lineNumber: number;
  type: 'en' | 'cn';
  readOnly?: boolean;
  onEdit: (content: string) => void;
  onClick?: () => void;
  comments?: Comment[];
  isSelected?: boolean;
}

export const EditableLine: React.FC<EditableLineProps> = ({
  id,
  content,
  lineNumber,
  type,
  readOnly = false,
  onEdit,
  onClick,
  comments = [],
  isSelected = false
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(content);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const lineRef = useRef<HTMLDivElement>(null);
  
  // 同步外部内容变化
  useEffect(() => {
    if (!isEditing) {
      setEditContent(content);
    }
  }, [content, isEditing]);
  
  // 编辑模式下自动聚焦和调整高度
  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.focus();
      adjustTextareaHeight();
    }
  }, [isEditing]);
  
  // 调整textarea高度
  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  };
  
  // 开始编辑
  const startEdit = () => {
    if (readOnly) return;
    setIsEditing(true);
  };
  
  // 保存编辑
  const saveEdit = () => {
    if (editContent !== content) {
      onEdit(editContent);
    }
    setIsEditing(false);
  };
  
  // 取消编辑
  const cancelEdit = () => {
    setEditContent(content);
    setIsEditing(false);
  };
  
  // 处理键盘事件
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      saveEdit();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      cancelEdit();
    }
  };
  
  // 处理点击事件
  const handleClick = (e: React.MouseEvent) => {
    if (!isEditing) {
      onClick?.();
    }
  };
  
  // 处理双击编辑
  const handleDoubleClick = () => {
    if (!readOnly) {
      startEdit();
    }
  };
  
  // 获取行样式类
  const getLineClasses = () => {
    const classes = ['editable-line'];
    
    if (isSelected) classes.push('selected');
    if (comments.length > 0) classes.push('has-comments');
    if (readOnly) classes.push('readonly');
    if (isEditing) classes.push('editing');
    
    return classes.join(' ');
  };
  
  // 获取批注指示器
  const getCommentIndicator = () => {
    if (comments.length === 0) return null;
    
    const unresolvedCount = comments.filter(c => !c.is_resolved).length;
    
    return (
      <div className="comment-indicator" title={`${comments.length} 条批注`}>
        <span className="comment-count">{unresolvedCount || comments.length}</span>
      </div>
    );
  };
  
  return (
    <div
      id={id}
      ref={lineRef}
      className={getLineClasses()}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
    >
      <div className="line-number">{lineNumber + 1}</div>
      
      <div className="line-content">
        {isEditing ? (
          <div className="edit-mode">
            <textarea
              ref={textareaRef}
              value={editContent}
              onChange={(e) => {
                setEditContent(e.target.value);
                adjustTextareaHeight();
              }}
              onKeyDown={handleKeyDown}
              onBlur={saveEdit}
              className="edit-textarea"
              placeholder="输入内容..."
            />
            <div className="edit-controls">
              <button onClick={saveEdit} className="save-btn">
                保存 (Ctrl+Enter)
              </button>
              <button onClick={cancelEdit} className="cancel-btn">
                取消 (Esc)
              </button>
            </div>
          </div>
        ) : (
          <div className="display-mode">
            <div className="text-content">
              {content || <span className="empty-line">空行</span>}
            </div>
            {!readOnly && (
              <div className="edit-hint">双击编辑</div>
            )}
          </div>
        )}
      </div>
      
      {getCommentIndicator()}
    </div>
  );
};
