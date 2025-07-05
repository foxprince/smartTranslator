import React from 'react';
import { Card, Typography } from 'antd';

const { Title } = Typography;

const SystemMonitoring: React.FC = () => {
  return (
    <div>
      <Card>
        <Title level={3}>系统监控</Title>
        <p>系统性能监控、告警管理、日志查看等功能正在开发中...</p>
      </Card>
    </div>
  );
};

export default SystemMonitoring;
