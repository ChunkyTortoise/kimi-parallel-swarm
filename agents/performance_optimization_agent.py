"""
Performance Optimization Agent
Continuously A/B tests templates, analyzes conversation data, recommends strategy adjustments.
"""
import json
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


@dataclass
class TemplatePerformance:
    template_key: str
    usage_count: int
    reply_count: int
    qualified_count: int
    reply_rate: float
    qualified_rate: float
    recommendation: str


@dataclass
class NichePerformance:
    niche: str
    prospects_researched: int
    connections_sent: int
    connections_accepted: int
    replies_received: int
    qualified_leads: int
    deals_closed: int
    avg_deal_value: float
    close_rate: float


class PerformanceOptimizationAgent:
    """Agent for analyzing performance and optimizing the system."""
    
    def __init__(self, config: Dict, crm_agent=None):
        self.config = config
        self.crm_agent = crm_agent
        self.moonshot_api_key = config.get("moonshot_api_key")
        self.moonshot_base_url = config.get("moonshot_base_url", "https://api.moonshot.cn/v1")
        
        # Performance thresholds
        self.acceptance_rate_target = 0.45
        self.reply_rate_target = 0.20
        self.qualified_rate_target = 0.10
        self.close_rate_target = 0.30
    
    def _call_kimi(self, prompt: str) -> str:
        """Call Kimi K2.5 for analysis."""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.moonshot_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.get("moonshot_model", "kimi-k2.5"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        try:
            response = requests.post(
                f"{self.moonshot_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Kimi API error: {e}")
            return ""
    
    def analyze_template_performance(self, days: int = 14) -> List[TemplatePerformance]:
        """Analyze performance of each outreach template."""
        if not self.crm_agent:
            return []
        
        # Aggregate data by template
        template_stats = defaultdict(lambda: {
            "usage": 0,
            "replies": 0,
            "qualified": 0
        })
        
        for prospect in self.crm_agent.prospects.values():
            template = prospect.get("recommended_template", "unknown")
            template_stats[template]["usage"] += 1
            
            if prospect.get("stage") in ["replied", "qualified", "discovery_call_booked", "proposal_sent", "negotiation", "closed_won"]:
                template_stats[template]["replies"] += 1
            
            if prospect.get("stage") in ["qualified", "discovery_call_booked", "proposal_sent", "negotiation", "closed_won"]:
                template_stats[template]["qualified"] += 1
        
        performances = []
        for template, stats in template_stats.items():
            usage = stats["usage"]
            if usage == 0:
                continue
            
            reply_rate = stats["replies"] / usage
            qualified_rate = stats["qualified"] / usage
            
            # Generate recommendation
            if qualified_rate >= self.qualified_rate_target:
                recommendation = "scale_up"
            elif reply_rate < 0.10:
                recommendation = "pause_and_redesign"
            elif qualified_rate < 0.05:
                recommendation = "tweak_cta"
            else:
                recommendation = "continue_monitoring"
            
            performances.append(TemplatePerformance(
                template_key=template,
                usage_count=usage,
                reply_count=stats["replies"],
                qualified_count=stats["qualified"],
                reply_rate=round(reply_rate, 3),
                qualified_rate=round(qualified_rate, 3),
                recommendation=recommendation
            ))
        
        # Sort by qualified rate (best indicator of quality)
        performances.sort(key=lambda x: x.qualified_rate, reverse=True)
        
        return performances
    
    def analyze_niche_performance(self) -> Tuple[NichePerformance, NichePerformance]:
        """Compare SaaS vs Agency niche performance."""
        if not self.crm_agent:
            return None, None
        
        niches = ["saas", "agency"]
        results = {}
        
        for niche in niches:
            prospects = [p for p in self.crm_agent.prospects.values() if p.get("niche") == niche]
            
            researched = len(prospects)
            connections_sent = len([p for p in prospects if p.get("stage") != "prospect"])
            connections_accepted = len([p for p in prospects if p.get("stage") not in ["prospect", "outreach"]])
            replies = len([p for p in prospects if p.get("stage") in ["replied", "qualified", "discovery_call_booked"]])
            qualified = len([p for p in prospects if p.get("stage") in ["qualified", "discovery_call_booked"]])
            closed = len([p for p in prospects if p.get("stage") == "closed_won"])
            
            # Estimate average deal value from offer ladders
            avg_deal = 8000 if niche == "saas" else 10000
            
            close_rate = closed / qualified if qualified > 0 else 0
            
            results[niche] = NichePerformance(
                niche=niche,
                prospects_researched=researched,
                connections_sent=connections_sent,
                connections_accepted=connections_accepted,
                replies_received=replies,
                qualified_leads=qualified,
                deals_closed=closed,
                avg_deal_value=avg_deal,
                close_rate=round(close_rate, 3)
            )
        
        return results.get("saas"), results.get("agency")
    
    def extract_conversation_insights(self, days: int = 7) -> Dict:
        """Extract insights from conversation data."""
        if not self.crm_agent:
            return {}
        
        objections = []
        buying_signals = []
        pricing_mentions = []
        
        # Analyze prospects with conversation history
        for prospect in self.crm_agent.prospects.values():
            log = prospect.get("outreach_log", [])
            for entry in log:
                if entry.get("action") == "reply_received":
                    message = entry.get("details", {}).get("message", "").lower()
                    
                    # Extract objections
                    objection_patterns = [
                        r"too expensive", r"not in budget", r"can't afford",
                        r"not right now", r"not interested", r"no need",
                        r"we have", r"already use", r"in-house"
                    ]
                    for pattern in objection_patterns:
                        if re.search(pattern, message):
                            objections.append({
                                "prospect_id": prospect["prospect_id"],
                                "objection": message[:100],
                                "date": entry.get("date")
                            })
                    
                    # Extract buying signals
                    buying_patterns = [
                        r"interested", r"tell me more", r"pricing", r"cost",
                        r"how much", r"book a call", r"schedule", r"sounds good"
                    ]
                    for pattern in buying_patterns:
                        if re.search(pattern, message):
                            buying_signals.append({
                                "prospect_id": prospect["prospect_id"],
                                "signal": message[:100],
                                "date": entry.get("date")
                            })
                    
                    # Extract pricing mentions
                    if "price" in message or "cost" in message or "$" in message:
                        pricing_mentions.append({
                            "prospect_id": prospect["prospect_id"],
                            "context": message[:150],
                            "date": entry.get("date")
                        })
        
        return {
            "common_objections": objections[:10],
            "buying_signals": buying_signals[:10],
            "pricing_sensitivity": len(pricing_mentions),
            "objection_categories": self._categorize_objections(objections)
        }
    
    def _categorize_objections(self, objections: List[Dict]) -> Dict[str, int]:
        """Categorize objections by type."""
        categories = defaultdict(int)
        
        for obj in objections:
            text = obj["objection"].lower()
            if "price" in text or "expensive" in text or "budget" in text:
                categories["price"] += 1
            elif "now" in text or "timing" in text:
                categories["timing"] += 1
            elif "have" in text or "use" in text or "already" in text:
                categories["competition"] += 1
            elif "need" in text or "interested" in text:
                categories["no_fit"] += 1
            else:
                categories["other"] += 1
        
        return dict(categories)
    
    def generate_recommendations(self) -> List[Dict]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Get performance data
        template_perf = self.analyze_template_performance()
        saas_perf, agency_perf = self.analyze_niche_performance()
        insights = self.extract_conversation_insights()
        
        # Template recommendations
        low_performers = [t for t in template_perf if t.qualified_rate < 0.05 and t.usage_count > 10]
        if low_performers:
            recommendations.append({
                "type": "template",
                "priority": "high",
                "issue": "Low performing templates",
                "action": f"Pause {len(low_performers)} templates with <5% qualified rate",
                "templates": [t.template_key for t in low_performers]
            })
        
        # Niche allocation recommendations
        if saas_perf and agency_perf:
            if agency_perf.close_rate > saas_perf.close_rate * 1.5:
                recommendations.append({
                    "type": "niche_allocation",
                    "priority": "medium",
                    "issue": "Agency niche outperforming SaaS",
                    "action": "Consider shifting to 60% SaaS / 40% Agency allocation",
                    "current": "70% SaaS / 30% Agency",
                    "suggested": "60% SaaS / 40% Agency"
                })
        
        # Objection-based recommendations
        objection_cats = insights.get("objection_categories", {})
        if objection_cats.get("price", 0) > 5:
            recommendations.append({
                "type": "messaging",
                "priority": "high",
                "issue": "Price objections common",
                "action": "Emphasize ROI and offer lower entry price ($1,800 audit) in templates",
                "data": f"{objection_cats['price']} price objections in last 7 days"
            })
        
        if objection_cats.get("timing", 0) > 3:
            recommendations.append({
                "type": "followup",
                "priority": "medium",
                "issue": "Timing objections",
                "action": "Extend follow-up sequence to 30 days for 'not now' prospects",
                "data": f"{objection_cats['timing']} timing objections"
            })
        
        # LinkedIn health check
        weekly_metrics = self.crm_agent.get_weekly_metrics() if self.crm_agent else {}
        if weekly_metrics.get("acceptance_rate", 0) < 0.35:
            recommendations.append({
                "type": "linkedin_health",
                "priority": "high",
                "issue": "Low connection acceptance rate",
                "action": "Review connection request messages, reduce sales language",
                "data": f"Acceptance rate: {weekly_metrics.get('acceptance_rate', 0):.1%}"
            })
        
        if weekly_metrics.get("reply_rate", 0) < 0.15:
            recommendations.append({
                "type": "messaging",
                "priority": "high",
                "issue": "Low reply rate",
                "action": "A/B test new templates, increase personalization depth",
                "data": f"Reply rate: {weekly_metrics.get('reply_rate', 0):.1%}"
            })
        
        return sorted(recommendations, key=lambda x: 0 if x["priority"] == "high" else 1)
    
    def generate_weekly_report(self) -> Dict:
        """Generate comprehensive weekly performance report."""
        template_perf = self.analyze_template_performance()
        saas_perf, agency_perf = self.analyze_niche_performance()
        insights = self.extract_conversation_insights()
        recommendations = self.generate_recommendations()
        
        weekly_metrics = self.crm_agent.get_weekly_metrics() if self.crm_agent else {}
        pipeline = self.crm_agent.get_pipeline_summary() if self.crm_agent else {}
        
        report = {
            "report_date": datetime.now().isoformat(),
            "period": "Last 7 days",
            "summary": {
                "connections_sent": weekly_metrics.get("connections_sent", 0),
                "acceptance_rate": f"{weekly_metrics.get('acceptance_rate', 0):.1%}",
                "reply_rate": f"{weekly_metrics.get('reply_rate', 0):.1%}",
                "qualified_leads": weekly_metrics.get("discovery_calls_booked", 0),
                "deals_closed": weekly_metrics.get("deals_closed", 0),
                "revenue": f"${weekly_metrics.get('revenue', 0):,}"
            },
            "template_rankings": [
                {
                    "template": t.template_key,
                    "usage": t.usage_count,
                    "reply_rate": f"{t.reply_rate:.1%}",
                    "qualified_rate": f"{t.qualified_rate:.1%}",
                    "action": t.recommendation
                }
                for t in template_perf[:5]
            ],
            "niche_comparison": {
                "saas": {
                    "prospects": saas_perf.prospects_researched if saas_perf else 0,
                    "close_rate": f"{saas_perf.close_rate:.1%}" if saas_perf else "0%",
                    "avg_deal": f"${saas_perf.avg_deal_value:,}" if saas_perf else "$0"
                },
                "agency": {
                    "prospects": agency_perf.prospects_researched if agency_perf else 0,
                    "close_rate": f"{agency_perf.close_rate:.1%}" if agency_perf else "0%",
                    "avg_deal": f"${agency_perf.avg_deal_value:,}" if agency_perf else "$0"
                }
            },
            "insights": {
                "top_objections": list(insights.get("objection_categories", {}).keys())[:3],
                "pricing_sensitivity": insights.get("pricing_sensitivity", 0)
            },
            "recommendations": recommendations,
            "alerts": [
                r["issue"] for r in recommendations 
                if r["priority"] == "high"
            ]
        }
        
        return report
    
    def save_report(self, report: Dict, filepath: str):
        """Save report to file."""
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Weekly report saved to {filepath}")


if __name__ == "__main__":
    agent = PerformanceOptimizationAgent({})
    
    # Test report generation
    report = agent.generate_weekly_report()
    print(json.dumps(report, indent=2))
