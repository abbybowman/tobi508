# specs/rules: the rules specs

One spec per Trusted Tester test, `<id>-<short-name>.md`: the only source of
outcome logic (root `CLAUDE.md`, principle 2). CODEOWNERS requires the
owner's review of every change here.

## Versions

- Each spec's `spec_version` is recorded in every report: 0.y.z is a draft
  with no outcome, 1.0.0 is approved and built, then MINOR for rule changes
  and PATCH for wording (`_template.md`).
- One version is one text: after any change, take a number `main` has not
  used and run `uv run python -m tobi508.rules lock` (`versions.lock`;
  checked by `tests/test_spec_versions.py` locally and
  `scripts/check_spec_versions.py` in CI against `main`).

## Outcomes

- A test the tool cannot perform, or has no implemented spec for, is
  `NEEDS_REVIEW` with the note "This test could not be performed" and the
  reason (`Finding.not_performed`).
- Never report `NOT_TESTED` unless the test's TT text names it (PDF p. 6).
  3.A is the one test that does (flashing found); its WCAG 2.3.1 assessment
  is a note in the summary, recorded with NOT TESTED, never an outcome.
- Answers to open questions are recorded, never turned into outcomes outside
  the spec.
- Never PASS or DOES NOT APPLY on a reading that is not complete: a shared
  guard may move either to NEEDS_REVIEW, never the other way (guard CN and
  the others in `_template.md`; a spec lists its guards in its front matter
  `guards:`).

## Questions a careful tester settles by looking

An opinion leads to PASS only when a key press or another mechanical check
confirms it, or when the spec marks the question as one a careful tester
settles by looking. Those questions today: 2.B J2, 2.C J1, 2.D J1 and J2,
4.E J1, 4.F J1, 5.A J1, 5.B J1, 5.C J1, 5.D J1 and J2, 5.F J1, 5.G J1, 5.H
J1 and J2, 9.A J2, 9.C J1, 19.A J1. For these the judge must answer "unsure"
whenever the evidence does not settle it, and only those go to a person.

## Writing a spec

- A step must match something the TT PDF asks a human tester to do
  (principle 7). Cite the PDF's printed pages; read the TT text from
  `catalog.py` / `tt.json`, never retype it.
- Research first, then draft from `_template.md` (the steps at the top of
  `src/tobi508/checks/base.py`). `_browser-checks.md` holds the V-checks of
  built tests; `<id>-build-tasks.md` exists only while a test is built.
- Ask the owner before a rule change that removes a FAIL an answer key
  confirms or turns a NEEDS REVIEW into a PASS.
