/**
 * 项目相关类型定义
 */

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: ProjectStatus;
  originalContent: string[];
  translationContent: string[];
  metadata: ProjectMetadata;
  collaborators: Collaborator[];
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

export enum ProjectStatus {
  DRAFT = 'draft',
  IN_PROGRESS = 'in_progress',
  REVIEW = 'review',
  COMPLETED = 'completed',
  ARCHIVED = 'archived'
}

export interface ProjectMetadata {
  title: string;
  author?: string;
  languagePair: string;
  totalLines: number;
  completedLines: number;
  processingReport?: ProcessingReport;
}

export interface ProcessingReport {
  originalStats: TextStats;
  cleanedStats: TextStats;
  issuesFound: TextIssue[];
  processingTime: number;
  changesMade: string[];
}

export interface TextStats {
  totalLines: number;
  emptyLines: number;
  contentLines: number;
  shortLines: number;
  longLines: number;
  averageLineLength: number;
  encoding: string;
}

export interface TextIssue {
  lineNumber: number;
  issueType: string;
  description: string;
  suggestion?: string;
}

export interface Collaborator {
  id: string;
  name: string;
  role: 'translator' | 'reviewer' | 'admin';
  status: 'active' | 'inactive';
  joinedAt: string;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  file: File;
}

export interface ProjectProgress {
  totalLines: number;
  translatedLines: number;
  reviewedLines: number;
  completionPercentage: number;
  estimatedTimeRemaining?: number;
}

export interface QualityIssue {
  id: string;
  lineNumber: number;
  type: 'alignment' | 'translation' | 'formatting';
  severity: 'low' | 'medium' | 'high';
  description: string;
  suggestion?: string;
  isResolved: boolean;
}
