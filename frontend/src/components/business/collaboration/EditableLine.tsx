/**
 * 可编辑行组件
 * 支持内联编辑和批注显示
 */
import React, { useState, useRef, useEffect } from 'react';

interface Comment {
  id: string;
  content: string;
  comment_type: string;
  author_name: string;
  is_resolved: boolean;
}

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
      
      {/* 样式 */}
      <style jsx>{`
        .editable-line {
          display: flex;
          align-items: flex-start;
          padding: 0.5rem;
          margin-bottom: 0.5rem;
          border: 1px solid transparent;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.2s ease;
          position: relative;
        }
        
        .editable-line:hover {
          background-color: #f8f9fa;
          border-color: #e9ecef;
        }
        
        .editable-line.selected {
          background-color: #e3f2fd;
          border-color: #2196F3;
        }
        
        .editable-line.has-comments {
          border-left: 3px solid #ff9800;
        }
        
        .editable-line.readonly {
          background-color: #f5f5f5;
        }
        
        .editable-line.editing {
          background-color: #fff;
          border-color: #2196F3;
          box-shadow: 0 2px 8px rgba(33, 150, 243, 0.2);
        }
        
        .line-number {
          min-width: 3rem;
          padding: 0.25rem 0.5rem;
          background-color: #f8f9fa;
          border-radius: 3px;
          font-size: 0.875rem;
          color: #6c757d;
          text-align: center;
          margin-right: 0.75rem;
        }
        
        .line-content {
          flex: 1;
          min-height: 1.5rem;
        }
        
        .display-mode {
          position: relative;
        }
        
        .text-content {
          line-height: 1.6;
          word-wrap: break-word;
          white-space: pre-wrap;
        }
        
        .empty-line {
          color: #adb5bd;
          font-style: italic;
        }
        
        .edit-hint {
          position: absolute;
          top: 0;
          right: 0;
          font-size: 0.75rem;
          color: #6c757d;
          opacity: 0;
          transition: opacity 0.2s ease;
        }
        
        .editable-line:hover .edit-hint {
          opacity: 1;
        }
        
        .edit-mode {
          width: 100%;
        }
        
        .edit-textarea {
          width: 100%;
          min-height: 3rem;
          padding: 0.5rem;
          border: 1px solid #ced4da;
          border-radius: 4px;
          font-family: inherit;
          font-size: inherit;
          line-height: 1.6;
          resize: none;
          outline: none;
        }
        
        .edit-textarea:focus {
          border-color: #2196F3;
          box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
        }
        
        .edit-controls {
          display: flex;
          gap: 0.5rem;
          margin-top: 0.5rem;
        }
        
        .save-btn,
        .cancel-btn {
          padding: 0.25rem 0.75rem;
          border: 1px solid #ced4da;
          border-radius: 3px;
          font-size: 0.875rem;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .save-btn {
          background-color: #28a745;
          color: white;
          border-color: #28a745;
        }
        
        .save-btn:hover {
          background-color: #218838;
        }
        
        .cancel-btn {
          background-color: #6c757d;
          color: white;
          border-color: #6c757d;
        }
        
        .cancel-btn:hover {
          background-color: #5a6268;
        }
        
        .comment-indicator {
          position: absolute;
          top: 0.25rem;
          right: 0.25rem;
          background-color: #ff9800;
          color: white;
          border-radius: 50%;
          width: 1.5rem;
          height: 1.5rem;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.75rem;
          font-weight: bold;
        }
        
        .comment-count {
          line-height: 1;
        }
      `}</style>
    </div>
  );
};
