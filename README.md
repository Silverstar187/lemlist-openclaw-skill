![Lemlist OpenClaw Skill](hero.png)

# Lemlist OpenClaw Skill

Direct Lemlist API integration for OpenClaw. No external proxies. No trial-and-error. Works on first try.

```bash
export LEMLIST_API_KEY="your_api_key"

curl -s "https://api.lemlist.com/api/campaigns" \
  --user ":$LEMLIST_API_KEY" | jq '.[].name'
```

## Why This Exists

Most API integrations promise "easy to use" but hide the real complexity. You spend hours debugging:
- Which endpoint actually works?
- Why does this return 404 when the docs say 200?
- How do I update lead variables without errors?

This skill documents what we learned the hard way—so you don't have to.

## What Makes This Different

| Others | This Skill |
|--------|------------|
| External proxies (security risk) | Direct API access |
| "Works on my machine" | Validated by autonomous agents |
| Outdated examples | Tested workflows with timing data |
| Hidden limitations | Transparent about API bugs |

**Agent-Validated:** Every endpoint tested by autonomous agents without human guidance. If they can use it, so can you.

## Quick Start

### 1. Get API Key
```bash
# From Lemlist: Settings → Integrations → API
export LEMLIST_API_KEY="lem_live_xxxxxxxx"
```

### 2. Test Connection
```bash
curl -s "https://api.lemlist.com/api/team" \
  --user ":$LEMLIST_API_KEY" | jq '.name'
```

### 3. List Campaigns
```bash
curl -s "https://api.lemlist.com/api/campaigns" \
  --user ":$LEMLIST_API_KEY" | jq '.[] | {id: ._id, name: .name}'
```

**Expected time to first success:** < 2 minutes

## Critical: Campaign Context Required

⚠️ **The #1 mistake:** Trying to access leads directly via `/leads/{id}`. This endpoint is unreliable.

**Always use Campaign context:**

```bash
# ❌ Unreliable
GET /leads/{leadId}

# ✅ Reliable
GET /campaigns/{campaignId}/leads/{leadId}
PATCH /campaigns/{campaignId}/leads/{leadId}
```

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for why this matters.

## Common Workflows

### Update Lead Variables
```bash
CAMPAIGN_ID="cam_xxx"
LEAD_ID="lea_xxx"

curl -X PATCH "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/leads/$LEAD_ID" \
  --user ":$LEMLIST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"variables": {"priority": "high", "source": "api"}}'
```

### Export Campaign Data
```bash
curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/export" \
  --user ":$LEMLIST_API_KEY" > campaign_export.csv
```

More examples in [examples/](examples/).

## Documentation

| Document | Purpose |
|----------|---------|
| [SKILL.md](SKILL.md) | Complete API reference (130+ endpoints) |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common pitfalls and solutions |
| [docs/PROCESS_DOCUMENTATION.md](docs/PROCESS_DOCUMENTATION.md) | Tested workflows step-by-step |
| [tests/](tests/) | Working code examples |

## API Limits

- **Rate:** 20 requests / 2 seconds
- **Auth:** HTTP Basic Auth with empty username (`:api_key`)
- **Format:** JSON

## Known Limitations

We document what doesn't work—so you don't waste time:

| Endpoint | Status | Alternative |
|----------|--------|-------------|
| `DELETE /campaigns/{id}` | Not supported | `PATCH` with `{"archived": true}` |
| `/leads/{id}/variables` | Broken | Use Campaign context |
| `GET /leads/{id}` | Unreliable | Use `/campaigns/{id}/leads/{id}` |

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for complete list.

## Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific workflow test
python -m pytest tests/test_common_mistakes.py -v
```

## Performance

The Lemlist API performs reliably for complex workflows. Results from our latest automated performance test (2026-03-17):

| Metric | Result |
|--------|--------|
| **Total Workflow Duration** | ~5-7 seconds |
| **Success Rate** | 100% |
| **Total Steps** | 13 |
| **Retries Needed** | 0 |

### Step Breakdown (Sample Run)

| Step | Description | Duration | Status |
|------|-------------|----------|--------|
| 1 | Create Campaign | 279ms | 200 ✓ |
| 2 | Add leads (5x) | ~300ms avg | 200 ✓ |
| 3 | Update variables (5x) | ~350ms avg | 200 ✓ |
| 4 | Verify leads | 76ms | 200 ✓ |
| 5 | Archive Campaign | 191ms | 200 ✓ |

**Key Finding:** `DELETE /campaigns/{id}` returns **HTTP 405**. Use `PATCH` with `{"archived": true}` instead.

## Validation

This skill was validated by autonomous agents without prior training:
- ✅ 10+ agent test runs
- ✅ 130+ endpoints verified
- ✅ Common mistakes documented
- ✅ Production workflows tested

Average time to first successful API call: **57 seconds**

## Contributing

Found an issue? The skill improves when you share what broke.

1. Test the endpoint
2. Document the behavior
3. Submit a PR

## License

MIT - Use it, improve it, share it.

---

**Not affiliated with Lemlist.** This is a community-maintained integration that prioritizes transparency over marketing.
