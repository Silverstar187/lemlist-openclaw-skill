# Rate Limits

Lemlist API implements rate limiting to ensure fair usage and system stability.

## Rate Limit Policy

- **Limit:** 20 requests per 2 seconds
- **Scope:** Per API key across all routes
- **Window:** Sliding window of 2 seconds

## Rate Limit Headers

Every API response includes rate limit information:

| Header | Description | Example |
|--------|-------------|---------|
| `X-RateLimit-Limit` | Maximum requests allowed | `20` |
| `X-RateLimit-Remaining` | Remaining requests in window | `15` |
| `X-RateLimit-Reset` | When the limit resets | `Tue Feb 16 2021 09:02:42 GMT+0100` |
| `Retry-After` | Seconds until retry allowed | `2` |

## Handling Rate Limits

### 429 Response

When you exceed the rate limit, you receive:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 2
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 0
X-RateLimit-Reset: Tue Feb 16 2021 09:02:42 GMT+0100

{
  "error": "Rate limit exceeded"
}
```

### Retry Strategy

**Basic retry with delay:**

```python
import time
import requests

def api_call_with_retry(url, auth, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, auth=auth)
        
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 2))
            time.sleep(retry_after)
            continue
            
        response.raise_for_status()
        return response.json()
    
    raise Exception("Max retries exceeded")
```

**Exponential backoff:**

```python
import time
import random

def exponential_backoff(attempt, base_delay=1, max_delay=60):
    """Calculate delay with jitter"""
    delay = min(base_delay * (2 ** attempt), max_delay)
    jitter = random.uniform(0, 0.1 * delay)
    return delay + jitter

def api_call_with_backoff(url, auth, max_retries=5):
    for attempt in range(max_retries):
        response = requests.get(url, auth=auth)
        
        if response.status_code == 429:
            delay = exponential_backoff(attempt)
            time.sleep(delay)
            continue
            
        response.raise_for_status()
        return response.json()
    
    raise Exception("Max retries exceeded")
```

## Best Practices

### 1. Monitor Headers

Always check rate limit headers to avoid hitting limits:

```python
response = requests.get(url, auth=auth)
remaining = int(response.headers.get("X-RateLimit-Remaining", 0))

if remaining < 5:
    # Slow down or queue requests
    time.sleep(1)
```

### 2. Implement Queuing

For bulk operations, use a queue with rate limiting:

```python
from collections import deque
import time

class RateLimitedQueue:
    def __init__(self, max_requests=20, window=2):
        self.queue = deque()
        self.timestamps = deque()
        self.max_requests = max_requests
        self.window = window
    
    def add(self, request):
        self.queue.append(request)
    
    def process(self):
        now = time.time()
        
        # Remove old timestamps
        while self.timestamps and self.timestamps[0] < now - self.window:
            self.timestamps.popleft()
        
        # Check if we can make a request
        if len(self.timestamps) >= self.max_requests:
            sleep_time = self.timestamps[0] - (now - self.window)
            time.sleep(max(0, sleep_time))
        
        # Process request
        if self.queue:
            request = self.queue.popleft()
            self.timestamps.append(time.time())
            return request()
```

### 3. Batch Operations

Use bulk endpoints when available:

```python
# Instead of multiple single requests
for email in emails:
    requests.post("/enrich", json={"email": email})  # Slow!

# Use bulk endpoint
requests.post("/v2/enrichments/bulk", json=[
    {"input": {"email": e}, "enrichmentRequests": ["verify"]}
    for e in emails
])  # Much faster!
```

### 4. Caching

Cache responses that don't change frequently:

```python
import functools
import time

@functools.lru_cache(maxsize=128)
def get_campaign(campaign_id):
    """Cached campaign lookup"""
    return requests.get(f"/campaigns/{campaign_id}").json()
```

## Rate Limit Exceptions

Some endpoints have different limits:

| Endpoint | Limit | Notes |
|----------|-------|-------|
| `/activities` | 20/2s | Standard |
| `/enrich` | 20/2s | Per enrichment |
| `/v2/enrichments/bulk` | 20/2s | Max 500 items |
| `/database/people` | 20/2s | Search limited per 24h |
| `/database/companies` | 20/2s | Search limited per 24h |

## Testing Rate Limits

```python
# Test rate limit handling
import concurrent.futures

def make_request(i):
    return requests.get("/campaigns", auth=auth)

# Make 25 concurrent requests (exceeds limit)
with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
    futures = [executor.submit(make_request, i) for i in range(25)]
    results = [f.result() for f in futures]

# Count rate limited responses
rate_limited = sum(1 for r in results if r.status_code == 429)
print(f"Rate limited: {rate_limited} requests")
```

## Monitoring

Track your API usage:

```python
class RateLimitMonitor:
    def __init__(self):
        self.requests = []
    
    def log_request(self, headers):
        self.requests.append({
            "timestamp": time.time(),
            "remaining": headers.get("X-RateLimit-Remaining"),
            "limit": headers.get("X-RateLimit-Limit")
        })
    
    def get_stats(self):
        if not self.requests:
            return {}
        
        remaining = [int(r["remaining"]) for r in self.requests if r["remaining"]]
        return {
            "total_requests": len(self.requests),
            "min_remaining": min(remaining) if remaining else 0,
            "avg_remaining": sum(remaining) / len(remaining) if remaining else 0
        }
```
