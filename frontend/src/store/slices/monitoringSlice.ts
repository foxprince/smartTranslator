import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { message } from 'antd';
import { monitoringApi } from '../../services/api';
import { MonitoringState, MonitoringMetrics, Alert } from '../../types';

// 异步actions
export const fetchMonitoringMetrics = createAsyncThunk(
  'monitoring/fetchMetrics',
  async (_, { rejectWithValue }) => {
    try {
      const metrics = await monitoringApi.getMetrics();
      return metrics;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '获取监控指标失败';
      return rejectWithValue(errorMessage);
    }
  }
);

export const fetchAlerts = createAsyncThunk(
  'monitoring/fetchAlerts',
  async (params: { severity?: string; resolved?: boolean } = {}, { rejectWithValue }) => {
    try {
      const result = await monitoringApi.getAlerts(params);
      return result;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '获取告警列表失败';
      return rejectWithValue(errorMessage);
    }
  }
);

export const resolveAlert = createAsyncThunk(
  'monitoring/resolveAlert',
  async (alertId: string, { rejectWithValue }) => {
    try {
      await monitoringApi.resolveAlert(alertId);
      message.success('告警已解决');
      return alertId;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '解决告警失败';
      message.error(errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

// 初始状态
const initialState: MonitoringState = {
  metrics: null,
  alerts: [],
  loading: false,
  error: undefined,
};

// Slice
const monitoringSlice = createSlice({
  name: 'monitoring',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = undefined;
    },
    addAlert: (state, action) => {
      state.alerts.unshift(action.payload);
    },
    updateMetrics: (state, action) => {
      if (state.metrics) {
        state.metrics = { ...state.metrics, ...action.payload };
      }
    },
  },
  extraReducers: (builder) => {
    // fetchMonitoringMetrics
    builder
      .addCase(fetchMonitoringMetrics.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(fetchMonitoringMetrics.fulfilled, (state, action) => {
        state.loading = false;
        state.metrics = action.payload;
      })
      .addCase(fetchMonitoringMetrics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // fetchAlerts
    builder
      .addCase(fetchAlerts.fulfilled, (state, action) => {
        state.alerts = action.payload.items || action.payload;
      });

    // resolveAlert
    builder
      .addCase(resolveAlert.fulfilled, (state, action) => {
        const alertId = action.payload;
        const alert = state.alerts.find(a => a.id === alertId);
        if (alert) {
          alert.resolved = true;
          alert.resolved_at = new Date().toISOString();
        }
      });
  },
});

export const { clearError, addAlert, updateMetrics } = monitoringSlice.actions;

export default monitoringSlice.reducer;
