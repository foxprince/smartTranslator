"""
文本工具函数单元测试
"""
import pytest
from app.utils.text_utils import (
    analyze_text_format,
    detect_text_issues,
    detect_chapters,
    standardize_format,
    should_merge_with_next
)


class TestAnalyzeTextFormat:
    """测试文本格式分析"""
    
    def test_basic_analysis(self):
        """测试基本分析功能"""
        lines = [
            "第一行内容",
            "",
            "第三行内容比较长一些，用来测试平均长度计算",
            "短",  # 1字符，< 5，算短行
            ""
        ]
        
        stats = analyze_text_format(lines)
        
        assert stats.total_lines == 5
        assert stats.empty_lines == 2
        assert stats.content_lines == 3
        assert stats.short_lines == 1  # "短" < 5字符
        assert stats.long_lines == 0
        assert stats.encoding == "utf-8"
        assert stats.average_line_length > 0
    
    def test_long_lines_detection(self):
        """测试长行检测"""
        long_line = "这是一个非常长的行内容" * 10  # 超过100字符
        lines = ["正常行", long_line, "另一个正常行"]
        
        stats = analyze_text_format(lines)
        
        assert stats.long_lines == 1
        assert stats.total_lines == 3


class TestDetectTextIssues:
    """测试文本问题检测"""
    
    def test_short_line_detection(self):
        """测试短行检测"""
        lines = ["正常长度的行内容", "短", "另一个正常行"]  # 只有"短"(1字符) < 5
        
        issues = detect_text_issues(lines)
        
        short_line_issues = [issue for issue in issues if issue.issue_type == "short_line"]
        assert len(short_line_issues) == 1
        assert short_line_issues[0].line_number == 2
    
    def test_dialogue_merge_detection(self):
        """测试对话合并检测"""
        lines = [
            '正常行',
            '"第一个对话""第二个对话""第三个对话"',  # 包含多个对话
            '正常行'
        ]
        
        issues = detect_text_issues(lines)
        
        dialogue_issues = [issue for issue in issues if issue.issue_type == "dialogue_merge"]
        assert len(dialogue_issues) == 1
        assert dialogue_issues[0].line_number == 2


class TestDetectChapters:
    """测试章节检测"""
    
    def test_english_chapters(self):
        """测试英文章节检测"""
        lines = [
            "Some content",
            "CHAPTER I.",
            "Chapter content",
            "CHAPTER II.",
            "More content"
        ]
        
        chapters = detect_chapters(lines)
        
        assert len(chapters) == 2
        assert chapters[0] == (2, "CHAPTER I.")
        assert chapters[1] == (4, "CHAPTER II.")
    
    def test_chinese_chapters(self):
        """测试中文章节检测"""
        lines = [
            "一些内容",
            "第一章",
            "章节内容",
            "第二章",
            "更多内容"
        ]
        
        chapters = detect_chapters(lines)
        
        assert len(chapters) == 2
        assert chapters[0] == (2, "第一章")
        assert chapters[1] == (4, "第二章")


class TestShouldMergeWithNext:
    """测试行合并判断"""
    
    def test_should_merge_short_line(self):
        """测试短行合并"""
        lines = ["短行", "这是下一行的内容"]
        
        result = should_merge_with_next("短行", lines, 0)
        
        assert result is True
    
    def test_should_not_merge_complete_sentence(self):
        """测试完整句子不合并"""
        lines = ["这是一个完整的句子。", "这是下一行"]
        
        result = should_merge_with_next("这是一个完整的句子。", lines, 0)
        
        assert result is False
    
    def test_should_not_merge_with_chapter(self):
        """测试不与章节标题合并"""
        lines = ["短行", "第一章"]
        
        result = should_merge_with_next("短行", lines, 0)
        
        assert result is False


class TestStandardizeFormat:
    """测试格式标准化"""
    
    def test_remove_empty_lines(self):
        """测试移除空行"""
        lines = ["第一行", "", "第二行", "", "第三行"]
        
        result = standardize_format(lines)
        
        assert len(result) == 3
        assert result == ["第一行", "第二行", "第三行"]
    
    def test_merge_short_lines(self):
        """测试合并短行"""
        lines = ["短", "这是一个较长的行内容"]
        
        result = standardize_format(lines)
        
        # 短行应该被合并
        assert len(result) == 1
        assert "短 这是一个较长的行内容" in result[0]
