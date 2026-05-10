---
name: cropfig
description: Produce figure-only PNGs from a Keynote deck — strips the "Figure N. Title" header above and any caption below, leaving just the figure panels with minimal padding. Use when an agent or command needs the raw figure content (no header, no caption) — including the /sync command's docx embed phase, slides, social posts, reviewer responses, or any context where the caption is supplied separately.
---

> **Neuro-fMRI preset — example skill.** This skill is part of the worked specialization in `examples/neuro-fmri/`. It is macOS-specific (Keynote + AppleScript) and assumes a paper-figure deck that has been exported to `Figures_snapshots/` by an `export_keynote.sh` companion script. Adapt the paths/commands to your stack; the core idea (band-classification + tight-bbox crop) transfers to any tool that exports captioned figure PNGs.

# Tight Figure Crop (figure-only PNGs)

## Configurable paths

The skill reads two environment variables (with sensible defaults relative to the project root):

| Variable | Default | Purpose |
|---|---|---|
| `FIGURES_SRC` | `Figures_snapshots/` | Captioned PNG export source — produced by your Keynote (or other) export script. Read-only here. |
| `FIGURES_DST` | `Figures_tight/` | Header-stripped figure-only PNG destination. Owned by this skill; overwritten on every run. |
| `EXPORT_SCRIPT` | `./export_keynote.sh` | Optional: path to your idempotent export script. If unset, you must export PNGs to `$FIGURES_SRC` yourself before invoking this skill. |

Set them in `.claude/settings.json` `env`, or export in the shell before invoking the skill.

## When to use

Invoke this skill when any of the following holds:

- A `/sync`-style docx-embed command needs to embed figure-only PNGs into a `.docx` (the docx already prints its own caption text, so the embedded picture must not duplicate "Figure N. Title").
- A subagent or slash command (e.g., `paper-writer`, `figure-descriptor`, `reviewer`, custom commands) needs the **figure-only** PNG of a slide — without the "Figure N. Title" header or caption.
- The user asks for "tight crop", "header 빼고", "캡션 빼고", "figure only PNG", or to produce a clean figure for slides / social / a reviewer response.
- Preparing a figure for downstream image processing where surrounding text would interfere.

Do **not** invoke this skill when:

- The caller wants the canonical caption-bearing PNG (e.g., to read the slide as it appears in Keynote, including its title and caption text) — read `$FIGURES_SRC/*.png` directly. This skill never overwrites that folder.
- The caller only needs to check figure metadata or layout; the captioned source is the simpler choice.

## Output contract

| Path | Owner | Top "Figure N." label | Bottom caption | Used by |
|------|-------|----------------------|----------------|---------|
| `$FIGURES_SRC` | your `export_keynote.sh` | KEPT | removed | slide-context readers, todofig, agents reading slide content |
| `$FIGURES_DST` | **this skill** | **removed** | removed | docx embeds, figure-only consumers |

`$FIGURES_DST/<filename>` mirrors the source filename so callers can map slide → output path 1-to-1.

## Procedure

### Step 1 — Refresh source PNGs

If `$EXPORT_SCRIPT` is configured and exists, run it (idempotent — should skip when source `.key` is unchanged):

```bash
bash "${EXPORT_SCRIPT:-./export_keynote.sh}"
```

If the user passes a custom path argument, forward it: `bash "$EXPORT_SCRIPT" "$KEY_PATH"`.

**Guard:** if the export fails (Keynote not installed, AppleScript permission denied, headless environment), surface the error and stop. Do not crop stale PNGs without telling the user.

If you don't have an export script, ensure `$FIGURES_SRC` already contains current captioned PNGs before invoking this skill.

### Step 2 — Tight-crop each slide

Run the bundled Python script. It detects and removes the top label band, then tight-bbox crops, adds 10 px white padding, and writes to `$FIGURES_DST/`:

```bash
python3 .claude/skills/cropfig/crop_top_label.py
```

Optional positional args override the env defaults: `python3 .claude/skills/cropfig/crop_top_label.py [SRC_DIR] [DST_DIR]`.

The script uses a band-classification heuristic (color saturation + long-dark-run detection) that mirrors typical bottom-caption detection in Keynote-export pipelines, so top-label detection stays consistent.

### Step 3 — Report

Brief report:

```
## Tight figure crop — YYYY-MM-DD

- Source: $FIGURES_SRC  (N PNGs)
- Output: $FIGURES_DST  (N PNGs)
- Top label removed: M / N

Slides where label was NOT detected (left as tight-bbox only):
- <filename> — tight-bbox only
```

If Step 1 failed, report only that and skip Steps 2–3.

## Failure modes

| Symptom | Cause | Action |
|---------|-------|--------|
| `Keynote file not found` | wrong `.key` path | check the argument; if no default makes sense for your project, set `EXPORT_SCRIPT` explicitly |
| `osascript` permission denied | macOS Automation permissions | grant Terminal/Claude permission to control Keynote |
| Top label NOT removed for a slide | label band thinner than `MIN_LABEL_HEIGHT=30` rows, or contains a colored element (logo, badge) | accept — tight-bbox still removes outer whitespace; do not lower thresholds globally to catch one slide |
| `ModuleNotFoundError: PIL` / `numpy` | bare environment | `python3 -m pip install pillow numpy` |

## Files

- `SKILL.md` — this file.
- `crop_top_label.py` — the cropper. Importable (`from crop_top_label import main`) or runnable as a script. Heuristic constants are at the top of the file; tune there if your deck layout changes.
