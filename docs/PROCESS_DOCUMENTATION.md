# Lemlist API - Prozess-Dokumentation (Geklärt)

> Stand: 2026-03-17 - Alle Prozesse getestet und verifiziert

---

## 🎯 Wichtigste Erkenntnis

**ALLE Lead-Operationen MÜSSEN über den Campaign-Kontext laufen!**

Die Endpunkte `/leads/{id}` und `/leads/{id}/variables` funktionieren NICHT zuverlässig.

---

## ✅ Korrekte API-Struktur

### Lead-Variablen

**❌ FALSCH (funktioniert nicht):**
```bash
# Diese Endpunkte sind BROKEN
POST /leads/{leadId}/variables
PATCH /leads/{leadId}/variables
GET /leads/{leadId}
```

**✅ RICHTIG (funktioniert):**
```bash
# Variablen setzen/aktualisieren
PATCH /campaigns/{campaignId}/leads/{leadId}
Body: {"variables": {"key": "value"}}

# Lead Details abrufen
GET /campaigns/{campaignId}/leads/{leadId}

# Alle Leads der Campaign
GET /campaigns/{campaignId}/leads
```

---

## 📋 Vollständiger Workflow (Tested)

### 1. Campaign Erstellen
```bash
POST /campaigns
Body: {
  "name": "My Campaign",
  "status": "draft"  # Wichtig: draft = nichts wird versendet!
}
```
**Response:** `{"_id": "cam_xxx", ...}`

### 2. Leads Hinzufügen
```bash
POST /campaigns/{campaignId}/leads
Body: {
  "email": "lead@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "companyName": "Acme Inc",
  "variables": {
    "custom_field": "value"
  }
}
```

### 3. Variablen Aktualisieren (WICHTIG!)
```bash
PATCH /campaigns/{campaignId}/leads/{leadId}
Body: {
  "variables": {
    "new_var": "new_value",
    "existing_var": "updated_value"
  }
}
```
**Hinweis:** Variablen werden gemerged, nicht überschrieben!

### 4. Leads Lesen
```bash
# Alle Leads
GET /campaigns/{campaignId}/leads

# Einzelner Lead
GET /campaigns/{campaignId}/leads/{leadId}
```

### 5. Enrichment (Optional)
```bash
POST /enrich
Body: {
  "email": "lead@example.com",
  "findEmail": true,
  "linkedinEnrichment": true
}
```

### 6. Sequenz Erstellen (Optional)
```bash
POST /campaigns/{campaignId}/sequence
Body: {
  "type": "api",  # oder "email", "linkedinVisit", etc.
  "name": "Step Name",
  "delay": 0
}
```

### 7. Campaign Starten (⚠️ Erst wenn wirklich versenden!)
```bash
POST /campaigns/{campaignId}/start
```

---

## ⚠️ Bekannte Probleme & Workarounds

### Problem 1: Lead nicht gefunden
**Symptom:** `GET /leads/{id}` gibt "Lead not found"

**Lösung:** Immer `/campaigns/{campaignId}/leads/{id}` verwenden

### Problem 2: Variablen nicht aktualisierbar
**Symptom:** `PATCH /leads/{id}/variables` funktioniert nicht

**Lösung:** `PATCH /campaigns/{campaignId}/leads/{id}` mit `{"variables": {...}}`

### Problem 3: POST auf Variablen gibt "already exist"
**Symptom:** `POST /leads/{id}/variables` sagt Variable existiert schon

**Lösung:** Nie POST verwenden, immer PATCH über Campaign-Lead

---

## 🔑 Authentifizierung

**Basic Auth mit leerem Username:**
```bash
curl --user ":$LEMLIST_API_KEY" https://api.lemlist.com/api/team
```

**Header-Variante:**
```bash
Authorization: Basic $(echo -n ':$LEMLIST_API_KEY' | base64)
```

---

## 📊 Rate Limits

- **20 Requests / 2 Sekunden**
- Per API Key
- Retry-After Header wird gesendet

---

## 🧪 Test-Account Status (2026-03-17)

**Campaign:** `cam_NuAHaczWN4tAkXbtD` (TEST-Campaign-Variables)
**Status:** draft (sicher, nichts wird versendet)
**Leads:** 5 Test-Leads mit Variablen

Alle Tests erfolgreich durchgeführt.

---

## 📝 Skill-Update Notwendig

Der Skill muss korrigiert werden:

1. ❌ Entfernen: `/leads/{id}/variables` Endpunkte
2. ✅ Hinzufügen: Campaign-Kontext für alle Lead-Ops
3. ✅ Dokumentieren: Variablen nur via Campaign-Lead PATCH
4. ✅ Beispiele: Korrekte Workflows zeigen

---

*Dokumentation erstellt nach vollständigem Durchlauf mit 5 Leads*
