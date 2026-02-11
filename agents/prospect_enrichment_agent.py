"""
Prospect Enrichment Agent
Enhances prospect data with additional intelligence from multiple sources
"""
import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class EnrichedProspect:
    """Prospect with enriched data."""
    original_data: Dict
    company_size: Optional[str]
    funding_status: Optional[str]
    tech_stack: List[str]
    recent_news: List[Dict]
    mutual_connections: List[str]
    personality_insights: Optional[Dict]
    engagement_history: List[Dict]
    enrichment_score: float  # 0-100


class ProspectEnrichmentAgent:
    """
    Agent for enriching prospect data with additional intelligence.
    
    Features:
    - Company research (size, funding, tech stack)
    - Recent news and announcements
    - Mutual connection identification
    - Personality insights from social profiles
    - Engagement pattern analysis
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.clearbit_key = self.config.get("clearbit_api_key") or os.getenv("CLEARBIT_API_KEY")
        this.rocketreach_key = self.config.get("rocketreach_key") or os.getenv("ROCKETREACH_KEY")
        
        # Enrichment data sources
        self.sources = {
            "linkedin": True,
            "crunchbase": True,
            "clearbit": bool(self.clearbit_key),
            "rocketreach": bool(this.rocketreach_key),
            "company_website": True
        }
    
    def enrich_prospect(self, prospect: Dict) -> EnrichedProspect:
        """Enrich a single prospect with additional data."""
        enriched = EnrichedProspect(
            original_data=prospect,
            company_size=None,
            funding_status=None,
            tech_stack=[],
            recent_news=[],
            mutual_connections=[],
            personality_insights=None,
            engagement_history=[],
            enrichment_score=0.0
        )
        
        # Enrich company data
        company_data = self._research_company(prospect.get("company", ""))
        enriched.company_size = company_data.get("size")
        enriched.funding_status = company_data.get("funding_status")
        enriched.tech_stack = company_data.get("tech_stack", [])
        
        # Get recent news
        enriched.recent_news = self._get_company_news(prospect.get("company", ""))
        
        # Find mutual connections
        enriched.mutual_connections = self._find_mutual_connections(prospect)
        
        # Analyze personality from social profiles
        enriched.personality_insights = self._analyze_personality(prospect)
        
        # Get engagement history
        enriched.engagement_history = self._get_engagement_history(prospect.get("id"))
        
        # Calculate enrichment score
        enriched.enrichment_score = self._calculate_enrichment_score(enriched)
        
        logger.info(f"Enriched prospect {prospect.get('id')}: score {enriched.enrichment_score}")
        
        return enriched
    
    def _research_company(self, company_name: str) -> Dict:
        """Research company information."""
        # Simulation - would integrate with Clearbit, Crunchbase, etc.
        
        company_data = {
            "size": "unknown",
            "funding_status": "unknown",
            "tech_stack": [],
            "industry": "unknown"
        }
        
        if not company_name:
            return company_data
        
        # Simulate data lookup
        if "stripe" in company_name.lower():
            company_data = {
                "size": "1000-5000",
                "funding_status": "Series H, $600M raised",
                "tech_stack": ["Ruby", "Scala", "React", "AWS"],
                "industry": "Fintech"
            }
        elif "notion" in company_name.lower():
            company_data = {
                "size": "500-1000",
                "funding_status": "Series C, $275M raised",
                "tech_stack": ["TypeScript", "Electron", "Python", "AWS"],
                "industry": "Productivity Software"
            }
        
        return company_data
    
    def _get_company_news(self, company_name: str) -> List[Dict]:
        """Get recent news about the company."""
        news = []
        
        if not company_name:
            return news
        
        # Simulation - would use news APIs
        if "stripe" in company_name.lower():
            news.append({
                "title": "Stripe expands into AI-powered billing",
                "date": "2024-01-15",
                "source": "TechCrunch",
                "relevance": "high"
            })
        
        return news
    
    def _find_mutual_connections(self, prospect: Dict) -> List[str]:
        """Find mutual connections with the prospect."""
        # Simulation - would use LinkedIn API
        return []
    
    def _analyze_personality(self, prospect: Dict) -> Optional[Dict]:
        """Analyze personality from social profiles."""
        # Simulation - would use IBM Watson or similar
        
        title = prospect.get("title", "").lower()
        
        if "cto" in title or "engineering" in title:
            return {
                "archetype": "technical_buyer",
                "preferences": ["detailed_specs", "integration_details", "security_info"],
                "communication_style": "data_driven"
            }
        elif "marketing" in title or "growth" in title:
            return {
                "archetype": "creative_buyer",
                "preferences": ["case_studies", "visual_demo", "roi_stories"],
                "communication_style": "story_driven"
            }
        elif "ceo" in title or "founder" in title:
            return {
                "archetype": "visionary_buyer",
                "preferences": ["strategic_value", "market_position", "scalability"],
                "communication_style": "vision_driven"
            }
        
        return None
    
    def _get_engagement_history(self, prospect_id: str) -> List[Dict]:
        """Get engagement history for the prospect."""
        # Simulation - would query CRM database
        return []
    
    def _calculate_enrichment_score(self, enriched: EnrichedProspect) -> float:
        """Calculate how well the prospect has been enriched."""
        score = 0.0
        
        # Base score
        score += 20
        
        # Company data (30 points)
        if enriched.company_size:
            score += 10
        if enriched.funding_status:
            score += 10
        if enriched.tech_stack:
            score += 10
        
        # News (20 points)
        score += min(20, len(enriched.recent_news) * 10)
        
        # Connections (10 points)
        if enriched.mutual_connections:
            score += min(10, len(enriched.mutual_connections) * 2)
        
        # Personality insights (10 points)
        if enriched.personality_insights:
            score += 10
        
        # Engagement history (10 points)
        if enriched.engagement_history:
            score += min(10, len(enriched.engagement_history) * 2)
        
        return min(100, score)
    
    def enrich_batch(self, prospects: List[Dict]) -> List[EnrichedProspect]:
        """Enrich multiple prospects in batch."""
        results = []
        
        for prospect in prospects:
            try:
                enriched = self.enrich_prospect(prospect)
                results.append(enriched)
            except Exception as e:
                logger.error(f"Error enriching prospect {prospect.get('id')}: {e}")
                # Return with minimal enrichment
                results.append(EnrichedProspect(
                    original_data=prospect,
                    company_size=None,
                    funding_status=None,
                    tech_stack=[],
                    recent_news=[],
                    mutual_connections=[],
                    personality_insights=None,
                    engagement_history=[],
                    enrichment_score=0.0
                ))
        
        return results
    
    def prioritize_by_enrichment(self, prospects: List[EnrichedProspect]) -> List[EnrichedProspect]:
        """Prioritize prospects by enrichment score and data quality."""
        return sorted(prospects, key=lambda p: p.enrichment_score, reverse=True)
    
    def generate_personalization_hints(self, enriched: EnrichedProspect) -> List[str]:
        """Generate personalization hints based on enriched data."""
        hints = []
        
        # Company-based hints
        if enriched.company_size:
            hints.append(f"Company size: {enriched.company_size} - emphasize scalability")
        
        if enriched.funding_status:
            hints.append(f"Funding: {enriched.funding_status} - likely growth mode, emphasize ROI")
        
        if enriched.tech_stack:
            tech_str = ", ".join(enriched.tech_stack[:3])
            hints.append(f"Tech stack includes {tech_str} - emphasize integrations")
        
        # News-based hints
        for news in enriched.recent_news[:2]:
            hints.append(f"Recent news: {news['title'][:80]}...")
        
        # Personality-based hints
        if enriched.personality_insights:
            archetype = enriched.personality_insights.get("archetype", "")
            if archetype == "technical_buyer":
                hints.append("Technical buyer - include API docs, security details")
            elif archetype == "creative_buyer":
                hints.append("Creative buyer - use case studies, visual examples")
            elif archetype == "visionary_buyer":
                hints.append("Visionary buyer - emphasize strategic value and market position")
        
        return hints


if __name__ == "__main__":
    agent = ProspectEnrichmentAgent()
    
    prospect = {
        "id": "123",
        "first_name": "John",
        "last_name": "Doe",
        "company": "Stripe",
        "title": "VP Engineering"
    }
    
    enriched = agent.enrich_prospect(prospect)
    print(f"Enrichment score: {enriched.enrichment_score}")
    print(f"Hints: {agent.generate_personalization_hints(enriched)}")
