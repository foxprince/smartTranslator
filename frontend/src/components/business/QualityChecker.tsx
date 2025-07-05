/**
 * 质量检查组件
 */
import React, { useState } from 'react';
import { QualityIssue } from '../../types/project';

interface QualityCheckerProps {
  issues: QualityIssue[];
  onIssueClick: (lineNumber: number) => void;
}

export const QualityChecker: React.FC<QualityCheckerProps> = ({
  issues,
  onIssueClick
}) => {
  const [filter, setFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [typeFilter, setTypeFilter] = useState<'all' | 'alignment' | 'translation' | 'formatting'>('all');

  // 过滤问题
  const filteredIssues = issues.filter(issue => {
    if (filter !== 'all' && issue.severity !== filter) return false;
    if (typeFilter !== 'all' && issue.type !== typeFilter) return false;
    return true;
  });

  // 按严重程度分组
  const issuesByType = {
    high: filteredIssues.filter(issue => issue.severity === 'high'),
    medium: filteredIssues.filter(issue => issue.severity === 'medium'),
    low: filteredIssues.filter(issue => issue.severity === 'low')
  };

  // 获取问题图标
  const getIssueIcon = (type: string) => {
    switch (type) {
      case 'alignment': return '🔗';
      case 'translation': return '🔤';
      case 'formatting': return '📝';
      default: return '⚠️';
    }
  };

  // 获取严重程度颜色
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return '#dc3545';
      case 'medium': return '#fd7e14';
      case 'low': return '#ffc107';
      default: return '#6c757d';
    }
  };

  // 获取严重程度文本
  const getSeverityText = (severity: string) => {
    switch (severity) {
      case 'high': return '严重';
      case 'medium': return '中等';
      case 'low': return '轻微';
      default: return '未知';
    }
  };

  return (
    <div className="quality-checker">
      {/* 质量概览 */}
      <div className="quality-overview">
        <h3>质量检查</h3>
        
        <div className="quality-summary">
          <div className="summary-item">
            <div className="summary-count">{issues.length}</div>
            <div className="summary-label">总问题</div>
          </div>
          <div className="summary-item high">
            <div className="summary-count">{issuesByType.high.length}</div>
            <div className="summary-label">严重</div>
          </div>
          <div className="summary-item medium">
            <div className="summary-count">{issuesByType.medium.length}</div>
            <div className="summary-label">中等</div>
          </div>
          <div className="summary-item low">
            <div className="summary-count">{issuesByType.low.length}</div>
            <div className="summary-label">轻微</div>
          </div>
        </div>
      </div>

      {/* 过滤器 */}
      <div className="quality-filters">
        <div className="filter-group">
          <label>严重程度:</label>
          <select value={filter} onChange={(e) => setFilter(e.target.value as any)}>
            <option value="all">全部</option>
            <option value="high">严重</option>
            <option value="medium">中等</option>
            <option value="low">轻微</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>问题类型:</label>
          <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value as any)}>
            <option value="all">全部</option>
            <option value="alignment">对齐问题</option>
            <option value="translation">翻译问题</option>
            <option value="formatting">格式问题</option>
          </select>
        </div>
      </div>

      {/* 问题列表 */}
      <div className="issues-list">
        {filteredIssues.length === 0 ? (
          <div className="no-issues">
            {issues.length === 0 ? (
              <>
                <div className="no-issues-icon">✅</div>
                <p>暂无质量问题</p>
                <p className="hint">运行质量检查来发现潜在问题</p>
              </>
            ) : (
              <>
                <div className="no-issues-icon">🔍</div>
                <p>没有符合条件的问题</p>
                <p className="hint">尝试调整过滤条件</p>
              </>
            )}
          </div>
        ) : (
          filteredIssues.map((issue) => (
            <div
              key={issue.id}
              className={`issue-item ${issue.severity} ${issue.isResolved ? 'resolved' : ''}`}
              onClick={() => onIssueClick(issue.lineNumber)}
            >
              <div className="issue-header">
                <div className="issue-icon">
                  {getIssueIcon(issue.type)}
                </div>
                <div className="issue-info">
                  <div className="issue-title">
                    第 {issue.lineNumber + 1} 行 - {issue.description}
                  </div>
                  <div className="issue-meta">
                    <span 
                      className="severity-badge"
                      style={{ backgroundColor: getSeverityColor(issue.severity) }}
                    >
                      {getSeverityText(issue.severity)}
                    </span>
                    <span className="issue-type">
                      {issue.type === 'alignment' && '对齐问题'}
                      {issue.type === 'translation' && '翻译问题'}
                      {issue.type === 'formatting' && '格式问题'}
                    </span>
                  </div>
                </div>
                <div className="issue-status">
                  {issue.isResolved ? (
                    <span className="resolved-badge">已解决</span>
                  ) : (
                    <span className="unresolved-badge">待解决</span>
                  )}
                </div>
              </div>
              
              {issue.suggestion && (
                <div className="issue-suggestion">
                  <strong>建议:</strong> {issue.suggestion}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* 质量建议 */}
      {issues.length > 0 && (
        <div className="quality-tips">
          <h4>质量提升建议</h4>
          <ul>
            {issuesByType.high.length > 0 && (
              <li>优先处理 {issuesByType.high.length} 个严重问题</li>
            )}
            {issuesByType.medium.length > 0 && (
              <li>关注 {issuesByType.medium.length} 个中等问题</li>
            )}
            <li>定期运行质量检查确保翻译质量</li>
            <li>使用协作功能邀请审核人员</li>
          </ul>
        </div>
      )}

      {/* 样式 */}
      <style jsx>{`
        .quality-checker {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .quality-overview h3 {
          margin: 0 0 1rem 0;
          font-size: 1.1rem;
          color: #333;
        }

        .quality-summary {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 0.5rem;
        }

        .summary-item {
          text-align: center;
          padding: 0.75rem;
          background: #f8f9fa;
          border-radius: 6px;
          border-left: 3px solid #6c757d;
        }

        .summary-item.high {
          border-left-color: #dc3545;
        }

        .summary-item.medium {
          border-left-color: #fd7e14;
        }

        .summary-item.low {
          border-left-color: #ffc107;
        }

        .summary-count {
          font-size: 1.25rem;
          font-weight: bold;
          color: #333;
          margin-bottom: 0.25rem;
        }

        .summary-label {
          font-size: 0.75rem;
          color: #666;
        }

        .quality-filters {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
        }

        .filter-group {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .filter-group label {
          font-size: 0.875rem;
          color: #666;
        }

        .filter-group select {
          padding: 0.25rem 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.875rem;
        }

        .issues-list {
          flex: 1;
          overflow-y: auto;
        }

        .no-issues {
          text-align: center;
          padding: 2rem 1rem;
          color: #666;
        }

        .no-issues-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
        }

        .no-issues p {
          margin: 0.5rem 0;
        }

        .hint {
          font-size: 0.875rem;
          color: #999;
        }

        .issue-item {
          background: white;
          border: 1px solid #e0e0e0;
          border-radius: 6px;
          margin-bottom: 0.5rem;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .issue-item:hover {
          border-color: #007bff;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .issue-item.resolved {
          opacity: 0.6;
          background: #f8f9fa;
        }

        .issue-header {
          display: flex;
          align-items: flex-start;
          padding: 0.75rem;
          gap: 0.75rem;
        }

        .issue-icon {
          font-size: 1.25rem;
          margin-top: 0.125rem;
        }

        .issue-info {
          flex: 1;
        }

        .issue-title {
          font-size: 0.875rem;
          color: #333;
          margin-bottom: 0.5rem;
          line-height: 1.4;
        }

        .issue-meta {
          display: flex;
          gap: 0.5rem;
          align-items: center;
        }

        .severity-badge {
          font-size: 0.75rem;
          color: white;
          padding: 0.125rem 0.5rem;
          border-radius: 10px;
          font-weight: 500;
        }

        .issue-type {
          font-size: 0.75rem;
          color: #666;
        }

        .issue-status {
          display: flex;
          align-items: center;
        }

        .resolved-badge {
          font-size: 0.75rem;
          color: #28a745;
          background: #d4edda;
          padding: 0.125rem 0.5rem;
          border-radius: 10px;
        }

        .unresolved-badge {
          font-size: 0.75rem;
          color: #dc3545;
          background: #f8d7da;
          padding: 0.125rem 0.5rem;
          border-radius: 10px;
        }

        .issue-suggestion {
          padding: 0 0.75rem 0.75rem 2.5rem;
          font-size: 0.875rem;
          color: #666;
          background: #f8f9fa;
          margin-top: -0.25rem;
          border-radius: 0 0 6px 6px;
        }

        .quality-tips {
          background: #e3f2fd;
          padding: 1rem;
          border-radius: 6px;
        }

        .quality-tips h4 {
          margin: 0 0 0.5rem 0;
          font-size: 1rem;
          color: #1976d2;
        }

        .quality-tips ul {
          margin: 0;
          padding-left: 1.25rem;
        }

        .quality-tips li {
          font-size: 0.875rem;
          color: #1976d2;
          margin-bottom: 0.25rem;
        }
      `}</style>
    </div>
  );
};
