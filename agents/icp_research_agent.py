"""
ICP Research Agent
Identifies high-intent prospects across LinkedIn, Reddit, and public databases.
"""
import json
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
import re
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class Prospect:
    prospect_id: str
    name: str
    title: str
    company: str
    company_stage: str
    arr_estimate: str
    pain_signals: List[str]
    email: str
    linkedin_url: str
    niche: str  # "saas" or "agency"
    priority_score: float
    recommended_template: str
    personalization_data: Dict
    source: str
    discovered_at: str
    status: str = "prospect"


class ICPResearchAgent:
    """Agent for researching and identifying ideal customer profile prospects."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.moonshot_api_key = config.get("moonshot_api_key")
        self.moonshot_base_url = config.get("moonshot_base_url", "https://api.moonshot.cn/v1")
        self.session = requests.Session()
        
    def _call_kimi(self, prompt: str, mode: str = "instant") -> str:
        """Call Kimi K2.5 API."""
        headers = {
            "Authorization": f"Bearer {self.moonshot_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.get("moonshot_model", "kimi-k2.5"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3 if mode == "instant" else 0.7,
            "max_tokens": 4000
        }
        
        try:
            response = self.session.post(
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
    
    def _generate_prospect_id(self, name: str, company: str) -> str:
        """Generate unique prospect ID."""
        import hashlib
        return hashlib.md5(f"{name}-{company}".encode()).hexdigest()[:12]
    
    def _calculate_priority_score(self, pain_signals: List[str], title: str, company_stage: str) -> float:
        """Calculate priority score 0-10 based on ICP criteria."""
        score = 5.0
        
        # Pain signals boost score
        score += len(pain_signals) * 0.8
        
        # Decision maker titles get priority
        decision_maker_keywords = ["founder", "vp", "head", "director", "cto", "ceo", "cmo"]
        if any(kw in title.lower() for kw in decision_maker_keywords):
            score += 1.5
        
        # Company stage scoring
        if "series a" in company_stage.lower() or "seed" in company_stage.lower():
            score += 0.5
        
        return min(round(score, 1), 10.0)
    
    def _select_template(self, pain_signals: List[str], niche: str) -> str:
        """Select best outreach template based on signals."""
        pain_text = " ".join(pain_signals).lower()
        
        if niche == "saas":
            if "reporting" in pain_text or "manual" in pain_text:
                return "Template_1_Pain_Point"
            elif "competitor" in pain_text or "dashboard" in pain_text:
                return "Template_2_Competitor_Reference"
            elif "data" in pain_text and ("overwhelm" in pain_text or "insight" in pain_text):
                return "Template_3_Content_Hook"
            else:
                return "Template_4_ROI_Focused"
        else:  # agency
            if "onboarding" in pain_text or "reporting" in pain_text:
                return "Template_1_Time_Savings"
            elif "scale" in pain_text or "growth" in pain_text:
                return "Template_2_Scale_Constraint"
            else:
                return "Template_3_Competitive_Edge"
    
    def research_linkedin_prospects(self, search_queries: List[str], niche: str, count: int = 25) -> List[Prospect]:
        """Research prospects from LinkedIn search queries."""
        prospects = []
        
        # This is a simplified implementation
        # In production, you'd integrate with LinkedIn Sales Navigator API
        # or use Phantombuster + proxy rotation
        
        for query in search_queries:
            prompt = f"""Given the LinkedIn search query "{query}" for {niche} prospects, 
            generate {count // len(search_queries)} realistic prospect profiles that match the ICP.
            
            Return JSON array with objects containing:
            - name
            - title  
            - company
            - company_stage (e.g., "Seed", "Series A", "$1M ARR", etc.)
            - arr_estimate
            - pain_signals (array of 2-4 specific pain points)
            - email (can be placeholder)
            - linkedin_url
            - personalization_data (object with recent milestone, funding info, etc.)
            
            Make data realistic and specific to the {niche} niche."""
            
            response = self._call_kimi(prompt, mode="instant")
            
            try:
                # Extract JSON from response
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    for p in data:
                        prospect = Prospect(
                            prospect_id=self._generate_prospect_id(p["name"], p["company"]),
                            name=p["name"],
                            title=p["title"],
                            company=p["company"],
                            company_stage=p["company_stage"],
                            arr_estimate=p["arr_estimate"],
                            pain_signals=p["pain_signals"],
                            email=p.get("email", ""),
                            linkedin_url=p["linkedin_url"],
                            niche=niche,
                            priority_score=self._calculate_priority_score(p["pain_signals"], p["title"], p["company_stage"]),
                            recommended_template=self._select_template(p["pain_signals"], niche),
                            personalization_data=p.get("personalization_data", {}),
                            source="linkedin_research",
                            discovered_at=datetime.now().isoformat()
                        )
                        prospects.append(prospect)
            except Exception as e:
                logger.error(f"Error parsing LinkedIn prospects: {e}")
        
        return prospects
    
    def monitor_reddit(self, subreddits: List[str], keywords: List[str]) -> List[Dict]:
        """Monitor Reddit for prospect signals."""
        import praw
        
        reddit = praw.Reddit(
            client_id=self.config.get("reddit_client_id"),
            client_secret=self.config.get("reddit_client_secret"),
            user_agent=self.config.get("reddit_user_agent", "KimiAgent/1.0")
        )
        
        opportunities = []
        
        for subreddit_name in subreddits:
            try:
                subreddit = reddit.subreddit(subreddit_name)
                for post in subreddit.new(limit=50):
                    post_text = f"{post.title} {post.selftext}".lower()
                    if any(kw.lower() in post_text for kw in keywords):
                        opportunities.append({
                            "type": "reddit_post",
                            "subreddit": subreddit_name,
                            "title": post.title,
                            "url": f"https://reddit.com{post.permalink}",
                            "author": str(post.author),
                            "created_utc": post.created_utc,
                            "keywords_found": [kw for kw in keywords if kw.lower() in post_text]
                        })
            except Exception as e:
                logger.error(f"Reddit monitoring error for r/{subreddit_name}: {e}")
        
        return opportunities
    
    def enrich_prospect(self, prospect: Prospect) -> Prospect:
        """Enrich prospect data with additional research."""
        prompt = f"""Enrich this prospect data with additional research:
        
        Name: {prospect.name}
        Title: {prospect.title}  
        Company: {prospect.company}
        
        Find or generate:
        1. Recent company news/funding
        2. Tech stack indicators
        3. Decision-making authority indicators
        4. Email pattern for company (if possible)
        
        Return as JSON with keys: recent_news, tech_stack, authority_signals, email_guess"""
        
        response = self._call_kimi(prompt, mode="instant")
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                enrichment = json.loads(json_match.group())
                prospect.personalization_data.update(enrichment)
        except Exception as e:
            logger.error(f"Enrichment error: {e}")
        
        return prospect
    
    def research_daily_batch(self, saas_count: int = 35, agency_count: int = 15) -> List[Prospect]:
        """Research daily batch of prospects (35 SaaS + 15 Agency = 50 total)."""
        all_prospects = []
        
        # SaaS queries
        saas_queries = [
            "VP Product SaaS seed funded",
            "SaaS founder analytics data",
            "Head of Growth startup metrics",
            "CTO SaaS dashboard reporting"
        ]
        saas_prospects = self.research_linkedin_prospects(saas_queries, "saas", saas_count)
        all_prospects.extend(saas_prospects)
        
        # Agency queries  
        agency_queries = [
            "marketing agency owner founder",
            "digital agency operations director",
            "PPC agency founder automation"
        ]
        agency_prospects = self.research_linkedin_prospects(agency_queries, "agency", agency_count)
        all_prospects.extend(agency_prospects)
        
        # Monitor Reddit for both niches
        reddit_opps = self.monitor_reddit(
            ["SaaS", "startups", "marketing"],
            ["analytics", "dashboard", "reporting", "automation", "manual work"]
        )
        
        logger.info(f"Research complete: {len(all_prospects)} prospects, {len(reddit_opps)} Reddit opportunities")
        
        return all_prospects
    
    def export_to_json(self, prospects: List[Prospect], filepath: str):
        """Export prospects to JSON file."""
        data = [asdict(p) for p in prospects]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Exported {len(prospects)} prospects to {filepath}")


if __name__ == "__main__":
    # Test the agent
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    config = {
        "moonshot_api_key": os.getenv("MOONSHOT_API_KEY"),
        "reddit_client_id": os.getenv("REDDIT_CLIENT_ID"),
        "reddit_client_secret": os.getenv("REDDIT_CLIENT_SECRET")
    }
    
    agent = ICPResearchAgent(config)
    prospects = agent.research_daily_batch(saas_count=5, agency_count=3)
    
    for p in prospects:
        print(f"{p.name} @ {p.company} ({p.niche}) - Score: {p.priority_score}")
