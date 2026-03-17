"""
Test-Konfiguration für Lemlist Tests
"""
import os
from typing import Dict

# API Konfiguration
LEMLIST_API_KEY = os.getenv("LEMLIST_API_KEY", "")
BASE_URL = "https://api.lemlist.com/api"

# Test-Naming
TEST_PREFIX = "TEST-AUTO"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# Timeouts
REQUEST_TIMEOUT = 30
RATE_LIMIT_DELAY = 0.1  # 100ms zwischen Requests

# Retry Konfiguration
MAX_RETRIES = 3
RETRY_DELAY = 2

# Test-Daten
TEST_LEAD_EMAIL_DOMAIN = "test.lemlist.example.com"


def get_test_campaign_name() -> str:
    """Generate unique test campaign name"""
    from datetime import datetime
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    return f"{TEST_PREFIX}-Campaign-{timestamp}"


def get_test_lead_data(timestamp: str = None) -> Dict:
    """Generate test lead data"""
    from datetime import datetime
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    return {
        "email": f"test.lead.{timestamp}@{TEST_LEAD_EMAIL_DOMAIN}",
        "firstName": "Test",
        "lastName": "Lead",
        "companyName": "Test Company Inc",
        "jobTitle": "Test Manager",
        "companyDomain": "testcompany.example.com",
        "timezone": "Europe/Berlin"
    }


def get_test_webhook_url() -> str:
    """Generate test webhook URL"""
    from datetime import datetime
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    return f"https://webhook.site/test-{timestamp}"
