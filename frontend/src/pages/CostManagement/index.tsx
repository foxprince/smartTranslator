import React from 'react';
import { Card, Typography } from 'antd';

const { Title } = Typography;

const CostManagement: React.FC = () => {
  return (
    <div>
      <Card>
        <Title level={3}>成本管理</Title>
        <p>成本统计、预算设置、成本分析等功能正在开发中...</p>
      </Card>
    </div>
  );
};

export default CostManagement;
