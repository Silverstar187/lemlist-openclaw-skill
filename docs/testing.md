# Testing Guide

Complete guide to testing the Lemlist API integration.

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── config.py                   # Test configuration
├── lemlist_client.py           # API client
├── test_unit_client.py         # Unit tests
├── test_integration_*.py       # Integration tests (read-only)
└── test_e2e_*.py               # E2E tests (write operations)
```

## Prerequisites

```bash
# Set your API key
export LEMLIST_API_KEY="your_api_key_here"

# Install dependencies
pip install pytest requests python-dotenv
```

## Running Tests

### All Tests

```bash
cd tests
python -m pytest
```

### Specific Test Categories

```bash
# Unit tests only
python -m pytest test_unit_*.py

# Integration tests (safe, read-only)
python -m pytest test_integration_*.py

# E2E tests (modifies data)
python -m pytest test_e2e_*.py

# Specific test file
python -m pytest test_integration_campaigns_read.py -v
```

### Test Options

```bash
# Verbose output
python -m pytest -v

# Stop on first failure
python -m pytest -x

# Run specific test
python -m pytest test_integration_campaigns_read.py::test_get_campaigns -v

# Show print statements
python -m pytest -s

# Generate coverage report
python -m pytest --cov=. --cov-report=html
```

## Test Categories

### Unit Tests

Fast tests with mocked API calls:

```python
# test_unit_client.py
def test_client_initialization():
    client = LemlistClient(api_key="test_key")
    assert client.api_key == "test_key"
    assert client.base_url == "https://api.lemlist.com/api"

def test_auth_header():
    client = LemlistClient(api_key="test_key")
    headers = client._get_auth_header()
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Basic ")
```

### Integration Tests

Read-only tests against real API:

```python
# test_integration_campaigns_read.py
def test_get_campaigns(api_client):
    """Test listing campaigns"""
    campaigns = api_client.get_campaigns()
    assert isinstance(campaigns, list)
    
    if campaigns:
        campaign = campaigns[0]
        assert "_id" in campaign
        assert "name" in campaign
        assert "status" in campaign

def test_get_campaign_stats(api_client):
    """Test getting campaign statistics"""
    campaigns = api_client.get_campaigns()
    if campaigns:
        stats = api_client.get_campaign_stats(campaigns[0]["_id"])
        assert isinstance(stats, dict)
```

### E2E Tests

Full workflow tests with cleanup:

```python
# test_e2e_campaigns_write.py
def test_create_and_delete_campaign(api_client):
    """Test campaign creation and deletion"""
    import time
    
    # Create
    name = f"TEST-{int(time.time())}"
    campaign = api_client.create_campaign(name=name)
    assert campaign["name"] == name
    
    # Verify
    fetched = api_client.get_campaign(campaign["_id"])
    assert fetched["_id"] == campaign["_id"]
    
    # Cleanup
    api_client.delete_campaign(campaign["_id"])
    
    # Verify deletion
    with pytest.raises(HTTPError):
        api_client.get_campaign(campaign["_id"])
```

## Fixtures

### Shared Fixtures (conftest.py)

```python
import pytest

@pytest.fixture(scope="session")
def api_client():
    """Shared API client for all tests"""
    from lemlist_client import LemlistClient
    client = LemlistClient()
    yield client

@pytest.fixture(scope="function")
def test_campaign(api_client):
    """Creates a test campaign and cleans up"""
    import time
    name = f"TEST-{int(time.time())}"
    campaign = api_client.create_campaign(name=name)
    yield campaign
    
    # Cleanup
    try:
        api_client.delete_campaign(campaign["_id"])
    except:
        pass
```

## Test Configuration

### config.py

```python
import os

# API Configuration
LEMLIST_API_KEY = os.getenv("LEMLIST_API_KEY", "")
BASE_URL = "https://api.lemlist.com/api"

# Test Naming
TEST_PREFIX = "TEST-AUTO"

# Timeouts
REQUEST_TIMEOUT = 30
RATE_LIMIT_DELAY = 0.1

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY = 2
```

## Writing Tests

### Test Naming

```python
# Good - descriptive
def test_get_campaigns_returns_list():
    pass

def test_create_campaign_with_valid_name_succeeds():
    pass

# Bad - unclear
def test_1():
    pass

def test_campaign():
    pass
```

### Test Structure

```python
def test_feature_scenario():
    # Arrange
    client = LemlistClient()
    
    # Act
    result = client.do_something()
    
    # Assert
    assert result.status_code == 200
    assert "expected_field" in result.json()
```

### Testing Error Cases

```python
def test_get_nonexistent_campaign_returns_404(api_client):
    with pytest.raises(HTTPError) as exc_info:
        api_client.get_campaign("cam_invalid_id")
    
    assert exc_info.value.response.status_code == 404
```

### Testing Rate Limits

```python
def test_rate_limit_handling(api_client):
    """Test that rate limits are properly handled"""
    import concurrent.futures
    
    def make_request():
        return api_client.get_campaigns()
    
    # Make many concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(make_request) for _ in range(25)]
        results = [f.result() for f in futures]
    
    # All should succeed (client handles rate limiting)
    assert all(isinstance(r, list) for r in results)
```

## Mocking

### Mock API Responses

```python
from unittest.mock import Mock, patch

def test_with_mocked_response():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "_id": "cam_test",
        "name": "Test Campaign"
    }
    
    with patch('requests.get', return_value=mock_response):
        client = LemlistClient()
        campaign = client.get_campaign("cam_test")
        assert campaign["name"] == "Test Campaign"
```

### Mock Environment Variables

```python
import os
from unittest.mock import patch

def test_without_api_key():
    with patch.dict(os.environ, {"LEMLIST_API_KEY": ""}):
        with pytest.raises(ValueError):
            LemlistClient()
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install pytest requests
      
      - name: Run unit tests
        env:
          LEMLIST_API_KEY: ${{ secrets.LEMLIST_API_KEY }}
        run: |
          python -m pytest test_unit_*.py
      
      - name: Run integration tests
        env:
          LEMLIST_API_KEY: ${{ secrets.LEMLIST_API_KEY }}
        run: |
          python -m pytest test_integration_*.py
```

## Test Data

### Using Fixtures

```python
# fixtures/sample_campaign.json
{
  "name": "Test Campaign",
  "status": "draft"
}

# In test
import json

def load_fixture(name):
    with open(f"fixtures/{name}.json") as f:
        return json.load(f)

def test_create_campaign(api_client):
    data = load_fixture("sample_campaign")
    campaign = api_client.create_campaign(**data)
    assert campaign["name"] == data["name"]
```

## Debugging Tests

### Verbose Output

```bash
# Show print statements
python -m pytest -s

# Show full traceback
python -m pytest --tb=long

# Enter debugger on failure
python -m pytest --pdb
```

### Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)

def test_with_logging(api_client):
    logging.debug("Starting test")
    result = api_client.get_campaigns()
    logging.debug(f"Got {len(result)} campaigns")
```

## Best Practices

1. **Isolate tests** - Each test should be independent
2. **Clean up** - Always clean up created resources
3. **Use fixtures** - Share setup code
4. **Test edge cases** - Empty lists, invalid IDs, etc.
5. **Mock external calls** - For unit tests
6. **Test real API** - For integration tests
7. **Document tests** - Clear docstrings
8. **Fast feedback** - Unit tests should be fast
