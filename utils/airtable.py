"""
Airtable CRM Integration
Syncs prospects and pipeline data with Airtable
"""
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AirtableCRM:
    """Airtable CRM client for pipeline management."""
    
    BASE_URL = "https://api.airtable.com/v0"
    
    def __init__(self, api_key: str, base_id: str):
        self.api_key = api_key
        self.base_id = base_id
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        
        # Table names (can be customized)
        self.prospects_table = "Prospects"
        self.tasks_table = "Tasks"
        self.analytics_table = "Analytics"
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request to Airtable."""
        url = f"{self.BASE_URL}/{self.base_id}/{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PATCH":
                response = self.session.patch(url, json=data)
            elif method == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Airtable API error: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            return {"error": str(e)}
    
    def list_records(self, table_name: str, view: Optional[str] = None, 
                     filter_formula: Optional[str] = None) -> List[Dict]:
        """List records from a table."""
        endpoint = f"{table_name}"
        params = {}
        
        if view:
            params["view"] = view
        if filter_formula:
            params["filterByFormula"] = filter_formula
        
        url = f"{self.BASE_URL}/{self.base_id}/{table_name}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json().get("records", [])
        except Exception as e:
            logger.error(f"Error listing records: {e}")
            return []
    
    def create_prospect(self, prospect: Dict) -> Optional[str]:
        """
        Create a prospect record in Airtable.
        
        Returns record ID if successful.
        """
        # Map prospect fields to Airtable fields
        fields = {
            "Name": prospect.get("name"),
            "Title": prospect.get("title"),
            "Company": prospect.get("company"),
            "Stage": prospect.get("stage", "Prospect"),
            "Niche": prospect.get("niche", ""),
            "Priority Score": prospect.get("priority_score", 0),
            "LinkedIn URL": prospect.get("linkedin_url", ""),
            "Email": prospect.get("email", ""),
            "Company Stage": prospect.get("company_stage", ""),
            "ARR Estimate": prospect.get("arr_estimate", ""),
            "Pain Signals": ", ".join(prospect.get("pain_signals", [])),
            "Template Used": prospect.get("recommended_template", ""),
            "Discovered At": prospect.get("discovered_at", datetime.now().isoformat()),
            "Last Touch": prospect.get("last_touch", ""),
            "Outreach Log": str(prospect.get("outreach_log", []))
        }
        
        data = {"fields": fields}
        
        result = self._make_request("POST", self.prospects_table, data)
        record_id = result.get("id")
        
        if record_id:
            logger.info(f"Created prospect record: {record_id}")
        
        return record_id
    
    def update_prospect(self, record_id: str, updates: Dict) -> bool:
        """Update a prospect record."""
        # Map updates to Airtable fields
        field_mapping = {
            "stage": "Stage",
            "status": "Stage",
            "last_touch": "Last Touch",
            "outreach_log": "Outreach Log",
            "priority_score": "Priority Score",
            "email": "Email"
        }
        
        fields = {}
        for key, value in updates.items():
            airtable_key = field_mapping.get(key, key)
            if isinstance(value, list):
                fields[airtable_key] = ", ".join(str(v) for v in value)
            else:
                fields[airtable_key] = value
        
        data = {"fields": fields}
        
        result = self._make_request("PATCH", f"{self.prospects_table}/{record_id}", data)
        
        success = "id" in result
        if success:
            logger.info(f"Updated prospect: {record_id}")
        
        return success
    
    def find_prospect_by_linkedin(self, linkedin_url: str) -> Optional[Dict]:
        """Find a prospect by LinkedIn URL."""
        filter_formula = f'{{LinkedIn URL}}="{linkedin_url}"'
        records = self.list_records(self.prospects_table, filter_formula=filter_formula)
        
        if records:
            return records[0]
        return None
    
    def sync_prospects_batch(self, prospects: List[Dict]) -> Dict:
        """
        Sync multiple prospects to Airtable.
        
        Returns stats on created vs updated.
        """
        stats = {"created": 0, "updated": 0, "failed": 0}
        
        for prospect in prospects:
            try:
                # Check if exists
                existing = self.find_prospect_by_linkedin(prospect.get("linkedin_url", ""))
                
                if existing:
                    # Update
                    record_id = existing["id"]
                    self.update_prospect(record_id, prospect)
                    stats["updated"] += 1
                else:
                    # Create
                    record_id = self.create_prospect(prospect)
                    if record_id:
                        stats["created"] += 1
                    else:
                        stats["failed"] += 1
                        
            except Exception as e:
                logger.error(f"Error syncing prospect {prospect.get('name')}: {e}")
                stats["failed"] += 1
        
        logger.info(f"Sync complete: {stats['created']} created, {stats['updated']} updated, {stats['failed']} failed")
        return stats
    
    def get_pipeline_view(self, view_name: str = "Pipeline") -> List[Dict]:
        """Get prospects organized by pipeline view."""
        return self.list_records(self.prospects_table, view=view_name)
    
    def get_stage_counts(self) -> Dict[str, int]:
        """Get count of prospects in each pipeline stage."""
        records = self.list_records(self.prospects_table)
        
        counts = {}
        for record in records:
            stage = record.get("fields", {}).get("Stage", "Unknown")
            counts[stage] = counts.get(stage, 0) + 1
        
        return counts
    
    def create_task(self, task: Dict) -> Optional[str]:
        """Create a task in Airtable."""
        fields = {
            "Task ID": task.get("task_id"),
            "Prospect ID": task.get("prospect_id"),
            "Type": task.get("task_type"),
            "Description": task.get("description"),
            "Due Date": task.get("due_date", ""),
            "Priority": task.get("priority", "medium"),
            "Status": task.get("status", "pending")
        }
        
        data = {"fields": fields}
        
        result = self._make_request("POST", self.tasks_table, data)
        return result.get("id")
    
    def get_tasks_due_today(self) -> List[Dict]:
        """Get tasks due today."""
        today = datetime.now().strftime("%Y-%m-%d")
        filter_formula = f'IS_SAME({{Due Date}}, "{today}", "day")'
        return self.list_records(self.tasks_table, filter_formula=filter_formula)
    
    def record_analytics(self, metric_type: str, data: Dict, date: Optional[str] = None):
        """Record analytics data."""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        fields = {
            "Date": date,
            "Metric Type": metric_type,
            "Data": str(data)
        }
        
        data = {"fields": fields}
        result = self._make_request("POST", self.analytics_table, data)
        
        if result.get("id"):
            logger.info(f"Recorded analytics for {date}: {metric_type}")
        
        return result.get("id")
    
    def get_weekly_analytics(self, days: int = 7) -> List[Dict]:
        """Get analytics for the past N days."""
        from datetime import timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        filter_formula = (
            f'AND({{Date}} >= "{start_date.strftime("%Y-%m-%d")}", '
            f'{{Date}} <= "{end_date.strftime("%Y-%m-%d")}")'
        )
        
        return self.list_records(self.analytics_table, filter_formula=filter_formula)


class AirtableSetup:
    """Helper to set up Airtable base structure."""
    
    @staticmethod
    def create_base_schema():
        """
        Returns the recommended base schema for the CRM.
        
        User should manually create these tables in Airtable:
        """
        schema = {
            "Prospects": {
                "fields": [
                    {"name": "Name", "type": "singleLineText"},
                    {"name": "Title", "type": "singleLineText"},
                    {"name": "Company", "type": "singleLineText"},
                    {"name": "Stage", "type": "singleSelect", 
                     "options": ["Prospect", "Outreach", "Connected", "Engaged", 
                                "Qualified", "Discovery Call Booked", "Proposal Sent",
                                "Negotiation", "Closed Won", "Closed Lost"]},
                    {"name": "Niche", "type": "singleSelect", "options": ["saas", "agency"]},
                    {"name": "Priority Score", "type": "number"},
                    {"name": "LinkedIn URL", "type": "url"},
                    {"name": "Email", "type": "email"},
                    {"name": "Company Stage", "type": "singleLineText"},
                    {"name": "ARR Estimate", "type": "singleLineText"},
                    {"name": "Pain Signals", "type": "longText"},
                    {"name": "Template Used", "type": "singleLineText"},
                    {"name": "Discovered At", "type": "dateTime"},
                    {"name": "Last Touch", "type": "dateTime"},
                    {"name": "Outreach Log", "type": "longText"}
                ],
                "views": [
                    {"name": "Grid", "type": "grid"},
                    {"name": "Pipeline", "type": "kanban", "groupField": "Stage"},
                    {"name": "High Priority", "type": "grid", 
                     "filter": "{Priority Score} >= 7"},
                    {"name": "SaaS Prospects", "type": "grid", 
                     "filter": "{Niche} = 'saas'"},
                    {"name": "Agency Prospects", "type": "grid",
                     "filter": "{Niche} = 'agency'"}
                ]
            },
            "Tasks": {
                "fields": [
                    {"name": "Task ID", "type": "singleLineText"},
                    {"name": "Prospect ID", "type": "singleLineText"},
                    {"name": "Type", "type": "singleSelect",
                     "options": ["discovery_call", "prep_call", "proposal_followup", 
                                "project_kickoff", "general"]},
                    {"name": "Description", "type": "longText"},
                    {"name": "Due Date", "type": "date"},
                    {"name": "Priority", "type": "singleSelect", 
                     "options": ["high", "medium", "low"]},
                    {"name": "Status", "type": "singleSelect",
                     "options": ["pending", "in_progress", "completed"]},
                    {"name": "Link to Prospects", "type": "link", "linkedTable": "Prospects"}
                ]
            },
            "Analytics": {
                "fields": [
                    {"name": "Date", "type": "date"},
                    {"name": "Metric Type", "type": "singleLineText"},
                    {"name": "Data", "type": "longText"},
                    {"name": "Connections Sent", "type": "number"},
                    {"name": "Connections Accepted", "type": "number"},
                    {"name": "Replies Received", "type": "number"},
                    {"name": "Deals Closed", "type": "number"},
                    {"name": "Revenue", "type": "number"}
                ]
            }
        }
        
        print("=" * 60)
        print("AIRTABLE BASE SETUP INSTRUCTIONS")
        print("=" * 60)
        print("\n1. Create a new Airtable base")
        print("2. Create 3 tables with these fields:\n")
        
        for table_name, config in schema.items():
            print(f"\n📋 Table: {table_name}")
            print("-" * 40)
            for field in config["fields"]:
                print(f"  • {field['name']} ({field['type']})")
            
            if "views" in config:
                print(f"\n  Views:")
                for view in config["views"]:
                    print(f"    - {view['name']}")
        
        print("\n" + "=" * 60)
        print("After creating, get your Base ID from:")
        print("https://airtable.com/api")
        print("=" * 60)
        
        return schema


if __name__ == "__main__":
    import os
    
    # Show setup instructions
    AirtableSetup.create_base_schema()
    
    # Test with real API if available
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    
    if api_key and base_id:
        crm = AirtableCRM(api_key, base_id)
        stages = crm.get_stage_counts()
        print(f"\nCurrent pipeline: {stages}")
    else:
        print("\n⚠️  Set AIRTABLE_API_KEY and AIRTABLE_BASE_ID to test")
