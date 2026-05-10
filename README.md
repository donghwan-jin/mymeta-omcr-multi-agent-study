# oh-my-claudecode-research

A small Claude Code plugin that ships a 5-agent **research team** — supervisor, analysis-implementer, paper-writer, figure-descriptor, reviewer — plus three lightweight hooks (PII scrub, MEMORY auto-load, citation warn) and a worked neuro-fMRI example preset.

This is the **research companion** to upstream [`oh-my-claudecode`](https://github.com/Yeachan-Heo/oh-my-claudecode), not a fork. It complements OMC (which provides a general orchestration system) with research-specific agent personas and conventions for projects that produce papers.

> **Status: v0.1.** Breaking changes are likely. Feedback and PRs welcome.

## The 5 agents

| Agent | Role |
|---|---|
| `@supervisor` | PI-level scientific vision keeper + project orchestrator. Owns the central hypothesis and the narrative spine; delegates to the four subagents. |
| `@analysis-implementer` | Implements pipelines, statistical analyses, ML/sim models. Field-neutral by default; overlay `examples/neuro-fmri/` for a neuro-flavored body. |
| `@paper-writer` | Drafts manuscript sections (abstract / intro / methods / results / discussion / cover / rebuttal) at high-impact-venue prose quality. |
| `@figure-descriptor` | Designs figures as implementation-ready briefs (panel layouts, color palette, captions) for any vector tool — no image generation. |
| `@reviewer` | Adversarial pre-submission peer review at the level of the project's target venue. |

## Install

Three paths, depending on how much harness you want:

**1. As a Claude Code plugin** (recommended — pulls in agents + hooks + manifest):

```bash
git clone https://github.com/<YOUR_HANDLE>/oh-my-claudecode-research ~/.claude/plugins/oh-my-claudecode-research
```

Then in any project, open Claude Code and run `/plugin` to load it. Once loaded, the 5 agents appear in the `@`-mention picker, and the 3 hooks register on session start.

**2. As a standalone clone** (use individual files without the plugin loader):

```bash
git clone https://github.com/<YOUR_HANDLE>/oh-my-claudecode-research /path/to/checkout
```

Then in your research project's `.claude/`, copy the agent files you want:

```bash
cp /path/to/checkout/agents/*.md /path/to/your-project/.claude/agents/
```

**3. Cherry-pick by file** — the agents are plain markdown, no runtime dependencies. Open any `agents/*.md` in this repo and drop the contents into your project as a project-level subagent.

## Quick start

After installing, open a research project and:

```
@supervisor where are we?
```

The supervisor will read the project's `CLAUDE.md` for the central hypothesis and project state, then orient you. If `CLAUDE.md` is empty or missing key fields (target venue, field, hypothesis), it will ask before assuming.

For a fully-fleshed worked example of how this looks in practice, see [`examples/neuro-fmri/`](examples/neuro-fmri/).

## Specializing for your field

The 5 core agents are field-neutral. For domain-specific flavor, overlay a preset:

```bash
# Currently shipped: neuro-fMRI specialization (Mapper-on-fMRI / TDA / nilearn / Schaefer parcellations)
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md
cp -r examples/neuro-fmri/skills/cropfig skills/
cp examples/neuro-fmri/commands/*.md commands/
```

See [examples/neuro-fmri/README.md](examples/neuro-fmri/README.md) for the full overlay recipe and a 4-step guide to authoring your own preset (wet-lab biology, ML research, astronomy, HCI, etc.). PRs adding new presets welcome.

## Memory pattern

Each agent maintains a persistent memory at `.claude/agent-memory/<agent-name>/MEMORY.md` in your project root. The `memory-load.sh` hook concatenates all of them and injects them at session start so every conversation begins with the agent's prior state.

Use [`templates/MEMORY.template.md`](templates/MEMORY.template.md) as a starting schema. The neuro preset ships redacted skeletons under [`examples/neuro-fmri/memory-templates/`](examples/neuro-fmri/memory-templates/) showing the structure each agent typically tracks.

## Harness — the 3 hooks

Shipped with the plugin (registered via `hooks/hooks.json`):

| Hook | Event | Behavior |
|---|---|---|
| [`hooks/pii-scrub.sh`](hooks/pii-scrub.sh) | `PreToolUse:Write\|Edit` | Blocks writes whose content matches a configurable PII pattern list (defaults: emails, SSNs, 6-digit subject IDs). Override per-project at `.claude/scrub-patterns.txt`. |
| [`hooks/memory-load.sh`](hooks/memory-load.sh) | `SessionStart` | Auto-loads all `.claude/agent-memory/*/MEMORY.md` files into session context. |
| [`hooks/citation-warn.sh`](hooks/citation-warn.sh) | `PostToolUse:Write\|Edit` | Heuristic non-blocking warning when manuscript markdown (`paper/`, `manuscript/`, `*draft*.md`) has paragraphs missing any citation form. |

Each hook honors a `CLAUDE_RESEARCH_DISABLE_<NAME>=1` env var for per-project disabling. See [`hooks/README.md`](hooks/README.md) for the full configuration guide.

## OMC companion installs (recommended)

This plugin treats upstream `oh-my-claudecode` as a *companion*, not a dependency. After installing OMC alongside, the following components fit naturally into a research workflow:

| Component | Path in OMC | Why for research |
|---|---|---|
| `scientist` agent | `oh-my-claudecode/agents/scientist.md` | Statistical-rigor data analyst — confidence intervals, p-values, effect sizes, `[LIMITATION]` markers, structured reports. Companion to our `analysis-implementer`. |
| `document-specialist` agent | `oh-my-claudecode/agents/document-specialist.md` | Literature/external-doc research with citation verification. Fills the literature-anchoring gap our agents don't cover. |
| `verifier` agent | `oh-my-claudecode/agents/verifier.md` | Evidence-based completion checks. Useful before submitting results or paper drafts. |
| `tracer` agent | `oh-my-claudecode/agents/tracer.md` | Evidence-driven causal tracing with competing hypotheses. Maps directly to research methods/results validation. |
| `autoresearch` skill | `oh-my-claudecode/skills/autoresearch/SKILL.md` | Bounded evaluator-driven iterative improvement loop with durable per-iteration JSON + decision logs. Pairs with `@supervisor`. |
| `deep-interview` skill | `oh-my-claudecode/skills/deep-interview/SKILL.md` | Socratic clarification of vague research goals into testable hypotheses. Project bootstrap. |
| `trace` skill | `oh-my-claudecode/skills/trace/SKILL.md` | Team-mode hypothesis ranking + disconfirmation orchestration. |

Install OMC alongside via the Claude Code marketplace, or `npm i -g oh-my-claude-sisyphus`. Then invoke as `/oh-my-claudecode:<skill>` or `@<agent>` from inside any project.

## Conventions (when contributing)

- **kebab-case** filenames for all agents, skills, commands.
- **YAML frontmatter** required on every agent / skill / command (`name`, `description`, optional `model` / `color` / `memory`).
- **No PII** in `agents/`, `templates/`, `hooks/`, or top-level docs — institutions, advisors, real subject IDs, emails, target journal names, absolute paths. Domain-specific content lives only under `examples/<field>/`.
- **English-first** language directive on all agents (override-in-CLAUDE.md pattern for users who want a different user-dialog language).

See [CONTRIBUTING.md](CONTRIBUTING.md) for full details.

## License

MIT — see [LICENSE](LICENSE).
