# `examples/neuro-fmri/` — worked specialization

This is a concrete, neuro-fMRI-flavored specialization of the generic 5-agent research toolkit at the repo root. It is the same set of agents and conventions, *fleshed out for a Mapper-on-fMRI study* — kept here as a reference for what a fully-instantiated project looks like, and as a head-start for anyone working in computational neuroscience.

This preset is what the original [DoD-Agent](https://github.com/) project used internally, with the project-specific content (advisor, target journal, subject IDs, hypothesis text, dataset paths, hyperparameters) scrubbed out.

## What's in here

```
examples/neuro-fmri/
├── README.md                                   # this file
├── agents/
│   └── analysis-implementer.md                 # neuro-flavored body (nilearn / kepler-mapper / Schaefer / fMRI preprocessing / TDA)
├── commands/
│   ├── todofig.md                              # Keynote-deck ↔ paper-outline gap analyzer (P0/P1/P2 TODO)
│   └── sync.md                                 # state snapshot + memory drift reconciler with .docx figure embed
├── skills/
│   └── cropfig/                                # tight-crop captioned PNGs to figure-only PNGs (Keynote → docx workflow)
└── memory-templates/                           # redacted MEMORY.md skeletons for each of the 5 agents
    ├── supervisor/MEMORY.md
    ├── analysis-implementer/MEMORY.md
    ├── paper-writer/MEMORY.md
    ├── figure-descriptor/MEMORY.md
    └── reviewer/MEMORY.md
```

## Install (overlay on top of the core)

After installing the core plugin, overlay this preset's files on a per-asset basis:

```bash
# 1. The neuro-flavored analysis-implementer (replaces the field-neutral core version):
cp examples/neuro-fmri/agents/analysis-implementer.md agents/analysis-implementer.md

# 2. The two slash commands (these don't exist in the core):
mkdir -p commands/
cp examples/neuro-fmri/commands/*.md commands/

# 3. The cropfig skill:
mkdir -p skills/
cp -r examples/neuro-fmri/skills/cropfig skills/

# 4. The MEMORY.md skeletons — copy into your project's .claude/agent-memory/<agent>/:
for agent in supervisor analysis-implementer paper-writer figure-descriptor reviewer; do
  mkdir -p .claude/agent-memory/$agent
  cp examples/neuro-fmri/memory-templates/$agent/MEMORY.md .claude/agent-memory/$agent/MEMORY.md
done
```

## What this preset adds vs. the field-neutral core

| Surface | Core (`agents/`, etc.) | Neuro preset (`examples/neuro-fmri/`) |
|---|---|---|
| `analysis-implementer` agent body | Field-neutral; talks generically about ML / stats / simulation | Concrete neuro tooling: `nilearn`, `nibabel`, `kepler-mapper`, `brainiak`, Schaefer/Gordon parcellations, fMRI preprocessing pitfalls, MATLAB ↔ Python interop |
| Slash commands | None | `/todofig`, `/sync` for Keynote-deck-driven manuscript workflows |
| Skills | None | `cropfig` for tight-cropping captioned PNGs to figure-only |
| Memory templates | None (just `templates/MEMORY.template.md` schema) | Redacted skeletons of all 5 agents' MEMORY.md, showing what each agent typically tracks |

## Adapt to your stack

The slash commands and the cropfig skill are **example-grade** — they hardcode Keynote / AppleScript / `python-docx` / Korean / 7-Result paper structure. They're not intended to run unmodified for projects that don't share those choices.

Re-read the headers at the top of `commands/todofig.md`, `commands/sync.md`, and `skills/cropfig/SKILL.md` for the explicit "adapt to your stack" guidance, then either:

1. **Specialize them in place.** Edit the files to match your project (e.g., swap Keynote for a Python-generated deck, swap Korean for English, swap 7 Results for your project's structure). Commit the result back into your project's `.claude/`.
2. **Author your own preset.** If you're publishing a reusable specialization for a different field (wet-lab biology, HCI, machine-learning research, astronomy, etc.), follow this preset's pattern: an `examples/<field>/` directory at the repo root with the same internal layout (`agents/`, `commands/`, `skills/`, `memory-templates/`, plus a `README.md` that mirrors this one). PRs welcome — see `CONTRIBUTING.md` at the repo root.

## How to author your own preset (4-step recipe)

1. **Identify which core agents need a domain-flavored rewrite.** For most fields it's just `analysis-implementer` — the supervisor / paper-writer / figure-descriptor / reviewer can usually stay generic with a few placeholder fills.
2. **Identify field-specific commands and skills you'd want.** Anything tied to a specific export pipeline (Keynote / Jupyter / RMarkdown / Quarto) belongs in your preset, not the core.
3. **Produce redacted memory skeletons.** Show what each agent typically tracks in your field, without leaking your real project content.
4. **Add a `README.md` and submit a PR.** Follow this file's structure.
