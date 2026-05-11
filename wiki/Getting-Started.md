# Getting Started

A 5-minute walkthrough: install OMCR, run `/setup` to initialize a project, start a first session. Assumes you have Claude Code installed.

## 1. Install

**Option A — Claude Code marketplace flow (recommended):** in any Claude Code session, run these one at a time (do not paste both at once):

```
/plugin marketplace add https://github.com/youngeun1209/oh-my-claudecode-research
```

```
/plugin install oh-my-claudecode-research
```

**Option B — manual checkout** (no plugin manager):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research \
  ~/.claude/plugins/oh-my-claudecode-research
```

Then run `/plugin` to load it.

**Option C — cherry-pick individual files** (skips hooks and commands):

```bash
git clone https://github.com/youngeun1209/oh-my-claudecode-research /path/to/checkout
cp /path/to/checkout/agents/*.md /path/to/your-project/.claude/agents/
```

For full feature parity, use Option A.

## 2. Verify install

In a Claude Code session, type `@` and check the autocomplete picker for 6 agents:
`@supervisor`, `@analysis-implementer`, `@paper-writer`, `@figure-descriptor`, `@reviewer`, `@literature-curator`.

The slash-command picker should show `/setup`, `/todofig`, `/sync`.

If they appear, install succeeded.

## 3. Initialize your project — `/setup`

In your project's root, run:

```
/setup
```

The command interviews you for two CLAUDE.md blocks (asks **only** for missing fields if you've already filled some):

**`## Project context`** (scientific identity — never invented for you)
- Working title
- Field / sub-field
- First author / PI
- Target venue (+ optional 2–3 backups)
- Central hypothesis (one sentence)
- Research topic (the big-picture question; broader than the hypothesis)
- Datasets (what you'll use, modality, access status)
- Narrative spine: Gap / Question / Approach / Implication

**`## Research stack`** (infrastructure — `/setup` proposes defaults you can accept)
- Deck export dir, outline file, figure count, result-pattern regex
- Report language and output directories
- `BibTeX file` and `Summary file` paths for `@literature-curator`
- Optional: CrossRef email (for `verify-citation` polite-pool access)
- Optional: preset overlay (e.g. `neuro-fmri`)

### What if you don't know the answers yet?

**Infrastructure fields** — accept the proposed default by pressing enter / typing `[skip]`.

**Scientific fields** — say "skip" or "don't know yet". `/setup` pushes back **once** with the reason it matters (e.g. "without a hypothesis, `@supervisor` will ask every conversation"), then accepts `[TBD: <one-line note>]` if you still skip. **It never invents content** for hypothesis / venue / dataset / topic / spine — those are scientific decisions only you can make.

Every `[TBD: ...]` becomes a tracked follow-up item that `@supervisor` will surface in later conversations.

### What `/setup` also does

- Scaffolds `.claude/agent-memory/<agent>/MEMORY.md` for all 6 agents (from the canonical schema, or from `examples/<field>/memory-templates/<agent>/` if you selected a preset).
- Creates an empty `references.bib` and a `references.csv` with the canonical header row (so `@literature-curator` has somewhere to write).
- Preserves any existing content — never overwrites filled MEMORY.md / bib / csv files.

If you skip `/setup`, the SessionStart `setup-nudge` hook will print a one-line reminder at every session start until you initialize. Suppress with `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1`.

Safe to re-run `/setup` later — it surfaces existing values as defaults and only writes through changes you confirm.

## 4. First real session

After `/setup`, start with:

```
@supervisor where are we?
```

Supervisor reads `CLAUDE.md` plus its memory and orients you: what's known, what's the immediate next action, and which subagent to delegate to.

Then drill into a specific task:

```
@analysis-implementer implement the [your-analysis-name] pipeline
@paper-writer draft the Introduction
@figure-descriptor design Fig 2 — show [the result]
@literature-curator resolve all [CITE: ...] placeholders in the Introduction
@reviewer stress-test the Methods at our target-venue bar
```

The five "doer" subagents report back to `@supervisor`, who decides when to advance and when to loop back.

## 5. Hooks behavior

Once the plugin is loaded, four hooks run automatically:

- **`pii-scrub`** (on every Write/Edit) — blocks writes whose content matches your PII pattern list. Customize via `.claude/scrub-patterns.txt` in your project.
- **`memory-load`** (on every session start) — auto-injects each agent's `MEMORY.md` into the new session's context.
- **`setup-nudge`** (on every session start, until you've run `/setup`) — one-line non-blocking reminder if `CLAUDE.md` is missing the `## Project context` or `## Research stack` blocks.
- **`citation-warn`** (on every Write/Edit of manuscript markdown) — non-blocking warning when paragraphs lack citations.

To disable a hook for a project, set the corresponding env var (`CLAUDE_RESEARCH_DISABLE_PII_SCRUB=1`, `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1`, etc.) in `.claude/settings.json`. See [Hooks](Hooks.md) for details.

## Common pitfalls

- **No agents in the picker.** Plugin not loaded. Run `/plugin` and check it's listed; if not, verify the marketplace/clone landed correctly.
- **`/setup` keeps nudging me.** You haven't run it yet, or your CLAUDE.md is missing one of the two blocks. Run `/setup`, or set `CLAUDE_RESEARCH_DISABLE_SETUP_NUDGE=1` to silence the nudge.
- **PII scrub blocks a legitimate write.** Edit your project's `.claude/scrub-patterns.txt` to refine the regex, or set `CLAUDE_RESEARCH_DISABLE_PII_SCRUB=1` to bypass.
- **Memory not loading.** Check that `.claude/agent-memory/<agent>/MEMORY.md` files exist in your project. The `memory-load` hook is a no-op if no `agent-memory/` directory exists (deliberately safe-by-default).
- **Hooks not running.** Verify in `~/.claude/plugins/oh-my-claudecode-research/hooks/*.sh` that the scripts are executable (`chmod +x hooks/*.sh`). If they're not (Git on some systems strips exec bits), the plugin loader will silently skip.

## Next steps

- **[Configuration](Configuration.md)** — Full Research stack block reference + env vars
- **[Standalone Usage](Standalone-Usage.md)** — Concrete walkthroughs without OMC
- **[With OMC](With-OMC.md)** — Add OMC for richer features (literature wiki, python_repl, verifier, tracer)
- **[Specializing](Specializing.md)** — Author a field-specific preset
