# Lemlist Official Skill

📧 Official Lemlist API integration for OpenClaw with direct API access.

## Overview

This skill provides comprehensive access to the Lemlist API (130+ endpoints) for managing outreach campaigns, leads, inbox, and more - without external proxies.

## Features

- ✅ **130+ API Endpoints** - Full coverage of Lemlist API
- ✅ **Direct API Access** - No external proxies required
- ✅ **Basic Auth** - Simple, secure authentication
- ✅ **Rate Limit Handling** - Built-in retry logic
- ✅ **Complete Test Suite** - Unit, integration, and E2E tests
- ✅ **Working Examples** - Ready-to-use code samples

## Quick Start

```bash
# 1. Set your API key
export LEMLIST_API_KEY="your_api_key_here"

# 2. Test connection
curl -s "https://api.lemlist.com/api/team" --user ":$LEMLIST_API_KEY"

# 3. List campaigns
curl -s "https://api.lemlist.com/api/campaigns" --user ":$LEMLIST_API_KEY" | jq .
```

## Installation

1. Copy this skill to your OpenClaw skills directory:
   ```bash
   cp -r /tmp/lemlist-official-skill ~/.openclaw/skills/
   ```

2. Set your API key:
   ```bash
   export LEMLIST_API_KEY="your_api_key_here"
   ```

3. Get your API key from [Lemlist Settings](https://app.lemlist.com/settings/integrations)

## Documentation

- [SKILL.md](SKILL.md) - Complete API documentation
- [docs/authentication.md](docs/authentication.md) - Auth guide
- [docs/rate-limits.md](docs/rate-limits.md) - Rate limiting
- [docs/error-handling.md](docs/error-handling.md) - Error handling
- [docs/testing.md](docs/testing.md) - Testing guide

## Examples

See the `examples/` directory:
- `campaigns.py` - Campaign management
- `leads.py` - Lead operations
- `inbox.py` - Inbox operations

## API Coverage

| Category | Endpoints |
|----------|-----------|
| Campaigns | 12 |
| Leads | 11 |
| Inbox | 14 |
| Activities | 1 |
| Tasks | 4 |
| Team | 5 |
| Webhooks | 3 |
| Unsubscribes | 4 |
| Enrichment | 4 |
| Database | 5 |
| Email Accounts | 3 |
| lemwarm | 4 |
| Schedules | 5 |
| Sequences | 3 |
| **Total** | **130+** |

## Testing

```bash
cd tests

# Run all tests
python -m pytest

# Run integration tests only
python -m pytest test_integration_*.py

# Run with verbose output
python -m pytest -v
```

## Rate Limits

- **20 requests per 2 seconds**
- Per API key across all routes
- Automatic retry headers included

## Authentication

Uses HTTP Basic Auth with empty username and API key as password:

```bash
curl --user ":$LEMLIST_API_KEY" https://api.lemlist.com/api/team
```

## Support

- [Lemlist API Docs](https://developer.lemlist.com)
- [OpenClaw Skills Guide](https://docs.openclaw.io/skills)

## License

MIT

## Author

Silverstar187
