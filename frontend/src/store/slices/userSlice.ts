import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { message } from 'antd';
import { userApi } from '@/services/api';
import { UserState, User } from '@/types';

// 异步actions
export const login = createAsyncThunk(
  'user/login',
  async (credentials: { username: string; password: string }, { rejectWithValue }) => {
    try {
      const result = await userApi.login(credentials);
      localStorage.setItem('auth_token', result.token);
      message.success('登录成功');
      return result;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '登录失败';
      message.error(errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

export const getCurrentUser = createAsyncThunk(
  'user/getCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const user = await userApi.getCurrentUser();
      return user;
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '获取用户信息失败';
      return rejectWithValue(errorMessage);
    }
  }
);

export const logout = createAsyncThunk(
  'user/logout',
  async (_, { rejectWithValue }) => {
    try {
      await userApi.logout();
      message.success('已退出登录');
      return null;
    } catch (error: any) {
      // 即使API调用失败，也要清除本地token
      localStorage.removeItem('auth_token');
      return null;
    }
  }
);

// 初始状态
const initialState: UserState = {
  currentUser: null,
  isAuthenticated: !!localStorage.getItem('auth_token'),
  loading: false,
  error: undefined,
};

// Slice
const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = undefined;
    },
    setUser: (state, action) => {
      state.currentUser = action.payload;
      state.isAuthenticated = !!action.payload;
    },
  },
  extraReducers: (builder) => {
    // login
    builder
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = undefined;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.currentUser = action.payload.user;
        state.isAuthenticated = true;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
      });

    // getCurrentUser
    builder
      .addCase(getCurrentUser.fulfilled, (state, action) => {
        state.currentUser = action.payload;
        state.isAuthenticated = true;
      })
      .addCase(getCurrentUser.rejected, (state) => {
        state.currentUser = null;
        state.isAuthenticated = false;
        localStorage.removeItem('auth_token');
      });

    // logout
    builder
      .addCase(logout.fulfilled, (state) => {
        state.currentUser = null;
        state.isAuthenticated = false;
      });
  },
});

export const { clearError, setUser } = userSlice.actions;

export default userSlice.reducer;
