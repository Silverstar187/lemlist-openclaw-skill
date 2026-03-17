"""
Lemlist API Client - Basis-Implementation für Tests
"""
import base64
import time
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime


class LemlistClient:
    """HTTP Client für Lemlist API"""
    
    BASE_URL = "https://api.lemlist.com/api"
    RATE_LIMIT_REQUESTS = 20
    RATE_LIMIT_WINDOW = 2  # seconds
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Lemlist client
        
        Args:
            api_key: Lemlist API key. If not provided, reads from LEMLIST_API_KEY env var
        """
        import os
        self.api_key = api_key or os.getenv("LEMLIST_API_KEY")
        if not self.api_key:
            raise ValueError("API key required. Set LEMLIST_API_KEY env var or pass to constructor.")
        
        # Basic Auth: :API_KEY (empty username, colon before key)
        auth_string = f":{self.api_key}"
        auth_bytes = base64.b64encode(auth_string.encode()).decode()
        
        self.headers = {
            "Authorization": f"Basic {auth_bytes}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Rate limiting
        self._last_request_time = 0
        self._request_count = 0
        self._window_start = 0
    
    def _handle_rate_limit(self):
        """Ensure we don't exceed rate limits (20 req / 2 sec)"""
        current_time = time.time()
        
        # Reset window if needed
        if current_time - self._window_start >= self.RATE_LIMIT_WINDOW:
            self._window_start = current_time
            self._request_count = 0
        
        # Check if we need to wait
        if self._request_count >= self.RATE_LIMIT_REQUESTS:
            sleep_time = self.RATE_LIMIT_WINDOW - (current_time - self._window_start)
            if sleep_time > 0:
                time.sleep(sleep_time)
            self._window_start = time.time()
            self._request_count = 0
        
        self._request_count += 1
    
    def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        max_retries: int = 3
    ) -> requests.Response:
        """
        Make HTTP request with retry logic
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_data: JSON body
            max_retries: Maximum retry attempts
            
        Returns:
            Response object
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        for attempt in range(max_retries):
            self._handle_rate_limit()
            
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    timeout=30
                )
                
                # Handle rate limit response
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 2))
                    time.sleep(retry_after)
                    continue
                
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return response
    
    # ==================== CAMPAIGNS ====================
    
    def get_campaigns(self, page: int = 1, limit: int = 10) -> List[Dict]:
        """Get all campaigns"""
        response = self._request("GET", "/campaigns", params={"page": page, "limit": limit})
        response.raise_for_status()
        return response.json()
    
    def get_campaign(self, campaign_id: str) -> Dict:
        """Get specific campaign by ID"""
        response = self._request("GET", f"/campaigns/{campaign_id}")
        response.raise_for_status()
        return response.json()
    
    def get_campaign_stats(self, campaign_id: str) -> Dict:
        """Get campaign statistics"""
        response = self._request("GET", f"/campaigns/{campaign_id}/stats")
        response.raise_for_status()
        return response.json()
    
    def get_campaign_reports(self, campaign_id: str) -> Dict:
        """Get campaign reports"""
        response = self._request("GET", f"/campaigns/{campaign_id}/reports")
        response.raise_for_status()
        return response.json()
    
    def get_campaign_sequences(self, campaign_id: str) -> List[Dict]:
        """Get campaign sequences"""
        response = self._request("GET", f"/campaigns/{campaign_id}/sequences")
        response.raise_for_status()
        return response.json()
    
    def get_campaign_schedules(self, campaign_id: str) -> List[Dict]:
        """Get campaign schedules"""
        response = self._request("GET", f"/campaigns/{campaign_id}/schedules")
        response.raise_for_status()
        return response.json()
    
    def create_campaign(self, name: str) -> Dict:
        """Create a new campaign"""
        response = self._request("POST", "/campaigns", json_data={"name": name})
        response.raise_for_status()
        return response.json()
    
    def update_campaign(self, campaign_id: str, data: Dict) -> Dict:
        """Update campaign settings"""
        response = self._request("PUT", f"/campaigns/{campaign_id}", json_data=data)
        response.raise_for_status()
        return response.json()
    
    def start_campaign(self, campaign_id: str) -> Dict:
        """Start or resume a campaign"""
        response = self._request("POST", f"/campaigns/{campaign_id}/start")
        response.raise_for_status()
        return response.json()
    
    def pause_campaign(self, campaign_id: str) -> Dict:
        """Pause a running campaign"""
        response = self._request("POST", f"/campaigns/{campaign_id}/pause")
        response.raise_for_status()
        return response.json()
    
    def delete_campaign(self, campaign_id: str) -> bool:
        """Delete a campaign"""
        response = self._request("DELETE", f"/campaigns/{campaign_id}")
        return response.status_code == 200
    
    # ==================== LEADS ====================
    
    def get_campaign_leads(
        self, 
        campaign_id: str, 
        page: int = 1, 
        limit: int = 10,
        state: Optional[str] = None
    ) -> Dict:
        """Get leads from a campaign"""
        params = {"page": page, "limit": limit}
        if state:
            params["state"] = state
        response = self._request("GET", f"/campaigns/{campaign_id}/leads", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_lead(self, email_or_id: str) -> Dict:
        """Get lead by email or ID"""
        response = self._request("GET", f"/leads/{email_or_id}")
        response.raise_for_status()
        return response.json()
    
    def add_lead(
        self, 
        campaign_id: str, 
        lead_data: Dict,
        deduplicate: bool = False
    ) -> Dict:
        """
        Add a lead to a campaign
        
        Args:
            campaign_id: Campaign ID
            lead_data: Dict with email, firstName, lastName, etc.
            deduplicate: Skip if email exists in other campaigns
        """
        params = {"deduplicate": str(deduplicate).lower()}
        response = self._request(
            "POST", 
            f"/campaigns/{campaign_id}/leads/",
            params=params,
            json_data=lead_data
        )
        response.raise_for_status()
        return response.json()
    
    def update_lead(self, email: str, data: Dict) -> Dict:
        """Update lead information"""
        response = self._request("PUT", f"/leads/{email}", json_data=data)
        response.raise_for_status()
        return response.json()
    
    def delete_lead(self, email: str, campaign_id: Optional[str] = None) -> bool:
        """Remove lead from campaign or unsubscribe completely"""
        params = {}
        if campaign_id:
            params["campaignId"] = campaign_id
        response = self._request("DELETE", f"/leads/{email}", params=params)
        return response.status_code == 200
    
    def unsubscribe_lead(self, email: str, campaign_id: Optional[str] = None) -> Dict:
        """Unsubscribe a lead"""
        endpoint = f"/leads/{email}/unsubscribe"
        if campaign_id:
            endpoint = f"/campaigns/{campaign_id}/leads/{email}/unsubscribe"
        response = self._request("POST", endpoint)
        response.raise_for_status()
        return response.json()
    
    def pause_lead(self, email: str, campaign_id: Optional[str] = None) -> Dict:
        """Pause a lead"""
        params = {}
        if campaign_id:
            params["campaignId"] = campaign_id
        response = self._request("POST", f"/leads/{email}/pause", params=params)
        response.raise_for_status()
        return response.json()
    
    def resume_lead(self, email: str, campaign_id: Optional[str] = None) -> Dict:
        """Resume a paused lead"""
        params = {}
        if campaign_id:
            params["campaignId"] = campaign_id
        response = self._request("POST", f"/leads/{email}/resume", params=params)
        response.raise_for_status()
        return response.json()
    
    # ==================== TEAM ====================
    
    def get_team(self) -> Dict:
        """Get team information"""
        response = self._request("GET", "/team")
        response.raise_for_status()
        return response.json()
    
    def get_team_senders(self) -> List[Dict]:
        """Get team senders"""
        response = self._request("GET", "/team/senders")
        response.raise_for_status()
        return response.json()
    
    def get_team_credits(self) -> Dict:
        """Get team credits balance"""
        response = self._request("GET", "/team/credits")
        response.raise_for_status()
        return response.json()
    
    def get_user(self, user_id: str) -> Dict:
        """Get user information"""
        response = self._request("GET", f"/users/{user_id}")
        response.raise_for_status()
        return response.json()
    
    def get_user_channels(self, user_id: str) -> Dict:
        """Get user connected channels"""
        response = self._request("GET", f"/users/{user_id}/channels")
        response.raise_for_status()
        return response.json()
    
    # ==================== INBOX ====================
    
    def get_inbox(
        self, 
        user_id: str,
        page: int = 1, 
        limit: int = 10
    ) -> Dict:
        """Get inbox conversations"""
        params = {"userId": user_id, "page": page, "limit": limit}
        response = self._request("GET", "/inbox", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_contact_messages(self, contact_id: str) -> List[Dict]:
        """Get messages for a contact"""
        response = self._request("GET", f"/inbox/{contact_id}/messages")
        response.raise_for_status()
        return response.json()
    
    def get_labels(self) -> List[Dict]:
        """Get all labels"""
        response = self._request("GET", "/labels")
        response.raise_for_status()
        return response.json()
    
    def get_label(self, label_id: str) -> Dict:
        """Get specific label"""
        response = self._request("GET", f"/labels/{label_id}")
        response.raise_for_status()
        return response.json()
    
    def create_draft(self, contact_id: str, draft_data: Dict) -> Dict:
        """Create a draft message"""
        response = self._request(
            "POST", 
            "/inbox/drafts",
            json_data={"contactId": contact_id, **draft_data}
        )
        response.raise_for_status()
        return response.json()
    
    def get_draft(self, draft_id: str) -> Dict:
        """Get a specific draft"""
        response = self._request("GET", f"/inbox/drafts/{draft_id}")
        response.raise_for_status()
        return response.json()
    
    def update_draft(self, draft_id: str, draft_data: Dict) -> Dict:
        """Update a draft"""
        response = self._request(
            "PUT",
            f"/inbox/drafts/{draft_id}",
            json_data=draft_data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_draft(self, draft_id: str) -> bool:
        """Delete a draft"""
        response = self._request("DELETE", f"/inbox/drafts/{draft_id}")
        return response.status_code == 200
    
    # ==================== ACTIVITIES ====================
    
    def get_activities(
        self,
        campaign_id: Optional[str] = None,
        activity_type: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Dict:
        """Get activities"""
        params = {"page": page, "limit": limit}
        if campaign_id:
            params["campaignId"] = campaign_id
        if activity_type:
            params["type"] = activity_type
        response = self._request("GET", "/activities", params=params)
        response.raise_for_status()
        return response.json()
    
    # ==================== TASKS ====================
    
    def get_tasks(
        self,
        page: int = 1,
        limit: int = 10
    ) -> Dict:
        """Get pending tasks"""
        params = {"page": page, "limit": limit}
        response = self._request("GET", "/tasks", params=params)
        response.raise_for_status()
        return response.json()
    
    def create_task(self, task_data: Dict) -> Dict:
        """Create a manual task"""
        response = self._request("POST", "/tasks", json_data=task_data)
        response.raise_for_status()
        return response.json()
    
    def update_task(self, task_id: str, task_data: Dict) -> Dict:
        """Update a task"""
        response = self._request("PUT", f"/tasks/{task_id}", json_data=task_data)
        response.raise_for_status()
        return response.json()
    
    # ==================== UNSUBSCRIBES ====================
    
    def get_unsubscribes(
        self,
        page: int = 1,
        limit: int = 10
    ) -> Dict:
        """Get unsubscribed emails"""
        params = {"page": page, "limit": limit}
        response = self._request("GET", "/unsubscribes", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_unsubscribe(self, email: str) -> Dict:
        """Get unsubscribe info for email"""
        response = self._request("GET", f"/unsubscribes/{email}")
        response.raise_for_status()
        return response.json()
    
    def add_unsubscribe(self, email: str, domain: Optional[str] = None) -> Dict:
        """Add email or domain to unsubscribe list"""
        data = {"email": email}
        if domain:
            data["domain"] = domain
        response = self._request("POST", "/unsubscribes", json_data=data)
        response.raise_for_status()
        return response.json()
    
    def delete_unsubscribe(self, email: str) -> bool:
        """Remove email from unsubscribe list"""
        response = self._request("DELETE", f"/unsubscribes/{email}")
        return response.status_code == 200
    
    # ==================== WEBHOOKS ====================
    
    def get_webhooks(self) -> List[Dict]:
        """Get all webhooks"""
        response = self._request("GET", "/webhooks")
        response.raise_for_status()
        return response.json()
    
    def add_webhook(self, url: str, events: List[str]) -> Dict:
        """Create a webhook"""
        response = self._request(
            "POST",
            "/webhooks",
            json_data={"url": url, "events": events}
        )
        response.raise_for_status()
        return response.json()
    
    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook"""
        response = self._request("DELETE", f"/webhooks/{webhook_id}")
        return response.status_code == 200
