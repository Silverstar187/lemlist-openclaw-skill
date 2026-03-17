"""
Integration Tests für Inbox Operations
Diese Tests führen nur GET Requests aus - keine Daten werden verändert.
"""
import pytest
import sys
sys.path.insert(0, '/tmp/lemlist_skill/tests')


class TestGetInbox:
    """Tests für GET /inbox"""
    
    def test_get_inbox(self, api_client, test_user_id):
        """Test: GET /inbox returns conversations"""
        result = api_client.get_inbox(test_user_id)
        
        assert isinstance(result, dict)
        assert "data" in result
        assert isinstance(result["data"], list)
        print(f"Found {len(result['data'])} inbox conversations")
    
    def test_get_inbox_pagination(self, api_client, test_user_id):
        """Test: Pagination works for inbox"""
        result = api_client.get_inbox(test_user_id, page=1, limit=5)
        
        assert len(result["data"]) <= 5
        
        # Check pagination info
        if "pagination" in result:
            pagination = result["pagination"]
            print(f"Pagination: {pagination}")
    
    def test_inbox_conversation_structure(self, api_client, test_user_id):
        """Test: Inbox conversations have expected structure"""
        result = api_client.get_inbox(test_user_id, limit=1)
        
        if result["data"]:
            conversation = result["data"][0]
            assert "_id" in conversation
            assert "contactId" in conversation
            print(f"Conversation structure: {list(conversation.keys())}")


class TestGetContactMessages:
    """Tests für GET /inbox/{id}/messages"""
    
    def test_get_contact_messages(self, api_client, test_user_id):
        """Test: GET /inbox/{id}/messages returns messages"""
        # Get first conversation
        inbox = api_client.get_inbox(test_user_id, limit=1)
        
        if not inbox["data"]:
            pytest.skip("No inbox conversations available")
        
        contact_id = inbox["data"][0]["contactId"]
        messages = api_client.get_contact_messages(contact_id)
        
        assert isinstance(messages, list)
        print(f"Found {len(messages)} messages for contact")
    
    def test_message_structure(self, api_client, test_user_id):
        """Test: Messages have expected structure"""
        inbox = api_client.get_inbox(test_user_id, limit=1)
        
        if not inbox["data"]:
            pytest.skip("No inbox conversations available")
        
        contact_id = inbox["data"][0]["contactId"]
        messages = api_client.get_contact_messages(contact_id)
        
        if messages:
            msg = messages[0]
            assert "_id" in msg
            print(f"Message structure: {list(msg.keys())}")


class TestGetLabels:
    """Tests für GET /labels"""
    
    def test_get_labels(self, api_client):
        """Test: GET /labels returns labels"""
        labels = api_client.get_labels()
        
        assert isinstance(labels, list)
        print(f"Found {len(labels)} labels")
    
    def test_label_structure(self, api_client):
        """Test: Label objects have expected structure"""
        labels = api_client.get_labels()
        
        if labels:
            label = labels[0]
            assert "_id" in label
            assert "name" in label
            print(f"Label: {label['name']}")
    
    def test_get_label_by_id(self, api_client):
        """Test: GET /labels/{id} returns specific label"""
        labels = api_client.get_labels()
        
        if not labels:
            pytest.skip("No labels available")
        
        label_id = labels[0]["_id"]
        label = api_client.get_label(label_id)
        
        assert label["_id"] == label_id
