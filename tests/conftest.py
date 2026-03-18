"""
Shared Fixtures für Lemlist Tests
"""
import pytest
import time
from datetime import datetime
from typing import Generator

# Import client and config
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from lemlist_client import LemlistClient
from config import get_test_campaign_name, get_test_lead_data


@pytest.fixture(scope="session")
def api_client() -> LemlistClient:
    """
    Shared API client for all tests.
    Requires LEMLIST_API_KEY environment variable.
    """
    client = LemlistClient()
    yield client


@pytest.fixture(scope="session")
def test_user_id(api_client: LemlistClient) -> str:
    """
    Get a valid user ID from the team for testing.
    Cached for the entire test session.
    """
    team = api_client.get_team()
    # Get first user from team
    users = team.get("users", [])
    if not users:
        pytest.skip("No users found in team")
    return users[0].get("_id")


@pytest.fixture(scope="function")
def test_campaign(api_client: LemlistClient) -> Generator[dict, None, None]:
    """
    Creates a test campaign and cleans up after test.
    Yields the campaign object.
    """
    name = get_test_campaign_name()
    campaign = None
    
    try:
        campaign = api_client.create_campaign(name=name)
        yield campaign
    finally:
        # Cleanup - always try to delete
        if campaign and "_id" in campaign:
            try:
                # First pause if running
                api_client.pause_campaign(campaign["_id"])
            except:
                pass
            
            try:
                api_client.delete_campaign(campaign["_id"])
            except Exception as e:
                print(f"Warning: Could not delete campaign {campaign['_id']}: {e}")


@pytest.fixture(scope="function")
def test_lead(api_client: LemlistClient, test_campaign: dict) -> Generator[dict, None, None]:
    """
    Creates a test lead in the test campaign.
    Cleans up by unsubscribing after test.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    lead_data = get_test_lead_data(timestamp)
    lead = None
    
    try:
        lead = api_client.add_lead(test_campaign["_id"], lead_data)
        yield lead
    finally:
        # Cleanup - unsubscribe lead
        if lead and "email" in lead:
            try:
                api_client.unsubscribe_lead(lead["email"])
            except Exception as e:
                print(f"Warning: Could not unsubscribe lead {lead['email']}: {e}")


@pytest.fixture(scope="function")
def test_draft(api_client: LemlistClient, test_user_id: str) -> Generator[dict, None, None]:
    """
    Creates a test draft and cleans up after test.
    Note: Requires an existing contact_id - using inbox contact if available.
    """
    draft = None
    
    try:
        # Get first inbox conversation to use as contact
        inbox = api_client.get_inbox(test_user_id, limit=1)
        conversations = inbox.get("data", [])
        
        if not conversations:
            pytest.skip("No inbox conversations available for draft testing")
        
        contact_id = conversations[0].get("contactId")
        
        draft_data = {
            "subject": f"Test Draft {datetime.now().strftime('%H%M%S')}",
            "body": "This is a test draft created by automated tests."
        }
        
        draft = api_client.create_draft(contact_id, draft_data)
        yield draft
        
    finally:
        # Cleanup
        if draft and "_id" in draft:
            try:
                api_client.delete_draft(draft["_id"])
            except Exception as e:
                print(f"Warning: Could not delete draft {draft['_id']}: {e}")


@pytest.fixture(scope="function")
def test_webhook(api_client: LemlistClient) -> Generator[dict, None, None]:
    """
    Creates a test webhook and cleans up after test.
    """
    from config import get_test_webhook_url
    
    webhook = None
    
    try:
        webhook = api_client.add_webhook(
            url=get_test_webhook_url(),
            events=["leadAdded", "leadUnsubscribed"]
        )
        yield webhook
    finally:
        # Cleanup
        if webhook and "_id" in webhook:
            try:
                api_client.delete_webhook(webhook["_id"])
            except Exception as e:
                print(f"Warning: Could not delete webhook {webhook['_id']}: {e}")
