import React from 'react';
import { Card, Typography } from 'antd';

const { Title } = Typography;

const Settings: React.FC = () => {
  return (
    <div>
      <Card>
        <Title level={3}>系统设置</Title>
        <p>系统配置、用户管理、权限设置等功能正在开发中...</p>
      </Card>
    </div>
  );
};

export default Settings;
