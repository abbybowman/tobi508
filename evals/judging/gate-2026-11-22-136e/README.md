# Gate 2026-11-22-136e, #136: 4.A 1.20.0 on round 2's search page

Agent-assisted results, not certified Trusted Tester results. A development
rerun on the round's frozen page; it never replaces the round's blind score.

4.A 1.20.0 (Abby, 2026-11-22, option 1): a radio group whose change makes the
page leave is reached when one ArrowDown and one ArrowUp from its stop each
select another radio of it. `evals/apijudge_gate.py run --date
2026-11-22-136e --round 2 --pages search --tests 4.A --types 4.A
--frozen-mode replay`, the server judge (CLI route, `claude-sonnet-5-5`),
Playwright's Chrome 153.0.8010.12; exited 0, the page from the freeze.

| Page | Key | 136d | Now |
| --- | --- | --- | --- |
| p03 search | Pass | NEEDS REVIEW (`G3`; five date radios J1 unsure, `k7`-`k11` M7) | NEEDS REVIEW (`G4 RC`): no instance fails or is open; held only by guard RC (content that opens, step 15) |

The date radio buttons are no longer asked (42 answers, 47 before). The
page's reload on each change is what the key fails under 5.D, not 4.A.
