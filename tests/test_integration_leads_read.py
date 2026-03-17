"""
Integration Tests für lesende Lead Operations
Diese Tests führen nur GET Requests aus - keine Daten werden verändert.
"""
import pytest
import sys
sys.path.insert(0, '/tmp/lemlist_skill/tests')


class TestGetCampaignLeads:
    """Tests für GET /campaigns/{id}/leads"""
    
    def test_get_campaign_leads(self, api_client, test_campaign, test_lead):
        """Test: GET /campaigns/{id}/leads returns leads"""
        result = api_client.get_campaign_leads(test_campaign["_id"])
        
        # Response should have pagination structure
        assert "data" in result or isinstance(result, list)
        
        if "data" in result:
            leads = result["data"]
        else:
            leads = result
            
        assert isinstance(leads, list)
        print(f"Found {len(leads)} leads in campaign")
    
    def test_get_campaign_leads_pagination(self, api_client, test_campaign):
        """Test: Pagination works for leads"""
        result = api_client.get_campaign_leads(
            test_campaign["_id"],
            page=1,
            limit=5
        )
        
        if "data" in result:
            assert len(result["data"]) <= 5
        else:
            assert len(result) <= 5
    
    def test_get_campaign_leads_with_state_filter(self, api_client, test_campaign, test_lead):
        """Test: State filter works for leads"""
        result = api_client.get_campaign_leads(
            test_campaign["_id"],
            state="active"
        )
        
        # Should return without error
        assert "data" in result or isinstance(result, list)


class TestGetLead:
    """Tests für GET /leads/{emailOrId}"""
    
    def test_get_lead_by_email(self, api_client, test_lead):
        """Test: GET /leads/{email} returns lead details"""
        email = test_lead["email"]
        lead = api_client.get_lead(email)
        
        assert lead["email"] == email
        assert "_id" in lead
        print(f"Lead: {lead.get('firstName')} {lead.get('lastName')}")
    
    def test_get_lead_by_id(self, api_client, test_lead):
        """Test: GET /leads/{id} returns lead details"""
        lead_id = test_lead["_id"]
        lead = api_client.get_lead(lead_id)
        
        assert lead["_id"] == lead_id
    
    def test_get_lead_not_found(self, api_client):
        """Test: GET /leads/{invalid_email} returns 404"""
        with pytest.raises(Exception) as exc_info:
            api_client.get_lead("nonexistent@example.com")
        
        assert "404" in str(exc_info.value) or "Not Found" in str(exc_info.value)


class TestLeadResponseStructure:
    """Tests für Lead Response Struktur"""
    
    def test_lead_has_required_fields(self, api_client, test_lead):
        """Test: Lead object has all required fields"""
        lead = api_client.get_lead(test_lead["email"])
        
        required_fields = ["_id", "email", "campaignId"]
        for field in required_fields:
            assert field in lead, f"Missing field: {field}"
        
        # Optional but common fields
        optional_fields = ["firstName", "lastName", "companyName", "isPaused"]
        print(f"Lead fields present: {[f for f in optional_fields if f in lead]}")
