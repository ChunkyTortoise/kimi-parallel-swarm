"""
Phantombuster LinkedIn Integration
Handles LinkedIn automation via Phantombuster API
"""
import requests
import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LinkedInProfile:
    linkedinUrl: str
    firstName: str
    lastName: str
    headline: str
    company: str
    email: Optional[str] = None
    phone: Optional[str] = None


class PhantombusterLinkedIn:
    """Phantombuster LinkedIn automation client."""
    
    BASE_URL = "https://phantombuster.com/api/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "X-Phantombuster-Key-1": api_key,
            "Content-Type": "application/json"
        })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request to Phantombuster."""
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Phantombuster API error: {e}")
            return {"error": str(e)}
    
    def list_agents(self) -> List[Dict]:
        """List available LinkedIn agents."""
        result = self._make_request("GET", "agents")
        return result.get("data", [])
    
    def launch_linkedin_network_search(self, search_url: str, max_results: int = 50) -> str:
        """
        Launch LinkedIn Network Search agent.
        
        Args:
            search_url: LinkedIn search URL
            max_results: Max profiles to extract (1-2500)
        
        Returns:
            container_id for tracking
        """
        # Find the LinkedIn Network Search agent
        agents = self.list_agents()
        agent_id = None
        
        for agent in agents:
            if "network" in agent.get("name", "").lower() and "search" in agent.get("name", "").lower():
                agent_id = agent["id"]
                break
        
        if not agent_id:
            # Use default LinkedIn Network Search agent ID
            agent_id = "3113123724622011"  # Standard LinkedIn Network Search
        
        data = {
            "agentId": agent_id,
            "arguments": {
                "sessionCookie": "YOUR_LINKEDIN_SESSION_COOKIE",
                "search": search_url,
                "numberOfResults": min(max_results, 100),  # Stay within limits
                "removeDuplicateProfiles": True,
                "extractDefaultUrl": True
            }
        }
        
        result = self._make_request("POST", f"agents/{agent_id}/launch", data)
        container_id = result.get("data", {}).get("containerId")
        
        logger.info(f"Launched LinkedIn search agent: {container_id}")
        return container_id
    
    def launch_linkedin_profile_scraper(self, profile_urls: List[str]) -> str:
        """
        Launch LinkedIn Profile Scraper for specific profiles.
        
        Args:
            profile_urls: List of LinkedIn profile URLs
        
        Returns:
            container_id for tracking
        """
        agent_id = "3113123724622012"  # LinkedIn Profile Scraper
        
        data = {
            "agentId": agent_id,
            "arguments": {
                "sessionCookie": "YOUR_LINKEDIN_SESSION_COOKIE",
                "profileUrls": profile_urls[:25],  # Limit to 25 per run
                "removeDuplicateProfiles": True
            }
        }
        
        result = self._make_request("POST", f"agents/{agent_id}/launch", data)
        container_id = result.get("data", {}).get("containerId")
        
        logger.info(f"Launched profile scraper: {container_id}")
        return container_id
    
    def launch_linkedin_message_sender(self, message_text: str, profile_urls: List[str]) -> str:
        """
        Send LinkedIn messages (with connection request if not connected).
        
        Args:
            message_text: Message template with placeholders
            profile_urls: Target profile URLs
        
        Returns:
            container_id for tracking
        """
        agent_id = "3113123724622013"  # LinkedIn Message Sender
        
        data = {
            "agentId": agent_id,
            "arguments": {
                "sessionCookie": "YOUR_LINKEDIN_SESSION_COOKIE",
                "message": message_text,
                "profileUrls": profile_urls[:20],  # Daily limit safety
                "sendConnectionRequest": True,
                "connectionRequestMessage": "",
                "delay": random.randint(300, 900),  # 5-15 min delay
                "noDuplicate": True
            }
        }
        
        result = self._make_request("POST", f"agents/{agent_id}/launch", data)
        container_id = result.get("data", {}).get("containerId")
        
        logger.info(f"Launched message sender: {container_id}")
        return container_id
    
    def get_container_status(self, container_id: str) -> Dict:
        """Get status of a running/finished container."""
        result = self._make_request("GET", f"containers/{container_id}")
        return result.get("data", {})
    
    def get_container_output(self, container_id: str) -> List[Dict]:
        """Get output data from completed container."""
        # Poll until complete
        max_wait = 300  # 5 minutes max
        waited = 0
        
        while waited < max_wait:
            status = self.get_container_status(container_id)
            
            if status.get("status") == "finished":
                # Get the JSON output
                json_url = status.get("resultObject", {}).get("jsonUrl")
                if json_url:
                    response = requests.get(json_url)
                    return response.json() if response.status_code == 200 else []
                return []
            
            elif status.get("status") == "error":
                logger.error(f"Container {container_id} failed: {status.get('error')}")
                return []
            
            time.sleep(10)
            waited += 10
        
        logger.warning(f"Container {container_id} timed out")
        return []
    
    def safe_connection_request(self, profile_url: str, message: str = "") -> bool:
        """
        Send a single connection request safely with rate limiting.
        
        Returns True if scheduled successfully.
        """
        try:
            container_id = self.launch_linkedin_message_sender(
                message_text=message or "Hi, I'd love to connect!",
                profile_urls=[profile_url]
            )
            
            # Wait for completion
            output = self.get_container_output(container_id)
            
            if output and len(output) > 0:
                result = output[0]
                if result.get("status") == "success":
                    logger.info(f"Connection request sent to {profile_url}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error sending connection request: {e}")
            return False
    
    def extract_prospects_from_search(self, search_url: str, max_results: int = 50) -> List[Dict]:
        """
        Full pipeline: search LinkedIn and extract prospect data.
        
        Returns list of prospect dictionaries.
        """
        # Launch search
        container_id = self.launch_linkedin_network_search(search_url, max_results)
        
        # Get results
        results = self.get_container_output(container_id)
        
        prospects = []
        for profile in results:
            prospects.append({
                "name": f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip(),
                "title": profile.get('headline', ''),
                "company": profile.get('company', ''),
                "linkedin_url": profile.get('linkedinUrl', ''),
                "source": "phantombuster_linkedin",
                "discovered_at": time.strftime("%Y-%m-%dT%H:%M:%S")
            })
        
        logger.info(f"Extracted {len(prospects)} prospects from LinkedIn search")
        return prospects


class LinkedInSafetyMonitor:
    """Monitor LinkedIn account health and enforce safety limits."""
    
    def __init__(self, daily_limit: int = 20, weekly_limit: int = 100):
        self.daily_limit = daily_limit
        self.weekly_limit = weekly_limit
        self.today_count = 0
        self.week_count = 0
        self.last_reset = time.time()
    
    def can_send(self) -> bool:
        """Check if it's safe to send another connection request."""
        self._reset_if_needed()
        return (self.today_count < self.daily_limit and 
                self.week_count < self.weekly_limit)
    
    def record_send(self):
        """Record that a connection request was sent."""
        self.today_count += 1
        self.week_count += 1
    
    def _reset_if_needed(self):
        """Reset counters if day/week has passed."""
        now = time.time()
        day_seconds = 24 * 3600
        week_seconds = 7 * day_seconds
        
        if now - self.last_reset > day_seconds:
            self.today_count = 0
            
        if now - self.last_reset > week_seconds:
            self.week_count = 0
            self.last_reset = now
    
    def get_status(self) -> Dict:
        """Get current safety status."""
        self._reset_if_needed()
        return {
            "today_sent": self.today_count,
            "today_limit": self.daily_limit,
            "week_sent": self.week_count,
            "week_limit": self.weekly_limit,
            "safe_to_send": self.can_send()
        }


if __name__ == "__main__":
    # Test with dummy API key
    import os
    api_key = os.getenv("PHANTOMBUSTER_API_KEY", "test_key")
    
    if api_key != "test_key":
        client = PhantombusterLinkedIn(api_key)
        agents = client.list_agents()
        print(f"Found {len(agents)} agents")
    else:
        print("Set PHANTOMBUSTER_API_KEY to test")
