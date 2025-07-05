import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Upload,
  Space,
  Tag,
  Progress,
  Modal,
  Form,
  Select,
  Input,
  message,
  Tooltip,
  Dropdown,
  Popconfirm,
  Row,
  Col,
  Statistic,
  Typography,
} from 'antd';
import {
  UploadOutlined,
  FileTextOutlined,
  TranslationOutlined,
  DownloadOutlined,
  DeleteOutlined,
  EyeOutlined,
  MoreOutlined,
  CloudUploadOutlined,
  FileOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import type { UploadProps, TableColumnsType } from 'antd';
import dayjs from 'dayjs';

import './index.css';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

// 文档状态配置
const documentStatusConfig = {
  uploaded: { color: 'blue', text: '已上传', icon: <CloudUploadOutlined /> },
  processing: { color: 'orange', text: '处理中', icon: <ClockCircleOutlined /> },
  completed: { color: 'green', text: '已完成', icon: <CheckCircleOutlined /> },
  failed: { color: 'red', text: '失败', icon: <ExclamationCircleOutlined /> },
};

// 处理状态配置
const processingStatusConfig = {
  pending: { color: 'default', text: '等待中' },
  text_extracting: { color: 'processing', text: '提取文本' },
  text_extracted: { color: 'success', text: '文本已提取' },
  translating: { color: 'processing', text: '翻译中' },
  translated: { color: 'success', text: '已翻译' },
  failed: { color: 'error', text: '失败' },
};

// 支持的文件格式
const supportedFormats = {
  '文本文档': ['.txt', '.md', '.rtf'],
  'Office文档': ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'],
  'PDF文档': ['.pdf'],
  '网页文档': ['.html', '.htm', '.xml'],
  '数据格式': ['.json', '.csv'],
  '图像文档': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'],
};

interface Document {
  id: string;
  original_filename: string;
  file_size: number;
  file_type: string;
  status: string;
  processing_status: string;
  text_length?: number;
  quality_score?: number;
  translation_cost?: number;
  created_at: string;
  upload_time: string;
  extraction_time?: string;
  translation_time?: string;
}

const DocumentManagement: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [translateModalVisible, setTranslateModalVisible] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [uploadForm] = Form.useForm();
  const [translateForm] = Form.useForm();
  const [stats, setStats] = useState({
    total_documents: 0,
    total_size_bytes: 0,
    documents_by_status: {},
    recent_uploads: 0,
  });

  // 加载文档列表
  const loadDocuments = async () => {
    setLoading(true);
    try {
      // 模拟API调用
      const mockDocuments: Document[] = [
        {
          id: '1',
          original_filename: '产品说明书.pdf',
          file_size: 2048576,
          file_type: '.pdf',
          status: 'completed',
          processing_status: 'translated',
          text_length: 5000,
          quality_score: 0.92,
          translation_cost: 2.5,
          created_at: '2024-01-15T10:30:00Z',
          upload_time: '2024-01-15T10:30:00Z',
          extraction_time: '2024-01-15T10:31:00Z',
          translation_time: '2024-01-15T10:35:00Z',
        },
        {
          id: '2',
          original_filename: '技术文档.docx',
          file_size: 1024000,
          file_type: '.docx',
          status: 'processing',
          processing_status: 'translating',
          text_length: 3200,
          created_at: '2024-01-15T11:00:00Z',
          upload_time: '2024-01-15T11:00:00Z',
          extraction_time: '2024-01-15T11:01:00Z',
        },
        {
          id: '3',
          original_filename: '数据报表.xlsx',
          file_size: 512000,
          file_type: '.xlsx',
          status: 'uploaded',
          processing_status: 'text_extracted',
          text_length: 1500,
          created_at: '2024-01-15T11:30:00Z',
          upload_time: '2024-01-15T11:30:00Z',
          extraction_time: '2024-01-15T11:31:00Z',
        },
      ];
      
      setDocuments(mockDocuments);
      
      // 模拟统计数据
      setStats({
        total_documents: mockDocuments.length,
        total_size_bytes: mockDocuments.reduce((sum, doc) => sum + doc.file_size, 0),
        documents_by_status: {
          uploaded: 1,
          processing: 1,
          completed: 1,
        },
        recent_uploads: 3,
      });
    } catch (error) {
      message.error('加载文档列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  // 文件上传配置
  const uploadProps: UploadProps = {
    name: 'file',
    action: '/api/document/upload',
    headers: {
      authorization: 'Bearer ' + localStorage.getItem('token'),
    },
    beforeUpload: (file) => {
      const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
      const allFormats = Object.values(supportedFormats).flat();
      
      if (!allFormats.includes(fileExt)) {
        message.error(`不支持的文件格式: ${fileExt}`);
        return false;
      }
      
      const maxSize = 50 * 1024 * 1024; // 50MB
      if (file.size > maxSize) {
        message.error('文件大小不能超过50MB');
        return false;
      }
      
      return true;
    },
    onChange: (info) => {
      if (info.file.status === 'done') {
        message.success(`${info.file.name} 上传成功`);
        loadDocuments();
        setUploadModalVisible(false);
      } else if (info.file.status === 'error') {
        message.error(`${info.file.name} 上传失败`);
      }
    },
  };

  // 表格列配置
  const columns: TableColumnsType<Document> = [
    {
      title: '文件名',
      dataIndex: 'original_filename',
      key: 'filename',
      width: 200,
      render: (filename: string, record: Document) => (
        <div className="filename-cell">
          <FileOutlined style={{ marginRight: 8, color: '#1890ff' }} />
          <Tooltip title={filename}>
            <span className="filename-text">{filename}</span>
          </Tooltip>
        </div>
      ),
    },
    {
      title: '文件类型',
      dataIndex: 'file_type',
      key: 'file_type',
      width: 80,
      render: (type: string) => (
        <Tag color="blue">{type.toUpperCase()}</Tag>
      ),
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 100,
      render: (size: number) => {
        if (size < 1024) return `${size} B`;
        if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
        return `${(size / (1024 * 1024)).toFixed(1)} MB`;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const config = documentStatusConfig[status as keyof typeof documentStatusConfig];
        return (
          <Tag color={config?.color} icon={config?.icon}>
            {config?.text || status}
          </Tag>
        );
      },
    },
    {
      title: '处理状态',
      dataIndex: 'processing_status',
      key: 'processing_status',
      width: 120,
      render: (status: string) => {
        const config = processingStatusConfig[status as keyof typeof processingStatusConfig];
        return (
          <Tag color={config?.color}>
            {config?.text || status}
          </Tag>
        );
      },
    },
    {
      title: '文本长度',
      dataIndex: 'text_length',
      key: 'text_length',
      width: 100,
      render: (length?: number) => length ? `${length.toLocaleString()} 字符` : '-',
    },
    {
      title: '质量评分',
      dataIndex: 'quality_score',
      key: 'quality_score',
      width: 100,
      render: (score?: number) => {
        if (!score) return '-';
        const percent = Math.round(score * 100);
        return (
          <div style={{ width: 60 }}>
            <Progress
              percent={percent}
              size="small"
              strokeColor={percent >= 90 ? '#52c41a' : percent >= 70 ? '#faad14' : '#ff4d4f'}
            />
          </div>
        );
      },
    },
    {
      title: '翻译成本',
      dataIndex: 'translation_cost',
      key: 'translation_cost',
      width: 100,
      render: (cost?: number) => cost ? `$${cost.toFixed(2)}` : '-',
    },
    {
      title: '上传时间',
      dataIndex: 'upload_time',
      key: 'upload_time',
      width: 150,
      render: (time: string) => dayjs(time).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      fixed: 'right',
      render: (_, record: Document) => {
        const menuItems = [
          {
            key: 'view',
            label: '查看详情',
            icon: <EyeOutlined />,
            onClick: () => handleViewDocument(record),
          },
          {
            key: 'extract',
            label: '提取文本',
            icon: <FileTextOutlined />,
            disabled: record.processing_status === 'text_extracted' || record.processing_status === 'translated',
            onClick: () => handleExtractText(record),
          },
          {
            key: 'translate',
            label: '翻译文档',
            icon: <TranslationOutlined />,
            disabled: record.processing_status !== 'text_extracted' && record.processing_status !== 'translated',
            onClick: () => handleTranslateDocument(record),
          },
          {
            key: 'download',
            label: '下载文档',
            icon: <DownloadOutlined />,
            onClick: () => handleDownloadDocument(record),
          },
          {
            type: 'divider',
          },
          {
            key: 'delete',
            label: '删除文档',
            icon: <DeleteOutlined />,
            danger: true,
            onClick: () => handleDeleteDocument(record),
          },
        ];

        return (
          <Space>
            <Button
              type="primary"
              size="small"
              icon={<TranslationOutlined />}
              disabled={record.processing_status !== 'text_extracted' && record.processing_status !== 'translated'}
              onClick={() => handleTranslateDocument(record)}
            >
              翻译
            </Button>
            <Dropdown
              menu={{
                items: menuItems,
                onClick: ({ key }) => {
                  const item = menuItems.find(item => item.key === key);
                  if (item && 'onClick' in item) {
                    item.onClick?.();
                  }
                },
              }}
              trigger={['click']}
            >
              <Button size="small" icon={<MoreOutlined />} />
            </Dropdown>
          </Space>
        );
      },
    },
  ];

  // 处理函数
  const handleViewDocument = (document: Document) => {
    setSelectedDocument(document);
    // 显示文档详情模态框
  };

  const handleExtractText = async (document: Document) => {
    try {
      message.loading('正在提取文本...', 0);
      // 调用提取文本API
      await new Promise(resolve => setTimeout(resolve, 2000)); // 模拟API调用
      message.destroy();
      message.success('文本提取成功');
      loadDocuments();
    } catch (error) {
      message.destroy();
      message.error('文本提取失败');
    }
  };

  const handleTranslateDocument = (document: Document) => {
    setSelectedDocument(document);
    setTranslateModalVisible(true);
  };

  const handleDownloadDocument = (document: Document) => {
    // 创建下载链接
    const link = document.createElement('a');
    link.href = `/api/document/${document.id}/download`;
    link.download = document.original_filename;
    link.click();
  };

  const handleDeleteDocument = (document: Document) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除文档 "${document.original_filename}" 吗？此操作不可恢复。`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          // 调用删除API
          message.success('文档删除成功');
          loadDocuments();
        } catch (error) {
          message.error('文档删除失败');
        }
      },
    });
  };

  const handleTranslateSubmit = async (values: any) => {
    try {
      message.loading('正在翻译文档...', 0);
      // 调用翻译API
      await new Promise(resolve => setTimeout(resolve, 3000)); // 模拟API调用
      message.destroy();
      message.success('文档翻译成功');
      setTranslateModalVisible(false);
      translateForm.resetFields();
      loadDocuments();
    } catch (error) {
      message.destroy();
      message.error('文档翻译失败');
    }
  };

  return (
    <div className="document-management">
      {/* 页面头部 */}
      <div className="page-header">
        <div className="header-content">
          <Title level={3}>文档管理</Title>
          <Text type="secondary">上传、处理和翻译各种格式的文档</Text>
        </div>
        <div className="header-actions">
          <Space>
            <Button
              type="primary"
              icon={<UploadOutlined />}
              onClick={() => setUploadModalVisible(true)}
            >
              上传文档
            </Button>
            <Button icon={<DownloadOutlined />}>
              批量下载
            </Button>
          </Space>
        </div>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} className="stats-row">
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总文档数"
              value={stats.total_documents}
              prefix={<FileOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总存储大小"
              value={stats.total_size_bytes / (1024 * 1024)}
              precision={1}
              suffix="MB"
              prefix={<CloudUploadOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已完成"
              value={stats.documents_by_status.completed || 0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="处理中"
              value={stats.documents_by_status.processing || 0}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 文档列表 */}
      <Card className="documents-table-card">
        <Table
          columns={columns}
          dataSource={documents}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{
            total: documents.length,
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
          }}
        />
      </Card>

      {/* 上传文档模态框 */}
      <Modal
        title="上传文档"
        open={uploadModalVisible}
        onCancel={() => setUploadModalVisible(false)}
        footer={null}
        width={600}
      >
        <div className="upload-modal-content">
          <div className="supported-formats">
            <Title level={5}>支持的文件格式：</Title>
            {Object.entries(supportedFormats).map(([category, formats]) => (
              <div key={category} className="format-category">
                <Text strong>{category}：</Text>
                <Text type="secondary">{formats.join(', ')}</Text>
              </div>
            ))}
          </div>
          
          <Upload.Dragger {...uploadProps} className="upload-dragger">
            <p className="ant-upload-drag-icon">
              <CloudUploadOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
            <p className="ant-upload-hint">
              支持单个文件上传，文件大小不超过50MB
            </p>
          </Upload.Dragger>
        </div>
      </Modal>

      {/* 翻译文档模态框 */}
      <Modal
        title="翻译文档"
        open={translateModalVisible}
        onCancel={() => {
          setTranslateModalVisible(false);
          translateForm.resetFields();
        }}
        onOk={() => translateForm.submit()}
        okText="开始翻译"
        cancelText="取消"
        width={500}
      >
        <Form
          form={translateForm}
          layout="vertical"
          onFinish={handleTranslateSubmit}
        >
          <Form.Item label="文档信息">
            <Text>{selectedDocument?.original_filename}</Text>
          </Form.Item>
          
          <Form.Item
            name="source_language"
            label="源语言"
            rules={[{ required: true, message: '请选择源语言' }]}
          >
            <Select placeholder="选择源语言">
              <Option value="en">英语</Option>
              <Option value="zh">中文</Option>
              <Option value="ja">日语</Option>
              <Option value="ko">韩语</Option>
              <Option value="fr">法语</Option>
              <Option value="de">德语</Option>
              <Option value="es">西班牙语</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="target_language"
            label="目标语言"
            rules={[{ required: true, message: '请选择目标语言' }]}
          >
            <Select placeholder="选择目标语言">
              <Option value="zh">中文</Option>
              <Option value="en">英语</Option>
              <Option value="ja">日语</Option>
              <Option value="ko">韩语</Option>
              <Option value="fr">法语</Option>
              <Option value="de">德语</Option>
              <Option value="es">西班牙语</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="provider"
            label="翻译提供商"
            initialValue="google"
          >
            <Select>
              <Option value="google">Google Translate</Option>
              <Option value="openai">OpenAI GPT</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="preserve_formatting"
            label="保持格式"
            initialValue={true}
          >
            <Select>
              <Option value={true}>是</Option>
              <Option value={false}>否</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default DocumentManagement;
