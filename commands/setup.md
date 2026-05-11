---
description: First-run project initialization — interview the user for Project context + Research stack, persist to CLAUDE.md, create agent-memory directories, and optionally apply a domain preset.
argument-hint: [optional: "minimal" | "neuro-fmri" | "no-overlay"]
---

# Project initialization

Goal: get a fresh research project from "empty directory" to "agents work" in one interactive command. Writes/updates the project's `CLAUDE.md`, scaffolds `.claude/agent-memory/<agent>/` for the 6 agents, initializes `references.bib` + `references.csv` if `literature-curator` paths are set, and optionally overlays a domain preset (e.g. `examples/neuro-fmri/`).

This command is the **front door** for new projects. Re-running it is safe — it diffs against the current state and only asks about missing/changed fields.

The argument is an optional preset hint:
- `minimal` — skip the preset-overlay prompt entirely (no `examples/<field>/` overlay)
- `neuro-fmri` — pre-select the neuro-fMRI preset overlay (still confirms before applying)
- `no-overlay` — same as `minimal`, kept as an alias
- (empty) — ask the user during the interview

---

## Step 0 — Read current state

Check the project for:
1. Does `CLAUDE.md` exist at the project root? If yes, parse it for `## Project context` and `## Research stack` blocks.
2. Does `.claude/agent-memory/` exist? Which of the 6 agents (`supervisor`, `analysis-implementer`, `paper-writer`, `figure-descriptor`, `reviewer`, `literature-curator`) have a `MEMORY.md` already?
3. Do `references.bib` and the configured summary table file already exist?
4. Is there an `examples/<field>/` preset overlay marker (e.g. note in CLAUDE.md "Preset overlay: neuro-fmri") indicating a preset is already applied?

Report this state to the user briefly before starting the interview — it sets expectations on what will be asked.

---

## Step 1 — Interview

Ask the user **only for fields that are missing**. Two policies depending on field type:

### A. Infrastructure fields — propose a default, accept "skip"

For each field below, present the default and ask "use this, or override?". If the user types `[skip]` or hits enter without input, accept the default. No push-back.

| Field | Default | Goes into |
|---|---|---|
| `Deck export dir` | `figures/captured/` | `## Research stack` |
| `Outline file` | `outline.md` | `## Research stack` |
| `Figure count` | `8` | `## Research stack` |
| `Result pattern` | `^### Result (\d+)` | `## Research stack` |
| `Report language` | `English` | `## Research stack` |
| `Report output dir` | `./todofig_reports/` | `## Research stack` |
| `Sync report dir` | `./sync_reports/` | `## Research stack` |
| `Tight-crop output dir` | `figures/tight/` | `## Research stack` (optional) |
| `Embed target` | (none) | `## Research stack` (optional) |
| `Deck export script` | (none) | `## Research stack` (optional) |
| `BibTeX file` | `references.bib` | `## Research stack` |
| `Summary file` | `references.csv` | `## Research stack` |
| `CrossRef email` | (none) | `## Research stack` (optional — recommend the user provide it for verify-citation polite-pool access) |
| `User-dialog language` | `English` | `## Language preference` (optional) |
| `Manuscript language` | `English` (do not let the user change this — keep manuscripts in English for venue compatibility) | `## Language preference` |

### B. Scientific identity fields — never invent, but push back once on `[skip]`

For each field below, ask plainly. If the user can answer, write it through. If the user says "skip" or "don't know yet", push back **exactly once** with the reason it matters, then accept `[TBD: <one-line note>]` if they still want to skip. Never invent content here.

| Field | Goes into | Push-back rationale (use when user skips) |
|---|---|---|
| `Working title` | `## Project context` | "Even a placeholder title gives `supervisor` something to anchor on — can be a rough one-liner." |
| `Field / sub-field` | `## Project context` | "Field determines which preset to suggest and how `figure-descriptor` defaults plot conventions — please name it even if narrow." |
| `First author` | `## Project context` | "Author identity is needed for the cover letter and the BibTeX self-citation later." |
| `PI / advisor` | `## Project context` | "PI name lets `supervisor` adjust framing tone and venue strategy." (Soft push-back — if the user genuinely has no PI, accept.) |
| `Target venue` | `## Project context` | "Venue determines word limits, figure budget, reviewer expectations, and `reviewer`'s severity bar. Even a top-2 short list is more useful than `[TBD]`." |
| `Backup venues (2–3)` | `## Project context` | "Helps `supervisor` keep a tier-list for framing pivots." (Skip allowed without push-back.) |
| `Central hypothesis` | `## Project context` | "Without a hypothesis, `supervisor` will ask every conversation. A rough one-sentence stake is far better than `[TBD]` — refine later." |
| `Research topic` | `## Project context` | "What's the **big-picture question**, distinct from the specific hypothesis? One or two sentences." |
| `Datasets` | `## Project context` | "Which dataset(s) are you using? Source, modality, approximate size, access status. If none decided yet, `[TBD]` is OK but flagged." |
| `Narrative spine — Gap` | `## Project context` | "What has the field NOT yet established that this study will?" |
| `Narrative spine — Question` | `## Project context` | "The specific testable question." |
| `Narrative spine — Approach` | `## Project context` | "One sentence of methodology." |
| `Narrative spine — Implication` | `## Project context` | "What this changes about how the field thinks. Often unknown early — `[TBD: filled as results emerge]` is the canonical placeholder." |

### C. Preset overlay (final step of the interview)

If the argument was `minimal` / `no-overlay`, skip this section entirely.

Otherwise, ask: "Apply a domain preset? Available presets in this plugin: `neuro-fmri`. Or `none` to stay field-neutral."

If the user selects a preset:
1. Note the preset name. The actual overlay (Step 3) copies preset agent bodies and memory templates.
2. If the argument was `neuro-fmri` and the user confirms, no need to re-ask.

---

## Step 2 — Persist to CLAUDE.md

Write the gathered fields into the project's `CLAUDE.md` using this canonical layout. If `CLAUDE.md` already exists with other content (e.g. a "Repository status" section), preserve it and **only** insert/update the `## Project context`, `## Research stack`, and `## Language preference` blocks.

```markdown
## Project context

- **Working title:** <title or [TBD]>
- **Field:** <field>
- **First author / PI:** <first author> / <PI>
- **Target venue:** <venue or [TBD: short note]>
- **Backup venues:** <comma-separated or [TBD]>
- **Central hypothesis:** <one sentence or [TBD: short note]>
- **Research topic:** <one-two sentences or [TBD]>
- **Datasets:** <name, source, modality, status — or [TBD: short note]>
- **Narrative spine:**
  1. *Gap:* <...>
  2. *Question:* <...>
  3. *Approach:* <...>
  4. *Finding:* [filled as results emerge]
  5. *Implication:* <... or [TBD]>
- **Preset overlay:** <name or none>

## Research stack (used by /todofig, /sync, /setup, and the verify-citation + cropfig skills)

- **Deck export dir:** <path>
- **Outline file:** <path>
- **Figure count:** <N>
- **Result pattern:** `<regex>`
- **Report language:** <lang>
- **Report output dir:** <path>
- **Sync report dir:** <path>
- **Tight-crop output dir:** <path or omit>
- **Embed target:** <path or omit>
- **Deck export script:** <path or omit>
- **BibTeX file:** <path>
- **Summary file:** <path>
- **CrossRef email:** <email or omit>

## Language preference

- **User-dialog language:** <lang>  (manuscripts always stay in English)
```

Show the resulting block(s) to the user before writing, and confirm. After confirmation, write `CLAUDE.md` and report the diff.

---

## Step 3 — Scaffold agent memory

Create `.claude/agent-memory/<agent>/` for each of the 6 agents and seed each with a `MEMORY.md`:

- **If the user selected a preset** with a matching `examples/<field>/memory-templates/<agent>/MEMORY.md`, copy that template.
- **Otherwise**, copy the canonical `templates/MEMORY.template.md` from this plugin.

For each agent that *already* has a MEMORY.md in the user's project, skip — do not overwrite. Report what was created vs. skipped.

Agents to scaffold:
- `supervisor`
- `analysis-implementer`
- `paper-writer`
- `figure-descriptor`
- `reviewer`
- `literature-curator`

If the user selected `neuro-fmri` and there's an agent-body overlay (currently only `analysis-implementer.md`), also offer to copy `examples/neuro-fmri/agents/analysis-implementer.md` over the project's `.claude/agents/analysis-implementer.md` (or note that this overlay lives in the plugin core when the plugin is installed by `/plugin install`, so no local copy is needed — only memory templates are project-local).

---

## Step 4 — Initialize bibliography files (literature-curator)

If a `BibTeX file` path is configured:
- If the file does not exist, create it as an empty file with a one-line header comment: `% References for <Working title>. Managed by @literature-curator. Do not hand-edit without coordinating with the agent.`
- If it exists, leave untouched.

If a `Summary file` path is configured:
- If the file does not exist, create it with **only the canonical header row**:
  ```
  citekey,authors,year,title,venue,doi,bucket,our_use,paper_says,cited_sections,verified_on,verify_status
  ```
- If it exists, leave untouched. Do NOT overwrite or migrate existing CSVs without an explicit user OK.

---

## Step 5 — Report

Produce a concise summary the user can read in 10 seconds:

```
## Setup complete — YYYY-MM-DD

### CLAUDE.md
- Project context: <created / updated / unchanged> (<N filled, M TBD>)
- Research stack: <created / updated / unchanged>
- Language preference: <created / updated / unchanged>

### Agent memory
- supervisor:           created from <preset|canonical>
- analysis-implementer: created from <...>
- paper-writer:         created from <...>
- figure-descriptor:    created from <...>
- reviewer:             created from <...>
- literature-curator:   created from <...>
(or "already exists — skipped" per agent)

### Bibliography
- references.bib: <created / already exists>
- references.csv: <created with header row / already exists>

### TBD items needing follow-up
- [list every field still marked [TBD], with the one-line note]

### Next steps
1. `@supervisor` to confirm hypothesis / venue / narrative spine framing
2. `@literature-curator` to start filling the BibTeX from your first 5–10 anchor papers
3. Run `/todofig` once you have a captured figure deck to compare against the outline
```

End by recommending the user run `@supervisor where are we?` for the first real conversation.

---

## Re-running `/setup`

Safe to re-run on an initialized project. Behavior:
- All existing CLAUDE.md fields are surfaced as defaults during the interview.
- The user can confirm-all to apply only newly-added fields (e.g. when this plugin adds a new field in a future version).
- Existing `MEMORY.md` files are never overwritten.
- Existing `references.bib` / `references.csv` are never overwritten.

If the user wants to **reset** an agent's memory, instruct them to delete the specific `.claude/agent-memory/<agent>/MEMORY.md` and re-run `/setup`. Do not provide a `--reset` flag; deletion is an explicit, reviewable action.
