# Lemlist API - Troubleshooting Guide

> Häufige Probleme und Lösungen basierend auf realen Nutzungserfahrungen

---

## ⚠️ Bekannte Fallstricke

### 1. grep -P nicht verfügbar

**Problem:** `grep -P` (Perl-compatible regex) funktioniert nicht auf allen Systemen

**Fehler:**
```
grep: invalid option -- P
usage: grep [-abcdDEFGHhIiJLlMmnOopqRSsUVvwXxZz] ...
```

**Lösung:** Verwende `grep -E` (Extended regex) stattdessen:
```bash
# ❌ FALSCH (nicht überall verfügbar)
grep -oP '\{\{[^}]+\}\}'

# ✅ RICHTIG (portabel)
grep -oE '\{\{[^}]+\}\}'
```

---

### 2. Lead-Liste gibt nur IDs zurück

**Problem:** `GET /campaigns/{id}/leads` gibt nur `_id`, `state`, `contactId` zurück - keine vollständigen Lead-Daten oder Variablen

**Beispiel Response:**
```json
[
  {
    "_id": "lea_xxx",
    "state": "emailsOpened",
    "contactId": "ctc_yyy"
  }
]
```

**Lösung:** Einzelne Lead-Abfrage für Details:
```bash
# 1. Lead-IDs holen
LEADS=$(curl -s "https://api.lemlist.com/api/campaigns/{id}/leads" \
  --user ":$API_KEY" | jq -r '.[]._id')

# 2. Jeden Lead einzeln abfragen für Variablen
for LEAD_ID in $LEADS; do
  curl -s "https://api.lemlist.com/api/campaigns/{id}/leads/$LEAD_ID" \
    --user ":$API_KEY" | jq '.variables'
done
```

---

### 3. Lead-Variablen nur via Campaign-Lead Endpunkt

**Problem:** `/leads/{id}/variables` Endpunkte sind BROKEN

**Fehler:**
```json
{"error": "Variables not found"}
```

**Lösung:** Immer Campaign-Lead Kontext verwenden:
```bash
# ❌ FALSCH (broken)
GET /leads/{leadId}
POST /leads/{leadId}/variables

# ✅ RICHTIG
GET /campaigns/{campaignId}/leads/{leadId}
PATCH /campaigns/{campaignId}/leads/{leadId}
Body: {"variables": {"key": "value"}}
```

---

### 4. Campaign DELETE nicht unterstützt

**Problem:** `DELETE /campaigns/{id}` gibt 405 Method Not Allowed

**Lösung:** Archivieren statt löschen:
```bash
PATCH /campaigns/{id}
Body: {"archived": true}
```

---

### 5. PATCH Response Format

**Problem:** PATCH gibt `variables` als String `"[object Object]"` zurück statt JSON

**Beispiel:**
```json
{
  "variables": "[object Object]"  // ❌ String statt Objekt
}
```

**Lösung:** Das ist ein API-Bug auf Lemlist-Seite. Der PATCH funktioniert trotzdem, aber zur Verifikation erneut GET aufrufen:
```bash
# PATCH ausführen
curl -X PATCH ...

# Verifikation via GET
GET /campaigns/{id}/leads/{leadId}
```

---

## 🚀 Optimierte Workflows

### Workflow: Alle Leads mit Variablen abrufen

```bash
#!/bin/bash
CAMPAIGN_ID="cam_xxx"
API_KEY="$LEMLIST_API_KEY"

# 1. Lead-IDs holen
echo "Fetching lead IDs..."
LEAD_IDS=$(curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/leads" \
  --user ":$API_KEY" | jq -r '.[]._id')

# 2. Jeden Lead einzeln abfragen
echo "Fetching lead details..."
for LEAD_ID in $LEAD_IDS; do
  echo "--- Lead: $LEAD_ID ---"
  curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/leads/$LEAD_ID" \
    --user ":$API_KEY" | jq '{
      email: .email,
      firstName: .firstName,
      lastName: .lastName,
      variables: .variables
    }'
done
```

### Workflow: Variablen für mehrere Leads setzen

```bash
#!/bin/bash
CAMPAIGN_ID="cam_xxx"
API_KEY="$LEMLIST_API_KEY"

# Variablen für alle Leads setzen
LEAD_IDS="lea_1 lea_2 lea_3"

for LEAD_ID in $LEAD_IDS; do
  echo "Updating $LEAD_ID..."
  curl -s -X PATCH "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/leads/$LEAD_ID" \
    --user ":$API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"variables": {"priority": "high", "source": "api"}}' \
    && echo " ✓ Done"
done
```

---

## 📊 Performance Tipps

| Operation | Durchschnitt | Tipp |
|-----------|--------------|------|
| GET /campaigns | ~100ms | Cachen wenn möglich |
| GET /campaigns/{id}/leads | ~100ms | Gibt nur IDs - schnell |
| GET /campaigns/{id}/leads/{id} | ~150ms | Einzel-Abfragen parallelisieren |
| PATCH variables | ~250ms | Batch-Updates verwenden |
| POST /campaigns | ~200ms | - |

**Rate Limit:** 20 Requests / 2 Sekunden

---

## 🔧 Debugging

### API-Call debuggen

```bash
# Mit verbose Output
curl -v -X GET "https://api.lemlist.com/api/campaigns" \
  --user ":$LEMLIST_API_KEY" 2>&1 | grep -E "(> |< |HTTP)"

# Response speichern
curl -s -X GET "https://api.lemlist.com/api/campaigns" \
  --user ":$LEMLIST_API_KEY" > response.json
jq . response.json
```

### Auth testen

```bash
# Einfacher Auth-Test
curl -s "https://api.lemlist.com/api/team" \
  --user ":$LEMLIST_API_KEY" | jq -r '.name'
# Sollte Team-Namen zurückgeben
```

---

*Basierend auf realen Nutzungserfahrungen mit Claude Code und anderen Agenten*
