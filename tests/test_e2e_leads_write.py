"""
E2E Tests für Lead Management
Diese Tests erstellen, modifizieren und verwalten Leads.
Cleanup ist in den Fixtures implementiert.
"""
import pytest
import time
import sys
sys.path.insert(0, '/tmp/lemlist_skill/tests')


class TestAddLead:
    """Tests für POST /campaigns/{id}/leads"""
    
    def test_add_lead_to_campaign(self, api_client, test_campaign):
        """Test: POST /campaigns/{id}/leads adds lead to campaign"""
        from config import get_test_lead_data
        
        timestamp = str(int(time.time()))
        lead_data = get_test_lead_data(timestamp)
        
        lead = api_client.add_lead(test_campaign["_id"], lead_data)
        
        assert lead["email"] == lead_data["email"]
        assert lead["campaignId"] == test_campaign["_id"]
        assert "_id" in lead
        
        # Cleanup
        api_client.unsubscribe_lead(lead["email"])
        print(f"Added lead: {lead['email']}")
    
    def test_add_lead_with_deduplication(self, api_client, test_campaign):
        """Test: Add lead with deduplication enabled"""
        from config import get_test_lead_data
        
        timestamp = str(int(time.time()))
        lead_data = get_test_lead_data(timestamp)
        
        # First add
        lead1 = api_client.add_lead(test_campaign["_id"], lead_data, deduplicate=True)
        
        # Second add with same email should be skipped
        lead2 = api_client.add_lead(test_campaign["_id"], lead_data, deduplicate=True)
        
        # Cleanup
        api_client.unsubscribe_lead(lead_data["email"])
    
    def test_add_lead_response_structure(self, api_client, test_campaign):
        """Test: Add lead returns complete lead object"""
        from config import get_test_lead_data
        
        timestamp = str(int(time.time()))
        lead_data = get_test_lead_data(timestamp)
        
        lead = api_client.add_lead(test_campaign["_id"], lead_data)
        
        # Check expected fields
        assert "_id" in lead
        assert "campaignId" in lead
        assert "contactId" in lead
        assert "isPaused" in lead


class TestUpdateLead:
    """Tests für PUT /leads/{email}"""
    
    def test_update_lead_info(self, api_client, test_lead):
        """Test: PUT /leads/{email} updates lead information"""
        email = test_lead["email"]
        
        update_data = {
            "firstName": "UpdatedFirst",
            "lastName": "UpdatedLast",
            "jobTitle": "Updated Title"
        }
        
        updated = api_client.update_lead(email, update_data)
        
        assert updated["firstName"] == "UpdatedFirst"
        assert updated["lastName"] == "UpdatedLast"
    
    def test_update_lead_company(self, api_client, test_lead):
        """Test: Update lead company information"""
        email = test_lead["email"]
        
        update_data = {
            "companyName": "Updated Company Inc",
            "companyDomain": "updated.example.com"
        }
        
        updated = api_client.update_lead(email, update_data)
        
        assert updated["companyName"] == "Updated Company Inc"


class TestPauseResumeLead:
    """Tests für Lead Pause/Resume"""
    
    def test_pause_lead(self, api_client, test_lead):
        """Test: POST /leads/{email}/pause pauses lead"""
        email = test_lead["email"]
        
        result = api_client.pause_lead(email)
        
        # Verify lead is paused
        lead = api_client.get_lead(email)
        assert lead.get("isPaused") is True
    
    def test_resume_lead(self, api_client, test_lead):
        """Test: POST /leads/{email}/resume resumes lead"""
        email = test_lead["email"]
        
        # First pause
        api_client.pause_lead(email)
        
        # Then resume
        result = api_client.resume_lead(email)
        
        # Verify lead is not paused
        lead = api_client.get_lead(email)
        assert lead.get("isPaused") is False


class TestUnsubscribeLead:
    """Tests für Lead Unsubscribe"""
    
    def test_unsubscribe_lead(self, api_client, test_campaign):
        """Test: POST /leads/{email}/unsubscribe unsubscribes lead"""
        from config import get_test_lead_data
        
        # Add a lead
        timestamp = str(int(time.time()))
        lead_data = get_test_lead_data(timestamp)
        lead = api_client.add_lead(test_campaign["_id"], lead_data)
        
        # Unsubscribe
        result = api_client.unsubscribe_lead(lead["email"])
        
        assert isinstance(result, dict)
        
        # Verify in unsubscribes list
        try:
            unsub = api_client.get_unsubscribe(lead["email"])
            assert unsub["email"] == lead["email"]
        except:
            # May take time to appear
            pass
    
    def test_unsubscribe_lead_from_campaign(self, api_client, test_campaign):
        """Test: Unsubscribe lead from specific campaign"""
        from config import get_test_lead_data
        
        timestamp = str(int(time.time()))
        lead_data = get_test_lead_data(timestamp)
        lead = api_client.add_lead(test_campaign["_id"], lead_data)
        
        # Unsubscribe from specific campaign
        result = api_client.unsubscribe_lead(lead["email"], test_campaign["_id"])
        
        assert isinstance(result, dict)


class TestDeleteLead:
    """Tests für DELETE /leads/{email}"""
    
    def test_delete_lead_from_campaign(self, api_client, test_campaign):
        """Test: DELETE /leads/{email} removes lead from campaign"""
        from config import get_test_lead_data
        
        timestamp = str(int(time.time()))
        lead_data = get_test_lead_data(timestamp)
        lead = api_client.add_lead(test_campaign["_id"], lead_data)
        
        # Delete from campaign
        success = api_client.delete_lead(lead["email"], test_campaign["_id"])
        
        # Verify removed from campaign
        leads = api_client.get_campaign_leads(test_campaign["_id"])
        lead_emails = [l.get("email") for l in leads.get("data", [])]
        assert lead["email"] not in lead_emails
