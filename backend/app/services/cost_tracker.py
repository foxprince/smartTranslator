"""
翻译成本跟踪服务
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from ..schemas.translation import TranslationProvider, UsageRecord, CostInfo


class CostTracker:
    """翻译成本跟踪器"""
    
    def __init__(self):
        # 内存存储使用记录（生产环境应使用数据库）
        self.usage_records: List[UsageRecord] = []
        
        # 提供商定价配置
        self.pricing_config = {
            TranslationProvider.GOOGLE: {
                'price_per_char': 0.00002,  # $20 per 1M characters
                'free_tier_chars': 500000,  # 500K characters per month
                'currency': 'USD'
            },
            TranslationProvider.OPENAI: {
                'price_per_1k_tokens': 0.002,  # $2 per 1K tokens for gpt-3.5-turbo
                'avg_chars_per_token': 4,
                'currency': 'USD'
            }
        }
        
        # 预算配置
        self.budget_limits = {
            'daily': 10.0,    # $10 per day
            'monthly': 200.0,  # $200 per month
            'yearly': 2000.0   # $2000 per year
        }
    
    async def track_translation_usage(
        self,
        provider: TranslationProvider,
        request_count: int,
        character_count: int,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> float:
        """
        跟踪翻译使用量并计算成本
        
        Args:
            provider: 翻译提供商
            request_count: 请求数量
            character_count: 字符数量
            user_id: 用户ID
            project_id: 项目ID
            
        Returns:
            float: 估算成本
        """
        # 计算成本
        estimated_cost = self._calculate_cost(provider, character_count)
        
        # 创建使用记录
        usage_record = UsageRecord(
            id=f"{provider.value}_{datetime.now().timestamp()}",
            provider=provider,
            user_id=user_id or "anonymous",
            project_id=project_id,
            request_count=request_count,
            character_count=character_count,
            estimated_cost=estimated_cost,
            timestamp=datetime.now()
        )
        
        # 如果是OpenAI，计算token数量
        if provider == TranslationProvider.OPENAI:
            token_count = character_count // self.pricing_config[provider]['avg_chars_per_token']
            usage_record.token_count = token_count
        
        # 存储记录
        self.usage_records.append(usage_record)
        
        # 清理旧记录（保留最近30天）
        await self._cleanup_old_records()
        
        return estimated_cost
    
    def _calculate_cost(self, provider: TranslationProvider, character_count: int) -> float:
        """计算翻译成本"""
        config = self.pricing_config.get(provider)
        if not config:
            return 0.0
        
        if provider == TranslationProvider.GOOGLE:
            # Google Translate按字符计费
            # 考虑免费额度
            monthly_usage = self._get_monthly_character_usage(provider)
            remaining_free = max(0, config['free_tier_chars'] - monthly_usage)
            
            billable_chars = max(0, character_count - remaining_free)
            return billable_chars * config['price_per_char']
        
        elif provider == TranslationProvider.OPENAI:
            # OpenAI按token计费
            token_count = character_count // config['avg_chars_per_token']
            return (token_count / 1000) * config['price_per_1k_tokens']
        
        return 0.0
    
    def _get_monthly_character_usage(self, provider: TranslationProvider) -> int:
        """获取当月字符使用量"""
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_usage = 0
        for record in self.usage_records:
            if (record.provider == provider and 
                record.timestamp >= month_start):
                monthly_usage += record.character_count
        
        return monthly_usage
    
    async def get_cost_info(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> CostInfo:
        """
        获取成本信息
        
        Args:
            user_id: 用户ID过滤
            project_id: 项目ID过滤
            
        Returns:
            CostInfo: 成本信息
        """
        # 过滤记录
        filtered_records = self._filter_records(user_id, project_id)
        
        # 计算各时间段的成本
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        daily_cost = sum(
            record.estimated_cost for record in filtered_records
            if record.timestamp >= today_start
        )
        
        monthly_cost = sum(
            record.estimated_cost for record in filtered_records
            if record.timestamp >= month_start
        )
        
        # 计算剩余预算
        remaining_daily_budget = max(0, self.budget_limits['daily'] - daily_cost)
        remaining_monthly_budget = max(0, self.budget_limits['monthly'] - monthly_cost)
        
        # 计算免费额度剩余
        google_free_remaining = self._calculate_google_free_tier_remaining()
        
        # 按提供商分解成本
        cost_breakdown = {}
        for provider in TranslationProvider:
            provider_cost = sum(
                record.estimated_cost for record in filtered_records
                if record.provider == provider and record.timestamp >= month_start
            )
            if provider_cost > 0:
                cost_breakdown[provider.value] = provider_cost
        
        return CostInfo(
            current_cost=daily_cost,
            monthly_total=monthly_cost,
            daily_total=daily_cost,
            remaining_budget=min(remaining_daily_budget, remaining_monthly_budget),
            free_tier_remaining=google_free_remaining,
            cost_breakdown=cost_breakdown
        )
    
    def _filter_records(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> List[UsageRecord]:
        """过滤使用记录"""
        filtered = self.usage_records
        
        if user_id:
            filtered = [r for r in filtered if r.user_id == user_id]
        
        if project_id:
            filtered = [r for r in filtered if r.project_id == project_id]
        
        return filtered
    
    def _calculate_google_free_tier_remaining(self) -> int:
        """计算Google Translate免费额度剩余"""
        monthly_usage = self._get_monthly_character_usage(TranslationProvider.GOOGLE)
        free_tier_limit = self.pricing_config[TranslationProvider.GOOGLE]['free_tier_chars']
        
        return max(0, free_tier_limit - monthly_usage)
    
    async def _cleanup_old_records(self):
        """清理旧的使用记录"""
        cutoff_date = datetime.now() - timedelta(days=30)
        self.usage_records = [
            record for record in self.usage_records
            if record.timestamp > cutoff_date
        ]
    
    async def get_usage_stats(
        self,
        days: int = 30,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, any]:
        """
        获取使用统计
        
        Args:
            days: 统计天数
            user_id: 用户ID过滤
            project_id: 项目ID过滤
            
        Returns:
            Dict[str, any]: 使用统计
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_records = [
            record for record in self._filter_records(user_id, project_id)
            if record.timestamp > cutoff_date
        ]
        
        if not filtered_records:
            return {
                "period_days": days,
                "total_requests": 0,
                "total_characters": 0,
                "total_cost": 0.0,
                "provider_stats": {},
                "daily_usage": []
            }
        
        # 总体统计
        total_requests = sum(record.request_count for record in filtered_records)
        total_characters = sum(record.character_count for record in filtered_records)
        total_cost = sum(record.estimated_cost for record in filtered_records)
        
        # 按提供商统计
        provider_stats = {}
        for provider in TranslationProvider:
            provider_records = [r for r in filtered_records if r.provider == provider]
            if provider_records:
                provider_stats[provider.value] = {
                    "requests": sum(r.request_count for r in provider_records),
                    "characters": sum(r.character_count for r in provider_records),
                    "cost": sum(r.estimated_cost for r in provider_records)
                }
        
        # 每日使用量
        daily_usage = self._calculate_daily_usage(filtered_records, days)
        
        return {
            "period_days": days,
            "total_requests": total_requests,
            "total_characters": total_characters,
            "total_cost": round(total_cost, 4),
            "average_cost_per_request": round(total_cost / total_requests, 4) if total_requests > 0 else 0,
            "average_cost_per_1k_chars": round(total_cost / (total_characters / 1000), 4) if total_characters > 0 else 0,
            "provider_stats": provider_stats,
            "daily_usage": daily_usage
        }
    
    def _calculate_daily_usage(self, records: List[UsageRecord], days: int) -> List[Dict[str, any]]:
        """计算每日使用量"""
        daily_usage = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date_start + timedelta(days=1)
            
            day_records = [
                record for record in records
                if date_start <= record.timestamp < date_end
            ]
            
            daily_usage.append({
                "date": date_start.strftime("%Y-%m-%d"),
                "requests": sum(r.request_count for r in day_records),
                "characters": sum(r.character_count for r in day_records),
                "cost": round(sum(r.estimated_cost for r in day_records), 4)
            })
        
        return list(reversed(daily_usage))  # 按时间正序
    
    async def check_budget_limits(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, any]:
        """
        检查预算限制
        
        Args:
            user_id: 用户ID
            project_id: 项目ID
            
        Returns:
            Dict[str, any]: 预算状态
        """
        cost_info = await self.get_cost_info(user_id, project_id)
        
        # 检查各种预算限制
        daily_usage_percent = (cost_info.daily_total / self.budget_limits['daily']) * 100
        monthly_usage_percent = (cost_info.monthly_total / self.budget_limits['monthly']) * 100
        
        warnings = []
        if daily_usage_percent > 80:
            warnings.append(f"日预算使用已超过80% ({daily_usage_percent:.1f}%)")
        
        if monthly_usage_percent > 80:
            warnings.append(f"月预算使用已超过80% ({monthly_usage_percent:.1f}%)")
        
        if cost_info.free_tier_remaining < 50000:  # 少于50K字符
            warnings.append(f"Google免费额度剩余不足: {cost_info.free_tier_remaining:,} 字符")
        
        return {
            "daily_usage_percent": round(daily_usage_percent, 1),
            "monthly_usage_percent": round(monthly_usage_percent, 1),
            "free_tier_remaining": cost_info.free_tier_remaining,
            "warnings": warnings,
            "budget_exceeded": daily_usage_percent > 100 or monthly_usage_percent > 100
        }
    
    async def get_daily_stats(self) -> Dict[str, any]:
        """获取今日统计"""
        today_stats = await self.get_usage_stats(days=1)
        budget_status = await self.check_budget_limits()
        
        return {
            "today_usage": today_stats,
            "budget_status": budget_status,
            "active_providers": len(set(r.provider for r in self.usage_records)),
            "total_records": len(self.usage_records)
        }
    
    def set_budget_limits(self, daily: float, monthly: float, yearly: float):
        """设置预算限制"""
        self.budget_limits = {
            'daily': daily,
            'monthly': monthly,
            'yearly': yearly
        }
    
    def update_pricing_config(self, provider: TranslationProvider, config: Dict[str, any]):
        """更新提供商定价配置"""
        if provider in self.pricing_config:
            self.pricing_config[provider].update(config)
        else:
            self.pricing_config[provider] = config
