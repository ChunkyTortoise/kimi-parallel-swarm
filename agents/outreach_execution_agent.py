"""
Outreach Execution Agent
Automates connection requests, DM sends, follow-ups, and multi-channel sequencing.
"""
import json
import logging
import random
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class OutreachStatus(Enum):
    CONNECTION_SENT = "connection_sent"
    CONNECTION_ACCEPTED = "connection_accepted"
    DM_SENT = "dm_sent"
    REPLIED = "replied"
    FOLLOWUP_1 = "followup_1_sent"
    FOLLOWUP_2 = "followup_2_sent"
    FOLLOWUP_3 = "followup_3_sent"
    COLD = "cold_no_response"
    QUALIFIED = "qualified"
    DISCOVERY_BOOKED = "discovery_booked"


@dataclass
class OutreachAction:
    prospect_id: str
    action_type: str
    channel: str
    content: str
    scheduled_time: datetime
    status: str = "pending"
    executed_at: Optional[datetime] = None
    response: Optional[str] = None


class OutreachExecutionAgent:
    """Agent for executing outreach safely across channels."""
    
    def __init__(self, config: Dict, crm_agent=None):
        self.config = config
        self.crm_agent = crm_agent
        self.daily_connections = 0
        self.weekly_connections = 0
        self.daily_messages = 0
        self.last_reset = datetime.now()
        
        # Safety limits
        self.max_daily_connections = config.get("daily_limits", {}).get("connections", 20)
        self.max_weekly_connections = config.get("safety", {}).get("weekly_connection_limit", 100)
        self.max_daily_messages = config.get("daily_limits", {}).get("messages", 20)
        self.min_delay = config.get("safety", {}).get("min_delay_seconds", 300)
        self.max_delay = config.get("safety", {}).get("max_delay_seconds", 900)
        
        # Queue for scheduled actions
        self.action_queue: List[OutreachAction] = []
        
    def _check_and_reset_limits(self):
        """Check if daily/weekly limits need reset."""
        now = datetime.now()
        
        # Reset daily counter
        if (now - self.last_reset).days >= 1:
            self.daily_connections = 0
            self.daily_messages = 0
            self.last_reset = now
            logger.info("Daily outreach limits reset")
    
    def _calculate_delay(self) -> int:
        """Calculate random delay between actions."""
        return random.randint(self.min_delay, self.max_delay)
    
    def _can_send_connection(self) -> bool:
        """Check if connection request can be sent safely."""
        self._check_and_reset_limits()
        return (self.daily_connections < self.max_daily_connections and 
                self.weekly_connections < self.max_weekly_connections)
    
    def _can_send_message(self) -> bool:
        """Check if DM can be sent safely."""
        self._check_and_reset_limits()
        return self.daily_messages < self.max_daily_messages
    
    def schedule_connection_request(self, prospect: Dict, message: str) -> Optional[OutreachAction]:
        """Schedule a connection request with safety delays."""
        if not self._can_send_connection():
            logger.warning(f"Connection limit reached for {prospect.get('name')}")
            return None
        
        # Calculate optimal send time (spread throughout day)
        # Slots: 9am, 12pm, 3pm, 6pm
        slots = [9, 12, 15, 18]
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Find next available slot
        current_hour = datetime.now().hour
        available_slots = [s for s in slots if s > current_hour]
        
        if not available_slots:
            # Schedule for tomorrow
            send_time = today + timedelta(days=1, hours=slots[0])
        else:
            send_time = today + timedelta(hours=available_slots[0])
        
        # Add random minute offset
        send_time += timedelta(minutes=random.randint(0, 30))
        
        action = OutreachAction(
            prospect_id=prospect.get("prospect_id"),
            action_type="connection_request",
            channel="LinkedIn",
            content=message,
            scheduled_time=send_time
        )
        
        self.action_queue.append(action)
        self.daily_connections += 1
        self.weekly_connections += 1
        
        logger.info(f"Scheduled connection request to {prospect.get('name')} at {send_time}")
        return action
    
    def schedule_dm(self, prospect: Dict, message: str, delay_hours: int = 0) -> OutreachAction:
        """Schedule a DM to be sent."""
        if not self._can_send_message():
            logger.warning(f"DM limit reached for {prospect.get('name')}")
            return None
        
        send_time = datetime.now() + timedelta(hours=delay_hours, minutes=random.randint(0, 30))
        
        action = OutreachAction(
            prospect_id=prospect.get("prospect_id"),
            action_type="dm",
            channel="LinkedIn",
            content=message,
            scheduled_time=send_time
        )
        
        self.action_queue.append(action)
        self.daily_messages += 1
        
        logger.info(f"Scheduled DM to {prospect.get('name')} at {send_time}")
        return action
    
    def execute_scheduled_actions(self) -> List[Dict]:
        """Execute actions that are due."""
        now = datetime.now()
        executed = []
        
        for action in self.action_queue[:]:
            if action.scheduled_time <= now and action.status == "pending":
                result = self._execute_action(action)
                if result:
                    executed.append(result)
                self.action_queue.remove(action)
                
                # Add delay between executions
                time.sleep(random.randint(5, 15))
        
        return executed
    
    def _execute_action(self, action: OutreachAction) -> Optional[Dict]:
        """Execute a single outreach action."""
        action.executed_at = datetime.now()
        
        try:
            if action.action_type == "connection_request":
                result = self._send_connection_request(action)
            elif action.action_type == "dm":
                result = self._send_dm(action)
            elif action.action_type == "followup":
                result = self._send_followup(action)
            elif action.action_type == "email":
                result = self._send_email(action)
            else:
                result = None
            
            action.status = "completed" if result else "failed"
            
            # Update CRM
            if self.crm_agent and result:
                self.crm_agent.log_outreach_action(action.prospect_id, action.action_type, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing action {action.action_type}: {e}")
            action.status = "failed"
            return None
    
    def _send_connection_request(self, action: OutreachAction) -> Dict:
        """Send LinkedIn connection request."""
        # In production, integrate with Phantombuster or LinkedIn API
        # This is a simulation
        logger.info(f"[SIMULATED] Connection request sent to {action.prospect_id}")
        return {
            "prospect_id": action.prospect_id,
            "action": "connection_request_sent",
            "channel": "LinkedIn",
            "timestamp": datetime.now().isoformat(),
            "message_preview": action.content[:50] + "..."
        }
    
    def _send_dm(self, action: OutreachAction) -> Dict:
        """Send LinkedIn DM."""
        logger.info(f"[SIMULATED] DM sent to {action.prospect_id}")
        return {
            "prospect_id": action.prospect_id,
            "action": "dm_sent",
            "channel": "LinkedIn",
            "timestamp": datetime.now().isoformat()
        }
    
    def _send_followup(self, action: OutreachAction) -> Dict:
        """Send follow-up message."""
        logger.info(f"[SIMULATED] Follow-up sent to {action.prospect_id}")
        return {
            "prospect_id": action.prospect_id,
            "action": "followup_sent",
            "channel": "LinkedIn",
            "timestamp": datetime.now().isoformat()
        }
    
    def _send_email(self, action: OutreachAction) -> Dict:
        """Send cold email."""
        # Integrate with SendGrid or SMTP
        logger.info(f"[SIMULATED] Email sent to {action.prospect_id}")
        return {
            "prospect_id": action.prospect_id,
            "action": "email_sent",
            "channel": "Email",
            "timestamp": datetime.now().isoformat()
        }
    
    def process_incoming_replies(self, replies: List[Dict]) -> List[Dict]:
        """Process incoming message replies."""
        processed = []
        
        for reply in replies:
            try:
                prospect_id = reply.get("prospect_id")
                message = reply.get("message", "").lower()
                
                # Analyze sentiment
                positive_indicators = ["interested", "yes", "sure", "book", "schedule", "call", "chat", "tell me more"]
                negative_indicators = ["no", "not interested", "unsubscribe", "stop", "remove"]
                
                sentiment = "neutral"
                if any(ind in message for ind in positive_indicators):
                    sentiment = "positive"
                elif any(ind in message for ind in negative_indicators):
                    sentiment = "negative"
                
                result = {
                    "prospect_id": prospect_id,
                    "action": "reply_received",
                    "sentiment": sentiment,
                    "timestamp": datetime.now().isoformat(),
                    "requires_response": sentiment == "positive"
                }
                
                processed.append(result)
                
                # Update CRM
                if self.crm_agent:
                    self.crm_agent.update_status(prospect_id, "replied")
                    if sentiment == "positive":
                        self.crm_agent.update_status(prospect_id, "qualified")
                
            except Exception as e:
                logger.error(f"Error processing reply: {e}")
        
        return processed
    
    def setup_followup_sequence(self, prospect: Dict) -> List[OutreachAction]:
        """Setup 4-touch follow-up sequence."""
        actions = []
        base_time = datetime.now()
        
        # Touch 1: Initial DM (already scheduled separately)
        # Touch 2: Day 3 follow-up
        actions.append(OutreachAction(
            prospect_id=prospect.get("prospect_id"),
            action_type="followup",
            channel="LinkedIn",
            content="Day 3 follow-up",
            scheduled_time=base_time + timedelta(days=3, hours=random.randint(9, 17))
        ))
        
        # Touch 3: Day 7 value-add
        actions.append(OutreachAction(
            prospect_id=prospect.get("prospect_id"),
            action_type="followup",
            channel="LinkedIn",
            content="Day 7 value-add follow-up",
            scheduled_time=base_time + timedelta(days=7, hours=random.randint(9, 17))
        ))
        
        # Touch 4: Day 14 final attempt (email if available)
        channel = "Email" if prospect.get("email") else "LinkedIn"
        actions.append(OutreachAction(
            prospect_id=prospect.get("prospect_id"),
            action_type="followup",
            channel=channel,
            content="Day 14 final follow-up",
            scheduled_time=base_time + timedelta(days=14, hours=random.randint(9, 17))
        ))
        
        self.action_queue.extend(actions)
        logger.info(f"Setup 3 follow-ups for {prospect.get('name')}")
        return actions
    
    def get_daily_stats(self) -> Dict:
        """Get daily outreach statistics."""
        self._check_and_reset_limits()
        return {
            "connections_sent_today": self.daily_connections,
            "connections_limit": self.max_daily_connections,
            "messages_sent_today": self.daily_messages,
            "messages_limit": self.max_daily_messages,
            "weekly_connections": self.weekly_connections,
            "weekly_limit": self.max_weekly_connections,
            "queue_length": len(self.action_queue)
        }


if __name__ == "__main__":
    config = {
        "daily_limits": {"connections": 20, "messages": 20},
        "safety": {"weekly_connection_limit": 100, "min_delay_seconds": 300, "max_delay_seconds": 900}
    }
    
    agent = OutreachExecutionAgent(config)
    
    # Test scheduling
    test_prospect = {"prospect_id": "test123", "name": "John Doe", "email": "john@test.com"}
    message = "Hi John, I'd love to connect!"
    
    action = agent.schedule_connection_request(test_prospect, message)
    if action:
        print(f"Scheduled: {action}")
    
    print(f"\nDaily stats: {agent.get_daily_stats()}")
