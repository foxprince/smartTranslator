"""
应用配置设置
"""
import os
from typing import List


class Settings:
    def __init__(self):
        # 应用基本配置
        self.APP_NAME: str = "Translation System"
        self.VERSION: str = "1.0.0"
        self.DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
        
        # 数据库配置
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/translation_db")
        
        # Redis配置
        self.REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # API密钥
        self.GOOGLE_TRANSLATE_API_KEY: str = os.getenv("GOOGLE_TRANSLATE_API_KEY", "")
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
        
        # 翻译配置
        self.DEFAULT_TRANSLATION_PROVIDER: str = os.getenv("DEFAULT_TRANSLATION_PROVIDER", "google")
        self.TRANSLATION_CACHE_TTL: int = int(os.getenv("TRANSLATION_CACHE_TTL", "3600"))  # 1小时
        self.MAX_BATCH_SIZE: int = int(os.getenv("MAX_BATCH_SIZE", "100"))
        
        # 文档处理配置
        self.UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
        self.MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", str(50 * 1024 * 1024)))  # 50MB
        self.ALLOWED_EXTENSIONS: List[str] = [
            ".txt", ".md", ".rtf", ".doc", ".docx", ".xls", ".xlsx",
            ".ppt", ".pptx", ".pdf", ".html", ".htm", ".xml",
            ".json", ".csv", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"
        ]
        
        # OCR配置
        self.TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "")  # Tesseract可执行文件路径
        self.OCR_LANGUAGES: str = os.getenv("OCR_LANGUAGES", "chi_sim+eng")  # 支持的OCR语言
        
        # 成本控制
        self.DAILY_BUDGET: float = float(os.getenv("DAILY_BUDGET", "100.0"))
        self.MONTHLY_BUDGET: float = float(os.getenv("MONTHLY_BUDGET", "3000.0"))
        
        # 安全配置
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24小时


settings = Settings()
