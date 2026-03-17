"""
E2E Tests für Inbox Draft Operations
Diese Tests erstellen, modifizieren und löschen Drafts.
Cleanup ist in den Fixtures implementiert.
"""
import pytest
import sys
sys.path.insert(0, '/tmp/lemlist_skill/tests')


class TestCreateDraft:
    """Tests für POST /inbox/drafts"""
    
    def test_create_draft(self, api_client, test_user_id):
        """Test: POST /inbox/drafts creates new draft"""
        # Get a contact first
        inbox = api_client.get_inbox(test_user_id, limit=1)
        
        if not inbox.get("data"):
            pytest.skip("No inbox conversations available")
        
        contact_id = inbox["data"][0]["contactId"]
        
        draft_data = {
            "subject": "Test Draft Subject",
            "body": "This is a test draft body."
        }
        
        draft = api_client.create_draft(contact_id, draft_data)
        
        assert "_id" in draft
        assert draft.get("subject") == "Test Draft Subject"
        
        # Cleanup
        api_client.delete_draft(draft["_id"])
        print(f"Created draft: {draft['_id']}")
    
    def test_create_draft_response_structure(self, api_client, test_user_id):
        """Test: Create draft returns complete draft object"""
        inbox = api_client.get_inbox(test_user_id, limit=1)
        
        if not inbox.get("data"):
            pytest.skip("No inbox conversations available")
        
        contact_id = inbox["data"][0]["contactId"]
        
        draft_data = {
            "subject": "Structure Test",
            "body": "Testing response structure."
        }
        
        draft = api_client.create_draft(contact_id, draft_data)
        
        # Check expected fields
        assert "_id" in draft
        assert "contactId" in draft
        assert "source" in draft  # Should be "api"
        
        # Cleanup
        api_client.delete_draft(draft["_id"])


class TestGetDraft:
    """Tests für GET /inbox/drafts/{id}"""
    
    def test_get_draft(self, api_client, test_user_id):
        """Test: GET /inbox/drafts/{id} returns draft"""
        # Create a draft first
        inbox = api_client.get_inbox(test_user_id, limit=1)
        
        if not inbox.get("data"):
            pytest.skip("No inbox conversations available")
        
        contact_id = inbox["data"][0]["contactId"]
        
        draft_data = {
            "subject": "Get Draft Test",
            "body": "Testing get draft."
        }
        
        created = api_client.create_draft(contact_id, draft_data)
        draft_id = created["_id"]
        
        # Get the draft
        draft = api_client.get_draft(draft_id)
        
        assert draft["_id"] == draft_id
        assert draft["subject"] == "Get Draft Test"
        
        # Cleanup
        api_client.delete_draft(draft_id)


class TestUpdateDraft:
    """Tests für PUT /inbox/drafts/{id}"""
    
    def test_update_draft(self, api_client, test_user_id):
        """Test: PUT /inbox/drafts/{id} updates draft"""
        # Create a draft first
        inbox = api_client.get_inbox(test_user_id, limit=1)
        
        if not inbox.get("data"):
            pytest.skip("No inbox conversations available")
        
        contact_id = inbox["data"][0]["contactId"]
        
        draft_data = {
            "subject": "Original Subject",
            "body": "Original body."
        }
        
        created = api_client.create_draft(contact_id, draft_data)
        draft_id = created["_id"]
        
        # Update the draft
        update_data = {
            "subject": "Updated Subject",
            "body": "Updated body content."
        }
        
        updated = api_client.update_draft(draft_id, update_data)
        
        assert updated["subject"] == "Updated Subject"
        
        # Cleanup
        api_client.delete_draft(draft_id)
    
    def test_partial_update_draft(self, api_client, test_user_id):
        """Test: Partial update of draft (only subject)"""
        inbox = api_client.get_inbox(test_user_id, limit=1)
        
        if not inbox.get("data"):
            pytest.skip("No inbox conversations available")
        
        contact_id = inbox["data"][0]["contactId"]
        
        draft_data = {
            "subject": "Partial Update Test",
            "body": "Body that should remain unchanged."
        }
        
        created = api_client.create_draft(contact_id, draft_data)
        draft_id = created["_id"]
        
        # Update only subject
        update_data = {"subject": "Only Subject Updated"}
        updated = api_client.update_draft(draft_id, update_data)
        
        assert updated["subject"] == "Only Subject Updated"
        
        # Cleanup
        api_client.delete_draft(draft_id)


class TestDeleteDraft:
    """Tests für DELETE /inbox/drafts/{id}"""
    
    def test_delete_draft(self, api_client, test_user_id):
        """Test: DELETE /inbox/drafts/{id} deletes draft"""
        # Create a draft to delete
        inbox = api_client.get_inbox(test_user_id, limit=1)
        
        if not inbox.get("data"):
            pytest.skip("No inbox conversations available")
        
        contact_id = inbox["data"][0]["contactId"]
        
        draft_data = {
            "subject": "Draft to Delete",
            "body": "This draft will be deleted."
        }
        
        created = api_client.create_draft(contact_id, draft_data)
        draft_id = created["_id"]
        
        # Delete it
        success = api_client.delete_draft(draft_id)
        assert success is True
        
        # Verify it's gone (should 404 or be marked deleted)
        try:
            draft = api_client.get_draft(draft_id)
            # If found, should have deletedAt
            assert "deletedAt" in draft
        except Exception:
            # 404 is expected
            pass
