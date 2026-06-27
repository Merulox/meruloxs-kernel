# AP-22 — Boréal tab in Aperture (client registry + service health)

**Status:** briefed (rerun — previous executor built wrong thing)  
**Owner:** executor  
**Depends on:** BX-01 ✓, BX-07 ✓

> ⚠ PREVIOUS RUN FAILED: executor added 418 lines to `index.astro` instead of creating a new page.
> The primary output of this job is `src/pages/boreal.astro` — a NEW FILE that did not previously exist.
> `index.astro` gets ONE change only: a single nav link added at line ~92. Nothing else in index.astro.

---

## GOAL

Add `/boreal` page to Aperture with two panels:
1. **Client registry** — list, add, and remove clients from `~/.config/boreal/clients.json`
2. **Boréal service health** — live status of the 4 Boréal-specific services

Also: patch `missed-call-bot` to use an `owner` field from the registry for the SMS fallback name (instead of splitting the business name).

---

## WHY

The `clients.json` file is the only way to register clients in the multi-tenant missed-call-bot system. Currently only editable by CLI. This tab makes client onboarding PO-operable without terminal access and surfaces Boréal service health in one place.

---

## FILES IT OWNS

| File | Change |
|------|--------|
| `src/pages/boreal.astro` | NEW — page shell |
| `src/components/boreal/BorealPanel.tsx` | NEW — React component (two panels) |
| `src/pages/api/boreal-clients.ts` | NEW — GET / POST / DELETE |
| `src/lib/boreal.ts` | NEW — client registry read/write |
| `src/pages/index.astro` | ADD nav link: `<a href="/boreal" class="nav-link">boréal</a>` next to `/tasks` |
| `~/projects/boreal/scripts/missed-call-bot` | PATCH fallback to use `owner` field |

## DO NOT TOUCH

- **`src/pages/index.astro`** — only the ONE nav link addition at line ~92. No other changes to this file.
- `crm.db` — no schema changes
- `boreal_send.py` — no send-path changes
- Any other existing Aperture page or component (`leads.astro`, `tasks.astro`, `now.astro`, existing components)
- `clients.json` read logic in missed-call-bot (only the fallback name extraction)

---

## ARCHITECTURE

### `src/lib/boreal.ts`

```typescript
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { homedir } from 'node:os';
import { join, dirname } from 'node:path';

const CLIENTS_PATH = join(homedir(), '.config/boreal/clients.json');

export interface BorealClient {
  number: string;   // "+1XXXXXXXXXX" (the map key, flattened for the list)
  name: string;     // business name, e.g. "Plomberie Tremblay"
  owner: string;    // owner first name for SMS fallback, e.g. "Marc"
  trade: string;    // e.g. "plomberie"
  city: string;     // e.g. "Trois-Rivières"
}

export async function getClients(): Promise<BorealClient[]> {
  try {
    const raw = await readFile(CLIENTS_PATH, 'utf-8');
    const registry = JSON.parse(raw) as Record<string, Omit<BorealClient, 'number'>>;
    return Object.entries(registry).map(([number, ctx]) => ({ number, ...ctx }));
  } catch {
    return [];
  }
}

export async function upsertClient(client: BorealClient): Promise<void> {
  const clients = await getClients();
  const registry: Record<string, Omit<BorealClient, 'number'>> = {};
  for (const c of clients) {
    const { number, ...rest } = c;
    registry[number] = rest;
  }
  const { number, ...rest } = client;
  registry[number] = rest;
  await mkdir(dirname(CLIENTS_PATH), { recursive: true });
  await writeFile(CLIENTS_PATH, JSON.stringify(registry, null, 2));
}

export async function deleteClient(number: string): Promise<void> {
  const clients = await getClients();
  const registry: Record<string, Omit<BorealClient, 'number'>> = {};
  for (const c of clients.filter(c => c.number !== number)) {
    const { number: n, ...rest } = c;
    registry[n] = rest;
  }
  await mkdir(dirname(CLIENTS_PATH), { recursive: true });
  await writeFile(CLIENTS_PATH, JSON.stringify(registry, null, 2));
}
```

### `src/pages/api/boreal-clients.ts`

```typescript
import type { APIRoute } from 'astro';
import { getClients, upsertClient, deleteClient } from '../../lib/boreal';

export const GET: APIRoute = async () => {
  const clients = await getClients();
  return Response.json({ clients }, { headers: { 'cache-control': 'no-store' } });
};

export const POST: APIRoute = async ({ request }) => {
  const body = await request.json();
  const { number, name, owner = '', trade = '', city = '' } = body;
  if (!number || !name) return new Response('number and name required', { status: 400 });
  // Normalize to E.164
  const digits = number.replace(/\D/g, '');
  const normalized = digits.length === 10 ? `+1${digits}` : `+${digits}`;
  await upsertClient({ number: normalized, name, owner, trade, city });
  return Response.json({ ok: true, number: normalized });
};

export const DELETE: APIRoute = async ({ request }) => {
  const { number } = await request.json();
  if (!number) return new Response('number required', { status: 400 });
  await deleteClient(number);
  return Response.json({ ok: true });
};
```

### `src/pages/boreal.astro`

Same shell pattern as `leads.astro`:

```astro
---
import '../styles/global.css';
import BorealPanel from '../components/boreal/BorealPanel';
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Boréal · Aperture</title>
</head>
<body>
  <BorealPanel client:load />
</body>
</html>
```

### `src/components/boreal/BorealPanel.tsx`

Two sections:

**Section 1 — Client registry**
- Table: number | name | owner | trade | city | [delete]
- Add client form below the table:
  - Fields: Twilio number (required), business name (required), owner first name, trade, city
  - Submit → POST /api/boreal-clients → refresh list
  - Delete button → DELETE /api/boreal-clients → refresh list
- Empty state: "No clients registered."

**Section 2 — Boréal services**
- Read from systemd via existing `/api/system-resources` or a new lightweight check
- OR: simple static list of the 4 service names with a fetch to confirm running status
- Services to show: `missed-call-bot`, `sms-webhook`, `sms-inbox`, `boreal-tunnel`
- Display: service name + green/red indicator based on `systemctl --user is-active <svc>`

For service status, use the existing `data.ts` health data if it includes service status, otherwise
do a lightweight `execFile('systemctl', ['--user', 'is-active', svc])` per service in the API.

Add a `/api/boreal-status` endpoint that returns `{ services: [{name, active: bool}] }`.

**UI conventions** — match LeadConsole:
- `font-family: monospace`, same muted/green/red color classes as the rest of Aperture
- No new CSS classes — reuse existing global styles

### `index.astro` nav change

Add after the existing `/tasks` link:
```html
<a href="/boreal" class="nav-link">boréal</a>
```

### `missed-call-bot` patch

In `generate_sms()`, the fallback line currently:
```python
name = client_name.split()[0] if client_name else "Brad"
```

Change to accept `owner` from the context:
```python
name = client_ctx.get("owner") or (client_name.split()[0] if client_name else "Brad")
```

This requires passing `client_ctx` (the raw dict) to `generate_sms()`, or passing `client_owner` as a
separate parameter (cleaner). Use a separate parameter: add `client_owner: str = ""` to the signature.

The handler already reads `client_ctx` — just extract `ctx.get("owner", "")` and pass it through.

---

## DONE LOOKS LIKE

1. `/boreal` renders in browser — two panels visible
2. "Add client" form: submit with a test number → appears in table → `clients.json` updated on disk
3. Delete button: removes the row → file updated
4. Service status panel shows green for `missed-call-bot` (it's running)
5. Nav link "boréal" appears in the topbar on the index page

## VERIFY WITH

```bash
# Build clean
cd ~/projects/aperture && pnpm build

# API endpoints
curl -s http://localhost:8788/api/boreal-clients | jq .
curl -s -X POST http://localhost:8788/api/boreal-clients \
  -H "Content-Type: application/json" \
  -d '{"number":"5141234567","name":"Test Plomberie","owner":"Marc","trade":"plomberie","city":"Montréal"}' | jq .
cat ~/.config/boreal/clients.json

# Delete
curl -s -X DELETE http://localhost:8788/api/boreal-clients \
  -H "Content-Type: application/json" \
  -d '{"number":"+15141234567"}' | jq .
cat ~/.config/boreal/clients.json  # should be empty {}
```

## OUT OF SCOPE

- Editing an existing client in-place (delete + re-add is enough for now)
- Connecting client numbers to Twilio (that's `missed-call-bot --setup`)
- CRM lead data in this tab (that's /leads)
- Follow-up engine controls (future panel)

---

## HANDOFF PROMPT (for Codex)

```
Read ~/kernel/agents/executor.md.
Then read ~/kernel/ecosystem-review/briefs/AP-22-boreal-tab.md and implement the task.
Report back using ~/kernel/templates/implementation-report.md.
Paste raw command output — do not summarize.
```
