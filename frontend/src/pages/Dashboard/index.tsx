import React, { useEffect, useState } from 'react';
import {
  Row,
  Col,
  Card,
  Statistic,
  Progress,
  Table,
  Tag,
  Space,
  Button,
  Select,
  DatePicker,
  Spin,
  Alert,
} from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  TranslationOutlined,
  CloudServerOutlined,
  DollarOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import dayjs from 'dayjs';

import { useAppDispatch, useAppSelector } from '@/store';
import { fetchSystemStats } from '@/store/slices/systemSlice';
import { fetchTranslationJobs } from '@/store/slices/translationSlice';
import { TranslationProvider, JobStatus } from '@/types';

import './index.css';

const { RangePicker } = DatePicker;

// 图表颜色配置
const COLORS = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2'];

// 模拟数据生成函数
const generateTimeSeriesData = (days: number) => {
  const data = [];
  for (let i = days - 1; i >= 0; i--) {
    const date = dayjs().subtract(i, 'day');
    data.push({
      date: date.format('MM-DD'),
      requests: Math.floor(Math.random() * 1000) + 500,
      success_rate: Math.floor(Math.random() * 20) + 80,
      cost: Math.floor(Math.random() * 50) + 20,
      response_time: Math.floor(Math.random() * 500) + 200,
    });
  }
  return data;
};

const Dashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().subtract(7, 'day'),
    dayjs(),
  ]);
  const [refreshing, setRefreshing] = useState(false);

  const dispatch = useAppDispatch();
  const { stats, loading } = useAppSelector((state) => state.system);
  const { jobs } = useAppSelector((state) => state.translation);

  // 模拟图表数据
  const [chartData] = useState({
    timeSeries: generateTimeSeriesData(7),
    providerUsage: [
      { name: 'Google Translate', value: 65, color: '#1890ff' },
      { name: 'OpenAI GPT', value: 35, color: '#52c41a' },
    ],
    languagePairs: [
      { name: 'EN→ZH', count: 1250 },
      { name: 'ZH→EN', count: 890 },
      { name: 'EN→ES', count: 650 },
      { name: 'EN→FR', count: 420 },
      { name: 'EN→DE', count: 380 },
    ],
    qualityDistribution: [
      { name: '优秀', value: 45, color: '#52c41a' },
      { name: '良好', value: 35, color: '#1890ff' },
      { name: '一般', value: 15, color: '#faad14' },
      { name: '较差', value: 5, color: '#f5222d' },
    ],
  });

  useEffect(() => {
    dispatch(fetchSystemStats());
    dispatch(fetchTranslationJobs({ page: 1, page_size: 10 }));
  }, [dispatch]);

  // 刷新数据
  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await Promise.all([
        dispatch(fetchSystemStats()),
        dispatch(fetchTranslationJobs({ page: 1, page_size: 10 })),
      ]);
    } finally {
      setRefreshing(false);
    }
  };

  // 获取提供商健康状态
  const getProviderHealthStatus = () => {
    if (!stats?.providers_health) return { healthy: 0, total: 0 };
    
    const providers = Object.values(stats.providers_health);
    const healthy = providers.filter(p => p.status).length;
    return { healthy, total: providers.length };
  };

  // 最近任务表格列配置
  const jobColumns = [
    {
      title: '任务ID',
      dataIndex: 'id',
      key: 'id',
      width: 120,
      render: (id: string) => id.slice(0, 8) + '...',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: JobStatus) => {
        const statusConfig = {
          [JobStatus.PENDING]: { color: 'default', text: '等待中' },
          [JobStatus.PROCESSING]: { color: 'processing', text: '处理中' },
          [JobStatus.COMPLETED]: { color: 'success', text: '已完成' },
          [JobStatus.FAILED]: { color: 'error', text: '失败' },
          [JobStatus.CANCELLED]: { color: 'default', text: '已取消' },
        };
        const config = statusConfig[status] || statusConfig[JobStatus.PENDING];
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      width: 120,
      render: (progress: number) => (
        <Progress percent={progress} size="small" />
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (time: string) => dayjs(time).format('MM-DD HH:mm'),
    },
  ];

  const providerHealth = getProviderHealthStatus();

  return (
    <div className="dashboard-container">
      {/* 页面头部 */}
      <div className="dashboard-header">
        <div className="header-title">
          <h2>系统仪表盘</h2>
          <p>翻译系统运行状态总览</p>
        </div>
        <div className="header-actions">
          <Space>
            <RangePicker
              value={timeRange}
              onChange={(dates) => dates && setTimeRange(dates)}
              format="YYYY-MM-DD"
            />
            <Button
              icon={<ReloadOutlined />}
              onClick={handleRefresh}
              loading={refreshing}
            >
              刷新
            </Button>
          </Space>
        </div>
      </div>

      <Spin spinning={loading}>
        {/* 核心指标卡片 */}
        <Row gutter={[16, 16]} className="metrics-row">
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="今日翻译请求"
                value={stats?.total_requests_today || 0}
                prefix={<TranslationOutlined />}
                suffix="次"
                valueStyle={{ color: '#1890ff' }}
              />
              <div className="metric-trend">
                <ArrowUpOutlined style={{ color: '#52c41a' }} />
                <span style={{ color: '#52c41a', marginLeft: 4 }}>
                  较昨日 +12.5%
                </span>
              </div>
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="活跃翻译任务"
                value={stats?.active_jobs || 0}
                prefix={<ClockCircleOutlined />}
                suffix="个"
                valueStyle={{ color: '#52c41a' }}
              />
              <div className="metric-trend">
                <ArrowDownOutlined style={{ color: '#f5222d' }} />
                <span style={{ color: '#f5222d', marginLeft: 4 }}>
                  较昨日 -3.2%
                </span>
              </div>
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="平均响应时间"
                value={stats?.average_response_time || 0}
                prefix={<ClockCircleOutlined />}
                suffix="ms"
                valueStyle={{ color: '#faad14' }}
              />
              <div className="metric-trend">
                <ArrowDownOutlined style={{ color: '#52c41a' }} />
                <span style={{ color: '#52c41a', marginLeft: 4 }}>
                  较昨日 -8.1%
                </span>
              </div>
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="今日翻译成本"
                value={stats?.cost_stats?.daily_cost || 0}
                prefix={<DollarOutlined />}
                suffix="USD"
                precision={2}
                valueStyle={{ color: '#722ed1' }}
              />
              <div className="metric-trend">
                <ArrowUpOutlined style={{ color: '#f5222d' }} />
                <span style={{ color: '#f5222d', marginLeft: 4 }}>
                  较昨日 +5.7%
                </span>
              </div>
            </Card>
          </Col>
        </Row>

        {/* 系统状态概览 */}
        <Row gutter={[16, 16]} className="status-row">
          <Col xs={24} lg={8}>
            <Card title="提供商状态" className="status-card">
              <div className="provider-status">
                <div className="status-summary">
                  <Statistic
                    title="健康提供商"
                    value={`${providerHealth.healthy}/${providerHealth.total}`}
                    valueStyle={{ 
                      color: providerHealth.healthy === providerHealth.total ? '#52c41a' : '#faad14' 
                    }}
                  />
                </div>
                <div className="provider-list">
                  {stats?.providers_health && Object.entries(stats.providers_health).map(([name, health]) => (
                    <div key={name} className="provider-item">
                      <div className="provider-info">
                        <CloudServerOutlined />
                        <span className="provider-name">{name}</span>
                      </div>
                      <div className="provider-health">
                        {health.status ? (
                          <CheckCircleOutlined style={{ color: '#52c41a' }} />
                        ) : (
                          <ExclamationCircleOutlined style={{ color: '#f5222d' }} />
                        )}
                        <span className="response-time">
                          {health.response_time}ms
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </Col>

          <Col xs={24} lg={8}>
            <Card title="缓存状态" className="status-card">
              <div className="cache-status">
                <div className="cache-metrics">
                  <div className="cache-metric">
                    <span className="metric-label">命中率</span>
                    <Progress
                      percent={Math.round((stats?.cache_stats?.hit_rate || 0) * 100)}
                      strokeColor="#52c41a"
                      size="small"
                    />
                  </div>
                  <div className="cache-metric">
                    <span className="metric-label">缓存项目</span>
                    <span className="metric-value">
                      {stats?.cache_stats?.total_items || 0}
                    </span>
                  </div>
                  <div className="cache-metric">
                    <span className="metric-label">内存使用</span>
                    <span className="metric-value">
                      {stats?.cache_stats?.memory_usage || '0MB'}
                    </span>
                  </div>
                </div>
              </div>
            </Card>
          </Col>

          <Col xs={24} lg={8}>
            <Card title="成本预算" className="status-card">
              <div className="budget-status">
                <div className="budget-item">
                  <span className="budget-label">日预算使用</span>
                  <Progress
                    percent={Math.round(
                      ((stats?.cost_stats?.budget_usage?.daily_usage || 0) /
                        (stats?.cost_stats?.budget_usage?.daily_limit || 1)) * 100
                    )}
                    strokeColor="#1890ff"
                    size="small"
                  />
                  <span className="budget-text">
                    ${stats?.cost_stats?.budget_usage?.daily_usage || 0} / 
                    ${stats?.cost_stats?.budget_usage?.daily_limit || 0}
                  </span>
                </div>
                <div className="budget-item">
                  <span className="budget-label">月预算使用</span>
                  <Progress
                    percent={Math.round(
                      ((stats?.cost_stats?.budget_usage?.monthly_usage || 0) /
                        (stats?.cost_stats?.budget_usage?.monthly_limit || 1)) * 100
                    )}
                    strokeColor="#722ed1"
                    size="small"
                  />
                  <span className="budget-text">
                    ${stats?.cost_stats?.budget_usage?.monthly_usage || 0} / 
                    ${stats?.cost_stats?.budget_usage?.monthly_limit || 0}
                  </span>
                </div>
              </div>
            </Card>
          </Col>
        </Row>

        {/* 图表区域 */}
        <Row gutter={[16, 16]} className="charts-row">
          <Col xs={24} lg={12}>
            <Card title="翻译请求趋势" className="chart-card">
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={chartData.timeSeries}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area
                    type="monotone"
                    dataKey="requests"
                    stroke="#1890ff"
                    fill="#1890ff"
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Card>
          </Col>

          <Col xs={24} lg={12}>
            <Card title="提供商使用分布" className="chart-card">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={chartData.providerUsage}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {chartData.providerUsage.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </Col>

          <Col xs={24} lg={12}>
            <Card title="热门语言对" className="chart-card">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData.languagePairs}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#52c41a" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </Col>

          <Col xs={24} lg={12}>
            <Card title="翻译质量分布" className="chart-card">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={chartData.qualityDistribution}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {chartData.qualityDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </Col>
        </Row>

        {/* 最近任务 */}
        <Row gutter={[16, 16]} className="recent-jobs-row">
          <Col span={24}>
            <Card title="最近翻译任务" className="jobs-card">
              <Table
                columns={jobColumns}
                dataSource={jobs.slice(0, 10)}
                rowKey="id"
                pagination={false}
                size="small"
              />
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  );
};

export default Dashboard;
