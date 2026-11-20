# Follow-through 2026-11-19: does Agent A now finish the workflow?

A behaviour check, not a scored round: no keys, no accuracy claim. Three live
public pages, frozen at the start (`frozen/freeze.json`) and replayed as the
agent eval does (`tested_frozen`: the tested page from the freeze, other pages
of its site live). Agent A (Sonnet 5.5, `claude-sonnet-5-5`) on the CLI route,
prompt `round1-v1` with no extra paragraph, `--no-subagents --debrief` as in
the 2026-11-19 compare, one page per run (`--group-size 1`), run from a
worktree at `81b8029` (the tool descriptions of PR #140). Once with the
calling agent answering open questions (`--judge client`) and once with the
server's own judge (`--judge api`: `JUDGE_ROUTE=cli`, the same model). Agent-
assisted results, not certified Trusted Tester results.

| Page | Why |
| --- | --- |
| https://www.section508.gov/ | asked for |
| https://www.nasa.gov/careers/ | asked for |
| https://www.weather.gov/ | a page with a form: text, radio and checkbox fields (counted from its markup before choosing) |

`pages.txt` needs a SHA-256 per page; there is no SCRT file, so each is the
SHA-256 of the URL itself.

## Figures

`followthrough.json` (this folder's runs) and `r3-followthrough.json` (the
2026-11-19 compare's 15 Agent A conversations, the "before"), both made by
`evals/agent/followthrough.py` from the files here (`--zip=` the transcript
zip): the same code on both sides. Summary in `evals/README.md`
("Follow-through 2026-11-19").

## In git

| Path | What |
| --- | --- |
| `pages.txt`, `frozen/index.json`, `frozen/freeze.json` | the page list and freeze records |
| `results/arm-a-<client\|api>-g<1-3>/` | each run's `summary.json`, `final.md`, `debrief.md`, and the tool's `runs/<id>/report.json` (`steps.jsonl` is left out: the transcripts have every call; `pre-scrt.json` too: `scrt.from_report` rebuilds it from the report, every line but the inlined screenshots, checked on client-g2: 2,616 of 2,620 lines) |
| `transcripts-no-images.zip` | the six `transcript.json`, picture bytes replaced by a marker (the counts are identical from it and from the full files, checked) |

## Not in git

The frozen recordings (`frozen/pages/`, 105 MB) and each run's evidence and
full transcripts (about 520 MB) stayed on the container this ran in. They
are not needed to recount anything above. One api-mode attempt at page 1 was
stopped after about 15 s, before any result, because it overlapped client
page 3 and the tool selection pass (load 4.7 on 4 CPUs); its folder was
deleted and the run started again on its own.
