import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { message } from 'antd';
import { systemApi, providerApi, cacheApi, costApi } from '@/services/api';
import { SystemState, SystemStats, SystemConfig } from '@/types';

// 异步actions
export const fetchSystemStats = createAsyncThunk(
  'system/fetchStats',
  async (_, { rejectWithValue }) => {
    try {
      const stats = await systemApi.getStats();
      return stats;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '获取系统统计失败';
      return rejectWithValue(errorMessage);
    }
  }
);

export const fetchSystemConfig = createAsyncThunk(
  'system/fetchConfig',
  async (_, { rejectWithValue }) => {
    try {
      const config = await systemApi.getConfig();
      return config;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '获取系统配置失败';
      return rejectWithValue(errorMessage);
    }
  }
);

export const updateSystemConfig = createAsyncThunk(
  'system/updateConfig',
  async (config: Partial<SystemConfig>, { rejectWithValue }) => {
    try {
      await systemApi.updateConfig(config);
      message.success('系统配置更新成功');
      return config;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '更新系统配置失败';
      message.error(errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

export const fetchProviderHealth = createAsyncThunk(
  'system/fetchProviderHealth',
  async (_, { rejectWithValue }) => {
    try {
      const health = await providerApi.getHealth();
      return health;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '获取提供商状态失败';
      return rejectWithValue(errorMessage);
    }
  }
);

export const testProvider = createAsyncThunk(
  'system/testProvider',
  async (provider: string, { rejectWithValue }) => {
    try {
      const result = await providerApi.testProvider(provider);
      if (result.status) {
        message.success(`${provider} 连接测试成功`);
      } else {
        message.error(`${provider} 连接测试失败: ${result.message}`);
      }
      return { provider, result };
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '测试提供商连接失败';
      message.error(errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

export const fetchCacheStats = createAsyncThunk(
  'system/fetchCacheStats',
  async (_, { rejectWithValue }) => {
    try {
      const stats = await cacheApi.getStats();
      return stats;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '获取缓存统计失败';
      return rejectWithValue(errorMessage);
    }
  }
);

export const clearCache = createAsyncThunk(
  'system/clearCache',
  async (_, { rejectWithValue }) => {
    try {
      const result = await cacheApi.clear();
      message.success(`缓存已清空，清理了 ${result.cleared_items} 个项目`);
      return result;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '清空缓存失败';
      message.error(errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

export const fetchCostStats = createAsyncThunk(
  'system/fetchCostStats',
  async (params?: { start_date?: string; end_date?: string; provider?: string }, { rejectWithValue }) => {
    try {
      const stats = await costApi.getStats(params);
      return stats;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '获取成本统计失败';
      return rejectWithValue(errorMessage);
    }
  }
);

export const setCostBudget = createAsyncThunk(
  'system/setCostBudget',
  async (budget: { daily_limit: number; monthly_limit: number }, { rejectWithValue }) => {
    try {
      await costApi.setBudget(budget);
      message.success('预算设置成功');
      return budget;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '设置预算失败';
      message.error(errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

// 初始状态
const initialState: SystemState = {
  stats: null,
  config: null,
  loading: false,
  error: undefined,
};

// Slice
const systemSlice = createSlice({
  name: 'system',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = undefined;
    },
    updateStats: (state, action) => {
      if (state.stats) {
        state.stats = { ...state.stats, ...action.payload };
      }
    },
  },
  extraReducers: (builder) => {
    // fetchSystemStats
    builder
      .addCase(fetchSystemStats.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(fetchSystemStats.fulfilled, (state, action) => {
        state.loading = false;
        state.stats = action.payload;
      })
      .addCase(fetchSystemStats.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // fetchSystemConfig
    builder
      .addCase(fetchSystemConfig.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(fetchSystemConfig.fulfilled, (state, action) => {
        state.loading = false;
        state.config = action.payload;
      })
      .addCase(fetchSystemConfig.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // updateSystemConfig
    builder
      .addCase(updateSystemConfig.fulfilled, (state, action) => {
        if (state.config) {
          state.config = { ...state.config, ...action.payload };
        }
      });

    // fetchProviderHealth
    builder
      .addCase(fetchProviderHealth.fulfilled, (state, action) => {
        if (state.stats) {
          state.stats.providers_health = action.payload;
        }
      });

    // fetchCacheStats
    builder
      .addCase(fetchCacheStats.fulfilled, (state, action) => {
        if (state.stats) {
          state.stats.cache_stats = action.payload;
        }
      });

    // clearCache
    builder
      .addCase(clearCache.fulfilled, (state) => {
        if (state.stats?.cache_stats) {
          state.stats.cache_stats.total_items = 0;
          state.stats.cache_stats.hit_rate = 0;
        }
      });

    // fetchCostStats
    builder
      .addCase(fetchCostStats.fulfilled, (state, action) => {
        if (state.stats) {
          state.stats.cost_stats = action.payload;
        }
      });
  },
});

export const { clearError, updateStats } = systemSlice.actions;

export default systemSlice.reducer;
