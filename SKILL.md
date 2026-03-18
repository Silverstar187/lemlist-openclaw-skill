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

# ⚠️ AGENTEN: DU MUSST DIESEN SKILL ZUERST LESEN!

> **🤖 AGENT INSTRUCTION:** Wenn du diese Datei siehst, ist dein ERSTER SCHRIMM das Lesen dieser Datei `~/.agents/skills/lemlist-openclaw/SKILL.md`!
> 
> **WICHTIGE REGELN:**
> 1. **IMMER Skill lesen zuerst** - Dieser Skill enthält kritische Workarounds
> 2. **Lead API liefert oft leere Werte** → CSV Export verwenden!
> 3. **NIE direkt API-Calls raten** - Die Endpoints sind unintuitiv
> 
> **Schnell-Navigation:**
> - [🎯 Agent Playbook](#-agent-playbook-decision-trees)
> - [⚠️ Lead API Troubleshooting](#-troubleshooting---leads-abrufen-leere-response)
> - [📋 Quick Start](#quick-start)

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

---

## 🤖 Agent Playbook (Decision Trees)

### 🎯 USE CASE: "Leads zur Campaign hinzufügen"
```
1. Lead-Daten vorbereiten (Email, firstName, variables)
2. POST /campaigns/{id}/leads
3. CSV Export verify: /campaigns/{id}/export/start → Download → Check
```

### 🎯 USE CASE: "Follow-ups sollen versendet werden"
```
1. Campaign Status prüfen → GET /campaigns/{id}
   └─ Status != "running"? → POST /campaigns/{id}/start
2. Sequenz-Struktur prüfen → GET /campaigns/{id}/sequences
   └─ Follow-up Step mit Delay > 0?
3. Lead-Variablen prüfen → CSV Export (verlässlich!)
   ├─ Leads mit {{email_betreff_follow1}} Variablen? → Weiter bei 4a
   └─ Leads ohne Variablen? → Weiter bei 4b
4a. Leads MIT Variablen:
    └─ Nur die mit Variablen aktivieren → POST /leads/start/{leadId}
4b. Leads OHNE Variablen (und noch nicht gestartet):
    └─ NUR scanned Leads pausieren → POST /leads/pause/{leadId}
       ⚠️ Achtung: Pause funktioniert NUR für scanned Leads!
       Leads mit emailsSent/opened/clicked können NICHT pausiert werden!
```

### 🎯 USE CASE: "Lead-Variablen ändern"
```
1. Lead-ID finden → CSV Export oder /campaigns/{id}/leads
2. PATCH /campaigns/{id}/leads/{leadId} mit neuen Variablen
3. Verifizieren → CSV Export (nicht Einzel-Lead API!)
```

---

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

**⚠️ TROUBLESHOOTING - Auth Fehler:**
- Fehler: `"The authentication you supplied is incorrect"` → API Key prüfen
- Fehler: `"Bad team"` → API Key gehört zu falschem Account

**Debugging & jq Best Practices:**

```bash
# RESPONSE IMMER ZUERST SPEICHERN - dann mit jq analysieren
# Das vermeidet Syntax-Fehler bei komplexen jq-Filtern

curl -s "https://api.lemlist.com/api/campaigns/cam_xxx/sequences" \
  --user ":$LEMLIST_API_KEY" > /tmp/response.json

# DANN: Einfache jq Filter verwenden
jq '.[] | ._id, .name' /tmp/response.json           # IDs und Namen
jq '.[] | .steps | length' /tmp/response.json      # Anzahl Steps
jq '.[].steps[].subject' /tmp/response.json        # Alle Betreffzeilen

# VERMEIDEN: Komplexe String-Interpolationen in jq
# STATT: jq '.[] | "\(.id): \(.name)"'            # Kann fehlschlagen
# BESSER: jq '.[] | {id: ._id, name: .name}'       # Sauberes JSON

# API-Call debuggen mit verbose Output
curl -v -X GET "https://api.lemlist.com/api/campaigns" \
  --user ":$LEMLIST_API_KEY" 2>&1 | grep -E "(> |< |HTTP)"
```

### 3. List Campaigns

```bash
curl -s "https://api.lemlist.com/api/campaigns" \
  --user ":$LEMLIST_API_KEY" | jq '.[] | {id: ._id, name: .name, status: .status}'

# Campaign nach Name filtern (case-insensitive)
curl -s "https://api.lemlist.com/api/campaigns" \
  --user ":$LEMLIST_API_KEY" | jq '.[] | select(.name | ascii_downcase | contains("search_term")) | {id: ._id, name: .name, status: .status}'
```

## Authentication

Lemlist uses **HTTP Basic Auth** with an empty username and your API key as the password:

**REGEL: API-Key IMMER aus der .env im lemlist-integration Ordner holen:**
```bash
# 1. API Key aus der .env Datei laden
export LEMLIST_API_KEY="your_api_key_here"
# Alternative: Aus Umgebungsvariable laden
# export LEMLIST_API_KEY="$LEMLIST_API_KEY"

# 2. ODER direkt setzen (nur wenn .env nicht verfügbar)
export LEMLIST_API_KEY="your_key_here"
```

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
| `/campaigns/{id}` | PATCH | Update campaign (name, archived) |
| `/campaigns/{id}` | DELETE | ⚠️ **NOT SUPPORTED** - 405 Error |
| `/campaigns/{id}/start` | POST | **Start campaign** - Triggert Follow-up Versand |
| `/campaigns/{id}/pause` | POST | **Pause campaign** - Stoppt alle Aktivitäten |
| `/campaigns/{id}/stats` | GET | Get campaign statistics |
| `/campaigns/reports` | GET | Get aggregated reports |
| `/campaigns/{id}/export/start` | GET | Start CSV export |
| `/campaigns/{id}/export/{exportId}/status` | GET | Check export status |
| `/campaigns/{id}/sequences` | GET | Get campaign sequences |
| `/campaigns/{id}/schedules` | GET | Get campaign schedules |

**Sequenz-Struktur analysieren:**

```bash
# Alle Steps einer Campaign anzeigen
CAMPAIGN_ID="cam_xxx"
curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/sequences" \
  --user ":$LEMLIST_API_KEY" | jq '.[] | {seqId: ._id, steps: [.steps[] | {index, delay, subject, templateId: .emailTemplateId}]}'
```

**Template-Variablen extrahieren (ALLE Variablen in einer Sequenz):**

```bash
# WICHTIG: Variablen sind in {{doppelten_geschweiften_klammern}}
# Extrahiere ALLE Variablen aus allen Sequenzen einer Campaign
CAMPAIGN_ID="cam_xxx"
curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/sequences" \
  --user ":$LEMLIST_API_KEY" | grep -oE '\{\{[^}]+\}\}' | sort | uniq

# Beispiel-Output:
# {{email_betreff_1}}
# {{email_betreff_follow1}}
# {{email_nachricht_1}}
# {{email_nachricht_follow1}}
```

**⚠️ TROUBLESHOOTING - Campaign löschen:**

`DELETE /campaigns/{id}` gibt **405 Method Not Allowed**!

**✅ Lösung - Campaign archivieren statt löschen:**
```bash
# Campaign archivieren (soft delete)
PATCH /campaigns/{id}
Body: {"archived": true}
```

---

### Campaign Status & Follow-up Steuerung

**USE CASE: Campaign pausiert → Follow-ups sollen versendet werden**

```bash
CAMPAIGN_ID="cam_xxx"

# 1. Aktuellen Status prüfen
curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID" \
  --user ":$LEMLIST_API_KEY" | jq '{id: ._id, name: .name, status: .status}'

# 2. Campaign starten (reaktiviert automatisch alle Leads)
curl -s -X POST "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/start" \
  --user ":$LEMLIST_API_KEY" | jq '.'

# 3. Status verifizieren (sollte "running" sein)
curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID" \
  --user ":$LEMLIST_API_KEY" | jq '.status'
```

**WANN WERDEN FOLLOW-UPS VERSENDET?**

| Campaign Status | Lead Status | Follow-up wird versendet? |
|----------------|-------------|---------------------------|
| `running` | `emailsSent` | ✅ Ja (nach Delay) |
| `running` | `emailsOpened` | ✅ Ja (nach Delay) |
| `running` | `emailsClicked` | ✅ Ja (nach Delay) |
| `paused` | *irgendein* | ❌ Nein (Campaign gestoppt) |
| `running` | `paused` | ❌ Nein (Lead manuell pausiert) |

**Lead MANUELL reaktivieren (falls einzelner Lead pausiert ist):**
```bash
# Lead starten (nur wenn Lead individuell pausiert wurde)
curl -s -X POST "https://api.lemlist.com/api/leads/start/lea_xxx" \
  --user ":$LEMLIST_API_KEY"
```

**CHECKLIST: Follow-ups versenden:**
1. ✅ Campaign Status = `running`
2. ✅ Leads haben Variablen für Follow-up gesetzt (`email_betreff_follow1`)
3. ✅ Leads sind nicht manuell pausiert (`state` != `paused`)
4. ✅ Sequenz hat Follow-up Step mit korrektem Delay

### Leads

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/campaigns/{id}/leads` | GET | List leads in campaign |
| `/campaigns/{id}/leads` | POST | Add lead to campaign |
| `/leads/{email}` | GET | ⚠️ **BROKEN** - Use `/campaigns/{id}/leads/{leadId}` instead |
| `/leads` | GET | ⚠️ **BROKEN** - Use `/campaigns/{id}/leads` instead |
| `/campaigns/{id}/leads/{leadId}` | PATCH | Update lead variables |
| `/campaigns/{id}/leads/{leadId}` | DELETE | Remove/unsubscribe lead |
| `/leads/pause/{leadId}` | POST | Pause lead (⚠️ **NUR für `scanned` Leads!**) |
| `/leads/start/{leadId}` | POST | Resume lead |

**⚠️ WICHTIG: Lead Pause funktioniert nur für `scanned` Leads!**

Die Pause-API (`POST /leads/pause/{leadId}`) funktioniert **NUR** für Leads im Status `scanned` (die noch keine Email erhalten haben).

**Warum?** Leads die bereits `emailsSent`, `emailsOpened`, `emailsClicked` oder `emailsBounced` sind, haben bereits die erste Email erhalten. Diese kann man NICHT mehr pausieren - sie sind bereits "unterwegs" in der Sequenz.

**Richtiger Workflow zum Pausieren:**
```bash
# 1. Leads holen
LEADS=$(curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/leads?limit=1000" \
  --user ":$LEMLIST_API_KEY")

# 2. NUR scanned Leads filtern (die man pausieren KANN)
SCANNED_LEADS=$(echo $LEADS | jq -r '.[] | select(.state == "scanned") | ._id')

# 3. Diese pausieren
for LEAD_ID in $SCANNED_LEADS; do
  curl -s -X POST "https://api.lemlist.com/api/leads/pause/$LEAD_ID" \
    --user ":$LEMLIST_API_KEY"
  sleep 0.15
done
```

**Lead States Übersicht:**
| State | Bedeutung | Pausierbar? |
|-------|-----------|-------------|
| `scanned` | Noch keine Email gesendet | ✅ Ja |
| `emailsSent` | Email wurde gesendet | ❌ Nein |
| `emailsOpened` | Email wurde geöffnet | ❌ Nein |
| `emailsClicked` | Link in Email geklickt | ❌ Nein |
| `emailsBounced` | Email bounced | ❌ Nein |
| `/leads/interested/{leadId}` | POST | Mark as interested |
| `/leads/notinterested/{leadId}` | POST | Mark as not interested |

**Pagination:** Use `?limit=1000` - see [docs/PAGINATION.md](docs/PAGINATION.md)

**Lead States:** `scanned`, `emailsSent`, `emailsOpened`, `emailsClicked`, `emailsBounced` - see [docs/LEAD_STATES.md](docs/LEAD_STATES.md)

---

## ⚠️ TROUBLESHOOTING - Leads abrufen (KRITISCH!)

### 🔴 PROBLEM: Leads API gibt leere/unvollständige Werte zurück!

Das Endpunkt `GET /campaigns/{id}/leads` gibt **nur** `_id`, `state`, `contactId` zurück - **keine vollständigen Lead-Daten oder Variablen**!

Und `GET /campaigns/{id}/leads/{leadId}` gibt oft **HTTP 200 mit leerem Body** zurück!

**❌ FALSCH (liefert NULL Werte):**
```bash
curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/leads" \
  --user ":$LEMLIST_API_KEY" | jq '.[] | {email, firstName, variables}'
# Output: {"email": null, "firstName": null, "variables": null}
```

---

## ✅ LÖSUNG: CSV Export (PRIMARY METHODE)

**IMMER CSV Export verwenden für verlässliche Lead-Daten!**

```bash
CAMPAIGN_ID="cam_xxx"

# 1. Export starten
EXPORT_RESULT=$(curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/export/start" \
  --user ":$LEMLIST_API_KEY")
EXPORT_ID=$(echo $EXPORT_RESULT | jq -r '._id')
FILE_URL=$(echo $EXPORT_RESULT | jq -r '.fileUrl')

# 2. Falls fileUrl direkt verfügbar, sofort downloaden
#    Sonst: 30-60 Sekunden warten und Status abfragen
if [ "$FILE_URL" != "null" ] && [ -n "$FILE_URL" ]; then
  curl -s "$FILE_URL" -o /tmp/leads.csv
else
  sleep 45
  DOWNLOAD_URL=$(curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/export/$EXPORT_ID/status" \
    --user ":$LEMLIST_API_KEY" | jq -r '.fileUrl')
  curl -s "$DOWNLOAD_URL" -o /tmp/leads.csv
fi

# 3. Lead-Daten filtern und analysieren
echo "=== Leads mit Follow-up Variablen ==="
grep "email_betreff_follow1" /tmp/leads.csv | wc -l

# 4. Als JSON konvertieren für weitere Verarbeitung
python3 -c "
import csv, json
with open('/tmp/leads.csv') as f:
    leads = list(csv.DictReader(f))
    # Filtern: Leads mit email_betreff_follow1 gesetzt
    follow_leads = [l for l in leads if l.get('email_betreff_follow1')]
    print(json.dumps(follow_leads, indent=2))
    print(f'\nTotal: {len(leads)}, With follow1: {len(follow_leads)}', file=__import__('sys').stderr)
"
```

**Entscheidungstabelle:**
| Kriterium | CSV Export | Einzel-Lead API |
|-----------|------------|-----------------|
| **Zuverlässigkeit** | ✅ **100%** | ❌ 30% leere Response |
| **Alle Daten** | ✅ Ja | ❌ Nur IDs |
| **Speed** | ⚠️ 30-60s | ✅ Sofort |
| **Empfohlen für Agenten** | ✅ **JA** | ❌ Nein |

---

### Lead Variables

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/campaigns/{id}/leads/{leadId}` | PATCH | Update lead variables (✅ **USE THIS**) |
| `/campaigns/{id}/leads/{leadId}` | GET | Get lead with variables (✅ **USE THIS**) |
| `/campaigns/{id}/leads` | GET | List leads (nur IDs, keine Variablen) |

**⚠️ TROUBLESHOOTING - Lead Variablen:**

**❌ BROKEN - NIE verwenden:**
```
POST /leads/{leadId}/variables  → {"error": "Variables not found"}
PATCH /leads/{leadId}/variables → {"error": "Variables not found"}
GET /leads/{leadId}             → "not found" oder unvollständig
GET /leads?contactId=ctc_xxx    → jq parse error
```

**✅ KORREKT - Immer Campaign-Lead Kontext verwenden:**
```bash
# Variablen setzen/aktualisieren
PATCH /campaigns/{campaignId}/leads/{leadId}
Body: {"variables": {"custom_field": "value", "priority": "high"}}

# Variablen abrufen
GET /campaigns/{campaignId}/leads/{leadId}
```

**⚠️ PATCH Response Bug:**
Der PATCH gibt manchmal `"variables": "[object Object]"` als String zurück - das ist ein API-Bug auf Lemlist-Seite. Der PATCH funktioniert trotzdem! Zur Verifikation erneut GET aufrufen.

**Notes:**
- Variables werden bei PATCH gemerged (nicht überschrieben)
- IMMER Campaign-Lead Kontext verwenden für zuverlässige Ergebnisse

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
