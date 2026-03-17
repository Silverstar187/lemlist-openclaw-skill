"""
Integration Tests für Activities und Tasks
Diese Tests führen nur GET Requests aus - keine Daten werden verändert.
"""
import pytest
import sys
sys.path.insert(0, '/tmp/lemlist_skill/tests')


class TestGetActivities:
    """Tests für GET /activities"""
    
    def test_get_activities(self, api_client):
        """Test: GET /activities returns activities"""
        result = api_client.get_activities()
        
        assert isinstance(result, dict)
        assert "data" in result or "activities" in result
        print(f"Activities response keys: {list(result.keys())}")
    
    def test_get_activities_with_campaign_filter(self, api_client, test_campaign):
        """Test: Filter activities by campaign"""
        result = api_client.get_activities(campaign_id=test_campaign["_id"])
        
        # Should return without error
        assert isinstance(result, dict)
    
    def test_get_activities_with_type_filter(self, api_client):
        """Test: Filter activities by type"""
        # Common activity types: email_sent, email_opened, email_clicked, etc.
        result = api_client.get_activities(activity_type="email_sent")
        
        assert isinstance(result, dict)
    
    def test_get_activities_pagination(self, api_client):
        """Test: Pagination works for activities"""
        result = api_client.get_activities(page=1, limit=5)
        
        if "data" in result:
            assert len(result["data"]) <= 5


class TestGetTasks:
    """Tests für GET /tasks"""
    
    def test_get_tasks(self, api_client):
        """Test: GET /tasks returns pending tasks"""
        result = api_client.get_tasks()
        
        assert isinstance(result, dict)
        assert "data" in result or "tasks" in result
        print(f"Tasks response keys: {list(result.keys())}")
    
    def test_get_tasks_pagination(self, api_client):
        """Test: Pagination works for tasks"""
        result = api_client.get_tasks(page=1, limit=5)
        
        if "data" in result:
            assert len(result["data"]) <= 5
    
    def test_task_structure(self, api_client):
        """Test: Task objects have expected structure"""
        result = api_client.get_tasks(limit=1)
        
        data_key = "data" if "data" in result else "tasks"
        
        if result.get(data_key):
            task = result[data_key][0]
            assert "_id" in task
            print(f"Task structure: {list(task.keys())}")
