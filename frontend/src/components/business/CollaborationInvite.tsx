/**
 * 协作邀请组件
 */
import React, { useState } from 'react';
import { Collaborator } from '../../types/project';
import { projectService } from '../../services/projectService';

interface CollaborationInviteProps {
  projectId: string;
  collaborators: Collaborator[];
}

export const CollaborationInvite: React.FC<CollaborationInviteProps> = ({
  projectId,
  collaborators
}) => {
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<'translator' | 'reviewer'>('reviewer');
  const [isInviting, setIsInviting] = useState(false);
  const [inviteError, setInviteError] = useState('');
  const [showInviteForm, setShowInviteForm] = useState(false);

  // 处理邀请提交
  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inviteEmail.trim()) {
      setInviteError('请输入邮箱地址');
      return;
    }

    // 简单的邮箱验证
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(inviteEmail)) {
      setInviteError('请输入有效的邮箱地址');
      return;
    }

    // 检查是否已经邀请过
    const existingCollaborator = collaborators.find(
      c => c.name.toLowerCase() === inviteEmail.toLowerCase()
    );
    if (existingCollaborator) {
      setInviteError('该用户已经是协作者');
      return;
    }

    setIsInviting(true);
    setInviteError('');

    try {
      await projectService.inviteCollaborator(projectId, inviteEmail, inviteRole);
      
      // 重置表单
      setInviteEmail('');
      setInviteRole('reviewer');
      setShowInviteForm(false);
      
      // 这里应该刷新协作者列表，但由于是演示，我们只显示成功消息
      alert('邀请已发送！');
    } catch (error) {
      setInviteError(error instanceof Error ? error.message : '邀请失败');
    } finally {
      setIsInviting(false);
    }
  };

  // 获取角色显示文本
  const getRoleText = (role: string) => {
    switch (role) {
      case 'translator': return '翻译员';
      case 'reviewer': return '审核员';
      case 'admin': return '管理员';
      default: return role;
    }
  };

  // 获取角色颜色
  const getRoleColor = (role: string) => {
    switch (role) {
      case 'translator': return '#007bff';
      case 'reviewer': return '#28a745';
      case 'admin': return '#dc3545';
      default: return '#6c757d';
    }
  };

  // 获取状态显示文本
  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '在线';
      case 'inactive': return '离线';
      default: return status;
    }
  };

  return (
    <div className="collaboration-invite">
      {/* 协作者列表 */}
      <div className="collaborators-section">
        <div className="section-header">
          <h3>协作者</h3>
          <span className="collaborator-count">{collaborators.length}人</span>
        </div>

        <div className="collaborators-list">
          {collaborators.length === 0 ? (
            <div className="no-collaborators">
              <div className="no-collaborators-icon">👥</div>
              <p>暂无协作者</p>
              <p className="hint">邀请他人一起完成翻译工作</p>
            </div>
          ) : (
            collaborators.map((collaborator) => (
              <div key={collaborator.id} className="collaborator-item">
                <div className="collaborator-avatar">
                  {collaborator.name.charAt(0).toUpperCase()}
                </div>
                <div className="collaborator-info">
                  <div className="collaborator-name">{collaborator.name}</div>
                  <div className="collaborator-meta">
                    <span 
                      className="role-badge"
                      style={{ backgroundColor: getRoleColor(collaborator.role) }}
                    >
                      {getRoleText(collaborator.role)}
                    </span>
                    <span className={`status-indicator ${collaborator.status}`}>
                      {getStatusText(collaborator.status)}
                    </span>
                  </div>
                </div>
                <div className="collaborator-actions">
                  <button className="action-btn" title="发送消息">
                    💬
                  </button>
                  <button className="action-btn" title="更多操作">
                    ⋯
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* 邀请按钮 */}
      <div className="invite-section">
        {!showInviteForm ? (
          <button
            onClick={() => setShowInviteForm(true)}
            className="invite-btn"
          >
            + 邀请协作者
          </button>
        ) : (
          <div className="invite-form">
            <div className="form-header">
              <h4>邀请协作者</h4>
              <button
                onClick={() => {
                  setShowInviteForm(false);
                  setInviteError('');
                  setInviteEmail('');
                }}
                className="close-btn"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleInvite}>
              <div className="form-group">
                <label htmlFor="inviteEmail">邮箱地址</label>
                <input
                  id="inviteEmail"
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="输入邀请者的邮箱"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="inviteRole">角色</label>
                <select
                  id="inviteRole"
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value as any)}
                >
                  <option value="reviewer">审核员 - 可添加批注和审核</option>
                  <option value="translator">翻译员 - 可编辑翻译内容</option>
                </select>
              </div>

              {inviteError && (
                <div className="error-message">
                  {inviteError}
                </div>
              )}

              <div className="form-actions">
                <button
                  type="button"
                  onClick={() => setShowInviteForm(false)}
                  className="cancel-btn"
                  disabled={isInviting}
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="submit-btn"
                  disabled={isInviting}
                >
                  {isInviting ? '发送中...' : '发送邀请'}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>

      {/* 协作提示 */}
      <div className="collaboration-tips">
        <h4>协作说明</h4>
        <ul>
          <li><strong>翻译员:</strong> 可以编辑译文内容，添加批注</li>
          <li><strong>审核员:</strong> 可以查看翻译，添加批注和建议</li>
          <li><strong>实时同步:</strong> 所有修改都会实时同步给协作者</li>
          <li><strong>版本控制:</strong> 系统会自动保存编辑历史</li>
        </ul>
      </div>

      {/* 样式 */}
      {/* @ts-ignore */}
      <style jsx>{`
        .collaboration-invite {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .section-header h3 {
          margin: 0;
          font-size: 1.1rem;
          color: #333;
        }

        .collaborator-count {
          font-size: 0.75rem;
          color: #666;
          background: #f0f0f0;
          padding: 0.25rem 0.5rem;
          border-radius: 12px;
        }

        .collaborators-list {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .no-collaborators {
          text-align: center;
          padding: 2rem 1rem;
          color: #666;
        }

        .no-collaborators-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
        }

        .no-collaborators p {
          margin: 0.5rem 0;
        }

        .hint {
          font-size: 0.875rem;
          color: #999;
        }

        .collaborator-item {
          display: flex;
          align-items: center;
          padding: 0.75rem;
          background: #f8f9fa;
          border-radius: 8px;
          gap: 0.75rem;
        }

        .collaborator-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: #007bff;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 1.1rem;
        }

        .collaborator-info {
          flex: 1;
        }

        .collaborator-name {
          font-weight: 500;
          color: #333;
          margin-bottom: 0.25rem;
        }

        .collaborator-meta {
          display: flex;
          gap: 0.5rem;
          align-items: center;
        }

        .role-badge {
          font-size: 0.75rem;
          color: white;
          padding: 0.125rem 0.5rem;
          border-radius: 10px;
          font-weight: 500;
        }

        .status-indicator {
          font-size: 0.75rem;
          padding: 0.125rem 0.5rem;
          border-radius: 10px;
        }

        .status-indicator.active {
          color: #28a745;
          background: #d4edda;
        }

        .status-indicator.inactive {
          color: #6c757d;
          background: #e9ecef;
        }

        .collaborator-actions {
          display: flex;
          gap: 0.25rem;
        }

        .action-btn {
          background: none;
          border: none;
          cursor: pointer;
          padding: 0.25rem;
          border-radius: 4px;
          font-size: 1rem;
        }

        .action-btn:hover {
          background: #e9ecef;
        }

        .invite-btn {
          width: 100%;
          padding: 0.75rem;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.875rem;
          font-weight: 500;
          transition: background-color 0.2s ease;
        }

        .invite-btn:hover {
          background: #0056b3;
        }

        .invite-form {
          background: white;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          padding: 1rem;
        }

        .form-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .form-header h4 {
          margin: 0;
          font-size: 1rem;
          color: #333;
        }

        .close-btn {
          background: none;
          border: none;
          cursor: pointer;
          font-size: 1.25rem;
          color: #666;
          padding: 0.25rem;
        }

        .form-group {
          margin-bottom: 1rem;
        }

        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-size: 0.875rem;
          color: #555;
          font-weight: 500;
        }

        .form-group input,
        .form-group select {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.875rem;
        }

        .form-group input:focus,
        .form-group select:focus {
          outline: none;
          border-color: #007bff;
        }

        .error-message {
          background: #f8d7da;
          color: #721c24;
          padding: 0.5rem;
          border-radius: 4px;
          font-size: 0.875rem;
          margin-bottom: 1rem;
        }

        .form-actions {
          display: flex;
          gap: 0.5rem;
          justify-content: flex-end;
        }

        .cancel-btn,
        .submit-btn {
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.875rem;
          transition: all 0.2s ease;
        }

        .cancel-btn {
          background: #f8f9fa;
          color: #666;
          border: 1px solid #ddd;
        }

        .cancel-btn:hover:not(:disabled) {
          background: #e9ecef;
        }

        .submit-btn {
          background: #007bff;
          color: white;
        }

        .submit-btn:hover:not(:disabled) {
          background: #0056b3;
        }

        .submit-btn:disabled,
        .cancel-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .collaboration-tips {
          background: #e8f4fd;
          padding: 1rem;
          border-radius: 6px;
        }

        .collaboration-tips h4 {
          margin: 0 0 0.5rem 0;
          font-size: 1rem;
          color: #1976d2;
        }

        .collaboration-tips ul {
          margin: 0;
          padding-left: 1.25rem;
        }

        .collaboration-tips li {
          font-size: 0.875rem;
          color: #1976d2;
          margin-bottom: 0.25rem;
          line-height: 1.4;
        }
      `}</style>
    </div>
  );
};
