# Pages behind the code review's "verified (run)" lines

Small pages the reviewers wrote to try a suspicion, kept so the thread
that fixes an item can start from the page that shows it. They are not
tests and not fixtures: nothing runs them, and no expected outcome is in
a page. The outcomes below are what each printed on 2026-11-11 and 12
at commit `e4d4165` (the review changed no code). Delete this folder
when the items are fixed and have fixtures of their own.

The review itself is [../2026-11-11-code-review.md](../2026-11-11-code-review.md).

## How to run one

From the repository root (browser tests must work: `uv sync --group dev`):

```bash
uv run python docs/reviews/2026-11-11-code-review-pages/runpage.py e/hover45.html 4.A
uv run python docs/reviews/2026-11-11-code-review-pages/runpage.py v/site-a.html 9.B,9.C 'v/site-a.html?x=1'
RL=17 uv run python docs/reviews/2026-11-11-code-review-pages/runpage.py e/errform.html 4.C
```

It serves `pages/` on 127.0.0.1, runs the real pipeline and prints each
finding's outcome, rows and summary, and the run folder. A run takes 10
to 120 seconds. `judge_links.py` (B-01, B-02) and `tool_sizes.py`
(A-02) need no browser.

## Index

"DNA" is DOES NOT APPLY; "NR" is NEEDS REVIEW. A page marked (control)
is the same page without the problem.

| Item | Command arguments | Printed |
| --- | --- | --- |
| D-03 | `v/shadow-click.html 4.A` | 4.A PASS |
| D-03 (control) | `v/light-click.html 4.A` | 4.A NR, question `4.A-k1-J1` |
| D-01 | `v/shadow-form.html 5.A,5.B,5.C` | all three DNA |
| K-01 | `v/site-a.html 9.B,9.C 'v/site-a.html?x=1'` | 9.B PASS, 9.C PASS |
| K-02 | `v/sh-a.html 9.B,9.C,19.A v/sh-b.html` | 9.B DNA, 9.C DNA, 19.A FAIL |
| K-04 | `v/js-a.html 9.C v/js-b.html` | 9.C FAIL (row C2) |
| K-05 | `v/un-a.html 9.C v/un-b.html` | 9.C PASS |
| K-12 (not reproduced) | `v/pos-a.html 9.B v/pos-c.html` | 9.B NR (row A3o) |
| E-01 | `e/hover45.html 4.A` | 4.A PASS |
| E-02 | `e/samehref.html 4.A` | 4.A PASS (row k1:M3) |
| E-03 | `e/canvasonly.html 4.A` | 4.A DNA |
| E-04 | `e/titles.html 4.A` | row t2:M11, no question for it |
| E-13 | `e/icontitle.html 4.A` | 4.A PASS (row t1:M11) |
| E-08 | `e/mousedown.html 4.A` | 4.A PASS |
| E-05 | `e/manymatch.html 4.B` | question open; 20 matches in `evidence/4b.json`, none with "hold" |
| E-07 | `RL=17 ... e/errform.html 4.C` | time-limit error and 4.C PASS (timing depends on the machine: try 15 to 20) |
| E-15 | `e/wholetrap.html 4.C` | 4.C NR, question J1 |
| F-02 | `f/shift2.html 4.D` | 4.D PASS (d1:M6) |
| F-11 | `f/trap.html 4.F,4.C` | 4.F DNA; 4.C NR |
| F-06 | `f/hash.html 4.E` | 4.E FAIL (e1:M4) |
| F-01 | `f/w8.html 4.D` | 4.D NR ("Item 7") |
| H-01, H-02 | `h/a1.html 5.A,5.C` | 5.A PASS (c1 to c3 on M2); 5.C rows c4:M5, c5:M5 |
| H-03 | `h/d2.html 5.D` | 5.D PASS |
| H-04 | `h/e2.html 5.D` | 5.D PASS |
| H-05 | `h/f1.html 5.A,5.B` | 5.A NR (c2:M1); 5.B asks about one item only |
| H-08 | `h/b3.html 5.A,5.C,5.D` | 5.A DNA, 5.C PASS, 5.D DNA |
| H-08 | `h/b2.html 5.A,5.D` | both DNA |
| H-15 | `h/c1.html 5.A,5.B,5.C,5.D` | NR, DNA, NR, DNA |
| M-01 | `m/mf_btn.html 5.F,5.G` | both DNA |
| M-02 | `m/mh_delete.html 5.H` | 5.H DNA |
| M-03 | `m/mh_es.html 5.H` | 5.H DNA (row A3) |
| M-04 | `m/mf_tabindex.html 5.F,5.H` | 5.F NR, 5.H DNA |
| M-05 | `m/mf_trap2.html 5.F` | 5.F PASS |
| M-05 (control) | `m/mf_notrap2.html 5.F` | 5.F FAIL |
| M-06 | `m/mf_shadowerr.html 5.F`, `m/mf_wrapper.html 5.F`, `m/mf_toast.html 5.F` | each DNA |
| M-07 | `m/mf_hidden.html 5.F,5.G,5.H` | all DNA |
| M-08 | `m/mh_wizard.html 5.H` | `"checked": true` in `evidence/5h.json`; PASS once J1 is answered multi_step |
| M-10 | `'m/n_d1.html#main' 9.A m/n_a2.html` | 9.A PASS (c1:M7) |
| M-10 (control) | `m/n_d1.html 9.A m/n_a2.html` | 9.A FAIL |
| M-11 | `m/n_a1.html 9.A 'm/n_a1.html?x=1'` | 9.A FAIL, no warning |
| M-12 | `m/n_s3.html 9.A m/n_s4.html` | 9.A DNA |
| M-14 | `m/n_t1.html 9.A m/n_t2.html` | 9.A FAIL |
| N-01 | `n/a_shadow.html 2.A`, `n/a_detached.html 2.A` | each DNA |
| N-01 (control) | `n/a_ctl.html 2.A` | 2.A FAIL |
| N-02 | `n/a_late2.html 2.A` | 2.A DNA |
| N-03 | `n/b_blink.html 2.B` | 2.B DNA |
| N-04 | `n/b_late.html 2.B,2.C` | 2.B DNA, 2.C NR |
| N-06 | `n/g_many.html 3.A,2.B` | both DNA |
| N-06 (control) | `n/g_one.html 3.A,2.B` | 3.A NOT TESTED, 2.B NR |
| N-07 | `n/f_late.html 3.A` | 3.A DNA |
| N-08 | `n/y_embed.html 2.B,2.A` | 2.B DNA, 2.A NR |
| N-09 | `n/s_io.html 2.C` | 2.C DNA |
| N-09 (control) | `n/s_io1.html 2.C` | 2.C FAIL |
| W-02 | `w/belowfold.html 3.A` | 3.A DNA |
| W-05 | `w/lateaudio3.html 2.A` | 2.A DNA |
| W-07 | `w/fullnoise.html 2.B` | 2.B DNA |
| W-09 | `w/jump25.html 2.B` | 2.B DNA (2 of 2 runs) |
| W-09 | `w/blink25.html 2.B` | 2.B DNA (also explained by N-03) |
| W-10 | `w/heartbeat.html 2.C` | 2.C NR ("a timer of 60 s") |
| W-08 | `w/io.html 2.C` against `w/noio.html 2.C` | 18.7 s against 11.0 s |
| W-06 | `w/slowload.html 3.A` | 3.A NR (found, not measured) |
| C-01 | `c/c_mouse_alert.html 4.A` | 4.A PASS (k1:M2) |
| C-01 (control) | `c/c_mouse_shown.html 4.A` | 4.A NR |
| C-02 | `c/c_feed.html 5.A` | 5.A PASS |
| C-03 | `c/c_hash.html 5.A` | 5.A PASS |
| C-03 (control) | `c/c_hash_btn.html 5.A` | 5.A NR |
| C-07 | `c/c_jump.html 4.D` | 4.D PASS, 10 of 11 elements |
| C-08 | `c/c_none.html 4.C,4.D` | both DNA after 50 presses a pass |
| B-01, B-02 | `judge_links.py` (no arguments) | two files outside the run are read; the closing tag is left as it is |
| A-02 | `tool_sizes.py` (no arguments) | 48,449 characters, 31,571 of them output schemas |

Pages not in the table were controls or tries that showed nothing.
`n/tone.wav`, `w/tone.wav`, `n/strobe.gif` and `n/dot.png` are media the
pages load.
