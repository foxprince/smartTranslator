#!/usr/bin/env python3
"""
数据备份和恢复脚本
支持数据库备份、恢复和数据迁移
"""
import asyncio
import sys
import os
import json
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import subprocess
import logging

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import get_database_url
from app.core.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackupManager:
    """备份管理器"""
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.db_url = get_database_url()
    
    def create_database_backup(self, backup_name: Optional[str] = None) -> Path:
        """创建数据库备份"""
        try:
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"db_backup_{timestamp}"
            
            backup_file = self.backup_dir / f"{backup_name}.sql"
            
            logger.info(f"创建数据库备份: {backup_file}")
            
            # 解析数据库URL
            from urllib.parse import urlparse
            parsed = urlparse(self.db_url)
            
            # 构建pg_dump命令
            cmd = [
                "pg_dump",
                "-h", parsed.hostname or "localhost",
                "-p", str(parsed.port or 5432),
                "-U", parsed.username,
                "-d", parsed.path.lstrip('/'),
                "-f", str(backup_file),
                "--verbose",
                "--no-password"
            ]
            
            # 设置密码环境变量
            env = os.environ.copy()
            if parsed.password:
                env["PGPASSWORD"] = parsed.password
            
            # 执行备份
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ 数据库备份成功: {backup_file}")
                
                # 压缩备份文件
                compressed_file = self.compress_backup(backup_file)
                backup_file.unlink()  # 删除原始文件
                
                return compressed_file
            else:
                logger.error(f"数据库备份失败: {result.stderr}")
                raise Exception(f"pg_dump failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"创建数据库备份失败: {e}")
            raise
    
    def compress_backup(self, backup_file: Path) -> Path:
        """压缩备份文件"""
        compressed_file = backup_file.with_suffix('.sql.gz')
        
        logger.info(f"压缩备份文件: {compressed_file}")
        
        with open(backup_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        logger.info(f"✅ 备份文件压缩完成: {compressed_file}")
        return compressed_file
    
    def restore_database_backup(self, backup_file: Path, target_db: Optional[str] = None):
        """恢复数据库备份"""
        try:
            logger.info(f"恢复数据库备份: {backup_file}")
            
            # 如果是压缩文件，先解压
            if backup_file.suffix == '.gz':
                sql_file = backup_file.with_suffix('')
                with gzip.open(backup_file, 'rb') as f_in:
                    with open(sql_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_file = sql_file
            
            # 解析数据库URL
            from urllib.parse import urlparse
            parsed = urlparse(self.db_url)
            
            db_name = target_db or parsed.path.lstrip('/')
            
            # 构建psql命令
            cmd = [
                "psql",
                "-h", parsed.hostname or "localhost",
                "-p", str(parsed.port or 5432),
                "-U", parsed.username,
                "-d", db_name,
                "-f", str(backup_file),
                "--quiet"
            ]
            
            # 设置密码环境变量
            env = os.environ.copy()
            if parsed.password:
                env["PGPASSWORD"] = parsed.password
            
            # 执行恢复
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ 数据库恢复成功")
            else:
                logger.error(f"数据库恢复失败: {result.stderr}")
                raise Exception(f"psql failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"恢复数据库备份失败: {e}")
            raise
    
    async def export_translation_data(self, output_file: Path):
        """导出翻译数据"""
        try:
            logger.info(f"导出翻译数据到: {output_file}")
            
            engine = create_async_engine(self.db_url)
            async_session = sessionmaker(engine, class_=AsyncSession)
            
            export_data = {
                "export_time": datetime.now().isoformat(),
                "version": "1.0",
                "data": {}
            }
            
            async with async_session() as session:
                # 导出翻译缓存
                result = await session.execute(
                    text("SELECT * FROM translation_cache ORDER BY created_at")
                )
                cache_data = [dict(row._mapping) for row in result]
                export_data["data"]["translation_cache"] = cache_data
                logger.info(f"导出翻译缓存: {len(cache_data)} 条记录")
                
                # 导出翻译任务
                result = await session.execute(
                    text("SELECT * FROM translation_jobs ORDER BY created_at")
                )
                jobs_data = [dict(row._mapping) for row in result]
                export_data["data"]["translation_jobs"] = jobs_data
                logger.info(f"导出翻译任务: {len(jobs_data)} 条记录")
                
                # 导出成本跟踪
                result = await session.execute(
                    text("SELECT * FROM cost_tracking ORDER BY date")
                )
                cost_data = [dict(row._mapping) for row in result]
                export_data["data"]["cost_tracking"] = cost_data
                logger.info(f"导出成本跟踪: {len(cost_data)} 条记录")
                
                # 导出质量评估
                result = await session.execute(
                    text("SELECT * FROM quality_assessments ORDER BY created_at")
                )
                quality_data = [dict(row._mapping) for row in result]
                export_data["data"]["quality_assessments"] = quality_data
                logger.info(f"导出质量评估: {len(quality_data)} 条记录")
            
            await engine.dispose()
            
            # 保存到JSON文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"✅ 翻译数据导出完成: {output_file}")
            
        except Exception as e:
            logger.error(f"导出翻译数据失败: {e}")
            raise
    
    async def import_translation_data(self, input_file: Path):
        """导入翻译数据"""
        try:
            logger.info(f"从文件导入翻译数据: {input_file}")
            
            with open(input_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            logger.info(f"数据版本: {import_data.get('version', 'unknown')}")
            logger.info(f"导出时间: {import_data.get('export_time', 'unknown')}")
            
            engine = create_async_engine(self.db_url)
            async_session = sessionmaker(engine, class_=AsyncSession)
            
            async with async_session() as session:
                data = import_data["data"]
                
                # 导入翻译缓存
                if "translation_cache" in data:
                    cache_data = data["translation_cache"]
                    for item in cache_data:
                        await session.execute(
                            text("""
                                INSERT INTO translation_cache 
                                (cache_key, original_text, translated_text, source_language, 
                                 target_language, provider, quality_score, created_at, expires_at)
                                VALUES (:cache_key, :original_text, :translated_text, :source_language,
                                        :target_language, :provider, :quality_score, :created_at, :expires_at)
                                ON CONFLICT (cache_key) DO NOTHING
                            """),
                            item
                        )
                    logger.info(f"导入翻译缓存: {len(cache_data)} 条记录")
                
                # 导入翻译任务
                if "translation_jobs" in data:
                    jobs_data = data["translation_jobs"]
                    for item in jobs_data:
                        await session.execute(
                            text("""
                                INSERT INTO translation_jobs 
                                (id, project_id, user_id, status, progress, request_data, 
                                 result_data, created_at, updated_at, completed_at)
                                VALUES (:id, :project_id, :user_id, :status, :progress, :request_data,
                                        :result_data, :created_at, :updated_at, :completed_at)
                                ON CONFLICT (id) DO NOTHING
                            """),
                            item
                        )
                    logger.info(f"导入翻译任务: {len(jobs_data)} 条记录")
                
                # 导入成本跟踪
                if "cost_tracking" in data:
                    cost_data = data["cost_tracking"]
                    for item in cost_data:
                        await session.execute(
                            text("""
                                INSERT INTO cost_tracking 
                                (date, provider, user_id, operation_type, character_count, 
                                 token_count, cost, created_at)
                                VALUES (:date, :provider, :user_id, :operation_type, :character_count,
                                        :token_count, :cost, :created_at)
                                ON CONFLICT (date, provider, user_id, operation_type) DO NOTHING
                            """),
                            item
                        )
                    logger.info(f"导入成本跟踪: {len(cost_data)} 条记录")
                
                # 导入质量评估
                if "quality_assessments" in data:
                    quality_data = data["quality_assessments"]
                    for item in quality_data:
                        await session.execute(
                            text("""
                                INSERT INTO quality_assessments 
                                (original_text, translated_text, source_language, target_language,
                                 provider, overall_score, length_score, consistency_score,
                                 language_score, structure_score, issues, created_at)
                                VALUES (:original_text, :translated_text, :source_language, :target_language,
                                        :provider, :overall_score, :length_score, :consistency_score,
                                        :language_score, :structure_score, :issues, :created_at)
                            """),
                            item
                        )
                    logger.info(f"导入质量评估: {len(quality_data)} 条记录")
                
                await session.commit()
            
            await engine.dispose()
            logger.info(f"✅ 翻译数据导入完成")
            
        except Exception as e:
            logger.error(f"导入翻译数据失败: {e}")
            raise
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有备份文件"""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.sql.gz"):
            stat = backup_file.stat()
            backups.append({
                "name": backup_file.name,
                "path": str(backup_file),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        # 按创建时间排序
        backups.sort(key=lambda x: x["created"], reverse=True)
        return backups
    
    def cleanup_old_backups(self, keep_days: int = 30):
        """清理旧的备份文件"""
        try:
            cutoff_time = datetime.now() - timedelta(days=keep_days)
            cleaned_count = 0
            
            for backup_file in self.backup_dir.glob("*.sql.gz"):
                if datetime.fromtimestamp(backup_file.stat().st_ctime) < cutoff_time:
                    backup_file.unlink()
                    cleaned_count += 1
                    logger.info(f"删除旧备份: {backup_file.name}")
            
            logger.info(f"✅ 清理完成，删除了 {cleaned_count} 个旧备份文件")
            
        except Exception as e:
            logger.error(f"清理旧备份失败: {e}")
            raise
    
    async def create_full_backup(self, backup_name: Optional[str] = None) -> Dict[str, Path]:
        """创建完整备份（数据库 + 翻译数据）"""
        try:
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"full_backup_{timestamp}"
            
            logger.info(f"创建完整备份: {backup_name}")
            
            # 创建数据库备份
            db_backup = self.create_database_backup(f"{backup_name}_db")
            
            # 导出翻译数据
            data_backup = self.backup_dir / f"{backup_name}_data.json"
            await self.export_translation_data(data_backup)
            
            logger.info(f"✅ 完整备份创建完成")
            
            return {
                "database": db_backup,
                "data": data_backup
            }
            
        except Exception as e:
            logger.error(f"创建完整备份失败: {e}")
            raise


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="数据备份和恢复工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 备份命令
    backup_parser = subparsers.add_parser('backup', help='创建备份')
    backup_parser.add_argument('--name', help='备份名称')
    backup_parser.add_argument('--full', action='store_true', help='创建完整备份')
    
    # 恢复命令
    restore_parser = subparsers.add_parser('restore', help='恢复备份')
    restore_parser.add_argument('backup_file', help='备份文件路径')
    restore_parser.add_argument('--target-db', help='目标数据库名称')
    
    # 导出命令
    export_parser = subparsers.add_parser('export', help='导出翻译数据')
    export_parser.add_argument('output_file', help='输出文件路径')
    
    # 导入命令
    import_parser = subparsers.add_parser('import', help='导入翻译数据')
    import_parser.add_argument('input_file', help='输入文件路径')
    
    # 列表命令
    list_parser = subparsers.add_parser('list', help='列出备份文件')
    
    # 清理命令
    cleanup_parser = subparsers.add_parser('cleanup', help='清理旧备份')
    cleanup_parser.add_argument('--days', type=int, default=30, help='保留天数')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    backup_manager = BackupManager()
    
    try:
        if args.command == 'backup':
            if args.full:
                result = await backup_manager.create_full_backup(args.name)
                print(f"完整备份创建完成:")
                print(f"  数据库: {result['database']}")
                print(f"  数据: {result['data']}")
            else:
                backup_file = backup_manager.create_database_backup(args.name)
                print(f"数据库备份创建完成: {backup_file}")
        
        elif args.command == 'restore':
            backup_file = Path(args.backup_file)
            if not backup_file.exists():
                print(f"备份文件不存在: {backup_file}")
                sys.exit(1)
            
            backup_manager.restore_database_backup(backup_file, args.target_db)
            print("数据库恢复完成")
        
        elif args.command == 'export':
            output_file = Path(args.output_file)
            await backup_manager.export_translation_data(output_file)
            print(f"翻译数据导出完成: {output_file}")
        
        elif args.command == 'import':
            input_file = Path(args.input_file)
            if not input_file.exists():
                print(f"输入文件不存在: {input_file}")
                sys.exit(1)
            
            await backup_manager.import_translation_data(input_file)
            print("翻译数据导入完成")
        
        elif args.command == 'list':
            backups = backup_manager.list_backups()
            if backups:
                print("备份文件列表:")
                print("-" * 80)
                for backup in backups:
                    size_mb = backup['size'] / (1024 * 1024)
                    print(f"{backup['name']:<40} {size_mb:>8.1f}MB {backup['created']}")
            else:
                print("没有找到备份文件")
        
        elif args.command == 'cleanup':
            backup_manager.cleanup_old_backups(args.days)
            print(f"清理完成，保留最近 {args.days} 天的备份")
    
    except Exception as e:
        logger.error(f"操作失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
