#!/usr/bin/env python3
"""
配置管理脚本
管理系统配置、环境变量和部署配置
"""
import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass, asdict

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str = "localhost"
    port: int = 5432
    database: str = "translation_db"
    username: str = "postgres"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30


@dataclass
class RedisConfig:
    """Redis配置"""
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: str = ""
    max_connections: int = 10
    socket_timeout: int = 5


@dataclass
class TranslationConfig:
    """翻译配置"""
    google_api_key: str = ""
    openai_api_key: str = ""
    default_provider: str = "google"
    cache_ttl: int = 3600
    max_batch_size: int = 100
    request_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 1


@dataclass
class CostConfig:
    """成本配置"""
    daily_budget: float = 100.0
    monthly_budget: float = 3000.0
    google_price_per_char: float = 0.00002  # $20/1M chars
    openai_price_per_token: float = 0.002   # $2/1K tokens
    alert_threshold: float = 0.8  # 80%


@dataclass
class SecurityConfig:
    """安全配置"""
    secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours
    cors_origins: List[str] = None
    rate_limit_per_minute: int = 100
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000"]


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/app.log"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    enable_console: bool = True


@dataclass
class ServerConfig:
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    worker_class: str = "uvicorn.workers.UvicornWorker"
    timeout: int = 30
    keepalive: int = 2
    max_requests: int = 1000
    max_requests_jitter: int = 100


@dataclass
class SystemConfig:
    """系统配置"""
    environment: str = "development"
    debug: bool = False
    testing: bool = False
    database: DatabaseConfig = None
    redis: RedisConfig = None
    translation: TranslationConfig = None
    cost: CostConfig = None
    security: SecurityConfig = None
    logging: LoggingConfig = None
    server: ServerConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
        if self.redis is None:
            self.redis = RedisConfig()
        if self.translation is None:
            self.translation = TranslationConfig()
        if self.cost is None:
            self.cost = CostConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
        if self.server is None:
            self.server = ServerConfig()


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path("config")
        self.config_dir.mkdir(exist_ok=True)
        self.env_file = Path(".env")
    
    def load_config(self, environment: str = "development") -> SystemConfig:
        """加载配置"""
        config_file = self.config_dir / f"{environment}.yaml"
        
        if config_file.exists():
            logger.info(f"从文件加载配置: {config_file}")
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            return self._dict_to_config(config_data)
        else:
            logger.info(f"配置文件不存在，使用默认配置: {config_file}")
            return SystemConfig(environment=environment)
    
    def save_config(self, config: SystemConfig, environment: str = None):
        """保存配置"""
        if environment is None:
            environment = config.environment
        
        config_file = self.config_dir / f"{environment}.yaml"
        config_data = self._config_to_dict(config)
        
        logger.info(f"保存配置到文件: {config_file}")
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
    
    def _dict_to_config(self, data: Dict[str, Any]) -> SystemConfig:
        """字典转配置对象"""
        config = SystemConfig()
        
        if 'environment' in data:
            config.environment = data['environment']
        if 'debug' in data:
            config.debug = data['debug']
        if 'testing' in data:
            config.testing = data['testing']
        
        # 数据库配置
        if 'database' in data:
            db_data = data['database']
            config.database = DatabaseConfig(**db_data)
        
        # Redis配置
        if 'redis' in data:
            redis_data = data['redis']
            config.redis = RedisConfig(**redis_data)
        
        # 翻译配置
        if 'translation' in data:
            trans_data = data['translation']
            config.translation = TranslationConfig(**trans_data)
        
        # 成本配置
        if 'cost' in data:
            cost_data = data['cost']
            config.cost = CostConfig(**cost_data)
        
        # 安全配置
        if 'security' in data:
            sec_data = data['security']
            config.security = SecurityConfig(**sec_data)
        
        # 日志配置
        if 'logging' in data:
            log_data = data['logging']
            config.logging = LoggingConfig(**log_data)
        
        # 服务器配置
        if 'server' in data:
            server_data = data['server']
            config.server = ServerConfig(**server_data)
        
        return config
    
    def _config_to_dict(self, config: SystemConfig) -> Dict[str, Any]:
        """配置对象转字典"""
        return {
            'environment': config.environment,
            'debug': config.debug,
            'testing': config.testing,
            'database': asdict(config.database),
            'redis': asdict(config.redis),
            'translation': asdict(config.translation),
            'cost': asdict(config.cost),
            'security': asdict(config.security),
            'logging': asdict(config.logging),
            'server': asdict(config.server)
        }
    
    def generate_env_file(self, config: SystemConfig):
        """生成.env文件"""
        logger.info(f"生成环境变量文件: {self.env_file}")
        
        env_vars = [
            "# 翻译系统环境变量配置",
            "# 自动生成，请勿手动编辑",
            "",
            "# 环境设置",
            f"ENVIRONMENT={config.environment}",
            f"DEBUG={str(config.debug).lower()}",
            f"TESTING={str(config.testing).lower()}",
            "",
            "# 数据库配置",
            f"DB_HOST={config.database.host}",
            f"DB_PORT={config.database.port}",
            f"DB_NAME={config.database.database}",
            f"DB_USER={config.database.username}",
            f"DB_PASSWORD={config.database.password}",
            f"DB_POOL_SIZE={config.database.pool_size}",
            "",
            "# Redis配置",
            f"REDIS_HOST={config.redis.host}",
            f"REDIS_PORT={config.redis.port}",
            f"REDIS_DB={config.redis.database}",
            f"REDIS_PASSWORD={config.redis.password}",
            "",
            "# 翻译API配置",
            f"GOOGLE_TRANSLATE_API_KEY={config.translation.google_api_key}",
            f"OPENAI_API_KEY={config.translation.openai_api_key}",
            f"DEFAULT_TRANSLATION_PROVIDER={config.translation.default_provider}",
            f"TRANSLATION_CACHE_TTL={config.translation.cache_ttl}",
            f"MAX_BATCH_SIZE={config.translation.max_batch_size}",
            "",
            "# 成本控制",
            f"DAILY_BUDGET={config.cost.daily_budget}",
            f"MONTHLY_BUDGET={config.cost.monthly_budget}",
            f"COST_ALERT_THRESHOLD={config.cost.alert_threshold}",
            "",
            "# 安全配置",
            f"SECRET_KEY={config.security.secret_key}",
            f"JWT_ALGORITHM={config.security.jwt_algorithm}",
            f"JWT_EXPIRE_MINUTES={config.security.jwt_expire_minutes}",
            f"CORS_ORIGINS={','.join(config.security.cors_origins)}",
            f"RATE_LIMIT_PER_MINUTE={config.security.rate_limit_per_minute}",
            "",
            "# 服务器配置",
            f"SERVER_HOST={config.server.host}",
            f"SERVER_PORT={config.server.port}",
            f"SERVER_WORKERS={config.server.workers}",
            "",
            "# 日志配置",
            f"LOG_LEVEL={config.logging.level}",
            f"LOG_FILE={config.logging.file_path}",
            ""
        ]
        
        with open(self.env_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(env_vars))
    
    def load_from_env(self) -> SystemConfig:
        """从环境变量加载配置"""
        logger.info("从环境变量加载配置")
        
        config = SystemConfig()
        
        # 基本设置
        config.environment = os.getenv("ENVIRONMENT", "development")
        config.debug = os.getenv("DEBUG", "false").lower() == "true"
        config.testing = os.getenv("TESTING", "false").lower() == "true"
        
        # 数据库配置
        config.database.host = os.getenv("DB_HOST", "localhost")
        config.database.port = int(os.getenv("DB_PORT", "5432"))
        config.database.database = os.getenv("DB_NAME", "translation_db")
        config.database.username = os.getenv("DB_USER", "postgres")
        config.database.password = os.getenv("DB_PASSWORD", "")
        config.database.pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        
        # Redis配置
        config.redis.host = os.getenv("REDIS_HOST", "localhost")
        config.redis.port = int(os.getenv("REDIS_PORT", "6379"))
        config.redis.database = int(os.getenv("REDIS_DB", "0"))
        config.redis.password = os.getenv("REDIS_PASSWORD", "")
        
        # 翻译配置
        config.translation.google_api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY", "")
        config.translation.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        config.translation.default_provider = os.getenv("DEFAULT_TRANSLATION_PROVIDER", "google")
        config.translation.cache_ttl = int(os.getenv("TRANSLATION_CACHE_TTL", "3600"))
        config.translation.max_batch_size = int(os.getenv("MAX_BATCH_SIZE", "100"))
        
        # 成本配置
        config.cost.daily_budget = float(os.getenv("DAILY_BUDGET", "100.0"))
        config.cost.monthly_budget = float(os.getenv("MONTHLY_BUDGET", "3000.0"))
        config.cost.alert_threshold = float(os.getenv("COST_ALERT_THRESHOLD", "0.8"))
        
        # 安全配置
        config.security.secret_key = os.getenv("SECRET_KEY", "")
        config.security.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        config.security.jwt_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
        cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
        config.security.cors_origins = [origin.strip() for origin in cors_origins.split(",")]
        config.security.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
        
        # 服务器配置
        config.server.host = os.getenv("SERVER_HOST", "0.0.0.0")
        config.server.port = int(os.getenv("SERVER_PORT", "8000"))
        config.server.workers = int(os.getenv("SERVER_WORKERS", "1"))
        
        # 日志配置
        config.logging.level = os.getenv("LOG_LEVEL", "INFO")
        config.logging.file_path = os.getenv("LOG_FILE", "logs/app.log")
        
        return config
    
    def validate_config(self, config: SystemConfig) -> List[str]:
        """验证配置"""
        errors = []
        
        # 验证必需的API密钥
        if not config.translation.google_api_key and not config.translation.openai_api_key:
            errors.append("至少需要配置一个翻译API密钥")
        
        # 验证数据库配置
        if not config.database.host:
            errors.append("数据库主机不能为空")
        if not config.database.database:
            errors.append("数据库名称不能为空")
        if not config.database.username:
            errors.append("数据库用户名不能为空")
        
        # 验证安全配置
        if not config.security.secret_key:
            errors.append("SECRET_KEY不能为空")
        if len(config.security.secret_key) < 32:
            errors.append("SECRET_KEY长度至少32个字符")
        
        # 验证成本配置
        if config.cost.daily_budget <= 0:
            errors.append("每日预算必须大于0")
        if config.cost.monthly_budget <= 0:
            errors.append("每月预算必须大于0")
        
        # 验证服务器配置
        if config.server.port < 1 or config.server.port > 65535:
            errors.append("服务器端口必须在1-65535之间")
        
        return errors
    
    def create_default_configs(self):
        """创建默认配置文件"""
        environments = ["development", "testing", "production"]
        
        for env in environments:
            config = SystemConfig(environment=env)
            
            if env == "development":
                config.debug = True
                config.logging.level = "DEBUG"
            elif env == "testing":
                config.testing = True
                config.database.database = "test_translation_db"
            elif env == "production":
                config.debug = False
                config.logging.level = "INFO"
                config.server.workers = 4
            
            self.save_config(config, env)
            logger.info(f"创建默认配置: {env}")
    
    def generate_secret_key(self) -> str:
        """生成安全密钥"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def setup_production_config(self):
        """设置生产环境配置"""
        config = self.load_config("production")
        
        # 生成安全密钥
        if not config.security.secret_key:
            config.security.secret_key = self.generate_secret_key()
        
        # 生产环境优化
        config.debug = False
        config.server.workers = 4
        config.database.pool_size = 20
        config.database.max_overflow = 40
        config.logging.level = "INFO"
        
        # 保存配置
        self.save_config(config, "production")
        logger.info("生产环境配置已更新")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="配置管理工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 初始化命令
    init_parser = subparsers.add_parser('init', help='初始化配置文件')
    
    # 生成命令
    generate_parser = subparsers.add_parser('generate', help='生成配置文件')
    generate_parser.add_argument('--env', default='development', help='环境名称')
    generate_parser.add_argument('--env-file', action='store_true', help='生成.env文件')
    
    # 验证命令
    validate_parser = subparsers.add_parser('validate', help='验证配置')
    validate_parser.add_argument('--env', default='development', help='环境名称')
    
    # 显示命令
    show_parser = subparsers.add_parser('show', help='显示配置')
    show_parser.add_argument('--env', default='development', help='环境名称')
    
    # 生产环境设置
    prod_parser = subparsers.add_parser('setup-prod', help='设置生产环境')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    config_manager = ConfigManager()
    
    try:
        if args.command == 'init':
            config_manager.create_default_configs()
            print("默认配置文件已创建")
        
        elif args.command == 'generate':
            config = config_manager.load_config(args.env)
            
            if args.env_file:
                config_manager.generate_env_file(config)
                print(f".env文件已生成")
            else:
                config_manager.save_config(config, args.env)
                print(f"{args.env}环境配置文件已生成")
        
        elif args.command == 'validate':
            config = config_manager.load_config(args.env)
            errors = config_manager.validate_config(config)
            
            if errors:
                print("配置验证失败:")
                for error in errors:
                    print(f"  ❌ {error}")
                sys.exit(1)
            else:
                print("✅ 配置验证通过")
        
        elif args.command == 'show':
            config = config_manager.load_config(args.env)
            config_dict = config_manager._config_to_dict(config)
            print(yaml.dump(config_dict, default_flow_style=False, allow_unicode=True))
        
        elif args.command == 'setup-prod':
            config_manager.setup_production_config()
            print("生产环境配置已设置")
    
    except Exception as e:
        logger.error(f"操作失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
