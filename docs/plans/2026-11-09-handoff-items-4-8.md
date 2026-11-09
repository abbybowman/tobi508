# Handoff: items 4-8 of bundles 1 and 2 (2026-11-09, second thread)

For a fresh session. It continues
[2026-11-09-handoff-bundles-1-2.md](2026-11-09-handoff-bundles-1-2.md) (read
it first: how to build each item, the token rule, when to stop and ask).
Abby (repository owner, tester, decision maker) reviews each pull request.
Agent-assisted results, not certified Trusted Tester results.

## Read first, in this order

1. `CLAUDE.md` (principles are non-negotiable; principle 5 now has a fourth
   approved exception, the chunk store).
2. The first handoff, then this file.
3. `docs/plans/2026-11-08-rules-principle3-build.md`: **"Status"** and
   **"Step 1 findings"** at the top (what is built and verified), then the
   builder notes for the item you take.
4. `docs/plans/2026-11-08-apijudge-build.md`: Status and builder note 4
   (item 6).
5. `docs/solutions/` README, then `recordings-miss-lazy-scripts.md`,
   `listeners-from-the-main-world.md`, `apijudge.md`.

## What is done (pull requests)

| # | What | State |
| --- | --- | --- |
| 31 | Step 1: findings from round 2's frozen pages; plan docs | merged |
| 32 | Fix 6: 9.A-9.C other templates (specs 9.A, 9.B 1.1.0; 9.C 1.2.0) | merged |
| 33 | ApiJudge: module, wiring, dry mode, tests (off by default) | merged |
| 34 | Chunk store and guard GU (ten specs +1 MINOR) and 4.C 1.11.0 (fix 2: M4 modal only, M4d, M4o, frame sections) | open, for Abby's review (CodeQL threads answered) |

Full suite on #34's head before the last two small commits: 1122 passed,
3 skipped, 1 xfailed (about 16 minutes with `-n 6`). The last commits
(middle option for 4.C, CodeQL fixes) ran the 4.C, ACT, Baseline and
chunk tests only (all passing after the f36 expectation moved); run the
full suite before you start building on it.

Branch `videos-3a-4a` exists locally from `fix2-4c-exit` with no commits;
start item 4 from `main` once #34 is merged (or from `fix2-4c-exit`).

## Decisions made this session (Abby, 2026-11-09)

- **A:** an exit that needs Enter (or another activation) on a control
  inside a keyboard trap is not an exit unless the page says explicitly how
  to leave. **Middle option for 4.C:** only a modal dialog passes on Enter
  (M4); a non-modal banner or section that Enter closes is NEEDS REVIEW
  (M4d); any other activation exit is not an exit (M4o).
- **Chunk store and guard GU approved**, a fourth exception to principle 5
  (page code names scripts the recorder fetches: limits in `capture.py` and
  CLAUDE.md). The guard moves a would-be PASS of 4.A-4.F, 5.D, 5.F-5.H to
  NEEDS REVIEW while the recording lacks code the page loads when used.
- **Agreed readings** (fix 6): "navigation of its own" = a banner,
  navigation, search or contentinfo region, or 4+ links outside `main`;
  "shares almost nothing" = no region with the same label or id and one unit
  or under 4 words in common.
- Decisions 1-3 of the bundle 2 plan stand (5.C asks one question per set of
  same-named buttons; the year popup is a trap if the keyboard cannot get
  back; 9.A with no matching pages is NEEDS REVIEW).

## What changed that you must know

- **5340's two FAILs (popup trap, 5.D focus jump) were hidden by the
  recording**, not the browser: the app loads a script on first use that
  the recording never held (verified in Chromium and Firefox). Fix 5
  (5.D tab-away) and item 8's popup trap can no longer be checked on the
  frozen 5340 recording (it still lacks the chunk: the guard turns those
  cells into NEEDS REVIEW). Test them on custom pages. A live re-recording
  of 5340 with the store was **not** done.
- **Spec versions are one MINOR higher than the bundle 2 plan lists** for
  4.A, 4.B, 4.D, 4.E, 4.F, 5.D, 5.F, 5.G, 5.H (guard GU), and 4.C is at
  1.11.0 (the plan's list is updated in its "Spec versions" paragraph).
  Never edit `evals/judging/round2*/`.
- **CILab 4.A (item 4, fix 4):** the guess about `hit()` was wrong. CDP
  lists listeners from the isolated world as none; from the page's own world
  it lists the page's (21 on CILab, including the row's jQuery click).
  Fix 4 starts with reading listeners from the main world
  (`traverse.Reader.listeners`, `t4a._own_listener_types`, `_mark_listeners`:
  `Runtime.evaluate` with no `contextId`, `DOMDebugger.getEventListeners`
  with depth -1). Delegated handlers on an ancestor are still not tied to
  their child: decide how when building.
- The frozen pages (round 2) are not in git. Abby re-attaches
  `round2-frozen` parts if the container is new; restore as
  `evals/judging/round2/results/ARCHIVE.md` says and check the manifest.
- **How to run things:** never edit files while a background pytest runs
  (workers read the tree; I had to kill and rerun twice). The test server
  serves only `.html` and `.js` files inside `tests/fixtures/`. To probe a
  recording: Playwright `route_from_har` on `pages/NNN.har.zip`
  (`008` is 5340, `005` CILab, `006` 14592, `009` 5144, `010` 4914). Playwright
  Firefox can be downloaded into a scratch folder
  (`PLAYWRIGHT_BROWSERS_PATH=<scratch> uv run playwright install firefox`, no
  system packages) for browser comparisons; TOBI itself is Chromium-only.

## Order of work (one pull request per item, from `main`)

| # | Item | Plan | Model calls |
| --- | --- | --- | --- |
| 4 | **Videos: fixes 1 (3.A) and 4 (4.A)**, with the main-world listener fix first. **Built, branch `videos-3a-4a` (status in the bundle 2 plan)** | bundle 2 | judge eval for 4.A only (done: 8 of 8) |
| 5' | **Fix 5: 5.D waits after Tab-away** (custom pages only: immediate jump, 500 ms jump, re-render on change, a jump inside a same-site frame). **Built on `videos-3a-4a` (PR #35)** | bundle 2 | none |
| 6 | ApiJudge gate scripts and trick-text pages, built and tried on 2 pages only | bundle 1 note 4 | a small CLI trial |
| 7 | Opening everything, phase 1 (fix 9b) | bundle 2 | judge eval for 5.A-5.C |
| 8 | Error values (fix 3), top-level forms only | bundle 2 | judge eval for 5.F, 4.C |

Item 4's notes: 3.A makes every `<video>` a trigger (`t3a.triggers`
takes only played ones; a click-to-play strobe must be NOT TESTED, an
unplayed missing file NEEDS REVIEW, an unplayed 3 s grey clip DNA; fix the
wrong "it streams its video" reason for an empty `currentSrc`; try other
`<source>` on a failed decode; hidden videos count). 4.A: a new term
*media start* (`paused` true to false after an action, an effect for 4.A
only), pages in `tests/fixtures/4a/`; leave 14592's `<video controls>`
question alone. Spec versions then: 3.A 1.0.0 to 1.1.0; 4.A 1.3.0 to 1.4.0
(then 9b 1.5.0). Hackathon `evaluation.md` and its deck slide in the same
commit as each spec version.

## Not built, from the ApiJudge plan (item 5, done)

Judging the questions an agent's answers raise inside
`tobi_answer_questions` (a job); a separate test of the 19.A follow-up path;
the gate scripts (item 6); a real model call and token measurement.

## Open for Abby

- Whether a Firefox replay (or any second browser) matters for the pitch, or
  a documented limit is enough (TOBI records its browser in the report and
  the SCRT).
- 9.A is a candidate for guard GU (it presses Enter on skip links).
- Keep the plans' Status sections current after each item (one line per item,
  verified vs assumed).

## Done means

Each item merged or in review with its status line in the plans, the full
suite passing, and the plans saying plainly what is built, what is tested on
which pages and what is left.
