# Round 1 on a refreeze: an experiment beside step 9c

Agent-assisted results, not certified Trusted Tester results. **This is a reference check, not part of step 9c's tally** (which uses round 1's original freeze, 2026-11-04) and not reflected in the README's status table. Round 1's pages are development pages.

**What was done.** Abby asked to refreeze round 1's pages with the freeze as it is now, compare the sources, and test again to see whether the results match before and after the freeze improvements. The refreeze is `evals/judging/gate-2026-11-17-9c/round1-refrozen/` (2026-11-18; 9 pages and 18 site searches, 27 recordings, none suspect; the original `evals/judging/round1/frozen/` was not touched). The tests ran with the same code, judge (CLI route, `claude-sonnet-5-5`, prompt SHA-256 `e8320f2c…`), types and mode (`tested_frozen`) as the formal 9c run, with `apijudge_gate.py --frozen-dir`; one run, one page at a time, after the formal runs.

**Source comparison (old recording against new).** No page's main document is byte-identical: the site's asset bundle names and cache-busting values changed on every page, and the site-wide news list in the header and footer changed (headlines, dates, counts). The text inside `<main>` is **identical on p01, p04, p07, p08 and p09**. It differs on p02 (the result count 23383 to 23481 and one other number), p03 (one link label, "Comments" to "X/Twitter") and p06 (a promotional block). p05's old recording has no `<main>` element to compare (not looked into). p03's first recorded document is a redirect placeholder in both freezes (its title names the tool that made it: "a11y-assist" then, "tobi508" now); its real page was compared after the redirect.

**Results**, formal 9c run (original freeze) against the refrozen run, scored by round 1's scorer and keys. `compare.json` and `compare.md` have every differing cell with its rows (the full per-cell rows are not kept here; the formal side is `../gate-2026-11-17-9c/compare-round1.json`).

- **Same main content** (p01, p04, p07, p08, p09; 85 keyed cells): 80 the same, 5 differ.

| Page | Test | Key | Formal (original freeze) | Refrozen | Key |
| --- | --- | --- | --- | --- | --- |
| p01 | 4.A | Fail | NEEDS REVIEW | Fail | yes |
| p01 | 9.A | Fail | Fail | NEEDS REVIEW | left for a person |
| p04 | 4.A | Pass | NEEDS REVIEW | Fail | no |
| p07 | 4.D | Fail | Fail | NEEDS REVIEW | left for a person |
| p07 | 4.E | Pass | Pass | NEEDS REVIEW | left for a person |

- **Changed content** (p02, p03, p05, p06; 68 keyed cells): 65 the same, 3 differ.

| Page | Test | Key | Formal (original freeze) | Refrozen | Key |
| --- | --- | --- | --- | --- | --- |
| p02 | 4.A | Pass | NEEDS REVIEW | Fail | no |
| p05 | 4.F | Pass | Pass | NEEDS REVIEW | left for a person |
| p06 | 4.D | Pass | Fail | NEEDS REVIEW | left for a person |

**Reading.** No cell moved to PASS or DOES NOT APPLY where the key fails, in either group. The cells that differ are 4.A, 4.D, 4.E, 4.F and 9.A, mostly between an outcome and NEEDS REVIEW; two are new false FAILs of 4.A (p04, in the group whose main content is identical, and p02). 4.A, 4.D and 4.F are judge-decided tests in part, so a judge answer varying between runs fits the pattern, but this was not traced and one repeat cannot separate it from the freeze's changes (nothing in the same-content group's `<main>` text changed). **Not verified:** whether any difference is the page, the freeze or the judge; a second run of the original freeze to measure the run-to-run variation alone.

Files: `compare.py` (writes `compare.json`, `compare.md`), `round1/gate.json`, `round1/run.json`. The recordings and page reports stay out of git.
