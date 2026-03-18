# Lemlist API - Paginierung

> Stand: 2026-03-18 - Getestet mit 471+ Leads

---

## 🎯 Wichtigste Erkenntnis

Die Lemlist API verwendet **keine klassische Offset-Paginierung**. Stattdessen funktioniert ein **Limit-basierter Ansatz**.

---

## ✅ Korrekte Paginierung

### Campaign Leads

```bash
# Standard (gibt nur 100 zurück!)
GET /campaigns/{id}/leads

# Mit Limit - funktioniert bis mindestens 1000
GET /campaigns/{id}/leads?limit=1000
```

**Getestete Limits:**

| Limit | Ergebnis | Status |
|-------|----------|--------|
| Kein Limit | 100 Leads | ⚠️ Standard-Begrenzung |
| ?limit=200 | 200 Leads | ✅ Funktioniert |
| ?limit=500 | 471 Leads | ✅ Alle Leads |
| ?limit=1000 | 471 Leads | ✅ Sicherer Puffer |

---

## ⚠️ Bekannte Einschränkungen

### Kein Offset-Parameter

```bash
# ❌ FUNKTIONIERT NICHT
GET /campaigns/{id}/leads?limit=100&offset=100

# ✅ RICHTIG - Einfach höheres Limit
GET /campaigns/{id}/leads?limit=1000
```

### Response-Größe

Bei sehr großen Kampagnen (1000+ Leads):
- Verwende `limit=1000` oder höher
- Die API scheint keine harte Obergrenze zu haben
- Praktisches Maximum: 1000-5000 je nach Datenmenge

---

## 📋 Best Practice

### Vollständige Lead-Liste abrufen

```bash
#!/bin/bash
CAMPAIGN_ID="cam_xxx"
API_KEY="$LEMLIST_API_KEY"

# Alle Leads in einem Call (bis 1000)
curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/leads?limit=1000" \
  --user ":$API_KEY" | jq '.'

# Für sehr große Kampagnen (>1000 Leads):
# Prüfe zuerst die Gesamtanzahl via Campaign Stats
```

### Anzahl prüfen

```bash
# Zähle Leads
 curl -s "https://api.lemlist.com/api/campaigns/$CAMPAIGN_ID/leads?limit=1000" \
   --user ":$API_KEY" | jq 'length'
```

---

## 🔍 Getestete Endpunkte

| Endpunkt | Paginierung | Getestet |
|----------|-------------|----------|
| `/campaigns/{id}/leads` | `?limit=1000` | ✅ 2026-03-18 |
| `/activities` | `?limit=200` | ✅ |
| `/inbox` | `?limit=50` | ✅ |

---

## 📝 Hinweis

Die API gibt **keine Paginierungs-Metadaten** zurück (kein `total`, `hasMore`, etc.).
Zähle die Ergebnisse client-seitig oder verwende ein großzügiges Limit.

---

*Dokumentation basierend auf realen Tests mit 471 Leads*
