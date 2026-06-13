# BX-04 — One canonical follow-up sequence + copy rewrite

**Loop:** A · **Priority:** P2 (required before any follow-up timer re-enables) · **Safety:** no sends in this brief; templates require PO sign-off before activation
**Status:** briefed · **Depends on:** BX-01 (all sends go through the gateway)
**Source:** `BOREAL_STACK_AUDIT.md` §4–§5

> **RE-SCOPED 2026-06-12 (PO strategic reorientation — do not launch as-written):** copy doctrine now governed by `~/obsidian/knowledge/projects/boreal/acquisition-machine-2026-06-12.md` §4. Touches lead with painful outcomes, never the service; no AI talk; one hand-raise CTA per message (reply keyword / call / booking link); no meeting-ask, no presumptive-call closes. Architect must rewrite the 4-touch template specs to that standard before this brief is handed off. Templates remain DRAFT until PO sign-off (unchanged).

## GOAL
Replace seven overlapping follow-up scripts and the presumptive-call template pool with ONE sequence script, ONE template file, and copy that doesn't manufacture opt-outs.

## WHY
Three stacked generations (followup-48h/-5d/-10d · the 86KB follow-up-sequence · PREGENED rounds · genesis-followup-auto "no approval needed") fire from two overlapping timers with `random.choice()` templates and no sent-history awareness. Results on record: 7 sends in 7 days to one lead, verbatim repeats, "je t'appelle lundi matin" promises nobody kept, STOP taught as a casual decline, and a harassment complaint. The lead who came back anyway (A.S Électrique) proves the offer survives the copy — barely.

## FILES IT OWNS
- `~/scripts/boreal-followup` (new — the ONE sequence engine)
- `~/projects/boreal-leads/templates/followup.yaml` (new — ALL copy lives here, nowhere else)
- Retirement moves: `follow-up-sequence`, `followup-48h`, `followup-5d`, `followup-10d`, `followup-pregened-advance`, `genesis-followup-auto`, `batch-send-drafted` → `~/scripts/inactive/` (git mv)
- systemd: new `boreal-followup.timer` unit file (created **disabled**, never enabled in this brief); `follow-up-auto.timer` + `follow-up-sequence.timer` unit files deleted

## DO NOT TOUCH
- `follow-up-brief` (the PO Telegram brief — different job, keep)
- `lead-followup-check` (read-only scanner — keep)
- reply-agent, sms-inbox, crm.db schema
- No timer may be ENABLED — activation is a PO go/no-go after template sign-off

## SPEC

### Sequence design (replaces all buckets/rounds)
Per lead, driven entirely by DB state (`last_outbound_ts`, `last_inbound_ts`, stage), max **4 touches** then hard stop → stage DEAD:
| Touch | When | Intent |
|---|---|---|
| T1 | 48h after last unanswered outbound | Light value nudge — new angle, not a repeat |
| T2 | 5d | Concrete proof point (the 28-seconds-response stat style) + soft question |
| T3 | 10d | Permission close: "veux-tu que je te recontacte plus tard, ou pas pantoute?" |
| T4 | 21d | Goodbye + door open ("si jamais ça redevient pertinent…") → DEAD after |

### Hard rules (enforced in code, not in copy discipline)
1. Every send goes through `boreal_send` (BX-01) — inherits STOP/cooldown/dedup/cap automatically.
2. **Never send a template the lead has already received** (check conversations history by template id AND by body).
3. Max 1 outbound per lead per 72h (the gateway enforces; the engine must also not queue more).
4. A lead reply at any point exits the sequence (stage REPLIED → human/reply-gate handles it).

### Copy principles (templates written to followup.yaml as DRAFTs)
- **No call promises.** Never "je t'appelle X à 9h" — the system cannot keep them. Offer slots, ask permission.
- **STOP is never the decline mechanism.** Decline phrasing: "réponds 'pas maintenant'" — STOP remains pure opt-out handled by the gateway.
- Value-first, one idea per message, ≤300 chars, joual-friendly QC French matching the existing voice ("Brad, Boréal"), question-ended.
- T3 permission ask uses softening ("Est-ce que ça se pourrait que…") per the follow-up-strategy playbook.
- Write 2 variants per touch (8 total). Mark every template `status: DRAFT`. The engine refuses to send any template not marked `status: APPROVED` — **PO flips them after review.**

## DONE LOOKS LIKE
One engine, one YAML, six scripts retired, two old timers gone, new timer present-but-disabled, `boreal-followup --dry-run` prints exactly which lead would get which touch and why, and zero sends occurred during implementation.

## VERIFY WITH (paste raw output)
```bash
ls ~/scripts/inactive/ | grep -E 'followup|follow-up-sequence|batch-send'      # 7 retired (6 + batch-send-drafted)
ls ~/.config/systemd/user/ | grep follow                                      # only boreal-followup.* + follow-up-brief.*
systemctl --user is-enabled boreal-followup.timer                              # disabled
~/scripts/boreal-followup --dry-run                                            # per-lead plan, no sends
grep -c "status: DRAFT" ~/projects/boreal-leads/templates/followup.yaml        # 8
grep -rn "api.twilio.com" ~/scripts/boreal-followup                            # nothing — gateway only
tail -3 ~/.local/share/boreal-outreach/send-gateway-log.jsonl                  # no new sends during this work
```

## OUT OF SCOPE
Cold outreach copy (outreach-batch templates — separate pass after this proves out) · enabling anything · the close-agent sequence (evaluate after BX-02 reveals the true pipeline; it may be redundant with T2/T3)
