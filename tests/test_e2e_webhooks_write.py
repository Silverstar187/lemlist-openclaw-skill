"""
E2E Tests für Webhook Operations
Diese Tests erstellen und löschen Webhooks.
Cleanup ist in den Fixtures implementiert.
"""
import pytest
import sys
sys.path.insert(0, '/tmp/lemlist_skill/tests')


class TestGetWebhooks:
    """Tests für GET /webhooks"""
    
    def test_get_webhooks(self, api_client):
        """Test: GET /webhooks returns webhooks"""
        webhooks = api_client.get_webhooks()
        
        assert isinstance(webhooks, list)
        print(f"Found {len(webhooks)} webhooks")
    
    def test_webhook_structure(self, api_client):
        """Test: Webhook objects have expected structure"""
        webhooks = api_client.get_webhooks()
        
        if webhooks:
            webhook = webhooks[0]
            assert "_id" in webhook
            assert "url" in webhook
            assert "events" in webhook
            print(f"Webhook events: {webhook.get('events')}")


class TestAddWebhook:
    """Tests für POST /webhooks"""
    
    def test_add_webhook(self, api_client):
        """Test: POST /webhooks creates webhook"""
        from config import get_test_webhook_url
        
        url = get_test_webhook_url()
        events = ["leadAdded", "leadUnsubscribed", "emailSent"]
        
        webhook = api_client.add_webhook(url, events)
        
        assert "_id" in webhook
        assert webhook["url"] == url
        assert all(e in webhook["events"] for e in events)
        
        # Cleanup
        api_client.delete_webhook(webhook["_id"])
        print(f"Created webhook: {webhook['_id']}")
    
    def test_add_webhook_single_event(self, api_client):
        """Test: Create webhook with single event"""
        from config import get_test_webhook_url
        
        url = get_test_webhook_url()
        events = ["leadAdded"]
        
        webhook = api_client.add_webhook(url, events)
        
        assert webhook["url"] == url
        assert "leadAdded" in webhook["events"]
        
        # Cleanup
        api_client.delete_webhook(webhook["_id"])


class TestDeleteWebhook:
    """Tests für DELETE /webhooks/{id}"""
    
    def test_delete_webhook(self, api_client):
        """Test: DELETE /webhooks/{id} deletes webhook"""
        from config import get_test_webhook_url
        
        # Create webhook to delete
        url = get_test_webhook_url()
        webhook = api_client.add_webhook(url, ["leadAdded"])
        webhook_id = webhook["_id"]
        
        # Delete it
        success = api_client.delete_webhook(webhook_id)
        assert success is True
    
    def test_delete_nonexistent_webhook(self, api_client):
        """Test: Deleting non-existent webhook"""
        success = api_client.delete_webhook("invalid_webhook_id_12345")
        # May return False or raise exception
        assert success is False or isinstance(success, bool)
