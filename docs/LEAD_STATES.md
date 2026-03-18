# Lemlist API - Lead States

> Stand: 2026-03-18 - Getestet mit 471 Leads in Live-Kampagne

---

## 🎯 Lead State Übersicht

Der `state` Feld in der Lead-Liste zeigt den aktuellen Status eines Leads in der Sequenz.

---

## 📊 Lead States Referenz

| State | Bedeutung | In Sequenz? |
|-------|-----------|-------------|
| `scanned` | Lead wurde erfasst/importiert | ✅ Ja, bereit |
| `emailsSent` | Erste Email wurde versendet | ✅ Ja, aktiv |
| `emailsOpened` | Email wurde geöffnet | ✅ Ja, aktiv |
| `emailsClicked` | Link in Email geklickt | ✅ Ja, aktiv |
| `emailsBounced` | Email konnte nicht zugestellt werden | ❌ Nein, gestoppt |
| `null` | Noch nicht gestartet | ✅ Ja, wartend |

---

## 📈 Beispiel-Verteilung

Basierend auf einer Kampagne mit 471 Leads:

```json
[
  {"state": "scanned", "count": 308},        // 65% - Bereit
  {"state": "emailsSent", "count": 72},        // 15% - Email 1 versendet
  {"state": "emailsClicked", "count": 46},     // 10% - Link geklickt
  {"state": "emailsOpened", "count": 43},      // 9% - Email geöffnet
  {"state": "emailsBounced", "count": 2}       // <1% - Ungültig
]
```

---

## 🔄 State Transitions

```
Import/Scan
    ↓
[scanned] ─────────────────────────────┐
    │                                    │
    │ Campaign Start                     │
    ↓                                    │
[emailsSent] ──→ [emailsOpened] ──→ [emailsClicked]
    │
    │ (ungültige Email)
    ↓
[emailsBounced]
```

---

## 🛠️ Praktische Anwendungen

### Leads filtern nach State

```bash
# Alle aktiven Leads (nicht bounced)
curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/leads?limit=1000" \
  --user ":$API_KEY" | jq '[.[] | select(.state != "emailsBounced")]'

# Leads die Email 1 erhalten haben
 curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/leads?limit=1000" \
   --user ":$API_KEY" | jq '[.[] | select(.state == "emailsSent")]'

# Leads die geklickt haben (für Follow-up)
curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/leads?limit=1000" \
  --user ":$API_KEY" | jq '[.[] | select(.state == "emailsClicked")]'
```

### State-Statistiken

```bash
# Verteilung anzeigen
curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/leads?limit=1000" \
  --user ":$API_KEY" | jq '
    group_by(.state) | 
    map({state: (.[0].state // "not_started"), count: length}) |
    sort_by(-.count)
  '
```

---

## ⚠️ Wichtige Hinweise

### State vs. isPaused

- `state` = Fortschritt in der Sequenz
- `isPaused` = Manuell pausiert (separates Feld)

Ein Lead kann `state: "emailsSent"` haben UND `isPaused: true`!

### Lead-Liste gibt nur Basis-Infos

```bash
GET /campaigns/{id}/leads
# Response: [{"_id": "...", "state": "...", "contactId": "..."}]
```

Für Details (Email, Name, Variablen):
```bash
GET /campaigns/{id}/leads/{leadId}
```

---

## 📊 "Launched" Leads

**Definition variiert:**

| Interpretation | Filter | Anzahl (Beispiel) |
|----------------|--------|-------------------|
| Strict | `state == "emailsSent"` | 72 |
| In Progress | `state != null` | 163 |
| All Active | `state != "emailsBounced"` | 469 |

---

*Dokumentation basierend auf Analyse von 471 Leads in Live-Kampagne*
