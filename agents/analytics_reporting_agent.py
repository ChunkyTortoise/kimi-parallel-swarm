"""
Analytics & Reporting Agent
Aggregates metrics from all agents and generates insights
"""
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AgentMetrics:
    """Metrics for a single agent."""
    agent_name: str
    tasks_completed: int
    tasks_failed: int
    avg_execution_time_ms: float
    success_rate: float
    last_run: Optional[datetime] = None


@dataclass
class PipelineMetrics:
    """Sales pipeline metrics."""
    total_prospects: int
    new_leads: int
    qualified_leads: int
    opportunities: int
    closed_won: int
    closed_lost: int
    pipeline_value: float
    avg_deal_size: float
    conversion_rate: float


@dataclass
class CampaignMetrics:
    """Outreach campaign metrics."""
    messages_sent: int
    messages_delivered: int
    opened: int
    clicked: int
    replied: int
    meetings_booked: int
    unsubscribed: int
    open_rate: float
    click_rate: float
    reply_rate: float


class AnalyticsReportingAgent:
    """
    Agent for collecting, analyzing, and reporting on all system metrics.
    
    Features:
    - Real-time metrics aggregation
    - Trend analysis and forecasting
    - Automated report generation
    - Performance benchmarking
    - Anomaly detection
    """
    
    def __init__(self, data_dir: str = "data/metrics"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_history: List[Dict] = []
        self.current_metrics: Dict = {}
        
        self._load_historical_data()
    
    def _load_historical_data(self):
        """Load historical metrics from disk."""
        history_file = self.data_dir / "metrics_history.json"
        if history_file.exists():
            with open(history_file) as f:
                self.metrics_history = json.load(f)
    
    def _save_historical_data(self):
        """Save metrics history to disk."""
        history_file = self.data_dir / "metrics_history.json"
        with open(history_file, 'w') as f:
            json.dump(self.metrics_history, f, indent=2, default=str)
    
    def collect_agent_metrics(self, agent_results: Dict[str, any]) -> List[AgentMetrics]:
        """Collect metrics from all agent executions."""
        metrics = []
        
        for agent_name, results in agent_results.items():
            if isinstance(results, list):
                completed = len([r for r in results if r.get('success', False)])
                failed = len(results) - completed
                success_rate = (completed / len(results) * 100) if results else 0
            else:
                completed = 1 if results else 0
                failed = 0 if results else 1
                success_rate = 100 if results else 0
            
            metric = AgentMetrics(
                agent_name=agent_name,
                tasks_completed=completed,
                tasks_failed=failed,
                avg_execution_time_ms=0.0,  # Would be calculated from timestamps
                success_rate=success_rate,
                last_run=datetime.now()
            )
            metrics.append(metric)
        
        return metrics
    
    def analyze_pipeline_health(self, 
                               current_prospects: List[Dict],
                               pipeline_stages: Dict) -> PipelineMetrics:
        """Analyze the health of the sales pipeline."""
        
        # Count prospects by stage
        stages = {
            "new": [],
            "qualified": [],
            "opportunity": [],
            "closed_won": [],
            "closed_lost": []
        }
        
        for prospect in current_prospects:
            stage = prospect.get("stage", "new").lower()
            if stage in stages:
                stages[stage].append(prospect)
        
        # Calculate metrics
        total = len(current_prospects)
        closed_won = len(stages["closed_won"])
        
        pipeline_value = sum(
            p.get("estimated_value", 0) 
            for p in stages["opportunity"]
        )
        
        avg_deal = pipeline_value / len(stages["opportunity"]) if stages["opportunity"] else 0
        
        conversion = (closed_won / total * 100) if total > 0 else 0
        
        return PipelineMetrics(
            total_prospects=total,
            new_leads=len(stages["new"]),
            qualified_leads=len(stages["qualified"]),
            opportunities=len(stages["opportunity"]),
            closed_won=closed_won,
            closed_lost=len(stages["closed_lost"]),
            pipeline_value=pipeline_value,
            avg_deal_size=avg_deal,
            conversion_rate=conversion
        )
    
    def analyze_campaign_performance(self, 
                                    email_results: List[Dict],
                                    linkedin_results: List[Dict]) -> Dict[str, CampaignMetrics]:
        """Analyze outreach campaign performance."""
        
        # Email metrics
        email_sent = len(email_results)
        email_opened = sum(1 for r in email_results if r.get('opened', False))
        email_clicked = sum(1 for r in email_results if r.get('clicked', False))
        email_replied = sum(1 for r in email_results if r.get('replied', False))
        
        email_metrics = CampaignMetrics(
            messages_sent=email_sent,
            messages_delivered=email_sent,
            opened=email_opened,
            clicked=email_clicked,
            replied=email_replied,
            meetings_booked=0,  # Would come from calendar integration
            unsubscribed=0,
            open_rate=(email_opened / email_sent * 100) if email_sent else 0,
            click_rate=(email_clicked / email_sent * 100) if email_sent else 0,
            reply_rate=(email_replied / email_sent * 100) if email_sent else 0
        )
        
        # LinkedIn metrics
        linkedin_sent = len(linkedin_results)
        linkedin_replied = sum(1 for r in linkedin_results if r.get('replied', False))
        
        linkedin_metrics = CampaignMetrics(
            messages_sent=linkedin_sent,
            messages_delivered=linkedin_sent,
            opened=0,  # LinkedIn doesn't provide open rates
            clicked=0,
            replied=linkedin_replied,
            meetings_booked=0,
            unsubscribed=0,
            open_rate=0,
            click_rate=0,
            reply_rate=(linkedin_replied / linkedin_sent * 100) if linkedin_sent else 0
        )
        
        return {
            "email": email_metrics,
            "linkedin": linkedin_metrics
        }
    
    def detect_anomalies(self, metrics: Dict, 
                        threshold_std: float = 2.0) -> List[Dict]:
        """Detect anomalies in current metrics vs historical data."""
        anomalies = []
        
        if len(self.metrics_history) < 7:
            return anomalies  # Need at least a week of data
        
        # Calculate historical averages
        historical = self.metrics_history[-7:]  # Last 7 data points
        
        for metric_name, current_value in metrics.items():
            if not isinstance(current_value, (int, float)):
                continue
            
            historical_values = [
                h.get(metric_name, 0) 
                for h in historical 
                if isinstance(h.get(metric_name), (int, float))
            ]
            
            if len(historical_values) < 3:
                continue
            
            import statistics
            avg = statistics.mean(historical_values)
            std = statistics.stdev(historical_values) if len(historical_values) > 1 else 0
            
            # Check if current value is an outlier
            if std > 0 and abs(current_value - avg) > (threshold_std * std):
                direction = "above" if current_value > avg else "below"
                anomalies.append({
                    "metric": metric_name,
                    "current": current_value,
                    "average": avg,
                    "deviation": abs(current_value - avg) / std,
                    "direction": direction,
                    "severity": "high" if abs(current_value - avg) > (3 * std) else "medium"
                })
        
        return anomalies
    
    def forecast_trends(self, days_ahead: int = 7) -> Dict:
        """Forecast future performance based on historical trends."""
        if len(self.metrics_history) < 14:
            return {"error": "Insufficient data for forecasting (need 14+ days)"}
        
        # Simple linear trend for key metrics
        forecasts = {}
        
        key_metrics = ["messages_sent", "replies_received", "meetings_booked"]
        
        for metric in key_metrics:
            values = [
                h.get(metric, 0) 
                for h in self.metrics_history[-14:]
                if isinstance(h.get(metric), (int, float))
            ]
            
            if len(values) >= 7:
                # Calculate trend (simple moving average slope)
                first_week = sum(values[:7]) / 7
                second_week = sum(values[7:14]) / 7
                weekly_trend = second_week - first_week
                
                # Project forward
                forecast = second_week + (weekly_trend * (days_ahead / 7))
                forecasts[metric] = {
                    "current_weekly_avg": second_week,
                    "weekly_trend": weekly_trend,
                    "forecast_next_week": max(0, forecast),
                    "trend_direction": "up" if weekly_trend > 0 else "down" if weekly_trend < 0 else "stable"
                }
        
        return forecasts
    
    def generate_daily_report(self, agent_metrics: List[AgentMetrics],
                            pipeline: PipelineMetrics,
                            campaigns: Dict[str, CampaignMetrics]) -> Dict:
        """Generate comprehensive daily report."""
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "period": "daily",
            "executive_summary": {
                "total_agents_active": len(agent_metrics),
                "overall_success_rate": sum(m.success_rate for m in agent_metrics) / len(agent_metrics) if agent_metrics else 0,
                "pipeline_health": "healthy" if pipeline.conversion_rate > 5 else "needs_attention",
                "campaign_performance": "strong" if campaigns.get("email", CampaignMetrics(0,0,0,0,0,0,0,0,0,0,0)).reply_rate > 10 else "average"
            },
            "agent_performance": [asdict(m) for m in agent_metrics],
            "pipeline": asdict(pipeline),
            "campaigns": {k: asdict(v) for k, v in campaigns.items()},
            "anomalies": self.detect_anomalies({
                "prospects": pipeline.total_prospects,
                "conversion": pipeline.conversion_rate,
                "messages_sent": campaigns.get("email", CampaignMetrics(0,0,0,0,0,0,0,0,0,0,0)).messages_sent
            }),
            "recommendations": self._generate_recommendations(
                agent_metrics, pipeline, campaigns
            )
        }
        
        # Store for historical tracking
        self.metrics_history.append({
            "timestamp": datetime.now().isoformat(),
            **report["executive_summary"]
        })
        self._save_historical_data()
        
        return report
    
    def _generate_recommendations(self, agent_metrics: List[AgentMetrics],
                                  pipeline: PipelineMetrics,
                                  campaigns: Dict[str, CampaignMetrics]) -> List[str]:
        """Generate actionable recommendations based on metrics."""
        recommendations = []
        
        # Pipeline recommendations
        if pipeline.conversion_rate < 3:
            recommendations.append(
                "⚠️ Conversion rate below 3% - consider refining ICP criteria or improving messaging"
            )
        
        if pipeline.pipeline_value < 10000:
            recommendations.append(
                "📉 Pipeline value below $10K - increase prospecting volume"
            )
        
        # Campaign recommendations
        email = campaigns.get("email", CampaignMetrics(0,0,0,0,0,0,0,0,0,0,0))
        if email.open_rate < 20:
            recommendations.append(
                "📧 Email open rate below 20% - A/B test subject lines"
            )
        
        if email.reply_rate < 5:
            recommendations.append(
                "💬 Reply rate below 5% - personalize message openers"
            )
        
        # Agent recommendations
        for metric in agent_metrics:
            if metric.success_rate < 80:
                recommendations.append(
                    f"🔧 {metric.agent_name} success rate at {metric.success_rate:.1f}% - review error logs"
                )
        
        if not recommendations:
            recommendations.append("✅ All metrics within healthy ranges - maintain current strategy")
        
        return recommendations
    
    def export_report(self, report: Dict, format: str = "json") -> str:
        """Export report in specified format."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            filepath = self.data_dir / f"report_{timestamp}.json"
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            return str(filepath)
        
        elif format == "markdown":
            filepath = self.data_dir / f"report_{timestamp}.md"
            md_content = self._generate_markdown_report(report)
            with open(filepath, 'w') as f:
                f.write(md_content)
            return str(filepath)
        
        return ""
    
    def _generate_markdown_report(self, report: Dict) -> str:
        """Generate human-readable markdown report."""
        lines = [
            "# Daily Performance Report",
            f"Generated: {report['generated_at']}",
            "",
            "## Executive Summary",
            f"- Agents Active: {report['executive_summary']['total_agents_active']}",
            f"- Overall Success Rate: {report['executive_summary']['overall_success_rate']:.1f}%",
            f"- Pipeline Health: {report['executive_summary']['pipeline_health']}",
            f"- Campaign Performance: {report['executive_summary']['campaign_performance']}",
            "",
            "## Recommendations",
        ]
        
        for rec in report['recommendations']:
            lines.append(f"- {rec}")
        
        return "\n".join(lines)
