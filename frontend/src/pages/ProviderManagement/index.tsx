import React from 'react';
import { Card, Typography } from 'antd';

const { Title } = Typography;

const ProviderManagement: React.FC = () => {
  return (
    <div>
      <Card>
        <Title level={3}>提供商管理</Title>
        <p>翻译提供商配置、健康检查、性能监控等功能正在开发中...</p>
      </Card>
    </div>
  );
};

export default ProviderManagement;
