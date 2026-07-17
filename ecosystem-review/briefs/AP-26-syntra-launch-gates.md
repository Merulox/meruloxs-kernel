# AP-26: Aperture — SYNTRA launch gates + required-inputs form

**Status:** briefed
**Depends on:** — (AP-04/AP-18 dep-gate code is the reference implementation, both done)
**Date:** 2026-07-02
**Touches:** `~/projects/aperture/src/lib/tasks.ts`, `~/projects/aperture/src/components/tasks/SyntraPanel.tsx`, new `~/projects/aperture/src/pages/api/brief-inputs.ts`, `~/projects/aperture/src/styles/global.css`

<!-- gates: depends=; inputs=; confirms= -->

---

## GOAL

A SYNTRA task whose brief declares unmet prerequisites cannot be launched from Aperture: the "Send to Codex" button is disabled with a reason, and any declared PO inputs are collected via textboxes/checkboxes in the panel — written into the brief file — before launch unlocks.

---

## WHY

Incident 2026-07-02 (D-014 in SYNTRA DECISIONS.md): the PO accidentally launched S-24 from the SYNTRA panel while S-23 was running. The brief said "OPEN INPUTS (PO — needed before executor starts)" in plain English, but `getSyntraTasks()` parses only the TASKS.md row — the panel showed a live "Send to Codex" button with no gate and no way to supply the inputs. It worked out only because the brief contained proposed placeholder values. The EX panel already has dependency gates (AP-04, multi-dep fix AP-18); the SYNTRA panel has none, and **neither** panel has input collection. Prose prerequisites that the launch surface can't see will be violated again.

---

## THE CONVENTION (machine-readable gate line in briefs)

Briefs declare gates in one HTML comment near the top (architect-authored; already retrofitted onto S-25/S-26/S-27 as live test data):

```
<!-- gates: depends=S-23,S-24; inputs=contact_email,identity_line; confirms=mailbox_created -->
```

- `depends` — comma-separated task IDs; gate clears when every ID is `done` in `~/syntra/.agent/TASKS.md`
- `inputs` — text values the PO must provide; collected via textboxes, **written into the brief** so the executor reads them with the brief (no new executor plumbing)
- `confirms` — manual out-of-band actions (e.g. "API key placed in .env"); collected via checkboxes. **Secrets are never typed into Aperture or written to a brief** — that's what `confirms` is for
- Missing comment or empty fields = no gate (all existing done briefs unaffected)

Provided values land in the brief as a section Aperture owns:

```
## PROVIDED INPUTS (via Aperture)
- contact_email: hello@syntraworks.ca
- identity_line: SYNTRA is an independent, Canadian-run gear curation site
- [x] mailbox_created
```

An input/confirm is "met" when a non-empty value / checked box for it exists in this section. Re-parsing this section (not separate state) is the source of truth — idempotent, survives restarts, visible in git diff of the brief.

---

## FILES IT OWNS

- `src/lib/tasks.ts` — `SyntraTask`: add `dependsOn: string`, `blocked: boolean`, `requiredInputs`, `requiredConfirms`, `providedInputs`, `missingGates: string[]`; parse the gates comment + PROVIDED INPUTS section from `briefContent` (already loaded via `getBriefPreview`); resolve `blocked` with a TASKS.md status map (split `depends` on comma — the AP-18 lesson, don't regress it)
- `src/components/tasks/SyntraPanel.tsx` — gate the button; render the inputs form
- `src/pages/api/brief-inputs.ts` — **new** POST endpoint that writes the PROVIDED INPUTS section
- `src/styles/global.css` — reuse `.dep-gate` / `.btn-disabled` / `.dep-label`; add form styles

## DO NOT TOUCH

- `ExPanel.tsx` / `getExTasks()` (EX gates work; porting inputs to EX is a follow-up)
- `launch-codex.ts` launch mechanics, job/PID handling, `overlayJobState`
- Any SYNTRA repo file except via the new endpoint's declared write behavior
- Brief prose sections — the endpoint may only create/replace the `## PROVIDED INPUTS (via Aperture)` section

---

## IMPLEMENTATION SPEC

### 1. Parsing (`src/lib/tasks.ts`)

```ts
const GATES_RE = /<!--\s*gates:\s*depends=([^;]*);\s*inputs=([^;]*);\s*confirms=([^>]*?)\s*-->/;
```
Split each field on comma, trim, drop empties. Parse `## PROVIDED INPUTS (via Aperture)` lines: `- key: value` and `- [x] key`. Compute:
- `blocked` = any `depends` ID whose TASKS.md status ≠ `done` (build the status map once per `getSyntraTasks()` call from the rows already being parsed)
- `missingGates` = human strings, e.g. `"requires S-23 (in_progress)"`, `"input: contact_email"`, `"confirm: mailbox_created"`

Launch is allowed only when `missingGates.length === 0`.

### 2. Panel (`src/components/tasks/SyntraPanel.tsx`) — port the ExPanel dep-gate feature-for-feature (read `ExPanel.tsx:39-55` first; it is the reference, per standing panel-consistency rule)

- `missingGates.length > 0` → disabled `.btn-disabled` button + `.dep-label` listing the gates (comma-joined)
- Declared inputs/confirms that are unmet → inline form under the prompt block: one labeled `<input type="text">` per input, one `<input type="checkbox">` per confirm, a single "Save inputs" button → POST `/api/brief-inputs` `{ briefPath, inputs: {k:v}, confirms: [k] }` → on 200, refetch tasks (existing poll/refresh path)
- Met inputs render read-only (value shown, from `providedInputs`) so the PO sees what the executor will read

### 3. Endpoint (`src/pages/api/brief-inputs.ts`)

- POST only. Resolve and validate `briefPath`: must be inside `~/syntra/docs/planning/` or `~/kernel/ecosystem-review/briefs/` after `realpath` — otherwise 403. File must exist.
- Read file; upsert the `## PROVIDED INPUTS (via Aperture)` section (replace if present, else append before EOF); merge new values over old; reject empty-string values with 400.
- Same auth as the other Aperture API routes (match whatever `launch-codex.ts` does — do not invent a new scheme).

### 4. Defense in depth

`launch-codex.ts` handler: before spawning, re-run the gate parse on the brief; if `missingGates.length > 0` → 409 `{ error, missingGates }`. The button being enabled client-side must not be the only gate (this is exactly how the incident happened).

---

## DONE LOOKS LIKE

1. `npm run build` clean; `systemctl --user restart aperture` → active
2. `/api/tasks-data` → S-25 shows `missingGates` containing `confirm: seed_copy_approved`; S-27 shows `confirm: umami_api_key_in_env`; S-26 shows `blocked: false` (S-23 done) — matching the gates comments retrofitted into those briefs
3. In the UI: gated SYNTRA tasks show a disabled button + reason; filling the form and saving unlocks the button on next poll; the brief file on disk contains the PROVIDED INPUTS section
4. `curl -X POST /api/brief-inputs` with a path outside the allowed dirs → 403
5. `curl` launch endpoint for a gated task → 409 with `missingGates`
6. `git status` in aperture clean — all changes committed

## VERIFY WITH

```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -3
systemctl --user restart aperture && systemctl --user is-active aperture
curl -s -H "Authorization: Basic bTpzdA==" http://localhost:8788/api/tasks-data | python3 -c "
import sys, json
for t in json.load(sys.stdin)['syntraTasks']:
    if t.get('missingGates'): print(t['id'], t['missingGates'])
"
# expect: S-25 [confirm: seed_copy_approved] · S-27 [confirm: umami_api_key_in_env] (S-26 absent — dep met)
curl -s -o /dev/null -w "%{http_code}\n" -X POST -H "Authorization: Basic bTpzdA==" \
  -H "Content-Type: application/json" -d '{"briefPath":"/etc/passwd","inputs":{}}' \
  http://localhost:8788/api/brief-inputs   # expect 403
cd ~/projects/aperture && git status --short
```

## OUT OF SCOPE

- Porting the inputs form to the EX/Boréal/VIC panels (follow-up once proven on SYNTRA)
- Secret entry of any kind (confirms-checkbox pattern only)
- Editing TASKS.md from Aperture, gate authoring UI (gates comments are architect-authored in briefs)
- Transitive dependency resolution (direct deps only, same as AP-04)

## HANDOFF PROMPT

```
Read ~/kernel/agents/executor.md.
Then read ~/kernel/ecosystem-review/briefs/AP-26-syntra-launch-gates.md and implement it.
Read ~/projects/aperture/src/components/tasks/ExPanel.tsx lines 35-60 BEFORE writing the gate UI — it is the reference implementation.
Report back using ~/kernel/templates/implementation-report.md. Paste raw command output.
```
