"""
Salesforce CRM Integration
Sync prospects, contacts, and opportunities with Salesforce
"""
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

class SalesforceIntegration:
    """Salesforce CRM connector for the agent system."""
    
    def __init__(self, client_id: str, client_secret: str, 
                 username: str, password: str, security_token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.security_token = security_token
        self.access_token = None
        self.instance_url = None
        self._authenticate()
    
    def _authenticate(self):
        """OAuth2 authentication with Salesforce."""
        auth_url = "https://login.salesforce.com/services/oauth2/token"
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password + self.security_token
        }
        
        response = requests.post(auth_url, data=data)
        if response.status_code == 200:
            auth_data = response.json()
            self.access_token = auth_data["access_token"]
            self.instance_url = auth_data["instance_url"]
        else:
            raise Exception(f"Salesforce auth failed: {response.text}")
    
    def create_lead(self, prospect: Dict) -> Dict:
        """Create a new Lead from prospect data."""
        url = f"{self.instance_url}/services/data/v58.0/sobjects/Lead"
        
        lead_data = {
            "FirstName": prospect.get("first_name", ""),
            "LastName": prospect.get("last_name", "Unknown"),
            "Company": prospect.get("company", "Unknown"),
            "Title": prospect.get("title", ""),
            "Email": prospect.get("email", ""),
            "Phone": prospect.get("phone", ""),
            "Website": prospect.get("linkedin_url", ""),
            "LeadSource": "LinkedIn Automation",
            "Description": f"Quality Score: {prospect.get('quality_score', 0)}/10",
            "Industry": prospect.get("industry", ""),
            "NumberOfEmployees": prospect.get("company_size", 0)
        }
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.post(url, json=lead_data, headers=headers)
        
        if response.status_code == 201:
            return {"success": True, "lead_id": response.json()["id"]}
        return {"success": False, "error": response.text}
    
    def update_opportunity(self, opportunity_id: str, stage: str, 
                          notes: str = "") -> Dict:
        """Update opportunity stage."""
        url = f"{self.instance_url}/services/data/v58.0/sobjects/Opportunity/{opportunity_id}"
        
        data = {
            "StageName": stage,
            "Description": notes,
            "LastModifiedDate": datetime.now().isoformat()
        }
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.patch(url, json=data, headers=headers)
        
        return {"success": response.status_code == 204}
    
    def get_pipeline_report(self) -> List[Dict]:
        """Get current pipeline data."""
        query = """
        SELECT Id, Name, StageName, Amount, CloseDate, Account.Name
        FROM Opportunity
        WHERE StageName != 'Closed Won' AND StageName != 'Closed Lost'
        ORDER BY Amount DESC
        """
        
        url = f"{self.instance_url}/services/data/v58.0/query"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        response = requests.get(url, headers=headers, params={"q": query})
        
        if response.status_code == 200:
            return response.json().get("records", [])
        return []


class HubSpotIntegration:
    """HubSpot CRM connector for the agent system."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def create_contact(self, prospect: Dict) -> Dict:
        """Create a new contact from prospect data."""
        url = f"{self.base_url}/crm/v3/objects/contacts"
        
        contact_data = {
            "properties": {
                "firstname": prospect.get("first_name", ""),
                "lastname": prospect.get("last_name", "Unknown"),
                "email": prospect.get("email", ""),
                "phone": prospect.get("phone", ""),
                "jobtitle": prospect.get("title", ""),
                "company": prospect.get("company", ""),
                "linkedin_profile": prospect.get("linkedin_url", ""),
                "lead_source": "LinkedIn Automation",
                "quality_score": str(prospect.get("quality_score", 0)),
                "lifecyclestage": "lead"
            }
        }
        
        response = requests.post(url, json=contact_data, headers=self.headers)
        
        if response.status_code == 201:
            return {"success": True, "contact_id": response.json()["id"]}
        return {"success": False, "error": response.text}
    
    def create_deal(self, contact_id: str, deal_name: str, 
                    amount: float = 0) -> Dict:
        """Create a deal associated with a contact."""
        url = f"{self.base_url}/crm/v3/objects/deals"
        
        deal_data = {
            "properties": {
                "dealname": deal_name,
                "amount": str(amount),
                "pipeline": "default",
                "dealstage": "appointmentscheduled"
            },
            "associations": [
                {
                    "to": {"id": contact_id},
                    "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 3}]
                }
            ]
        }
        
        response = requests.post(url, json=deal_data, headers=self.headers)
        
        if response.status_code == 201:
            return {"success": True, "deal_id": response.json()["id"]}
        return {"success": False, "error": response.text}
    
    def update_contact_stage(self, contact_id: str, stage: str) -> bool:
        """Update contact lifecycle stage."""
        url = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"
        
        data = {"properties": {"lifecyclestage": stage}}
        response = requests.patch(url, json=data, headers=self.headers)
        
        return response.status_code == 200
    
    def get_engagement_metrics(self) -> Dict:
        """Get engagement analytics."""
        url = f"{self.base_url}/analytics/v2/reports/engagement"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        return {"error": response.text}


# Usage example
if __name__ == "__main__":
    # Example: HubSpot integration
    # hubspot = HubSpotIntegration(api_key="your_api_key")
    # prospect = {"first_name": "John", "last_name": "Doe", "company": "Acme"}
    # result = hubspot.create_contact(prospect)
    # print(result)
    pass
