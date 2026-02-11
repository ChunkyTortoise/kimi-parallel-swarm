"""
Slack & Discord Integration
Send notifications, alerts, and reports to team channels
"""
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
import requests
import json

logger = logging.getLogger(__name__)


class SlackIntegration:
    """Slack webhook integration for notifications."""
    
    def __init__(self, webhook_url: Optional[str] = None,
                 bot_token: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN")
        self.channel = os.getenv("SLACK_CHANNEL", "#outreach-alerts")
    
    def send_message(self, text: str, blocks: Optional[List[Dict]] = None) -> bool:
        """Send a message to Slack."""
        if not self.webhook_url:
            logger.warning("Slack webhook not configured")
            return False
        
        payload = {
            "text": text,
            "channel": self.channel,
            "username": "Kimi Agent Swarm",
            "icon_emoji": ":robot_face:"
        }
        
        if blocks:
            payload["blocks"] = blocks
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Slack send error: {e}")
            return False
    
    def send_campaign_complete(self, campaign_stats: Dict) -> bool:
        """Send campaign completion notification."""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎯 Campaign Complete",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Messages Sent:*\n{campaign_stats.get('messages_sent', 0)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Success Rate:*\n{campaign_stats.get('success_rate', 0):.1f}%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Replies:*\n{campaign_stats.get('replies', 0)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Meetings:*\n{campaign_stats.get('meetings', 0)}"
                    }
                ]
            }
        ]
        
        return self.send_message("Campaign completed", blocks)
    
    def send_daily_summary(self, report: Dict) -> bool:
        """Send daily performance summary."""
        summary = report.get("executive_summary", {})
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Daily Performance Summary",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Agents Active:*\n{summary.get('total_agents_active', 0)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Success Rate:*\n{summary.get('overall_success_rate', 0):.1f}%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Pipeline Health:*\n{summary.get('pipeline_health', 'unknown')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Campaigns:*\n{summary.get('campaign_performance', 'unknown')}"
                    }
                ]
            }
        ]
        
        # Add recommendations if any
        recommendations = report.get("recommendations", [])
        if recommendations:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Recommendations:*\n• " + "\n• ".join(recommendations[:3])
                }
            })
        
        return self.send_message("Daily summary", blocks)
    
    def send_alert(self, alert_type: str, message: str, 
                   severity: str = "warning") -> bool:
        """Send alert notification."""
        emoji_map = {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        color_map = {
            "critical": "#FF0000",
            "warning": "#FFA500",
            "info": "#0000FF"
        }
        
        emoji = emoji_map.get(severity, "⚠️")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {alert_type}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ]
        
        return self.send_message(f"{emoji} {alert_type}: {message}", blocks)


class DiscordIntegration:
    """Discord webhook integration for notifications."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
        self.username = "Kimi Agent Swarm"
    
    def send_message(self, content: str, embeds: Optional[List[Dict]] = None) -> bool:
        """Send a message to Discord."""
        if not self.webhook_url:
            logger.warning("Discord webhook not configured")
            return False
        
        payload = {
            "content": content,
            "username": self.username,
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
        }
        
        if embeds:
            payload["embeds"] = embeds
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return response.status_code == 204
        except Exception as e:
            logger.error(f"Discord send error: {e}")
            return False
    
    def send_campaign_complete(self, campaign_stats: Dict) -> bool:
        """Send campaign completion notification."""
        embed = {
            "title": "🎯 Campaign Complete",
            "color": 3066993,  # Green
            "fields": [
                {
                    "name": "Messages Sent",
                    "value": str(campaign_stats.get('messages_sent', 0)),
                    "inline": True
                },
                {
                    "name": "Success Rate",
                    "value": f"{campaign_stats.get('success_rate', 0):.1f}%",
                    "inline": True
                },
                {
                    "name": "Replies",
                    "value": str(campaign_stats.get('replies', 0)),
                    "inline": True
                },
                {
                    "name": "Meetings Booked",
                    "value": str(campaign_stats.get('meetings', 0)),
                    "inline": True
                }
            ],
            "timestamp": datetime.now().isoformat(),
            "footer": {
                "text": "Kimi Agent Swarm"
            }
        }
        
        return self.send_message("Campaign completed! 🎉", [embed])
    
    def send_daily_summary(self, report: Dict) -> bool:
        """Send daily performance summary."""
        summary = report.get("executive_summary", {})
        
        embed = {
            "title": "📊 Daily Performance Summary",
            "color": 3447003,  # Blue
            "fields": [
                {
                    "name": "Agents Active",
                    "value": str(summary.get('total_agents_active', 0)),
                    "inline": True
                },
                {
                    "name": "Success Rate",
                    "value": f"{summary.get('overall_success_rate', 0):.1f}%",
                    "inline": True
                },
                {
                    "name": "Pipeline Health",
                    "value": summary.get('pipeline_health', 'unknown'),
                    "inline": True
                },
                {
                    "name": "Campaign Performance",
                    "value": summary.get('campaign_performance', 'unknown'),
                    "inline": True
                }
            ],
            "timestamp": datetime.now().isoformat(),
            "footer": {
                "text": "Kimi Agent Swarm"
            }
        }
        
        # Add recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            rec_text = "\n".join([f"• {r}" for r in recommendations[:3]])
            embed["fields"].append({
                "name": "💡 Recommendations",
                "value": rec_text[:1024],  # Discord limit
                "inline": False
            })
        
        return self.send_message("Daily summary ready! 📈", [embed])
    
    def send_alert(self, alert_type: str, message: str,
                   severity: str = "warning") -> bool:
        """Send alert notification."""
        color_map = {
            "critical": 15158332,  # Red
            "warning": 16776960,   # Yellow
            "info": 3447003        # Blue
        }
        
        emoji_map = {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        embed = {
            "title": f"{emoji_map.get(severity, '⚠️')} {alert_type}",
            "description": message,
            "color": color_map.get(severity, 16776960),
            "timestamp": datetime.now().isoformat(),
            "footer": {
                "text": "Kimi Agent Swarm Alert"
            }
        }
        
        return self.send_message(f"Alert: {alert_type}", [embed])


class NotificationManager:
    """Manages notifications across multiple channels."""
    
    def __init__(self):
        self.slack = SlackIntegration()
        self.discord = DiscordIntegration()
        self.enabled_channels = []
        
        if self.slack.webhook_url:
            self.enabled_channels.append("slack")
        if self.discord.webhook_url:
            self.enabled_channels.append("discord")
    
    def notify_campaign_complete(self, stats: Dict) -> Dict[str, bool]:
        """Send campaign completion to all enabled channels."""
        results = {}
        
        if "slack" in self.enabled_channels:
            results["slack"] = self.slack.send_campaign_complete(stats)
        
        if "discord" in self.enabled_channels:
            results["discord"] = self.discord.send_campaign_complete(stats)
        
        return results
    
    def notify_daily_summary(self, report: Dict) -> Dict[str, bool]:
        """Send daily summary to all enabled channels."""
        results = {}
        
        if "slack" in self.enabled_channels:
            results["slack"] = self.slack.send_daily_summary(report)
        
        if "discord" in self.enabled_channels:
            results["discord"] = self.discord.send_daily_summary(report)
        
        return results
    
    def notify_alert(self, alert_type: str, message: str,
                    severity: str = "warning") -> Dict[str, bool]:
        """Send alert to all enabled channels."""
        results = {}
        
        if "slack" in self.enabled_channels:
            results["slack"] = self.slack.send_alert(alert_type, message, severity)
        
        if "discord" in self.enabled_channels:
            results["discord"] = self.discord.send_alert(alert_type, message, severity)
        
        return results
