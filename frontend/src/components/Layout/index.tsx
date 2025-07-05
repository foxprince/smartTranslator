import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Layout as AntLayout,
  Menu,
  Avatar,
  Dropdown,
  Badge,
  Button,
  Space,
  Typography,
  Divider,
} from 'antd';
import {
  DashboardOutlined,
  TranslationOutlined,
  CloudServerOutlined,
  DatabaseOutlined,
  DollarOutlined,
  BarChartOutlined,
  MonitorOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  BellOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  FileOutlined,
} from '@ant-design/icons';

import { useAppDispatch, useAppSelector } from '../../store';
import { fetchSystemStats } from '../../store/slices/systemSlice';
import NotificationPanel from '../NotificationPanel';

import './index.css';

const { Header, Sider, Content } = AntLayout;
const { Text } = Typography;

// 菜单项配置
const menuItems = [
  {
    key: 'dashboard',
    icon: <DashboardOutlined />,
    label: '仪表盘',
    path: '/dashboard',
  },
  {
    key: 'translation',
    icon: <TranslationOutlined />,
    label: '翻译管理',
    path: '/translation',
  },
  {
    key: 'documents',
    icon: <FileOutlined />,
    label: '文档管理',
    path: '/documents',
  },
  {
    key: 'providers',
    icon: <CloudServerOutlined />,
    label: '提供商管理',
    path: '/providers',
  },
  {
    key: 'cache',
    icon: <DatabaseOutlined />,
    label: '缓存管理',
    path: '/cache',
  },
  {
    key: 'cost',
    icon: <DollarOutlined />,
    label: '成本管理',
    path: '/cost',
  },
  {
    key: 'quality',
    icon: <BarChartOutlined />,
    label: '质量分析',
    path: '/quality',
  },
  {
    key: 'monitoring',
    icon: <MonitorOutlined />,
    label: '系统监控',
    path: '/monitoring',
  },
  {
    key: 'settings',
    icon: <SettingOutlined />,
    label: '系统设置',
    path: '/settings',
  },
];

const Layout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [notificationVisible, setNotificationVisible] = useState(false);
  
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useAppDispatch();
  
  const { stats } = useAppSelector((state) => state.system);
  const { alerts } = useAppSelector((state) => state.monitoring);

  // 获取当前选中的菜单项
  const selectedKey = menuItems.find(item => 
    location.pathname.startsWith(item.path)
  )?.key || 'dashboard';

  // 定期刷新系统统计
  useEffect(() => {
    dispatch(fetchSystemStats());
    
    const interval = setInterval(() => {
      dispatch(fetchSystemStats());
    }, 30000); // 30秒刷新一次

    return () => clearInterval(interval);
  }, [dispatch]);

  // 菜单点击处理
  const handleMenuClick = ({ key }: { key: string }) => {
    const item = menuItems.find(item => item.key === key);
    if (item) {
      navigate(item.path);
    }
  };

  // 用户菜单
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
    },
    {
      key: 'divider',
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ];

  const handleUserMenuClick = ({ key }: { key: string }) => {
    switch (key) {
      case 'profile':
        // 处理个人资料
        break;
      case 'logout':
        // 处理退出登录
        localStorage.removeItem('auth_token');
        navigate('/login');
        break;
    }
  };

  // 未读告警数量
  const unreadAlerts = alerts.filter(alert => !alert.resolved).length;

  return (
    <AntLayout className="layout-container">
      {/* 侧边栏 */}
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        width={240}
        className="layout-sider"
      >
        {/* Logo */}
        <div className="layout-logo">
          <TranslationOutlined className="logo-icon" />
          {!collapsed && <span className="logo-text">翻译系统</span>}
        </div>

        {/* 菜单 */}
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={handleMenuClick}
        />

        {/* 系统状态指示器 */}
        {!collapsed && (
          <div className="system-status">
            <Divider style={{ margin: '12px 0', borderColor: '#434343' }} />
            <div className="status-item">
              <Text type="secondary" style={{ fontSize: '12px' }}>
                系统状态
              </Text>
              <div className="status-indicators">
                <div className="status-indicator">
                  <div className={`status-dot ${stats?.providers_health ? 'online' : 'offline'}`} />
                  <Text style={{ fontSize: '11px', color: '#999' }}>API</Text>
                </div>
                <div className="status-indicator">
                  <div className={`status-dot ${stats?.cache_stats ? 'online' : 'offline'}`} />
                  <Text style={{ fontSize: '11px', color: '#999' }}>缓存</Text>
                </div>
                <div className="status-indicator">
                  <div className="status-dot online" />
                  <Text style={{ fontSize: '11px', color: '#999' }}>数据库</Text>
                </div>
              </div>
            </div>
          </div>
        )}
      </Sider>

      {/* 主内容区 */}
      <AntLayout className="layout-main">
        {/* 顶部导航 */}
        <Header className="layout-header">
          <div className="header-left">
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              className="collapse-btn"
            />
            
            {/* 面包屑或页面标题 */}
            <div className="page-title">
              {menuItems.find(item => item.key === selectedKey)?.label}
            </div>
          </div>

          <div className="header-right">
            <Space size="middle">
              {/* 系统统计快览 */}
              {stats && (
                <Space size="large" className="header-stats">
                  <div className="stat-item">
                    <Text type="secondary" style={{ fontSize: '12px' }}>今日请求</Text>
                    <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                      {stats.total_requests_today || 0}
                    </div>
                  </div>
                  <div className="stat-item">
                    <Text type="secondary" style={{ fontSize: '12px' }}>活跃任务</Text>
                    <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                      {stats.active_jobs || 0}
                    </div>
                  </div>
                  <div className="stat-item">
                    <Text type="secondary" style={{ fontSize: '12px' }}>响应时间</Text>
                    <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                      {stats.average_response_time ? `${stats.average_response_time}ms` : '-'}
                    </div>
                  </div>
                </Space>
              )}

              {/* 通知铃铛 */}
              <Badge count={unreadAlerts} size="small">
                <Button
                  type="text"
                  icon={<BellOutlined />}
                  onClick={() => setNotificationVisible(true)}
                  className="notification-btn"
                />
              </Badge>

              {/* 用户头像和菜单 */}
              <Dropdown
                menu={{
                  items: userMenuItems,
                  onClick: handleUserMenuClick,
                }}
                placement="bottomRight"
              >
                <div className="user-info">
                  <Avatar size="small" icon={<UserOutlined />} />
                  <Text className="username">管理员</Text>
                </div>
              </Dropdown>
            </Space>
          </div>
        </Header>

        {/* 内容区域 */}
        <Content className="layout-content">
          <div className="content-wrapper">
            <Outlet />
          </div>
        </Content>
      </AntLayout>

      {/* 通知面板 */}
      <NotificationPanel
        visible={notificationVisible}
        onClose={() => setNotificationVisible(false)}
        alerts={alerts}
      />
    </AntLayout>
  );
};

export default Layout;
