"""
应用配置设置
"""
from pydantic import BaseSettings


class Settings(BaseSettings):
    # 应用基本配置
    APP_NAME: str = "Translation System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://user:password@localhost/translation_db"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    
    # API密钥
    GOOGLE_TRANSLATE_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # 翻译配置
    DEFAULT_TRANSLATION_PROVIDER: str = "google"
    TRANSLATION_CACHE_TTL: int = 3600  # 1小时
    MAX_BATCH_SIZE: int = 100
    
    # 文档处理配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: list = [
        ".txt", ".md", ".rtf", ".doc", ".docx", ".xls", ".xlsx", 
        ".ppt", ".pptx", ".pdf", ".html", ".htm", ".xml", 
        ".json", ".csv", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"
    ]
    
    # OCR配置
    TESSERACT_CMD: str = ""  # Tesseract可执行文件路径
    OCR_LANGUAGES: str = "chi_sim+eng"  # 支持的OCR语言
    
    # 成本控制
    DAILY_BUDGET: float = 100.0
    MONTHLY_BUDGET: float = 3000.0
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24小时
    
    class Config:
        env_file = ".env"


settings = Settings()
