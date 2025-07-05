/**
 * 项目仪表盘页面
 * 显示所有翻译项目的概览
 */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProjectStore } from '../store/projectStore';
import { Project, ProjectStatus } from '../types/project';

interface ProjectDashboardProps {}

export const ProjectDashboard: React.FC<ProjectDashboardProps> = () => {
  const navigate = useNavigate();
  const { projects, isLoading, error, loadProjects, deleteProject, clearError } = useProjectStore();
  
  const [filter, setFilter] = useState<'all' | ProjectStatus>('all');
  const [sortBy, setSortBy] = useState<'name' | 'updated' | 'created' | 'progress'>('updated');
  const [searchTerm, setSearchTerm] = useState('');

  // 加载项目列表
  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  // 过滤和排序项目
  const filteredAndSortedProjects = React.useMemo(() => {
    let filtered = projects;

    // 按状态过滤
    if (filter !== 'all') {
      filtered = filtered.filter(project => project.status === filter);
    }

    // 按搜索词过滤
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(project =>
        project.name.toLowerCase().includes(searchLower) ||
        project.description?.toLowerCase().includes(searchLower)
      );
    }

    // 排序
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'created':
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
        case 'updated':
          return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
        case 'progress':
          const aProgress = (a.metadata.completedLines / a.metadata.totalLines) * 100;
          const bProgress = (b.metadata.completedLines / b.metadata.totalLines) * 100;
          return bProgress - aProgress;
        default:
          return 0;
      }
    });

    return filtered;
  }, [projects, filter, sortBy, searchTerm]);

  // 统计数据
  const stats = React.useMemo(() => {
    const total = projects.length;
    const draft = projects.filter(p => p.status === ProjectStatus.DRAFT).length;
    const inProgress = projects.filter(p => p.status === ProjectStatus.IN_PROGRESS).length;
    const review = projects.filter(p => p.status === ProjectStatus.REVIEW).length;
    const completed = projects.filter(p => p.status === ProjectStatus.COMPLETED).length;

    return { total, draft, inProgress, review, completed };
  }, [projects]);

  // 获取状态显示文本
  const getStatusText = (status: ProjectStatus) => {
    switch (status) {
      case ProjectStatus.DRAFT: return '草稿';
      case ProjectStatus.IN_PROGRESS: return '进行中';
      case ProjectStatus.REVIEW: return '审核中';
      case ProjectStatus.COMPLETED: return '已完成';
      case ProjectStatus.ARCHIVED: return '已归档';
      default: return status;
    }
  };

  // 获取状态颜色
  const getStatusColor = (status: ProjectStatus) => {
    switch (status) {
      case ProjectStatus.DRAFT: return '#6c757d';
      case ProjectStatus.IN_PROGRESS: return '#007bff';
      case ProjectStatus.REVIEW: return '#fd7e14';
      case ProjectStatus.COMPLETED: return '#28a745';
      case ProjectStatus.ARCHIVED: return '#6c757d';
      default: return '#6c757d';
    }
  };

  // 计算项目进度
  const getProjectProgress = (project: Project) => {
    return (project.metadata.completedLines / project.metadata.totalLines) * 100;
  };

  // 处理项目删除
  const handleDeleteProject = async (projectId: string, projectName: string) => {
    if (window.confirm(`确定要删除项目"${projectName}"吗？此操作不可撤销。`)) {
      try {
        await deleteProject(projectId);
      } catch (error) {
        console.error('Delete project failed:', error);
      }
    }
  };

  return (
    <div className="project-dashboard">
      {/* 页面头部 */}
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-left">
            <h1>翻译项目</h1>
            <p>管理您的所有翻译项目</p>
          </div>
          <div className="header-right">
            <button
              onClick={() => navigate('/upload')}
              className="create-project-btn"
            >
              + 创建项目
            </button>
          </div>
        </div>
      </header>

      {/* 统计卡片 */}
      <div className="stats-section">
        <div className="stat-card">
          <div className="stat-number">{stats.total}</div>
          <div className="stat-label">总项目</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.inProgress}</div>
          <div className="stat-label">进行中</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.review}</div>
          <div className="stat-label">审核中</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{stats.completed}</div>
          <div className="stat-label">已完成</div>
        </div>
      </div>

      {/* 过滤和搜索 */}
      <div className="filters-section">
        <div className="filters-left">
          <div className="filter-group">
            <label>状态:</label>
            <select value={filter} onChange={(e) => setFilter(e.target.value as any)}>
              <option value="all">全部</option>
              <option value={ProjectStatus.DRAFT}>草稿</option>
              <option value={ProjectStatus.IN_PROGRESS}>进行中</option>
              <option value={ProjectStatus.REVIEW}>审核中</option>
              <option value={ProjectStatus.COMPLETED}>已完成</option>
            </select>
          </div>

          <div className="filter-group">
            <label>排序:</label>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value as any)}>
              <option value="updated">最近更新</option>
              <option value="created">创建时间</option>
              <option value="name">项目名称</option>
              <option value="progress">完成进度</option>
            </select>
          </div>
        </div>

        <div className="filters-right">
          <div className="search-box">
            <input
              type="text"
              placeholder="搜索项目..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <span className="search-icon">🔍</span>
          </div>
        </div>
      </div>

      {/* 项目列表 */}
      <div className="projects-section">
        {isLoading ? (
          <div className="loading-state">
            <div className="loading-spinner">⏳</div>
            <p>加载项目中...</p>
          </div>
        ) : filteredAndSortedProjects.length === 0 ? (
          <div className="empty-state">
            {projects.length === 0 ? (
              <>
                <div className="empty-icon">📝</div>
                <h3>还没有翻译项目</h3>
                <p>创建您的第一个翻译项目开始工作</p>
                <button
                  onClick={() => navigate('/upload')}
                  className="create-first-project-btn"
                >
                  创建项目
                </button>
              </>
            ) : (
              <>
                <div className="empty-icon">🔍</div>
                <h3>没有找到匹配的项目</h3>
                <p>尝试调整搜索条件或过滤器</p>
              </>
            )}
          </div>
        ) : (
          <div className="projects-grid">
            {filteredAndSortedProjects.map((project) => (
              <div key={project.id} className="project-card">
                <div className="project-header">
                  <div className="project-title">
                    <h3>{project.name}</h3>
                    {project.description && (
                      <p className="project-description">{project.description}</p>
                    )}
                  </div>
                  <div className="project-status">
                    <span
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(project.status) }}
                    >
                      {getStatusText(project.status)}
                    </span>
                  </div>
                </div>

                <div className="project-progress">
                  <div className="progress-info">
                    <span>进度: {getProjectProgress(project).toFixed(1)}%</span>
                    <span>{project.metadata.completedLines}/{project.metadata.totalLines} 行</span>
                  </div>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${getProjectProgress(project)}%` }}
                    />
                  </div>
                </div>

                <div className="project-meta">
                  <div className="meta-item">
                    <span className="meta-label">语言对:</span>
                    <span className="meta-value">{project.metadata.languagePair}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">协作者:</span>
                    <span className="meta-value">{project.collaborators.length}人</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">更新:</span>
                    <span className="meta-value">
                      {new Date(project.updatedAt).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="project-actions">
                  <button
                    onClick={() => navigate(`/workspace/${project.id}`)}
                    className="action-btn primary"
                  >
                    打开项目
                  </button>
                  <button
                    onClick={() => navigate(`/project/${project.id}/settings`)}
                    className="action-btn secondary"
                  >
                    设置
                  </button>
                  <button
                    onClick={() => handleDeleteProject(project.id, project.name)}
                    className="action-btn danger"
                  >
                    删除
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="error-toast">
          <span>{error}</span>
          <button onClick={clearError}>✕</button>
        </div>
      )}

      {/* 样式 */}
      {/* @ts-ignore */}
      <style jsx>{`
        .project-dashboard {
          min-height: 100vh;
          background: #f8f9fa;
          padding: 2rem;
        }

        .dashboard-header {
          background: white;
          border-radius: 12px;
          padding: 2rem;
          margin-bottom: 2rem;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .header-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .header-left h1 {
          margin: 0 0 0.5rem 0;
          font-size: 2rem;
          color: #333;
        }

        .header-left p {
          margin: 0;
          color: #666;
        }

        .create-project-btn {
          background: #007bff;
          color: white;
          border: none;
          padding: 0.75rem 1.5rem;
          border-radius: 6px;
          cursor: pointer;
          font-size: 1rem;
          font-weight: 500;
          transition: background-color 0.2s ease;
        }

        .create-project-btn:hover {
          background: #0056b3;
        }

        .stats-section {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
          margin-bottom: 2rem;
        }

        .stat-card {
          background: white;
          padding: 1.5rem;
          border-radius: 8px;
          text-align: center;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .stat-number {
          font-size: 2rem;
          font-weight: bold;
          color: #007bff;
          margin-bottom: 0.5rem;
        }

        .stat-label {
          color: #666;
          font-size: 0.875rem;
        }

        .filters-section {
          background: white;
          padding: 1rem;
          border-radius: 8px;
          margin-bottom: 2rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .filters-left {
          display: flex;
          gap: 1rem;
        }

        .filter-group {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .filter-group label {
          font-size: 0.875rem;
          color: #666;
        }

        .filter-group select {
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.875rem;
        }

        .search-box {
          position: relative;
        }

        .search-box input {
          padding: 0.5rem 2rem 0.5rem 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.875rem;
          width: 250px;
        }

        .search-icon {
          position: absolute;
          right: 0.5rem;
          top: 50%;
          transform: translateY(-50%);
          color: #666;
        }

        .projects-section {
          background: white;
          border-radius: 8px;
          padding: 1rem;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .loading-state,
        .empty-state {
          text-align: center;
          padding: 4rem 2rem;
          color: #666;
        }

        .loading-spinner,
        .empty-icon {
          font-size: 4rem;
          margin-bottom: 1rem;
        }

        .empty-state h3 {
          margin: 0 0 0.5rem 0;
          color: #333;
        }

        .create-first-project-btn {
          background: #007bff;
          color: white;
          border: none;
          padding: 0.75rem 1.5rem;
          border-radius: 6px;
          cursor: pointer;
          font-size: 1rem;
          margin-top: 1rem;
        }

        .projects-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 1.5rem;
        }

        .project-card {
          background: #f8f9fa;
          border: 1px solid #e9ecef;
          border-radius: 8px;
          padding: 1.5rem;
          transition: all 0.2s ease;
        }

        .project-card:hover {
          border-color: #007bff;
          box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        .project-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1rem;
        }

        .project-title h3 {
          margin: 0 0 0.5rem 0;
          font-size: 1.25rem;
          color: #333;
        }

        .project-description {
          margin: 0;
          font-size: 0.875rem;
          color: #666;
          line-height: 1.4;
        }

        .status-badge {
          font-size: 0.75rem;
          color: white;
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-weight: 500;
        }

        .project-progress {
          margin-bottom: 1rem;
        }

        .progress-info {
          display: flex;
          justify-content: space-between;
          font-size: 0.875rem;
          color: #666;
          margin-bottom: 0.5rem;
        }

        .progress-bar {
          height: 6px;
          background: #e9ecef;
          border-radius: 3px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: #007bff;
          transition: width 0.3s ease;
        }

        .project-meta {
          margin-bottom: 1rem;
        }

        .meta-item {
          display: flex;
          justify-content: space-between;
          font-size: 0.875rem;
          margin-bottom: 0.25rem;
        }

        .meta-label {
          color: #666;
        }

        .meta-value {
          color: #333;
          font-weight: 500;
        }

        .project-actions {
          display: flex;
          gap: 0.5rem;
        }

        .action-btn {
          flex: 1;
          padding: 0.5rem;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.875rem;
          transition: all 0.2s ease;
        }

        .action-btn.primary {
          background: #007bff;
          color: white;
        }

        .action-btn.primary:hover {
          background: #0056b3;
        }

        .action-btn.secondary {
          background: #6c757d;
          color: white;
        }

        .action-btn.secondary:hover {
          background: #545b62;
        }

        .action-btn.danger {
          background: #dc3545;
          color: white;
        }

        .action-btn.danger:hover {
          background: #c82333;
        }

        .error-toast {
          position: fixed;
          bottom: 1rem;
          right: 1rem;
          background: #dc3545;
          color: white;
          padding: 1rem;
          border-radius: 4px;
          display: flex;
          align-items: center;
          gap: 1rem;
          box-shadow: 0 4px 8px rgba(0,0,0,0.2);
          z-index: 1000;
        }

        .error-toast button {
          background: none;
          border: none;
          color: white;
          cursor: pointer;
          font-size: 1.25rem;
        }

        @media (max-width: 768px) {
          .project-dashboard {
            padding: 1rem;
          }

          .header-content {
            flex-direction: column;
            gap: 1rem;
            text-align: center;
          }

          .filters-section {
            flex-direction: column;
            gap: 1rem;
            align-items: stretch;
          }

          .filters-left {
            justify-content: center;
          }

          .search-box input {
            width: 100%;
          }

          .projects-grid {
            grid-template-columns: 1fr;
          }

          .project-actions {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};
