# Commands — reference

OMCR ships 3 slash commands and 2 invocable skills, all parameterized via the [Project context + Research stack blocks](Configuration.md) in your project's `CLAUDE.md`.

## `/setup`

**Goal:** First-run project initialization. Interactively populate `CLAUDE.md`'s `## Project context` + `## Research stack` blocks, scaffold per-agent memory directories for all 6 agents, and (optionally) overlay a domain preset from `examples/<field>/`. Safe to re-run.

**Argument:** `$ARGUMENTS` — optional preset hint:
- `minimal` / `no-overlay` — skip the preset-overlay prompt entirely
- `neuro-fmri` — pre-select the neuro-fMRI preset (still confirms before applying)
- (empty) — ask interactively

**What it asks (interview phases):**

| Phase | Field type | Behavior on "skip" |
|---|---|---|
| Project context — scientific identity | hypothesis / venue / topic / datasets / spine | Push back **once** with the reason it matters; if user still skips, store as `[TBD: <one-line note>]`. **Never invent.** |
| Research stack — infrastructure | paths / patterns / counts / language / BibTeX file / Summary file / CrossRef email | Propose a sensible default; accept silently if user types `[skip]`. |
| Preset overlay | apply `neuro-fmri` or stay field-neutral | Skip allowed, no push-back |

**What it writes:**
1. The `## Project context`, `## Research stack`, and `## Language preference` blocks in `CLAUDE.md` — preserving any pre-existing content elsewhere in the file.
2. `.claude/agent-memory/<agent>/MEMORY.md` for all 6 agents — from the preset if selected, otherwise from `templates/MEMORY.template.md`. Existing memory files are **never overwritten**.
3. Empty `references.bib` and `references.csv` (with canonical header row) if the bibliography paths are configured. Existing files are **never overwritten**.

**Output:** A summary block listing what was created / updated / skipped, with explicit follow-up items for every `[TBD: ...]` placeholder.

[Source: `commands/setup.md`](../commands/setup.md)

### Example session

```
/setup
```

The command reads your current `CLAUDE.md` state, then asks only for missing fields:

```
Found CLAUDE.md with `## Project context` (5 fields) but no `## Research stack`.
Skipping to Research stack interview...

Deck export dir [default: figures/captured/]:
> [enter — accept default]

Outline file [default: outline.md]:
> manuscripts/outline.md

Figure count [default: 8]:
> 6

BibTeX file [default: references.bib]:
> [enter]

Summary file [default: references.csv]:
> [enter]

CrossRef email (optional, for verify-citation polite pool):
> me@example.edu

Apply a domain preset? (neuro-fmri / none) [default: none]:
> neuro-fmri

About to write the following to CLAUDE.md:
[shows diff]

Confirm? (y/n) > y

✓ Wrote ## Research stack to CLAUDE.md
✓ Scaffolded 6 agent memory files from examples/neuro-fmri/
✓ Created references.bib (empty, with comment header)
✓ Created references.csv (header row only)
✓ Setup complete — run `@supervisor where are we?` to start
```

If the user skips a scientific field:

```
Central hypothesis (one sentence):
> skip

→ "Without a hypothesis, @supervisor will ask every conversation. A rough one-sentence stake is far better than [TBD] — refine later. Want to give it a shot?"

> still skip

Saved as: [TBD: revisit after pilot]
```

### Re-running `/setup`

Safe. Existing values are surfaced as defaults; existing MEMORY.md / references.bib / references.csv are never overwritten. If you want to reset an agent's memory, delete the specific `.claude/agent-memory/<agent>/MEMORY.md` and re-run `/setup`.

## `/todofig`

**Goal:** Compare a captured figure deck against an outline document; produce a prioritized TODO of gaps (P0/P1/P2).

**Inputs (from `## Research stack` block):**
- `deck_export_dir` — captured PNG source
- `outline_file` — canonical outline (markdown)
- `figure_count` — total figures expected
- `result_pattern` — regex to find figure blocks in outline
- `report_lang` — output language
- `report_output_dir` — where to save the TODO report
- `deck_export_script` (optional) — idempotent refresh script

**Argument:** `$ARGUMENTS` — optional figure identifier to focus on (e.g., `Fig4`, `R1`, `Figure 5`). Empty = full sweep.

**Output:**
1. Per-figure ✅ / ⚠️ / ❌ block + "next action"
2. Cross-cutting concerns (missing panels / orphan slides / stale figures / consistency issues)
3. Prioritized TODO (P0 / P1 / P2 / Later)

**Saved to:** `${report_output_dir}/todofig_YYYY-MM-DD.md`

**Priorities:**
- **P0** — blocks a main-text claim, or is an unresolved CRITICAL issue from supervisor memory
- **P1** — figure exists but does not convey the outline's key message
- **P2** — cosmetic / consistency issues
- **Later** — supplementary / replication panels

[Source: `commands/todofig.md`](../commands/todofig.md)

### Example session

```
/todofig
```

Output:
```
# Figure-Outline Gap Report — 2026-05-10

## Figure-by-figure

### Fig 1 — Conceptual schematic
- ✅ Pipeline overview present
- ⚠️ Color palette differs from rest of deck
- ❌ Step 3 ("group comparison") panel missing
- **Next action:** Add Step 3 schematic; harmonize palette per color-system.md

### Fig 2 — R1 (rest scaffold)
...

## Prioritized TODO

1. [P0] Add Fig 1 Step 3 schematic — blocks the "Approach" narrative
2. [P0] R3 panel D — outline shows 4 conditions, slide has 3
3. [P1] Fig 5 caption mentions "87% of ceiling" but figure doesn't display the number
4. [P2] Harmonize Fig 1 palette
...
```

For a focused single-figure pass:

```
/todofig Fig5
```

Skips the cross-cutting section, produces only Fig 5's diff + focused TODO.

## `/sync`

**Goal:** Reconcile current state (captured deck) with final goal (outline), refresh agent memories with drifts, optionally embed cropped figures into a target document. Produces a status snapshot — **not a TODO**.

**Inputs (from `## Research stack` block):**
- All `/todofig` fields, plus:
- `sync_report_dir` — where to save status reports
- `tight_crop_dir` (optional) — for Phase 4 figure embedding
- `embed_target` (optional) — document (`.docx` / `.md`) to embed cropped figures into

**Argument:** `$ARGUMENTS` — optional scope hint:
- `memory-heavy` — deep memory reconciliation
- `outline just changed` — aggressive memory updates
- `figures only` — skip Phase 2 (memory)
- `no-embed` — skip Phase 4 (embed)
- `embed only` — run Phase 1.1 + Phase 4 only
- (empty) — default full pass

**Output (6 phases):**
1. Phase 1 — Read everything (export, outline, deck, memories)
2. Phase 2 — Reconcile memories (limited surgical edits only)
3. Phase 3 — Status snapshot (✅ / 🟡 / ⬜ / 🚧 per figure)
4. Phase 4 — Embed cropped figures into `embed_target` (optional)
5. Phase 5 — Report
6. Phase 6 — Persist report + update sync coordinator memory

**Saved to:** `${sync_report_dir}/sync_YYYY-MM-DD.md`

**Critical:** Phase 2 is **strictly limited** — no auto-rewriting of agent-authored interpretive content. Sync can only add/refresh sync markers and append drift entries.

[Source: `commands/sync.md`](../commands/sync.md)

### Authority hierarchy (sync's mental model)

| Question | Ground truth |
|---|---|
| What exists right now? | Captured PNGs in `deck_export_dir` |
| Where are we heading? | `outline_file` |
| What has been done / decided? | `.claude/agent-memory/<agent>/MEMORY.md` |

When sources disagree:
- Memory vs. PNG → trust PNG, update memory
- Memory vs. outline → update memory, flag drift
- Outline vs. PNG → flag gap (defer to `/todofig`)
- Memory references stale paths → normalize

### Example session

```
/sync
```

Output:
```
## Sync Report — 2026-05-10

### Current state
- Deck source: figures/captured/
- Latest export: 8 PNGs (refreshed)
- Per-figure summary: Fig 1 ✅, Fig 2 ✅, Fig 3 🟡, Fig 4 🚧, ...

### Goal alignment (vs. outline.md)
- ✅ Completed: Fig 1, Fig 2, Fig 6
- 🟡 In progress: Fig 3 (panel C placeholder), Fig 5 (stale)
- ⬜ Not started: Fig 8
- 🚧 Blocked: Fig 4 (waiting on R4 permutation test result)

### Embed updates (since embed_target = outline.docx)
- Refreshed: R1, R2, R3, R6
- Skipped: R4 (no PNG yet), R7 (no PNG yet)

### Agent memory updates
- supervisor: Last synced refreshed; 1 drift flagged
- analysis-implementer: no change
- paper-writer: no change
- figure-descriptor: 1 drift flagged (Fig 5 condition labels)
- reviewer: no change

### ⚠️ Manual review needed
- Fig 5 figure-descriptor memory says "Raw / Own / Other" but slide shows "Baseline / Treatment / Sham" — please reconcile.
```

## `cropfig` (skill, not a slash command)

**Goal:** Tight-crop captioned figure PNGs to figure-only content. Strips the top "Figure N. Title" label, removes trailing whitespace, adds uniform 10 px white padding.

**Invocation:** Not directly via `/`; agents and other commands invoke via the `Skill` tool with `skill="cropfig"`. Most commonly invoked by `/sync` Phase 4 to produce header-stripped PNGs for `.docx` embedding.

**Inputs:** `FIGURES_SRC`, `FIGURES_DST`, `EXPORT_SCRIPT` (env vars) or the corresponding Research-stack fields.

**Output contract:**

| Path | Owner | Top label | Bottom caption |
|---|---|---|---|
| `$FIGURES_SRC` | your export pipeline | KEPT | should be pre-stripped |
| `$FIGURES_DST` | this skill | **removed** | (pre-stripped) |

**Implementation:** Python (PIL + numpy) — see `skills/cropfig/crop_top_label.py` for the band-classification heuristic (color saturation + long-dark-run detection).

[Source: `skills/cropfig/SKILL.md`](../skills/cropfig/SKILL.md) and [`crop_top_label.py`](../skills/cropfig/crop_top_label.py)

### Direct CLI use

If you want to invoke `cropfig` outside of `/sync`:

```bash
# Defaults
python3 ~/.claude/plugins/oh-my-claudecode-research/skills/cropfig/crop_top_label.py

# Explicit paths
python3 ~/.claude/plugins/oh-my-claudecode-research/skills/cropfig/crop_top_label.py \
  path/to/captured/ \
  path/to/tight/

# Env vars
FIGURES_SRC=path/to/captured FIGURES_DST=path/to/tight \
  python3 ~/.claude/plugins/oh-my-claudecode-research/skills/cropfig/crop_top_label.py
```

Or as a Python import:

```python
from skills.cropfig.crop_top_label import main
main(src="path/to/captured", dst="path/to/tight")
```

## `verify-citation` (skill, not a slash command)

**Goal:** Verify that an academic citation exists and that its metadata matches what is claimed for it. Hits CrossRef for canonical metadata, OpenAlex for the abstract, and optionally writes the verdict into the project's literature summary table (`references.csv` by default) without clobbering human-curated columns.

**Invocation:** Used primarily by `@literature-curator` as a gate on every citation added to the bibliography. Can also be invoked directly for one-off audits.

**Inputs:** `BIB_FILE`, `SUMMARY_FILE`, `CITATION_VERIFY_EMAIL` (env vars) or the corresponding Research-stack fields.

**Modes:**

```bash
# Verify a single DOI (existence check + fetch metadata + fetch abstract)
python3 .../verify_citation.py --doi 10.1038/nature14236

# Verify one citekey from the project BibTeX
python3 .../verify_citation.py --bib references.bib --key smith2023connectome

# Full audit of the BibTeX
python3 .../verify_citation.py --bib references.bib

# Full audit AND write verified_on/verify_status into the summary table
python3 .../verify_citation.py --bib references.bib --summary-csv references.csv

# Attach a one-line claim for downstream logging (skill does NOT judge claim-fit — the agent reads the abstract and decides)
python3 .../verify_citation.py --doi 10.1038/nature14236 \
        --claim "DQN reaches human-level performance on Atari"
```

**Statuses:**

| Status | Meaning |
|---|---|
| `PASS` | DOI resolves AND title/authors/year all match (case-insensitive, normalized) |
| `MISMATCH` | Found at CrossRef but at least one metadata field disagrees with the BibTeX entry |
| `NOT_FOUND` | DOI does not resolve and title+author search returns no plausible match |
| `NOT_VERIFIED` | Network error — not treated as a pass |

**Exit codes:** `0` = all PASS; `1` = at least one MISMATCH/NOT_FOUND/NOT_VERIFIED; `2` = script error (missing file, malformed BibTeX, persistent network failure).

**Summary-table columns the skill writes:** `verified_on` (YYYY-MM-DD), `verify_status`. Plus bibliographic defaults (`authors`, `year`, `title`, `venue`, `doi`) **only when the row is blank** — never overwrites curator-curated columns (`bucket`, `our_use`, `paper_says`, `cited_sections`).

**Implementation:** Pure Python stdlib (urllib + csv + json + re) — no external dependencies.

[Source: `skills/verify-citation/SKILL.md`](../skills/verify-citation/SKILL.md) and [`verify_citation.py`](../skills/verify-citation/verify_citation.py)

## See also

- [Configuration](Configuration.md) — `## Research stack` block schema
- [Agents](Agents.md) — agents that may invoke these commands
- [Hooks](Hooks.md) — `pii-scrub` runs before any write the commands produce
