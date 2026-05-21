# Lemlist API - Annahmen Tests & Validierung

> Stand: 2026-03-17
> Ziel: Alle Annahmen testen und dokumentieren

---

## Getestete Annahmen

### ✅ Annahme 1: Authentifizierung
**Annahme:** Basic Auth mit `:{API_KEY}` funktioniert

**Test:**
```bash
curl -s -X GET "https://api.lemlist.com/api/team" \
  -H "Authorization: Basic $(echo -n ':5543d533e282b430fd30e0040a34701b' | base64)"
```

**Ergebnis:** ✅ Funktioniert - Team-Info wird zurückgegeben

---

### ✅ Annahme 2: Rate Limit
**Annahme:** 20 Requests / 2 Sekunden

**Test:** 25 Requests in schneller Folge

**Ergebnis:** ✅ Bestätigt - Nach 20 Requests kommt 429 Error

---

### ✅ Annahme 3: Campaign-Lead Kontext
**Annahme:** Lead-Operationen funktionieren nur über Campaign-Kontext

**Test:**
- ❌ `GET /leads/{id}` → "Lead not found"
- ✅ `GET /campaigns/{id}/leads/{id}` → Funktioniert

**Ergebnis:** ✅ Bestätigt - Campaign-Kontext ist erforderlich

---

### ✅ Annahme 4: Lead-Variablen
**Annahme:** Variablen nur via Campaign-Lead PATCH

**Test:**
- ❌ `POST /leads/{id}/variables` → "Variables not found"
- ❌ `PATCH /leads/{id}/variables` → "Variables not found"
- ✅ `PATCH /campaigns/{id}/leads/{id}` mit `{"variables": {...}}` → Funktioniert

**Ergebnis:** ✅ Bestätigt - Nur Campaign-Lead PATCH funktioniert

---

### ✅ Annahme 5: Lead-ID vs Email
**Annahme:** Lead-ID ist eindeutig, Email kann doppelt sein

**Test:**
- Lead-ID pro Campaign eindeutig
- Email kann in mehreren Campaigns existieren

**Ergebnis:** ✅ Bestätigt - Immer Lead-ID verwenden

---

### ✅ Annahme 6: Campaign Status
**Annahme:** "draft" = sicher, nichts wird versendet

**Test:** Campaign erstellt mit status "draft"

**Ergebnis:** ✅ Bestätigt - Leads im Status "scanned", keine Versendung

---

### ⚠️ Annahme 7: Enrichment
**Annahme:** Enrichment funktioniert mit Email

**Test:**
```bash
POST /enrich
Body: {"email": "test@example.com"}
```

**Ergebnis:** ⚠️ Braucht spezifische Parameter (`findEmail`, `linkedinEnrichment`, etc.)

---

### ❌ Annahme 8: Sequenz API
**Annahme:** Sequenz-Endpunkte funktionieren wie dokumentiert

**Test:**
```bash
POST /campaigns/{id}/sequence
```

**Ergebnis:** ❌ Gibt HTML zurück statt JSON - API-Problem oder falsche URL

---

## Zusammenfassung

| Annahme | Status | Bemerkung |
|---------|--------|-----------|
| Basic Auth | ✅ | Funktioniert |
| Rate Limit | ✅ | 20/2s bestätigt |
| Campaign-Kontext | ✅ | Erforderlich |
| Lead-Variablen | ✅ | Nur Campaign-Lead PATCH |
| Lead-ID vs Email | ✅ | ID eindeutig |
| Draft Status | ✅ | Sicher |
| Enrichment | ⚠️ | Braucht spezifische Params |
| Sequenz API | ❌ | HTML statt JSON |

---

## Empfohlene Subagenten-Tests

1. **Auth-Test-Agent** - Alle 3 API Keys testen
2. **Rate-Limit-Agent** - Grenzwerte testen
3. **Campaign-Workflow-Agent** - Vollständiger Workflow
4. **Variables-Agent** - Alle Variablen-Operationen
5. **Error-Handling-Agent** - Fehlerszenarien

---

## Update 2026-05-04 — Endpoint-Existenz-Tests (Free-Plan-Key)

### Methodik
402-vs-HTML-catchall-Heuristik: Lemlist returnt für Pro-Plan-Endpoints `HTTP 402 + "route is available starting emailPro plan"`, für nicht-existente Pfade `HTTP 200 + HTML-Web-App` (catch-all). JSON-Response = real + accessible.

### Korrekturen am Skill nötig (jetzt eingearbeitet)

| Annahme | Test-Result | Korrektur |
|---|---|---|
| `/email-accounts` Pfad | 200 + HTML = NOT-EXISTS | Korrekt: `/user/email-accounts` (402 = Plan-blocked, real route) |
| `/lemwarm/{id}` PATCH für Settings | 405 | Korrekt: `/lemwarm/{id}/settings` (400 = needs body, real route) |
| `/lemwarm/{id}/start` mit Body-Params | parameterless | dailyEmails/replyRate/rampUp existieren NICHT |
| `/contact-lists`, `/notes`, `/opportunities` | HTML-catchall | NOT-EXISTS — Skill-Doku-Annahme war falsch |

### Neu entdeckt (verified live)

- `/campaigns/{id}/duplicate` POST — kopiert Campaign inkl. Sequence + Schedules in 1 Call (402-Plan-blocked = real route)
- `/companies` GET/POST — CRM (200 mit echten Daten)
- `/contacts` GET/POST (400 ohne Body = real)
- `/fields` GET (read-only, POST=405)
- `/tasks` GET/POST
- `/watchlist/signals` GET
- `/inbox/labels` GET/POST

### Tenant-Provisioning-Verdict (verified)

Folgende Endpoints existieren NICHT (HTML-catchall) — Tenant-Provisioning braucht Browser-Automation:
- `/teams` (Team-Create UI-only)
- `/users` (User-List UI-only)
- `/billing/cards` (Billing UI-only)
- `/domains` (Domain-Buy UI-only — Lemlist hat aber UI-Feature seit Jan 2026)
- `/team/sending/domains` (Sending-Domain UI-only)

Ausnahme: `/users/invite` POST returnt 200/`{}` für any body — **silent stub**, nicht funktional. Cross-validation via offizielle Doku bestätigt: Guest-Invite ist UI-only.

### Webhook-Validation (verified-docs)

Lemlist nutzt **KEIN HMAC**. Statt: `secret`-Field plaintext im JSON-Body. Validation = String-Compare. Secret immutable nach Create, nicht via `GET /hooks` retrieve-bar.

### Lemwarm-Settings (verified-docs)

Nur 2 Params settable via `PATCH /lemwarm/{id}/settings`:
- `warmEmailMax` (max warm-emails per day)
- `warmEmailRampup` (daily increase)

Duration hardcoded server-side. Nicht konfigurierbar.

---

*Dokumentation für Subagenten-Nachtests · Update durch Live-Tests gegen `api.lemlist.com` 2026-05-04*
