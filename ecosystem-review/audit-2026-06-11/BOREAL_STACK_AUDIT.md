# BORÉAL STACK AUDIT — 2026-06-12

Requested by PO before sender go/no-go: "audit all the scripts and ops related to boreal — the texting, the bots, the databases. Most of it is broken, unstructured, weak, unconvincing."

**Verdict: the PO is right.** The transport layer (webhook→tunnel→Twilio, approval gate, secrets) is solid. The data layer is corrupt-by-fallback, the state layer is split-brain, the follow-up layer is three stacked generations, and the message strategy manufactured its own opt-outs. **NO-GO on all auto-senders until BX-01 + BX-02 land.**

---

## 0. The number that changes everything

The strategy docs say "98 responses." The database says:

| Truth source | Warm count |
|---|---|
| `leads.stage = RESPONDED` | **3** |
| `leads.pipeline_stage = REPLIED` | 27 (vocab disagreement, see §2) |
| signals.md snapshot 05-15 | RESPONDED: 3, named |

"98" was raw inbound volume — including 36–39 STOPs, hostile replies, and Tinder OTP codes. The real warm pipeline is **3 named leads + A.S Électrique (live, call Fri 06-13 15:00)**. This is smaller and *more actionable*: four conversations a human can run personally. The case-study path does not need automation volume; it needs these four handled well.

## 1. What's actually good (keep, don't rebuild)

- **reply-agent's approval gate** — drafts go to Telegram with ✏️ Répondre / 📞 / 🚫 buttons before send (`reply-gate.jsonl`). This is the correct architecture; make it the *only* path to send.
- **crm_lib.py / boreal_db.py** — all DB access routes through two libs pointing at the one real DB. The foundation for consolidation exists.
- **sms-inbox classifier design** — regex pre-filters + LLM with "doubt → STOP" rule. The *design* is right; the failure mode (§3.1) is wrong.
- **Secrets** — per-credential files in `~/.secrets/` (0700/0600), read at runtime. Fine.
- **Transport** — sms-webhook (8765) → boreal-tunnel → webhook.borealnumerique.ca verified 200; missed-call-bot (8766) + own tunnel; zero crash-loops since resume.

## 2. BROKEN — databases and state

| # | Finding | Evidence |
|---|---|---|
| 2.1 | **10 of 11 DB files are 0-byte decoys.** Only `~/projects/boreal-leads/crm.db` is real (617 leads, 3,452 conversations, written today). Decoys: `~/scripts/crm.db`, `~/scripts/boreal.db`, 3 in `~/.local/share/boreal-outreach/`, 5 in `~/projects/boreal-leads/`. | `stat` + `.tables` on all 11 |
| 2.2 | **Dual stage columns disagree on 149/617 leads (24%)** — `stage` (SENT/DRAFTED/STOP/IGNORED/DEAD/RESPONDED/POSTPONED) vs `pipeline_stage` (SENT/DEAD/REPLIED/STOP). Different vocabularies, no sync. | `SELECT COUNT(*) WHERE stage != pipeline_stage` → 149 |
| 2.3 | **Split-brain state:** `outreach-batch` reads `leads.md` + `crm.md` (markdown, frozen 2026-05-27) — NOT the DB. A lead who texted STOP after 05-27 still looks fresh in crm.md. | outreach-batch:47; crm.md mtime |
| 2.4 | **HTML entities stored raw** — `A.S &Eacute;lectrique Inc.` — garbles every downstream surface (Telegram showed "acute;lectrique Inc."). | leads.name |
| 2.5 | Junk in funnel: Tinder/OTP shortcode messages ingested as conversations. | reply-log 05-12 |
| 2.6 | leads schema: 17 columns bolted on over time (`fu_bucket`, `close_touch`, `booked_nudge_sent`, `postpone_note`…) — each automation era added columns, none removed. | `.schema leads` |

## 3. BROKEN — classification

| # | Finding | Evidence |
|---|---|---|
| 3.1 | **96% of classified inbound = "ENGAGED" (2,316/2,420)** because sms-inbox falls back to `"ENGAGED"` on ANY exception or unexpected LLM output (lines ~317–322). The classifier ran through the credit-depleted period → a month of inbound rubber-stamped. OTP codes = ENGAGED. **All May classification data is untrustworthy.** | classification GROUP BY; sms-inbox:317 |
| 3.2 | Today's "ENGAGED from A.S Électrique: Vendredi 3:00h pm" should have been **READY** (booking intent). Even working, the taxonomy under-routes the hottest signal. | bus event 10:04 |

## 4. WEAK/UNCONVINCING — message strategy (the PO's instinct, confirmed in data)

| # | Finding | Evidence |
|---|---|---|
| 4.1 | **Presumptive-call templates promise calls that never happen:** "Je t'appelle {d1} matin à 9h. Réponds STOP si ça marche pas." On 05-23 A.S Électrique was told "je t'appelle lundi matin" — no call ever happened (and the lead STILL came back, which says the offer is good and the execution is what's burning trust). | sms-sent-log; TEMPLATES in follow-up-sequence |
| 4.2 | **STOP used as a casual decline mechanism** — the templates invite the compliance keyword as "no thanks for this slot." This manufactures permanent opt-outs (36 STOPs) and conflates "not Friday" with "never contact me." | same templates |
| 4.3 | **Bombardment cadence:** 7 sends in 7 consecutive days to one lead (05-09→05-15), with the SAME message verbatim on 05-10/05-12/05-14 — `random.choice()` template picker has no sent-history dedup. Result on record: "pas mal harcelant pour quelqu'un qui a rien à vendre" (05-13). | sms-sent-log for +18199961171 |
| 4.4 | **Double-send bug:** two near-identical messages 36s apart (04-11) and 5s apart (05-07) — no idempotency on the send path. | reply-sent-log, sms-sent-log |
| 4.5 | **Two timers fire the same script:** follow-up-auto (08,12,16,20h) AND follow-up-sequence (08h) both run `follow-up-sequence --send` — 5 firing opportunities/day, double-fire at 08:00. | systemd units |

## 5. UNSTRUCTURED — script sprawl

| # | Finding |
|---|---|
| 5.1 | **Seven follow-up scripts from three generations:** `followup-48h/-5d/-10d` (staged chain) · `follow-up-sequence` (86KB mega-script with buckets + templates) · `followup-pregened-advance` ("PREGENED Round 3") · `genesis-followup-auto` (**"No approval needed"** — exactly the opposite of the reply-gate philosophy) · `lead-followup-check`. Nobody can say which is canonical. |
| 5.2 | **Outreach lineage:** `outreach` (36KB) → `outreach-send` → `outreach-batch` (which dynamically imports the old `outreach` module at runtime). Plus `sms-agent`, `batch-send-drafted`, `send-rescue`, `warm-lead-rescue`, `boreal-inbox` — overlapping send paths. |
| 5.3 | **No single send chokepoint.** Twilio POSTs are inlined separately in send-sms (bash), outreach-batch, sms-webhook, reply-agent… → STOP filtering is per-script (follow-up-sequence: 23 mentions; **outreach-batch: 0**), no shared quiet-hours, no shared idempotency. This is the root cause of 4.2–4.4 and a **CASL exposure**. |
| 5.4 | `DAILY_CAP = 150  # raised from 20` in outreach-batch. With the copy in §4, volume is a liability multiplier, not an asset. |
| 5.5 | Triple decision-state (rules.md / signals.md / DB): the resume didn't propagate until signals.md's own `active_rule:` field was edited — ops_state kept broadcasting "system halted" for a day. Fixed 06-12, but the duplication remains. |

## 6. Fix plan (briefs, in order — all Loop A)

| ID | Fix | Size | Gate |
|---|---|---|---|
| **BX-01** | **Single send gateway**: one `boreal-send` entrypoint every script must use — STOP check against DB (not md), Québec quiet hours, per-lead cooldown (≥72h), sent-history dedup (no verbatim repeats ever), idempotency key, unified send log. Kill inline Twilio calls everywhere else. | 1 brief | **blocks all senders** |
| **BX-02** | **Data hygiene migration**: merge `stage`+`pipeline_stage` → one column/one vocabulary; decode HTML entities; purge OTP/shortcode junk; re-run classifier over the 2,316 ENGAGED rows (backfill with fixed fallback); recount true pipeline. `[DATA]` — reviewer gate. | 1 brief | **blocks senders** |
| **BX-03** | Classifier fallback `ENGAGED` → `UNCLASSIFIED` + retry queue; add READY routing for booking intent ("vendredi 3pm" → calendar alert, not a bus line). | small | with BX-02 |
| **BX-04** | **Copy + sequence rewrite**: kill presumptive-call templates and STOP-as-decline; one canonical 5-touch sequence (value-first, spaced 48h/5d/10d, hard stop after), thread-aware (never repeat a sent message). Retire 6 of 7 follow-up scripts to `inactive/`. | 1 brief | before re-enabling follow-ups |
| **BX-05** | Retire `crm.md`/`leads.md` as state (regenerate as read-only views from DB); delete the 10 decoy .db files; point outreach-batch at the DB. | small | with BX-03 |
| BX-06 | Cap sanity: outreach DAILY_CAP back to ≤20 until copy is validated by reply quality, not volume. | 1 line | with BX-04 |

**Corrected in passing:** MO-01 brief pointed at the 0-byte `~/scripts/crm.db` — updated to the real DB path.

## 7. Go/no-go recommendation

- **NO-GO** (stay held): outreach-batch, db-reactivation, follow-up-auto, follow-up-sequence, close-agent, genesis-followup-auto — until BX-01 + BX-02 verified.
- **Already fine to run**: everything currently running (inbound + reply-gate drafts + brief/reminder timers) — the gate keeps a human on every send.
- **Today, no automation needed:** call A.S Électrique back and confirm **vendredi 15:00**. The whole stack exists to produce exactly this moment; don't let a script ruin it twice.
