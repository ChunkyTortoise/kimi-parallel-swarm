"""
Copy Generation Agent
Generates hyper-personalized outreach messages using templates and Kimi K2.5.
"""
import json
import logging
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class GeneratedMessage:
    prospect_id: str
    message_type: str
    subject: str
    body: str
    quality_score: float
    personalization_elements: List[str]
    send_status: str
    template_used: str


class CopyGenerationAgent:
    """Agent for generating personalized outreach messages."""
    
    def __init__(self, config: Dict, templates_path: str = "templates"):
        self.config = config
        self.templates_path = Path(templates_path)
        self.moonshot_api_key = config.get("moonshot_api_key")
        self.moonshot_base_url = config.get("moonshot_base_url", "https://api.moonshot.cn/v1")
        self.quality_threshold = config.get("quality_threshold", 7.0)
        self.user_name = config.get("user_name", "Your Name")
        self.user_title = config.get("user_title", "AI Engineer")
        self.linkedin_profile = config.get("linkedin_profile_url", "")
        
        self.saas_templates = self._load_templates("linkedin_outreach_saas.json")
        self.agency_templates = self._load_templates("linkedin_outreach_agency.json")
    
    def _load_templates(self, filename: str) -> Dict:
        """Load message templates from JSON."""
        try:
            filepath = self.templates_path / filename
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading templates {filename}: {e}")
            return {}
    
    def _call_kimi(self, prompt: str, mode: str = "thinking") -> str:
        """Call Kimi K2.5 API with thinking mode for quality."""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.moonshot_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.get("moonshot_model", "kimi-k2.5"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000
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
    
    def _calculate_quality_score(self, message: str, personalization_data: Dict) -> float:
        """Calculate quality score (0-10) for generated message."""
        score = 5.0
        
        # Length check (100-150 words ideal for LinkedIn)
        word_count = len(message.split())
        if 80 <= word_count <= 170:
            score += 1.5
        elif 60 <= word_count <= 200:
            score += 0.5
        
        # Personalization elements present
        personalization_count = sum(1 for key, value in personalization_data.items() 
                                    if value and str(value).lower() in message.lower())
        score += min(personalization_count * 0.5, 2.0)
        
        # No placeholder text remaining
        placeholders = ["[Company]", "[First Name]", "[Agency]", "[Your Name]", "[X hours]"]
        if not any(ph in message for ph in placeholders):
            score += 1.0
        else:
            score -= 2.0
        
        # Conversational tone (avoid corporate jargon)
        corporate_words = ["leverage", "synergy", "paradigm", "utilize", "holistic"]
        if not any(word in message.lower() for word in corporate_words):
            score += 0.5
        
        # Has clear CTA
        if any(cta in message.lower() for cta in ["worth a", "interested", "chat", "call", "15-min", "quick convo"]):
            score += 0.5
        
        return round(max(min(score, 10.0), 1.0), 1)
    
    def _extract_personalization_elements(self, message: str, prospect_data: Dict) -> List[str]:
        """Extract which personalization elements were used."""
        elements = []
        
        for key, value in prospect_data.get("personalization_data", {}).items():
            if value and str(value).lower() in message.lower():
                elements.append(key)
        
        if prospect_data.get("company") and prospect_data["company"].lower() in message.lower():
            elements.append("company_name")
        
        if prospect_data.get("name", "").split()[0].lower() in message.lower():
            elements.append("first_name")
        
        return elements
    
    def personalize_message(self, prospect: Dict, template_key: Optional[str] = None) -> GeneratedMessage:
        """Generate personalized message for a prospect."""
        niche = prospect.get("niche", "saas")
        templates = self.saas_templates if niche == "saas" else self.agency_templates
        
        # Select template
        if template_key and template_key in templates:
            template = templates[template_key]
        else:
            template_key = prospect.get("recommended_template", list(templates.keys())[0])
            template = templates.get(template_key, list(templates.values())[0])
        
        # Build personalization data
        personalization = prospect.get("personalization_data", {})
        first_name = prospect.get("name", "").split()[0]
        company = prospect.get("company", "")
        
        # Generate personalized message using Kimi
        prompt = f"""You are an expert copywriter specializing in personalized LinkedIn outreach.
        
        ORIGINAL TEMPLATE:
        Subject: {template['Subject']}
        Body: {template['Body']}
        
        PROSPECT DATA:
        - Name: {prospect.get('name')}
        - Title: {prospect.get('title')}
        - Company: {company}
        - Stage: {prospect.get('company_stage')}
        - Pain Signals: {', '.join(prospect.get('pain_signals', []))}
        - Personalization Data: {json.dumps(personalization, indent=2)}
        
        YOUR TASK:
        1. Replace ALL placeholders like [Company], [First Name], [Agency Name], etc. with actual values
        2. Use first name only (not full name)
        3. Incorporate 1-2 pain signals naturally into the message
        4. Add specific detail from personalization_data if available
        5. Sign with: {self.user_name}
        6. Keep tone conversational, not corporate
        7. Keep length 100-150 words
        
        Return ONLY the final message as:
        SUBJECT: [subject line]
        BODY:
        [message body]
        
        No explanations, no markdown, just the message."""
        
        response = self._call_kimi(prompt, mode="thinking")
        
        # Parse response
        subject = ""
        body = ""
        
        if "SUBJECT:" in response:
            lines = response.split("\n")
            for i, line in enumerate(lines):
                if "SUBJECT:" in line:
                    subject = line.replace("SUBJECT:", "").strip()
                elif "BODY:" in line:
                    body = "\n".join(lines[i+1:]).strip()
                    break
        
        if not body:
            # Fallback: use template directly with simple replacement
            subject = template['Subject'].replace("[Company]", company).replace("[First Name]", first_name)
            body = template['Body'].replace("[Company]", company).replace("[First Name]", first_name).replace("[Your Name]", self.user_name)
        
        # Calculate quality
        personalization_elements = self._extract_personalization_elements(body, prospect)
        quality_score = self._calculate_quality_score(body, prospect)
        
        # Determine send status
        send_status = "ready" if quality_score >= self.quality_threshold else "needs_review"
        
        return GeneratedMessage(
            prospect_id=prospect.get("prospect_id"),
            message_type="LinkedIn DM",
            subject=subject,
            body=body,
            quality_score=quality_score,
            personalization_elements=personalization_elements,
            send_status=send_status,
            template_used=template_key
        )
    
    def generate_batch(self, prospects: List[Dict]) -> List[GeneratedMessage]:
        """Generate messages for a batch of prospects."""
        messages = []
        
        for prospect in prospects:
            try:
                message = self.personalize_message(prospect)
                messages.append(message)
                logger.info(f"Generated message for {prospect.get('name')} - Score: {message.quality_score}")
            except Exception as e:
                logger.error(f"Error generating message for {prospect.get('name')}: {e}")
        
        return messages
    
    def generate_followup(self, prospect: Dict, stage: int, conversation_history: List[Dict]) -> GeneratedMessage:
        """Generate follow-up message based on conversation stage."""
        
        stage_prompts = {
            1: "Initial follow-up (3 days after first message). Soft reminder, add value.",
            2: "Second follow-up (7 days). Brief check-in, offer case study or resource.",
            3: "Final follow-up (14 days). Offer free audit or consultation, last attempt."
        }
        
        prompt = f"""Generate a follow-up LinkedIn message.
        
        Prospect: {prospect.get('name')} at {prospect.get('company')}
        Stage: {stage} - {stage_prompts.get(stage, 'General follow-up')}
        
        Previous messages:
        {json.dumps(conversation_history, indent=2)}
        
        Rules:
        - Keep it under 80 words
        - Reference previous conversation lightly
        - No pressure, but clear next step
        - Sign as {self.user_name}
        
        Return as:
        SUBJECT: [optional for follow-ups]
        BODY:
        [message]"""
        
        response = self._call_kimi(prompt, mode="thinking")
        
        body = response.replace("BODY:", "").replace("SUBJECT:", "").strip()
        
        return GeneratedMessage(
            prospect_id=prospect.get("prospect_id"),
            message_type="LinkedIn Follow-up",
            subject="",
            body=body,
            quality_score=8.0,
            personalization_elements=["conversation_history"],
            send_status="ready",
            template_used=f"followup_stage_{stage}"
        )


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    config = {
        "moonshot_api_key": os.getenv("MOONSHOT_API_KEY"),
        "user_name": "Alex Chen",
        "user_title": "AI Engineer | Analytics for SaaS"
    }
    
    agent = CopyGenerationAgent(config, templates_path="/Users/cave/Downloads")
    
    # Test with sample prospect
    test_prospect = {
        "prospect_id": "test123",
        "name": "Sarah Johnson",
        "title": "VP Product",
        "company": "DataFlow SaaS",
        "niche": "saas",
        "company_stage": "Series A",
        "pain_signals": ["manual reporting taking 10hrs/week", "data scattered across tools"],
        "personalization_data": {"recent_milestone": "just raised $5M Series A"},
        "recommended_template": "Template_1_Pain_Point"
    }
    
    message = agent.personalize_message(test_prospect)
    print(f"\nQuality Score: {message.quality_score}")
    print(f"Status: {message.send_status}")
    print(f"\nSubject: {message.subject}")
    print(f"\nBody:\n{message.body}")
