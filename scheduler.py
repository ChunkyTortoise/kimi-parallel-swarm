"""
Automated Scheduler
Runs daily workflows at scheduled times using APScheduler
"""
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from agents.orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)


class OutreachScheduler:
    """Scheduler for automated daily outreach workflows."""
    
    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = config_path
        self.scheduler = BackgroundScheduler()
        self.orchestrator = None
        self._running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info("Shutdown signal received, stopping scheduler...")
        self.stop()
        sys.exit(0)
    
    def _morning_job(self):
        """Morning routine job."""
        logger.info("=" * 60)
        logger.info("🌅 STARTING MORNING ROUTINE (8:00 AM PT)")
        logger.info("=" * 60)
        
        try:
            if not self.orchestrator:
                self.orchestrator = AgentOrchestrator(self.config_path)
            
            results = self.orchestrator.morning_routine()
            
            logger.info(f"✅ Morning routine complete")
            logger.info(f"   New prospects: {results['new_prospects']}")
            logger.info(f"   Messages ready: {results['messages_ready']}")
            logger.info(f"   Priority tasks: {results['priority_tasks']}")
            
        except Exception as e:
            logger.error(f"❌ Morning routine failed: {e}", exc_info=True)
    
    def _midday_job(self):
        """Midday execution job."""
        logger.info("=" * 60)
        logger.info("☀️ STARTING MIDDAY EXECUTION (12:00 PM PT)")
        logger.info("=" * 60)
        
        try:
            if not self.orchestrator:
                self.orchestrator = AgentOrchestrator(self.config_path)
            
            results = self.orchestrator.midday_execution()
            
            logger.info(f"✅ Midday execution complete")
            logger.info(f"   Actions executed: {results['actions_executed']}")
            
        except Exception as e:
            logger.error(f"❌ Midday execution failed: {e}", exc_info=True)
    
    def _evening_job(self):
        """Evening wrap-up job."""
        logger.info("=" * 60)
        logger.info("🌆 STARTING EVENING WRAP-UP (6:00 PM PT)")
        logger.info("=" * 60)
        
        try:
            if not self.orchestrator:
                self.orchestrator = AgentOrchestrator(self.config_path)
            
            results = self.orchestrator.evening_wrapup()
            
            logger.info(f"✅ Evening wrap-up complete")
            logger.info(f"   Final actions: {results['final_actions']}")
            logger.info(f"   Pipeline value: ${results.get('pipeline_value', 0):,}")
            logger.info(f"   Reddit opportunities: {results['reddit_opportunities']}")
            
        except Exception as e:
            logger.error(f"❌ Evening wrap-up failed: {e}", exc_info=True)
    
    def _weekly_job(self):
        """Weekly review job (Mondays 8 AM)."""
        logger.info("=" * 60)
        logger.info("📊 GENERATING WEEKLY REPORT (Monday 8:00 AM)")
        logger.info("=" * 60)
        
        try:
            if not self.orchestrator:
                self.orchestrator = AgentOrchestrator(self.config_path)
            
            report = self.orchestrator.weekly_review()
            
            logger.info(f"✅ Weekly report generated")
            logger.info(f"   Connections sent: {report['summary']['connections_sent']}")
            logger.info(f"   Reply rate: {report['summary']['reply_rate']}")
            logger.info(f"   Deals closed: {report['summary']['deals_closed']}")
            
            # Log any alerts
            if report.get('alerts'):
                logger.warning("⚠️ Alerts this week:")
                for alert in report['alerts']:
                    logger.warning(f"   - {alert}")
            
            # Log recommendations
            if report.get('recommendations'):
                logger.info("💡 Recommendations:")
                for rec in report['recommendations'][:3]:
                    priority = "HIGH" if rec['priority'] == 'high' else "MED"
                    logger.info(f"   [{priority}] {rec['issue']}: {rec['action']}")
            
        except Exception as e:
            logger.error(f"❌ Weekly review failed: {e}", exc_info=True)
    
    def setup_schedule(self):
        """Configure the job schedule."""
        # Morning routine: 8:00 AM PT, Monday-Friday
        self.scheduler.add_job(
            self._morning_job,
            trigger=CronTrigger(hour=8, minute=0, day_of_week="mon-fri"),
            id="morning_routine",
            name="Morning Routine",
            replace_existing=True
        )
        
        # Midday execution: 12:00 PM PT, Monday-Friday
        self.scheduler.add_job(
            self._midday_job,
            trigger=CronTrigger(hour=12, minute=0, day_of_week="mon-fri"),
            id="midday_execution",
            name="Midday Execution",
            replace_existing=True
        )
        
        # Evening wrap-up: 6:00 PM PT, Monday-Friday
        self.scheduler.add_job(
            self._evening_job,
            trigger=CronTrigger(hour=18, minute=0, day_of_week="mon-fri"),
            id="evening_wrapup",
            name="Evening Wrap-Up",
            replace_existing=True
        )
        
        # Weekly review: Monday 8:00 AM PT
        self.scheduler.add_job(
            self._weekly_job,
            trigger=CronTrigger(hour=8, minute=0, day_of_week="mon"),
            id="weekly_review",
            name="Weekly Review",
            replace_existing=True
        )
        
        logger.info("✅ Schedule configured:")
        logger.info("   Morning Routine: 8:00 AM PT (Mon-Fri)")
        logger.info("   Midday Execution: 12:00 PM PT (Mon-Fri)")
        logger.info("   Evening Wrap-Up: 6:00 PM PT (Mon-Fri)")
        logger.info("   Weekly Review: 8:00 AM PT (Monday)")
    
    def start(self):
        """Start the scheduler."""
        self.setup_schedule()
        self.scheduler.start()
        self._running = True
        
        logger.info("=" * 60)
        logger.info("🚀 SCHEDULER STARTED")
        logger.info("=" * 60)
        logger.info("Press Ctrl+C to stop\n")
        
        # Keep running
        try:
            while self._running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the scheduler."""
        self._running = False
        self.scheduler.shutdown()
        logger.info("\n🛑 Scheduler stopped")
    
    def run_once(self, job_name: str = "morning"):
        """Run a specific job once immediately (for testing)."""
        logger.info(f"Running {job_name} job once...")
        
        if job_name == "morning":
            self._morning_job()
        elif job_name == "midday":
            self._midday_job()
        elif job_name == "evening":
            self._evening_job()
        elif job_name == "weekly":
            self._weekly_job()
        else:
            logger.error(f"Unknown job: {job_name}")


def main():
    """Main entry point for scheduler."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kimi Agent System Scheduler")
    parser.add_argument(
        "--run-once",
        choices=["morning", "midday", "evening", "weekly"],
        help="Run a specific job once and exit"
    )
    parser.add_argument(
        "--config",
        default="config/settings.json",
        help="Path to config file"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data/scheduler.log'),
            logging.StreamHandler()
        ]
    )
    
    scheduler = OutreachScheduler(args.config)
    
    if args.run_once:
        scheduler.run_once(args.run_once)
    else:
        scheduler.start()


if __name__ == "__main__":
    main()
