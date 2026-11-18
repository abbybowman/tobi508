# Hackathon submission docs

The documents for the GSA MCP and AI Agent Hackathon (Service "Read"
Integration track). Due Nov 20, 2026; reviewed asynchronously with a
5-minute demo video. Hackathon page:
https://www.gsa.gov/super-intelligence/si-community-of-practice/events-and-training/mcp-server-and-si-agent-government-hackathon

| File | What it is |
| --- | --- |
| [evaluation.md](evaluation.md) | Evaluation document, the source |
| [out/TOBI-evaluation.docx](out/TOBI-evaluation.docx) | The same, built in GSA's Word template (the file to upload) |
| [build_pptx.py](build_pptx.py) | The deck's source: builds it in GSA's PowerPoint template |
| [out/TOBI-deck.pptx](out/TOBI-deck.pptx) | The deck (the file to upload) |
| [deck.md](deck.md) | The deck's text and speaker notes, generated from the `.pptx` for reading and diffs |
| [demo.md](demo.md) | The 5-minute demo script |
| [templates/](templates/) | GSA's sample evaluation document and deck, byte for byte, used as templates |
| [diagrams/](diagrams/) | The flow diagram |

## Building the Word file

```bash
python3 docs/hackathon/build_docx.py docs/hackathon/evaluation.md docs/hackathon/out/TOBI-evaluation.docx
```

It needs python-docx (not a project dependency). It keeps the template's
styles and replaces its body; blockquotes in the Markdown are drafting
notes and are left out. Rebuild and commit the `.docx` whenever
`evaluation.md` changes.

## Building the deck

```bash
python3 docs/hackathon/build_pptx.py docs/hackathon/out/TOBI-deck.pptx
```

Needs python-pptx. Every figure in it is copied from `evaluation.md`:
change both together, rebuild both files, and regenerate `deck.md` with the
pptx skill's `slide_text.py` (or any `.pptx` text dump).

## Where the figures come from (Abby, 2026-11-18)

- **The three blind rounds** (`evals/judging/round1`, `round2`,
  `round2-armc`, `round3`): each scored once, before the site was used for
  development. Never replaced by a later run.
- **The rerun after the fixes** (`evals/judging/gate-2026-11-17-9c/`,
  `evals/README.md` "Gate 2026-11-17-9c"): all 29 pages, labelled as
  development evidence. The README's status table reads the same run.
- **The comparison of the calling agent, the server judge and the
  baseline on round 3's pages** (`evals/judging/compare-2026-11-19-r3/`,
  in progress): fills the remaining [FILL] markers.
- **Published answer keys:** the ACT and Baseline tests at the commit
  named in the document.

There is no separate scored run at the submission commit.

## Markers

- **[FILL: …]** a figure a run still in progress will supply. Copy it from
  that run's files, never estimate it.
- **No certification claims.** Never describe a tested page as certified,
  compliant or Section 508 conformant (CLAUDE.md principle 1).
