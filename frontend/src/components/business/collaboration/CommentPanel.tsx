import React, { useState } from 'react';
import { Comment, CommentType, UserRole } from '../../../types';

interface CommentPanelProps {
  comments: Comment[];
  selectedLine: number | null;
  onAddComment: (lineNumber: number, content: string, commentType: string) => void;
  onClose: () => void;
  currentUser: {
    id: string;
    username: string;
    role: UserRole;
  };
}

export const CommentPanel: React.FC<CommentPanelProps> = ({
  comments,
  selectedLine,
  onAddComment,
  onClose,
  currentUser
}) => {
  const [commentContent, setCommentContent] = useState('');
  const [commentType, setCommentType] = useState<CommentType>(CommentType.SUGGESTION);

  const handleSubmit = () => {
    if (!commentContent.trim() || selectedLine === null) return;
    
    onAddComment(selectedLine, commentContent, commentType);
    setCommentContent('');
    setCommentType(CommentType.SUGGESTION);
  };

  const selectedLineComments = comments.filter(c => c.line_number === selectedLine);

  return (
    <div className="comment-panel">
      <div className="comment-panel-header">
        <h3>批注</h3>
        <button onClick={onClose} className="close-button">×</button>
      </div>
      
      <div className="comment-panel-content">
        {selectedLine !== null && (
          <div className="add-comment-section">
            <h4>为第 {selectedLine + 1} 行添加批注</h4>
            <div className="comment-type-selector">
              <label>
                <input
                  type="radio"
                  value="suggestion"
                  checked={commentType === CommentType.SUGGESTION}
                  onChange={() => setCommentType(CommentType.SUGGESTION)}
                />
                建议
              </label>
              <label>
                <input
                  type="radio"
                  value="question"
                  checked={commentType === CommentType.QUESTION}
                  onChange={() => setCommentType(CommentType.QUESTION)}
                />
                问题
              </label>
              <label>
                <input
                  type="radio"
                  value="approval"
                  checked={commentType === CommentType.APPROVAL}
                  onChange={() => setCommentType(CommentType.APPROVAL)}
                />
                批准
              </label>
              <label>
                <input
                  type="radio"
                  value="correction"
                  checked={commentType === CommentType.CORRECTION}
                  onChange={() => setCommentType(CommentType.CORRECTION)}
                />
                修正
              </label>
            </div>
            <textarea
              value={commentContent}
              onChange={(e) => setCommentContent(e.target.value)}
              placeholder="请输入批注内容..."
              rows={3}
            />
            <button onClick={handleSubmit} disabled={!commentContent.trim()}>
              添加批注
            </button>
          </div>
        )}
        
        <div className="comments-list">
          <h4>所有批注</h4>
          {selectedLineComments.length === 0 ? (
            <p>暂无批注</p>
          ) : (
            selectedLineComments.map((comment) => (
              <div key={comment.id} className="comment-item">
                <div className="comment-header">
                  <span className="comment-author">{comment.author_name}</span>
                  <span className={`comment-type ${comment.comment_type}`}>
                    {comment.comment_type}
                  </span>
                  <span className="comment-date">
                    {new Date(comment.created_at).toLocaleString()}
                  </span>
                </div>
                <div className="comment-content">{comment.content}</div>
              </div>
            ))
          )}
        </div>
      </div>
      
      <style>{`
        .comment-panel {
          width: 300px;
          background: white;
          border-left: 1px solid #e0e0e0;
          display: flex;
          flex-direction: column;
          max-height: 100%;
        }
        
        .comment-panel-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          border-bottom: 1px solid #e0e0e0;
        }
        
        .close-button {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          color: #666;
        }
        
        .comment-panel-content {
          flex: 1;
          padding: 1rem;
          overflow-y: auto;
        }
        
        .add-comment-section {
          margin-bottom: 1rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid #e0e0e0;
        }
        
        .comment-type-selector {
          display: flex;
          gap: 0.5rem;
          margin: 0.5rem 0;
          flex-wrap: wrap;
        }
        
        .comment-type-selector label {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 14px;
        }
        
        .add-comment-section textarea {
          width: 100%;
          margin: 0.5rem 0;
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          resize: vertical;
        }
        
        .add-comment-section button {
          background: #2196f3;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
        }
        
        .add-comment-section button:disabled {
          background: #ccc;
          cursor: not-allowed;
        }
        
        .comments-list {
          margin-top: 1rem;
        }
        
        .comment-item {
          margin-bottom: 1rem;
          padding: 0.5rem;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
        }
        
        .comment-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
          font-size: 12px;
        }
        
        .comment-author {
          font-weight: bold;
        }
        
        .comment-type {
          padding: 2px 6px;
          border-radius: 3px;
          font-size: 10px;
          text-transform: uppercase;
        }
        
        .comment-type.suggestion {
          background: #e3f2fd;
          color: #1976d2;
        }
        
        .comment-type.question {
          background: #fff3e0;
          color: #f57c00;
        }
        
        .comment-type.approval {
          background: #e8f5e8;
          color: #388e3c;
        }
        
        .comment-type.correction {
          background: #ffebee;
          color: #d32f2f;
        }
        
        .comment-content {
          color: #333;
          line-height: 1.4;
        }
      `}</style>
    </div>
  );
};