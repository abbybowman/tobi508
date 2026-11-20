# How TOBI is built

A map of the code for a first-time reader. The rules for working on it are
in [CLAUDE.md](../CLAUDE.md); what each test decides is in
[specs/rules/](../specs/rules/).

## One call, end to end

1. **An MCP tool is called** (`tools/run_tt_tests.py`). Inputs are Pydantic
   models (`models.py`); the URL is checked against the allowlist
   (`policy.py`, `browser.NavigationGuard`) before anything loads.
2. **The page is recorded once** (`capture.py`) in a fresh Chrome context
   (`browser.py`). Every browser connection goes through a local proxy that
   refuses private and cloud-metadata addresses (`egress.py`). Every later
   step replays this recording, never the live page.
3. **Shared evidence is collected once:** the page's inventory (`count.py`),
   the keyboard walk, Tab and Shift+Tab (`walk.py`, `traverse.py`), menus and
   panels opened (`reveal.py`), a watch for motion and sound (`motion.py`;
   what it records is in `motion_models.py`),
   form fields (`forms.py`), labels through ANDI (`labels.py`, `andi.py`),
   and other pages of the same site (`site.py`).
4. **Each test's check decides** (`checks/t<id>.py`, one per Trusted Tester
   test, e.g. `checks/t4c.py` for 4.C No keyboard trap). It applies the rows
   of its rules spec, first match wins (`engine.py`). Outcome logic lives
   only here and in the spec.
5. **Open questions go to a judge** (`judgment.py`): the server's own pinned
   model (`apijudge.py`, prompt in `judge_prompt.md`) when one is configured,
   otherwise, or when that model cannot be reached, the calling agent through
   `tobi_answer_questions`. Answers are
   facts for a rule, never outcomes; the check decides again.
6. **The result is written** (`pipeline.py` orchestrates steps 2 to 6): a
   short tool result (one line per finding, the questions, pictures attached
   by `inline.py`), the full report as a `run://` resource (`resources/`),
   and a pre-SCRT file in DHS's report rows (`scrt.py`). A run longer than
   one call continues as a job (`jobs.py`).

## Where things live

| Area | Files |
| --- | --- |
| MCP surface | `app.py` (server), `tools/` (one file per tool), `resources/`, `prompts/`, `routes.py` (HTTP-only routes) |
| Inputs, outputs, settings | `models.py`, `config.py` |
| Browser and safety | `browser.py`, `policy.py`, `egress.py`, `capture.py`, `redact.py`, `access.py` (hosted sign-in) |
| Evidence collectors | `walk.py`, `traverse.py`, `observe.py`, `reveal.py`, `count.py`, `motion.py` (pass T, the watch; its page script in `motion_init.js`), `motion_models.py` (what pass T records), `motion_media.py` (sound and animated images decoded from the recording), `motion_pictures.py` (crops and states of moving regions), `mechanism.py`, `flash.py`, `flashcap.py`, `forms.py`, `labels.py`, `andi.py`, `site.py`, `hidden.py`, `jslib.py` |
| Decisions | `checks/` (one module per test), `engine.py` (rule tables), `rules.py` (loads specs), `catalog.py` (the Trusted Tester text) |
| Judging | `judgment.py`, `apijudge.py`, `judge_prompt.md` |
| Output | `pipeline.py`, `scrt.py`, `compare.py`, `explain.py`, `inline.py`, `runlog.py`, `versions.py` |
| Runs and hosting | `jobs.py` (runs longer than one call), `progress.py` (its progress line: reading steps, then tests, done of total), `pagecache.py` (other pages recorded once a session), `frozen.py` (recorded pages for evaluations), `livelog.py` and `livepage.py` (a demo log, off by default) |

Outside `src/tobi508/`: `specs/rules/` (one versioned rules spec per test,
citing the Trusted Tester PDF in `specs/sources/`), `tests/` (unit tests and
fixture pages, including vendored W3C ACT and Section 508 Baseline cases),
`evals/` (the judge eval, the agent eval and the scored rounds against a
certified tester's blind reports), `third_party/` (ANDI, jQuery and SCRT,
pinned by hash).

## Adding a Trusted Tester test

Follow the steps at the top of
[`checks/base.py`](../src/tobi508/checks/base.py): research, a draft spec,
fixtures, the check, a judge eval, then version 1.0.0. The tools, the
report and the description need no changes: the new test is listed from
the registry.
