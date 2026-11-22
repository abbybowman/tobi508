# Gate 2026-11-22, #136 (4.A and 4.F): the rerun after the two fixes

Agent-assisted results, not certified Trusted Tester results. A development
rerun on the rounds' pages; it never replaces any round's blind score.

## What ran

The branch after #136's two follow-up fixes (Abby, 2026-11-21): 4.A 1.18.0
(a title that rewords the element's name is not essential; F38, F39) and 4.F
1.15.0 (a keyboard trap's move back to its start is no signal; F34).
`evals/apijudge_gate.py run --date 2026-11-22-136b --round 3|2|1 --tests
4.A,4.F --types 4.A,4.F --frozen-mode replay`, the server judge (CLI route,
`claude-sonnet-5-5`), Playwright's Chrome 153.0.8010.12. Each round exited
0; every page came from the freeze. Each round's `run.json` is here;
`results/` and `runs/` stay out of git.

Compared with gate 2026-11-21-136 by each round's own key and scorer:
`compare.py`, every moved cell in `moved.md` (`moved.json`).

## What it found

No PASS against a FAIL key, in any round.

**Round 2 p03 (4.A, key Pass): the sort button is fixed, the page still
FAILs.** The sort button's title is now "not essential" (`t12:M13`: "name
already says it toggles the order and gives the current state; title just
rewords it"). Two titles the last run also asked about now answer the other
way: the "(RSS)" and "(Atom)" links, titles "View the current search as an
RSS feed" / "... Atom feed" (`t18`, `t19`: M14). Last run: "not essential"
("visible text '(RSS)' with an RSS icon already says what it is"); this run:
"essential" ("'(RSS)' is a bare abbreviation; the title explains it is a
feed of the current search"). The new rubric's "anything else the title adds
that the name and page do not give" fits these as it fits F39 ("Sort" with
"Sort by release date, newest first"), so this is the rubric as written, not
a judge slip. Whether a link named by a format (RSS, Atom) with a title that
spells it out is essential is Abby's call (asked on #136); not changed.

**Round 2 p08 (4.F, key Pass, the 5340 timeline): still FAIL in this run,
now fixed (gate 2026-11-22-136c below).** The trap fix took the wrap's S2
and S3 away (`o1:M6[S2,S3,S3]` before, `o1:M6[S3]` now). The S3 left was a
measuring error: inside the timeline's frame, the stop was placed on the
page but its scroll box where it sits in the frame, 396 px higher (the
frame's offset), so the panel's button read as above the panel.

**Round 2 p09 (4.F, key Pass): new wrong FAIL in this run, NEEDS REVIEW
after the fix.** The same signals as last run (`S3` x4); the judge answered
"does not preserve" where last run's said "unsure". Two of the four S3 were
the frame measuring error above.

**Round 1 p01 (4.F, key Pass): NEEDS REVIEW to PASS** (`o1:M7`, G5). The trap fix does not touch this page (no
loop): both runs' walks wrapped after the same 69 stops with the same
signals, and the judge's answer moved from "unsure" to "preserves".

**Round 1 p02 (4.A, key Pass): new wrong FAIL, the judge alone.** The same
evidence and question as last run; last run's judge answered "unsure"
whether Tab reaches anything that does what the unreached "Last Month" radio
button does, this run's "no alternative" (`k1:M6`). Radio buttons in a group
take one Tab stop and arrow keys move between them, so the radio button is
reachable by keyboard. Not changed here; noted on #136.

Round 3: no cell moved. Unchanged wrong FAIL: round 2 p01 4.A (the home
page's category icon links; Abby retests it).

## Gate 2026-11-22-136c: the frame fix (4.F 1.15.1)

A stop's scroll box inside a frame now moves onto the page with the stop
(`t4f.OrderHook.on_step`; F35, f28's in-order list inside a frame 400 px
down, which failed before the fix and passes after). Among all three rounds'
pages in this rerun, only round 2's p08 (5340) and p09 (5144) have a stop in
a scroll box inside a frame, so only they were rerun (`--pages 5340`,
`--pages 5144`, `--tests 4.F`), into `../gate-2026-11-22-136c/round2/`:

| Page | Key | 136b | 136c | Rows |
| --- | --- | --- | --- | --- |
| p08 | Pass | FAIL | NEEDS REVIEW | `o1:M4 G3`: no signal left; held for a person because Tab never left the timeline's trap |
| p09 | Pass | FAIL | NEEDS REVIEW | `o1:M9[S3 x3] G3`: the judge answered "unsure" |

p09's move is partly the judge: its last three answers on near-identical
evidence were "unsure", "does not preserve", "unsure".
