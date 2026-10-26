**English** | [中文](./README.zh.md)

# Vibe Coding Textbook: From Running to Getting Paid

> **In one line**: a five-volume open textbook that teaches you, in the age of AI-written code, **how to do it right, how to trust it, how to keep it contained, and how to make it sell**.
> **Maps to**: Stages 1–5 of the "Vibe Coding Study Plan" (about 23 weeks, 30+ hours per week).
> **Zero-background friendly**: every volume enters from intuition and assumes no testing, security, or business background.

---

## Why These Five Volumes

AI has cut the cost of "writing code" down to minutes, but **the delivery bottleneck has moved from "can it be written" to "is it right, can it be trusted, is it contained, is it worth doing"**. Each of these five questions gets its own volume:

| Stage | Volume | The question it answers | Directory | Chapters |
|---|---|---|---|---|
| 1 | *Vibe Coding: Putting the "Vibe" into a Harness* | Why should I trust that this generation is correct? | [`phase1/`](phase1/) | 4 |
| 2 | *Write the Spec First, Then Let the AI Build* | How do I get it to do things right to the standard I set? | [`phase2/`](phase2/) | 12 |
| 3 | *Treating AI Code as Untrusted Input* | What makes this code fit to ship? | [`phase3/`](phase3/) | 12 |
| 4 | *Contained: Attack Surface and Blast Radius* | Can an AI system be kept contained? | [`phase4/`](phase4/) | 10 |
| 5 | *From Running to Getting Paid* | Is this worth continuing to invest in? | [`phase5/`](phase5/) | 10 |

**48 chapters, 58 figures (one Chinese set and one English set, 116 PNG files in total), with runnable forensics scripts and delivery templates.**

## How to Read

- **Read in order**: the five volumes build on one another: Stage 2 assumes you already record your own numbers, Stage 3 assumes you already have specs.
- **Each volume is self-contained**: each has a `README.md` (whole-book map + outline), `chapters/`, `assets/`, `code/`, and most come with `templates/`. Chapter numbers restart from ch01 within each volume and **do not run continuously across volumes**.
- **Exercises are mandatory**: the three-tier exercises at the end of each chapter (intuition check / hands-on application / boundary transfer) all come with collapsed answers. Skipping Tier 2 and Tier 3 means you have not really read the chapter.
- **Weekly breakdown**: each volume's README includes a "Reading Path and Weekly Plan Mapping", laid out for 30 hours per week.

## Quality Gates

Every chapter passes three gates before delivery, each reviewable:

| Gate | What it checks |
|---|---|
| Freshness fingerprint | The YAML frontmatter carries `last_verified` / `baseline_version` / `volatile_points` / `upstream_urls` — which numbers will go stale, and which version they were checked against, are written at the head of the chapter |
| Authoritative sources | Every chapter ends with "Authoritative references and further reading"; all links are tested reachable, and **definitions and specs are traceable to source** |
| Teaching completeness | Every chapter contains a cognitive anchor, a first-principles breakdown, a hands-on walkthrough, a misconception contrast table, a local knowledge map, and three-tier exercises; no placeholders; figures show no tofu boxes and no overlapping labels |

**Number discipline**: every number in the text falls into three explicitly labeled classes — external facts (source and date noted), teaching models (parameter assumptions stated), and example data (constructed, not measured). **Never draw a schematic curve as if it were measured data.**

## Repository Layout

```text
.
├── README.md          # this file: whole-book index and how to read
├── LICENSE            # license terms
└── phase1/ … phase5/  # five volumes, each self-contained
│   ├── README.md      # the volume's full map, outline, and reading path
│   ├── chapters/      # chapters (ch01-…, numbered within the volume)
│   ├── assets/        # figures (200+ DPI, PNG)
│   ├── code/          # runnable scripts (figures / forensics / template data)
│   └── templates/     # delivery templates you can copy as-is (in most volumes)
```

## Bilingual Maintenance

This repository ships both languages as equal products: an English file `X.md` and a Chinese file `X.zh.md` (English takes the default name, Chinese carries the `.zh` suffix). Figures follow the same rule: `fig-NN-slug.png` (English) pairs with `fig-NN-slug.zh.png` (Chinese). To keep the two versions in sync:

- Install the pre-commit hook once per clone: `git config core.hooksPath .githooks`
- Run the machine check before committing: `python3 tools/check_bilingual.py --min`
- Term translations follow [`docs/glossary.md`](docs/glossary.md); do not coin new renderings for listed terms.

## License

By default this work is licensed under **[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)** (Attribution–NonCommercial–ShareAlike):

- You are free to share and adapt the material, provided you give attribution and share under the same license;
- **Commercial use requires written authorization** (including paid training, paid newsletters, commercial publishing);
- For commercial licensing, contact the author through the repository's Issue tracker.

The code and scripts in this repository are covered by the same terms; if the code is ever open-sourced separately, a `LICENSE` notice will be added in that directory.

---

*This repository was split out from `books_lab` at `outputs/vibe-coding-textbook/`; all five volumes passed the quality gates on first release (verification date 2026-10-23).*
