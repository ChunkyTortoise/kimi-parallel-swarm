"""
Email Automation Agent
Sends personalized cold emails via SendGrid/SES with tracking
"""
import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


@dataclass
class EmailCampaign:
    """Represents an email campaign."""
    campaign_id: str
    name: str
    subject_template: str
    body_template: str
    prospects: List[Dict]
    scheduled_time: Optional[datetime] = None
    status: str = "draft"  # draft, scheduled, sending, complete


@dataclass
class EmailResult:
    """Result of sending an email."""
    prospect_id: str
    email: str
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    sent_at: Optional[datetime] = None
    opened: bool = False
    clicked: bool = False


class EmailAutomationAgent:
    """
    Agent for automating personalized email outreach.
    
    Features:
    - SendGrid/AWS SES integration
    - Template-based personalization
    - Rate limiting and scheduling
    - Open/click tracking
    - Bounce handling
    """
    
    def __init__(self, sendgrid_api_key: Optional[str] = None,
                 aws_access_key: Optional[str] = None,
                 aws_secret_key: Optional[str] = None,
                 sender_email: str = ""):
        self.sendgrid_api_key = sendgrid_api_key or os.getenv("SENDGRID_API_KEY")
        self.aws_access_key = aws_access_key or os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = aws_secret_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        self.sender_email = sender_email or os.getenv("SENDER_EMAIL", "outreach@company.com")
        
        self.daily_sent = 0
        self.daily_limit = int(os.getenv("DAILY_EMAIL_LIMIT", "100"))
        self.last_reset = datetime.now()
        
        self._init_clients()
    
    def _init_clients(self):
        """Initialize email service clients."""
        self.sendgrid_client = None
        self.ses_client = None
        
        if self.sendgrid_api_key:
            try:
                from sendgrid import SendGridAPIClient
                self.sendgrid_client = SendGridAPIClient(self.sendgrid_api_key)
                logger.info("SendGrid client initialized")
            except ImportError:
                logger.warning("SendGrid package not installed")
        
        if self.aws_access_key and self.aws_secret_key:
            try:
                import boto3
                self.ses_client = boto3.client(
                    'ses',
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    region_name='us-east-1'
                )
                logger.info("AWS SES client initialized")
            except ImportError:
                logger.warning("Boto3 package not installed")
    
    def _reset_daily_counter(self):
        """Reset daily send counter."""
        now = datetime.now()
        if now.date() > self.last_reset.date():
            self.daily_sent = 0
            self.last_reset = now
    
    def _check_rate_limit(self) -> bool:
        """Check if we can send more emails today."""
        self._reset_daily_counter()
        return self.daily_sent < self.daily_limit
    
    def personalize_template(self, template: str, prospect: Dict) -> str:
        """Personalize email template with prospect data."""
        result = template
        
        # Replace variables
        variables = {
            "{{first_name}}": prospect.get("first_name", ""),
            "{{last_name}}": prospect.get("last_name", ""),
            "{{company}}": prospect.get("company", ""),
            "{{title}}": prospect.get("title", ""),
            "{{industry}}": prospect.get("industry", ""),
            "{{pain_point}}": prospect.get("pain_point", ""),
            "{{custom_hook}}": prospect.get("custom_hook", ""),
        }
        
        for var, value in variables.items():
            result = result.replace(var, str(value))
        
        return result
    
    def send_email_sendgrid(self, to_email: str, subject: str, 
                          body: str, prospect_id: str) -> EmailResult:
        """Send email via SendGrid."""
        if not self.sendgrid_client:
            return EmailResult(
                prospect_id=prospect_id,
                email=to_email,
                success=False,
                error="SendGrid not configured"
            )
        
        try:
            from sendgrid.helpers.mail import Mail
            
            message = Mail(
                from_email=self.sender_email,
                to_emails=to_email,
                subject=subject,
                html_content=body
            )
            
            response = self.sendgrid_client.send(message)
            
            self.daily_sent += 1
            
            return EmailResult(
                prospect_id=prospect_id,
                email=to_email,
                success=response.status_code == 202,
                message_id=response.headers.get('X-Message-Id'),
                sent_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            return EmailResult(
                prospect_id=prospect_id,
                email=to_email,
                success=False,
                error=str(e)
            )
    
    def send_email_ses(self, to_email: str, subject: str,
                      body: str, prospect_id: str) -> EmailResult:
        """Send email via AWS SES."""
        if not self.ses_client:
            return EmailResult(
                prospect_id=prospect_id,
                email=to_email,
                success=False,
                error="AWS SES not configured"
            )
        
        try:
            response = self.ses_client.send_email(
                Source=self.sender_email,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {
                        'Html': {'Data': body}
                    }
                }
            )
            
            self.daily_sent += 1
            
            return EmailResult(
                prospect_id=prospect_id,
                email=to_email,
                success=True,
                message_id=response['MessageId'],
                sent_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"SES error: {e}")
            return EmailResult(
                prospect_id=prospect_id,
                email=to_email,
                success=False,
                error=str(e)
            )
    
    def send_single_email(self, prospect: Dict, subject_template: str,
                         body_template: str) -> EmailResult:
        """Send a single personalized email."""
        if not self._check_rate_limit():
            return EmailResult(
                prospect_id=prospect.get("id", ""),
                email=prospect.get("email", ""),
                success=False,
                error="Daily limit reached"
            )
        
        # Personalize
        subject = self.personalize_template(subject_template, prospect)
        body = self.personalize_template(body_template, prospect)
        
        # Add tracking pixel (optional)
        tracking_id = prospect.get("id", "")
        tracking_pixel = f'<img src="https://tracker.example.com/pixel/{tracking_id}" width="1" height="1" />'
        body += tracking_pixel
        
        # Send via preferred method
        to_email = prospect.get("email", "")
        prospect_id = prospect.get("id", "")
        
        if self.sendgrid_client:
            return self.send_email_sendgrid(to_email, subject, body, prospect_id)
        elif self.ses_client:
            return self.send_email_ses(to_email, subject, body, prospect_id)
        else:
            # Simulation mode
            logger.info(f"[SIMULATION] Would send to {to_email}: {subject}")
            self.daily_sent += 1
            return EmailResult(
                prospect_id=prospect_id,
                email=to_email,
                success=True,
                message_id="simulated",
                sent_at=datetime.now()
            )
    
    def send_campaign(self, campaign: EmailCampaign,
                     delay_seconds: int = 30) -> List[EmailResult]:
        """Send a campaign to multiple prospects with delays."""
        results = []
        
        for prospect in campaign.prospects:
            # Check rate limit
            if not self._check_rate_limit():
                logger.warning("Daily limit reached, stopping campaign")
                break
            
            # Send email
            result = self.send_single_email(
                prospect,
                campaign.subject_template,
                campaign.body_template
            )
            results.append(result)
            
            if result.success:
                logger.info(f"✅ Sent to {prospect.get('email')}")
            else:
                logger.error(f"❌ Failed to send to {prospect.get('email')}: {result.error}")
            
            # Rate limiting delay
            if delay_seconds > 0:
                time.sleep(delay_seconds)
        
        return results
    
    def get_campaign_stats(self, results: List[EmailResult]) -> Dict:
        """Get statistics for a campaign."""
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        
        return {
            "total_sent": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "daily_remaining": self.daily_limit - self.daily_sent
        }
    
    def validate_email_list(self, prospects: List[Dict]) -> List[Dict]:
        """Validate and clean email list."""
        import re
        
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        valid = []
        for prospect in prospects:
            email = prospect.get("email", "")
            if email_pattern.match(email):
                valid.append(prospect)
            else:
                logger.warning(f"Invalid email: {email}")
        
        return valid
