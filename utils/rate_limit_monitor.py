"""
Rate Limit Monitor
Track LinkedIn and API usage to prevent account restrictions
"""
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


@dataclass
class RateLimitEvent:
    timestamp: str
    event_type: str  # 'connection', 'message', 'api_call'
    platform: str    # 'linkedin', 'moonshot', 'phantombuster'
    status: str      # 'success', 'rate_limited', 'error'
    details: str


class RateLimitMonitor:
    """Monitor rate limits across all platforms."""
    
    # Safety thresholds
    LINKEDIN_DAILY_CONNECTIONS = 20
    LINKEDIN_WEEKLY_CONNECTIONS = 100
    LINKEDIN_DAILY_MESSAGES = 20
    MOONSHOT_DAILY_TOKENS = 1000000  # 1M tokens
    
    def __init__(self, log_file: str = "data/rate_limits.json"):
        self.log_file = Path(log_file)
        self.events: List[RateLimitEvent] = []
        self._load_events()
    
    def _load_events(self):
        """Load event history."""
        if self.log_file.exists():
            with open(self.log_file) as f:
                data = json.load(f)
                self.events = [RateLimitEvent(**e) for e in data.get('events', [])]
    
    def _save_events(self):
        """Save event history."""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'w') as f:
            json.dump({
                'events': [asdict(e) for e in self.events[-1000:]]  # Keep last 1000
            }, f, indent=2)
    
    def log_event(self, event_type: str, platform: str, status: str, details: str = ""):
        """Log a rate limit event."""
        event = RateLimitEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            platform=platform,
            status=status,
            details=details
        )
        self.events.append(event)
        self._save_events()
    
    def get_linkedin_usage(self, hours: int = 24) -> Dict:
        """Get LinkedIn usage for the past N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        events = [
            e for e in self.events
            if e.platform == 'linkedin'
            and datetime.fromisoformat(e.timestamp) > cutoff
        ]
        
        connections = len([e for e in events if e.event_type == 'connection'])
        messages = len([e for e in events if e.event_type == 'message'])
        errors = len([e for e in events if e.status == 'error'])
        
        # Calculate remaining limits
        if hours >= 24:
            remaining_connections = self.LINKEDIN_DAILY_CONNECTIONS - connections
            remaining_messages = self.LINKEDIN_DAILY_MESSAGES - messages
        else:
            remaining_connections = None
            remaining_messages = None
        
        return {
            'period_hours': hours,
            'connections_sent': connections,
            'messages_sent': messages,
            'errors': errors,
            'remaining_connections': remaining_connections,
            'remaining_messages': remaining_messages,
            'safe_to_continue': remaining_connections > 5 if remaining_connections else True
        }
    
    def check_linkedin_health(self) -> Dict:
        """Check LinkedIn account health."""
        daily = self.get_linkedin_usage(hours=24)
        weekly_events = [
            e for e in self.events
            if e.platform == 'linkedin'
            and datetime.fromisoformat(e.timestamp) > datetime.now() - timedelta(days=7)
        ]
        weekly_connections = len([e for e in weekly_events if e.event_type == 'connection'])
        
        alerts = []
        
        if daily['connections_sent'] >= self.LINKEDIN_DAILY_CONNECTIONS * 0.9:
            alerts.append("Approaching daily connection limit")
        
        if weekly_connections >= self.LINKEDIN_WEEKLY_CONNECTIONS * 0.9:
            alerts.append("Approaching weekly connection limit")
        
        if daily['errors'] > 3:
            alerts.append("Multiple errors detected - possible rate limiting")
        
        status = 'healthy' if not alerts else 'warning' if len(alerts) < 3 else 'critical'
        
        return {
            'status': status,
            'daily': daily,
            'weekly_connections': weekly_connections,
            'alerts': alerts,
            'recommendation': 'pause' if status == 'critical' else 'caution' if status == 'warning' else 'continue'
        }
    
    def get_api_usage(self, platform: str, hours: int = 24) -> Dict:
        """Get API usage statistics."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        events = [
            e for e in self.events
            if e.platform == platform
            and datetime.fromisoformat(e.timestamp) > cutoff
        ]
        
        successful = len([e for e in events if e.status == 'success'])
        errors = len([e for e in events if e.status == 'error'])
        total = len(events)
        
        return {
            'platform': platform,
            'period_hours': hours,
            'total_calls': total,
            'successful': successful,
            'errors': errors,
            'success_rate': successful / total if total > 0 else 0
        }
    
    def print_status_report(self):
        """Print a formatted status report."""
        print("\n" + "=" * 60)
        print("📊 RATE LIMIT STATUS REPORT")
        print("=" * 60)
        
        # LinkedIn
        linkedin = self.check_linkedin_health()
        print(f"\n🔗 LinkedIn: {linkedin['status'].upper()}")
        print(f"   Daily connections: {linkedin['daily']['connections_sent']}/{self.LINKEDIN_DAILY_CONNECTIONS}")
        print(f"   Weekly connections: {linkedin['weekly_connections']}/{self.LINKEDIN_WEEKLY_CONNECTIONS}")
        print(f"   Remaining today: {linkedin['daily']['remaining_connections']}")
        
        if linkedin['alerts']:
            print(f"\n   ⚠️  Alerts:")
            for alert in linkedin['alerts']:
                print(f"      - {alert}")
        
        # API usage
        print(f"\n🌐 API Usage (24h):")
        for platform in ['moonshot', 'phantombuster']:
            usage = self.get_api_usage(platform)
            status_icon = "✅" if usage['success_rate'] > 0.9 else "⚠️"
            print(f"   {status_icon} {platform}: {usage['successful']}/{usage['total_calls']} calls ({usage['success_rate']:.0%} success)")
        
        print(f"\n🎯 Recommendation: {linkedin['recommendation'].upper()}")
        print("=" * 60)


def main():
    """CLI for rate limit monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor rate limits')
    parser.add_argument('--report', action='store_true', help='Print full status report')
    parser.add_argument('--linkedin', action='store_true', help='Check LinkedIn only')
    parser.add_argument('--log', nargs=4, metavar=('TYPE', 'PLATFORM', 'STATUS', 'DETAILS'),
                       help='Log an event: type platform status details')
    
    args = parser.parse_args()
    
    monitor = RateLimitMonitor()
    
    if args.report:
        monitor.print_status_report()
    elif args.linkedin:
        health = monitor.check_linkedin_health()
        print(json.dumps(health, indent=2))
    elif args.log:
        monitor.log_event(args.log[0], args.log[1], args.log[2], args.log[3])
        print(f"✅ Logged event: {args.log[0]} on {args.log[1]}")
    else:
        # Default: print quick status
        health = monitor.check_linkedin_health()
        print(f"LinkedIn status: {health['status']}")
        print(f"Connections today: {health['daily']['connections_sent']}/{monitor.LINKEDIN_DAILY_CONNECTIONS}")
        print(f"Recommendation: {health['recommendation']}")


if __name__ == '__main__':
    main()
