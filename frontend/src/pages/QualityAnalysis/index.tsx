import React from 'react';
import { Card, Typography } from 'antd';

const { Title } = Typography;

const QualityAnalysis: React.FC = () => {
  return (
    <div>
      <Card>
        <Title level={3}>质量分析</Title>
        <p>翻译质量评估、质量趋势分析、质量报告等功能正在开发中...</p>
      </Card>
    </div>
  );
};

export default QualityAnalysis;
