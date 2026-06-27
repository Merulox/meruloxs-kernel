# AP-24 — Call recording + call history in /boreal

**Status:** pending  
**Priority:** low  
**Depends on:** AP-22 (done)

## What's missing from the /boreal leads port

Two features from command-center LEADS tab were NOT ported:

1. **ENREGISTREMENT** — "🎙 Démarrer enregistrement" button
   - Captures mic (Blue) + system audio simultaneously via browser MediaStream API
   - Auto-transcribes after call ends via Gemini
   - Saves recording + transcript to `~/.local/share/boreal-calls/`

2. **HISTORIQUE DES APPELS** — per-lead call history panel
   - Shows past sessions with score (0–10), outcome, coaching note
   - Depends on `call_sessions` storage created by the recording flow

## Why deferred

Both features share the same infrastructure: `call-record` script + `call_sessions` storage. Without the recording pipeline, the history panel has nothing to show.

## What needs to be built

### Backend

- `~/scripts/call-record` — start/stop recording via PulseAudio/PipeWire loopback + mic
  - `call-record start <phone> <name>` → returns session ID
  - `call-record stop <session-id>` → triggers Gemini transcription, saves JSON
- Call session storage (sqlite or JSONL at `~/.local/share/boreal-calls/sessions.jsonl`)
  - Fields: id, phone, name, started_at, duration, status, analysis.score, analysis.outcome, analysis.coaching_note, transcript

### Aperture API

- `GET /api/call-sessions?phone=` — return call history for a lead
- `POST /api/call-start` — spawn call-record, return session_id
- `POST /api/call-stop` — stop recording, trigger transcription

### Frontend (BorealPanel.tsx)

- Re-enable ENREGISTREMENT panel with start/stop recording UI + timer
- Add HISTORIQUE DES APPELS panel (uses `/api/call-sessions`)

## Notes

- The command-center already has full call-record + Gemini transcription infrastructure
- Before building, check if `~/scripts/call-record` already exists
- PipeWire loopback device: `pw-loopback` or PulseAudio combined sink approach
