#!/usr/bin/env python3
"""
Lemlist Lead Examples

This script demonstrates common lead operations using the Lemlist API.

Prerequisites:
    export LEMLIST_API_KEY="your_api_key_here"
    # Have at least one campaign to add leads to

Usage:
    python leads.py
"""

import os
import sys
import time
import requests
from requests.auth import HTTPBasicAuth

# Configuration
API_KEY = os.getenv("LEMLIST_API_KEY")
BASE_URL = "https://api.lemlist.com/api"

if not API_KEY:
    print("Error: LEMLIST_API_KEY environment variable not set")
    sys.exit(1)

auth = HTTPBasicAuth("", API_KEY)


def list_campaigns():
    """List all campaigns"""
    response = requests.get(f"{BASE_URL}/campaigns", auth=auth)
    response.raise_for_status()
    return response.json()


def get_campaign_leads(campaign_id):
    """Get leads in a campaign"""
    response = requests.get(
        f"{BASE_URL}/campaigns/{campaign_id}/leads",
        auth=auth
    )
    response.raise_for_status()
    return response.json()


def add_lead(campaign_id, lead_data):
    """Add a lead to a campaign"""
    response = requests.post(
        f"{BASE_URL}/campaigns/{campaign_id}/leads/",
        auth=auth,
        params={
            "deduplicate": "true",
            "findEmail": "false"
        },
        json=lead_data
    )
    response.raise_for_status()
    return response.json()


def get_lead_by_email(email):
    """Get lead by email address"""
    response = requests.get(
        f"{BASE_URL}/leads/{email}",
        auth=auth
    )
    response.raise_for_status()
    return response.json()


def update_lead(campaign_id, lead_id, updates):
    """Update a lead"""
    response = requests.patch(
        f"{BASE_URL}/campaigns/{campaign_id}/leads/{lead_id}",
        auth=auth,
        json=updates
    )
    response.raise_for_status()
    return response.json()


def pause_lead(lead_id, campaign_id=None):
    """Pause a lead"""
    params = {}
    if campaign_id:
        params["campaignId"] = campaign_id
    
    response = requests.post(
        f"{BASE_URL}/leads/pause/{lead_id}",
        auth=auth,
        params=params
    )
    response.raise_for_status()
    return response.json()


def resume_lead(lead_id, campaign_id=None):
    """Resume a paused lead"""
    params = {}
    if campaign_id:
        params["campaignId"] = campaign_id
    
    response = requests.post(
        f"{BASE_URL}/leads/start/{lead_id}",
        auth=auth,
        params=params
    )
    response.raise_for_status()
    return response.json()


def mark_interested(lead_id):
    """Mark lead as interested"""
    response = requests.post(
        f"{BASE_URL}/leads/interested/{lead_id}",
        auth=auth
    )
    response.raise_for_status()
    return response.json()


def mark_not_interested(lead_id):
    """Mark lead as not interested"""
    response = requests.post(
        f"{BASE_URL}/leads/notinterested/{lead_id}",
        auth=auth
    )
    response.raise_for_status()
    return response.json()


def unsubscribe_lead(campaign_id, email):
    """Unsubscribe a lead from a campaign"""
    response = requests.delete(
        f"{BASE_URL}/campaigns/{campaign_id}/leads/{email}",
        auth=auth
    )
    response.raise_for_status()
    return response.json()


def main():
    print("=" * 60)
    print("Lemlist Lead Examples")
    print("=" * 60)
    
    # Get a campaign to work with
    print("\n1. Finding a campaign...")
    campaigns = list_campaigns()
    
    if not campaigns:
        print("   No campaigns found. Please create a campaign first.")
        sys.exit(1)
    
    campaign = campaigns[0]
    campaign_id = campaign["_id"]
    print(f"   Using campaign: {campaign['name']} ({campaign_id})")
    
    # 2. List existing leads
    print("\n2. Listing existing leads...")
    leads = get_campaign_leads(campaign_id)
    print(f"   Found {len(leads)} leads in campaign")
    
    # 3. Add a test lead
    print("\n3. Adding test lead...")
    timestamp = int(time.time())
    lead_data = {
        "email": f"test.lead.{timestamp}@example.com",
        "firstName": "Test",
        "lastName": "Lead",
        "companyName": "Example Corp",
        "jobTitle": "Software Engineer",
        "linkedinUrl": "https://linkedin.com/in/testlead"
    }
    
    try:
        lead = add_lead(campaign_id, lead_data)
        lead_id = lead["_id"]
        print(f"   Added lead: {lead['firstName']} {lead['lastName']} ({lead_id})")
    except requests.HTTPError as e:
        print(f"   Error adding lead: {e}")
        print("   (Lead might already exist)")
        # Try to find existing lead
        try:
            lead = get_lead_by_email(lead_data["email"])
            lead_id = lead["_id"]
            print(f"   Using existing lead: {lead_id}")
        except:
            print("   Could not find existing lead")
            sys.exit(1)
    
    # 4. Get lead details
    print("\n4. Getting lead details...")
    lead_details = get_lead_by_email(lead_data["email"])
    print(f"   Email: {lead_details['email']}")
    print(f"   Company: {lead_details.get('companyName', 'N/A')}")
    print(f"   Status: {lead_details.get('emailStatus', 'N/A')}")
    
    # 5. Update lead
    print("\n5. Updating lead...")
    updated = update_lead(campaign_id, lead_id, {
        "jobTitle": "Senior Software Engineer"
    })
    print(f"   Updated job title to: {updated.get('jobTitle', 'N/A')}")
    
    # 6. Pause lead
    print("\n6. Pausing lead...")
    paused = pause_lead(lead_id, campaign_id)
    print(f"   Lead paused: {paused[0].get('isPaused', True)}")
    
    # 7. Resume lead
    print("\n7. Resuming lead...")
    resumed = resume_lead(lead_id, campaign_id)
    print(f"   Lead active: {not resumed[0].get('isPaused', False)}")
    
    # 8. Mark as interested
    print("\n8. Marking lead as interested...")
    interested = mark_interested(lead_id)
    print(f"   Lead marked as interested")
    
    # 9. Mark as not interested
    print("\n9. Marking lead as not interested...")
    not_interested = mark_not_interested(lead_id)
    print(f"   Lead marked as not interested")
    
    # 10. Unsubscribe lead
    print("\n10. Unsubscribing lead...")
    try:
        unsubscribed = unsubscribe_lead(campaign_id, lead_data["email"])
        print(f"   Lead unsubscribed successfully")
    except requests.HTTPError as e:
        print(f"   Note: {e}")
    
    print("\n" + "=" * 60)
    print("Lead examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
