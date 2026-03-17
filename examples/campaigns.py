#!/usr/bin/env python3
"""
Lemlist Campaign Examples

This script demonstrates common campaign operations using the Lemlist API.

Prerequisites:
    export LEMLIST_API_KEY="your_api_key_here"

Usage:
    python campaigns.py
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

# Setup authentication
auth = HTTPBasicAuth("", API_KEY)


def list_campaigns():
    """List all campaigns"""
    response = requests.get(
        f"{BASE_URL}/campaigns",
        auth=auth
    )
    response.raise_for_status()
    return response.json()


def get_campaign(campaign_id):
    """Get a specific campaign"""
    response = requests.get(
        f"{BASE_URL}/campaigns/{campaign_id}",
        auth=auth
    )
    response.raise_for_status()
    return response.json()


def create_campaign(name):
    """Create a new campaign"""
    response = requests.post(
        f"{BASE_URL}/campaigns",
        auth=auth,
        json={"name": name}
    )
    response.raise_for_status()
    return response.json()


def update_campaign(campaign_id, name):
    """Update campaign name"""
    response = requests.patch(
        f"{BASE_URL}/campaigns/{campaign_id}",
        auth=auth,
        json={"name": name}
    )
    response.raise_for_status()
    return response.json()


def start_campaign(campaign_id):
    """Start a campaign"""
    response = requests.post(
        f"{BASE_URL}/campaigns/{campaign_id}/start",
        auth=auth
    )
    response.raise_for_status()
    return response.json()


def pause_campaign(campaign_id):
    """Pause a campaign"""
    response = requests.post(
        f"{BASE_URL}/campaigns/{campaign_id}/pause",
        auth=auth
    )
    response.raise_for_status()
    return response.json()


def get_campaign_stats(campaign_id):
    """Get campaign statistics"""
    response = requests.get(
        f"{BASE_URL}/campaigns/{campaign_id}/stats",
        auth=auth
    )
    response.raise_for_status()
    return response.json()


def get_campaign_reports(campaign_ids):
    """Get reports for multiple campaigns"""
    ids = ",".join(campaign_ids)
    response = requests.get(
        f"{BASE_URL}/campaigns/reports",
        auth=auth,
        params={"campaignIds": ids}
    )
    response.raise_for_status()
    return response.json()


def delete_campaign(campaign_id):
    """Delete a campaign"""
    response = requests.delete(
        f"{BASE_URL}/campaigns/{campaign_id}",
        auth=auth
    )
    response.raise_for_status()
    return response.json()


def main():
    print("=" * 60)
    print("Lemlist Campaign Examples")
    print("=" * 60)
    
    # 1. List existing campaigns
    print("\n1. Listing existing campaigns...")
    campaigns = list_campaigns()
    print(f"   Found {len(campaigns)} campaigns")
    
    if campaigns:
        for camp in campaigns[:3]:  # Show first 3
            print(f"   - {camp['name']} ({camp['_id']}) - {camp['status']}")
    
    # 2. Create a test campaign
    print("\n2. Creating test campaign...")
    timestamp = int(time.time())
    campaign_name = f"Example Campaign {timestamp}"
    campaign = create_campaign(campaign_name)
    campaign_id = campaign["_id"]
    print(f"   Created: {campaign['name']} ({campaign_id})")
    
    # 3. Get campaign details
    print("\n3. Getting campaign details...")
    details = get_campaign(campaign_id)
    print(f"   Status: {details['status']}")
    print(f"   Created: {details['createdAt']}")
    
    # 4. Update campaign
    print("\n4. Updating campaign name...")
    updated = update_campaign(campaign_id, f"{campaign_name} - Updated")
    print(f"   New name: {updated['name']}")
    
    # 5. Get campaign stats (if campaign has activity)
    print("\n5. Getting campaign stats...")
    try:
        stats = get_campaign_stats(campaign_id)
        print(f"   Emails sent: {stats.get('emailsSent', 0)}")
        print(f"   Emails opened: {stats.get('emailsOpened', 0)}")
    except requests.HTTPError as e:
        print(f"   No stats yet (campaign is new)")
    
    # 6. Get reports for all campaigns
    print("\n6. Getting campaign reports...")
    all_ids = [c["_id"] for c in campaigns[:5]]  # First 5
    if all_ids:
        reports = get_campaign_reports(all_ids)
        print(f"   Got reports for {len(reports)} campaigns")
        for report in reports[:2]:
            print(f"   - {report['name']}: {report.get('emailsSent', 0)} sent")
    
    # 7. Cleanup - delete test campaign
    print("\n7. Cleaning up - deleting test campaign...")
    delete_campaign(campaign_id)
    print(f"   Deleted campaign {campaign_id}")
    
    print("\n" + "=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
