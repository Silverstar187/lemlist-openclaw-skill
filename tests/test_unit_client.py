"""
Unit Tests für Lemlist Client
"""
import pytest
import base64
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.insert(0, '/tmp/lemlist_skill/tests')

from lemlist_client import LemlistClient


class TestClientInitialization:
    """Tests für Client Initialisierung"""
    
    def test_client_init_with_api_key(self):
        """Test: Client initialization with explicit API key"""
        client = LemlistClient(api_key="test_key_123")
        assert client.api_key == "test_key_123"
    
    def test_client_init_without_api_key_raises(self, monkeypatch):
        """Test: Client initialization without API key raises error"""
        monkeypatch.delenv("LEMLIST_API_KEY", raising=False)
        with pytest.raises(ValueError, match="API key required"):
            LemlistClient()
    
    def test_client_init_from_env(self, monkeypatch):
        """Test: Client reads API key from environment"""
        monkeypatch.setenv("LEMLIST_API_KEY", "env_test_key")
        client = LemlistClient()
        assert client.api_key == "env_test_key"
    
    def test_basic_auth_encoding(self):
        """Test: Basic auth header is correctly encoded"""
        client = LemlistClient(api_key="my_api_key")
        
        # Format should be "Basic {base64(:api_key)}"
        expected_auth = base64.b64encode(b":my_api_key").decode()
        assert client.headers["Authorization"] == f"Basic {expected_auth}"
    
    def test_session_headers_set(self):
        """Test: Session has correct headers"""
        client = LemlistClient(api_key="test_key")
        
        assert "Authorization" in client.session.headers
        assert "Content-Type" in client.session.headers
        assert client.session.headers["Content-Type"] == "application/json"


class TestRateLimiting:
    """Tests für Rate Limiting Logik"""
    
    def test_rate_limit_initialization(self):
        """Test: Rate limit counters initialized correctly"""
        client = LemlistClient(api_key="test_key")
        assert client._request_count == 0
        assert client._window_start == 0
    
    @patch('time.time')
    def test_rate_limit_window_reset(self, mock_time):
        """Test: Rate limit window resets after 2 seconds"""
        client = LemlistClient(api_key="test_key")
        
        # Simulate time passing
        mock_time.return_value = 100.0
        client._handle_rate_limit()
        assert client._request_count == 1
        
        # Move forward past window
        mock_time.return_value = 103.0
        client._handle_rate_limit()
        assert client._window_start == 103.0
        assert client._request_count == 1  # Reset to 1 (new request)
    
    @patch('time.time')
    @patch('time.sleep')
    def test_rate_limit_throttling(self, mock_sleep, mock_time):
        """Test: Requests are throttled when limit reached"""
        client = LemlistClient(api_key="test_key")
        
        mock_time.return_value = 100.0
        client._window_start = 100.0
        client._request_count = 20  # At limit
        
        # Next request should trigger sleep
        mock_time.return_value = 101.0  # 1 second into window
        client._handle_rate_limit()
        
        # Should sleep for remaining window time
        mock_sleep.assert_called_once_with(1.0)


class TestRequestRetry:
    """Tests für Request Retry Logik"""
    
    @patch('requests.Session.request')
    def test_successful_request_no_retry(self, mock_request):
        """Test: Successful request doesn't retry"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        client = LemlistClient(api_key="test_key")
        response = client._request("GET", "/test")
        
        assert response.status_code == 200
        assert mock_request.call_count == 1
    
    @patch('requests.Session.request')
    def test_rate_limit_triggers_retry(self, mock_request):
        """Test: 429 response triggers retry with delay"""
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"Retry-After": "2"}
        
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        
        mock_request.side_effect = [mock_response_429, mock_response_200]
        
        with patch('time.sleep'):
            client = LemlistClient(api_key="test_key")
            response = client._request("GET", "/test")
        
        assert response.status_code == 200
        assert mock_request.call_count == 2
    
    @patch('requests.Session.request')
    def test_network_error_triggers_retry(self, mock_request):
        """Test: Network errors trigger exponential backoff retry"""
        from requests.exceptions import ConnectionError
        
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_request.side_effect = [ConnectionError(), ConnectionError(), mock_response]
        
        with patch('time.sleep'):
            client = LemlistClient(api_key="test_key")
            response = client._request("GET", "/test")
        
        assert response.status_code == 200
        assert mock_request.call_count == 3
    
    @patch('requests.Session.request')
    def test_max_retries_exceeded_raises(self, mock_request):
        """Test: Exception raised after max retries exceeded"""
        from requests.exceptions import Timeout
        
        mock_request.side_effect = Timeout()
        
        with patch('time.sleep'):
            client = LemlistClient(api_key="test_key")
            with pytest.raises(Timeout):
                client._request("GET", "/test", max_retries=3)
        
        assert mock_request.call_count == 3


class TestErrorHandling:
    """Tests für Error Handling"""
    
    @patch('requests.Session.request')
    def test_401_raises_on_get_team(self, mock_request):
        """Test: 401 response raises HTTPError"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
        mock_request.return_value = mock_response
        
        client = LemlistClient(api_key="invalid_key")
        with pytest.raises(Exception):
            client.get_team()
    
    @patch('requests.Session.request')
    def test_404_raises_on_get_campaign(self, mock_request):
        """Test: 404 response raises HTTPError for non-existent campaign"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_request.return_value = mock_response
        
        client = LemlistClient(api_key="test_key")
        with pytest.raises(Exception):
            client.get_campaign("non_existent_id")


class TestUrlConstruction:
    """Tests für URL Konstruktion"""
    
    def test_base_url_format(self):
        """Test: Base URL is correctly formatted"""
        client = LemlistClient(api_key="test_key")
        assert client.BASE_URL == "https://api.lemlist.com/api"
    
    @patch('requests.Session.request')
    def test_endpoint_url_construction(self, mock_request):
        """Test: Endpoint URLs are correctly constructed"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        client = LemlistClient(api_key="test_key")
        client._request("GET", "/campaigns")
        
        call_args = mock_request.call_args
        assert call_args[1]["url"] == "https://api.lemlist.com/api/campaigns"
    
    @patch('requests.Session.request')
    def test_endpoint_with_leading_slash(self, mock_request):
        """Test: Endpoints with leading slash work correctly"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        client = LemlistClient(api_key="test_key")
        client._request("GET", "campaigns")  # Without leading slash
        
        call_args = mock_request.call_args
        assert call_args[1]["url"] == "https://api.lemlist.com/api/campaigns"
