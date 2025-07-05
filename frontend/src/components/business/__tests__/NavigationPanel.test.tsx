/**
 * NavigationPanel 组件测试
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { NavigationPanel } from '../NavigationPanel';

// Mock数据
const mockContent = [
  'CHAPTER I.',
  'This is the first chapter content.',
  'Some more content in chapter one.',
  '',
  'CHAPTER II.',
  'This is the second chapter content.',
  'More content here.',
  '',
  '第三章',
  '这是第三章的内容。',
  '更多中文内容。'
];

const mockOnNavigate = jest.fn();

describe('NavigationPanel', () => {
  beforeEach(() => {
    mockOnNavigate.mockClear();
  });

  test('renders navigation panel with search box', () => {
    render(
      <NavigationPanel
        content={mockContent}
        onNavigate={mockOnNavigate}
      />
    );

    expect(screen.getByPlaceholderText('搜索内容...')).toBeInTheDocument();
    expect(screen.getByText('章节导航')).toBeInTheDocument();
  });

  test('detects chapters correctly', () => {
    render(
      <NavigationPanel
        content={mockContent}
        onNavigate={mockOnNavigate}
      />
    );

    expect(screen.getByText('共 3 章')).toBeInTheDocument();
    expect(screen.getByText('CHAPTER I.')).toBeInTheDocument();
    expect(screen.getByText('CHAPTER II.')).toBeInTheDocument();
    expect(screen.getByText('第三章')).toBeInTheDocument();
  });

  test('handles search functionality', () => {
    render(
      <NavigationPanel
        content={mockContent}
        onNavigate={mockOnNavigate}
      />
    );

    const searchInput = screen.getByPlaceholderText('搜索内容...');
    fireEvent.change(searchInput, { target: { value: 'first' } });

    expect(screen.getByText('找到 1 个结果')).toBeInTheDocument();
    expect(screen.getByText('第 2 行')).toBeInTheDocument();
  });

  test('calls onNavigate when chapter is clicked', () => {
    render(
      <NavigationPanel
        content={mockContent}
        onNavigate={mockOnNavigate}
      />
    );

    const firstChapter = screen.getByText('CHAPTER I.');
    fireEvent.click(firstChapter);

    expect(mockOnNavigate).toHaveBeenCalledWith(0);
  });

  test('expands and collapses chapters', () => {
    render(
      <NavigationPanel
        content={mockContent}
        onNavigate={mockOnNavigate}
      />
    );

    const expandButton = screen.getAllByText('▶')[0];
    fireEvent.click(expandButton);

    // 章节应该展开，显示段落
    expect(screen.getByText('This is the first chapter content.')).toBeInTheDocument();
  });

  test('handles quick jump buttons', () => {
    render(
      <NavigationPanel
        content={mockContent}
        onNavigate={mockOnNavigate}
      />
    );

    const jumpToStart = screen.getByText('文档开头');
    const jumpToEnd = screen.getByText('文档结尾');

    fireEvent.click(jumpToStart);
    expect(mockOnNavigate).toHaveBeenCalledWith(0);

    fireEvent.click(jumpToEnd);
    expect(mockOnNavigate).toHaveBeenCalledWith(mockContent.length - 1);
  });

  test('shows no chapters message when no chapters detected', () => {
    const contentWithoutChapters = [
      'Just some regular content',
      'No chapters here',
      'More regular text'
    ];

    render(
      <NavigationPanel
        content={contentWithoutChapters}
        onNavigate={mockOnNavigate}
      />
    );

    expect(screen.getByText('未检测到章节结构')).toBeInTheDocument();
    expect(screen.getByText('支持格式：CHAPTER I. / 第一章 / 第1章')).toBeInTheDocument();
  });

  test('limits search results to 50', () => {
    // 创建包含大量匹配项的内容
    const largeContent = Array(100).fill('test content line');
    
    render(
      <NavigationPanel
        content={largeContent}
        onNavigate={mockOnNavigate}
      />
    );

    const searchInput = screen.getByPlaceholderText('搜索内容...');
    fireEvent.change(searchInput, { target: { value: 'test' } });

    expect(screen.getByText('找到 50 个结果')).toBeInTheDocument();
  });
});
