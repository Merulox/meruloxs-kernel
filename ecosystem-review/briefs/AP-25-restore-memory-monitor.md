# AP-25: Restore Process Memory Monitor

**Loop:** A (operational visibility for Boréal ops)

## EXECUTOR
codex

---

## GOAL

Restore the process memory panel to `src/pages/index.astro`. It was built, tested, and working — then lost when commit `c37069c` reverted AP-22 and the re-implementation (`cb4adc9`) never put it back.

---

## WHY

The panel was working and visible. The revert wiped it. The data layer (`src/lib/data.ts`) still fetches all memory/swap/pressure/process data — it's just not rendered. Pure restoration from git history, no design work needed.

---

## ROOT CAUSE

Commit `c37069c` (revert of `43bbb59`) removed:
1. `system` from the `getDashboardData()` destructure on line 7
2. `processTone()`, `pressureTone()`, `formatBytes()` helper functions from the frontmatter
3. The entire process memory `<section>` panel
4. The swap composition `<dialog>` and its JS

---

## FILES IT OWNS

- `src/pages/index.astro` only — all changes are here

---

## DO NOT TOUCH

- `src/lib/data.ts` — untouched, still exports `system` correctly
- `src/lib/actions.ts`
- Any other page or component
- CSS / global styles

---

## DONE LOOKS LIKE

The process memory panel renders on the Aperture index page with:
- Memory pressure meter (% + used/available bytes)
- Swap meter (% + used/free bytes)
- PSI badges: cpu, mem, mem full, io
- Flagged processes table
- Top processes table
- Swap composition dialog (opens on meter click)

---

## IMPLEMENTATION — exact steps

### Step 1: verify the source
```bash
git show 43bbb59:src/pages/index.astro | grep -n "process memory\|formatBytes\|pressureTone\|processTone" | head -20
```

### Step 2: restore the destructure (line 7 of current file)

Change:
```
const [{ health, genesis, vitals, mode, monitor, backup }, actions] = await Promise.all([
```
To:
```
const [{ health, genesis, vitals, mode, monitor, backup, system }, actions] = await Promise.all([
```

### Step 3: restore helper functions

Extract from `43bbb59` and add to the frontmatter (before the closing `---`):
```bash
git show 43bbb59:src/pages/index.astro | sed -n '41,50p'   # processTone
git show 43bbb59:src/pages/index.astro | sed -n '47,55p'   # pressureTone
git show 43bbb59:src/pages/index.astro | sed -n '62,75p'   # formatBytes
```

The current file already has `formatMoney`, `formatScore`, `ageInDays` — do NOT duplicate those. Only add the three missing ones: `processTone`, `pressureTone`, `formatBytes`.

### Step 4: restore the panel HTML

Extract from `43bbb59` (lines 184–372) and insert before the closing `</div>` of the grid:
```bash
git show 43bbb59:src/pages/index.astro | sed -n '184,372p'
```

### Step 5: restore the swap dialog and its JS

Extract from `43bbb59` (lines 375–500+) — the `<dialog data-swap-dialog>` block and its inline `<script>` tag:
```bash
git show 43bbb59:src/pages/index.astro | sed -n '375,520p'
```

Insert after the closing `</div>` of the grid (before `</main>`).

---

## VERIFY WITH

```bash
# Build must be clean
cd ~/projects/aperture && npm run build 2>&1 | tail -20

# Restart and check page loads
systemctl --user restart aperture
curl -s -o /dev/null -w "%{http_code}" -u m:st http://localhost:8788/

# Visual check: open in browser
# - process memory panel visible on index
# - memory meter shows non-zero %
# - clicking swap meter opens the dialog
```

---

## OUT OF SCOPE

- Any new features or changes to the panel design
- CSS changes
- data.ts changes
- Any other page
