"""
Sentiment Analysis Agent
Analyzes prospect replies, social mentions, and market sentiment
"""
import os
import logging
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass
from datetime import datetime
import re

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    text: str
    sentiment: Literal["positive", "neutral", "negative"]
    confidence: float  # 0-1
    score: float  # -1 to 1
    key_phrases: List[str]
    urgency_level: Literal["low", "medium", "high"]
    intent: Optional[str] = None  # buying, researching, complaining, etc.


class SentimentAnalysisAgent:
    """
    Agent for analyzing sentiment in prospect communications.
    
    Features:
    - Analyze reply sentiment (positive/neutral/negative)
    - Detect buying signals
    - Identify objections and concerns
    - Prioritize responses by urgency
    - Track sentiment trends over time
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MOONSHOT_API_KEY")
        
        # Sentiment keywords
        self.positive_indicators = [
            "interested", "love", "great", "perfect", "awesome", "amazing",
            "exactly", "definitely", "absolutely", "yes", "sure", "ok",
            "sounds good", "let's do it", "i'm in", "excited", "looking forward",
            "book a call", "schedule", "meeting", "demo", "trial", "pricing"
        ]
        
        self.negative_indicators = [
            "not interested", "no thanks", "unsubscribe", "spam", "annoying",
            "too expensive", "not now", "maybe later", "not the right time",
            "already have", "using competitor", "don't need", "stop"
        ]
        
        self.buying_signals = [
            "pricing", "cost", "budget", "roi", "implementation", "onboarding",
            "contract", "terms", "trial", "demo", "features", "integration",
            "setup", "deployment", "team", "users", "seats", "license"
        ]
        
        self.urgency_indicators = [
            "asap", "urgent", "this week", "today", "tomorrow", "immediately",
            "quickly", "fast", "rush", "deadline", "quarter", "end of month"
        ]
    
    def analyze_text(self, text: str, context: str = "reply") -> SentimentResult:
        """Analyze sentiment of a text."""
        text_lower = text.lower()
        
        # Calculate sentiment score
        positive_count = sum(1 for word in self.positive_indicators if word in text_lower)
        negative_count = sum(1 for word in self.negative_indicators if word in text_lower)
        
        # Normalize score (-1 to 1)
        total = positive_count + negative_count
        if total == 0:
            score = 0.0
        else:
            score = (positive_count - negative_count) / total
        
        # Determine sentiment category
        if score > 0.2:
            sentiment = "positive"
        elif score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Calculate confidence
        confidence = min(0.95, 0.5 + (abs(score) * 0.5) + (total * 0.05))
        
        # Extract key phrases
        key_phrases = self._extract_key_phrases(text)
        
        # Determine urgency
        urgency = self._detect_urgency(text_lower)
        
        # Detect intent
        intent = self._detect_intent(text_lower)
        
        return SentimentResult(
            text=text,
            sentiment=sentiment,
            confidence=confidence,
            score=score,
            key_phrases=key_phrases,
            urgency_level=urgency,
            intent=intent
        )
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text."""
        # Simple extraction - in production would use NLP
        phrases = []
        
        # Look for quoted phrases
        quotes = re.findall(r'"([^"]*)"', text)
        phrases.extend(quotes)
        
        # Look for key terms
        key_terms = [
            "analytics", "dashboard", "automation", "integration",
            "reporting", "roi", "efficiency", "productivity"
        ]
        
        text_lower = text.lower()
        for term in key_terms:
            if term in text_lower:
                phrases.append(term)
        
        return list(set(phrases))[:5]  # Return top 5 unique
    
    def _detect_urgency(self, text_lower: str) -> Literal["low", "medium", "high"]:
        """Detect urgency level in text."""
        urgency_count = sum(1 for word in self.urgency_indicators if word in text_lower)
        
        if urgency_count >= 2:
            return "high"
        elif urgency_count == 1:
            return "medium"
        return "low"
    
    def _detect_intent(self, text_lower: str) -> Optional[str]:
        """Detect prospect intent."""
        # Check for buying signals
        buying_matches = sum(1 for word in self.buying_signals if word in text_lower)
        if buying_matches >= 2:
            return "buying"
        
        # Check for objections
        if any(word in text_lower for word in ["too expensive", "no budget", "can't afford"]):
            return "price_objection"
        
        # Check for research
        if any(word in text_lower for word in ["researching", "comparing", "evaluating", "options"]):
            return "researching"
        
        # Check for referral
        if any(word in text_lower for word in ["colleague", "team", "manager", "decision maker"]):
            return "referral_needed"
        
        return None
    
    def analyze_conversation(self, messages: List[Dict]) -> Dict:
        """Analyze sentiment across an entire conversation."""
        results = []
        
        for msg in messages:
            result = self.analyze_text(
                msg.get("text", ""),
                msg.get("context", "reply")
            )
            results.append({
                "timestamp": msg.get("timestamp"),
                "sender": msg.get("sender"),
                "sentiment": result.sentiment,
                "score": result.score,
                "urgency": result.urgency_level,
                "intent": result.intent
            })
        
        # Calculate trends
        if results:
            avg_score = sum(r["score"] for r in results) / len(results)
            positive_ratio = sum(1 for r in results if r["sentiment"] == "positive") / len(results)
            
            # Detect trend
            if len(results) >= 2:
                first_half = sum(r["score"] for r in results[:len(results)//2]) / (len(results)//2)
                second_half = sum(r["score"] for r in results[len(results)//2:]) / (len(results) - len(results)//2)
                trend = "improving" if second_half > first_half else "declining" if second_half < first_half else "stable"
            else:
                trend = "insufficient_data"
        else:
            avg_score = 0
            positive_ratio = 0
            trend = "no_data"
        
        return {
            "message_count": len(results),
            "average_sentiment_score": round(avg_score, 2),
            "positive_message_ratio": round(positive_ratio, 2),
            "trend": trend,
            "highest_urgency": max((r["urgency"] for r in results), default="low"),
            "buying_signals_detected": sum(1 for r in results if r["intent"] == "buying"),
            "detailed_results": results
        }
    
    def prioritize_responses(self, replies: List[Dict]) -> List[Dict]:
        """Prioritize prospect replies by urgency and sentiment."""
        analyzed = []
        
        for reply in replies:
            sentiment = self.analyze_text(reply.get("text", ""))
            
            # Calculate priority score
            priority = 0
            
            # Urgency points
            if sentiment.urgency_level == "high":
                priority += 30
            elif sentiment.urgency_level == "medium":
                priority += 15
            
            # Sentiment points (prioritize positive)
            if sentiment.sentiment == "positive":
                priority += 25
            elif sentiment.sentiment == "neutral":
                priority += 10
            
            # Intent points
            if sentiment.intent == "buying":
                priority += 40
            elif sentiment.intent == "referral_needed":
                priority += 20
            
            analyzed.append({
                **reply,
                "sentiment_analysis": sentiment,
                "priority_score": priority,
                "priority_label": "high" if priority >= 50 else "medium" if priority >= 25 else "low"
            })
        
        # Sort by priority
        return sorted(analyzed, key=lambda x: x["priority_score"], reverse=True)
    
    def detect_at_risk_prospects(self, conversations: List[List[Dict]]) -> List[Dict]:
        """Identify prospects showing negative sentiment trends."""
        at_risk = []
        
        for conversation in conversations:
            if not conversation:
                continue
            
            analysis = self.analyze_conversation(conversation)
            
            # Risk factors
            if analysis["trend"] == "declining":
                at_risk.append({
                    "prospect_id": conversation[0].get("prospect_id"),
                    "reason": "sentiment_declining",
                    "current_score": analysis["average_sentiment_score"],
                    "recommendation": "Personal outreach from senior team member",
                    "urgency": "high"
                })
            elif analysis["average_sentiment_score"] < -0.3:
                at_risk.append({
                    "prospect_id": conversation[0].get("prospect_id"),
                    "reason": "consistently_negative",
                    "current_score": analysis["average_sentiment_score"],
                    "recommendation": "Address concerns directly, offer value",
                    "urgency": "high"
                })
        
        return at_risk
    
    def generate_sentiment_report(self, period_days: int = 7) -> Dict:
        """Generate sentiment analysis report."""
        return {
            "period": f"Last {period_days} days",
            "summary": {
                "total_analyzed": 0,
                "positive_percentage": 0,
                "neutral_percentage": 0,
                "negative_percentage": 0,
                "buying_signals": 0,
                "urgent_responses_needed": 0
            },
            "trends": [],
            "recommendations": []
        }
