# Gate 2026-11-23-135d, #135: 5.D 1.13.0 (step 15, phase 3)

Agent-assisted results, not certified Trusted Tester results. A development
rerun on the rounds' frozen pages; it never replaces any round's blind score.

## What ran

This branch with 5.D 1.13.0: the fields 4.C's walk reaches inside what a
menu, tab or section opens are filled (pass FO), and guard RC narrowed to
`reveal-walk` (Abby approved 2026-11-23, option a). `evals/apijudge_gate.py
run --date 2026-11-23-135d --round 3 --tests 5.D --types 5.D --frozen-mode
replay --frozen-dir <round 3 copy>`, the server judge (CLI route,
`claude-sonnet-5-5`), Chromium 157.0.8103.78 (not the pinned 153, #142).

Round 3's freeze: #134's copy (`round3-frozen-2026-11-20-134-chunks.zip`,
SHA-256 `31bd2443…13bd6`, every file its `MANIFEST-round3-copy.sha256`), so
p07 and p08 have the code they load when used; its other files are the
original freeze `2ce3446a…` byte for byte. Every page came from the freeze,
nothing was loaded live. 5.D took at most 33 s on a page; none ran out of
its time.

## What moved against gate 9c (round 3)

No PASS against a FAIL key.

| Page | Key | Gate 9c | Now | Why |
| --- | --- | --- | --- | --- |
| p01 home | Pass | NEEDS REVIEW (`G4 RC`) | **PASS** (agree) | The five header menus hold links only, and 4.C's walk reached every one |
| p03 contact | Pass | NEEDS REVIEW (`G4 RC`) | **PASS** (agree) | The same |
| p05 FITS verifier | Pass | NEEDS REVIEW (`G4 RC`) | **PASS** (agree) | The same |
| p06 FITS samples | Pass | NEEDS REVIEW (`G4 RC`) | **PASS** (agree) | The same, and 14 sections, all 19 walked to the end |

Still NEEDS REVIEW, with other rows than gate 9c (verdict unchanged):

- **p07** (Pass): gate 9c `G4 GU` (code missing from the recording); now
  `f1:M15 G3`: typing in the global search changes most of the window, so
  a person looks (#134's copy has the code, so guard GU no longer holds it).
- **p08** (Pass): gate 9c `G4 GU`; now both fields pass (`f1:M11 f2:M11
  G4`) and guard RC holds it: Tab did not reach every control in the "User
  menu for Guest User".
- **p09** (Pass): `G4 RC`, unchanged: the "All" drop-down's options are not
  reached by Tab (option a: a custom drop-down's options 5.D cannot say it
  checked).

Unchanged: p02 FAIL (false; #137 step 35b), p04 FAIL (agree), p10 DOES NOT
APPLY (as gate 9c).

No round 3 page has a form field inside opened content, so pass FO itself
moved nothing here; fixtures f25 to f28 show it.

5.D on round 3 now: agree 5, false FAIL 1, needs review 3, other 1
(`moved.md`, from `compare.py`).
