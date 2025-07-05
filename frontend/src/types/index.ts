// 翻译系统类型定义

export interface TranslationRequest {
  texts: string[];
  source_language: string;
  target_language: string;
  provider: TranslationProvider;
}

export interface TranslationItem {
  original_text: string;
  translated_text: string;
  confidence: number;
  provider: TranslationProvider;
  quality_score: number;
  is_cached?: boolean;
  estimated_cost?: number;
}

export interface TranslationResult {
  total_count: number;
  success_count: number;
  failed_count: number;
  provider_used: TranslationProvider;
  translations: TranslationItem[];
  quality_summary: QualitySummary;
  total_cost: number;
  cache_hit_rate: number;
  processing_time: number;
}

export interface TranslationJob {
  id: string;
  project_id: string;
  user_id: string;
  status: JobStatus;
  progress: number;
  request_data: TranslationRequest;
  result_data?: TranslationResult;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  error_message?: string;
}

export interface QualitySummary {
  excellent: number;
  good: number;
  fair: number;
  poor: number;
  average_score: number;
}

export interface QualityAssessment {
  overall_score: number;
  length_score: number;
  consistency_score: number;
  language_score: number;
  structure_score: number;
  confidence_level: QualityLevel;
  issues: string[];
}

export interface CacheStats {
  total_items: number;
  hit_rate: number;
  memory_usage: string;
  oldest_entry: string;
  newest_entry: string;
  cache_size_mb: number;
  eviction_count: number;
}

export interface CostStats {
  daily_cost: number;
  monthly_cost: number;
  yearly_cost: number;
  total_translations: number;
  cost_by_provider: Record<string, number>;
  cost_by_language: Record<string, number>;
  budget_usage: {
    daily_usage: number;
    monthly_usage: number;
    daily_limit: number;
    monthly_limit: number;
  };
}

export interface ProviderHealth {
  [key: string]: {
    status: boolean;
    response_time: number;
    error_rate: number;
    last_check: string;
  };
}

export interface SystemStats {
  providers_health: ProviderHealth;
  cache_stats: CacheStats;
  cost_stats: CostStats;
  active_jobs: number;
  total_requests_today: number;
  average_response_time: number;
  error_rate: number;
}

export interface MonitoringMetrics {
  timestamp: string;
  system: {
    cpu: {
      percent: number;
      count: number;
    };
    memory: {
      total: number;
      available: number;
      percent: number;
      used: number;
    };
    disk: {
      total: number;
      used: number;
      free: number;
      percent: number;
    };
  };
  api: {
    status: string;
    response_time: number;
  };
  providers: ProviderHealth;
  database: {
    status: string;
    connections: {
      active: number;
      idle: number;
      total: number;
    };
  };
}

export interface Alert {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  message: string;
  timestamp: string;
  resolved: boolean;
  resolved_at?: string;
}

// 枚举类型
export enum TranslationProvider {
  GOOGLE = 'google',
  OPENAI = 'openai',
}

export enum JobStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export enum QualityLevel {
  EXCELLENT = 'excellent',
  GOOD = 'good',
  FAIR = 'fair',
  POOR = 'poor',
}

export enum AlertType {
  CPU_HIGH = 'cpu_high',
  MEMORY_HIGH = 'memory_high',
  DISK_HIGH = 'disk_high',
  API_UNHEALTHY = 'api_unhealthy',
  PROVIDERS_UNHEALTHY = 'providers_unhealthy',
  TRANSLATION_SLOW = 'translation_slow',
  COST_BUDGET_EXCEEDED = 'cost_budget_exceeded',
}

export enum AlertSeverity {
  INFO = 'info',
  WARNING = 'warning',
  CRITICAL = 'critical',
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// 分页类型
export interface PaginationParams {
  page: number;
  page_size: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// 表格列类型
export interface TableColumn {
  key: string;
  title: string;
  dataIndex: string;
  width?: number;
  sorter?: boolean;
  render?: (value: any, record: any) => React.ReactNode;
}

// 图表数据类型
export interface ChartData {
  name: string;
  value: number;
  timestamp?: string;
}

export interface TimeSeriesData {
  timestamp: string;
  [key: string]: number | string;
}

// 配置类型
export interface SystemConfig {
  translation: {
    default_provider: TranslationProvider;
    cache_ttl: number;
    max_batch_size: number;
    request_timeout: number;
  };
  cost: {
    daily_budget: number;
    monthly_budget: number;
    alert_threshold: number;
  };
  monitoring: {
    check_interval: number;
    alert_enabled: boolean;
    retention_days: number;
  };
}

// 用户类型
export interface User {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  created_at: string;
  last_login: string;
}

export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  VIEWER = 'viewer',
}

// Redux状态类型
export interface RootState {
  translation: TranslationState;
  system: SystemState;
  monitoring: MonitoringState;
  user: UserState;
}

export interface TranslationState {
  jobs: TranslationJob[];
  currentJob?: TranslationJob;
  loading: boolean;
  error?: string;
}

export interface SystemState {
  stats: SystemStats | null;
  config: SystemConfig | null;
  loading: boolean;
  error?: string;
}

export interface MonitoringState {
  metrics: MonitoringMetrics | null;
  alerts: Alert[];
  loading: boolean;
  error?: string;
}

export interface UserState {
  currentUser: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error?: string;
}
