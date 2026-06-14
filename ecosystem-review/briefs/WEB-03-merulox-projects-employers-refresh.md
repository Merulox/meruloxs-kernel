# WEB-03 — Refresh merulox.com /projects + /employers (preview on dev.merulox.com)

**Loop:** Neither A nor B — **PO exception (career/credibility surface), PO-directed 2026-06-14.** Log in DECISIONS if formalized.
**Priority:** P2 · **Safety:** `[DEPLOY]` (publishes to a preview host; production promote is PO-gated)
**Status:** briefed

## GOAL
Bring the public **/projects** page and the **/employers** section up to date with what's actually shipped, then publish to **dev.merulox.com** for PO review before any production deploy.

## WHY — the current content is factually wrong
`src/pages/employers/projects.astro` holds a hardcoded `projects` array that is stale:
- **SYNTRA** is described as "AI-assisted product discovery pipeline." That's the dead concept. SYNTRA is now a **curated everyday-carry (EDC) retailer** — storefront live at **syntraworks.ca**, ~1750 products across Bellroy / Orbitkey / Secrid / Peak Design, affiliate model, React SPA + SSG, Supabase, Railway + Cloudflare. Must be rewritten.
- **Boréal Numérique** is marked `state: "paused"` — it's **active/resumed** (live Twilio SMS pipeline: send gateway with STOP/cooldown/dedup, CRM of 618 leads, classifier + hot-lead routing, canonical follow-up engine). Tags say `n8n` — the real stack is Python + systemd + Twilio + Claude API. Update state, description, impact, tags.
- **Personal AI Infrastructure** — broadly correct; add the **agent-infra methodology** (architect/executor/reviewer) and the **Aperture** ops dashboard.
- **MERULOX** — accurate; leave or lightly refresh.
- **Public `/projects`** (`src/pages/projects/`) is an **empty directory** — the public route has no page (the only roster is the `noindex`, employer-gated one).

## FILES IT OWNS
- `src/pages/employers/projects.astro` — rewrite the `projects` array to current truth (above). Keep the existing component/markup/styles; only update data + any copy that's now false.
- `src/pages/employers.astro` — refresh `focusAreas` / `usefulWhen` / intro copy if it misstates current work (light touch).
- `src/pages/projects/index.astro` — **create** a public (indexable) projects page: a public-safe version of the roster (no private context, no lead data, no internal URLs). Reuse the same project objects/markup where sensible; this one is NOT `noindex`.
- `src/data/` — if extracting the roster into a shared `projects.ts` data module is cleaner than duplicating between the employer + public pages, do that and import from both (preferred — single source).

## DO NOT TOUCH
- Feed/proxy functions (`functions/`), KV bindings, `wrangler.toml` · the log/tweets/reading pipelines · unrelated pages · production deploy (PO promotes).

## SPEC / CONTENT NOTES
- Keep claims **truthful and verifiable**: SYNTRA → link `syntraworks.ca` (live). Boréal → "case study available on request" (no client names, no lead data, no phone numbers — this is public). Don't invent metrics; "1000+ SMS sent" is fine if kept.
- Public `/projects` must be safe to index: no `noindex`, no private infra hostnames, no secrets.
- Match the existing visual style and keyboard-nav conventions (see `DESIGN.md`).

## DONE LOOKS LIKE
1. `npm run build` clean.
2. `/employers/projects` roster reflects current truth (SYNTRA = retailer, Boréal = active, correct tags).
3. Public `/projects` page exists, builds, is indexable, and contains no private data.
4. Deployed to **dev.merulox.com** (preview), URL reported for PO review. **Production NOT promoted** (PO does that after approving the preview).

## VERIFY WITH (paste raw output)
```bash
cd ~/website && npm run build 2>&1 | tail -3
grep -A2 '"SYNTRA"\|name: "SYNTRA"' src/pages/employers/projects.astro   # description = retailer, not "discovery"
grep -n 'paused' src/pages/employers/projects.astro                       # Boréal no longer paused
ls src/pages/projects/                                                     # index.astro now exists
# preview deploy (Cloudflare Pages) — report the dev URL:
npx wrangler pages deploy dist --branch=dev 2>&1 | tail -5
# confirm no private data on the public page:
grep -riE "819[0-9]{7}|crm\.db|\.secrets|boreal-leads" src/pages/projects/ && echo "LEAK" || echo "clean"
```

## OUT OF SCOPE
- Production deploy to merulox.com (PO promotes the preview) · redesign · new sections beyond projects/employers · the case study document itself (separate task) · SEO beyond making `/projects` indexable.

## OPEN QUESTION FOR PO
Final wording/voice on the public `/projects` page is yours to approve on dev.merulox.com — the brief fixes the factual staleness and sets up the preview; ping changes after you see it live.
