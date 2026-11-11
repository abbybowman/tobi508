# Code review notes, 2026-11-11 (partial, unverified)

Raw output of a line-by-line review that was cut short by a usage limit.
It is the starting point for a dedicated review thread, not a finished
list: **nothing here has been verified by a second reader**, and reviewers
that were interrupted wrote down only what they had found so far. Delete
this folder once that thread has produced the triaged list.

## What was covered

| File | Scope | State |
| --- | --- | --- |
| [A-surface.md](A-surface.md) | tools, `models.py`, `inline.py`, `explain.py`, resources, `app.py`, `jobs.py`, `config.py` | interrupted; 19 findings |
| [B-pipeline.md](B-pipeline.md) | `pipeline.py`, `judgment.py`, `apijudge.py`, `engine.py`, `rules.py`, `catalog.py`, `runlog.py`, `versions.py`, `pagecache.py` | interrupted; 18 findings |
| [D-traverse.md](D-traverse.md) | `traverse.py`, `walk.py`, `observe.py`, `reveal.py`, `forms.py`, `labels.py` | interrupted; 25 findings |
| [K-checks-9bc-19a.md](K-checks-9bc-19a.md) | `site.py`, 9.B, 9.C, 19.A against their specs | complete; 15 findings |
| [L-evals.md](L-evals.md) | `evals/*.py`, `evals/agent/*.py` | interrupted; 18 findings |

Not reviewed at all: `browser.py`, `capture.py`, `egress.py`, `policy.py`,
`redact.py`, `access.py`, `frozen.py`, `andi.py`, `scrt.py`, `compare.py`;
`motion.py`, `mechanism.py`, `flash.py`, `flashcap.py`; the checks for
2.A-2.D, 3.A, 4.A-4.F, 5.A-5.H and 9.A; the test suite, CI, Dockerfile and
packaging. [BRIEF.md](BRIEF.md) is the brief every reviewer worked from.

## Leads to verify first

Reported as P1 by a reviewer; each needs a second look before any fix.

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
