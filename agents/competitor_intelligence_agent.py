"""
Competitor Intelligence Agent
Monitors competitor activities, pricing, and market positioning
"""
import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


@dataclass
class CompetitorInsight:
    """Represents a competitor insight."""
    competitor_name: str
    insight_type: str  # pricing, feature, positioning, hiring
    description: str
    source: str
    date_detected: datetime
    confidence_score: float  # 0-1
    recommended_action: Optional[str] = None


class CompetitorIntelligenceAgent:
    """
    Agent for monitoring and analyzing competitor activities.
    
    Features:
    - Track competitor pricing changes
    - Monitor new feature releases
    - Analyze job postings for strategy signals
    - Track funding and acquisitions
    - Monitor social media positioning
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.competitors = self.config.get("competitors", [])
        self.tracking_keywords = self.config.get("keywords", [])
        self.insights_history: List[CompetitorInsight] = []
        
        # Data sources
        self.sources = {
            "linkedin": self.config.get("linkedin_enabled", True),
            "crunchbase": self.config.get("crunchbase_enabled", True),
            "job_boards": self.config.get("job_tracking_enabled", True),
            "pricing_pages": self.config.get("pricing_tracking_enabled", True),
            "twitter": self.config.get("twitter_enabled", False)
        }
    
    def add_competitor(self, name: str, website: str, 
                      linkedin_url: Optional[str] = None) -> bool:
        """Add a new competitor to monitor."""
        competitor = {
            "name": name,
            "website": website,
            "linkedin_url": linkedin_url,
            "added_at": datetime.now().isoformat(),
            "baseline_pricing": None,
            "baseline_features": [],
            "last_checked": None
        }
        self.competitors.append(competitor)
        logger.info(f"Added competitor: {name}")
        return True
    
    def monitor_pricing_changes(self, competitor: Dict) -> Optional[CompetitorInsight]:
        """Monitor competitor pricing page for changes."""
        # This would scrape pricing pages or use APIs
        # Simulation for now
        
        logger.info(f"Checking pricing for {competitor['name']}")
        
        # Simulate price change detection
        if competitor.get("baseline_pricing"):
            # Compare with current
            pass
        else:
            # Set baseline
            competitor["baseline_pricing"] = {
                "starter": 29,
                "professional": 99,
                "enterprise": 299,
                "captured_at": datetime.now().isoformat()
            }
        
        return None  # No change detected in simulation
    
    def monitor_job_postings(self, competitor: Dict) -> List[CompetitorInsight]:
        """Analyze job postings for strategic signals."""
        insights = []
        
        # Key roles that indicate strategy shifts
        strategic_roles = [
            "enterprise sales", "solution engineer", "integration",
            "ai/ml engineer", "data scientist", "product manager",
            "customer success", "account executive"
        ]
        
        logger.info(f"Checking job postings for {competitor['name']}")
        
        # Simulation: Detect strategic hiring
        if "salesforce" in competitor["name"].lower():
            insight = CompetitorInsight(
                competitor_name=competitor["name"],
                insight_type="hiring",
                description="Hiring 5 Enterprise Account Executives - likely targeting mid-market expansion",
                source="LinkedIn Jobs",
                date_detected=datetime.now(),
                confidence_score=0.85,
                recommended_action="Review your enterprise positioning and prepare competitive responses"
            )
            insights.append(insight)
        
        return insights
    
    def monitor_social_positioning(self, competitor: Dict) -> List[CompetitorInsight]:
        """Monitor social media for positioning changes."""
        insights = []
        
        logger.info(f"Checking social positioning for {competitor['name']}")
        
        # Simulation: Detect messaging shift
        if competitor["name"] == "HubSpot":
            insight = CompetitorInsight(
                competitor_name=competitor["name"],
                insight_type="positioning",
                description="Shifted messaging from 'inbound marketing' to 'customer platform' - expanding beyond marketing",
                source="LinkedIn/Twitter",
                date_detected=datetime.now(),
                confidence_score=0.90,
                recommended_action="Highlight your specialized focus vs their broad approach"
            )
            insights.append(insight)
        
        return insights
    
    def analyze_feature_releases(self, competitor: Dict) -> List[CompetitorInsight]:
        """Monitor for new feature announcements."""
        insights = []
        
        logger.info(f"Checking feature releases for {competitor['name']}")
        
        # Simulation: Detect AI feature launch
        if "ai" in competitor["name"].lower() or "openai" in competitor["name"].lower():
            insight = CompetitorInsight(
                competitor_name=competitor["name"],
                insight_type="feature",
                description="Launched AI-powered content generation feature - directly competes with your offering",
                source="Product Blog",
                date_detected=datetime.now(),
                confidence_score=0.95,
                recommended_action="Accelerate your AI roadmap and emphasize your unique data advantages"
            )
            insights.append(insight)
        
        return insights
    
    def check_funding_news(self, competitor: Dict) -> Optional[CompetitorInsight]:
        """Monitor for funding and acquisition news."""
        logger.info(f"Checking funding news for {competitor['name']}")
        
        # Simulation: Detect funding
        if competitor["name"] == "Notion":
            return CompetitorInsight(
                competitor_name=competitor["name"],
                insight_type="funding",
                description="Raised $50M Series C at $2B valuation - significant war chest for expansion",
                source="TechCrunch",
                date_detected=datetime.now(),
                confidence_score=0.98,
                recommended_action="Expect aggressive hiring and pricing - focus on your niche expertise"
            )
        
        return None
    
    def run_full_competitor_scan(self) -> Dict:
        """Run comprehensive scan on all competitors."""
        all_insights = []
        
        for competitor in self.competitors:
            logger.info(f"Scanning competitor: {competitor['name']}")
            
            # Run all monitoring functions
            pricing = self.monitor_pricing_changes(competitor)
            if pricing:
                all_insights.append(pricing)
            
            jobs = self.monitor_job_postings(competitor)
            all_insights.extend(jobs)
            
            social = self.monitor_social_positioning(competitor)
            all_insights.extend(social)
            
            features = self.analyze_feature_releases(competitor)
            all_insights.extend(features)
            
            funding = self.check_funding_news(competitor)
            if funding:
                all_insights.append(funding)
            
            competitor["last_checked"] = datetime.now().isoformat()
        
        # Store insights
        self.insights_history.extend(all_insights)
        
        return {
            "scan_date": datetime.now().isoformat(),
            "competitors_scanned": len(self.competitors),
            "insights_found": len(all_insights),
            "insights_by_type": self._categorize_insights(all_insights),
            "high_priority": [i for i in all_insights if i.confidence_score > 0.8],
            "all_insights": all_insights
        }
    
    def _categorize_insights(self, insights: List[CompetitorInsight]) -> Dict:
        """Categorize insights by type."""
        categories = {}
        for insight in insights:
            if insight.insight_type not in categories:
                categories[insight.insight_type] = []
            categories[insight.insight_type].append(insight)
        
        return {k: len(v) for k, v in categories.items()}
    
    def generate_competitive_report(self, days: int = 7) -> Dict:
        """Generate weekly competitive intelligence report."""
        cutoff = datetime.now() - timedelta(days=days)
        recent_insights = [
            i for i in self.insights_history 
            if i.date_detected > cutoff
        ]
        
        return {
            "report_period": f"Last {days} days",
            "total_insights": len(recent_insights),
            "by_competitor": self._group_by_competitor(recent_insights),
            "by_type": self._categorize_insights(recent_insights),
            "trends": self._identify_trends(recent_insights),
            "recommendations": self._generate_strategic_recommendations(recent_insights)
        }
    
    def _group_by_competitor(self, insights: List[CompetitorInsight]) -> Dict:
        """Group insights by competitor."""
        grouped = {}
        for insight in insights:
            name = insight.competitor_name
            if name not in grouped:
                grouped[name] = []
            grouped[name].append(insight)
        return grouped
    
    def _identify_trends(self, insights: List[CompetitorInsight]) -> List[str]:
        """Identify trends across insights."""
        trends = []
        
        # Check for AI focus
        ai_count = sum(1 for i in insights if "ai" in i.description.lower())
        if ai_count >= 3:
            trends.append(f"AI features: {ai_count} competitors launched AI capabilities")
        
        # Check for pricing changes
        pricing_count = sum(1 for i in insights if i.insight_type == "pricing")
        if pricing_count >= 2:
            trends.append(f"Pricing pressure: {pricing_count} competitors adjusted pricing")
        
        return trends
    
    def _generate_strategic_recommendations(self, 
                                           insights: List[CompetitorInsight]) -> List[str]:
        """Generate strategic recommendations based on insights."""
        recommendations = []
        
        # Collect recommended actions from high-confidence insights
        for insight in insights:
            if insight.confidence_score > 0.8 and insight.recommended_action:
                recommendations.append({
                    "priority": "high" if insight.confidence_score > 0.9 else "medium",
                    "competitor": insight.competitor_name,
                    "action": insight.recommended_action
                })
        
        return recommendations


if __name__ == "__main__":
    # Example usage
    config = {
        "competitors": [
            {"name": "Salesforce", "website": "salesforce.com"},
            {"name": "HubSpot", "website": "hubspot.com"},
            {"name": "Notion", "website": "notion.so"}
        ]
    }
    
    agent = CompetitorIntelligenceAgent(config)
    results = agent.run_full_competitor_scan()
    print(json.dumps(results, indent=2, default=str))
