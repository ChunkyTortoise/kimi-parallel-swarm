"""
CRM & Pipeline Agent
Auto-update CRM, track pipeline stages, flag high-priority opportunities, schedule tasks.
"""
import json
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    PROSPECT = "prospect"
    OUTREACH = "outreach"
    CONNECTED = "connected"
    ENGAGED = "engaged"
    QUALIFIED = "qualified"
    DISCOVERY_BOOKED = "discovery_call_booked"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


@dataclass
class Task:
    task_id: str
    prospect_id: str
    task_type: str
    description: str
    due_date: datetime
    priority: str  # "high", "medium", "low"
    status: str = "pending"
    completed_at: Optional[datetime] = None


class CRMPipelineAgent:
    """Agent for CRM management and pipeline tracking."""
    
    def __init__(self, config: Dict, crm_type: str = "json"):
        self.config = config
        self.crm_type = crm_type  # "json", "airtable", "sheets"
        self.data_path = Path("data/prospects.json")
        self.tasks_path = Path("data/tasks.json")
        self.analytics_path = Path("data/analytics.json")
        
        # Ensure data directory exists
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize data
        self.prospects: Dict[str, Dict] = self._load_prospects()
        self.tasks: List[Task] = self._load_tasks()
        self.analytics: Dict = self._load_analytics()
        
        # Pipeline stage progression rules
        self.stage_flow = {
            PipelineStage.PROSPECT: [PipelineStage.OUTREACH],
            PipelineStage.OUTREACH: [PipelineStage.CONNECTED, PipelineStage.CLOSED_LOST],
            PipelineStage.CONNECTED: [PipelineStage.ENGAGED, PipelineStage.CLOSED_LOST],
            PipelineStage.ENGAGED: [PipelineStage.QUALIFIED, PipelineStage.CLOSED_LOST],
            PipelineStage.QUALIFIED: [PipelineStage.DISCOVERY_BOOKED, PipelineStage.CLOSED_LOST],
            PipelineStage.DISCOVERY_BOOKED: [PipelineStage.PROPOSAL_SENT, PipelineStage.CLOSED_LOST],
            PipelineStage.PROPOSAL_SENT: [PipelineStage.NEGOTIATION, PipelineStage.CLOSED_WON, PipelineStage.CLOSED_LOST],
            PipelineStage.NEGOTIATION: [PipelineStage.CLOSED_WON, PipelineStage.CLOSED_LOST],
        }
    
    def _load_prospects(self) -> Dict[str, Dict]:
        """Load prospects from storage."""
        if self.data_path.exists():
            with open(self.data_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_prospects(self):
        """Save prospects to storage."""
        with open(self.data_path, 'w') as f:
            json.dump(self.prospects, f, indent=2, default=str)
    
    def _load_tasks(self) -> List[Task]:
        """Load tasks from storage."""
        if self.tasks_path.exists():
            with open(self.tasks_path, 'r') as f:
                data = json.load(f)
                return [Task(**t) for t in data]
        return []
    
    def _save_tasks(self):
        """Save tasks to storage."""
        with open(self.tasks_path, 'w') as f:
            json.dump([asdict(t) for t in self.tasks], f, indent=2, default=str)
    
    def _load_analytics(self) -> Dict:
        """Load analytics data."""
        if self.analytics_path.exists():
            with open(self.analytics_path, 'r') as f:
                return json.load(f)
        return {
            "daily_metrics": {},
            "weekly_metrics": {},
            "template_performance": {},
            "niche_performance": {"saas": {}, "agency": {}}
        }
    
    def _save_analytics(self):
        """Save analytics data."""
        with open(self.analytics_path, 'w') as f:
            json.dump(self.analytics, f, indent=2, default=str)
    
    def add_prospect(self, prospect: Dict) -> str:
        """Add a new prospect to CRM."""
        prospect_id = prospect.get("prospect_id")
        
        if prospect_id in self.prospects:
            logger.warning(f"Prospect {prospect_id} already exists, updating")
        
        prospect["stage"] = PipelineStage.PROSPECT.value
        prospect["stage_changed_at"] = datetime.now().isoformat()
        prospect["outreach_log"] = []
        prospect["created_at"] = datetime.now().isoformat()
        prospect["last_touch"] = None
        
        self.prospects[prospect_id] = prospect
        self._save_prospects()
        
        logger.info(f"Added prospect {prospect.get('name')} to CRM")
        return prospect_id
    
    def add_prospects_batch(self, prospects: List[Dict]) -> List[str]:
        """Add multiple prospects to CRM."""
        ids = []
        for prospect in prospects:
            pid = self.add_prospect(prospect)
            ids.append(pid)
        return ids
    
    def update_status(self, prospect_id: str, new_stage: str) -> bool:
        """Update prospect pipeline stage."""
        if prospect_id not in self.prospects:
            logger.error(f"Prospect {prospect_id} not found")
            return False
        
        old_stage = self.prospects[prospect_id].get("stage")
        
        self.prospects[prospect_id]["stage"] = new_stage
        self.prospects[prospect_id]["stage_changed_at"] = datetime.now().isoformat()
        
        # Trigger stage-specific actions
        self._handle_stage_change(prospect_id, old_stage, new_stage)
        
        self._save_prospects()
        logger.info(f"Updated {prospect_id}: {old_stage} -> {new_stage}")
        return True
    
    def _handle_stage_change(self, prospect_id: str, old_stage: str, new_stage: str):
        """Handle actions triggered by stage changes."""
        prospect = self.prospects[prospect_id]
        
        if new_stage == PipelineStage.QUALIFIED.value:
            # High-priority lead - create task for discovery call
            self.create_task(
                prospect_id=prospect_id,
                task_type="discovery_call",
                description=f"Book discovery call with {prospect.get('name')} at {prospect.get('company')}",
                due_date=datetime.now() + timedelta(days=2),
                priority="high"
            )
            
        elif new_stage == PipelineStage.DISCOVERY_BOOKED.value:
            # Prepare call briefing
            self.create_task(
                prospect_id=prospect_id,
                task_type="prep_call",
                description=f"Prepare discovery call briefing for {prospect.get('name')}",
                due_date=datetime.now() + timedelta(hours=2),
                priority="medium"
            )
            
        elif new_stage == PipelineStage.PROPOSAL_SENT.value:
            # Follow up on proposal
            self.create_task(
                prospect_id=prospect_id,
                task_type="proposal_followup",
                description=f"Follow up on proposal sent to {prospect.get('name')}",
                due_date=datetime.now() + timedelta(days=3),
                priority="high"
            )
            
        elif new_stage == PipelineStage.CLOSED_WON.value:
            # Onboarding task
            self.create_task(
                prospect_id=prospect_id,
                task_type="project_kickoff",
                description=f"Schedule project kickoff with {prospect.get('name')}",
                due_date=datetime.now() + timedelta(days=2),
                priority="high"
            )
    
    def log_outreach_action(self, prospect_id: str, action_type: str, details: Dict):
        """Log an outreach action to prospect history."""
        if prospect_id not in self.prospects:
            return
        
        log_entry = {
            "date": datetime.now().isoformat(),
            "action": action_type,
            "details": details
        }
        
        if "outreach_log" not in self.prospects[prospect_id]:
            self.prospects[prospect_id]["outreach_log"] = []
        
        self.prospects[prospect_id]["outreach_log"].append(log_entry)
        self.prospects[prospect_id]["last_touch"] = datetime.now().isoformat()
        
        self._save_prospects()
    
    def create_task(self, prospect_id: str, task_type: str, description: str, 
                   due_date: datetime, priority: str = "medium") -> Task:
        """Create a new task."""
        task = Task(
            task_id=f"{prospect_id}_{task_type}_{int(datetime.now().timestamp())}",
            prospect_id=prospect_id,
            task_type=task_type,
            description=description,
            due_date=due_date,
            priority=priority
        )
        
        self.tasks.append(task)
        self._save_tasks()
        
        logger.info(f"Created task: {description}")
        return task
    
    def get_daily_tasks(self) -> List[Task]:
        """Get tasks due today."""
        today = datetime.now().replace(hour=23, minute=59, second=59)
        today_start = datetime.now().replace(hour=0, minute=0, second=0)
        
        return [
            t for t in self.tasks 
            if t.status == "pending" 
            and today_start <= t.due_date <= today
        ]
    
    def get_high_priority_leads(self) -> List[Dict]:
        """Get high-priority qualified leads."""
        return [
            p for p in self.prospects.values()
            if p.get("stage") == PipelineStage.QUALIFIED.value
            and p.get("priority_score", 0) >= 7.0
        ]
    
    def get_pipeline_summary(self) -> Dict:
        """Get pipeline stage counts."""
        stages = {stage.value: 0 for stage in PipelineStage}
        
        for prospect in self.prospects.values():
            stage = prospect.get("stage", "prospect")
            if stage in stages:
                stages[stage] += 1
        
        # Calculate pipeline value
        pipeline_value = 0
        deal_values = {
            PipelineStage.DISCOVERY_BOOKED.value: 8000,
            PipelineStage.PROPOSAL_SENT.value: 10000,
            PipelineStage.NEGOTIATION.value: 10000
        }
        
        for stage, value in deal_values.items():
            pipeline_value += stages.get(stage, 0) * value
        
        return {
            "stage_counts": stages,
            "total_prospects": len(self.prospects),
            "pipeline_value": pipeline_value,
            "qualified_leads": stages.get(PipelineStage.QUALIFIED.value, 0),
            "discovery_calls_booked": stages.get(PipelineStage.DISCOVERY_BOOKED.value, 0),
            "proposals_sent": stages.get(PipelineStage.PROPOSAL_SENT.value, 0),
            "deals_won": stages.get(PipelineStage.CLOSED_WON.value, 0),
            "deals_lost": stages.get(PipelineStage.CLOSED_LOST.value, 0)
        }
    
    def record_analytics(self, metric_type: str, data: Dict):
        """Record analytics data."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today not in self.analytics["daily_metrics"]:
            self.analytics["daily_metrics"][today] = {}
        
        self.analytics["daily_metrics"][today][metric_type] = data
        self._save_analytics()
    
    def get_weekly_metrics(self) -> Dict:
        """Get metrics for the past 7 days."""
        metrics = {
            "connections_sent": 0,
            "connections_accepted": 0,
            "replies_received": 0,
            "discovery_calls_booked": 0,
            "proposals_sent": 0,
            "deals_closed": 0,
            "revenue": 0
        }
        
        for i in range(7):
            date_str = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if date_str in self.analytics["daily_metrics"]:
                day_data = self.analytics["daily_metrics"][date_str]
                for key in metrics:
                    if key in day_data:
                        metrics[key] += day_data[key].get("count", 0)
        
        # Calculate rates
        if metrics["connections_sent"] > 0:
            metrics["acceptance_rate"] = round(
                metrics["connections_accepted"] / metrics["connections_sent"], 3
            )
        else:
            metrics["acceptance_rate"] = 0
        
        if metrics["connections_sent"] > 0:
            metrics["reply_rate"] = round(
                metrics["replies_received"] / metrics["connections_sent"], 3
            )
        else:
            metrics["reply_rate"] = 0
        
        return metrics
    
    def export_report(self, filepath: str):
        """Export full CRM report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "pipeline_summary": self.get_pipeline_summary(),
            "weekly_metrics": self.get_weekly_metrics(),
            "high_priority_leads": self.get_high_priority_leads(),
            "pending_tasks": len([t for t in self.tasks if t.status == "pending"]),
            "total_tasks": len(self.tasks)
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Exported CRM report to {filepath}")


if __name__ == "__main__":
    agent = CRMPipelineAgent({})
    
    # Test data
    test_prospect = {
        "prospect_id": "test123",
        "name": "Jane Smith",
        "title": "VP Product",
        "company": "TestCo",
        "priority_score": 8.5
    }
    
    agent.add_prospect(test_prospect)
    agent.update_status("test123", PipelineStage.QUALIFIED.value)
    
    print(f"Pipeline summary: {agent.get_pipeline_summary()}")
    print(f"Daily tasks: {len(agent.get_daily_tasks())}")
