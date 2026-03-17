"""
Integration Tests für Unsubscribes
Diese Tests führen nur GET Requests aus - keine Daten werden verändert.
"""
import pytest
import sys
sys.path.insert(0, '/tmp/lemlist_skill/tests')


class TestGetUnsubscribes:
    """Tests für GET /unsubscribes"""
    
    def test_get_unsubscribes(self, api_client):
        """Test: GET /unsubscribes returns unsubscribed emails"""
        result = api_client.get_unsubscribes()
        
        assert isinstance(result, dict)
        assert "data" in result or isinstance(result.get("data"), list)
        
        if "data" in result:
            print(f"Found {len(result['data'])} unsubscribes")
        elif "unsubscribes" in result:
            print(f"Found {len(result['unsubscribes'])} unsubscribes")
    
    def test_get_unsubscribes_pagination(self, api_client):
        """Test: Pagination works for unsubscribes"""
        result = api_client.get_unsubscribes(page=1, limit=5)
        
        if "data" in result:
            assert len(result["data"]) <= 5
    
    def test_unsubscribe_structure(self, api_client):
        """Test: Unsubscribe objects have expected structure"""
        result = api_client.get_unsubscribes(limit=1)
        
        data = result.get("data", result.get("unsubscribes", []))
        
        if data:
            unsub = data[0]
            # Should have email or domain
            assert "email" in unsub or "domain" in unsub
            print(f"Unsubscribe structure: {list(unsub.keys())}")


class TestGetUnsubscribeByEmail:
    """Tests für GET /unsubscribes/{email}"""
    
    def test_get_unsubscribe_not_found(self, api_client):
        """Test: GET /unsubscribes/{email} for non-existent email"""
        # This will likely return 404 or empty result
        try:
            result = api_client.get_unsubscribe("notunsubscribed@example.com")
            # If it doesn't raise, check response
            print(f"Unsubscribe check result: {result}")
        except Exception as e:
            # 404 is expected for non-unsubscribed emails
            assert "404" in str(e) or "Not Found" in str(e)
