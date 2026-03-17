---
name: lemlist-official
description: |
  Official Lemlist API integration for OpenClaw.
  Direct API access without external proxies.
  130+ endpoints for campaigns, leads, inbox, and more.
  Use when: (1) managing outreach campaigns, (2) adding/updating leads, 
  (3) checking inbox messages, (4) tracking campaign stats, (5) managing webhooks.
  NOT for: (1) general email sending → use email tools, (2) CRM management → use CRM skills.
homepage: https://developer.lemlist.com
user-invocable: true
metadata:
  author: Silverstar187
  version: "1.0.0"
  openclaw:
    emoji: "📧"
    homepage: "https://github.com/Silverstar187/lemlist-openclaw-skill"
    requires:
      env:
        - LEMLIST_API_KEY
    primaryEnv: LEMLIST_API_KEY
---

# Lemlist Official

Official Lemlist API integration for OpenClaw with direct API access - no external proxies required.

## When to Use

✅ **USE this skill when:**
- Managing outreach campaigns (create, start, pause, update)
- Adding or updating leads in campaigns
- Checking inbox conversations and messages
- Tracking campaign statistics and reports
- Managing webhooks for real-time events
- Exporting campaign data
- Managing sequences and schedules

❌ **DON'T use this skill when:**
- Sending general emails → use email CLI tools
- Managing external CRMs → use specific CRM skills
- Bulk data processing → use dedicated ETL tools

## Quick Start

### 1. Setup

Get your API key from [Lemlist Integrations](https://app.lemlist.com/settings/integrations):

```bash
export LEMLIST_API_KEY="your_api_key_here"
```

### 2. Test Connection

```bash
curl -s "https://api.lemlist.com/api/team" \
  --user ":$LEMLIST_API_KEY" | jq .
```

### 3. List Campaigns

```bash
curl -s "https://api.lemlist.com/api/campaigns" \
  --user ":$LEMLIST_API_KEY" | jq '.[] | {id: ._id, name: .name, status: .status}'
```

## Authentication

Lemlist uses **HTTP Basic Auth** with an empty username and your API key as the password:

```bash
# Format: :API_KEY (note the leading colon)
curl --user ":$LEMLIST_API_KEY" \
  "https://api.lemlist.com/api/campaigns"
```

Or with explicit header:

```bash
AUTH=$(echo -n ":$LEMLIST_API_KEY" | base64)
curl -H "Authorization: Basic $AUTH" \
  "https://api.lemlist.com/api/campaigns"
```

## API Reference

### Campaigns

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/campaigns` | GET | List all campaigns |
| `/campaigns` | POST | Create new campaign |
| `/campaigns/{id}` | GET | Get campaign details |
| `/campaigns/{id}` | PATCH | Update campaign name |
| `/campaigns/{id}/start` | POST | Start campaign |
| `/campaigns/{id}/pause` | POST | Pause campaign |
| `/campaigns/{id}/stats` | GET | Get campaign statistics |
| `/campaigns/reports` | GET | Get aggregated reports |
| `/campaigns/{id}/export/start` | GET | Start CSV export |
| `/campaigns/{id}/export/{exportId}/status` | GET | Check export status |
| `/campaigns/{id}/sequences` | GET | Get campaign sequences |
| `/campaigns/{id}/schedules` | GET | Get campaign schedules |

### Leads

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/campaigns/{id}/leads` | GET | List leads in campaign |
| `/campaigns/{id}/leads` | POST | Add lead to campaign |
| `/leads/{email}` | GET | Get lead by email |
| `/leads` | GET | Get lead by email or ID |
| `/campaigns/{id}/leads/{leadId}` | PATCH | Update lead |
| `/campaigns/{id}/leads/{leadId}` | DELETE | Remove/unsubscribe lead |
| `/leads/pause/{leadId}` | POST | Pause lead |
| `/leads/start/{leadId}` | POST | Resume lead |
| `/leads/interested/{leadId}` | POST | Mark as interested |
| `/leads/notinterested/{leadId}` | POST | Mark as not interested |

### Inbox

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/inbox` | GET | List inbox conversations |
| `/inbox/{contactId}` | GET | Get contact messages |
| `/inbox/email` | POST | Send email |
| `/inbox/linkedin` | POST | Send LinkedIn message |
| `/inbox/whatsapp` | POST | Send WhatsApp message |
| `/inbox/drafts/{contactId}` | POST | Create draft |
| `/inbox/drafts/{contactId}` | GET | List drafts |
| `/inbox/drafts/{contactId}/{draftId}` | PATCH | Update draft |
| `/inbox/drafts/{contactId}/{draftId}` | DELETE | Delete draft |
| `/inbox/labels` | GET | List labels |
| `/inbox/labels` | POST | Create label |

### Activities & Tasks

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/activities?version=v2` | GET | List activities |
| `/tasks` | GET | List tasks |
| `/tasks` | POST | Create task |
| `/tasks/{taskId}` | PATCH | Update task |
| `/tasks/ignore` | POST | Ignore tasks |

### Team & Users

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/team` | GET | Get team info |
| `/team/credits` | GET | Get credits balance |
| `/team/senders` | GET | List team senders |
| `/users/{userId}` | GET | Get user info |
| `/users/{userId}/channels` | GET | Get user channels |

### Webhooks

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/hooks` | GET | List webhooks |
| `/hooks` | POST | Create webhook |
| `/hooks/{hookId}` | DELETE | Delete webhook |

### Unsubscribes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/unsubscribes` | GET | List unsubscribes |
| `/unsubscribes/{email}` | GET | Check unsubscribe status |
| `/unsubscribes` | POST | Add unsubscribe |
| `/unsubscribes/{email}` | DELETE | Remove unsubscribe |

### Enrichment

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/enrich` | POST | Enrich single entity |
| `/v2/enrichments/bulk` | POST | Bulk enrichment (max 500) |
| `/enrich/{enrichId}` | GET | Get enrichment result |
| `/leads/{leadId}/enrich` | POST | Enrich existing lead |

### Database

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/schema/people` | GET | Get people schema |
| `/schema/companies` | GET | Get companies schema |
| `/database/filters` | GET | Get database filters |
| `/database/people` | POST | Search people database |
| `/database/companies` | POST | Search companies database |

### Email Accounts & lemwarm

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/email-accounts` | POST | Connect email account |
| `/email-accounts/{id}` | DELETE | Disconnect email account |
| `/email-accounts/{id}/test` | POST | Test email connection |
| `/lemwarm/{id}` | GET | Get lemwarm settings |
| `/lemwarm/{id}/start` | POST | Start lemwarm |
| `/lemwarm/{id}/pause` | POST | Pause lemwarm |
| `/lemwarm/{id}` | PATCH | Update lemwarm settings |

### Schedules

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/schedules` | GET | List schedules |
| `/schedules/{id}` | GET | Get schedule |
| `/schedules` | POST | Create schedule |
| `/schedules/{id}` | PATCH | Update schedule |
| `/schedules/{id}` | DELETE | Delete schedule |

### Sequences

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sequences/{sequenceId}/steps` | POST | Add step to sequence |
| `/sequences/{sequenceId}/steps/{stepId}` | PATCH | Update sequence step |
| `/sequences/{sequenceId}/steps/{stepId}` | DELETE | Delete sequence step |

## Rate Limits

- **Limit:** 20 requests per 2 seconds
- Applied per API key across all routes

**Rate Limit Headers:**

| Header | Description |
|--------|-------------|
| `Retry-After` | Seconds until you can retry |
| `X-RateLimit-Limit` | Maximum requests allowed |
| `X-RateLimit-Remaining` | Remaining requests |
| `X-RateLimit-Reset` | Reset timestamp |

**Example Response (429):**
```json
{
  "Retry-After": 2,
  "X-RateLimit-Limit": 20,
  "X-RateLimit-Remaining": 0,
  "X-RateLimit-Reset": "Tue Feb 16 2021 09:02:42 GMT+0100"
}
```

## Error Handling

### HTTP Status Codes

| Code | Description | Solution |
|------|-------------|----------|
| `200` | Success | - |
| `201` | Created | - |
| `400` | Bad Request | Check request parameters |
| `401` | Unauthorized | Check API key |
| `403` | Forbidden | User may be blocked |
| `404` | Not Found | Resource doesn't exist |
| `405` | Method Not Allowed | Wrong HTTP method |
| `409` | Conflict | Resource already exists |
| `422` | Unprocessable | Validation error |
| `429` | Rate Limited | Wait and retry |

### Common Errors

**"The authentication you supplied is incorrect"**
- **Cause:** Invalid or missing API key
- **Solution:** Check `LEMLIST_API_KEY` environment variable

**"Bad team"**
- **Cause:** API key doesn't match any team
- **Solution:** Verify API key from correct account

**"Campaign not found"**
- **Cause:** Invalid campaign ID
- **Solution:** Use `/campaigns` to list valid IDs

**"Rate limit exceeded"**
- **Cause:** Too many requests
- **Solution:** Implement retry with backoff

## Testing

Run the included test suite:

```bash
# Set your API key
export LEMLIST_API_KEY="your_api_key"

# Run all tests
cd tests && python -m pytest

# Run only integration tests (read-only)
python -m pytest test_integration_*.py

# Run specific test
python -m pytest test_integration_campaigns_read.py -v
```

See `docs/testing.md` for detailed testing instructions.

## Examples

See `examples/` directory for complete working examples:
- `campaigns.py` - Campaign management
- `leads.py` - Lead operations
- `inbox.py` - Inbox operations

## Notes

- All timestamps are in ISO 8601 format (UTC)
- IDs use format: `{prefix}_{hash}` (e.g., `cam_abc123`, `lea_def456`)
- Campaign exports are available for 24 hours after completion
- Webhook events are sent as POST requests to your URL
- Credits are consumed for enrichment operations
