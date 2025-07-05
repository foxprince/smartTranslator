import React from 'react';
import { User } from '../../../types';

interface CollaborationIndicatorProps {
  users: User[];
  isConnected: boolean;
}

export const CollaborationIndicator: React.FC<CollaborationIndicatorProps> = ({ users, isConnected }) => {
  return (
    <div className="collaboration-indicator">
      <div className="connection-status">
        <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
        <span>{isConnected ? '已连接' : '连接中...'}</span>
      </div>
      <div className="active-users">
        <span>在线用户: {users.filter(u => u.is_online).length}</span>
        <div className="user-list">
          {users.filter(u => u.is_online).map(user => (
            <div key={user.id} className="user-avatar" title={user.username}>
              {user.username.charAt(0).toUpperCase()}
            </div>
          ))}
        </div>
      </div>
      
      <style>{`
        .collaboration-indicator {
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        
        .connection-status {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }
        
        .status-dot.connected {
          background-color: #4caf50;
        }
        
        .status-dot.disconnected {
          background-color: #f44336;
        }
        
        .active-users {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .user-list {
          display: flex;
          gap: 0.25rem;
        }
        
        .user-avatar {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          background-color: #2196f3;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          font-weight: bold;
        }
      `}</style>
    </div>
  );
};