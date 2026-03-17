#!/usr/bin/env python3
"""
Lemlist Inbox Examples

This script demonstrates inbox operations using the Lemlist API.

Prerequisites:
    export LEMLIST_API_KEY="your_api_key_here"

Usage:
    python inbox.py
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


def list_inboxes(user_id, page=1, limit=10):
    """List inbox conversations"""
    response = requests.get(
        f"{BASE_URL}/inbox",
        auth=auth,
        params={
            "userId": user_id,
            "page": page,
            "limit": limit
        }
    )
    response.raise_for_status()
    return response.json()


def get_contact_messages(contact_id, limit=10):
    """Get messages for a contact"""
    response = requests.get(
        f"{BASE_URL}/inbox/{contact_id}",
        auth=auth,
        params={"limit": limit}
    )
    response.raise_for_status()
    return response.json()


def list_labels():
    """List all labels"""
    response = requests.get(
        f"{BASE_URL}/inbox/labels",
        auth=auth
    )
    response.raise_for_status()
    return response.json()


def create_label(name):
    """Create a new label"""
    response = requests.post(
        f"{BASE_URL}/inbox/labels",
        auth=auth,
        json={"labelName": name}
    )
    response.raise_for_status()
    return response.json()


def attach_labels(contact_id, label_ids, append=True):
    """Attach labels to a conversation"""
    response = requests.post(
        f"{BASE_URL}/inbox/conversations/labels/{contact_id}",
        auth=auth,
        json={
            "labelIds": label_ids,
            "appendLabels": append
        }
    )
    response.raise_for_status()
    return response.json()


def remove_labels(contact_id, label_ids):
    """Remove labels from a conversation"""
    response = requests.delete(
        f"{BASE_URL}/inbox/conversations/labels/{contact_id}",
        auth=auth,
        json={"labelIds": label_ids}
    )
    response.raise_for_status()
    return response.json()


def create_draft(contact_id, owner_id, content, subject=None, channel="email"):
    """Create a draft message"""
    response = requests.post(
        f"{BASE_URL}/inbox/drafts/{contact_id}",
        auth=auth,
        params={"draftOwner": owner_id},
        json={
            "content": content,
            "subject": subject,
            "channel": channel
        }
    )
    response.raise_for_status()
    return response.json()


def list_drafts(contact_id, owner_id):
    """List drafts for a contact"""
    response = requests.get(
        f"{BASE_URL}/inbox/drafts/{contact_id}",
        auth=auth,
        params={"draftOwner": owner_id}
    )
    response.raise_for_status()
    return response.json()


def update_draft(contact_id, draft_id, owner_id, content, subject=None):
    """Update a draft"""
    data = {"content": content}
    if subject:
        data["subject"] = subject
    
    response = requests.patch(
        f"{BASE_URL}/inbox/drafts/{contact_id}/{draft_id}",
        auth=auth,
        params={"draftOwner": owner_id},
        json=data
    )
    response.raise_for_status()
    return response.json()


def delete_draft(contact_id, draft_id, owner_id):
    """Delete a draft"""
    response = requests.delete(
        f"{BASE_URL}/inbox/drafts/{contact_id}/{draft_id}",
        auth=auth,
        params={"draftOwner": owner_id}
    )
    response.raise_for_status()
    return response.json()


def get_team_info():
    """Get team info to find a user"""
    response = requests.get(
        f"{BASE_URL}/team",
        auth=auth
    )
    response.raise_for_status()
    return response.json()


def main():
    print("=" * 60)
    print("Lemlist Inbox Examples")
    print("=" * 60)
    
    # Get team info for user ID
    print("\n1. Getting team info...")
    team = get_team_info()
    
    if not team.get("users"):
        print("   No users found in team")
        sys.exit(1)
    
    user = team["users"][0]
    user_id = user["_id"]
    print(f"   Using user: {user.get('email', user_id)}")
    
    # 2. List inbox conversations
    print("\n2. Listing inbox conversations...")
    try:
        inboxes = list_inboxes(user_id, limit=5)
        conversations = inboxes.get("data", [])
        print(f"   Found {inboxes.get('pagination', {}).get('totalItems', 0)} total conversations")
        
        if conversations:
            for conv in conversations[:3]:
                contact = conv.get("contact", {})
                print(f"   - {contact.get('fullName', 'Unknown')} ({contact.get('email', 'N/A')})")
    except requests.HTTPError as e:
        print(f"   Could not list inboxes: {e}")
        conversations = []
    
    # 3. List labels
    print("\n3. Listing labels...")
    try:
        labels = list_labels()
        print(f"   Found {len(labels)} labels")
        for label in labels[:3]:
            print(f"   - {label['name']} ({label['_id']})")
    except requests.HTTPError as e:
        print(f"   Could not list labels: {e}")
        labels = []
    
    # 4. Create a test label
    print("\n4. Creating test label...")
    try:
        timestamp = int(time.time())
        label = create_label(f"Test Label {timestamp}")
        label_id = label["_id"]
        print(f"   Created label: {label['name']} ({label_id})")
    except requests.HTTPError as e:
        print(f"   Could not create label: {e}")
        label_id = None
    
    # 5. Work with drafts (if we have a conversation)
    if conversations:
        conversation = conversations[0]
        contact_id = conversation.get("contactId")
        
        print(f"\n5. Working with drafts for contact {contact_id}...")
        
        # Create draft
        print("   Creating draft...")
        try:
            draft = create_draft(
                contact_id=contact_id,
                owner_id=user_id,
                content="This is a test draft message created via API.",
                subject="Test Draft",
                channel="email"
            )
            draft_id = draft.get("_id")
            print(f"   Created draft: {draft_id}")
            
            # List drafts
            print("   Listing drafts...")
            drafts = list_drafts(contact_id, user_id)
            print(f"   Found {len(drafts.get('data', []))} drafts")
            
            # Update draft
            if draft_id:
                print("   Updating draft...")
                updated = update_draft(
                    contact_id=contact_id,
                    draft_id=draft_id,
                    owner_id=user_id,
                    content="This is the updated draft content."
                )
                print(f"   Draft updated")
                
                # Delete draft
                print("   Deleting draft...")
                delete_draft(contact_id, draft_id, user_id)
                print(f"   Draft deleted")
        
        except requests.HTTPError as e:
            print(f"   Draft operation failed: {e}")
    
    print("\n" + "=" * 60)
    print("Inbox examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
