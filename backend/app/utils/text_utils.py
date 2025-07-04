"""
文本处理工具函数
基于《真正的朋友》项目的实践经验
"""
import re
from typing import List, Tuple
from ..schemas.document import TextStats, TextIssue


def analyze_text_format(lines: List[str], encoding: str = "utf-8") -> TextStats:
    """
    分析文本格式的核心算法
    
    Args:
        lines: 文本行列表
        encoding: 文件编码
        
    Returns:
        TextStats: 文本统计信息
    """
    total_lines = len(lines)
    empty_lines = sum(1 for line in lines if not line.strip())
    content_lines = sum(1 for line in lines if line.strip())
    
    # 对于中文文本，使用更合适的阈值
    short_lines = sum(1 for line in lines if 0 < len(line.strip()) < 5)  # 中文短行阈值调整为5
    long_lines = sum(1 for line in lines if len(line.strip()) > 100)  # 中文长行阈值调整为100
    
    # 计算平均行长度（仅计算非空行）
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    average_line_length = sum(len(line) for line in non_empty_lines) / len(non_empty_lines) if non_empty_lines else 0
    
    return TextStats(
        total_lines=total_lines,
        empty_lines=empty_lines,
        content_lines=content_lines,
        short_lines=short_lines,
        long_lines=long_lines,
        average_line_length=round(average_line_length, 2),
        encoding=encoding
    )


def detect_text_issues(lines: List[str]) -> List[TextIssue]:
    """
    检测文本中的格式问题
    
    Args:
        lines: 文本行列表
        
    Returns:
        List[TextIssue]: 发现的问题列表
    """
    issues = []
    
    for i, line in enumerate(lines, 1):
        line_content = line.strip()
        
        # 检测过短行（中文阈值调整）
        if 0 < len(line_content) < 5:
            issues.append(TextIssue(
                line_number=i,
                issue_type="short_line",
                description=f"行内容过短({len(line_content)}字符)",
                suggestion="检查是否为段落分割错误"
            ))
        
        # 检测过长行（中文阈值调整）
        if len(line_content) > 100:
            issues.append(TextIssue(
                line_number=i,
                issue_type="long_line",
                description=f"行内容过长({len(line_content)}字符)",
                suggestion="检查是否需要分段"
            ))
        
        # 检测可能的对话合并问题
        if line_content.count('"') >= 4:
            issues.append(TextIssue(
                line_number=i,
                issue_type="dialogue_merge",
                description="可能存在对话合并问题",
                suggestion="检查是否需要分行显示不同对话"
            ))
    
    return issues


def detect_chapters(lines: List[str]) -> List[Tuple[int, str]]:
    """
    检测章节结构
    
    Args:
        lines: 文本行列表
        
    Returns:
        List[Tuple[int, str]]: 章节位置和标题列表
    """
    chapters = []
    
    # 英文章节模式
    en_pattern = r'^CHAPTER\s+[IVX]+\.'
    # 中文章节模式
    cn_pattern = r'^第[一二三四五六七八九十]+章'
    
    for i, line in enumerate(lines):
        line_content = line.strip()
        if re.match(en_pattern, line_content) or re.match(cn_pattern, line_content):
            chapters.append((i + 1, line_content))
    
    return chapters


def should_merge_with_next(current_line: str, lines: List[str], index: int) -> bool:
    """
    判断当前行是否应该与下一行合并
    
    Args:
        current_line: 当前行内容
        lines: 所有行列表
        index: 当前行索引
        
    Returns:
        bool: 是否应该合并
    """
    if index >= len(lines) - 1:
        return False
    
    next_line = lines[index + 1].strip()
    if not next_line:
        return False
    
    # 如果当前行很短且下一行不是章节标题，考虑合并
    if len(current_line) < 50 and not re.match(r'^(CHAPTER|第.+章)', next_line):
        # 检查是否是句子的延续
        if not current_line.endswith(('.', '!', '?', '。', '！', '？')):
            return True
    
    return False


def merge_lines(lines_to_merge: List[str]) -> str:
    """
    合并多行文本
    
    Args:
        lines_to_merge: 需要合并的行列表
        
    Returns:
        str: 合并后的文本
    """
    return ' '.join(line.strip() for line in lines_to_merge if line.strip())


def standardize_format(lines: List[str]) -> List[str]:
    """
    格式标准化核心算法
    
    Args:
        lines: 原始文本行列表
        
    Returns:
        List[str]: 标准化后的文本行列表
    """
    cleaned_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # 跳过空行
        if not line:
            i += 1
            continue
        
        # 检查是否需要与下一行合并
        if should_merge_with_next(line, lines, i):
            merged_line = merge_lines(lines[i:i+2])
            cleaned_lines.append(merged_line)
            i += 2
        else:
            cleaned_lines.append(line)
            i += 1
    
    return cleaned_lines
