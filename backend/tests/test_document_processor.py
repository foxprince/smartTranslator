"""
文档处理服务单元测试
"""
import pytest
from app.services.document_processor import DocumentProcessor, DocumentProcessingError
from app.schemas.document import DocumentPreprocessRequest


class TestDocumentProcessor:
    """测试文档处理器"""
    
    def setup_method(self):
        """测试前准备"""
        self.processor = DocumentProcessor()
    
    def test_validate_request_success(self):
        """测试请求验证成功"""
        request = DocumentPreprocessRequest(
            file_content="测试内容\n第二行内容",
            filename="test.txt"
        )
        
        # 不应该抛出异常
        self.processor.validate_request(request)
    
    def test_validate_request_invalid_extension(self):
        """测试无效文件扩展名"""
        request = DocumentPreprocessRequest(
            file_content="测试内容",
            filename="test.doc"  # 不支持的格式
        )
        
        with pytest.raises(DocumentProcessingError) as exc_info:
            self.processor.validate_request(request)
        
        assert "不支持的文件格式" in str(exc_info.value)
    
    def test_validate_request_empty_filename(self):
        """测试空文件名"""
        request = DocumentPreprocessRequest(
            file_content="测试内容",
            filename=""
        )
        
        with pytest.raises(DocumentProcessingError) as exc_info:
            self.processor.validate_request(request)
        
        assert "文件名不能为空" in str(exc_info.value)
    
    def test_preprocess_document_success(self):
        """测试文档预处理成功"""
        request = DocumentPreprocessRequest(
            file_content="第一行内容\n\n第二行内容\n短\n这是一个较长的行",
            filename="test.txt"
        )
        
        result = self.processor.preprocess_document(request)
        
        assert result.cleaned_content is not None
        assert result.processing_report is not None
        assert result.processing_report.processing_time > 0
        assert len(result.processing_report.changes_made) > 0
    
    def test_preprocess_document_with_issues(self):
        """测试包含问题的文档预处理"""
        # 创建包含各种问题的测试文档
        content = """第一章 测试章节

这是正常的段落内容。

短

这是一个非常长的行内容""" + "很长很长" * 50 + """

"第一个对话""第二个对话""第三个对话"

结束内容。
"""
        
        request = DocumentPreprocessRequest(
            file_content=content,
            filename="test_with_issues.txt"
        )
        
        result = self.processor.preprocess_document(request)
        
        # 检查是否检测到问题
        assert len(result.processing_report.issues_found) > 0
        
        # 检查是否有短行问题
        short_line_issues = [
            issue for issue in result.processing_report.issues_found 
            if issue.issue_type == "short_line"
        ]
        assert len(short_line_issues) > 0
        
        # 检查是否有对话合并问题
        dialogue_issues = [
            issue for issue in result.processing_report.issues_found 
            if issue.issue_type == "dialogue_merge"
        ]
        assert len(dialogue_issues) > 0
        
        # 检查是否有长行问题
        long_line_issues = [
            issue for issue in result.processing_report.issues_found 
            if issue.issue_type == "long_line"
        ]
        assert len(long_line_issues) > 0
    
    def test_generate_changes_summary(self):
        """测试修改摘要生成"""
        from app.schemas.document import TextStats
        
        original_stats = TextStats(
            total_lines=10,
            empty_lines=3,
            content_lines=7,
            short_lines=2,
            long_lines=1,
            average_line_length=50.0,
            encoding="utf-8"
        )
        
        cleaned_stats = TextStats(
            total_lines=8,
            empty_lines=1,
            content_lines=7,
            short_lines=0,
            long_lines=1,
            average_line_length=55.0,
            encoding="utf-8"
        )
        
        changes = self.processor._generate_changes_summary(
            original_stats, 
            cleaned_stats, 
            chapter_count=2
        )
        
        assert len(changes) > 0
        assert any("移除了" in change for change in changes)
        assert any("检测到 2 个章节" in change for change in changes)
        assert any("合并了" in change for change in changes)
