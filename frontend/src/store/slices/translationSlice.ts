import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { message } from 'antd';
import { translationApi } from '../../services/api';
import {
  TranslationState,
  TranslationRequest,
  TranslationResult,
  TranslationJob,
  PaginationParams,
} from '../../types';

// 异步actions
export const translateText = createAsyncThunk(
  'translation/translateText',
  async (request: TranslationRequest, { rejectWithValue }) => {
    try {
      const result = await translationApi.translate(request);
      message.success(`翻译完成！成功 ${result.success_count}/${result.total_count} 条`);
      return result;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '翻译失败';
      message.error(errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

export const createTranslationJob = createAsyncThunk(
  'translation/createJob',
  async (
    request: TranslationRequest & { project_id: string; user_id: string },
    { rejectWithValue }
  ) => {
    try {
      const result = await translationApi.createJob(request);
      message.success('翻译任务创建成功');
      return result;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '创建任务失败';
      message.error(errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

export const fetchTranslationJobs = createAsyncThunk(
  'translation/fetchJobs',
  async (params: PaginationParams, { rejectWithValue }) => {
    try {
      const result = await translationApi.getJobs(params);
      return result;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '获取任务列表失败';
      return rejectWithValue(errorMessage);
    }
  }
);

export const fetchJobStatus = createAsyncThunk(
  'translation/fetchJobStatus',
  async (jobId: string, { rejectWithValue }) => {
    try {
      const job = await translationApi.getJobStatus(jobId);
      return job;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '获取任务状态失败';
      return rejectWithValue(errorMessage);
    }
  }
);

export const cancelTranslationJob = createAsyncThunk(
  'translation/cancelJob',
  async (jobId: string, { rejectWithValue }) => {
    try {
      await translationApi.cancelJob(jobId);
      message.success('任务已取消');
      return jobId;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '取消任务失败';
      message.error(errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

// 初始状态
const initialState: TranslationState = {
  jobs: [],
  currentJob: undefined,
  loading: false,
  error: undefined,
};

// Slice
const translationSlice = createSlice({
  name: 'translation',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = undefined;
    },
    setCurrentJob: (state, action: PayloadAction<TranslationJob | undefined>) => {
      state.currentJob = action.payload;
    },
    updateJobStatus: (state, action: PayloadAction<{ jobId: string; status: string; progress?: number }>) => {
      const { jobId, status, progress } = action.payload;
      const job = state.jobs.find(j => j.id === jobId);
      if (job) {
        job.status = status as any;
        if (progress !== undefined) {
          job.progress = progress;
        }
        job.updated_at = new Date().toISOString();
      }
      if (state.currentJob?.id === jobId) {
        state.currentJob.status = status as any;
        if (progress !== undefined) {
          state.currentJob.progress = progress;
        }
        state.currentJob.updated_at = new Date().toISOString();
      }
    },
    addJob: (state, action: PayloadAction<TranslationJob>) => {
      state.jobs.unshift(action.payload);
    },
    removeJob: (state, action: PayloadAction<string>) => {
      state.jobs = state.jobs.filter(job => job.id !== action.payload);
      if (state.currentJob?.id === action.payload) {
        state.currentJob = undefined;
      }
    },
  },
  extraReducers: (builder) => {
    // translateText
    builder
      .addCase(translateText.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(translateText.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(translateText.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // createTranslationJob
    builder
      .addCase(createTranslationJob.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(createTranslationJob.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(createTranslationJob.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // fetchTranslationJobs
    builder
      .addCase(fetchTranslationJobs.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(fetchTranslationJobs.fulfilled, (state, action) => {
        state.loading = false;
        state.jobs = action.payload.items;
      })
      .addCase(fetchTranslationJobs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // fetchJobStatus
    builder
      .addCase(fetchJobStatus.fulfilled, (state, action) => {
        const job = action.payload;
        const existingJobIndex = state.jobs.findIndex(j => j.id === job.id);
        if (existingJobIndex >= 0) {
          state.jobs[existingJobIndex] = job;
        }
        if (state.currentJob?.id === job.id) {
          state.currentJob = job;
        }
      });

    // cancelTranslationJob
    builder
      .addCase(cancelTranslationJob.fulfilled, (state, action) => {
        const jobId = action.payload;
        const job = state.jobs.find(j => j.id === jobId);
        if (job) {
          job.status = 'cancelled' as any;
          job.updated_at = new Date().toISOString();
        }
        if (state.currentJob?.id === jobId) {
          state.currentJob.status = 'cancelled' as any;
          state.currentJob.updated_at = new Date().toISOString();
        }
      });
  },
});

export const {
  clearError,
  setCurrentJob,
  updateJobStatus,
  addJob,
  removeJob,
} = translationSlice.actions;

export default translationSlice.reducer;
