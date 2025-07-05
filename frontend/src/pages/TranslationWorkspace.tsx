/**
 * 翻译工作台主页面
 * 集成双语编辑器和协作功能
 */
import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProjectStore } from '../store/projectStore';
import { BilingualEditor } from '../components/business/collaboration/BilingualEditor';
import { NavigationPanel } from '../components/business/NavigationPanel';
import { ProgressTracker } from '../components/business/ProgressTracker';
import { QualityChecker } from '../components/business/QualityChecker';
import { CollaborationInvite } from '../components/business/CollaborationInvite';
import { projectService } from '../services/projectService';
import { UserRole } from '../types';

interface TranslationWorkspaceProps {}

export const TranslationWorkspace: React.FC<TranslationWorkspaceProps> = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const {
    currentProject,
    projectProgress,
    qualityIssues,
    isLoading,
    error,
    loadProject,
    loadProjectProgress,
    runQualityCheck,
    saveTranslation,
    clearError
  } = useProjectStore();

  // 本地状态
  const [collaborationSession, setCollaborationSession] = useState<any>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activePanel, setActivePanel] = useState<'navigation' | 'progress' | 'quality' | 'collaboration'>('navigation');
  const [unsavedChanges, setUnsavedChanges] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  // 当前用户信息（实际应用中从认证系统获取）
  const currentUser = {
    id: 'user-123',
    name: '翻译员',
    role: 'translator' as const
  };

  // 加载项目数据
  useEffect(() => {
    if (projectId) {
      loadProject(projectId);
      loadProjectProgress(projectId);
    }
  }, [projectId, loadProject, loadProjectProgress]);

  // 创建协作会话
  useEffect(() => {
    if (currentProject && !collaborationSession) {
      createCollaborationSession();
    }
  }, [currentProject]);

  // 创建协作会话
  const createCollaborationSession = async () => {
    if (!currentProject) return;

    try {
      const session = await projectService.createCollaborationSession(
        currentProject.id,
        currentUser.id
      );
      setCollaborationSession(session);
    } catch (error) {
      console.error('Failed to create collaboration session:', error);
    }
  };

  // 处理内容变化
  const handleContentChange = useCallback((lineNumber: number, content: string, type: 'en' | 'cn') => {
    if (type === 'cn') {
      setUnsavedChanges(true);
    }
  }, []);

  // 自动保存
  useEffect(() => {
    if (!unsavedChanges || !currentProject) return;

    const saveTimer = setTimeout(async () => {
      try {
        await saveTranslation(currentProject.id, currentProject.translationContent);
        setUnsavedChanges(false);
        setLastSaved(new Date());
      } catch (error) {
        console.error('Auto-save failed:', error);
      }
    }, 2000); // 2秒后自动保存

    return () => clearTimeout(saveTimer);
  }, [unsavedChanges, currentProject, saveTranslation]);

  // 手动保存
  const handleSave = async () => {
    if (!currentProject || !unsavedChanges) return;

    try {
      await saveTranslation(currentProject.id, currentProject.translationContent);
      setUnsavedChanges(false);
      setLastSaved(new Date());
    } catch (error) {
      console.error('Save failed:', error);
    }
  };

  // 运行质量检查
  const handleQualityCheck = () => {
    if (currentProject) {
      runQualityCheck(currentProject.id);
      setActivePanel('quality');
    }
  };

  // 导出项目
  const handleExport = async (format: 'txt' | 'html' | 'pdf') => {
    if (!currentProject) return;

    try {
      const blob = await projectService.exportProject(currentProject.id, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${currentProject.name}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  // 如果项目不存在，跳转到首页
  if (!isLoading && !currentProject && projectId) {
    navigate('/');
    return null;
  }

  // 加载状态
  if (isLoading || !currentProject) {
    return (
      <div className="workspace-loading">
        <div className="loading-spinner">⏳</div>
        <p>加载翻译工作台...</p>
      </div>
    );
  }

  return (
    <div className="translation-workspace">
      {/* 顶部工具栏 */}
      <header className="workspace-header">
        <div className="header-left">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="sidebar-toggle"
          >
            ☰
          </button>
          <h1 className="project-title">{currentProject.name}</h1>
          <div className="project-status">
            <span className={`status-badge ${currentProject.status}`}>
              {currentProject.status}
            </span>
          </div>
        </div>

        <div className="header-center">
          {projectProgress && (
            <div className="progress-info">
              <span>进度: {projectProgress.completionPercentage.toFixed(1)}%</span>
              <div className="progress-bar-mini">
                <div 
                  className="progress-fill"
                  style={{ width: `${projectProgress.completionPercentage}%` }}
                />
              </div>
            </div>
          )}
        </div>

        <div className="header-right">
          <div className="save-status">
            {unsavedChanges ? (
              <span className="unsaved">未保存</span>
            ) : lastSaved ? (
              <span className="saved">已保存 {lastSaved.toLocaleTimeString()}</span>
            ) : null}
          </div>

          <button onClick={handleSave} className="save-btn" disabled={!unsavedChanges}>
            保存
          </button>

          <button onClick={handleQualityCheck} className="quality-btn">
            质量检查
          </button>

          <div className="export-dropdown">
            <button className="export-btn">导出 ▼</button>
            <div className="export-menu">
              <button onClick={() => handleExport('txt')}>导出为TXT</button>
              <button onClick={() => handleExport('html')}>导出为HTML</button>
              <button onClick={() => handleExport('pdf')}>导出为PDF</button>
            </div>
          </div>
        </div>
      </header>

      {/* 主工作区 */}
      <div className="workspace-main">
        {/* 侧边栏 */}
        {sidebarOpen && (
          <aside className="workspace-sidebar">
            <div className="sidebar-tabs">
              <button
                className={`tab ${activePanel === 'navigation' ? 'active' : ''}`}
                onClick={() => setActivePanel('navigation')}
              >
                导航
              </button>
              <button
                className={`tab ${activePanel === 'progress' ? 'active' : ''}`}
                onClick={() => setActivePanel('progress')}
              >
                进度
              </button>
              <button
                className={`tab ${activePanel === 'quality' ? 'active' : ''}`}
                onClick={() => setActivePanel('quality')}
              >
                质量
              </button>
              <button
                className={`tab ${activePanel === 'collaboration' ? 'active' : ''}`}
                onClick={() => setActivePanel('collaboration')}
              >
                协作
              </button>
            </div>

            <div className="sidebar-content">
              {activePanel === 'navigation' && (
                <NavigationPanel
                  content={currentProject.originalContent}
                  onNavigate={(lineNumber) => {
                    // 滚动到指定行
                    const element = document.getElementById(`line-${lineNumber}`);
                    element?.scrollIntoView({ behavior: 'smooth' });
                  }}
                />
              )}

              {activePanel === 'progress' && (
                <ProgressTracker
                  progress={projectProgress}
                  project={currentProject}
                />
              )}

              {activePanel === 'quality' && (
                <QualityChecker
                  issues={qualityIssues}
                  onIssueClick={(lineNumber) => {
                    const element = document.getElementById(`line-${lineNumber}`);
                    element?.scrollIntoView({ behavior: 'smooth' });
                  }}
                />
              )}

              {activePanel === 'collaboration' && (
                <CollaborationInvite
                  projectId={currentProject.id}
                  collaborators={currentProject.collaborators}
                />
              )}
            </div>
          </aside>
        )}

        {/* 编辑器区域 */}
        <main className="workspace-editor">
          {collaborationSession && (
            <BilingualEditor
              sessionId={collaborationSession.session_id}
              initialEnContent={currentProject.originalContent}
              initialCnContent={currentProject.translationContent}
              currentUser={{...currentUser, username: currentUser.name, role: currentUser.role as UserRole}}
              onContentChange={handleContentChange}
            />
          )}
        </main>
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
        .translation-workspace {
          height: 100vh;
          display: flex;
          flex-direction: column;
          background: #f5f5f5;
        }

        .workspace-loading {
          height: 100vh;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          background: #f5f5f5;
        }

        .loading-spinner {
          font-size: 3rem;
          margin-bottom: 1rem;
        }

        .workspace-header {
          background: white;
          border-bottom: 1px solid #e0e0e0;
          padding: 1rem;
          display: flex;
          align-items: center;
          justify-content: space-between;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .header-left {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .sidebar-toggle {
          background: none;
          border: none;
          font-size: 1.25rem;
          cursor: pointer;
          padding: 0.5rem;
          border-radius: 4px;
        }

        .sidebar-toggle:hover {
          background: #f0f0f0;
        }

        .project-title {
          margin: 0;
          font-size: 1.25rem;
          color: #333;
        }

        .status-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.875rem;
          font-weight: 500;
        }

        .status-badge.draft {
          background: #fff3cd;
          color: #856404;
        }

        .status-badge.in_progress {
          background: #d1ecf1;
          color: #0c5460;
        }

        .status-badge.review {
          background: #f8d7da;
          color: #721c24;
        }

        .status-badge.completed {
          background: #d4edda;
          color: #155724;
        }

        .header-center {
          flex: 1;
          display: flex;
          justify-content: center;
        }

        .progress-info {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .progress-bar-mini {
          width: 200px;
          height: 6px;
          background: #e0e0e0;
          border-radius: 3px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: #28a745;
          transition: width 0.3s ease;
        }

        .header-right {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .save-status {
          font-size: 0.875rem;
        }

        .unsaved {
          color: #dc3545;
        }

        .saved {
          color: #28a745;
        }

        .save-btn,
        .quality-btn,
        .export-btn {
          padding: 0.5rem 1rem;
          border: 1px solid #ddd;
          background: white;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .save-btn:hover:not(:disabled),
        .quality-btn:hover,
        .export-btn:hover {
          background: #f8f9fa;
        }

        .save-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .export-dropdown {
          position: relative;
        }

        .export-menu {
          position: absolute;
          top: 100%;
          right: 0;
          background: white;
          border: 1px solid #ddd;
          border-radius: 4px;
          box-shadow: 0 4px 8px rgba(0,0,0,0.1);
          display: none;
          min-width: 150px;
          z-index: 1000;
        }

        .export-dropdown:hover .export-menu {
          display: block;
        }

        .export-menu button {
          display: block;
          width: 100%;
          padding: 0.5rem 1rem;
          border: none;
          background: none;
          text-align: left;
          cursor: pointer;
        }

        .export-menu button:hover {
          background: #f8f9fa;
        }

        .workspace-main {
          flex: 1;
          display: flex;
          overflow: hidden;
        }

        .workspace-sidebar {
          width: 300px;
          background: white;
          border-right: 1px solid #e0e0e0;
          display: flex;
          flex-direction: column;
        }

        .sidebar-tabs {
          display: flex;
          border-bottom: 1px solid #e0e0e0;
        }

        .tab {
          flex: 1;
          padding: 0.75rem;
          border: none;
          background: none;
          cursor: pointer;
          border-bottom: 2px solid transparent;
          transition: all 0.2s ease;
        }

        .tab:hover {
          background: #f8f9fa;
        }

        .tab.active {
          border-bottom-color: #007bff;
          color: #007bff;
        }

        .sidebar-content {
          flex: 1;
          overflow: auto;
          padding: 1rem;
        }

        .workspace-editor {
          flex: 1;
          overflow: hidden;
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
          .workspace-header {
            flex-direction: column;
            gap: 1rem;
            align-items: stretch;
          }

          .header-left,
          .header-center,
          .header-right {
            justify-content: center;
          }

          .workspace-sidebar {
            width: 100%;
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            z-index: 1000;
            transform: translateX(-100%);
            transition: transform 0.3s ease;
          }

          .workspace-sidebar.open {
            transform: translateX(0);
          }

          .progress-bar-mini {
            width: 150px;
          }
        }
      `}</style>
    </div>
  );
};
