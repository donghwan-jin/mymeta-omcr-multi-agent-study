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
| `Manuscript dir` | `paper/` | `## Research stack` |
| `BibTeX file` | `<Manuscript dir>/references.bib` (i.e. `paper/references.bib`) | `## Research stack` |
| `Summary file` | `references.csv` (project root — kept OUT of the manuscript dir so it doesn't get pushed to Overleaf) | `## Research stack` |
| `CrossRef email` | (none) | `## Research stack` (optional — recommend the user provide it for verify-citation polite-pool access) |
| `Overleaf git URL` | (none) | `## Research stack` (optional — only if user has Overleaf with Git Integration enabled, which requires a paid plan) |
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

## Step 4 — Scaffold manuscript directory (with optional Overleaf integration)

This step is **always run** unless the user explicitly opted out during the interview by setting `Manuscript dir` to an empty value.

### 4a — Decide the working state

Inspect the configured `Manuscript dir` (default `paper/`):

| Current state | Action |
|---|---|
| Does not exist | Will be created in 4c/4d. |
| Exists, empty | Will be populated in 4c/4d. |
| Exists, has files | **Stop. Ask the user.** Do not clobber. Offer (a) pick a different `Manuscript dir`, (b) re-run after manually clearing the directory, or (c) skip manuscript scaffolding entirely. |
| Exists, is already a git repo | Note this. Continue, but staging-branch logic in 4d must NOT clobber existing branches. |

### 4b — Journal template lookup (informs `main.tex`)

If the user filled `Target venue` during Step 1, look it up in `$CLAUDE_PLUGIN_ROOT/templates/journal-registry.json` before populating `main.tex`.

**Matching policy:**
- Case-insensitive **exact** match against the venue name OR any entry's `aliases` list. No fuzzy match — partial matches are treated as misses.
- On match, **confirm with the user before applying**:
  ```
  Target venue "<user input>" matched: <registry name>
    Publisher:               <publisher>
    LaTeX class:             <ctan_package>
    documentclass line:      <documentclass>
    Submission guidelines:   <submission_guidelines_url>
    Registry verified on:    <verified_on>  ← OMCR snapshot, may be stale; verify against the publisher guidelines above before submission.

  Apply this class to main.tex and bibstyle to the \bibliographystyle line? (y/N)
  ```
- Default is **no** (skip on empty input). The user has to explicitly say yes.

**On confirmation (y):**
- In the manuscript skeleton copy, replace the `\documentclass[11pt]{article}` line in `main.tex` with the registry's `documentclass`.
- Replace the `\bibliographystyle{plainnat}` line with `\bibliographystyle{<bibstyle>}`.
- Print: `TeX Live note — this class requires the '<ctan_package>' package. If your TeX install does not have it, run:  tlmgr install <ctan_package>` (skip this line when `ctan_package == "base"`).
- Append the venue + class info to the manuscript-dir's `README.md` (under a "Journal template" section) so subsequent contributors see what was applied.

**On no match (or user declines):**
- Print the registry's `not_in_registry_response` (the three-option fallback: keep generic article / specify a class name / paste a publisher URL).
- If the user picks (b) "specify a class name": just swap the documentclass line, no .cls file fetch. User is responsible for ensuring the class is installed.
- If the user picks (c) "paste a publisher URL": treat as advanced flow — WebFetch only if user passes an `https://` URL, show the SHA256 of the downloaded archive before extracting anything, and stop if the user does not confirm the hash. The `.cls` files extracted from the archive go into `<manuscript_dir>/`, not into the OMCR plugin repo.
- If the user picks (a) "keep generic article" (or skips): leave the skeleton as-is.

**What this step does NOT do:**
- Never bundles `.cls` files into the OMCR plugin repo.
- Never fetches anything without explicit user OK + hash display.
- Never uses fuzzy matching on the venue name — a near-miss is treated as a miss.

### 4c — Without Overleaf (no `Overleaf git URL` configured)

1. Create `Manuscript dir` if missing.
2. Copy the manuscript skeleton from `$CLAUDE_PLUGIN_ROOT/templates/manuscript-skeleton/` into it:
   ```
   <manuscript_dir>/
     main.tex                  # documentclass line possibly customized by Step 4b
     sections/{abstract,introduction,methods,results,discussion}.tex
     figures/.gitkeep
     references.bib            # empty header — managed by @literature-curator
     .gitignore                # LaTeX build artifacts
     README.md                 # conventions reference (+ "Journal template" section if 4b applied)
   ```
3. Initialize git in the manuscript dir if it isn't already a repo: `git init`.
4. Continue to 4e for the commit + ask-before-push flow.

### 4d — With Overleaf (a non-empty `Overleaf git URL` was configured)

**Before doing anything, confirm with the user:**
- Overleaf Git Integration requires a paid Overleaf plan (Personal / Pro / Group / Premium). If the user is on the free tier, this will fail. Mention this once.
- The user must have **already created an empty project on Overleaf** (we cannot create one programmatically — that requires the browser). The Git URL comes from `Overleaf menu → Sync → Git`.
- The user must generate a **Git authentication token** at `Overleaf → Account Settings → Git Integration → Generate Token`. The token grants access to ALL their Overleaf projects, so treat it as a secret.

**Token handling — non-negotiable security rules:**
- **NEVER** write the token into `CLAUDE.md`, the project repo, agent memory, or any tracked file.
- **NEVER** echo the full token back to the user in the report (mask all but the last 4 chars if you reference it).
- Recommended storage: `git credential-store` scoped to the Overleaf host only, or the user's `~/.netrc` with `git.overleaf.com` only. Ask the user which they prefer; default to git's credential helper.
- The token value lives in the user's session input — do not persist it anywhere except the credential store the user picked.

**Flow:**

1. Ask the user to paste the Overleaf Git URL. Validate it matches `https://git.overleaf.com/<24-hex-id>`.
2. Ask the user to paste their Overleaf Git authentication token (input should be treated as sensitive — do not echo full value).
3. Cache the credential for the host so `git` can authenticate non-interactively:
   ```bash
   git config --global credential.https://git.overleaf.com.helper store
   # then write a line to ~/.git-credentials:
   #   https://git:<TOKEN>@git.overleaf.com
   ```
   Or, if the user preferred `~/.netrc`:
   ```
   machine git.overleaf.com
     login git
     password <TOKEN>
   ```
4. Verify access with a lightweight call:
   ```bash
   git ls-remote "$OVERLEAF_URL" HEAD
   ```
   If this fails: stop, show the error verbatim, ask the user to re-check the URL + token (and verify their plan includes Git Integration).
5. Detect whether the Overleaf project is empty. Strategy: `git ls-remote "$OVERLEAF_URL"` returns no refs for a truly empty project; otherwise it returns the default branch. If the project is non-empty:
   - Show the user what's there (branches + last commit).
   - **Stop and ask** — do not clobber an existing Overleaf project. Offer (a) pick a different Overleaf project, (b) skip Overleaf integration, (c) manually clear the Overleaf project via the web UI and re-run.
6. Clone the (empty) Overleaf project into `Manuscript dir`:
   ```bash
   git clone "$OVERLEAF_URL" "$MANUSCRIPT_DIR"
   ```
   (For a truly empty Overleaf project the clone will report a warning that the remote is empty — this is expected.)
7. Detect the Overleaf project's default branch name. New Overleaf projects use `master`; some use `main`. Use `git remote show origin | grep "HEAD branch"` after the clone, or default to `master` if the remote was empty.
8. Copy the manuscript skeleton from `$CLAUDE_PLUGIN_ROOT/templates/manuscript-skeleton/` into `Manuscript dir` (over the empty clone). The `documentclass` line in `main.tex` reflects the Step 4b journal-template choice, if any.
9. Continue to 4e.

### 4e — Commit on the default branch, then ask before pushing

The safety harness here is **explicit user confirmation before any network push** — never auto-push, even when an Overleaf URL is configured. Local commits are always safe; pushing is irreversible from the user's perspective (collaborators see it immediately) and requires their OK.

1. In the manuscript dir, detect the default branch:
   ```bash
   default_branch=$(git remote show origin 2>/dev/null | awk '/HEAD branch/ {print $NF}')
   # if no remote (local-only, no Overleaf):
   default_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)
   ```
   If the manuscript dir was just cloned from an empty Overleaf remote, there is no checked-out branch yet — initialize one matching the remote's `HEAD` symref, or default to `master` (Overleaf's historical default) and let the first commit create it.
2. Make sure we are on the default branch:
   ```bash
   git checkout "$default_branch"
   ```
3. `git add .` everything in `Manuscript dir`.
4. Commit:
   ```bash
   git commit -m "Scaffold manuscript via oh-my-claudecode-research /setup

   - main.tex with section includes
   - sections/{abstract,introduction,methods,results,discussion}.tex stubs
   - figures/ (empty, .gitkeep)
   - references.bib (empty, managed by @literature-curator)
   - .gitignore for LaTeX artifacts
   "
   ```
5. Show the user the commit summary (`git log -1 --stat`) and **ask explicitly**:
   ```
   Manuscript scaffold committed locally on `<default_branch>`.
   <if Overleaf URL is configured>
     This would push to your Overleaf project at <masked URL>.
     Saying "yes" makes the scaffold visible in Overleaf web immediately.
     Saying "no" keeps the commit local — you can run `git push` later when ready.
   <else>
     Local-only — no remote configured. (No push to perform.)
   </if>

   Push now? (y/N)
   ```
   Default is **no** if the user just hits enter — we err on the side of not touching the network.
6. **Only if** the user answers `y` / `yes`:
   ```bash
   git push origin "$default_branch"
   ```
   On push failure (auth issue, non-fast-forward, etc.), show the error verbatim, leave the local commit in place, and tell the user how to retry (`git push origin <default_branch>` from `<manuscript_dir>/`).
7. If the user answered no (or the answer was empty), record the deferred state and remind them in the final report (Step 6) of the exact command to run when ready.

---

## Step 5 — Initialize bibliography files (literature-curator)

If a `BibTeX file` path is configured:
- If the file does not exist, create it as an empty file with a one-line header comment: `% References for <Working title>. Managed by @literature-curator. Do not hand-edit without coordinating with the agent.`
- If it exists, leave untouched.
- **If the path points inside `Manuscript dir`** (the default — `paper/references.bib`), the file was already created in Step 4 from the manuscript skeleton. Verify it has the canonical header comment; if not, add it. Otherwise leave alone.

If a `Summary file` path is configured:
- If the file does not exist, create it with **only the canonical header row**:
  ```
  citekey,authors,year,title,venue,doi,bucket,our_use,paper_says,cited_sections,verified_on,verify_status
  ```
- If it exists, leave untouched. Do NOT overwrite or migrate existing CSVs without an explicit user OK.
- The default location is the **project root** (`./references.csv`), explicitly outside `Manuscript dir`, so it does not get pushed to Overleaf. The CSV is project metadata, not part of the paper.

---

## Step 6 — Report

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

### Manuscript scaffold
- Manuscript dir: <path> (<created / existed empty / existed with content — skipped>)
- Skeleton: <main.tex + 5 sections + figures/ + references.bib + .gitignore — copied / skipped>
- Overleaf: <connected to https://git.overleaf.com/****/ / no — local only>
- Branch: `<default_branch>` (commit `<short SHA>` — `<pushed to Overleaf / local only — push deferred>`)
- Deferred push command (if applicable): `git -C <manuscript_dir> push origin <default_branch>`

### Bibliography
- references.bib (inside manuscript dir): <created / already exists>
- references.csv (project root): <created with header row / already exists>

### TBD items needing follow-up
- [list every field still marked [TBD], with the one-line note]

### Next steps
1. `@supervisor` to confirm hypothesis / venue / narrative spine framing
2. `@literature-curator` to start filling the BibTeX from your first 5–10 anchor papers
3. `@paper-writer` to draft each section under `<manuscript_dir>/sections/`
4. Preview locally: `cd <manuscript_dir> && latexmk -pdf main.tex`
5. (If push was deferred) When satisfied with the scaffold:
     `git -C <manuscript_dir> push origin <default_branch>`
6. Run `/todofig` once you have a captured figure deck to compare against the outline
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
