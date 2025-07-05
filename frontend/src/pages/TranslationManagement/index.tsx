import React from 'react';
import { Card, Typography } from 'antd';

const { Title } = Typography;

const TranslationManagement: React.FC = () => {
  return (
    <div>
      <Card>
        <Title level={3}>翻译管理</Title>
        <p>翻译任务管理、批量翻译、翻译历史等功能正在开发中...</p>
      </Card>
    </div>
  );
};

export default TranslationManagement;
