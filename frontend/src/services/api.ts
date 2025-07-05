import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { message } from 'antd';
import {
  TranslationRequest,
  TranslationResult,
  TranslationJob,
  SystemStats,
  MonitoringMetrics,
  CacheStats,
  CostStats,
  ProviderHealth,
  ApiResponse,
  PaginatedResponse,
  PaginationParams,
  SystemConfig,
} from '@/types';

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    const { response } = error;
    
    if (response) {
      const { status, data } = response;
      
      switch (status) {
        case 401:
          message.error('认证失败，请重新登录');
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
          break;
        case 403:
          message.error('权限不足');
          break;
        case 404:
          message.error('请求的资源不存在');
          break;
        case 500:
          message.error('服务器内部错误');
          break;
        default:
          message.error(data?.message || '请求失败');
      }
    } else {
      message.error('网络连接失败');
    }
    
    return Promise.reject(error);
  }
);

// 翻译API
export const translationApi = {
  // 批量翻译
  translate: async (request: TranslationRequest): Promise<TranslationResult> => {
    const response = await api.post<TranslationResult>('/translation/translate', request);
    return response.data;
  },

  // 获取翻译建议
  getSuggestions: async (params: {
    text: string;
    providers: string;
    source_lang: string;
    target_lang: string;
  }) => {
    const response = await api.get('/translation/suggestions', { params });
    return response.data;
  },

  // 创建翻译任务
  createJob: async (request: TranslationRequest & {
    project_id: string;
    user_id: string;
  }): Promise<{ job_id: string; status: string }> => {
    const response = await api.post('/translation/jobs', request);
    return response.data;
  },

  // 获取任务状态
  getJobStatus: async (jobId: string): Promise<TranslationJob> => {
    const response = await api.get(`/translation/jobs/${jobId}`);
    return response.data;
  },

  // 获取任务列表
  getJobs: async (params: PaginationParams): Promise<PaginatedResponse<TranslationJob>> => {
    const response = await api.get('/translation/jobs', { params });
    return response.data;
  },

  // 取消任务
  cancelJob: async (jobId: string): Promise<void> => {
    await api.delete(`/translation/jobs/${jobId}`);
  },
};

// 提供商API
export const providerApi = {
  // 获取提供商健康状态
  getHealth: async (): Promise<ProviderHealth> => {
    const response = await api.get('/translation/providers/health');
    return response.data;
  },

  // 测试提供商连接
  testProvider: async (provider: string): Promise<{ status: boolean; message: string }> => {
    const response = await api.post(`/translation/providers/${provider}/test`);
    return response.data;
  },
};

// 缓存API
export const cacheApi = {
  // 获取缓存统计
  getStats: async (): Promise<CacheStats> => {
    const response = await api.get('/translation/cache/stats');
    return response.data;
  },

  // 清空缓存
  clear: async (): Promise<{ cleared_items: number }> => {
    const response = await api.delete('/translation/cache');
    return response.data;
  },

  // 搜索缓存
  search: async (params: {
    query?: string;
    source_lang?: string;
    target_lang?: string;
    provider?: string;
    page?: number;
    page_size?: number;
  }) => {
    const response = await api.get('/translation/cache/search', { params });
    return response.data;
  },
};

// 成本API
export const costApi = {
  // 获取成本统计
  getStats: async (params?: {
    start_date?: string;
    end_date?: string;
    provider?: string;
  }): Promise<CostStats> => {
    const response = await api.get('/translation/costs/stats', { params });
    return response.data;
  },

  // 获取成本趋势
  getTrends: async (params: {
    period: 'daily' | 'weekly' | 'monthly';
    days?: number;
  }) => {
    const response = await api.get('/translation/costs/trends', { params });
    return response.data;
  },

  // 设置预算
  setBudget: async (budget: {
    daily_limit: number;
    monthly_limit: number;
  }): Promise<void> => {
    await api.post('/translation/costs/budget', budget);
  },
};

// 质量API
export const qualityApi = {
  // 获取质量统计
  getStats: async (params?: {
    start_date?: string;
    end_date?: string;
    provider?: string;
    language_pair?: string;
  }) => {
    const response = await api.get('/translation/quality/stats', { params });
    return response.data;
  },

  // 获取质量趋势
  getTrends: async (params: {
    period: 'daily' | 'weekly' | 'monthly';
    days?: number;
  }) => {
    const response = await api.get('/translation/quality/trends', { params });
    return response.data;
  },

  // 获取质量详情
  getDetails: async (params: PaginationParams & {
    min_score?: number;
    max_score?: number;
    provider?: string;
  }) => {
    const response = await api.get('/translation/quality/details', { params });
    return response.data;
  },
};

// 系统API
export const systemApi = {
  // 获取系统统计
  getStats: async (): Promise<SystemStats> => {
    const response = await api.get('/translation/stats');
    return response.data;
  },

  // 获取系统配置
  getConfig: async (): Promise<SystemConfig> => {
    const response = await api.get('/system/config');
    return response.data;
  },

  // 更新系统配置
  updateConfig: async (config: Partial<SystemConfig>): Promise<void> => {
    await api.put('/system/config', config);
  },

  // 健康检查
  healthCheck: async (): Promise<{ status: string; timestamp: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

// 监控API
export const monitoringApi = {
  // 获取监控指标
  getMetrics: async (): Promise<MonitoringMetrics> => {
    const response = await api.get('/monitoring/metrics');
    return response.data;
  },

  // 获取历史指标
  getHistoricalMetrics: async (params: {
    start_time: string;
    end_time: string;
    interval?: string;
  }) => {
    const response = await api.get('/monitoring/metrics/history', { params });
    return response.data;
  },

  // 获取告警列表
  getAlerts: async (params?: {
    severity?: string;
    resolved?: boolean;
    page?: number;
    page_size?: number;
  }) => {
    const response = await api.get('/monitoring/alerts', { params });
    return response.data;
  },

  // 解决告警
  resolveAlert: async (alertId: string): Promise<void> => {
    await api.post(`/monitoring/alerts/${alertId}/resolve`);
  },
};

// 用户API
export const userApi = {
  // 登录
  login: async (credentials: {
    username: string;
    password: string;
  }): Promise<{ token: string; user: any }> => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  // 获取当前用户信息
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  // 登出
  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
    localStorage.removeItem('auth_token');
  },
};

// 导出默认API实例
export default api;
