/**
 * 项目状态管理
 * 使用Zustand进行状态管理
 */
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { Project, ProjectProgress, QualityIssue } from '../types/project';
import { projectService } from '../services/projectService';

interface ProjectState {
  // 状态
  projects: Project[];
  currentProject: Project | null;
  projectProgress: ProjectProgress | null;
  qualityIssues: QualityIssue[];
  isLoading: boolean;
  error: string | null;

  // 操作
  loadProjects: () => Promise<void>;
  loadProject: (projectId: string) => Promise<void>;
  createProject: (name: string, description: string, file: File) => Promise<Project>;
  updateProject: (projectId: string, updates: Partial<Project>) => Promise<void>;
  deleteProject: (projectId: string) => Promise<void>;
  loadProjectProgress: (projectId: string) => Promise<void>;
  runQualityCheck: (projectId: string) => Promise<void>;
  saveTranslation: (projectId: string, content: string[]) => Promise<void>;
  clearError: () => void;
  setCurrentProject: (project: Project | null) => void;
}

export const useProjectStore = create<ProjectState>()(
  devtools(
    (set, get) => ({
      // 初始状态
      projects: [],
      currentProject: null,
      projectProgress: null,
      qualityIssues: [],
      isLoading: false,
      error: null,

      // 加载项目列表
      loadProjects: async () => {
        set({ isLoading: true, error: null });
        try {
          const projects = await projectService.getProjects();
          set({ projects, isLoading: false });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load projects',
            isLoading: false 
          });
        }
      },

      // 加载单个项目
      loadProject: async (projectId: string) => {
        set({ isLoading: true, error: null });
        try {
          const project = await projectService.getProject(projectId);
          set({ currentProject: project, isLoading: false });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load project',
            isLoading: false 
          });
        }
      },

      // 创建项目
      createProject: async (name: string, description: string, file: File) => {
        set({ isLoading: true, error: null });
        try {
          const project = await projectService.createProject({
            name,
            description,
            file
          });
          
          set(state => ({
            projects: [...state.projects, project],
            currentProject: project,
            isLoading: false
          }));
          
          return project;
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to create project',
            isLoading: false 
          });
          throw error;
        }
      },

      // 更新项目
      updateProject: async (projectId: string, updates: Partial<Project>) => {
        set({ isLoading: true, error: null });
        try {
          const updatedProject = await projectService.updateProject(projectId, updates);
          
          set(state => ({
            projects: state.projects.map(p => 
              p.id === projectId ? updatedProject : p
            ),
            currentProject: state.currentProject?.id === projectId 
              ? updatedProject 
              : state.currentProject,
            isLoading: false
          }));
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to update project',
            isLoading: false 
          });
        }
      },

      // 删除项目
      deleteProject: async (projectId: string) => {
        set({ isLoading: true, error: null });
        try {
          await projectService.deleteProject(projectId);
          
          set(state => ({
            projects: state.projects.filter(p => p.id !== projectId),
            currentProject: state.currentProject?.id === projectId 
              ? null 
              : state.currentProject,
            isLoading: false
          }));
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to delete project',
            isLoading: false 
          });
        }
      },

      // 加载项目进度
      loadProjectProgress: async (projectId: string) => {
        try {
          const progress = await projectService.getProjectProgress(projectId);
          set({ projectProgress: progress });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load progress'
          });
        }
      },

      // 运行质量检查
      runQualityCheck: async (projectId: string) => {
        set({ isLoading: true, error: null });
        try {
          const issues = await projectService.runQualityCheck(projectId);
          set({ qualityIssues: issues, isLoading: false });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to run quality check',
            isLoading: false 
          });
        }
      },

      // 保存翻译
      saveTranslation: async (projectId: string, content: string[]) => {
        try {
          await projectService.saveTranslation(projectId, content);
          
          // 更新本地状态
          set(state => ({
            currentProject: state.currentProject ? {
              ...state.currentProject,
              translationContent: content,
              updatedAt: new Date().toISOString()
            } : null
          }));
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to save translation'
          });
        }
      },

      // 清除错误
      clearError: () => set({ error: null }),

      // 设置当前项目
      setCurrentProject: (project: Project | null) => set({ currentProject: project }),
    }),
    {
      name: 'project-store',
    }
  )
);
