# OpenRouter — Model Routing Table

**Provider:** OpenRouter (cloud API, paid per token)
**Key:** `~/.secrets/openrouter-api-key.txt` → `$OPENROUTER_API_KEY`
**Base URL:** `https://openrouter.ai/api/v1`

---

## Model assignments

| Role | Model | When |
|------|-------|------|
| OpenCode default | `nousresearch/hermes-3-llama-3.1-70b` | All standard tasks |
| OpenCode heavy | `nousresearch/hermes-3-llama-3.1-405b` | Complex reasoning, long briefs |
| Local fallback | Ollama `hermes3:8b` | Zero-cost, 32GB RAM fits |

## Switching models in OpenCode

Inside OpenCode, use `/model` to switch mid-session.  
Config default is 70b — override to 405b only when task complexity justifies cost.

## Why 70b as default

- 32GB RAM cannot run 70b or 405b locally (would need ~40GB / ~200GB)
- OpenRouter 405b costs ~7–10× more per token than 70b
- 70b handles executor-level implementation tasks well
- 405b reserved for architect-level reasoning on complex briefs

## Local inference (Ollama)

Hermes 8b fits in 32GB RAM. Pull with:
```
ollama pull hermes3:8b
```
Then in OpenCode: switch provider to Ollama or use the model ID directly.
