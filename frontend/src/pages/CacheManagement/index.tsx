import React from 'react';
import { Card, Typography } from 'antd';

const { Title } = Typography;

const CacheManagement: React.FC = () => {
  return (
    <div>
      <Card>
        <Title level={3}>缓存管理</Title>
        <p>缓存统计、缓存清理、缓存配置等功能正在开发中...</p>
      </Card>
    </div>
  );
};

export default CacheManagement;
