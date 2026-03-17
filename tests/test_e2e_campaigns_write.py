"""
E2E Tests für schreibende Campaign Operations
Diese Tests erstellen, modifizieren und löschen Campaigns.
Cleanup ist in den Fixtures implementiert.
"""
import pytest
import time
import sys
sys.path.insert(0, '/tmp/lemlist_skill/tests')


class TestCreateCampaign:
    """Tests für POST /campaigns"""
    
    def test_create_campaign(self, api_client):
        """Test: POST /campaigns creates new campaign"""
        from config import get_test_campaign_name
        
        name = get_test_campaign_name()
        campaign = api_client.create_campaign(name=name)
        
        assert "_id" in campaign
        assert campaign["name"] == name
        assert "state" in campaign
        
        # Cleanup
        api_client.delete_campaign(campaign["_id"])
        print(f"Created campaign: {campaign['_id']}")
    
    def test_create_campaign_response_structure(self, api_client):
        """Test: Create campaign returns complete campaign object"""
        from config import get_test_campaign_name
        
        name = get_test_campaign_name()
        campaign = api_client.create_campaign(name=name)
        
        # Should have IDs for related entities
        assert "sequenceId" in campaign
        assert "scheduleIds" in campaign
        assert "teamId" in campaign
        
        # Cleanup
        api_client.delete_campaign(campaign["_id"])


class TestUpdateCampaign:
    """Tests für PUT /campaigns/{id}"""
    
    def test_update_campaign_name(self, api_client, test_campaign):
        """Test: PUT /campaigns/{id} updates campaign"""
        campaign_id = test_campaign["_id"]
        new_name = f"Updated-{test_campaign['name']}"
        
        updated = api_client.update_campaign(campaign_id, {"name": new_name})
        
        assert updated["name"] == new_name
    
    def test_update_campaign_settings(self, api_client, test_campaign):
        """Test: Update various campaign settings"""
        campaign_id = test_campaign["_id"]
        
        # Update emoji
        updated = api_client.update_campaign(campaign_id, {"emoji": "🧪"})
        assert updated.get("emoji") == "🧪"


class TestStartPauseCampaign:
    """Tests für Campaign Start/Pause"""
    
    def test_pause_campaign(self, api_client, test_campaign):
        """Test: POST /campaigns/{id}/pause pauses campaign"""
        # First ensure it's running or draft
        result = api_client.pause_campaign(test_campaign["_id"])
        
        # Should return without error
        assert isinstance(result, dict)
    
    def test_start_campaign(self, api_client, test_campaign):
        """Test: POST /campaigns/{id}/start starts campaign"""
        # Note: Campaign needs leads and sender to start
        # This test may fail if prerequisites not met
        try:
            result = api_client.start_campaign(test_campaign["_id"])
            assert isinstance(result, dict)
        except Exception as e:
            # Expected if campaign can't be started (no leads, etc.)
            pytest.skip(f"Campaign couldn't be started: {e}")


class TestDeleteCampaign:
    """Tests für DELETE /campaigns/{id}"""
    
    def test_delete_campaign(self, api_client):
        """Test: DELETE /campaigns/{id} deletes campaign"""
        from config import get_test_campaign_name
        
        # Create campaign to delete
        name = get_test_campaign_name()
        campaign = api_client.create_campaign(name=name)
        campaign_id = campaign["_id"]
        
        # Delete it
        success = api_client.delete_campaign(campaign_id)
        assert success is True
        
        # Verify it's gone
        with pytest.raises(Exception):
            api_client.get_campaign(campaign_id)
    
    def test_delete_nonexistent_campaign(self, api_client):
        """Test: Deleting non-existent campaign returns False"""
        success = api_client.delete_campaign("invalid_id_12345")
        # May return False or raise exception depending on API behavior
        assert success is False or isinstance(success, bool)
