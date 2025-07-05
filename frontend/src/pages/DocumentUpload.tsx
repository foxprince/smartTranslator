/**
 * 文档上传页面
 * 集成文本预处理功能
 */
import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProjectStore } from '../store/projectStore';

interface DocumentUploadProps {}

export const DocumentUpload: React.FC<DocumentUploadProps> = () => {
  const navigate = useNavigate();
  const { createProject, isLoading, error, clearError } = useProjectStore();
  
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);

  // 处理文件拖拽
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  // 处理文件放置
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  }, []);

  // 处理文件选择
  const handleFileSelect = (file: File) => {
    // 验证文件类型
    if (!file.name.toLowerCase().endsWith('.txt')) {
      alert('请选择txt格式的文件');
      return;
    }

    // 验证文件大小（10MB限制）
    if (file.size > 10 * 1024 * 1024) {
      alert('文件大小不能超过10MB');
      return;
    }

    setSelectedFile(file);
    
    // 如果项目名称为空，使用文件名
    if (!projectName) {
      const nameWithoutExt = file.name.replace(/\.txt$/i, '');
      setProjectName(nameWithoutExt);
    }
  };

  // 处理文件输入变化
  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  };

  // 处理表单提交
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedFile) {
      alert('请选择要上传的文件');
      return;
    }

    if (!projectName.trim()) {
      alert('请输入项目名称');
      return;
    }

    try {
      clearError();
      const project = await createProject(
        projectName.trim(),
        projectDescription.trim(),
        selectedFile
      );
      
      // 跳转到翻译工作台
      navigate(`/workspace/${project.id}`);
    } catch (error) {
      console.error('Failed to create project:', error);
    }
  };

  // 移除选中的文件
  const removeSelectedFile = () => {
    setSelectedFile(null);
  };

  return (
    <div className="document-upload">
      <div className="upload-container">
        <div className="upload-header">
          <h1>创建翻译项目</h1>
          <p>上传txt文档开始您的翻译工作</p>
        </div>

        <form onSubmit={handleSubmit} className="upload-form">
          {/* 项目信息 */}
          <div className="form-section">
            <h2>项目信息</h2>
            
            <div className="form-group">
              <label htmlFor="projectName">项目名称 *</label>
              <input
                id="projectName"
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="输入项目名称"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="projectDescription">项目描述</label>
              <textarea
                id="projectDescription"
                value={projectDescription}
                onChange={(e) => setProjectDescription(e.target.value)}
                placeholder="输入项目描述（可选）"
                rows={3}
              />
            </div>
          </div>

          {/* 文件上传 */}
          <div className="form-section">
            <h2>文档上传</h2>
            
            {!selectedFile ? (
              <div
                className={`file-drop-zone ${dragActive ? 'active' : ''}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <div className="drop-zone-content">
                  <div className="upload-icon">📄</div>
                  <p>拖拽txt文件到此处，或点击选择文件</p>
                  <p className="file-requirements">
                    支持格式：.txt | 最大大小：10MB
                  </p>
                  
                  <input
                    type="file"
                    accept=".txt"
                    onChange={handleFileInputChange}
                    className="file-input"
                    id="fileInput"
                  />
                  <label htmlFor="fileInput" className="file-input-label">
                    选择文件
                  </label>
                </div>
              </div>
            ) : (
              <div className="selected-file">
                <div className="file-info">
                  <div className="file-icon">📄</div>
                  <div className="file-details">
                    <div className="file-name">{selectedFile.name}</div>
                    <div className="file-size">
                      {(selectedFile.size / 1024).toFixed(1)} KB
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={removeSelectedFile}
                    className="remove-file-btn"
                  >
                    ✕
                  </button>
                </div>
                
                <div className="file-preview">
                  <p>文件已选择，将自动进行预处理：</p>
                  <ul>
                    <li>✓ 编码格式检测</li>
                    <li>✓ 文本格式清理</li>
                    <li>✓ 章节结构识别</li>
                    <li>✓ 质量问题检测</li>
                  </ul>
                </div>
              </div>
            )}
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          {/* 提交按钮 */}
          <div className="form-actions">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="cancel-btn"
              disabled={isLoading}
            >
              取消
            </button>
            
            <button
              type="submit"
              className="submit-btn"
              disabled={isLoading || !selectedFile || !projectName.trim()}
            >
              {isLoading ? '创建中...' : '创建项目'}
            </button>
          </div>
        </form>
      </div>

      {/* 样式 */}
      <style jsx>{`
        .document-upload {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2rem;
        }

        .upload-container {
          background: white;
          border-radius: 12px;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
          max-width: 600px;
          width: 100%;
          overflow: hidden;
        }

        .upload-header {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 2rem;
          text-align: center;
        }

        .upload-header h1 {
          margin: 0 0 0.5rem 0;
          font-size: 2rem;
          font-weight: 600;
        }

        .upload-header p {
          margin: 0;
          opacity: 0.9;
        }

        .upload-form {
          padding: 2rem;
        }

        .form-section {
          margin-bottom: 2rem;
        }

        .form-section h2 {
          margin: 0 0 1rem 0;
          font-size: 1.25rem;
          color: #333;
          border-bottom: 2px solid #f0f0f0;
          padding-bottom: 0.5rem;
        }

        .form-group {
          margin-bottom: 1rem;
        }

        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
          color: #555;
        }

        .form-group input,
        .form-group textarea {
          width: 100%;
          padding: 0.75rem;
          border: 2px solid #e0e0e0;
          border-radius: 6px;
          font-size: 1rem;
          transition: border-color 0.2s ease;
        }

        .form-group input:focus,
        .form-group textarea:focus {
          outline: none;
          border-color: #667eea;
        }

        .file-drop-zone {
          border: 2px dashed #d0d0d0;
          border-radius: 8px;
          padding: 3rem 2rem;
          text-align: center;
          transition: all 0.2s ease;
          cursor: pointer;
        }

        .file-drop-zone:hover,
        .file-drop-zone.active {
          border-color: #667eea;
          background-color: #f8f9ff;
        }

        .drop-zone-content {
          position: relative;
        }

        .upload-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
        }

        .file-requirements {
          font-size: 0.875rem;
          color: #666;
          margin-top: 0.5rem;
        }

        .file-input {
          position: absolute;
          opacity: 0;
          width: 100%;
          height: 100%;
          cursor: pointer;
        }

        .file-input-label {
          display: inline-block;
          padding: 0.75rem 1.5rem;
          background: #667eea;
          color: white;
          border-radius: 6px;
          cursor: pointer;
          transition: background-color 0.2s ease;
          margin-top: 1rem;
        }

        .file-input-label:hover {
          background: #5a6fd8;
        }

        .selected-file {
          border: 2px solid #e0e0e0;
          border-radius: 8px;
          padding: 1.5rem;
        }

        .file-info {
          display: flex;
          align-items: center;
          margin-bottom: 1rem;
        }

        .file-icon {
          font-size: 2rem;
          margin-right: 1rem;
        }

        .file-details {
          flex: 1;
        }

        .file-name {
          font-weight: 500;
          margin-bottom: 0.25rem;
        }

        .file-size {
          font-size: 0.875rem;
          color: #666;
        }

        .remove-file-btn {
          background: #ff4757;
          color: white;
          border: none;
          border-radius: 50%;
          width: 2rem;
          height: 2rem;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .file-preview {
          background: #f8f9fa;
          padding: 1rem;
          border-radius: 6px;
        }

        .file-preview ul {
          margin: 0.5rem 0 0 0;
          padding-left: 1rem;
        }

        .file-preview li {
          margin-bottom: 0.25rem;
          color: #28a745;
        }

        .error-message {
          background: #fff5f5;
          border: 1px solid #fed7d7;
          color: #c53030;
          padding: 1rem;
          border-radius: 6px;
          display: flex;
          align-items: center;
          margin-bottom: 1rem;
        }

        .error-icon {
          margin-right: 0.5rem;
        }

        .form-actions {
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
          margin-top: 2rem;
        }

        .cancel-btn,
        .submit-btn {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 6px;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .cancel-btn {
          background: #f8f9fa;
          color: #666;
          border: 1px solid #e0e0e0;
        }

        .cancel-btn:hover {
          background: #e9ecef;
        }

        .submit-btn {
          background: #667eea;
          color: white;
        }

        .submit-btn:hover:not(:disabled) {
          background: #5a6fd8;
        }

        .submit-btn:disabled {
          background: #d0d0d0;
          cursor: not-allowed;
        }

        @media (max-width: 768px) {
          .document-upload {
            padding: 1rem;
          }

          .upload-container {
            max-width: none;
          }

          .upload-form {
            padding: 1.5rem;
          }

          .form-actions {
            flex-direction: column;
          }

          .cancel-btn,
          .submit-btn {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};
