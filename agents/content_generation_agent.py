"""
Content Generation Agent
Creates blog posts, social media content, and marketing copy
"""
import os
import logging
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ContentPiece:
    """Represents a piece of generated content."""
    content_id: str
    content_type: Literal["blog", "linkedin", "twitter", "email", "ad"]
    title: str
    body: str
    hashtags: List[str]
    seo_keywords: List[str]
    character_count: int
    reading_time_minutes: int
    generated_at: datetime
    quality_score: float  # 0-10


class ContentGenerationAgent:
    """
    Agent for generating various types of marketing content.
    
    Content Types:
    - Blog posts (SEO optimized)
    - LinkedIn posts (professional)
    - Twitter/X threads (viral potential)
    - Email newsletters
    - Ad copy (Google/Facebook)
    """
    
    def __init__(self, moonshot_api_key: Optional[str] = None):
        self.api_key = moonshot_api_key or os.getenv("MOONSHOT_API_KEY")
        self.model = "kimi-k2.5"
        
        # Content templates
        self.templates = {
            "blog": self._get_blog_template(),
            "linkedin": self._get_linkedin_template(),
            "twitter": self._get_twitter_template(),
            "newsletter": self._get_newsletter_template(),
            "ad": self._get_ad_template()
        }
    
    def _get_blog_template(self) -> str:
        return """Write a comprehensive blog post about {{topic}}.

Target Audience: {{audience}}
Tone: {{tone}}
SEO Keywords: {{keywords}}
Word Count: {{word_count}}

Structure:
1. Hook - Compelling opening that addresses a pain point
2. Problem - Describe the challenge in detail
3. Solution - Present the answer with examples
4. Proof - Data, case studies, testimonials
5. CTA - Clear next step for readers

Guidelines:
- Use H2 and H3 headings
- Include 2-3 relevant statistics
- Add bullet points for readability
- End with a question to encourage comments"""
    
    def _get_linkedin_template(self) -> str:
        return """Write a LinkedIn post about {{topic}}.

Target: {{audience}}
Tone: Professional but conversational
Length: 150-300 words

Structure:
1. Hook (first 2 lines) - Make them click "see more"
2. Story/Insight - Personal experience or observation
3. Lesson/Value - Actionable takeaway
4. Engagement question - Prompt comments
5. 3-5 relevant hashtags

Guidelines:
- Use line breaks for readability
- Include 1-2 emojis maximum
- Reference trends or recent news if relevant
- Tag relevant people if applicable"""
    
    def _get_twitter_template(self) -> str:
        return """Write a Twitter/X thread about {{topic}}.

Target: {{audience}}
Tone: {{tone}}
Format: Thread (5-10 tweets)

Structure:
Tweet 1: Hook - Strong opening that creates curiosity
Tweet 2-9: Value - Break down the topic into digestible points
Tweet 10: CTA - Follow, RT, or comment prompt

Guidelines:
- Each tweet under 280 characters
- Use numbering (1/10, 2/10, etc.)
- Include 1 powerful image suggestion
- End with engagement question
- Thread should tell a complete story"""
    
    def _get_newsletter_template(self) -> str:
        return """Write an email newsletter about {{topic}}.

Audience: {{audience}}
Tone: Friendly, valuable, not salesy
Sections: 3-5

Structure:
1. Subject Line - Compelling, under 50 chars
2. Opening - Personal greeting, brief intro
3. Main Content - Valuable insights/tips
4. Curated Links - 2-3 relevant resources
5. P.S. - Personal touch or bonus tip

Guidelines:
- Scannable with subheadings
- One clear CTA
- Mobile-friendly formatting"""
    
    def _get_ad_template(self) -> str:
        return """Write ad copy for {{platform}} about {{topic}}.

Platform: {{platform}} (Google/Facebook/LinkedIn)
Objective: {{objective}}
Audience: {{audience}}

Structure:
Headline (30-40 chars): Attention-grabbing, benefit-focused
Body (90-125 chars): Key benefit + social proof or urgency
CTA (2-4 words): Action-oriented (Get, Start, Claim, etc.)

Guidelines:
- Focus on ONE main benefit
- Include numbers if possible (Save 50%, 10K+ users)
- Create urgency or scarcity
- Match platform tone (professional for LinkedIn, casual for FB)"""
    
    def generate_content(self, content_type: str, topic: str,
                        audience: str, tone: str = "professional",
                        keywords: Optional[List[str]] = None,
                        word_count: int = 500) -> ContentPiece:
        """Generate content based on type and parameters."""
        
        template = self.templates.get(content_type, self.templates["blog"])
        
        # Build prompt
        keywords_str = ", ".join(keywords) if keywords else "relevant keywords"
        
        prompt = template.replace("{{topic}}", topic)
        prompt = prompt.replace("{{audience}}", audience)
        prompt = prompt.replace("{{tone}}", tone)
        prompt = prompt.replace("{{keywords}}", keywords_str)
        prompt = prompt.replace("{{word_count}}", str(word_count))
        
        # Call Kimi API (simulation for now)
        generated_content = self._call_kimi_api(prompt, content_type)
        
        # Parse and structure
        content = self._parse_generated_content(
            generated_content, content_type, topic
        )
        
        return content
    
    def _call_kimi_api(self, prompt: str, content_type: str) -> str:
        """Call Kimi K2.5 API to generate content."""
        # Simulation mode - would integrate with actual API
        logger.info(f"Generating {content_type} content via Kimi API")
        
        # Return simulated content based on type
        simulations = {
            "blog": f"# The Ultimate Guide to {prompt[:30]}...\n\n[Full blog post content would be generated here via Kimi K2.5 API]",
            "linkedin": f"🚀 Just published insights on {prompt[:30]}...\n\n[LinkedIn post would be generated here]",
            "twitter": f"1/ 🧵 Thread on {prompt[:30]}...\n\n[Twitter thread would be generated here]",
            "newsletter": f"Subject: This Week: {prompt[:30]}\n\n[Newsletter would be generated here]",
            "ad": f"Headline: Transform Your {prompt[:30]}\n\n[Ad copy would be generated here]"
        }
        
        return simulations.get(content_type, "[Content generation simulated]")
    
    def _parse_generated_content(self, raw_content: str, 
                                content_type: str, topic: str) -> ContentPiece:
        """Parse raw content into structured format."""
        
        # Extract hashtags
        import re
        hashtags = re.findall(r'#\w+', raw_content)
        if not hashtags:
            hashtags = [f"#{topic.replace(' ', '')}", "#B2B", "#SaaS"]
        
        # Estimate reading time (200 words per minute)
        word_count = len(raw_content.split())
        reading_time = max(1, word_count // 200)
        
        # Generate SEO keywords
        seo_keywords = topic.lower().split()[:5]
        
        return ContentPiece(
            content_id=f"{content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content_type=content_type,
            title=topic[:100],
            body=raw_content,
            hashtags=hashtags[:5],
            seo_keywords=seo_keywords,
            character_count=len(raw_content),
            reading_time_minutes=reading_time,
            generated_at=datetime.now(),
            quality_score=8.5  # Would be scored by Kimi
        )
    
    def generate_content_calendar(self, topics: List[str],
                                 content_types: List[str],
                                 schedule_days: int = 30) -> List[Dict]:
        """Generate a full content calendar."""
        calendar = []
        
        for i, topic in enumerate(topics):
            content_type = content_types[i % len(content_types)]
            
            content = self.generate_content(
                content_type=content_type,
                topic=topic,
                audience="B2B professionals",
                tone="professional"
            )
            
            calendar.append({
                "day": i + 1,
                "topic": topic,
                "type": content_type,
                "content": content,
                "publish_date": datetime.now().strftime("%Y-%m-%d")
            })
        
        return calendar
    
    def repurpose_content(self, original_content: ContentPiece,
                         target_type: str) -> ContentPiece:
        """Repurpose existing content into a new format."""
        
        prompt = f"""Repurpose this {original_content.content_type} content into a {target_type}:

Original:
{original_content.body[:500]}

Target Format: {target_type}
Maintain the core message but adapt for the new platform's style and constraints.
"""
        
        new_content = self._call_kimi_api(prompt, target_type)
        
        return self._parse_generated_content(
            new_content, target_type, original_content.title
        )
    
    def score_content_quality(self, content: ContentPiece) -> Dict:
        """Score content quality across multiple dimensions."""
        
        scores = {
            "engagement_potential": min(10, content.quality_score + 0.5),
            "seo_optimization": min(10, len(content.seo_keywords) * 1.5),
            "readability": min(10, 10 - (content.reading_time_minutes / 10)),
            "completeness": min(10, content.character_count / 100),
            "viral_potential": min(10, len(content.hashtags) * 1.5)
        }
        
        scores["overall"] = sum(scores.values()) / len(scores)
        
        return scores
