# Code review notes, 2026-11-11 (raw, superseded)

The reviewers' raw notes, one file per group. **The checked and triaged
list is [../2026-11-11-code-review.md](../2026-11-11-code-review.md)**;
read that, not these. What these still hold that the list does not: the
row-by-row spec tables (files E, F, H, M, N), the measurement tables
(T, W) and the test-coverage tables (Q). Severities here are the
reviewers' own and were changed in the triage. Delete this folder when
those tables are no longer wanted.

## What was covered

| File | Scope | State |
| --- | --- | --- |
| [A-surface.md](A-surface.md) | tools, `models.py`, `inline.py`, `explain.py`, resources, `app.py`, `jobs.py`, `config.py` | interrupted; 19 findings |
| [B-pipeline.md](B-pipeline.md) | `pipeline.py`, `judgment.py`, `apijudge.py`, `engine.py`, `rules.py`, `catalog.py`, `runlog.py`, `versions.py`, `pagecache.py` | interrupted; 18 findings |
| [D-traverse.md](D-traverse.md) | `traverse.py`, `walk.py`, `observe.py`, `reveal.py`, `forms.py`, `labels.py` | interrupted; 25 findings |
| [K-checks-9bc-19a.md](K-checks-9bc-19a.md) | `site.py`, 9.B, 9.C, 19.A against their specs | complete; 15 findings |
| [L-evals.md](L-evals.md) | `evals/*.py`, `evals/agent/*.py` | interrupted; 18 findings |
| [S-security.md](S-security.md) | `browser.py`, `capture.py`, `egress.py`, `policy.py`, `redact.py`, `access.py`, `frozen.py`, `andi.py`, `scrt.py`, `compare.py` | complete; 12 findings |
| [T-tokens.md](T-tokens.md) | what a calling agent receives, measured on `agency-home.html` | complete; 11 findings |
| [G-gaps-AB.md](G-gaps-AB.md) | what A and B left in the tools, `models.py`, `jobs.py`, `config.py`, `pipeline.py`, `judgment.py`, `apijudge.py` | complete; 15 findings |
| [E-checks-4abc.md](E-checks-4abc.md) | `checks/base.py`, 4.A, 4.B, 4.C against their specs | complete; 19 findings |
| [F-checks-4def.md](F-checks-4def.md) | 4.D, 4.E, 4.F against their specs | complete; 23 findings |
| [H-checks-5abcd.md](H-checks-5abcd.md) | 5.A to 5.D against their specs | complete; 17 findings |
| [M-checks-5fgh-9a.md](M-checks-5fgh-9a.md) | 5.F, 5.G, 5.H, 9.A against their specs | complete; 22 findings |
| [N-checks-2x-3a.md](N-checks-2x-3a.md) | 2.A to 2.D, 3.A against their specs | complete; 16 findings |
| [W-watchers.md](W-watchers.md) | `motion.py`, `mechanism.py`, `flash.py`, `flashcap.py` | complete; 17 findings |
| [C-core-rest.md](C-core-rest.md) | what D left in the keyboard core | complete; 11 findings |
| [Q-tests-ci.md](Q-tests-ci.md) | tests, CI, Dockerfile, packaging | complete; 16 findings |

[BRIEF.md](BRIEF.md) is the brief every reviewer worked from;
[HANDOFF.md](HANDOFF.md) is the prompt the phases followed.

## Leads of the first attempt

All checked in phase 0; the triaged list has what became of each.

- **B-01** picture links taken from page text are read as file paths
  (path traversal, another run's files).
- **B-02** page text can close the `<untrusted_page_data>` block in a
  judge request.
- **A-01** jobs have no owner: in hosted mode another user's job could be
  reached. **A-05** `decided_by: "human"` is self-asserted (already on the
  roadmap: Now, 3).
- **B-03** `report.json` is written without a lock or an atomic rename; a
  half-written read looks like "nothing left". **B-04** the judge phase
  runs inside the browser slot and outside every run limit.
- **D-01** form fields in shadow roots read as "no form fields" (DOES NOT
  APPLY). **D-02** `evaluate_top` turns an exception into `None`, which
  callers read as "nothing found". **D-03** click handlers in shadow roots
  are not found by 4.A's scan.
- **K-01** an "other page" that is the tested page under another spelling
  (trailing slash, http, a redirect) is compared with itself, so 9.B and
  9.C can PASS on nothing. **K-02/K-03** shadow DOM and frame content is
  invisible to 9.B, 9.C and 19.A; 9.C with nothing analysed is DNA.
  **K-04** 9.C pairs `javascript:` links as the same destination.
- **L-01** re-scoring a locked round uses today's registry. **L-02/L-03**
  the ApiJudge gate has no minimum number of decided cells and ignores a
  wrong DNA. Check these before the gate decides `JUDGE_TYPES`.

## What every session pays (measured)

From `list_tools` on the server as of this commit: about **55,000
characters (roughly 13,700 tokens)** before any call. Output schemas are
31,600 of them (`tobi_run_status` 11,200, `tobi_run_tt_tests` 9,300,
`tobi_answer_questions` 7,800); descriptions 7,000 (`tobi_run_tt_tests`
4,300); input schemas 9,800 (`tobi_answer_questions` 5,200); server
instructions 2,300. A result for a tiny page (`no_trap.html`, default
tests) was about 19,500 characters. Measurement of a realistic page, the
answer flow and the report resource was not finished.
