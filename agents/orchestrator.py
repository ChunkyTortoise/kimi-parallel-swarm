"""
Agent Orchestrator
Coordinates all 5 agents in daily workflows (morning, midday, evening).
"""
import json
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from pathlib import Path

from agents.icp_research_agent import ICPResearchAgent
from agents.copy_generation_agent import CopyGenerationAgent
from agents.outreach_execution_agent import OutreachExecutionAgent
from agents.crm_pipeline_agent import CRMPipelineAgent
from agents.performance_optimization_agent import PerformanceOptimizationAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates the 5-agent swarm for daily operations."""
    
    def __init__(self, config_path: str = "config/settings.json"):
        # Load config
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize all agents
        self.crm_agent = CRMPipelineAgent(self.config)
        self.icp_agent = ICPResearchAgent(self.config)
        self.copy_agent = CopyGenerationAgent(self.config, templates_path="templates")
        self.outreach_agent = OutreachExecutionAgent(self.config, crm_agent=self.crm_agent)
        self.performance_agent = PerformanceOptimizationAgent(self.config, crm_agent=self.crm_agent)
        
        # Load templates into copy agent from downloads folder
        self.copy_agent.saas_templates = self._load_external_templates("/Users/cave/Downloads/linkedin_outreach_saas.json")
        self.copy_agent.agency_templates = self._load_external_templates("/Users/cave/Downloads/linkedin_outreach_agency.json")
        
        self.report_path = Path("data/daily_reports")
        self.report_path.mkdir(parents=True, exist_ok=True)
    
    def _load_external_templates(self, filepath: str) -> Dict:
        """Load templates from external file."""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading templates from {filepath}: {e}")
            return {}
    
    def morning_routine(self) -> Dict:
        """
        Morning Routine (8:00 AM PT)
        - Research new prospects
        - Generate personalized messages
        - Generate daily task list
        - Review yesterday's metrics
        """
        logger.info("=" * 50)
        logger.info("STARTING MORNING ROUTINE")
        logger.info("=" * 50)
        
        results = {}
        
        # 1. ICP Research Agent: Research 50 new prospects
        logger.info("[ICP Agent] Researching prospects...")
        saas_count = int(50 * self.config.get("niche_allocation", {}).get("saas", 0.7))
        agency_count = 50 - saas_count
        
        prospects = self.icp_agent.research_daily_batch(
            saas_count=saas_count,
            agency_count=agency_count
        )
        
        # Add to CRM
        if prospects:
            self.crm_agent.add_prospects_batch([p.__dict__ for p in prospects])
        
        results["new_prospects"] = len(prospects)
        logger.info(f"[ICP Agent] Found {len(prospects)} prospects")
        
        # 2. Copy Generation Agent: Personalize messages
        logger.info("[Copy Agent] Generating messages...")
        
        # Get prospects ready for outreach (not yet contacted)
        ready_prospects = [
            p for p in self.crm_agent.prospects.values()
            if p.get("stage") == "prospect" and p.get("priority_score", 0) >= 7.0
        ][:self.config.get("daily_limits", {}).get("connections", 20)]
        
        if ready_prospects:
            messages = self.copy_agent.generate_batch(ready_prospects)
            
            # Schedule connection requests for high-quality messages
            for msg in messages:
                if msg.quality_score >= self.config.get("quality_threshold", 7.0):
                    prospect = self.crm_agent.prospects.get(msg.prospect_id)
                    if prospect:
                        self.outreach_agent.schedule_connection_request(
                            prospect, msg.body
                        )
            
            results["messages_ready"] = len(messages)
            results["avg_quality_score"] = sum(m.quality_score for m in messages) / len(messages) if messages else 0
        else:
            results["messages_ready"] = 0
            results["avg_quality_score"] = 0
        
        logger.info(f"[Copy Agent] Generated {results['messages_ready']} messages")
        
        # 3. CRM Agent: Generate daily task list
        logger.info("[CRM Agent] Generating tasks...")
        daily_tasks = self.crm_agent.get_daily_tasks()
        high_priority = self.crm_agent.get_high_priority_leads()
        
        results["priority_tasks"] = len(daily_tasks)
        results["high_priority_leads"] = len(high_priority)
        
        logger.info(f"[CRM Agent] {len(daily_tasks)} tasks, {len(high_priority)} high-priority leads")
        
        # 4. Performance Agent: Review yesterday's metrics
        logger.info("[Performance Agent] Reviewing metrics...")
        yesterday_summary = self.crm_agent.get_weekly_metrics()
        results["yesterday_summary"] = yesterday_summary
        
        logger.info("=" * 50)
        logger.info("MORNING ROUTINE COMPLETE")
        logger.info("=" * 50)
        
        return results
    
    def midday_execution(self) -> Dict:
        """
        Midday Execution (12:00 PM PT)
        - Send scheduled connection requests
        - Send scheduled DMs
        - Process new replies
        - Draft follow-ups
        """
        logger.info("=" * 50)
        logger.info("STARTING MIDDAY EXECUTION")
        logger.info("=" * 50)
        
        results = {}
        
        # 1. Outreach Agent: Send scheduled actions
        logger.info("[Outreach Agent] Sending scheduled actions...")
        executed = self.outreach_agent.execute_scheduled_actions()
        results["actions_executed"] = len(executed)
        
        for action in executed:
            logger.info(f"  - Executed: {action.get('action')} for {action.get('prospect_id')}")
        
        # 2. CRM Agent: Process new replies (simulated)
        logger.info("[CRM Agent] Processing replies...")
        # In production, this would fetch from LinkedIn API
        results["replies_processed"] = 0
        
        # 3. Copy Agent: Draft follow-ups for new replies
        # This would be triggered by actual replies
        
        # 4. Update pipeline stages based on actions
        for action in executed:
            if action.get("action") == "connection_request_sent":
                self.crm_agent.update_status(action["prospect_id"], "outreach")
            elif action.get("action") == "dm_sent":
                self.crm_agent.update_status(action["prospect_id"], "engaged")
        
        logger.info("=" * 50)
        logger.info("MIDDAY EXECUTION COMPLETE")
        logger.info("=" * 50)
        
        return results
    
    def evening_wrapup(self) -> Dict:
        """
        Evening Wrap-Up (6:00 PM PT)
        - Final outreach batch
        - Update pipeline stages
        - Calculate daily metrics
        - Monitor Reddit
        """
        logger.info("=" * 50)
        logger.info("STARTING EVENING WRAP-UP")
        logger.info("=" * 50)
        
        results = {}
        
        # 1. Outreach Agent: Final daily batch
        logger.info("[Outreach Agent] Final batch...")
        final_actions = self.outreach_agent.execute_scheduled_actions()
        results["final_actions"] = len(final_actions)
        
        # 2. CRM Agent: Update pipeline stages
        logger.info("[CRM Agent] Updating pipeline...")
        pipeline = self.crm_agent.get_pipeline_summary()
        results["pipeline_value"] = pipeline.get("pipeline_value", 0)
        results["qualified_leads"] = pipeline.get("qualified_leads", 0)
        
        # 3. Performance Agent: Calculate daily metrics
        logger.info("[Performance Agent] Calculating metrics...")
        daily_stats = self.outreach_agent.get_daily_stats()
        
        # Record in CRM analytics
        self.crm_agent.record_analytics("outreach", {
            "connections_sent": daily_stats["connections_sent_today"],
            "messages_sent": daily_stats["messages_sent_today"],
            "count": daily_stats["connections_sent_today"] + daily_stats["messages_sent_today"]
        })
        
        results["daily_stats"] = daily_stats
        
        # 4. ICP Agent: Monitor Reddit for evening activity
        logger.info("[ICP Agent] Monitoring Reddit...")
        reddit_opps = self.icp_agent.monitor_reddit(
            ["SaaS", "startups", "marketing"],
            ["analytics", "dashboard", "automation", "reporting"]
        )
        results["reddit_opportunities"] = len(reddit_opps)
        
        # Save daily report
        self._save_daily_report(results)
        
        logger.info("=" * 50)
        logger.info("EVENING WRAP-UP COMPLETE")
        logger.info("=" * 50)
        
        return results
    
    def _save_daily_report(self, data: Dict):
        """Save daily report to file."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        filepath = self.report_path / f"report_{date_str}.json"
        
        report = {
            "date": date_str,
            "generated_at": datetime.now().isoformat(),
            "data": data,
            "pipeline": self.crm_agent.get_pipeline_summary()
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Daily report saved to {filepath}")
    
    def weekly_review(self) -> Dict:
        """
        Weekly Review (Monday 8:00 AM)
        - Generate performance report
        - Analyze template performance
        - Compare niche performance
        - Generate recommendations
        """
        logger.info("=" * 50)
        logger.info("GENERATING WEEKLY REVIEW")
        logger.info("=" * 50)
        
        report = self.performance_agent.generate_weekly_report()
        
        # Save report
        week_str = datetime.now().strftime("%Y-W%U")
        filepath = self.report_path / f"weekly_{week_str}.json"
        self.performance_agent.save_report(report, str(filepath))
        
        logger.info("=" * 50)
        logger.info("WEEKLY REVIEW COMPLETE")
        logger.info("=" * 50)
        
        return report
    
    def run_full_day(self):
        """Execute a full day of operations."""
        morning_results = self.morning_routine()
        midday_results = self.midday_execution()
        evening_results = self.evening_wrapup()
        
        return {
            "morning": morning_results,
            "midday": midday_results,
            "evening": evening_results
        }
    
    def get_dashboard(self) -> Dict:
        """Get current system dashboard."""
        return {
            "timestamp": datetime.now().isoformat(),
            "daily_limits": self.outreach_agent.get_daily_stats(),
            "pipeline": self.crm_agent.get_pipeline_summary(),
            "today_tasks": len(self.crm_agent.get_daily_tasks()),
            "queue_length": len(self.outreach_agent.action_queue)
        }


if __name__ == "__main__":
    # Initialize orchestrator
    orchestrator = AgentOrchestrator("/Users/cave/kimi_agent_system/config/settings.json")
    
    # Run morning routine as test
    results = orchestrator.morning_routine()
    print(json.dumps(results, indent=2, default=str))
    
    # Show dashboard
    print("\nDashboard:")
    print(json.dumps(orchestrator.get_dashboard(), indent=2, default=str))
