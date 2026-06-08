---
name: lemlist-openclaw
description: |
  Official Lemlist API integration for OpenClaw.
  Direct API access without external proxies.
  130+ endpoints for campaigns, leads, inbox, and more.
metadata:
  openclaw:
    emoji: "📧"
    skillKey: "lemlist-official"
    userInvocable: true
    requires:
      env:
        - LEMLIST_API_KEY
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

## MCP Server

Lemlist bietet einen offiziellen MCP-Server unter `https://app.lemlist.com/mcp`.

> **Tipp:** Die verfügbaren MCP-Tools entwickeln sich täglich weiter. Frage deinen AI-Assistenten direkt: *"What lemlist operations can you perform?"*

### OAuth (kein API-Key nötig)

#### Claude Code (OAuth)

```bash
claude mcp add --transport http lemlist https://app.lemlist.com/mcp
```

Beim ersten Aufruf öffnet sich automatisch ein Browser-Consent-Fenster.
Token-Lebensdauer: Access Token **1h**, Refresh Token **30 Tage** — wird automatisch verwaltet.

#### Claude Desktop (OAuth) — `claude_desktop_config.json`

```json
{
  "mcpServers": {
    "lemlist": {
      "command": "npx",
      "args": ["mcp-remote", "https://app.lemlist.com/mcp"]
    }
  }
}
```

### Mit API-Key

#### Claude Code

```bash
claude mcp add --transport http lemlist https://app.lemlist.com/mcp --header "X-API-Key: PUTYOURAPIKEY"
```

#### Cursor — Settings/Tools & MCP

```json
{
  "mcpServers": {
    "lemlist": {
      "url": "https://app.lemlist.com/mcp",
      "headers": { "X-API-Key": "... YOUR API KEY ..." }
    }
  }
}
```

#### Claude Desktop mit npm — `claude_desktop_config.json`

```json
{
  "mcpServers": {
    "lemlist": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://app.lemlist.com/mcp",
        "--header",
        "X-API-Key: ${API_KEY}"
      ],
      "env": { "API_KEY": "... YOUR API KEY ..." }
    }
  }
}
```

**Windows:**

```json
{
  "lemlist": {
    "command": "C:\\PROGRA~1\\nodejs\\npx.cmd",
    "args": ["mcp-remote", "https://app.lemlist.com/mcp", "--header", "X-API-Key: ${API_KEY}"],
    "env": { "API_KEY": "... YOUR API KEY ..." }
  }
}
```

### MCP Tool-Namen (wichtigste)

| Tool | Beschreibung |
|------|-------------|
| `get_campaigns` | Alle Kampagnen auflisten |
| `get_campaign_details` | Kampagnen-Details abrufen |
| `get_campaign_sequences` | E-Mail-Sequenz/Copy abrufen |
| `get_campaign_stats` | Performance-Metriken analysieren |
| `create_campaign_with_sequence` | Neue Kampagne mit Sequenz anlegen |
| `add_sequence_step` | Follow-up hinzufügen |
| `preview_sequence_update` | Änderungen vor Anwendung prüfen |
| `update_sequence_step` | Bestehende E-Mails bearbeiten |
| `search_campaign_leads` | Leads nach E-Mail/ID suchen |
| `add_lead_to_campaign` | Lead importieren (mit optionalem Enrichment) |
| `get_lemleads_filters` | Verfügbare Suchfilter abrufen |
| `lemleads_search` | 450M+ B2B-Datenbank durchsuchen |
| `get_team_info` | Team-Details abrufen |

### MCP Technischer Stack

- **Stack:** Node.js (MeteorJS)
- **Protokoll:** MCP (JSON-RPC 2.0 über HTTP/POST)
- **Auth:** `X-API-Key` Header oder OAuth
- **Validation:** Zod Schemas
- **Health Check:** `GET https://app.lemlist.com/mcp/health`

### lemlist-agent (Claude Code Command)

Spezialisierter Agent als wiederverwendbarer `/lemlist-agent` Command. Datei unter `.claude/commands/lemlist-agent.md` ablegen:

```bash
# Aktivieren mit:
/lemlist-agent
```

Der Agent führt automatisch Campaign-Audits durch, sourct Leads aus der Lemleads-Datenbank und erstellt optimierte E-Mail-Sequenzen (AIDA, PAS, BAB Frameworks).

**Sicherheits-Protokolle des Agents:**

- Warnt vor Credit-Kosten bei: `findEmail`, `verifyEmail`, `linkedinEnrichment`, `findPhone`
- Nutzt `preview_sequence_update` vor Live-Änderungen
- Prüft Kampagnenstatus vor Bearbeitung (laufende Kampagnen können nicht editiert werden)
- Fordert Bestätigung vor Änderungen an laufenden Kampagnen

---

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

⚠️ **NICHT Bearer-Token!** Lemlist nutzt HTTP Basic Auth, nicht Bearer. Häufiger Fehler.

⚠️ **API v2:** über Query-Param `?version=v2` aktivieren, NICHT Pfad-Änderung. Base bleibt `https://api.lemlist.com/api`.

⚠️ **Cloudflare blockt Nicht-Browser-Clients** (verifiziert 2026-06-08): Python `urllib`/`requests` mit Default-UA (`Python-urllib/3.x`) bekommen `403 {error code: 1010}` auf JEDEN Endpoint. `curl` (Default-UA `curl/x.y`) geht durch. Fix für eigene Skripte: Browser-`User-Agent`-Header setzen, z.B. `Mozilla/5.0 (...) Chrome/124.0 Safari/537.36`.

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
| `/campaigns/{id}` | DELETE | Delete campaign |
| `/campaigns/{id}/duplicate` | POST | **Duplicate campaign** — body: `{name}` — kopiert Sequence-Steps + Schedules + AI-Vars in 1 Call (sauberster Weg für Tenant-from-Template) |
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
| `/campaigns/{id}/leads` | GET | List leads in campaign (⚠️ only `_id`, `state`, `contactId`) |
| `/campaigns/{id}/leads` | POST | Add lead to campaign |
| `/leads/{email}` | GET | Get lead by email |
| `/leads` | GET | Get lead by email or ID |
| `/campaigns/{id}/leads/{leadId}` | PATCH | Update lead |
| `/campaigns/{id}/leads/{leadId}` | DELETE | Remove/unsubscribe lead |
| `/leads/pause/{leadId}` | POST | Pause lead |
| `/leads/start/{leadId}` | POST | Resume lead |
| `/leads/interested/{leadId}` | POST | Mark as interested |
| `/leads/notinterested/{leadId}` | POST | Mark as not interested |

**Pagination:** Use `?limit=1000` - see [docs/PAGINATION.md](docs/PAGINATION.md)

**Lead States:** `scanned`, `emailsSent`, `emailsOpened`, `emailsClicked`, `emailsBounced` - see [docs/LEAD_STATES.md](docs/LEAD_STATES.md)

### Lead Variables (IMPORTANT!)

⚠️ **CRITICAL:** Lead variables ONLY work through the Campaign context!

**❌ BROKEN - Do NOT use:**
```
POST /leads/{leadId}/variables
PATCH /leads/{leadId}/variables
DELETE /leads/{leadId}/variables
GET /leads/{leadId}  (often returns "not found")
```

**✅ CORRECT - Use these instead:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/campaigns/{id}/leads/{leadId}` | PATCH | Update lead variables |
| `/campaigns/{id}/leads/{leadId}` | GET | Get lead with variables |
| `/campaigns/{id}/leads` | GET | List all leads with variables |

**Setting Variables:**
```bash
PATCH /campaigns/{campaignId}/leads/{leadId}
Body: {
  "variables": {
    "custom_field": "value",
    "priority": "high"
  }
}
```

**Notes:**
- Variables are merged (not overwritten) on PATCH
- Always use Campaign context for reliable results
- See `docs/PROCESS_DOCUMENTATION.md` for detailed workflow

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

⚠️ **Signature-Validation:** Lemlist nutzt **KEIN HMAC**. Stattdessen wird das beim Create gesetzte `secret`-Field im JSON-Body jedes Webhook-Calls zurückgesendet. Validation = String-Compare auf Body-Field. Secret ist **immutable** nach Create und wird via `GET /hooks` NICHT zurückgegeben → bei Create lokal speichern.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/hooks` | GET | List webhooks |
| `/hooks` | POST | Create webhook — body: `{targetUrl, events:[...], secret}` |
| `/hooks/{hookId}` | DELETE | Delete webhook |

**Verfügbare Events** (50+ — Lemlist-Stand 2026-05):
- **Email:** `emailsSent, emailsOpened, emailsClicked, emailsReplied, emailsBounced, emailsSendFailed, emailsFailed, emailsUnsubscribed, emailsInterested, emailsNotInterested`
- **Activity:** `contacted, hooked, attracted, warmed, interested, skipped, notInterested, opportunitiesDone, paused, resumed`
- **LinkedIn:** `linkedinVisitDone/Failed, linkedinInviteDone/Failed/Accepted, linkedinReplied, linkedinSent, linkedinVoiceNoteDone/Failed, linkedinInterested/NotInterested, linkedinSendFailed`
- **Aircall (Phone):** `aircallCreated/Ended/Done/Interested/NotInterested`
- **API/Manual:** `apiDone/Interested/NotInterested/Failed, manualInterested/NotInterested`
- **Operational:** `customDomainErrors, connectionIssue, sendLimitReached, lemwarmPaused, campaignComplete, annotated, enrichmentDone/Error, callRecordingDone, callTranscriptDone`

**KEIN Event** für `mailboxConnected` / `oauthCompleted` → Polling auf `GET /user.mailboxes` Pflicht.

### Unsubscribes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/unsubscribes` | GET | List unsubscribes |
| `/unsubscribes/{email}` | GET | Check unsubscribe status |
| `/unsubscribes` | POST | Add unsubscribe |
| `/unsubscribes/{email}` | DELETE | Remove unsubscribe |

### Enrichment

⚠️ **`/enrich` Params gehören in den QUERY-STRING, NICHT in den JSON-Body** (verifiziert 2026-06-08). Body-Flags werden ignoriert → `400 "No enrichment requested"`. Body leer lassen, alles als `?email=...&findPhone=true&...` anhängen. Flags: `findEmail | findPhone | linkedinEnrichment | verifyEmail` (mind. 1). Browser-`User-Agent` Pflicht (sonst CF `403 1010`). Async: POST → `{"id":"enr_..."}`, dann `GET /enrich/{id}` bis `enrichmentStatus=="done"` pollen.
Phone-Shape: Treffer `data.phone={"phone":"+49…","notFound":false}`; sonst `{"notFound":false/true}`. Kosten: Phone nur bei Treffer (~24 cr/Nr), notFound ~gratis; DE-Hit-Rate ~33%. Identitäts-Match läuft primär über die **E-Mail** (eindeutiger Key); Vor-/Nachname + Firma sind nur Hints. Details: [docs/PROCESS_DOCUMENTATION.md](docs/PROCESS_DOCUMENTATION.md) §5.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/enrich?<params>` | POST | Enrich single entity (params in QUERY-STRING, body empty, async) |
| `/v2/enrichments/bulk` | POST | Bulk enrichment (max 500) |
| `/enrich/{enrichId}` | GET | Get enrichment result (poll until `enrichmentStatus==done`) |
| `/leads/{leadId}/enrich` | POST | Enrich existing lead |

### Database (Lemleads B2B-DB, 450M)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/schema/people` | GET | Get people schema |
| `/schema/companies` | GET | Get companies schema |
| `/database/filters` | GET | Get database filters — **39 filterIds incl. industry tree, seniority enum, headcount bands, etc.** Full spec: [docs/DATABASE_FILTERS.md](docs/DATABASE_FILTERS.md) + raw [docs/database-filters-spec.json](docs/database-filters-spec.json) |
| `/database/people` | POST | Search people database — body `{filters:[{filterId,in[],out[]}], page, size}`, max 100/page |
| `/database/companies` | POST | Search companies database — same shape, only `mode:companies` filterIds |

#### Filter Quick-Reference (most common ICP fields)
- **Role:** `currentTitle`, `seniority` (7-enum: Entry-Level → Ownership / Firm Leadership), `department` (~30-enum)
- **Company:** `currentCompanyHeadcount` (8 bands), `currentCompanySubIndustry` (hierarchical level), `currentCompanyRevenue` (8 buckets), `currentCompanyMarket` (B2B/B2C/B2B/B2C), `currentCompanyType`
- **Geo:** `country`, `region` (incl. `DACH` shorthand), `currentCompanyCountry`
- **Search keywords:** `keyword` (profile-level: headline+summary+skills), `keywordInCompany` (company-description-level — use to dodge "fridge in plane post" false-positives)

⚠️ **Seniority enum changed** in 2026 — old `CxO/Director/Vice President/Owner-Partner` no longer match. Migrate to current 7-level enum.

⚠️ **Silent zero on bad values** (verified 2026-05-21): an off-taxonomy filter value (e.g. legacy `currentCompanySubIndustry` strings like `Computer Software`/`Internet`) returns `200 {results:[],total:0}`, NOT an error. filterIds are AND-ed → one stale value zeroes the whole search. On unexpected-empty, isolate filters one at a time. Look subIndustry values up via `GET /database/filters`, never guess.

⚠️ **No email in discovery** — `/database/people` results carry no email; email needs the paid enrichment endpoints. Response also returns `total`, `took`(ms), `search`(`lsh_` handle), `limitation`(remaining daily-search quota), `team`.

### CRM (verified live 2026-05-04)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/contacts` | GET, POST | Contacts CRUD (POST needs identifier in body) |
| `/companies` | GET, POST | Companies CRUD |
| `/fields` | GET | Custom Fields (read-only — POST returns 405) |
| `/tasks` | GET, POST | Tasks CRUD |
| `/watchlist/signals` | GET | Watchlist signals stream |

### Inbox-Labels

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/inbox/labels` | GET, POST | List/create labels |

### NOT-EXISTS (verified — vorher fälschlich im Skill)

Diese Pfade sind HTML-catchall (= Lemlist-Web-App-Route, KEIN API):
- `/contact-lists` ❌
- `/notes` ❌
- `/opportunities` ❌
- `/email-accounts` (ohne `/user/` prefix) ❌ — korrekt: `/user/email-accounts`
- `/inbox/drafts/{contactId}` GET ❌ — Draft-Pfad zu klären
- `/teams`, `/users`, `/billing/cards`, `/domains`, `/team/sending/domains` ❌ (kein Tenant-Provisioning-API)

### Email Accounts & lemwarm

⚠️ **Path-Correction:** Email-Accounts hängen unter `/user/email-accounts`, NICHT `/email-accounts` (Skill-Annahme war falsch — Live-test 2026-05-04: `/email-accounts` GET = HTML-catchall, `/user/email-accounts` GET = 402 Plan-blocked = real route).

⚠️ **Gmail/Microsoft:** SMTP/IMAP-Direct-Connect wird **abgelehnt** — OAuth-UI-Klick zwingend. Custom-SMTP-Provider (Postmark, Mailgun, eigene Server) gehen API-able mit `smtp_host/port/login/password` + `imap_*` Body.

⚠️ **lemwarm 2-Call-Pattern:** Start ist parameterlos (`POST /lemwarm/{id}/start` body=empty → returns `{ok:true}`). Settings via separater `PATCH /lemwarm/{id}/settings` Call. **Nur 2 Params settable:** `warmEmailMax` + `warmEmailRampup`. `dailyEmails`, `replyRate`, `rampUp` existieren NICHT.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/user/email-accounts` | POST | Connect email account (Custom-SMTP only — Gmail/MS via UI-OAuth) |
| `/user/email-accounts/{id}` | DELETE | Disconnect (soft: removes credentials, pauses warmup, unlinks campaigns) |
| `/email-accounts/{id}/test` | POST | Test email connection |
| `/lemwarm/{id}` | GET | Get lemwarm settings (returns `active, dailyLimit, warmupTemplate, deliverability`) |
| `/lemwarm/{id}/start` | POST | Start lemwarm — **parameterless** |
| `/lemwarm/{id}/pause` | POST | Pause lemwarm |
| `/lemwarm/{id}/settings` | PATCH | Update lemwarm settings — only `warmEmailMax` + `warmEmailRampup` settable |

**Mailbox-OAuth-Status:** Kein Webhook-Event für `mailboxConnected` / `oauthCompleted`. Polling auf `GET /user.mailboxes` Pflicht.

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

## Email Personalization — Liquid Syntax

Lemlist verwendet Liquid-Syntax für dynamische E-Mail-Inhalte:

```liquid
{{ firstName | default: "there" }}
{{ companyName | default: "your company" }}

{% if companyName %}your neighbors in{% else %}those in{% endif %} Silicon Valley
```

**Best Practices:**
- Immer `| default: "..."` setzen, damit Emails auch ohne den Wert valide sind
- Personalisierung über `{{firstName}}` hinaus: Firma, Branche, aktuelle News
- E-Mails unter 100 Wörter halten
- Ein klarer CTA pro E-Mail
- Versandzeiten: Dienstag–Donnerstag, 8–10 Uhr oder 14–16 Uhr (Empfänger-Timezone)
- Follow-up-Abstand: Tag 3, 7, 14

## Documentation

For detailed guides on specific topics, see the `docs/` directory:

| Document | Topic |
|----------|-------|
| [docs/authentication.md](docs/authentication.md) | Authentication methods |
| [docs/error-handling.md](docs/error-handling.md) | Error codes and handling |
| [docs/rate-limits.md](docs/rate-limits.md) | Rate limiting details |
| [docs/PROCESS_DOCUMENTATION.md](docs/PROCESS_DOCUMENTATION.md) | Verified workflows |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [docs/PAGINATION.md](docs/PAGINATION.md) | Pagination behavior |
| [docs/LEAD_STATES.md](docs/LEAD_STATES.md) | Lead state reference |
| [docs/ASSUMPTIONS_TESTED.md](docs/ASSUMPTIONS_TESTED.md) | Tested assumptions |
| [docs/testing.md](docs/testing.md) | Testing guidelines |

---

*Last updated: 2026-06-08*
