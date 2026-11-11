# Handoff: finish the code review, in phases

Paste everything below the line into a fresh session on this repository.

---

You are picking up a line-by-line review of this codebase (`tobi508`).
Read `CLAUDE.md` first, then
`docs/reviews/2026-11-11-code-review-notes/README.md` (what a first
attempt covered, its unverified leads, measured tool sizes) and
`BRIEF.md` in the same folder (the brief every reviewer works from).

**What I want at the end:** one file,
`docs/reviews/2026-11-11-code-review.md`: a triaged, prioritized list of
things to fix, in plain language for me (Abby) to review and hand to
other threads. For each item: what is wrong, why it matters, where
(file:line), the smallest sensible fix, and whether you **verified** it
(how) or it is a reviewer's unverified claim. Group by priority: P0 a
false PASS or wrong Does Not Apply on real pages, or a security hole; P1
wrong result, crash or hang in plausible conditions, or large waste; P2
moderate waste or a NEEDS REVIEW-safe gap; P3 cleanup. Within a priority,
put first what affects the Nov 20 demo and what a consumer agent sees
(tokens, time). End with a short "if we started over" section: the few
structural changes worth making, with what each would cost. Do not fix
code in this thread; no pull request.

**Why phases.** The first attempt launched 18 reviewers at once and hit
the 5-hour usage limit in minutes, losing most of the work. So:

- At most **3 subagents at a time**; wait for all of them before starting
  more. Use Sonnet for reviewers (never the top-tier model, and Opus only
  if a finding cannot be settled otherwise); Haiku for mechanical checks.
- Every reviewer writes to its own file **inside
  `docs/reviews/2026-11-11-code-review-notes/`** and appends each finding
  as soon as it has it, so an interrupted reviewer loses nothing.
- **After each phase:** verify that phase's P0 and P1 claims yourself
  (read the code; run one targeted test or a short script where that is
  cheap), add them to the triaged file as confirmed, refuted or
  unverified, then commit and push. A phase that is committed is done
  even if the session ends there.
- If a phase is cut off, the next session starts from the files on disk.

**Phase 0: no subagents.** Verify the leads already on file (README,
"Leads to verify first": B-01, B-02, A-01, A-05, B-03, B-04, D-01 to
D-03, K-01 to K-04, L-01 to L-03) and read the rest of A, B, D, K and L
for anything else at P1. Write the first version of the triaged file from
what survives. Commit. This alone is a useful result.

**Phase 1: security and what agents see (3 reviewers).**
1. `browser.py`, `capture.py`, `egress.py`, `policy.py`, `redact.py`,
   `access.py`, `frozen.py`, `andi.py`, `scrt.py`, `compare.py`: the
   allowlist and redirects, the egress proxy, the HAR, chunk and media
   stores, redaction, sign-in and run ownership (do resources check the
   owner as tools do?), parsing of an untrusted report file.
2. Finish the token measurement the README started: a real run on a
   realistic page (`tests/fixtures/budget/agency-home.html`), the answer
   flow, `tobi_run_status`, `tobi_explain`, and the report resource; size
   by field, repeated strings, empty fields serialized, what a calling
   agent cannot act on. Output schemas are already known to be more than
   half of the 13,700 tokens a session pays before any call.
3. The files the interrupted reviewers did not reach in groups A
   (tools, `models.py`, `jobs.py`, `config.py`) and B (`pipeline.py`,
   `judgment.py`, `apijudge.py`): compare each notes file's findings with
   the file list in the README and review what has no findings yet.

**Phase 2: the keyboard and label checks against their specs
(3 reviewers).** `checks/base.py` with 4.A-4.C; 4.D-4.F; 5.A-5.D. Each
reads the check and its spec in `specs/rules/` row by row: a spec row
with no code, code deciding what no row states, a different first-match
order. A mismatch that can give PASS or Does Not Apply is P0. Also: extra
page loads and why; long or repeated text sent to the agent; code copied
from another check (name both).

**Phase 3: the rest of the checks and the watchers (3 reviewers).**
5.F-5.H with 9.A; 2.A-2.D with 3.A; `motion.py`, `mechanism.py`,
`flash.py`, `flashcap.py` (fixed waits in seconds, "nothing observed"
against "could not observe", the flash maths against WCAG 2.3.1).

**Phase 4: the core and the plumbing (2 reviewers).** What group D left
in `traverse.py`, `walk.py`, `observe.py`, `reveal.py`, `forms.py`,
`labels.py`; then the test suite, CI, Dockerfile and packaging (where the
suite's time goes, modules and principles with no test, tests that assert
little, unused fixtures, image and CI problems).

**Phase 5: no subagents.** The "if we started over" section, from the
duplication and design notes every reviewer left; a final pass on
ordering; commit and push. Then delete the raw notes folder, or ask me.

Start each of your updates to me with the phase you are in and what is
committed so far.
