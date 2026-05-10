---
description: Export the latest Keynote figures and gap-analyze them against paper_outline.md, producing a prioritized TODO.
argument-hint: [optional: focus on one figure, e.g. "Fig4" or "R1"]
---

> **Example command — adapt to your stack.** This is the worked neuro-fMRI specialization. It hardcodes Keynote AppleScript export, an 8-figure / 7-Result paper structure, a `paper_outline.md` schema with `### Result N -- ... [Figure M]` headings, control conditions specific to the original DoD-Agent project (Raw / Own Mapper / OTHER Mapper / RANDOM Walk), Korean output, and a `seed_42` "other subject" convention. The reusable pattern is **"deck snapshot + outline → diff → prioritized P0/P1/P2 TODO"** — adapt the export step, outline schema, control condition list, language preference, and result count to your project.

# Figure ↔ Outline Gap Analysis

Goal: compare what the Keynote figure deck currently contains against what `paper_outline.md` prescribes for each of Fig 1–8 (R1–R7), and produce a **prioritized, actionable TODO** so the user knows exactly what to fix or make next.

All scientific reasoning is in English (per CLAUDE.md §Language Protocol); the final TODO is delivered **in Korean**.

---

## Step 1 — Export the latest Keynote snapshots

Run:

```bash
bash results-G1-traversal/export_keynote.sh
```

The script is idempotent (skips if PNGs are newer than the `.key`), so running it first is safe and fast. If it exports, note how many slides were produced.

**Guard:** if the script is missing, Keynote is not installed, or AppleScript permission is denied, continue with outline-only analysis. State in the final report that figure snapshots were unavailable, and skip Step 3 PNG inspection. Do not fabricate panel contents.

## Step 2 — Load the ground-truth outline

Read `results-G1-traversal/paper_outline.md` in full. For every `### Result N` block, extract:

- The intended figure number and panel list (A/B/C/D/...).
- The "Key message" sentence at the end of the block — that is what the figure must visually communicate.
- The methods specific to that figure (Mapper params, control conditions Raw / Own Mapper / OTHER Mapper / RANDOM Walk, scene cluster k, etc.).

### Step 2.5 — Pull supervisor's unresolved CRITICAL issues

Read `.claude/agent-memory/supervisor/MEMORY.md` (and any linked "critical issues" topic file). For each unresolved issue that blocks a figure or a main-text claim (e.g., "Own Mapper vs OTHER Mapper n.s.", "RANDOM Walk null not run"), record it — these become auto-injected P0 items in Step 5, even if the figure itself looks superficially complete.

## Step 3 — Inspect each exported PNG

List `results-G1-traversal/Figures_snapshots/*.png` in filename order. Each PNG ≈ one slide, but **slide index ≠ figure number in general** — the deck can contain dividers, title slides, or supplementary slides. Determine the offset on the first run and record it in `.claude/agent-memory/figure-descriptor/MEMORY.md` so later runs don't re-discover it.

For every figure, note:

- Which panels are actually drawn.
- Whether data labels / legends / axes are legible at Nature Neuroscience standard.
- Whether 4-condition controls (Raw / Own Mapper / OTHER Mapper / RANDOM Walk) are present where the outline requires them.
- Whether the "other subject" single-example figures visibly follow `seed_42` convention (see CLAUDE.md §Conventions).
- Whether the figure's "key message" can be read off the panels without reading the caption.

### Visual-language checklist (do not skip)

The canonical palette, typography, and plot-type conventions live in `.claude/agent-memory/figure-descriptor/color-system.md`. Load that file once at the start of Step 3 and check every figure against:

- **Palette conformance** — do condition colors (Raw / Own Mapper / OTHER Mapper / RANDOM Walk) and brain-network colors match the hex codes in `color-system.md`? Flag any inline-invented color.
- **Plot-type conformance** — where the outline calls for a raincloud / half-violin, is that the plot type shown (not a bar chart or plain box plot)?
- **Typography** — axis labels ~7–8 pt, panel labels bold 10 pt, ticks ≥ 6 pt at print width.
- **Visual hierarchy** — is the figure's primary contrast (e.g., Own > Other) the most prominent element in the panel? If the eye lands on a secondary panel first, flag it.
- **Overclaim check** — per CLAUDE.md §Project Overview, R4 Own-Mapper-vs-OTHER-Mapper is not significant (p_FDR ≈ 0.063). If a Fig 5 panel or its title visually asserts subject-specific trajectories at classification level, flag as P0 overclaim.

**Budget note:** reading every PNG individually is token-heavy. If the deck has >12 slides, inspect the slides corresponding to the current `$ARGUMENTS` figure + its immediate neighbors first; defer remaining slides unless the gap analysis demands them.

## Step 4 — Run the comparison

Build a mental diff: outline-prescribed panels and contrasts **vs.** what is currently on the slide. Specifically check:

1. **Missing panels** — outline calls for panel X, slide does not show it.
2. **Wrong/placeholder content** — panel is present but shows preliminary data, wrong subject, incorrect control, or stale version.
3. **Orphan slides** — a slide exists that the outline does not describe.
4. **Cross-figure consistency** — color palette, subject-ID choices, atlas / network coloring, and Raw / Own Mapper / OTHER Mapper / RANDOM Walk labels must match across Fig 2 → 8.
5. **Replication completeness (Fig 8 / R7)** — Filmfest + in-lab panels for R4, R5, R6. Very often incomplete; flag explicitly.
6. **Key-message visibility** — if the outline says "Own Mapper ≈ 87% of Raw ceiling" (R4), does the figure actually communicate that number?
7. **Stale vs. fresh** — if `paper_outline.md` mtime is newer than `Figures_key_ver7.key` mtime, the outline has probably drifted ahead of the figures; flag which figures look stale.

## Step 5 — Produce the TODO

Deliver the result **in Korean** using the structure below. Keep figure/panel identifiers and scientific terms in English.

```
# Figure-Outline Gap Report — YYYY-MM-DD

## Figure-by-figure

### Fig 1 — Conceptual schematic
- ✅ …
- ⚠️ …
- ❌ …
- **다음 액션:** …

### Fig 2 — R1 (rest scaffold)
- ✅ …
- ⚠️ …
- ❌ …
- **다음 액션:** …

… (through Fig 8)

## Cross-cutting

- **Missing figures/panels:** …
- **Orphan slides:** …
- **Stale (outline newer than key):** …
- **Consistency issues:** …

## Prioritized TODO (this week)

Each item tagged with narrative half it serves: `[repertoire]` (R1 + R6 half), `[path]` (R3+R4+R5 half), `[both]` (cross-cutting), or `[infra]` (tooling/consistency).

1. [P0 · path] …
2. [P0 · repertoire] …
3. [P1 · both] …
4. [P2 · infra] …

## Prioritized TODO (later, before submission)

- …
```

Rules for priority:

- **P0** — blocks a main-text claim (e.g., central Own > Other contrast missing) OR is an unresolved CRITICAL issue carried from `supervisor/MEMORY.md` (Step 2.5).
- **P1** — figure exists but does not clearly convey the outline's key message.
- **P2** — cosmetic / consistency issues (palette, labels, subject matching, figure-descriptor/color-system.md violations).
- **Later** — replication / supplementary panels that are not load-bearing for the core narrative.

**Narrative-half balance check:** after ranking, look at your P0/P1 list. If all items cluster in one narrative half, the other half is under-resourced — flag this explicitly at the top of the TODO section.

## Step 6 — Persist the report (optional but default ON)

Run `mkdir -p results-G1-traversal/todofig_reports` first, then save the full English + Korean TODO to `results-G1-traversal/todofig_reports/todofig_YYYY-MM-DD.md` so the user can track gaps over time. Do **not** overwrite `TODO_master.md` — that file is human-maintained.

---

## Argument handling

If `$ARGUMENTS` is non-empty (e.g. `Fig4`, `R1`, `Figure 5`), **restrict the analysis to that single figure** and skip the cross-cutting and multi-figure sections. Produce only that figure's ✅ / ⚠️ / ❌ block and a focused TODO.

If `$ARGUMENTS` is empty, run the full sweep over Fig 1–8.
