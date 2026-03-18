# lemlist — OpenClaw Skill

Add lemlist superpowers to your OpenClaw agents. Campaigns, leads, sequences, inbox — all controllable via natural language.

```
/lemlist-agent
```

---

## What your agent can do

Once active, your agent handles the full outreach workflow:

- **Campaign management** — create, start, pause, update campaigns
- **Lead sourcing** — search 450M+ B2B contacts via Lemleads database
- **Sequences** — write and optimize multi-step email flows
- **Lead operations** — import, enrich, update variables, track status
- **Inbox** — read conversations, send replies, manage drafts
- **Analytics** — campaign stats, conversion funnels, export data

> The available tools evolve continuously. Ask your agent: *"What lemlist operations can you perform?"*

---

## Setup

### Option A — MCP (recommended)

**Claude Code:**
```bash
# OAuth (no API key needed)
claude mcp add --transport http lemlist https://app.lemlist.com/mcp

# With API key
claude mcp add --transport http lemlist https://app.lemlist.com/mcp --header "X-API-Key: YOUR_KEY"
```

**Claude Desktop** — add to `claude_desktop_config.json`:
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

**Cursor** — add to Settings/Tools & MCP:
```json
{
  "mcpServers": {
    "lemlist": {
      "url": "https://app.lemlist.com/mcp",
      "headers": { "X-API-Key": "YOUR_KEY" }
    }
  }
}
```

### Option B — Direct API (OpenClaw skill)

```bash
export LEMLIST_API_KEY="lem_live_xxxxxxxx"
```

Get your key: Settings → Integrations → API in lemlist.

---

## lemlist-agent command

Save this as `.claude/commands/lemlist-agent.md` to get a specialized outreach agent:

```bash
/lemlist-agent
```

The agent runs systematic workflows — campaign audits, lead sourcing, sequence writing — and follows safe defaults (warns before credit usage, previews before editing live campaigns).

Full prompt template in [SKILL.md → lemlist-agent](SKILL.md#lemlist-agent-claude-code-command).

---

## Agent-critical knowledge

A few things every agent working with lemlist needs to know:

**Lead variables only work via campaign context:**
```bash
# ❌ broken
PATCH /leads/{id}/variables

# ✅ works
PATCH /campaigns/{campaignId}/leads/{leadId}
# body: { "variables": { "key": "value" } }
```

**Campaign deletion is unsupported:**
```bash
# ❌ returns 405
DELETE /campaigns/{id}

# ✅ use instead
PATCH /campaigns/{id}  # body: { "archived": true }
```

**Conditional branches on lead variables** (undocumented, discovered 2026-03-17):
```json
{
  "type": "conditional",
  "conditionKey": "customLeadInfo",
  "selector": "{\"variables.field\":{\"$exists\":true,\"$ne\":\"\"}}"
}
```

Full reference: [SKILL.md](SKILL.md) · [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## Performance

Results from automated agent test run (2026-03-17):

| Metric | Result |
|--------|--------|
| Total workflow (13 steps) | ~5–7 seconds |
| Success rate | 100% |
| Retries needed | 0 |

---

## Validation

Every endpoint verified by autonomous agents — no human guidance, no cherry-picked examples.

- ✅ 10+ agent test runs
- ✅ 130+ endpoints tested
- ✅ Known failures documented with working alternatives

---

## Contributing

Found something broken or undocumented? Open a PR.

1. Reproduce the behavior
2. Document it in the relevant `docs/` file
3. Add a test if applicable

MIT License · Not affiliated with Lemlist
