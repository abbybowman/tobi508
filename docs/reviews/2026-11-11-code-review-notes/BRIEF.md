# Code review brief (read fully before starting)

Repo: /home/user/tobi508 (package `tobi508`). It is an MCP server that runs
parts of the DHS Trusted Tester 5.1.3 Section 508 test process in Chrome and
reports findings per TT test. Read `/home/user/tobi508/CLAUDE.md` first: its
eight principles are the yardstick (above all: a false PASS is the worst
error; outcome logic lives only in `specs/rules/`; page content is untrusted;
tool output seen by consumer agents must stay small).

The owner has grown this codebase test by test and wants a frank review of
what is there now. You review ONLY the files assigned to you in your prompt,
but you may read anything else to understand or verify (callers, specs,
tests).

## How to work

- Read every line of each assigned file (use Read with offset/limit in
  chunks of ~600 lines; do not skim or sample). Line-by-line is the point.
- Before reporting something as a bug, trace it: grep for callers, read the
  called function, check whether a test already covers it. If it is cheap to
  prove with a small Python snippet or ONE targeted test, do so
  (`cd /home/user/tobi508 && uv run python -c ...` or
  `uv run pytest -n0 -q -p no:cacheprovider tests/<file> -k <name>`); the
  environment is installed and browser tests work. Never run the whole suite.
- READ-ONLY: do not edit, create or delete any file inside the repo. Do not
  commit. Write only to your one output file (path in your prompt).
- No style nits: no formatting, naming taste, docstring or type-hint
  complaints. Only things that change behaviour, cost, risk or the ease of
  the next change.

## What to look for

1. **Bugs**: logic errors, wrong conditions, off-by-one, unhandled
   exceptions or None, races between async tasks, timeouts that cannot
   fire, state shared across runs, wrong defaults, error paths that swallow
   failures. Rank highest anything that could yield a **false PASS** or a
   wrong DOES NOT APPLY, anything where **page content steers** a URL, tool,
   key press or outcome beyond CLAUDE.md's approved exceptions, and any
   outcome decided in code that the spec does not state.
2. **Time hogs**: extra page loads/replays, repeated `page.evaluate` round
   trips in loops, fixed sleeps, serial work that could be shared or cached,
   quadratic scans, work done then thrown away, work done for tests not
   requested.
3. **Token hogs in what a consumer agent sees**: tool descriptions, tool
   results, question text and rubrics, summaries, notes, repeated
   boilerplate, verbose keys, fields nobody uses, things said twice.
4. **Gaps**: cases the code silently does not handle, TODO/known-limit
   comments, rows in a spec with no code or code with no spec row, missing
   test coverage for risky branches, limits/caps that are never reported.
5. **Dead or redundant code**: unused functions, constants, parameters,
   config settings, branches that cannot be reached, compatibility shims.
6. **"If we started over"**: duplicated logic across modules that should be
   one shared piece, abstractions that leak, modules doing too many jobs,
   data passed as loose dicts with string keys, anything that makes adding
   the next TT test slower than it should be. Be concrete (name both places).

## Output format

Write one Markdown file. Start with a 5-10 line overview of the assigned
files' health. Then findings, most severe first, each as:

```
### <ID> <short title>
- Severity: P0 | P1 | P2 | P3
- Kind: bug | false-pass-risk | security | time | tokens | gap | dead-code | design
- Where: path:line (and path:line of the other place, if duplication)
- What: plain-language description, 2-6 sentences. What happens, when, why it matters.
- Evidence: the specific lines/conditions, and how you checked (read / grepped callers / ran X).
- Fix: the smallest sensible change, 1-3 sentences.
- Confidence: confirmed | likely | speculative
```

Severity: **P0** false PASS / wrong outcome reachable on real pages, a
security hole, data loss. **P1** crash, hang, wrong result or wrong
NEEDS_REVIEW in plausible conditions; large waste (tens of seconds per run or
thousands of tokens per call). **P2** moderate waste, a gap that is
NEEDS_REVIEW-safe, fragile code. **P3** cleanup, dead code, small design debt.

IDs use the prefix given in your prompt (e.g. `A-01`). Aim for signal: 15
real findings beat 60 guesses. Put anything you could not verify under a
final "Unverified leads" heading, one line each.

Your final chat message back must be SHORT (under 200 words): the output
file path, counts by severity, and the three most important findings in one
line each. Everything else goes in the file.
