/**
 * 章节导航面板组件
 */
import React, { useState, useMemo } from 'react';

interface Chapter {
  number: number;
  title: string;
  startLine: number;
  endLine?: number;
}

interface NavigationPanelProps {
  content: string[];
  onNavigate: (lineNumber: number) => void;
}

export const NavigationPanel: React.FC<NavigationPanelProps> = ({
  content,
  onNavigate
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedChapters, setExpandedChapters] = useState<Set<number>>(new Set());

  // 检测章节结构
  const chapters = useMemo(() => {
    const detectedChapters: Chapter[] = [];
    
    content.forEach((line, index) => {
      const trimmedLine = line.trim();
      
      // 英文章节模式
      const enChapterMatch = trimmedLine.match(/^CHAPTER\s+([IVX]+)\./i);
      if (enChapterMatch) {
        detectedChapters.push({
          number: detectedChapters.length + 1,
          title: trimmedLine,
          startLine: index
        });
        return;
      }
      
      // 中文章节模式
      const cnChapterMatch = trimmedLine.match(/^第[一二三四五六七八九十]+章/);
      if (cnChapterMatch) {
        detectedChapters.push({
          number: detectedChapters.length + 1,
          title: trimmedLine,
          startLine: index
        });
        return;
      }
      
      // 数字章节模式
      const numChapterMatch = trimmedLine.match(/^第?\s*(\d+)\s*章/);
      if (numChapterMatch) {
        detectedChapters.push({
          number: detectedChapters.length + 1,
          title: trimmedLine,
          startLine: index
        });
      }
    });
    
    // 设置章节结束行
    detectedChapters.forEach((chapter, index) => {
      if (index < detectedChapters.length - 1) {
        chapter.endLine = detectedChapters[index + 1].startLine - 1;
      } else {
        chapter.endLine = content.length - 1;
      }
    });
    
    return detectedChapters;
  }, [content]);

  // 搜索结果
  const searchResults = useMemo(() => {
    if (!searchTerm.trim()) return [];
    
    const results: Array<{ lineNumber: number; content: string; preview: string }> = [];
    const searchLower = searchTerm.toLowerCase();
    
    content.forEach((line, index) => {
      if (line.toLowerCase().includes(searchLower)) {
        const startIndex = Math.max(0, line.toLowerCase().indexOf(searchLower) - 20);
        const endIndex = Math.min(line.length, startIndex + searchTerm.length + 40);
        const preview = line.substring(startIndex, endIndex);
        
        results.push({
          lineNumber: index,
          content: line,
          preview: startIndex > 0 ? '...' + preview : preview
        });
      }
    });
    
    return results.slice(0, 50); // 限制搜索结果数量
  }, [content, searchTerm]);

  // 切换章节展开状态
  const toggleChapter = (chapterNumber: number) => {
    const newExpanded = new Set(expandedChapters);
    if (newExpanded.has(chapterNumber)) {
      newExpanded.delete(chapterNumber);
    } else {
      newExpanded.add(chapterNumber);
    }
    setExpandedChapters(newExpanded);
  };

  // 获取章节内的段落
  const getChapterParagraphs = (chapter: Chapter) => {
    const paragraphs: Array<{ lineNumber: number; content: string }> = [];
    const startLine = chapter.startLine + 1; // 跳过章节标题
    const endLine = chapter.endLine || content.length - 1;
    
    for (let i = startLine; i <= endLine; i++) {
      const line = content[i];
      if (line && line.trim().length > 0) {
        paragraphs.push({
          lineNumber: i,
          content: line.trim()
        });
      }
    }
    
    return paragraphs.slice(0, 10); // 限制显示的段落数量
  };

  return (
    <div className="navigation-panel">
      {/* 搜索框 */}
      <div className="search-section">
        <div className="search-box">
          <input
            type="text"
            placeholder="搜索内容..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <span className="search-icon">🔍</span>
        </div>
        
        {searchTerm && (
          <div className="search-results">
            <div className="search-header">
              找到 {searchResults.length} 个结果
            </div>
            {searchResults.map((result, index) => (
              <div
                key={index}
                className="search-result"
                onClick={() => onNavigate(result.lineNumber)}
              >
                <div className="result-line">第 {result.lineNumber + 1} 行</div>
                <div className="result-preview">{result.preview}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 章节导航 */}
      {!searchTerm && (
        <div className="chapters-section">
          <div className="section-header">
            <h3>章节导航</h3>
            <span className="chapter-count">共 {chapters.length} 章</span>
          </div>
          
          {chapters.length === 0 ? (
            <div className="no-chapters">
              <p>未检测到章节结构</p>
              <p className="hint">支持格式：CHAPTER I. / 第一章 / 第1章</p>
            </div>
          ) : (
            <div className="chapters-list">
              {chapters.map((chapter) => (
                <div key={chapter.number} className="chapter-item">
                  <div
                    className="chapter-header"
                    onClick={() => onNavigate(chapter.startLine)}
                  >
                    <button
                      className="expand-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleChapter(chapter.number);
                      }}
                    >
                      {expandedChapters.has(chapter.number) ? '▼' : '▶'}
                    </button>
                    <span className="chapter-title">{chapter.title}</span>
                    <span className="chapter-info">
                      第 {chapter.startLine + 1} 行
                    </span>
                  </div>
                  
                  {expandedChapters.has(chapter.number) && (
                    <div className="chapter-content">
                      {getChapterParagraphs(chapter).map((paragraph) => (
                        <div
                          key={paragraph.lineNumber}
                          className="paragraph-item"
                          onClick={() => onNavigate(paragraph.lineNumber)}
                        >
                          <span className="paragraph-line">
                            {paragraph.lineNumber + 1}
                          </span>
                          <span className="paragraph-text">
                            {paragraph.content.substring(0, 50)}
                            {paragraph.content.length > 50 ? '...' : ''}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 快速跳转 */}
      <div className="quick-jump-section">
        <h3>快速跳转</h3>
        <div className="jump-controls">
          <button onClick={() => onNavigate(0)} className="jump-btn">
            文档开头
          </button>
          <button onClick={() => onNavigate(content.length - 1)} className="jump-btn">
            文档结尾
          </button>
        </div>
      </div>

      {/* 样式 */}
      <style jsx>{`
        .navigation-panel {
          height: 100%;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .search-section {
          position: relative;
        }

        .search-box {
          position: relative;
        }

        .search-input {
          width: 100%;
          padding: 0.5rem 2rem 0.5rem 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.875rem;
        }

        .search-input:focus {
          outline: none;
          border-color: #007bff;
        }

        .search-icon {
          position: absolute;
          right: 0.5rem;
          top: 50%;
          transform: translateY(-50%);
          color: #666;
        }

        .search-results {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: white;
          border: 1px solid #ddd;
          border-top: none;
          border-radius: 0 0 4px 4px;
          max-height: 300px;
          overflow-y: auto;
          z-index: 100;
          box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        .search-header {
          padding: 0.5rem 0.75rem;
          background: #f8f9fa;
          font-size: 0.875rem;
          color: #666;
          border-bottom: 1px solid #eee;
        }

        .search-result {
          padding: 0.5rem 0.75rem;
          cursor: pointer;
          border-bottom: 1px solid #f0f0f0;
        }

        .search-result:hover {
          background: #f8f9fa;
        }

        .result-line {
          font-size: 0.75rem;
          color: #007bff;
          margin-bottom: 0.25rem;
        }

        .result-preview {
          font-size: 0.875rem;
          color: #333;
          line-height: 1.4;
        }

        .chapters-section {
          flex: 1;
          overflow: hidden;
          display: flex;
          flex-direction: column;
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .section-header h3 {
          margin: 0;
          font-size: 1rem;
          color: #333;
        }

        .chapter-count {
          font-size: 0.75rem;
          color: #666;
          background: #f0f0f0;
          padding: 0.25rem 0.5rem;
          border-radius: 12px;
        }

        .no-chapters {
          text-align: center;
          color: #666;
          padding: 2rem 1rem;
        }

        .no-chapters p {
          margin: 0.5rem 0;
        }

        .hint {
          font-size: 0.75rem;
          color: #999;
        }

        .chapters-list {
          flex: 1;
          overflow-y: auto;
        }

        .chapter-item {
          margin-bottom: 0.5rem;
        }

        .chapter-header {
          display: flex;
          align-items: center;
          padding: 0.5rem;
          background: #f8f9fa;
          border-radius: 4px;
          cursor: pointer;
          transition: background-color 0.2s ease;
        }

        .chapter-header:hover {
          background: #e9ecef;
        }

        .expand-btn {
          background: none;
          border: none;
          cursor: pointer;
          margin-right: 0.5rem;
          font-size: 0.75rem;
          color: #666;
          width: 1rem;
          text-align: center;
        }

        .chapter-title {
          flex: 1;
          font-size: 0.875rem;
          font-weight: 500;
          color: #333;
        }

        .chapter-info {
          font-size: 0.75rem;
          color: #666;
        }

        .chapter-content {
          margin-top: 0.5rem;
          margin-left: 1.5rem;
        }

        .paragraph-item {
          display: flex;
          align-items: flex-start;
          padding: 0.25rem 0.5rem;
          cursor: pointer;
          border-radius: 3px;
          margin-bottom: 0.25rem;
        }

        .paragraph-item:hover {
          background: #f0f0f0;
        }

        .paragraph-line {
          font-size: 0.75rem;
          color: #007bff;
          margin-right: 0.5rem;
          min-width: 2rem;
        }

        .paragraph-text {
          font-size: 0.75rem;
          color: #555;
          line-height: 1.4;
        }

        .quick-jump-section h3 {
          margin: 0 0 0.5rem 0;
          font-size: 1rem;
          color: #333;
        }

        .jump-controls {
          display: flex;
          gap: 0.5rem;
        }

        .jump-btn {
          flex: 1;
          padding: 0.5rem;
          border: 1px solid #ddd;
          background: white;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.875rem;
          transition: all 0.2s ease;
        }

        .jump-btn:hover {
          background: #f8f9fa;
          border-color: #007bff;
        }
      `}</style>
    </div>
  );
};
