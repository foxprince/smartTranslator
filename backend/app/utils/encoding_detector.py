"""
文件编码检测工具
"""
import chardet
from typing import Optional


def detect_encoding(content: bytes) -> str:
    """
    检测文件编码
    
    Args:
        content: 文件字节内容
        
    Returns:
        str: 检测到的编码格式
        
    Raises:
        ValueError: 编码检测失败
    """
    try:
        # 使用chardet检测编码
        result = chardet.detect(content)
        
        if result['encoding'] is None:
            # 如果检测失败，尝试常见编码
            common_encodings = ['utf-8', 'gbk', 'gb2312', 'big5', 'ascii']
            
            for encoding in common_encodings:
                try:
                    content.decode(encoding)
                    return encoding
                except UnicodeDecodeError:
                    continue
            
            raise ValueError("无法检测文件编码")
        
        return result['encoding'].lower()
    
    except Exception as e:
        raise ValueError(f"编码检测失败: {str(e)}")


def safe_decode(content: bytes, encoding: Optional[str] = None) -> str:
    """
    安全解码文件内容
    
    Args:
        content: 文件字节内容
        encoding: 指定编码，为空则自动检测
        
    Returns:
        str: 解码后的文本内容
        
    Raises:
        ValueError: 解码失败
    """
    if encoding is None:
        encoding = detect_encoding(content)
    
    try:
        return content.decode(encoding)
    except UnicodeDecodeError as e:
        # 如果指定编码失败，尝试自动检测
        if encoding != 'utf-8':
            try:
                return content.decode('utf-8', errors='replace')
            except:
                pass
        
        raise ValueError(f"使用编码 {encoding} 解码失败: {str(e)}")


def validate_text_content(content: str) -> bool:
    """
    验证文本内容是否有效
    
    Args:
        content: 文本内容
        
    Returns:
        bool: 内容是否有效
    """
    if not content or not content.strip():
        return False
    
    # 检查是否包含过多的乱码字符
    replacement_char_count = content.count('�')
    if replacement_char_count > len(content) * 0.1:  # 超过10%的替换字符
        return False
    
    return True
