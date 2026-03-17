"""
Integration Tests für Team und User Operations
Diese Tests führen nur GET Requests aus - keine Daten werden verändert.
"""
import pytest
import sys
sys.path.insert(0, '/tmp/lemlist_skill/tests')


class TestGetTeam:
    """Tests für GET /team"""
    
    def test_get_team(self, api_client):
        """Test: GET /team returns team information"""
        team = api_client.get_team()
        
        assert isinstance(team, dict)
        assert "_id" in team
        print(f"Team ID: {team['_id']}")
    
    def test_team_has_users(self, api_client):
        """Test: Team has users array"""
        team = api_client.get_team()
        
        assert "users" in team
        assert isinstance(team["users"], list)
        print(f"Team has {len(team['users'])} users")
    
    def test_team_user_structure(self, api_client):
        """Test: Team users have expected structure"""
        team = api_client.get_team()
        
        if team["users"]:
            user = team["users"][0]
            assert "_id" in user
            assert "email" in user
            print(f"User structure: {list(user.keys())}")


class TestGetTeamSenders:
    """Tests für GET /team/senders"""
    
    def test_get_team_senders(self, api_client):
        """Test: GET /team/senders returns senders"""
        senders = api_client.get_team_senders()
        
        assert isinstance(senders, list)
        print(f"Found {len(senders)} senders")
    
    def test_sender_structure(self, api_client):
        """Test: Sender objects have expected structure"""
        senders = api_client.get_team_senders()
        
        if senders:
            sender = senders[0]
            assert "_id" in sender
            print(f"Sender structure: {list(sender.keys())}")


class TestGetTeamCredits:
    """Tests für GET /team/credits"""
    
    def test_get_team_credits(self, api_client):
        """Test: GET /team/credits returns credits info"""
        credits = api_client.get_team_credits()
        
        assert isinstance(credits, dict)
        print(f"Credits: {credits}")
    
    def test_credits_structure(self, api_client):
        """Test: Credits response has expected fields"""
        credits = api_client.get_team_credits()
        
        # Common credit fields
        expected_fields = ["credits", "remaining", "used"]
        for field in expected_fields:
            if field in credits:
                assert isinstance(credits[field], (int, float))


class TestGetUser:
    """Tests für GET /users/{id}"""
    
    def test_get_user(self, api_client, test_user_id):
        """Test: GET /users/{id} returns user info"""
        user = api_client.get_user(test_user_id)
        
        assert user["_id"] == test_user_id
        assert "email" in user
        print(f"User: {user['email']}")
    
    def test_user_not_found(self, api_client):
        """Test: GET /users/{invalid_id} returns 404"""
        with pytest.raises(Exception) as exc_info:
            api_client.get_user("invalid_user_id_12345")
        
        assert "404" in str(exc_info.value) or "Not Found" in str(exc_info.value)


class TestGetUserChannels:
    """Tests für GET /users/{id}/channels"""
    
    def test_get_user_channels(self, api_client, test_user_id):
        """Test: GET /users/{id}/channels returns channels"""
        channels = api_client.get_user_channels(test_user_id)
        
        assert isinstance(channels, dict)
        print(f"User channels: {list(channels.keys())}")
    
    def test_channels_structure(self, api_client, test_user_id):
        """Test: Channels response has expected structure"""
        channels = api_client.get_user_channels(test_user_id)
        
        # Common channel types
        channel_types = ["email", "linkedin", "whatsapp"]
        for ch_type in channel_types:
            if ch_type in channels:
                print(f"{ch_type} channel: {channels[ch_type]}")
