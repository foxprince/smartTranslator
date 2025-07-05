import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import { Provider } from 'react-redux';
import zhCN from 'antd/locale/zh_CN';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';

import { store } from './store';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import TranslationManagement from './pages/TranslationManagement';
import DocumentManagement from './pages/DocumentManagement';
import ProviderManagement from './pages/ProviderManagement';
import CacheManagement from './pages/CacheManagement';
import CostManagement from './pages/CostManagement';
import QualityAnalysis from './pages/QualityAnalysis';
import SystemMonitoring from './pages/SystemMonitoring';
import Settings from './pages/Settings';

import './App.css';

// 设置dayjs中文
dayjs.locale('zh-cn');

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <ConfigProvider
        locale={zhCN}
        theme={{
          algorithm: theme.defaultAlgorithm,
          token: {
            colorPrimary: '#1890ff',
            borderRadius: 6,
          },
        }}
      >
        <Router>
          <div className="App">
            <Routes>
              <Route path="/" element={<Layout />}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="translation" element={<TranslationManagement />} />
                <Route path="documents" element={<DocumentManagement />} />
                <Route path="providers" element={<ProviderManagement />} />
                <Route path="cache" element={<CacheManagement />} />
                <Route path="cost" element={<CostManagement />} />
                <Route path="quality" element={<QualityAnalysis />} />
                <Route path="monitoring" element={<SystemMonitoring />} />
                <Route path="settings" element={<Settings />} />
              </Route>
            </Routes>
          </div>
        </Router>
      </ConfigProvider>
    </Provider>
  );
};

export default App;
