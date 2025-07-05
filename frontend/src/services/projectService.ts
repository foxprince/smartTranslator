/**
 * 项目管理服务
 */
import { apiClient } from './api';
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
      originalContent: preprocessResult.cleaned_content.split('\n'),
      metadata: {
        title: request.name,
        languagePair: 'en-zh',
        totalLines: preprocessResult.processing_report.cleaned_stats.totalLines,
        completedLines: 0,
        processingReport: preprocessResult.processing_report
      }
    };

    return apiClient.post<Project>('/projects', projectData);
  }

  /**
   * 文档预处理（集成故事9）
   */
  async preprocessDocument(file: File) {
    const fileContent = await file.text();
    
    return apiClient.post('/documents/preprocess', {
      file_content: fileContent,
      filename: file.name
    });
  }

  /**
   * 获取项目列表
   */
  async getProjects(): Promise<Project[]> {
    return apiClient.get<Project[]>('/projects');
  }

  /**
   * 获取项目详情
   */
  async getProject(projectId: string): Promise<Project> {
    return apiClient.get<Project>(`/projects/${projectId}`);
  }

  /**
   * 更新项目
   */
  async updateProject(projectId: string, updates: Partial<Project>): Promise<Project> {
    return apiClient.put<Project>(`/projects/${projectId}`, updates);
  }

  /**
   * 删除项目
   */
  async deleteProject(projectId: string): Promise<void> {
    return apiClient.delete(`/projects/${projectId}`);
  }

  /**
   * 获取项目进度
   */
  async getProjectProgress(projectId: string): Promise<ProjectProgress> {
    return apiClient.get<ProjectProgress>(`/projects/${projectId}/progress`);
  }

  /**
   * 运行质量检查
   */
  async runQualityCheck(projectId: string): Promise<QualityIssue[]> {
    return apiClient.post<QualityIssue[]>(`/projects/${projectId}/quality-check`);
  }

  /**
   * 创建协作会话（集成故事10）
   */
  async createCollaborationSession(projectId: string, userId: string) {
    const project = await this.getProject(projectId);
    
    return apiClient.post('/collaboration/create-session', {
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
  }

  /**
   * 保存翻译内容
   */
  async saveTranslation(projectId: string, content: string[]): Promise<void> {
    return apiClient.put(`/projects/${projectId}/translation`, {
      translationContent: content
    });
  }

  /**
   * 邀请协作者
   */
  async inviteCollaborator(projectId: string, email: string, role: string): Promise<void> {
    return apiClient.post(`/projects/${projectId}/collaborators`, {
      email,
      role
    });
  }

  /**
   * 导出项目
   */
  async exportProject(projectId: string, format: 'txt' | 'html' | 'pdf'): Promise<Blob> {
    const response = await fetch(`${apiClient['baseURL']}/projects/${projectId}/export?format=${format}`);
    
    if (!response.ok) {
      throw new Error('Export failed');
    }
    
    return response.blob();
  }
}

export const projectService = new ProjectService();
