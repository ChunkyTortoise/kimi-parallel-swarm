"""
Performance Optimization Configuration
Tuning parameters for maximum speed and cost efficiency
"""

# ==========================================
# PARALLEL EXECUTION TUNING
# ==========================================

PARALLEL_CONFIG = {
    # Worker configuration
    "max_workers": 10,  # Default, auto-adjusts based on CPU count
    "min_workers": 4,
    "worker_scaling": "dynamic",  # static, dynamic, adaptive
    
    # Task chunking
    "chunk_size": 10,  # Prospects per chunk
    "chunk_timeout_seconds": 300,
    
    # Rate limiting (prevents API throttling)
    "rate_limits": {
        "linkedin_requests_per_minute": 30,
        "email_sends_per_minute": 60,
        "moonshot_api_calls_per_minute": 100,
        "phantombuster_requests_per_minute": 20,
        "airtable_requests_per_minute": 50
    },
    
    # Retry configuration
    "max_retries": 3,
    "retry_backoff_seconds": [5, 15, 45],  # Exponential backoff
    
    # Circuit breaker (fails fast on repeated failures)
    "circuit_breaker": {
        "failure_threshold": 5,
        "recovery_timeout_seconds": 300,
        "enabled": True
    }
}


# ==========================================
# COST OPTIMIZATION
# ==========================================

COST_OPTIMIZATION = {
    # API cost management
    "api_cost_limits": {
        "daily_usd_limit": 50.0,
        "monthly_usd_limit": 1000.0,
        "alert_threshold_percent": 80
    },
    
    # Caching strategy (reduces API calls)
    "caching": {
        "enabled": True,
        "ttl_seconds": {
            "linkedin_profile": 86400,  # 24 hours
            "company_data": 604800,     # 7 days
            "crm_records": 3600,        # 1 hour
            "generated_content": 86400  # 24 hours
        },
        "storage": "disk",  # memory, disk, redis
        "max_cache_size_mb": 500
    },
    
    # Batch processing (cheaper than individual calls)
    "batch_processing": {
        "enabled": True,
        "min_batch_size": 5,
        "max_batch_size": 50,
        "optimal_batch_size": 20
    },
    
    # Smart filtering (don't process low-quality leads)
    "quality_filtering": {
        "enabled": True,
        "min_quality_score": 7.0,
        "skip_threshold": 0.3,  # Skip if more than 30% would be filtered
    },
    
    # Time-of-day optimization (cheaper rates)
    "cost_aware_scheduling": {
        "enabled": True,
        "off_peak_multiplier": 0.7,  # 30% cheaper
        "off_peak_hours": [22, 23, 0, 1, 2, 3, 4, 5],  # UTC
        "defer_non_urgent": True
    }
}


# ==========================================
# PERFORMANCE MONITORING
# ==========================================

PERFORMANCE_MONITORING = {
    # Metrics to track
    "tracked_metrics": [
        "execution_time_ms",
        "api_calls_count",
        "api_cost_usd",
        "cache_hit_rate",
        "error_rate",
        "throughput_per_minute",
        "queue_depth",
        "worker_utilization"
    ],
    
    # Alerting thresholds
    "alert_thresholds": {
        "max_execution_time_seconds": 300,
        "max_error_rate_percent": 10,
        "min_cache_hit_rate": 50,
        "max_queue_depth": 100,
        "max_cost_per_task_usd": 0.50
    },
    
    # Reporting intervals
    "reporting": {
        "real_time_metrics_interval_seconds": 60,
        "hourly_summary": True,
        "daily_report": True,
        "weekly_analysis": True
    }
}


# ==========================================
# RESOURCE OPTIMIZATION
# ==========================================

RESOURCE_OPTIMIZATION = {
    # Memory management
    "memory": {
        "max_heap_size_mb": 2048,
        "gc_threshold": 0.8,
        "cleanup_interval_seconds": 300,
        "agent_pool_size": 8
    },
    
    # CPU utilization
    "cpu": {
        "target_utilization_percent": 75,
        "max_utilization_percent": 90,
        "throttle_on_overload": True
    },
    
    # Connection pooling
    "connection_pools": {
        "http_connections": 50,
        "db_connections": 20,
        "keep_alive_seconds": 30
    }
}


# ==========================================
# API-SPECIFIC OPTIMIZATIONS
# ==========================================

API_OPTIMIZATIONS = {
    "moonshot_api": {
        "model_selection": {
            "default": "kimi-k2.5",
            "fast_tasks": "kimi-k2.5",  # Use fastest model for simple tasks
            "complex_tasks": "kimi-k2.5"
        },
        "token_optimization": {
            "max_context_tokens": 8000,
            "compress_old_context": True,
            "prompt_caching": True
        },
        "batch_completion": True  # Batch multiple prompts
    },
    
    "sendgrid": {
        "batch_size": 100,  # Max per batch
        "personalization_batch_size": 1000,
        "use_templates": True  # Predefined templates cheaper than custom
    },
    
    "linkedin_phantombuster": {
        "session_reuse": True,
        "headless_optimization": True,
        "request_delay_ms": 2000,  # Minimum delay
        "batch_scraping": True
    }
}


# ==========================================
# OPTIMIZATION STRATEGIES
# ==========================================

def get_optimization_strategy(workload_type: str) -> Dict:
    """Get optimization config for specific workload."""
    
    strategies = {
        "morning_routine": {
            "priority": "high",
            "max_workers": 10,
            "quality_threshold": 7.0,
            "cache_aggressive": True,
            "deferrable": False
        },
        
        "batch_processing": {
            "priority": "medium",
            "max_workers": 8,
            "batch_size": 20,
            "quality_threshold": 6.0,
            "use_off_peak": True,
            "deferrable": True
        },
        
        "real_time_messaging": {
            "priority": "critical",
            "max_workers": 5,
            "cache_enabled": False,  # Real-time needs fresh data
            "batch_size": 1,
            "deferrable": False
        },
        
        "analytics_reporting": {
            "priority": "low",
            "max_workers": 3,
            "use_cached_data": True,
            "deferrable": True,
            "schedule_off_peak": True
        },
        
        "content_generation": {
            "priority": "medium",
            "max_workers": 4,
            "batch_prompts": True,
            "use_cheaper_model_for_drafts": True,
            "deferrable": True
        }
    }
    
    return strategies.get(workload_type, strategies["batch_processing"])


# ==========================================
# COST TRACKING
# ==========================================

class CostTracker:
    """Track and optimize API costs."""
    
    def __init__(self):
        self.daily_costs = {}
        self.monthly_costs = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def record_api_call(self, service: str, cost_usd: float, cached: bool = False):
        """Record an API call cost."""
        if cached:
            self.cache_hits += 1
            return
        
        self.cache_misses += 1
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today not in self.daily_costs:
            self.daily_costs[today] = {}
        
        if service not in self.daily_costs[today]:
            self.daily_costs[today][service] = 0.0
        
        self.daily_costs[today][service] += cost_usd
    
    def get_cache_hit_rate(self) -> float:
        """Get cache hit rate percentage."""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return (self.cache_hits / total) * 100
    
    def get_daily_cost(self, date: str = None) -> float:
        """Get total cost for a day."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        return sum(self.daily_costs.get(date, {}).values())
    
    def check_budget(self) -> Dict:
        """Check if within budget."""
        daily = self.get_daily_cost()
        monthly = sum(
            self.get_daily_cost(d) 
            for d in self.daily_costs.keys()
        )
        
        daily_limit = COST_OPTIMIZATION["api_cost_limits"]["daily_usd_limit"]
        monthly_limit = COST_OPTIMIZATION["api_cost_limits"]["monthly_usd_limit"]
        threshold = COST_OPTIMIZATION["api_cost_limits"]["alert_threshold_percent"]
        
        return {
            "daily_cost": daily,
            "daily_limit": daily_limit,
            "daily_percent": (daily / daily_limit) * 100,
            "monthly_cost": monthly,
            "monthly_limit": monthly_limit,
            "monthly_percent": (monthly / monthly_limit) * 100,
            "alert": daily >= (daily_limit * threshold / 100) or monthly >= (monthly_limit * threshold / 100),
            "cache_hit_rate": self.get_cache_hit_rate()
        }


# Initialize cost tracker
COST_TRACKER = CostTracker()
