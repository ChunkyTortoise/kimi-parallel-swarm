"""
Zapier & Make.com Integration
Webhook triggers for automation workflows
"""
import os
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import asdict
from datetime import datetime
import requests
import json
import hmac
import hashlib

logger = logging.getLogger(__name__)


class WebhookManager:
    """Manages webhooks for Zapier, Make.com, and custom endpoints."""
    
    def __init__(self, zapier_webhook: Optional[str] = None,
                 make_webhook: Optional[str] = None):
        self.zapier_webhook = zapier_webhook or os.getenv("ZAPIER_WEBHOOK_URL")
        self.make_webhook = make_webhook or os.getenv("MAKE_WEBHOOK_URL")
        self.secret_key = os.getenv("WEBHOOK_SECRET", "default-secret")
        
        self.event_handlers: Dict[str, List[Callable]] = {}
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register a handler for a specific event type."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def _generate_signature(self, payload: str) -> str:
        """Generate HMAC signature for webhook security."""
        return hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _send_webhook(self, url: str, payload: Dict, 
                     headers: Optional[Dict] = None) -> bool:
        """Send webhook payload to URL."""
        if not url:
            return False
        
        default_headers = {
            "Content-Type": "application/json",
            "X-Webhook-Source": "kimi-agent-swarm",
            "X-Webhook-Timestamp": datetime.now().isoformat()
        }
        
        # Add signature for security
        payload_str = json.dumps(payload, default=str)
        default_headers["X-Webhook-Signature"] = self._generate_signature(payload_str)
        
        if headers:
            default_headers.update(headers)
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=default_headers,
                timeout=30
            )
            return response.status_code in [200, 201, 202, 204]
        except Exception as e:
            logger.error(f"Webhook send error: {e}")
            return False
    
    def trigger_event(self, event_type: str, data: Dict) -> Dict[str, bool]:
        """Trigger an event across all configured webhooks."""
        results = {}
        
        # Build payload
        payload = {
            "event": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # Send to Zapier
        if self.zapier_webhook:
            results["zapier"] = self._send_webhook(
                self.zapier_webhook,
                payload,
                {"X-Event-Type": event_type}
            )
        
        # Send to Make.com
        if self.make_webhook:
            results["make"] = self._send_webhook(
                self.make_webhook,
                payload,
                {"X-Event-Type": event_type}
            )
        
        # Call local handlers
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Handler error: {e}")
        
        return results
    
    def on_prospect_qualified(self, prospect: Dict):
        """Trigger when a prospect is qualified."""
        return self.trigger_event("prospect.qualified", {
            "prospect_id": prospect.get("id"),
            "first_name": prospect.get("first_name"),
            "last_name": prospect.get("last_name"),
            "company": prospect.get("company"),
            "email": prospect.get("email"),
            "quality_score": prospect.get("quality_score"),
            "linkedin_url": prospect.get("linkedin_url"),
            "source": prospect.get("source", "icp_research")
        })
    
    def on_message_sent(self, message_data: Dict):
        """Trigger when a message is sent."""
        return self.trigger_event("message.sent", {
            "message_id": message_data.get("message_id"),
            "prospect_id": message_data.get("prospect_id"),
            "platform": message_data.get("platform"),  # linkedin, email
            "message_type": message_data.get("type"),
            "sent_at": datetime.now().isoformat()
        })
    
    def on_message_replied(self, reply_data: Dict):
        """Trigger when a reply is received."""
        return self.trigger_event("message.replied", {
            "message_id": reply_data.get("message_id"),
            "prospect_id": reply_data.get("prospect_id"),
            "platform": reply_data.get("platform"),
            "reply_text": reply_data.get("text", "")[:500],  # Truncate
            "sentiment": reply_data.get("sentiment", "neutral"),
            "replied_at": datetime.now().isoformat()
        })
    
    def on_meeting_booked(self, meeting_data: Dict):
        """Trigger when a meeting is booked."""
        return self.trigger_event("meeting.booked", {
            "meeting_id": meeting_data.get("id"),
            "prospect_id": meeting_data.get("prospect_id"),
            "prospect_name": meeting_data.get("prospect_name"),
            "company": meeting_data.get("company"),
            "meeting_time": meeting_data.get("scheduled_time"),
            "calendar_link": meeting_data.get("calendar_link"),
            "platform": meeting_data.get("platform", "calendly")
        })
    
    def on_deal_stage_changed(self, deal_data: Dict):
        """Trigger when a deal moves stages."""
        return self.trigger_event("deal.stage_changed", {
            "deal_id": deal_data.get("id"),
            "prospect_id": deal_data.get("prospect_id"),
            "previous_stage": deal_data.get("from_stage"),
            "new_stage": deal_data.get("to_stage"),
            "deal_value": deal_data.get("value", 0),
            "probability": deal_data.get("probability", 0)
        })
    
    def on_campaign_complete(self, campaign_stats: Dict):
        """Trigger when a campaign finishes."""
        return self.trigger_event("campaign.complete", {
            "campaign_id": campaign_stats.get("campaign_id"),
            "total_sent": campaign_stats.get("messages_sent", 0),
            "successful": campaign_stats.get("successful", 0),
            "replies": campaign_stats.get("replies", 0),
            "meetings": campaign_stats.get("meetings", 0),
            "duration_seconds": campaign_stats.get("duration", 0)
        })
    
    def on_daily_report(self, report_data: Dict):
        """Trigger daily report event."""
        return self.trigger_event("report.daily", {
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "agents_active": report_data.get("total_agents_active", 0),
            "success_rate": report_data.get("overall_success_rate", 0),
            "pipeline_value": report_data.get("pipeline_value", 0),
            "new_prospects": report_data.get("new_prospects", 0),
            "recommendations": report_data.get("recommendations", [])
        })
    
    def on_anomaly_detected(self, anomaly_data: Dict):
        """Trigger when anomaly is detected."""
        return self.trigger_event("anomaly.detected", {
            "metric": anomaly_data.get("metric"),
            "current_value": anomaly_data.get("current"),
            "expected_value": anomaly_data.get("average"),
            "deviation": anomaly_data.get("deviation"),
            "severity": anomaly_data.get("severity"),
            "timestamp": datetime.now().isoformat()
        })


class ZapierFormatter:
    """Format data specifically for Zapier consumption."""
    
    @staticmethod
    def format_prospect(prospect: Dict) -> Dict:
        """Format prospect data for Zapier."""
        return {
            "id": prospect.get("id"),
            "first_name": prospect.get("first_name"),
            "last_name": prospect.get("last_name"),
            "full_name": f"{prospect.get('first_name', '')} {prospect.get('last_name', '')}".strip(),
            "email": prospect.get("email"),
            "company": prospect.get("company"),
            "title": prospect.get("title"),
            "linkedin_url": prospect.get("linkedin_url"),
            "company_size": prospect.get("company_size"),
            "industry": prospect.get("industry"),
            "quality_score": prospect.get("quality_score"),
            "source": prospect.get("source"),
            "created_at": prospect.get("created_at")
        }
    
    @staticmethod
    def format_campaign_stats(stats: Dict) -> Dict:
        """Format campaign stats for Zapier."""
        return {
            "campaign_id": stats.get("campaign_id"),
            "campaign_name": stats.get("name"),
            "total_messages": stats.get("messages_sent", 0),
            "delivered": stats.get("delivered", 0),
            "replies": stats.get("replies", 0),
            "meetings": stats.get("meetings", 0),
            "success_rate_percent": round(stats.get("success_rate", 0), 2),
            "reply_rate_percent": round(stats.get("reply_rate", 0), 2),
            "duration_minutes": round(stats.get("duration", 0) / 60, 2)
        }
    
    @staticmethod
    def format_deal(deal: Dict) -> Dict:
        """Format deal data for Zapier."""
        return {
            "deal_id": deal.get("id"),
            "deal_name": deal.get("name"),
            "prospect_name": deal.get("prospect_name"),
            "company": deal.get("company"),
            "stage": deal.get("stage"),
            "value": deal.get("value", 0),
            "probability": deal.get("probability", 0),
            "expected_close": deal.get("expected_close_date"),
            "created_at": deal.get("created_at")
        }


class MakeFormatter:
    """Format data specifically for Make.com (Integromat) consumption."""
    
    @staticmethod
    def format_bundle(data: Dict, bundle_type: str) -> List[Dict]:
        """Format data as Make.com bundle structure."""
        # Make.com uses bundles (arrays) for data
        return [{
            "__IMTINDEX__": 1,
            "__IMTLENGTH__": 1,
            "type": bundle_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }]


# Example usage
if __name__ == "__main__":
    # Initialize webhook manager
    webhooks = WebhookManager()
    
    # Example: Trigger prospect qualified
    prospect = {
        "id": "123",
        "first_name": "John",
        "last_name": "Doe",
        "company": "Acme Inc",
        "email": "john@acme.com",
        "quality_score": 9.5
    }
    
    results = webhooks.on_prospect_qualified(prospect)
    print(f"Webhook results: {results}")
