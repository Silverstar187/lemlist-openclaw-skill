"""
Integration Tests für lesende Campaign Operations
Diese Tests führen nur GET Requests aus - keine Daten werden verändert.
"""
import pytest
import sys
sys.path.insert(0, '/tmp/lemlist_skill/tests')


class TestGetCampaigns:
    """Tests für GET /campaigns"""
    
    def test_get_campaigns_returns_list(self, api_client):
        """Test: GET /campaigns returns a list of campaigns"""
        campaigns = api_client.get_campaigns()
        
        # Should return a list
        assert isinstance(campaigns, list)
        print(f"Found {len(campaigns)} campaigns")
    
    def test_get_campaigns_pagination(self, api_client):
        """Test: Pagination parameters work correctly"""
        campaigns = api_client.get_campaigns(page=1, limit=5)
        
        assert isinstance(campaigns, list)
        assert len(campaigns) <= 5
    
    def test_get_campaigns_response_structure(self, api_client):
        """Test: Campaign objects have expected structure"""
        campaigns = api_client.get_campaigns(limit=1)
        
        if campaigns:
            campaign = campaigns[0]
            # Check expected fields
            assert "_id" in campaign
            assert "name" in campaign
            assert "state" in campaign
            print(f"Campaign structure: {list(campaign.keys())}")


class TestGetCampaign:
    """Tests für GET /campaigns/{id}"""
    
    def test_get_campaign_by_id(self, api_client, test_campaign):
        """Test: GET /campaigns/{id} returns campaign details"""
        campaign_id = test_campaign["_id"]
        campaign = api_client.get_campaign(campaign_id)
        
        assert campaign["_id"] == campaign_id
        assert "name" in campaign
        assert "state" in campaign
        print(f"Campaign: {campaign['name']} (State: {campaign['state']})")
    
    def test_get_campaign_not_found(self, api_client):
        """Test: GET /campaigns/{invalid_id} returns 404"""
        with pytest.raises(Exception) as exc_info:
            api_client.get_campaign("invalid_campaign_id_12345")
        
        assert "404" in str(exc_info.value) or "Not Found" in str(exc_info.value)


class TestGetCampaignStats:
    """Tests für GET /campaigns/{id}/stats"""
    
    def test_get_campaign_stats(self, api_client, test_campaign):
        """Test: GET /campaigns/{id}/stats returns statistics"""
        campaign_id = test_campaign["_id"]
        stats = api_client.get_campaign_stats(campaign_id)
        
        # Stats should be a dict
        assert isinstance(stats, dict)
        print(f"Campaign stats: {stats}")
    
    def test_get_campaign_stats_structure(self, api_client, test_campaign):
        """Test: Stats response has expected structure"""
        stats = api_client.get_campaign_stats(test_campaign["_id"])
        
        # Common stat fields (may vary based on campaign state)
        expected_fields = ["sent", "opened", "clicked", "replied"]
        for field in expected_fields:
            if field in stats:
                assert isinstance(stats[field], (int, type(None)))


class TestGetCampaignReports:
    """Tests für GET /campaigns/{id}/reports"""
    
    def test_get_campaign_reports(self, api_client, test_campaign):
        """Test: GET /campaigns/{id}/reports returns reports"""
        reports = api_client.get_campaign_reports(test_campaign["_id"])
        
        assert isinstance(reports, dict)
        print(f"Campaign reports keys: {list(reports.keys())}")


class TestGetCampaignSequences:
    """Tests für GET /campaigns/{id}/sequences"""
    
    def test_get_campaign_sequences(self, api_client, test_campaign):
        """Test: GET /campaigns/{id}/sequences returns sequences"""
        sequences = api_client.get_campaign_sequences(test_campaign["_id"])
        
        assert isinstance(sequences, list)
        print(f"Found {len(sequences)} sequences")
    
    def test_get_campaign_sequences_structure(self, api_client, test_campaign):
        """Test: Sequence objects have expected structure"""
        sequences = api_client.get_campaign_sequences(test_campaign["_id"])
        
        if sequences:
            seq = sequences[0]
            assert "_id" in seq
            print(f"Sequence structure: {list(seq.keys())}")


class TestGetCampaignSchedules:
    """Tests für GET /campaigns/{id}/schedules"""
    
    def test_get_campaign_schedules(self, api_client, test_campaign):
        """Test: GET /campaigns/{id}/schedules returns schedules"""
        schedules = api_client.get_campaign_schedules(test_campaign["_id"])
        
        assert isinstance(schedules, list)
        print(f"Found {len(schedules)} schedules")
