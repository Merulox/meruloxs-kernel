# AP-21 — API Token Drain Map (command-center tab)

**Status:** briefed  
**Owner:** executor  
**Depends on:** none (BX-01 done; BX-07 review status does not block — this patches AI generation only, not the send path)

---

## GOAL

New `APIMAP` tab in command-center showing every service that calls the Anthropic API — with
on/off toggles, trigger type, model, and cost estimates. Also lists stopped "dangerous" services
and their potential drain rate so PO knows what NOT to start blindly.

---

## WHY

Credits have been drained explosively in past funding cycles when brain-*/genesis/* daemons were
running. PO currently has zero visibility into which running services call Claude or how much.
This tab makes cost legible and adds individual AI killswitches per service without stopping the
whole service.

---

## ARCHITECTURE

### 1 — Shared gate module: `~/scripts/boreal_api_gate.py`

New file. Every service that calls Anthropic imports this before touching the API.

```python
from pathlib import Path

API_FLAGS_DIR = Path.home() / ".config/boreal/api-flags"

def api_enabled(service_name: str) -> bool:
    """Return False if a .disabled flag file exists for this service."""
    API_FLAGS_DIR.mkdir(parents=True, exist_ok=True)
    return not (API_FLAGS_DIR / f"{service_name}.disabled").exists()

def set_api_flag(service_name: str, enabled: bool) -> None:
    API_FLAGS_DIR.mkdir(parents=True, exist_ok=True)
    flag = API_FLAGS_DIR / f"{service_name}.disabled"
    if enabled:
        flag.unlink(missing_ok=True)
    else:
        flag.touch()
```

### 2 — Patches to 4 live services

Each patch is a 1-3 line guard inserted before the API call. Log the skip clearly.

**missed-call-bot** (`~/projects/boreal/scripts/missed-call-bot`):
```python
# At top of generate_sms(), before building the prompt:
import sys; sys.path.insert(0, str(Path.home() / "scripts"))
from boreal_api_gate import api_enabled
if not api_enabled("missed-call-bot"):
    name = client_name.split()[0] if client_name else "Brad"
    print("  [api-gate] AI disabled — returning static fallback")
    return f"Salut, c'est {name} — j'ai vu ton appel. Je te rappelle aujourd'hui. C'est pour quel type de projet?"
```

**sms-inbox** (`~/projects/boreal/scripts/sms-inbox`):
```python
# In classify_response(), before the Haiku call (after regex fast-path):
from boreal_api_gate import api_enabled
if not api_enabled("sms-inbox"):
    print("[api-gate] sms-inbox AI disabled — returning UNCLASSIFIED")
    return "UNCLASSIFIED"
```

**sms-webhook** (`~/projects/boreal/scripts/sms-webhook`):
```python
# In draft_reply(), before the API call:
from boreal_api_gate import api_enabled
if not api_enabled("sms-webhook"):
    print("[api-gate] sms-webhook AI disabled — draft skipped")
    return "?", ""
```

**telegram-commander** (`~/scripts/telegram-commander`):
```python
# In _classify_stop_intent(), after api_key load:
from boreal_api_gate import api_enabled
if not api_enabled("telegram-commander"):
    return {"intent": "unsuitable", "reason": "api-gate: AI disabled"}
```

### 3 — command-center data function: `get_api_map()`

Add near the health/services data layer. Returns two sections: live services (with flag state)
and dangerous-if-started services (static catalog, informational only).

```python
API_FLAGS_DIR = HOME / ".config/boreal/api-flags"

# Static service catalog — update costs here if models change
_LIVE_API_SERVICES = [
    {"name": "missed-call-bot",    "trigger": "per inbound call",   "model": "sonnet-4-6",        "cost_per_event": 0.002,  "events_per_day": 10},
    {"name": "sms-inbox",          "trigger": "per ambiguous SMS",  "model": "haiku-4-5",          "cost_per_event": 0.0001, "events_per_day": 20},
    {"name": "sms-webhook",        "trigger": "per inbound SMS",    "model": "haiku-4-5",          "cost_per_event": 0.0002, "events_per_day": 20},
    {"name": "telegram-commander", "trigger": "per STOP event",     "model": "haiku-4-5",          "cost_per_event": 0.0001, "events_per_day": 2},
    {"name": "aperture-summarize", "trigger": "per active Codex job poll (~5s)",  "model": "haiku-4-5", "cost_per_event": 0.0001, "events_per_day": 5},
]

_DANGEROUS_STOPPED = [
    {"name": "reply-agent",        "description": "Lead follow-up daemon (while True loop)",       "drain_per_day": "$0.50–$5.00",  "model": "sonnet"},
    {"name": "close-agent",        "description": "Closing automation daemon",                      "drain_per_day": "$0.10–$1.00",  "model": "haiku"},
    {"name": "brain-fill",         "description": "Vault fill loop (runs continuously)",            "drain_per_day": "$10–$50",       "model": "opus"},
    {"name": "brain-loop",         "description": "Brain pipeline loop",                            "drain_per_day": "$10–$50",       "model": "opus"},
    {"name": "brain-synthesize",   "description": "Domain synthesis daemon",                        "drain_per_day": "$5–$20",        "model": "opus"},
    {"name": "brain-dialogue-auto","description": "Auto dialogue daemon",                           "drain_per_day": "$5–$20",        "model": "opus"},
    {"name": "genesis-core",       "description": "Autonomous Genesis agent",                       "drain_per_day": "$5–$50",        "model": "opus"},
    {"name": "genesis-api",        "description": "Genesis API daemon",                             "drain_per_day": "$5–$50",        "model": "opus"},
]

def get_api_map() -> dict:
    flags_dir = API_FLAGS_DIR
    services = []
    total_est = 0.0
    for svc in _LIVE_API_SERVICES:
        disabled_flag = flags_dir / f"{svc['name']}.disabled"
        enabled = not disabled_flag.exists()
        est = svc["cost_per_event"] * svc["events_per_day"]
        total_est += est if enabled else 0
        services.append({**svc, "enabled": enabled, "cost_per_day_est": round(est, 5)})
    return {
        "live": services,
        "dangerous_stopped": _DANGEROUS_STOPPED,
        "total_daily_est": round(total_est, 4),
    }
```

### 4 — API endpoints in command-center

```python
# GET /api/api-map
elif path == "/api/api-map":
    self._json_sensitive(get_api_map())

# POST /api/api-flag  body: {"service": "sms-webhook", "enabled": false}
elif path == "/api/api-flag" and method == "POST":
    body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
    svc  = body.get("service", "")
    enbl = bool(body.get("enabled", True))
    allowed = {s["name"] for s in _LIVE_API_SERVICES}
    if svc not in allowed:
        self._error(400, "unknown service")
    else:
        flag = API_FLAGS_DIR / f"{svc}.disabled"
        API_FLAGS_DIR.mkdir(parents=True, exist_ok=True)
        if enbl: flag.unlink(missing_ok=True)
        else: flag.touch()
        self._json({"service": svc, "enabled": enbl})
```

### 5 — Tab: APIMAP (4-step pattern)

**Nav button** (after HEALTH button):
```html
<button class="nav-btn" data-view="apimap" onclick="showView('apimap')" style="color:var(--yellow)">
  APIMAP ◈
</button>
```

**showView dispatch:**
```js
if (name === 'apimap') renderApiMap();
```

**Poll tick:**
```js
if (currentView === 'apimap') renderApiMap();
```

**renderApiMap() function** — two sections:

*Live services* — card per service: name, trigger, model, est cost/day, toggle button.
Toggle button: green ON / red OFF, calls `POST /api/api-flag`.

*Dangerous if started* — collapsed warning card listing stopped daemons with drain estimates.
No toggle (they're stopped — this is informational).

*Footer*: total estimated daily cost across enabled live services.

UI pattern notes:
- Toggle buttons: `<button class="btn" style="color:var(--green)">AI ON</button>` /
  `<button class="btn" style="color:var(--red)">AI OFF</button>`
- Re-fetch after toggle to reflect new state
- Dangerous section uses `border-color:var(--red)` card with collapse
- Use `.section-title` + `.card` + `.card-body` — no new CSS

---

## FILES IT OWNS

| File | Change |
|------|--------|
| `~/scripts/boreal_api_gate.py` | NEW — shared gate module |
| `~/scripts/command-center` | new tab + 2 endpoints + data function + static catalog |
| `~/projects/boreal/scripts/missed-call-bot` | patch: gate check before Sonnet call |
| `~/projects/boreal/scripts/sms-inbox` | patch: gate check before Haiku classify call |
| `~/projects/boreal/scripts/sms-webhook` | patch: gate check before Haiku draft_reply call |
| `~/scripts/telegram-commander` | patch: gate check before Haiku stop-intent call |
| `~/.config/boreal/api-flags/` | auto-created by gate module |

## DO NOT TOUCH

- `boreal_send.py` — no send behavior changes
- `crm.db` — no schema changes
- `.service` unit files — no restarts needed except `command-center`
- Any send-path logic — this touches AI generation only, not SMS delivery

---

## DONE LOOKS LIKE

1. `systemctl --user restart command-center` — server up, no crash
2. APIMAP tab renders all 4 live services + dangerous list
3. Toggle "sms-webhook" OFF → `/home/merulox/.config/boreal/api-flags/sms-webhook.disabled` created
4. Send a test SMS → check `/tmp/sms-webhook.log` → `[api-gate] sms-webhook AI disabled — draft skipped` line present
5. Toggle back ON → flag removed → API calls resume normally
6. `curl localhost:<port>/api/api-map | jq .live[].enabled` → all true after re-enable

## VERIFY WITH

```bash
# 1. Tab renders
curl -s http://localhost:<port>/api/api-map | jq '{total: .total_daily_est, services: [.live[] | {name, enabled}]}'

# 2. Toggle off
curl -s -X POST http://localhost:<port>/api/api-flag \
  -H "Content-Type: application/json" \
  -d '{"service":"sms-webhook","enabled":false}' | jq .

# 3. Flag file exists
ls ~/.config/boreal/api-flags/

# 4. Log confirms gate fired
grep "api-gate" /tmp/sms-webhook.log

# 5. Toggle back on
curl -s -X POST http://localhost:<port>/api/api-flag \
  -H "Content-Type: application/json" \
  -d '{"service":"sms-webhook","enabled":true}' | jq .
```

## OUT OF SCOPE

- Checking actual Anthropic credit balance (credit-monitor handles that)
- Starting/stopping services from this tab (HEALTH tab owns that)
- Changing which model a service uses
- Patching stopped brain-*/genesis-* services (they're stopped; gate is informational for them)

---

## HANDOFF PROMPT (for Codex)

```
Read ~/kernel/agents/executor.md.
Then read ~/kernel/ecosystem-review/briefs/AP-20-api-map.md and implement the task.
Report back using ~/kernel/templates/implementation-report.md.
Paste raw command output — do not summarize.
```
