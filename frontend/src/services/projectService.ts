/**
 * 项目管理服务
 */
import api from './api';
import { Project, CreateProjectRequest, ProjectProgress, QualityIssue } from '../types/project';

export class ProjectService {
  /**
   * 创建新项目（包含文档预处理）
   */
  async createProject(request: CreateProjectRequest): Promise<Project> {
    // 1. 先调用文档预处理
    const preprocessResult = await this.preprocessDocument(request.file);
    
    // 2. 创建项目
    const projectData = {
      name: request.name,
      description: request.description,
      originalContent: preprocessResult.data.cleaned_content.split('\n'),
      metadata: {
        title: request.name,
        languagePair: 'en-zh',
        totalLines: preprocessResult.data.processing_report.cleaned_stats.totalLines,
        completedLines: 0,
        processingReport: preprocessResult.data.processing_report
      }
    };

    const response = await api.post<Project>('/projects', projectData);
    return response.data;
  }

  /**
   * 文档预处理（集成故事9）
   */
  async preprocessDocument(file: File) {
    const fileContent = await file.text();
    
    return api.post('/documents/preprocess', {
      file_content: fileContent,
      filename: file.name
    });
  }

  /**
   * 获取项目列表
   */
  async getProjects(): Promise<Project[]> {
    const response = await api.get<Project[]>('/projects');
    return response.data;
  }

  /**
   * 获取项目详情
   */
  async getProject(projectId: string): Promise<Project> {
    const response = await api.get<Project>(`/projects/${projectId}`);
    return response.data;
  }

  /**
   * 更新项目
   */
  async updateProject(projectId: string, updates: Partial<Project>): Promise<Project> {
    const response = await api.put<Project>(`/projects/${projectId}`, updates);
    return response.data;
  }

  /**
   * 删除项目
   */
  async deleteProject(projectId: string): Promise<void> {
    await api.delete(`/projects/${projectId}`);
  }

  /**
   * 获取项目进度
   */
  async getProjectProgress(projectId: string): Promise<ProjectProgress> {
    const response = await api.get<ProjectProgress>(`/projects/${projectId}/progress`);
    return response.data;
  }

  /**
   * 运行质量检查
   */
  async runQualityCheck(projectId: string): Promise<QualityIssue[]> {
    const response = await api.post<QualityIssue[]>(`/projects/${projectId}/quality-check`);
    return response.data;
  }

  /**
   * 创建协作会话（集成故事10）
   */
  async createCollaborationSession(projectId: string, userId: string) {
    const project = await this.getProject(projectId);
    
    const response = await api.post('/collaboration/create-session', {
      document_id: projectId,
      en_content: project.originalContent,
      cn_content: project.translationContent,
      metadata: {
        title: project.name,
        total_lines: project.metadata.totalLines,
        created_at: new Date().toISOString()
      },
      creator_id: userId
    });
    return response.data;
  }

  /**
   * 保存翻译内容
   */
  async saveTranslation(projectId: string, content: string[]): Promise<void> {
    await api.put(`/projects/${projectId}/translation`, {
      translationContent: content
    });
  }

  /**
   * 邀请协作者
   */
  async inviteCollaborator(projectId: string, email: string, role: string): Promise<void> {
    await api.post(`/projects/${projectId}/collaborators`, {
      email,
      role
    });
  }

  /**
   * 导出项目
   */
  async exportProject(projectId: string, format: 'txt' | 'html' | 'pdf'): Promise<Blob> {
    const response = await fetch(`${process.env.REACT_APP_API_BASE_URL || '/api'}/projects/${projectId}/export?format=${format}`);
    
    if (!response.ok) {
      throw new Error('Export failed');
    }
    
    return response.blob();
  }
}

export const projectService = new ProjectService();
