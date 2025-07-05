import React from 'react';
import {
  Drawer,
  List,
  Badge,
  Tag,
  Button,
  Empty,
  Typography,
  Space,
  Divider,
} from 'antd';
import {
  ExclamationCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

import { Alert, AlertSeverity, AlertType } from '../../types';
import { useAppDispatch } from '../../store';
import { resolveAlert } from '../../store/slices/monitoringSlice';

import './index.css';

dayjs.extend(relativeTime);

const { Text, Title } = Typography;

interface NotificationPanelProps {
  visible: boolean;
  onClose: () => void;
  alerts: Alert[];
}

const NotificationPanel: React.FC<NotificationPanelProps> = ({
  visible,
  onClose,
  alerts,
}) => {
  const dispatch = useAppDispatch();

  // 告警类型配置
  const alertTypeConfig = {
    [AlertType.CPU_HIGH]: { label: 'CPU使用率过高', color: 'orange' },
    [AlertType.MEMORY_HIGH]: { label: '内存使用率过高', color: 'red' },
    [AlertType.DISK_HIGH]: { label: '磁盘使用率过高', color: 'volcano' },
    [AlertType.API_UNHEALTHY]: { label: 'API服务异常', color: 'red' },
    [AlertType.PROVIDERS_UNHEALTHY]: { label: '翻译提供商异常', color: 'orange' },
    [AlertType.TRANSLATION_SLOW]: { label: '翻译响应缓慢', color: 'yellow' },
    [AlertType.COST_BUDGET_EXCEEDED]: { label: '成本预算超限', color: 'purple' },
  };

  // 严重程度配置
  const severityConfig = {
    [AlertSeverity.INFO]: { 
      icon: <InfoCircleOutlined />, 
      color: 'blue',
      label: '信息'
    },
    [AlertSeverity.WARNING]: { 
      icon: <WarningOutlined />, 
      color: 'orange',
      label: '警告'
    },
    [AlertSeverity.CRITICAL]: { 
      icon: <ExclamationCircleOutlined />, 
      color: 'red',
      label: '严重'
    },
  };

  // 处理告警解决
  const handleResolveAlert = async (alertId: string) => {
    await dispatch(resolveAlert(alertId));
  };

  // 未解决的告警
  const unresolvedAlerts = alerts.filter(alert => !alert.resolved);
  const resolvedAlerts = alerts.filter(alert => alert.resolved);

  return (
    <Drawer
      title={
        <div className="notification-header">
          <Title level={4} style={{ margin: 0 }}>
            系统通知
          </Title>
          <Badge count={unresolvedAlerts.length} size="small" />
        </div>
      }
      placement="right"
      width={400}
      open={visible}
      onClose={onClose}
      className="notification-drawer"
    >
      <div className="notification-content">
        {/* 未解决告警 */}
        {unresolvedAlerts.length > 0 && (
          <div className="alert-section">
            <div className="section-header">
              <Text strong>未解决告警 ({unresolvedAlerts.length})</Text>
            </div>
            <List
              dataSource={unresolvedAlerts}
              renderItem={(alert) => {
                const typeConfig = alertTypeConfig[alert.type as AlertType] || 
                  { label: alert.type, color: 'default' };
                const severityConfig_ = severityConfig[alert.severity];

                return (
                  <List.Item className="alert-item">
                    <div className="alert-content">
                      <div className="alert-header">
                        <div className="alert-title">
                          {severityConfig_.icon}
                          <Text strong className="alert-type">
                            {typeConfig.label}
                          </Text>
                          <Tag color={severityConfig_.color}>
                            {severityConfig_.label}
                          </Tag>
                        </div>
                        <Text type="secondary" className="alert-time">
                          {dayjs(alert.timestamp).fromNow()}
                        </Text>
                      </div>
                      
                      <div className="alert-message">
                        <Text>{alert.message}</Text>
                      </div>
                      
                      <div className="alert-actions">
                        <Button
                          type="link"
                          size="small"
                          onClick={() => handleResolveAlert(alert.id)}
                        >
                          标记为已解决
                        </Button>
                      </div>
                    </div>
                  </List.Item>
                );
              }}
            />
          </div>
        )}

        {/* 已解决告警 */}
        {resolvedAlerts.length > 0 && (
          <>
            {unresolvedAlerts.length > 0 && <Divider />}
            <div className="alert-section">
              <div className="section-header">
                <Text type="secondary">已解决告警 ({resolvedAlerts.length})</Text>
              </div>
              <List
                dataSource={resolvedAlerts.slice(0, 10)} // 只显示最近10个
                renderItem={(alert) => {
                  const typeConfig = alertTypeConfig[alert.type as AlertType] || 
                    { label: alert.type, color: 'default' };

                  return (
                    <List.Item className="alert-item resolved">
                      <div className="alert-content">
                        <div className="alert-header">
                          <div className="alert-title">
                            <CheckCircleOutlined style={{ color: '#52c41a' }} />
                            <Text className="alert-type" type="secondary">
                              {typeConfig.label}
                            </Text>
                            <Tag color="success">
                              已解决
                            </Tag>
                          </div>
                          <Text type="secondary" className="alert-time">
                            {dayjs(alert.resolved_at).fromNow()}
                          </Text>
                        </div>
                        
                        <div className="alert-message">
                          <Text type="secondary">{alert.message}</Text>
                        </div>
                      </div>
                    </List.Item>
                  );
                }}
              />
            </div>
          </>
        )}

        {/* 空状态 */}
        {alerts.length === 0 && (
          <div className="empty-state">
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="暂无系统通知"
            />
          </div>
        )}
      </div>

      {/* 底部操作 */}
      {unresolvedAlerts.length > 0 && (
        <div className="notification-footer">
          <Space>
            <Button
              type="primary"
              size="small"
              onClick={() => {
                unresolvedAlerts.forEach(alert => {
                  handleResolveAlert(alert.id);
                });
              }}
            >
              全部标记为已解决
            </Button>
            <Button size="small" onClick={onClose}>
              关闭
            </Button>
          </Space>
        </div>
      )}
    </Drawer>
  );
};

export default NotificationPanel;
