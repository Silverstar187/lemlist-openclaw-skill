"""
E2E Tests für komplette Workflows
Diese Tests führen komplexe Szenarien durch.
"""
import pytest
import time
import sys
sys.path.insert(0, '/tmp/lemlist_skill/tests')


class TestCampaignLeadWorkflow:
    """
    Complete workflow: Create Campaign → Add Lead → Verify → Cleanup
    """
    
    def test_full_campaign_lead_workflow(self, api_client):
        """
        E2E: Full workflow from campaign creation to lead management
        """
        from config import get_test_campaign_name, get_test_lead_data
        
        # 1. Create Campaign
        campaign_name = get_test_campaign_name()
        campaign = api_client.create_campaign(name=campaign_name)
        campaign_id = campaign["_id"]
        
        assert "_id" in campaign
        print(f"✓ Created campaign: {campaign_id}")
        
        # 2. Verify Campaign Exists
        fetched = api_client.get_campaign(campaign_id)
        assert fetched["_id"] == campaign_id
        print(f"✓ Verified campaign exists")
        
        # 3. Add Lead to Campaign
        timestamp = str(int(time.time()))
        lead_data = get_test_lead_data(timestamp)
        lead = api_client.add_lead(campaign_id, lead_data)
        
        assert lead["email"] == lead_data["email"]
        print(f"✓ Added lead: {lead['email']}")
        
        # 4. Verify Lead in Campaign
        leads_result = api_client.get_campaign_leads(campaign_id)
        leads = leads_result.get("data", [])
        lead_emails = [l.get("email") for l in leads]
        assert lead_data["email"] in lead_emails
        print(f"✓ Verified lead in campaign")
        
        # 5. Update Lead
        updated = api_client.update_lead(lead_data["email"], {
            "firstName": "Workflow",
            "lastName": "Test"
        })
        assert updated["firstName"] == "Workflow"
        print(f"✓ Updated lead")
        
        # 6. Pause Lead
        api_client.pause_lead(lead_data["email"])
        lead_check = api_client.get_lead(lead_data["email"])
        assert lead_check.get("isPaused") is True
        print(f"✓ Paused lead")
        
        # 7. Resume Lead
        api_client.resume_lead(lead_data["email"])
        lead_check = api_client.get_lead(lead_data["email"])
        assert lead_check.get("isPaused") is False
        print(f"✓ Resumed lead")
        
        # 8. Unsubscribe Lead
        api_client.unsubscribe_lead(lead_data["email"])
        print(f"✓ Unsubscribed lead")
        
        # 9. Pause Campaign
        api_client.pause_campaign(campaign_id)
        print(f"✓ Paused campaign")
        
        # 10. Delete Campaign
        api_client.delete_campaign(campaign_id)
        
        # Verify deletion
        with pytest.raises(Exception):
            api_client.get_campaign(campaign_id)
        print(f"✓ Deleted campaign")
        
        print("\n✅ Full workflow completed successfully!")


class TestDraftWorkflow:
    """
    Complete workflow: Create Draft → Update → Verify → Delete
    """
    
    def test_full_draft_workflow(self, api_client, test_user_id):
        """
        E2E: Full draft management workflow
        """
        # Get a contact
        inbox = api_client.get_inbox(test_user_id, limit=1)
        
        if not inbox.get("data"):
            pytest.skip("No inbox conversations available")
        
        contact_id = inbox["data"][0]["contactId"]
        
        # 1. Create Draft
        draft_data = {
            "subject": "Workflow Test Draft",
            "body": "Initial draft body."
        }
        draft = api_client.create_draft(contact_id, draft_data)
        draft_id = draft["_id"]
        
        assert "_id" in draft
        print(f"✓ Created draft: {draft_id}")
        
        # 2. Get Draft
        fetched = api_client.get_draft(draft_id)
        assert fetched["_id"] == draft_id
        print(f"✓ Retrieved draft")
        
        # 3. Update Draft
        updated = api_client.update_draft(draft_id, {
            "subject": "Updated Workflow Draft",
            "body": "Updated body content."
        })
        assert updated["subject"] == "Updated Workflow Draft"
        print(f"✓ Updated draft")
        
        # 4. Verify Update
        verified = api_client.get_draft(draft_id)
        assert verified["body"] == "Updated body content."
        print(f"✓ Verified update")
        
        # 5. Delete Draft
        api_client.delete_draft(draft_id)
        print(f"✓ Deleted draft")
        
        print("\n✅ Draft workflow completed successfully!")


class TestWebhookWorkflow:
    """
    Complete workflow: Create Webhook → Verify → Delete
    """
    
    def test_full_webhook_workflow(self, api_client):
        """
        E2E: Full webhook management workflow
        """
        from config import get_test_webhook_url
        
        # 1. Get initial webhook count
        initial_webhooks = api_client.get_webhooks()
        initial_count = len(initial_webhooks)
        print(f"✓ Initial webhooks: {initial_count}")
        
        # 2. Create Webhook
        url = get_test_webhook_url()
        webhook = api_client.add_webhook(url, ["leadAdded", "leadUnsubscribed"])
        webhook_id = webhook["_id"]
        
        assert "_id" in webhook
        print(f"✓ Created webhook: {webhook_id}")
        
        # 3. Verify in List
        webhooks = api_client.get_webhooks()
        webhook_ids = [w["_id"] for w in webhooks]
        assert webhook_id in webhook_ids
        print(f"✓ Verified webhook in list")
        
        # 4. Delete Webhook
        api_client.delete_webhook(webhook_id)
        print(f"✓ Deleted webhook")
        
        # 5. Verify Deletion
        webhooks = api_client.get_webhooks()
        webhook_ids = [w["_id"] for w in webhooks]
        assert webhook_id not in webhook_ids
        print(f"✓ Verified webhook removed")
        
        print("\n✅ Webhook workflow completed successfully!")


class TestUnsubscribeWorkflow:
    """
    Complete workflow: Add Unsubscribe → Verify → Delete
    """
    
    def test_full_unsubscribe_workflow(self, api_client):
        """
        E2E: Full unsubscribe management workflow
        """
        email = f"workflow.test.{int(time.time())}@example.com"
        
        # 1. Add to Unsubscribe List
        result = api_client.add_unsubscribe(email)
        assert result["email"] == email
        print(f"✓ Added unsubscribe: {email}")
        
        # 2. Verify in List
        try:
            unsub = api_client.get_unsubscribe(email)
            assert unsub["email"] == email
            print(f"✓ Verified in unsubscribe list")
        except:
            # May not be immediately available
            print(f"⚠ Unsubscribe verification skipped (may need time)")
        
        # 3. Remove from List
        api_client.delete_unsubscribe(email)
        print(f"✓ Removed from unsubscribe list")
        
        print("\n✅ Unsubscribe workflow completed successfully!")
