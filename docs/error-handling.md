# Error Handling

Comprehensive guide to handling errors from the Lemlist API.

## HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| `200` | OK | Success |
| `201` | Created | Resource created successfully |
| `400` | Bad Request | Check request parameters |
| `401` | Unauthorized | Check API key |
| `403` | Forbidden | User blocked or insufficient permissions |
| `404` | Not Found | Resource doesn't exist |
| `405` | Method Not Allowed | Wrong HTTP method |
| `409` | Conflict | Resource already exists |
| `422` | Unprocessable Entity | Validation error |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Retry with backoff |
| `502` | Bad Gateway | Temporary error, retry |
| `503` | Service Unavailable | Service temporarily down |

## Common Errors

### Authentication Errors

#### "The authentication you supplied is incorrect"

```json
{
  "error": "The authentication you supplied is incorrect"
}
```

**Cause:** Invalid or missing API key

**Solution:**
```bash
# Check if API key is set
echo $LEMLIST_API_KEY

# Verify format (should have colon prefix)
curl --user ":$LEMLIST_API_KEY" https://api.lemlist.com/api/team
```

#### "No API key provided"

**Cause:** Missing Authorization header

**Solution:**
```python
# Correct
auth = HTTPBasicAuth("", api_key)

# Incorrect - missing auth
requests.get(url)  # Will fail
```

### Resource Errors

#### "Campaign not found"

```json
{
  "error": "Campaign not found"
}
```

**Cause:** Invalid campaign ID

**Solution:**
```python
# List valid campaigns first
campaigns = client.get_campaigns()
valid_ids = [c["_id"] for c in campaigns]

# Verify ID before using
if campaign_id not in valid_ids:
    raise ValueError(f"Invalid campaign ID: {campaign_id}")
```

#### "Lead not found"

**Cause:** Lead doesn't exist in campaign

**Solution:**
```python
# Search across all leads
lead = client.get_lead_by_email(email)
if not lead:
    # Lead doesn't exist anywhere
    pass
```

### Validation Errors

#### "Bad team"

**Cause:** API key doesn't match any team

**Solution:**
- Verify you're using the correct API key
- Check if account is active

#### "labelName is required"

```json
{
  "error": "labelName is required"
}
```

**Cause:** Missing required field

**Solution:**
```python
# Always include required fields
data = {
    "labelName": "My Label"  # Required!
}
```

### Rate Limit Errors

#### "Rate limit exceeded"

```json
{
  "Retry-After": 2,
  "X-RateLimit-Limit": 20,
  "X-RateLimit-Remaining": 0
}
```

**Cause:** Too many requests

**Solution:**
```python
import time

def api_call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        response = func()
        
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 2))
            time.sleep(retry_after)
            continue
            
        return response
    
    raise Exception("Rate limit exceeded, max retries reached")
```

## Error Handling Patterns

### Pattern 1: Try-Except with Specific Errors

```python
from requests.exceptions import HTTPError

def get_campaign_safe(campaign_id):
    try:
        return client.get_campaign(campaign_id)
    except HTTPError as e:
        if e.response.status_code == 404:
            print(f"Campaign {campaign_id} not found")
            return None
        elif e.response.status_code == 401:
            print("Invalid API key")
            raise
        else:
            raise
```

### Pattern 2: Result Pattern

```python
from dataclasses import dataclass
from typing import Optional, Union

@dataclass
class Error:
    code: int
    message: str
    details: Optional[dict] = None

@dataclass
class Success:
    data: dict

Result = Union[Success, Error]

def get_campaign_result(campaign_id) -> Result:
    response = requests.get(f"/campaigns/{campaign_id}")
    
    if response.status_code == 200:
        return Success(data=response.json())
    elif response.status_code == 404:
        return Error(code=404, message="Campaign not found")
    elif response.status_code == 401:
        return Error(code=401, message="Unauthorized")
    else:
        return Error(
            code=response.status_code,
            message="Unknown error",
            details=response.json()
        )

# Usage
result = get_campaign_result("cam_123")
if isinstance(result, Success):
    print(result.data)
else:
    print(f"Error {result.code}: {result.message}")
```

### Pattern 3: Decorator for Retry

```python
import functools
import time

def retry_on_error(max_retries=3, retry_codes=(429, 500, 502, 503)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except HTTPError as e:
                    if e.response.status_code in retry_codes:
                        if attempt < max_retries - 1:
                            delay = 2 ** attempt  # Exponential backoff
                            time.sleep(delay)
                            continue
                    raise
            return None
        return wrapper
    return decorator

@retry_on_error(max_retries=3)
def get_campaign(campaign_id):
    return client.get_campaign(campaign_id)
```

## Error Categories

### Category 1: Client Errors (4xx)

These are your responsibility to fix:

| Error | Fix |
|-------|-----|
| 400 Bad Request | Check request format |
| 401 Unauthorized | Verify API key |
| 404 Not Found | Check resource ID |
| 409 Conflict | Handle duplicate |
| 422 Validation | Fix field values |
| 429 Rate Limit | Implement retry |

### Category 2: Server Errors (5xx)

These are temporary, retry with backoff:

| Error | Fix |
|-------|-----|
| 500 Internal Error | Retry |
| 502 Bad Gateway | Retry |
| 503 Unavailable | Retry with longer delay |

## Logging Errors

```python
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def log_api_error(response):
    """Log API errors with context"""
    logger.error(
        f"API Error: {response.status_code}",
        extra={
            "url": response.url,
            "method": response.request.method,
            "status": response.status_code,
            "response": response.text[:500],
            "headers": dict(response.headers)
        }
    )
```

## Testing Error Handling

```python
import pytest
from unittest.mock import Mock, patch

def test_handle_404():
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"error": "Not found"}
    
    with patch('requests.get', return_value=mock_response):
        result = get_campaign("invalid_id")
        assert result is None

def test_handle_rate_limit():
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.headers = {"Retry-After": "2"}
    
    with patch('requests.get', return_value=mock_response):
        with pytest.raises(Exception):
            get_campaign("cam_123")
```

## Best Practices

1. **Always check status codes** - Don't assume success
2. **Log errors with context** - URL, method, response
3. **Implement retry logic** - For transient errors
4. **Fail fast on auth errors** - Don't retry 401
5. **Provide helpful messages** - Users should understand the fix
6. **Use exponential backoff** - For retries
7. **Set request timeouts** - Don't wait forever

```python
# Good
response = requests.get(url, auth=auth, timeout=30)
response.raise_for_status()

# Bad - no timeout, no error checking
response = requests.get(url)
return response.json()  # May fail!
```
