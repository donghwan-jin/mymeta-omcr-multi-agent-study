---
description: Reconcile Keynote figures (current state) with paper_outline.md (final goal), embed the latest figure PNGs into paper_outline.docx at each Result heading, and refresh agent memories. Produces a status snapshot — not a TODO (use /todofig for that).
argument-hint: [optional scope hint, e.g. "memory-heavy", "outline just changed", "no-docx-embed", "embed only"]
---

> **Example command — adapt to your stack.** This is the worked neuro-fMRI specialization. It hardcodes Keynote AppleScript export + `python-docx` embed pipeline, an 8-figure / 7-Result paper structure, a specific `paper_outline.md` ↔ `paper_outline.docx` working-copy convention, the original DoD-Agent project's narrative-spine / overclaim-check rules, and Korean reporting. The reusable pattern is **"current state + final goal + agent memories → drift report (no auto-resolve of judgment calls)"** — adapt the export, embed, and reporting steps to whatever working-copy your project uses.

# Project Sync (status + memory reconciliation)

Goal: keep the project's **agent memories** and the team's mental model aligned with the **current state** (Keynote) and the **final goal** (outline). This command does **not** produce an actionable TODO — that is what `/todofig` is for. The output is a status snapshot and a list of drifts that were (or must be) reconciled.

All reasoning is in English (per CLAUDE.md §Language Protocol); the final report is delivered **in Korean**.

---

## Authority hierarchy

| Question | Ground truth | Format Claude reads / writes |
|----------|--------------|------------------------------|
| What exists RIGHT NOW? | `results-G1-traversal/Figures_key_ver7.key` | PNGs in `results-G1-traversal/Figures_snapshots/` (via `export_keynote.sh`). The `.key` itself is read-only. |
| Where are we heading? | `results-G1-traversal/paper_outline.md` | The `.md` is the canonical reference **for prose**. `.docx` files in the same folder are the user's editable working copies — do not read their prose as ground truth; treat the `.md` as ground truth. **Exception (Phase 4):** `/sync` invokes the `cropfig` skill to produce figure-only PNGs in `Figures_tight/`, then embeds those at each Result heading in `paper_outline.docx` so the user's working copy stays visually in sync. Prose inside the `.docx` is never rewritten. |
| What has been done and decided? | Agent memories under `.claude/agent-memory/<agent>/MEMORY.md` and linked files. | Markdown. |

When sources disagree:
- Agent memory vs. Keynote-PNG → trust the PNG (current state); update the memory.
- Agent memory vs. `paper_outline.md` → update the memory; flag the drift.
- `paper_outline.md` vs. Keynote-PNG → note the gap for the user. Do not generate TODO here — defer to `/todofig`.
- An agent memory references stale `_v3` / `_v2` outline names → normalize the reference to `paper_outline.md`.

---

## Phase 1 — Read everything

### 1.1 Export the latest figures

```bash
bash results-G1-traversal/export_keynote.sh
```

Idempotent. Note how many slides were exported (or "skipped — up to date").

**Guard:** if the script is missing or returns non-zero (e.g., Keynote not installed, AppleScript permission denied, running on a headless cluster), continue with outline-only analysis and state clearly in the report that figure snapshots are unavailable. Do not fail the whole sync.

### 1.2 Read the final goal

Read `results-G1-traversal/paper_outline.md` in full. For each `### Result N` block, extract: intended figure number, panel list, key message, control conditions, methods constraints.

If `paper_outline.docx` has mtime newer than `paper_outline.md` (check with `stat -f %m`), the user has edited the docx more recently than the plaintext export. Flag this so they can regenerate the `.md` — do not attempt to read the `.docx` directly.

### 1.3 Read the current state

Read `results-G1-traversal/Figures_snapshots/*.png` (each PNG ≈ one slide) to determine which panels actually exist, which are placeholders, and which conditions are shown.

### 1.4 Read agent memories

For each agent under `.claude/agent-memory/`:
- `supervisor/MEMORY.md`
- `analysis-implementer/MEMORY.md`
- `paper-writer/MEMORY.md`
- `figure-descriptor/MEMORY.md`
- `reviewer/MEMORY.md`

Also read any linked files referenced inside each MEMORY.md. Note the last-synced date.

---

## Phase 2 — Reconcile memories

Each agent owns the structure of its own memory files (frontmatter, topic-link indexing, schemas). **`/sync` must not restructure or delete agent-authored content.** Allowed edits are strictly limited to:

1. Add or refresh the top-of-file sync marker: `**Last synced: YYYY-MM-DD**`.
2. Append a "## Drifts flagged at last sync" section (create if absent) listing factual mismatches found vs. Keynote / outline — one bullet per drift, no prose interpretation.
3. Correct factual fields that are unambiguously wrong by current ground truth (e.g., a memory says `paper_outline_v3.md` → rename to `paper_outline.md`; a memory says "k=10 scene clusters" while the outline now says "k=4" → note the drift but only change if the memory explicitly claims the outline states k=10).
4. If `paper_outline.md` mtime is newer than an agent's `Last synced:` marker, that agent's memory is potentially stale across the board — flag it, do not rewrite.

**Never do** any of the following in `/sync`:
- Add new interpretive claims, design decisions, or narrative framings.
- Invent new TODO items.
- Remove an agent's topic files or flatten its internal schema.
- Write to `.claude/agent-memory/figure-descriptor/color-system.md` or other agent-owned specification files.

Drifts that require human judgment (narrative direction changes, contradictions across documents, decisions affecting multiple agents) are **surfaced only in the report's "수동 확인 필요" section**, not auto-resolved.

---

## Phase 3 — Status snapshot

For each Result (R1–R7 / Fig 1–8), classify into exactly one status (no prescriptive next steps — this is status only):

- **✅ Completed** — outline panels match what is in the Keynote, and the key message is readable from the figure.
- **🟡 In progress** — data or code exists, but the figure is incomplete, placeholder, or shows a stale version.
- **⬜ Not started** — no data, code, or panel exists yet.
- **🚧 Blocked** — cannot proceed without a decision or a prerequisite (specify what).

For non-completed items, just name the gap in one sentence. Do **not** author multi-step plans, priorities, or delegations — those are `/todofig`'s job.

### Phase 3.5 — Narrative-spine check

A project can be 100% ✅ per-figure and still fail the narrative. Explicitly verify that each half of the paper's title is still load-bearing in the current figure deck:

- **First narrative half** — is it visibly carried by its load-bearing Result? If that Result is ⬜/🚧, this half is at risk.
- **Second narrative half** — is it visibly carried by its load-bearing Results?
- **Canonical quantitative claim** — is the headline number still representable from the current figure deck? If results have shifted, flag.
- **Overclaim check** — per the project's `CLAUDE.md` §Project Overview, identify any non-significant contrast that figures, captions, or memories have started to assert as significant. Flag as overclaim.

Surface any weakened half as a 🔴 item in the "수동 확인 필요" section with one sentence explaining which half is weakened and why.

---

## Phase 4 — Embed current figures into `paper_outline.docx`

Goal: at every `### Result N` heading in `results-G1-traversal/paper_outline.docx`, embed the **figure-only** PNG(s) (no "Figure N. Title" header, no caption — just the panels) for the Figure that Result references, replacing any previously sync-embedded image block. Keeps the user's editable working copy visually in sync with the Keynote deck. The prose inside the `.docx` is **never** touched (and the docx already carries its own figure caption text, so embedding the header-less PNG avoids duplicate "Figure 2. ..." text in the document).

### Step 4.0 — Produce figure-only PNGs via the `cropfig` skill

Invoke the **cropfig** skill (`Skill` tool with `skill="cropfig"`). It re-runs `export_keynote.sh` (idempotent), then strips the top "Figure N. Title" label and tight-bbox crops each slide, writing to `results-G1-traversal/Figures_tight/`. `Figures_snapshots/` (used elsewhere in `/sync` for slide context) is left untouched.

If cropfig fails (Keynote unavailable, headless, ImageMagick/PIL missing), skip Phase 4 entirely and flag in the report — do not fall back to embedding the captioned `Figures_snapshots/` PNGs, because that would duplicate caption text inside the docx.

### Prerequisites

- Step 4.0 must have produced PNGs in `results-G1-traversal/Figures_tight/`. If none exist (cropfig failed), skip this phase and flag in the report.
- `paper_outline.docx` must not be open in Word. Detect via `ls results-G1-traversal/~$paper_outline.docx 2>/dev/null` — if the lock file exists, skip this phase and surface "`paper_outline.docx` is open in Word — close it and rerun `/sync`" in the 수동 확인 필요 section.
- `python-docx` must be importable (`python3 -c "import docx"`). If missing, skip + flag; do not auto-install.

### Result → Figure → slide(s) mapping

Result → Figure is parsed directly from the `### Result N -- ...  [Figure M]` heading in `paper_outline.md`. The current map (as of this command's authoring) is:

| Result | Figure |
|--------|--------|
| R1 | Figure 2 |
| R2 | Figure 3 |
| R3 | Figure 4 |
| R4 | Figure 5 |
| R5 | Figure 6 |
| R6 | Figure 7 |
| R7 | Figure 8 |

Figure → slide mapping is **strictly one-to-one**: slide N = Figure N. Each Keynote export produces `Figures_snapshots/Figures_snapshots.NNN.png` (1-based slide index); the cropfig skill mirrors that filename to `Figures_tight/Figures_snapshots.NNN.png`. So Result N's embed source is `Figures_tight/Figures_snapshots.{(N+1):03d}.png` (R1 → slide 2, R2 → slide 3, …, R7 → slide 8), since slide 1 is the conceptual schematic for Figure 1.

If a slide PNG is missing for a Result, skip that one Result's embed and note it in the report.

### Implementation

Author a single-use Python script (do not commit it; run inline via `python3 -c "..."` or a temp file) using `python-docx`:

1. Load `paper_outline.docx`.
2. Iterate paragraphs. For each paragraph whose text matches `^Result\s+(\d+)\b` with heading-like styling (e.g., `Heading 3`) or begins with `### Result `, record the paragraph index and the captured `N`.
3. For each matched Result heading, in order:
   a. Scan paragraphs immediately after the heading (until the next Result / Methods / Discussion heading) and **delete** any paragraph that starts with the sentinel text `<<sync-embedded-figure:R{N}>>` **and** the paragraph immediately following it (which holds the inline picture). This removes stale embeds.
   b. Insert a new sentinel paragraph with text `<<sync-embedded-figure:R{N}>>` (style: small, italic, gray — purely a marker; OK if it renders plainly).
   c. Insert one picture from `Figures_tight/Figures_snapshots.{(N+1):03d}.png` (the figure-only PNG produced by Step 4.0; Result N → slide N+1, since slide 1 is Figure 1's conceptual schematic) at a width of 6 inches (`Inches(6)`), in its own paragraph. **Do not** use `Figures_snapshots/` for the embed — those PNGs still carry the "Figure N. Title" header which would duplicate the docx's own caption text.
4. Save back to the same path: `paper_outline.docx`.

Idempotency is enforced by the sentinel: re-running `/sync` always rewrites sync-owned blocks and never touches anything else.

### "바뀐게 있다면 바꿔주고" semantics

Because Phase 1.1 re-exports the PNGs idempotently (skip if `.key` is unchanged) and Phase 4 always replaces the sentinel-bounded block, embedded pictures are automatically up to date after every sync. Claude does not need to diff PNG bytes manually — running Phase 4 unconditionally is the simplest correct behavior.

### Failure modes (all → skip + surface in 수동 확인 필요)

- No PNGs exported (Phase 1.1 failed).
- `cropfig` skill failed (no `Figures_tight/` produced) — do **not** fall back to `Figures_snapshots/`; skip Phase 4 entirely.
- `paper_outline.docx` locked by Word.
- `python-docx` not importable.
- Script exception (e.g., docx schema surprise): report the exception message verbatim; do not attempt multiple retries or heuristic fixes.

---

## Phase 5 — Report

Deliver in Korean with this exact structure. Keep figure / panel / condition names in English.

```
## 싱크 결과 — YYYY-MM-DD

### 현재 상태 (Keynote 기준)
- Figures_key_ver7.key: [Fig 1–8 한 줄 status summary]
- 최근 export: [N slides / skipped — up to date]

### 최종 목표 대비 status (paper_outline.md 기준)
- ✅ Completed: [R/Fig list]
- 🟡 In progress: [R/Fig + 한 문장 gap]
- ⬜ Not started: [R/Fig list]
- 🚧 Blocked: [R/Fig + 무엇이 막혀있는지]

### paper_outline.docx 이미지 갱신
- 삽입/교체된 Result: [R1, R2, … 중 이번에 갱신된 것]
- 스킵 사유: [해당 시 — 예: "docx가 Word에 열려 있음", "PNG export 실패", "python-docx 미설치"]

### 에이전트 메모리 업데이트
- supervisor: [한 줄 변경 요약 or "no change"]
- analysis-implementer: …
- paper-writer: …
- figure-descriptor: …
- reviewer: …

### 내러티브 스파인 체크
- 첫 번째 narrative half: [carrying / weakened — 이유]
- 두 번째 narrative half: [carrying / weakened — 이유]
- Canonical quantitative claim: [여전히 유효 / 재검토 필요]
- 오버클레임 감지: [있다면 위치 + 내용]

### ⚠️ 수동 확인 필요
- [사용자 결정이 필요한 항목 — 내러티브 방향, 문서 간 모순, outline vs Keynote 충돌, 🔴 내러티브 약화 등]
```

---

## Phase 6 — Persist

Save the full report (English reasoning + Korean output) to:

```
results-G1-traversal/sync_reports/sync_YYYY-MM-DD.md
```

Run `mkdir -p results-G1-traversal/sync_reports` before writing. Do **not** overwrite `TODO_master.md` — that file is human-maintained.

Also update `.claude/agent-memory/sync-coordinator/MEMORY.md` (kept as the sync command's persistent memory) with:
- Sync date.
- One-line summary of what changed since the last sync.
- Current state snapshot (N completed / in progress / not started / blocked).
- Any flagged drifts the user still needs to resolve.

---

## Argument handling

If `$ARGUMENTS` is non-empty, treat it as a scope hint. Examples:
- `/sync memory-heavy` → spend extra effort on Phase 2 (deep memory reconciliation).
- `/sync outline just changed` → re-parse `paper_outline.md` carefully and aggressively update memories that reference old terminology.
- `/sync figures only` → skip Phase 2 (agent memory updates); still run Phase 4 (docx embeds) and Phase 5 (status snapshot).
- `/sync no-docx-embed` → skip Phase 4; useful when the docx is open in Word and cannot be closed right now.
- `/sync embed only` → run Phase 1.1 + Phase 4 only (refresh docx image embeds, no memories, no report).

If `$ARGUMENTS` is empty, run the default full pass (Phase 1 → Phase 6).
