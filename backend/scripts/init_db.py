#!/usr/bin/env python3
"""
数据库初始化脚本
创建数据库表、索引和初始数据
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_database_url
from app.core.config import settings
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_database_if_not_exists():
    """创建数据库（如果不存在）"""
    try:
        # 连接到默认数据库
        default_url = get_database_url().replace('/translation_db', '/postgres')
        engine = create_async_engine(default_url)
        
        async with engine.begin() as conn:
            # 检查数据库是否存在
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = 'translation_db'")
            )
            
            if not result.fetchone():
                logger.info("创建数据库 translation_db...")
                await conn.execute(text("CREATE DATABASE translation_db"))
                logger.info("✅ 数据库创建成功")
            else:
                logger.info("数据库已存在")
        
        await engine.dispose()
        
    except Exception as e:
        logger.error(f"创建数据库失败: {e}")
        raise


async def create_tables():
    """创建数据库表"""
    try:
        engine = create_async_engine(get_database_url())
        
        async with engine.begin() as conn:
            logger.info("创建数据库表...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ 数据库表创建成功")
        
        await engine.dispose()
        
    except Exception as e:
        logger.error(f"创建表失败: {e}")
        raise


async def create_indexes():
    """创建数据库索引"""
    try:
        engine = create_async_engine(get_database_url())
        
        indexes = [
            # 翻译缓存索引
            """
            CREATE INDEX IF NOT EXISTS idx_translation_cache_key 
            ON translation_cache(cache_key);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_translation_cache_created 
            ON translation_cache(created_at);
            """,
            
            # 翻译任务索引
            """
            CREATE INDEX IF NOT EXISTS idx_translation_jobs_user 
            ON translation_jobs(user_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_translation_jobs_project 
            ON translation_jobs(project_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_translation_jobs_status 
            ON translation_jobs(status);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_translation_jobs_created 
            ON translation_jobs(created_at);
            """,
            
            # 成本跟踪索引
            """
            CREATE INDEX IF NOT EXISTS idx_cost_tracking_date 
            ON cost_tracking(date);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_cost_tracking_provider 
            ON cost_tracking(provider);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_cost_tracking_user 
            ON cost_tracking(user_id);
            """,
            
            # 质量评估索引
            """
            CREATE INDEX IF NOT EXISTS idx_quality_assessments_score 
            ON quality_assessments(overall_score);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_quality_assessments_created 
            ON quality_assessments(created_at);
            """
        ]
        
        async with engine.begin() as conn:
            logger.info("创建数据库索引...")
            for index_sql in indexes:
                await conn.execute(text(index_sql))
            logger.info("✅ 数据库索引创建成功")
        
        await engine.dispose()
        
    except Exception as e:
        logger.error(f"创建索引失败: {e}")
        raise


async def insert_initial_data():
    """插入初始数据"""
    try:
        engine = create_async_engine(get_database_url())
        async_session = sessionmaker(engine, class_=AsyncSession)
        
        async with async_session() as session:
            logger.info("插入初始数据...")
            
            # 插入系统配置
            config_data = [
                {
                    'key': 'translation.default_provider',
                    'value': 'google',
                    'description': '默认翻译提供商'
                },
                {
                    'key': 'translation.cache_ttl',
                    'value': '3600',
                    'description': '翻译缓存TTL（秒）'
                },
                {
                    'key': 'translation.max_batch_size',
                    'value': '100',
                    'description': '最大批量翻译数量'
                },
                {
                    'key': 'cost.daily_budget',
                    'value': '100.0',
                    'description': '每日成本预算（美元）'
                },
                {
                    'key': 'cost.monthly_budget',
                    'value': '3000.0',
                    'description': '每月成本预算（美元）'
                }
            ]
            
            for config in config_data:
                # 检查配置是否已存在
                result = await session.execute(
                    text("SELECT 1 FROM system_config WHERE key = :key"),
                    {"key": config['key']}
                )
                
                if not result.fetchone():
                    await session.execute(
                        text("""
                            INSERT INTO system_config (key, value, description, created_at, updated_at)
                            VALUES (:key, :value, :description, NOW(), NOW())
                        """),
                        config
                    )
            
            await session.commit()
            logger.info("✅ 初始数据插入成功")
        
        await engine.dispose()
        
    except Exception as e:
        logger.error(f"插入初始数据失败: {e}")
        raise


async def setup_database():
    """完整的数据库设置"""
    logger.info("🚀 开始数据库初始化...")
    
    try:
        # 1. 创建数据库
        await create_database_if_not_exists()
        
        # 2. 创建表
        await create_tables()
        
        # 3. 创建索引
        await create_indexes()
        
        # 4. 插入初始数据
        await insert_initial_data()
        
        logger.info("🎉 数据库初始化完成!")
        
    except Exception as e:
        logger.error(f"💥 数据库初始化失败: {e}")
        sys.exit(1)


async def reset_database():
    """重置数据库（危险操作）"""
    logger.warning("⚠️  准备重置数据库...")
    
    confirm = input("这将删除所有数据！请输入 'RESET' 确认: ")
    if confirm != 'RESET':
        logger.info("操作已取消")
        return
    
    try:
        engine = create_async_engine(get_database_url())
        
        async with engine.begin() as conn:
            logger.info("删除所有表...")
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("✅ 表删除成功")
        
        await engine.dispose()
        
        # 重新创建
        await setup_database()
        
    except Exception as e:
        logger.error(f"重置数据库失败: {e}")
        raise


async def check_database_health():
    """检查数据库健康状态"""
    try:
        engine = create_async_engine(get_database_url())
        
        async with engine.begin() as conn:
            # 检查连接
            await conn.execute(text("SELECT 1"))
            logger.info("✅ 数据库连接正常")
            
            # 检查表是否存在
            tables = [
                'translation_cache',
                'translation_jobs', 
                'cost_tracking',
                'quality_assessments',
                'system_config'
            ]
            
            for table in tables:
                result = await conn.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                )
                count = result.scalar()
                logger.info(f"✅ 表 {table}: {count} 条记录")
        
        await engine.dispose()
        logger.info("🎉 数据库健康检查完成")
        
    except Exception as e:
        logger.error(f"💥 数据库健康检查失败: {e}")
        raise


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库管理工具")
    parser.add_argument(
        'action',
        choices=['init', 'reset', 'health'],
        help='操作类型'
    )
    
    args = parser.parse_args()
    
    if args.action == 'init':
        asyncio.run(setup_database())
    elif args.action == 'reset':
        asyncio.run(reset_database())
    elif args.action == 'health':
        asyncio.run(check_database_health())


if __name__ == "__main__":
    main()
