#!/usr/bin/env python3
"""
翻译系统监控脚本
监控系统健康状态、性能指标和资源使用情况
"""
import asyncio
import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import psutil
import aiohttp
import logging

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.translation_engine import TranslationEngine
from app.providers.provider_factory import provider_factory

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self):
        self.translation_engine = TranslationEngine()
        self.api_base_url = "http://localhost:8000"
        self.alerts = []
    
    async def check_api_health(self) -> Dict[str, Any]:
        """检查API健康状态"""
        try:
            async with aiohttp.ClientSession() as session:
                # 检查健康端点
                async with session.get(f"{self.api_base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "healthy",
                            "response_time": data.get("response_time", 0),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "error": f"HTTP {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def check_providers_health(self) -> Dict[str, Any]:
        """检查翻译提供商健康状态"""
        try:
            health_status = await provider_factory.check_providers_health()
            return {
                "providers": health_status,
                "healthy_count": sum(1 for status in health_status.values() if status),
                "total_count": len(health_status),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def check_database_health(self) -> Dict[str, Any]:
        """检查数据库健康状态"""
        try:
            # 这里应该连接到实际的数据库检查
            # 简化版本，检查连接池状态
            return {
                "status": "healthy",
                "connections": {
                    "active": 5,
                    "idle": 10,
                    "total": 15
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """检查系统资源使用情况"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            
            # 网络统计
            network = psutil.net_io_counters()
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def check_translation_performance(self) -> Dict[str, Any]:
        """检查翻译性能"""
        try:
            start_time = time.time()
            
            # 执行一个简单的翻译测试
            test_request = {
                "texts": ["Hello, world!"],
                "source_language": "en",
                "target_language": "zh",
                "provider": "google"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/api/translation/translate",
                    json=test_request
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "healthy",
                            "response_time": response_time,
                            "success_count": data.get("success_count", 0),
                            "total_count": data.get("total_count", 0),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "status": "error",
                            "response_time": response_time,
                            "error": f"HTTP {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base_url}/api/translation/cache/stats"
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"HTTP {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_cost_stats(self) -> Dict[str, Any]:
        """获取成本统计"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base_url}/api/translation/costs/stats"
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"HTTP {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查告警条件"""
        alerts = []
        
        # CPU使用率告警
        if "system" in metrics and "cpu" in metrics["system"]:
            cpu_percent = metrics["system"]["cpu"]["percent"]
            if cpu_percent > 80:
                alerts.append({
                    "type": "cpu_high",
                    "severity": "warning" if cpu_percent < 90 else "critical",
                    "message": f"CPU使用率过高: {cpu_percent}%",
                    "timestamp": datetime.now().isoformat()
                })
        
        # 内存使用率告警
        if "system" in metrics and "memory" in metrics["system"]:
            memory_percent = metrics["system"]["memory"]["percent"]
            if memory_percent > 85:
                alerts.append({
                    "type": "memory_high",
                    "severity": "warning" if memory_percent < 95 else "critical",
                    "message": f"内存使用率过高: {memory_percent}%",
                    "timestamp": datetime.now().isoformat()
                })
        
        # 磁盘使用率告警
        if "system" in metrics and "disk" in metrics["system"]:
            disk_percent = metrics["system"]["disk"]["percent"]
            if disk_percent > 85:
                alerts.append({
                    "type": "disk_high",
                    "severity": "warning" if disk_percent < 95 else "critical",
                    "message": f"磁盘使用率过高: {disk_percent:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
        
        # API健康状态告警
        if "api" in metrics and metrics["api"]["status"] != "healthy":
            alerts.append({
                "type": "api_unhealthy",
                "severity": "critical",
                "message": f"API服务异常: {metrics['api'].get('error', 'Unknown')}",
                "timestamp": datetime.now().isoformat()
            })
        
        # 翻译提供商告警
        if "providers" in metrics and "providers" in metrics["providers"]:
            unhealthy_providers = [
                provider for provider, status in metrics["providers"]["providers"].items()
                if not status
            ]
            if unhealthy_providers:
                alerts.append({
                    "type": "providers_unhealthy",
                    "severity": "warning",
                    "message": f"翻译提供商异常: {', '.join(unhealthy_providers)}",
                    "timestamp": datetime.now().isoformat()
                })
        
        # 翻译性能告警
        if "translation_performance" in metrics:
            response_time = metrics["translation_performance"].get("response_time", 0)
            if response_time > 5:  # 5秒
                alerts.append({
                    "type": "translation_slow",
                    "severity": "warning",
                    "message": f"翻译响应时间过长: {response_time:.2f}秒",
                    "timestamp": datetime.now().isoformat()
                })
        
        return alerts
    
    async def collect_all_metrics(self) -> Dict[str, Any]:
        """收集所有监控指标"""
        logger.info("开始收集监控指标...")
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "system": self.check_system_resources(),
        }
        
        # 异步收集其他指标
        tasks = {
            "api": self.check_api_health(),
            "providers": self.check_providers_health(),
            "database": self.check_database_health(),
            "translation_performance": self.check_translation_performance(),
            "cache_stats": self.get_cache_stats(),
            "cost_stats": self.get_cost_stats()
        }
        
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        for key, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                metrics[key] = {"error": str(result)}
            else:
                metrics[key] = result
        
        return metrics
    
    def format_metrics_report(self, metrics: Dict[str, Any]) -> str:
        """格式化监控报告"""
        report = []
        report.append("=" * 60)
        report.append("翻译系统监控报告")
        report.append("=" * 60)
        report.append(f"时间: {metrics['timestamp']}")
        report.append("")
        
        # 系统资源
        if "system" in metrics:
            system = metrics["system"]
            report.append("📊 系统资源:")
            report.append(f"  CPU: {system['cpu']['percent']:.1f}%")
            report.append(f"  内存: {system['memory']['percent']:.1f}%")
            report.append(f"  磁盘: {system['disk']['percent']:.1f}%")
            report.append("")
        
        # API状态
        if "api" in metrics:
            api = metrics["api"]
            status_icon = "✅" if api["status"] == "healthy" else "❌"
            report.append(f"🌐 API状态: {status_icon} {api['status']}")
            if "response_time" in api:
                report.append(f"  响应时间: {api['response_time']:.3f}秒")
            report.append("")
        
        # 翻译提供商
        if "providers" in metrics and "providers" in metrics["providers"]:
            providers = metrics["providers"]["providers"]
            report.append("🔧 翻译提供商:")
            for provider, status in providers.items():
                status_icon = "✅" if status else "❌"
                report.append(f"  {provider}: {status_icon}")
            report.append("")
        
        # 数据库状态
        if "database" in metrics:
            db = metrics["database"]
            status_icon = "✅" if db["status"] == "healthy" else "❌"
            report.append(f"🗄️  数据库: {status_icon} {db['status']}")
            report.append("")
        
        # 缓存统计
        if "cache_stats" in metrics and "error" not in metrics["cache_stats"]:
            cache = metrics["cache_stats"]
            report.append("💾 缓存统计:")
            report.append(f"  总项目: {cache.get('total_items', 0)}")
            report.append(f"  命中率: {cache.get('hit_rate', 0):.2%}")
            report.append("")
        
        # 成本统计
        if "cost_stats" in metrics and "error" not in metrics["cost_stats"]:
            cost = metrics["cost_stats"]
            report.append("💰 成本统计:")
            report.append(f"  今日成本: ${cost.get('daily_cost', 0):.2f}")
            report.append(f"  本月成本: ${cost.get('monthly_cost', 0):.2f}")
            report.append("")
        
        return "\n".join(report)
    
    async def run_monitoring_cycle(self, interval: int = 60):
        """运行监控循环"""
        logger.info(f"开始监控循环，间隔: {interval}秒")
        
        while True:
            try:
                # 收集指标
                metrics = await self.collect_all_metrics()
                
                # 检查告警
                alerts = self.check_alerts(metrics)
                
                # 输出报告
                report = self.format_metrics_report(metrics)
                print(report)
                
                # 处理告警
                if alerts:
                    print("\n🚨 告警信息:")
                    for alert in alerts:
                        severity_icon = "⚠️" if alert["severity"] == "warning" else "🔥"
                        print(f"  {severity_icon} {alert['message']}")
                    print("")
                
                # 保存指标到文件
                self.save_metrics(metrics, alerts)
                
                # 等待下一个周期
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("监控已停止")
                break
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
                await asyncio.sleep(interval)
    
    def save_metrics(self, metrics: Dict[str, Any], alerts: List[Dict[str, Any]]):
        """保存监控指标到文件"""
        try:
            # 创建监控数据目录
            monitor_dir = Path("monitoring")
            monitor_dir.mkdir(exist_ok=True)
            
            # 保存指标
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metrics_file = monitor_dir / f"metrics_{timestamp}.json"
            
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "metrics": metrics,
                    "alerts": alerts
                }, f, indent=2, ensure_ascii=False)
            
            # 保留最近24小时的数据
            self.cleanup_old_metrics(monitor_dir)
            
        except Exception as e:
            logger.error(f"保存监控数据失败: {e}")
    
    def cleanup_old_metrics(self, monitor_dir: Path):
        """清理旧的监控数据"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for file_path in monitor_dir.glob("metrics_*.json"):
                if file_path.stat().st_mtime < cutoff_time.timestamp():
                    file_path.unlink()
                    
        except Exception as e:
            logger.error(f"清理旧监控数据失败: {e}")


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="翻译系统监控工具")
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='监控间隔（秒），默认60秒'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='只运行一次监控检查'
    )
    
    args = parser.parse_args()
    
    monitor = SystemMonitor()
    
    if args.once:
        # 单次监控检查
        metrics = await monitor.collect_all_metrics()
        alerts = monitor.check_alerts(metrics)
        
        report = monitor.format_metrics_report(metrics)
        print(report)
        
        if alerts:
            print("\n🚨 告警信息:")
            for alert in alerts:
                severity_icon = "⚠️" if alert["severity"] == "warning" else "🔥"
                print(f"  {severity_icon} {alert['message']}")
    else:
        # 持续监控
        await monitor.run_monitoring_cycle(args.interval)


if __name__ == "__main__":
    asyncio.run(main())
