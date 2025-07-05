/**
 * 进度跟踪组件
 */
import React from 'react';
import { Project, ProjectProgress } from '../../types/project';

interface ProgressTrackerProps {
  progress: ProjectProgress | null;
  project: Project;
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  progress,
  project
}) => {
  // 计算统计数据
  const stats = {
    totalLines: project.metadata.totalLines,
    translatedLines: project.translationContent.filter(line => line.trim().length > 0).length,
    emptyLines: project.translationContent.filter(line => line.trim().length === 0).length,
    completionRate: progress?.completionPercentage || 0
  };

  // 计算预估完成时间
  const getEstimatedTime = () => {
    if (!progress?.estimatedTimeRemaining) return null;
    
    const hours = Math.floor(progress.estimatedTimeRemaining / 60);
    const minutes = progress.estimatedTimeRemaining % 60;
    
    if (hours > 0) {
      return `${hours}小时${minutes}分钟`;
    }
    return `${minutes}分钟`;
  };

  // 获取进度状态
  const getProgressStatus = () => {
    if (stats.completionRate === 0) return { text: '未开始', color: '#6c757d' };
    if (stats.completionRate < 25) return { text: '刚开始', color: '#dc3545' };
    if (stats.completionRate < 50) return { text: '进行中', color: '#fd7e14' };
    if (stats.completionRate < 75) return { text: '过半', color: '#ffc107' };
    if (stats.completionRate < 100) return { text: '接近完成', color: '#20c997' };
    return { text: '已完成', color: '#28a745' };
  };

  const progressStatus = getProgressStatus();

  return (
    <div className="progress-tracker">
      {/* 总体进度 */}
      <div className="progress-overview">
        <h3>翻译进度</h3>
        
        <div className="progress-circle">
          <svg width="120" height="120" viewBox="0 0 120 120">
            <circle
              cx="60"
              cy="60"
              r="50"
              fill="none"
              stroke="#e9ecef"
              strokeWidth="8"
            />
            <circle
              cx="60"
              cy="60"
              r="50"
              fill="none"
              stroke={progressStatus.color}
              strokeWidth="8"
              strokeDasharray={`${2 * Math.PI * 50}`}
              strokeDashoffset={`${2 * Math.PI * 50 * (1 - stats.completionRate / 100)}`}
              strokeLinecap="round"
              transform="rotate(-90 60 60)"
              style={{ transition: 'stroke-dashoffset 0.5s ease' }}
            />
          </svg>
          <div className="progress-text">
            <div className="progress-percentage">
              {stats.completionRate.toFixed(1)}%
            </div>
            <div className="progress-status" style={{ color: progressStatus.color }}>
              {progressStatus.text}
            </div>
          </div>
        </div>
      </div>

      {/* 详细统计 */}
      <div className="progress-stats">
        <div className="stat-item">
          <div className="stat-label">总行数</div>
          <div className="stat-value">{stats.totalLines}</div>
        </div>
        
        <div className="stat-item">
          <div className="stat-label">已翻译</div>
          <div className="stat-value translated">{stats.translatedLines}</div>
        </div>
        
        <div className="stat-item">
          <div className="stat-label">未翻译</div>
          <div className="stat-value untranslated">
            {stats.totalLines - stats.translatedLines}
          </div>
        </div>
        
        <div className="stat-item">
          <div className="stat-label">空行</div>
          <div className="stat-value empty">{stats.emptyLines}</div>
        </div>
      </div>

      {/* 时间估算 */}
      {getEstimatedTime() && (
        <div className="time-estimate">
          <h4>预估完成时间</h4>
          <div className="estimate-value">
            <span className="time-icon">⏱️</span>
            {getEstimatedTime()}
          </div>
        </div>
      )}

      {/* 每日进度 */}
      <div className="daily-progress">
        <h4>最近7天进度</h4>
        <div className="progress-chart">
          {/* 这里可以集成图表库显示每日进度 */}
          <div className="chart-placeholder">
            <div className="chart-bar" style={{ height: '20%' }}></div>
            <div className="chart-bar" style={{ height: '35%' }}></div>
            <div className="chart-bar" style={{ height: '45%' }}></div>
            <div className="chart-bar" style={{ height: '60%' }}></div>
            <div className="chart-bar" style={{ height: '80%' }}></div>
            <div className="chart-bar" style={{ height: '70%' }}></div>
            <div className="chart-bar" style={{ height: '90%' }}></div>
          </div>
          <div className="chart-labels">
            <span>周一</span>
            <span>周二</span>
            <span>周三</span>
            <span>周四</span>
            <span>周五</span>
            <span>周六</span>
            <span>周日</span>
          </div>
        </div>
      </div>

      {/* 项目信息 */}
      <div className="project-info">
        <h4>项目信息</h4>
        <div className="info-item">
          <span className="info-label">创建时间:</span>
          <span className="info-value">
            {new Date(project.createdAt).toLocaleDateString()}
          </span>
        </div>
        <div className="info-item">
          <span className="info-label">最后更新:</span>
          <span className="info-value">
            {new Date(project.updatedAt).toLocaleDateString()}
          </span>
        </div>
        <div className="info-item">
          <span className="info-label">语言对:</span>
          <span className="info-value">{project.metadata.languagePair}</span>
        </div>
        <div className="info-item">
          <span className="info-label">协作者:</span>
          <span className="info-value">{project.collaborators.length}人</span>
        </div>
      </div>

      {/* 样式 */}
      {/* @ts-ignore */}
      <style jsx>{`
        .progress-tracker {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .progress-overview {
          text-align: center;
        }

        .progress-overview h3 {
          margin: 0 0 1rem 0;
          font-size: 1.1rem;
          color: #333;
        }

        .progress-circle {
          position: relative;
          display: inline-block;
        }

        .progress-text {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          text-align: center;
        }

        .progress-percentage {
          font-size: 1.5rem;
          font-weight: bold;
          color: #333;
          margin-bottom: 0.25rem;
        }

        .progress-status {
          font-size: 0.875rem;
          font-weight: 500;
        }

        .progress-stats {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }

        .stat-item {
          text-align: center;
          padding: 1rem;
          background: #f8f9fa;
          border-radius: 8px;
        }

        .stat-label {
          font-size: 0.875rem;
          color: #666;
          margin-bottom: 0.5rem;
        }

        .stat-value {
          font-size: 1.25rem;
          font-weight: bold;
          color: #333;
        }

        .stat-value.translated {
          color: #28a745;
        }

        .stat-value.untranslated {
          color: #dc3545;
        }

        .stat-value.empty {
          color: #6c757d;
        }

        .time-estimate {
          background: #e3f2fd;
          padding: 1rem;
          border-radius: 8px;
          text-align: center;
        }

        .time-estimate h4 {
          margin: 0 0 0.5rem 0;
          font-size: 1rem;
          color: #1976d2;
        }

        .estimate-value {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          font-size: 1.1rem;
          font-weight: 500;
          color: #1976d2;
        }

        .daily-progress h4 {
          margin: 0 0 1rem 0;
          font-size: 1rem;
          color: #333;
        }

        .progress-chart {
          background: #f8f9fa;
          padding: 1rem;
          border-radius: 8px;
        }

        .chart-placeholder {
          display: flex;
          align-items: end;
          justify-content: space-between;
          height: 80px;
          margin-bottom: 0.5rem;
        }

        .chart-bar {
          width: 12px;
          background: linear-gradient(to top, #007bff, #66b3ff);
          border-radius: 2px 2px 0 0;
          transition: height 0.3s ease;
        }

        .chart-labels {
          display: flex;
          justify-content: space-between;
          font-size: 0.75rem;
          color: #666;
        }

        .project-info h4 {
          margin: 0 0 1rem 0;
          font-size: 1rem;
          color: #333;
        }

        .info-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.5rem 0;
          border-bottom: 1px solid #f0f0f0;
        }

        .info-item:last-child {
          border-bottom: none;
        }

        .info-label {
          font-size: 0.875rem;
          color: #666;
        }

        .info-value {
          font-size: 0.875rem;
          color: #333;
          font-weight: 500;
        }
      `}</style>
    </div>
  );
};
