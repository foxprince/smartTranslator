#!/usr/bin/env python3
"""
部署脚本
自动化部署翻译系统到不同环境
"""
import os
import sys
import subprocess
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional
import logging
import yaml
import requests

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeploymentManager:
    """部署管理器"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.config_dir = self.project_root / "config"
        self.deployment_config = {}
    
    def load_deployment_config(self, environment: str) -> Dict:
        """加载部署配置"""
        config_file = self.config_dir / f"deploy_{environment}.yaml"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            return self.get_default_deployment_config(environment)
    
    def get_default_deployment_config(self, environment: str) -> Dict:
        """获取默认部署配置"""
        if environment == "development":
            return {
                "environment": "development",
                "host": "localhost",
                "port": 8000,
                "workers": 1,
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "name": "translation_db"
                },
                "redis": {
                    "host": "localhost",
                    "port": 6379
                },
                "docker": {
                    "enabled": False
                },
                "nginx": {
                    "enabled": False
                },
                "ssl": {
                    "enabled": False
                }
            }
        elif environment == "staging":
            return {
                "environment": "staging",
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 2,
                "database": {
                    "host": "staging-db.example.com",
                    "port": 5432,
                    "name": "translation_db_staging"
                },
                "redis": {
                    "host": "staging-redis.example.com",
                    "port": 6379
                },
                "docker": {
                    "enabled": True,
                    "image": "translation-backend:staging"
                },
                "nginx": {
                    "enabled": True,
                    "config": "nginx/staging.conf"
                },
                "ssl": {
                    "enabled": True,
                    "cert_path": "/etc/ssl/certs/staging.crt",
                    "key_path": "/etc/ssl/private/staging.key"
                }
            }
        elif environment == "production":
            return {
                "environment": "production",
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 4,
                "database": {
                    "host": "prod-db.example.com",
                    "port": 5432,
                    "name": "translation_db"
                },
                "redis": {
                    "host": "prod-redis.example.com",
                    "port": 6379
                },
                "docker": {
                    "enabled": True,
                    "image": "translation-backend:latest"
                },
                "nginx": {
                    "enabled": True,
                    "config": "nginx/production.conf"
                },
                "ssl": {
                    "enabled": True,
                    "cert_path": "/etc/ssl/certs/production.crt",
                    "key_path": "/etc/ssl/private/production.key"
                },
                "monitoring": {
                    "enabled": True,
                    "prometheus": True,
                    "grafana": True
                }
            }
        else:
            raise ValueError(f"未知环境: {environment}")
    
    def run_command(self, cmd: List[str], description: str = "", cwd: Path = None) -> bool:
        """运行命令"""
        logger.info(f"执行: {description or ' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"✅ 成功: {description}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 失败: {description}")
            logger.error(f"错误输出: {e.stderr}")
            return False
    
    def check_prerequisites(self, config: Dict) -> bool:
        """检查部署前提条件"""
        logger.info("检查部署前提条件...")
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version < (3, 9):
            logger.error("需要Python 3.9或更高版本")
            return False
        
        # 检查必需的命令
        required_commands = ["pip", "python"]
        if config.get("docker", {}).get("enabled"):
            required_commands.extend(["docker", "docker-compose"])
        
        for cmd in required_commands:
            if not shutil.which(cmd):
                logger.error(f"缺少必需命令: {cmd}")
                return False
        
        # 检查数据库连接
        if not self.check_database_connection(config["database"]):
            logger.error("数据库连接失败")
            return False
        
        # 检查Redis连接
        if not self.check_redis_connection(config["redis"]):
            logger.error("Redis连接失败")
            return False
        
        logger.info("✅ 前提条件检查通过")
        return True
    
    def check_database_connection(self, db_config: Dict) -> bool:
        """检查数据库连接"""
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=db_config["host"],
                port=db_config["port"],
                database=db_config["name"],
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "")
            )
            conn.close()
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def check_redis_connection(self, redis_config: Dict) -> bool:
        """检查Redis连接"""
        try:
            import redis
            r = redis.Redis(
                host=redis_config["host"],
                port=redis_config["port"],
                password=os.getenv("REDIS_PASSWORD", "")
            )
            r.ping()
            return True
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """安装依赖"""
        logger.info("安装Python依赖...")
        
        # 安装生产依赖
        if not self.run_command(
            ["pip", "install", "-r", "requirements.txt"],
            "安装生产依赖"
        ):
            return False
        
        return True
    
    def run_database_migrations(self) -> bool:
        """运行数据库迁移"""
        logger.info("运行数据库迁移...")
        
        # 初始化数据库
        if not self.run_command(
            ["python", "scripts/init_db.py", "init"],
            "初始化数据库"
        ):
            return False
        
        return True
    
    def build_docker_image(self, config: Dict) -> bool:
        """构建Docker镜像"""
        if not config.get("docker", {}).get("enabled"):
            return True
        
        logger.info("构建Docker镜像...")
        
        image_name = config["docker"]["image"]
        
        if not self.run_command(
            ["docker", "build", "-t", image_name, "."],
            f"构建Docker镜像: {image_name}"
        ):
            return False
        
        return True
    
    def deploy_with_docker(self, config: Dict) -> bool:
        """使用Docker部署"""
        logger.info("使用Docker部署...")
        
        # 停止现有容器
        self.run_command(
            ["docker", "stop", "translation-backend"],
            "停止现有容器"
        )
        
        self.run_command(
            ["docker", "rm", "translation-backend"],
            "删除现有容器"
        )
        
        # 启动新容器
        docker_cmd = [
            "docker", "run", "-d",
            "--name", "translation-backend",
            "-p", f"{config['port']}:8000",
            "--env-file", ".env"
        ]
        
        # 添加数据库和Redis连接
        docker_cmd.extend([
            "-e", f"DB_HOST={config['database']['host']}",
            "-e", f"DB_PORT={config['database']['port']}",
            "-e", f"REDIS_HOST={config['redis']['host']}",
            "-e", f"REDIS_PORT={config['redis']['port']}"
        ])
        
        docker_cmd.append(config["docker"]["image"])
        
        if not self.run_command(docker_cmd, "启动Docker容器"):
            return False
        
        return True
    
    def deploy_with_systemd(self, config: Dict) -> bool:
        """使用systemd部署"""
        logger.info("使用systemd部署...")
        
        # 创建systemd服务文件
        service_content = f"""[Unit]
Description=Translation Backend Service
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory={self.project_root}
Environment=PATH={self.project_root}/venv/bin
ExecStart={self.project_root}/venv/bin/gunicorn app.main:app \\
    --workers {config['workers']} \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --bind {config['host']}:{config['port']} \\
    --timeout 30 \\
    --keepalive 2
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path("/etc/systemd/system/translation-backend.service")
        
        try:
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            # 重新加载systemd配置
            self.run_command(["sudo", "systemctl", "daemon-reload"], "重新加载systemd")
            
            # 启用并启动服务
            self.run_command(["sudo", "systemctl", "enable", "translation-backend"], "启用服务")
            self.run_command(["sudo", "systemctl", "start", "translation-backend"], "启动服务")
            
            return True
        except Exception as e:
            logger.error(f"创建systemd服务失败: {e}")
            return False
    
    def configure_nginx(self, config: Dict) -> bool:
        """配置Nginx"""
        if not config.get("nginx", {}).get("enabled"):
            return True
        
        logger.info("配置Nginx...")
        
        nginx_config = f"""server {{
    listen 80;
    server_name _;
    
    location / {{
        proxy_pass http://127.0.0.1:{config['port']};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /health {{
        proxy_pass http://127.0.0.1:{config['port']}/health;
        access_log off;
    }}
}}"""
        
        if config.get("ssl", {}).get("enabled"):
            nginx_config += f"""

server {{
    listen 443 ssl http2;
    server_name _;
    
    ssl_certificate {config['ssl']['cert_path']};
    ssl_certificate_key {config['ssl']['key_path']};
    
    location / {{
        proxy_pass http://127.0.0.1:{config['port']};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}"""
        
        nginx_file = Path("/etc/nginx/sites-available/translation-backend")
        
        try:
            with open(nginx_file, 'w') as f:
                f.write(nginx_config)
            
            # 创建符号链接
            sites_enabled = Path("/etc/nginx/sites-enabled/translation-backend")
            if sites_enabled.exists():
                sites_enabled.unlink()
            sites_enabled.symlink_to(nginx_file)
            
            # 测试配置并重新加载
            if self.run_command(["sudo", "nginx", "-t"], "测试Nginx配置"):
                self.run_command(["sudo", "systemctl", "reload", "nginx"], "重新加载Nginx")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"配置Nginx失败: {e}")
            return False
    
    def health_check(self, config: Dict) -> bool:
        """健康检查"""
        logger.info("执行健康检查...")
        
        base_url = f"http://localhost:{config['port']}"
        
        # 等待服务启动
        for i in range(30):  # 最多等待30秒
            try:
                response = requests.get(f"{base_url}/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ 健康检查通过")
                    return True
            except requests.RequestException:
                pass
            
            time.sleep(1)
        
        logger.error("❌ 健康检查失败")
        return False
    
    def rollback(self, config: Dict):
        """回滚部署"""
        logger.info("执行部署回滚...")
        
        if config.get("docker", {}).get("enabled"):
            # Docker回滚
            self.run_command(
                ["docker", "stop", "translation-backend"],
                "停止当前容器"
            )
            
            # 启动备份容器（如果存在）
            self.run_command(
                ["docker", "start", "translation-backend-backup"],
                "启动备份容器"
            )
        else:
            # systemd回滚
            self.run_command(
                ["sudo", "systemctl", "stop", "translation-backend"],
                "停止服务"
            )
            
            # 这里应该恢复之前的代码版本
            # 简化版本，重启服务
            self.run_command(
                ["sudo", "systemctl", "start", "translation-backend"],
                "重启服务"
            )
    
    def deploy(self, environment: str, skip_checks: bool = False) -> bool:
        """执行部署"""
        logger.info(f"开始部署到 {environment} 环境...")
        
        # 加载部署配置
        config = self.load_deployment_config(environment)
        
        try:
            # 检查前提条件
            if not skip_checks and not self.check_prerequisites(config):
                return False
            
            # 安装依赖
            if not self.install_dependencies():
                return False
            
            # 运行数据库迁移
            if not self.run_database_migrations():
                return False
            
            # 构建Docker镜像（如果需要）
            if not self.build_docker_image(config):
                return False
            
            # 部署应用
            if config.get("docker", {}).get("enabled"):
                if not self.deploy_with_docker(config):
                    return False
            else:
                if not self.deploy_with_systemd(config):
                    return False
            
            # 配置Nginx（如果需要）
            if not self.configure_nginx(config):
                return False
            
            # 健康检查
            if not self.health_check(config):
                logger.warning("健康检查失败，考虑回滚")
                return False
            
            logger.info(f"🎉 部署到 {environment} 环境成功!")
            return True
            
        except Exception as e:
            logger.error(f"部署失败: {e}")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="翻译系统部署工具")
    parser.add_argument(
        'environment',
        choices=['development', 'staging', 'production'],
        help='部署环境'
    )
    parser.add_argument(
        '--skip-checks',
        action='store_true',
        help='跳过前提条件检查'
    )
    parser.add_argument(
        '--rollback',
        action='store_true',
        help='回滚部署'
    )
    
    args = parser.parse_args()
    
    deployment_manager = DeploymentManager()
    
    if args.rollback:
        config = deployment_manager.load_deployment_config(args.environment)
        deployment_manager.rollback(config)
    else:
        success = deployment_manager.deploy(args.environment, args.skip_checks)
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
