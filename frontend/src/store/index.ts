import { configureStore } from '@reduxjs/toolkit';
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';

import translationReducer from './slices/translationSlice';
import systemReducer from './slices/systemSlice';
import monitoringReducer from './slices/monitoringSlice';
import userReducer from './slices/userSlice';

import type { RootState } from '@/types';

export const store = configureStore({
  reducer: {
    translation: translationReducer,
    system: systemReducer,
    monitoring: monitoringReducer,
    user: userReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

export type AppDispatch = typeof store.dispatch;

// 类型化的hooks
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

export default store;
