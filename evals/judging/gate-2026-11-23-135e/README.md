# Gate 2026-11-23-135e, #135: 4.A 1.21.0 and 4.F 1.16.0 (step 15)

Agent-assisted results, not certified Trusted Tester results. A development
rerun on the rounds' frozen pages; it never replaces any round's blind score.

## What ran

This branch: 4.A and 4.F read what menus, tabs and sections open from the
shared walk, with its onward Tabs (`opened.py`); 4.A's key press that only
scrolls has no effect (option ii); 4.F's S6 where Tab reaches a menu late
(option a). `evals/apijudge_gate.py run --date 2026-11-23-135e --round
3|1|2 --tests 4.A,4.F --types 4.A,4.F --frozen-mode replay --frozen-dir
<copy>`, the server judge (CLI route, `claude-sonnet-5-5`), Chromium
157.0.8103.78 (not the pinned 153, #142), one round at a time. Nothing was
loaded live.

Freezes (all checked before use): round 1 and round 2, #138's copies
(`gate-2026-11-22-138-roundN-copy.zip` parts, every file against the
`SHA256SUMS.txt` inside; their original recordings byte for byte the
checked archives `768b8f5f…` and `8115fde0…`); round 3, #138's copy with
#134's p07 and p08 recordings (`34e95dbc…`, `26cb20bb…`; #134's zip
`31bd2443…`), its other 26 original recordings byte for byte `2ce3446a…`.

Code: round 3 ran before three late changes, round 1 before the tab rule,
round 2 before it too: `HOVER_OPENED_MAX` 200 to 250 (round 3 p06's 4.A
was held by it), the tab-list exception (round 1 p04's 4.F, rerun alone
after: PASS), and the visible-text naming (wording only).

## What moved against gate 9c

See `moved.md` (from `compare.py`) for every cell with its rows.

- **Round 3:** 4.A PASS on p01 to p05 and 4.F PASS on p01, p02, p04, p06
  (key Pass); p04's 4.F was a false FAIL in 9c (the "Type" filter is open
  at load despite `aria-expanded="false"`). p09 4.A **FAIL** (key Fail):
  the "All" options are reached only after leaving the menu, and Enter and
  Space do nothing. Against the key: p09 4.F FAIL (S6, F85; Abby's option
  a) and **p08 4.F PASS (false)**: the judge called the tag cloud
  "independent links"; not from opened content; a known wrong outcome,
  accepted for now (Abby, 2026-11-23).
- **Round 1:** 4.F p01 and 4.A p08, p09 PASS (key Pass). p04 4.F PASS to
  NEEDS REVIEW (the Careers tabs, now opened): fixed by the tab-list
  exception and rerun alone: PASS. p06 4.F PASS to NEEDS REVIEW: the
  judge unsure on the video player's jumps, the same signals gate 9c
  passed (judge variation).
- **Round 2:** 4.F p01, p04, p06, p07, p10 and 4.A p02 PASS (key Pass);
  4.F p02 false FAIL to PASS; 4.F p08 false FAIL to NEEDS REVIEW.
  p05 4.A FAIL to NEEDS REVIEW (key Fail): the judge answered "unsure"
  whether another link plays the demo reel; run again alone: FAIL (M6),
  as the key. Judge variation, not this change (the button is on the
  page, not in opened content).

Judge eval for 4.F's J1 (its input changed): run 44, `judge-eval-4f/`.
