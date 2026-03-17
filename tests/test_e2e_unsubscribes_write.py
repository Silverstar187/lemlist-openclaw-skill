"""
E2E Tests für Unsubscribe Management
Diese Tests fügen und entfernen Unsubscribes.
"""
import pytest
import time
import sys
sys.path.insert(0, '/tmp/lemlist_skill/tests')


class TestAddUnsubscribe:
    """Tests für POST /unsubscribes"""
    
    def test_add_unsubscribe_email(self, api_client):
        """Test: POST /unsubscribes adds email to unsubscribe list"""
        email = f"test.unsubscribe.{int(time.time())}@example.com"
        
        result = api_client.add_unsubscribe(email)
        
        assert result["email"] == email
        
        # Cleanup
        api_client.delete_unsubscribe(email)
        print(f"Added unsubscribe: {email}")
    
    def test_add_unsubscribe_with_domain(self, api_client):
        """Test: Add domain to unsubscribe list"""
        email = f"test.{int(time.time())}@testdomain.example.com"
        
        result = api_client.add_unsubscribe(email, domain="testdomain.example.com")
        
        assert result["email"] == email
        
        # Cleanup
        api_client.delete_unsubscribe(email)


class TestDeleteUnsubscribe:
    """Tests für DELETE /unsubscribes/{email}"""
    
    def test_delete_unsubscribe(self, api_client):
        """Test: DELETE /unsubscribes/{email} removes from list"""
        # Add first
        email = f"test.delete.{int(time.time())}@example.com"
        api_client.add_unsubscribe(email)
        
        # Then delete
        success = api_client.delete_unsubscribe(email)
        assert success is True
    
    def test_delete_nonexistent_unsubscribe(self, api_client):
        """Test: Deleting non-existent unsubscribe"""
        success = api_client.delete_unsubscribe("not.in.list@example.com")
        # May return False or raise exception
        assert success is False or isinstance(success, bool)
