# Demo script (5 minutes)

The recorded demo for slide 9. One screen, split: **Claude Code** on the
left (what a user sees), **TOBI's live log** on the right (what the server
receives, sends back and does). The scan takes about 11 minutes; the video
speeds through it.

Agent-assisted results, never a certified Trusted Tester result: say so on
camera at least once, and never call the page certified, compliant or
conformant.

## The page

**https://www.nasa.gov/mission/artemis-iii/**, live, as a user would test it,
with two other www.nasa.gov pages for the site-wide tests.

Why this page:

- It is NASA's own page, not another agency's.
- Its FAILs are ones a certified Trusted Tester also found. The tester's
  blind SCRT file for it (round 1, 2026-11-02) fails 5.A (the search box's
  only label is its placeholder) and 9.A (no way to skip the top
  navigation). TOBI fails both on the live page today (dry run below).
- It has the one failure TOBI found that the tester missed (4.D: the
  YouTube player's "Hide player controls" button shows no focus; Abby
  confirmed it after the reveal). Today's run does not FAIL it: the focus
  ring is near black on black, the rubric calls a faint ring "unsure", and
  it goes to a person. That is the story of the tool in one row.

**Say plainly:** www.nasa.gov was round 1's site, so it is a development
site: we fixed the tool with it. This is a demonstration, not a blind result.

## Before recording

1. **VAST.** The server needs sign-in working end to end (roadmap 12b) and,
   for the live log, the cluster admins set `LIVE_LOG: "true"` in the
   ConfigMap, `LIVE_LOG_TOKEN` in `tobi508-secrets`, and restart
   ([guide, "Live log"](../how-to/deploy-on-vast.md)). After the demo, set
   it back to `"false"` and restart (the restart also clears the log).
   GSA asks to see an MCP server, so the demo uses the hosted server on
   VAST only, never a local one. If sign-in on VAST is not working in time,
   that is the blocker to fix (roadmap 12b). The server's browser is
   headless there, so the live log is how the audience sees what it does.
2. **Open the live log** at `https://<app host>/live#token=<token>`. Clear
   view. Leave Requests, Responses and Progress on; turn **Run steps** off
   for the recording if it is too busy (turn it on for one shot during the
   scan).
3. **Claude Code**, signed in to TOBI (`/mcp` shows it connected), in an
   empty folder (`demo-output/`), large font.
4. **The viewer**: `https://<app host>/viewer` (TOBI serves it; the files
   you load stay in your browser) opened in a browser tab, and the
   tester's file ready to load:
   `evals/judging/round1/keys/www.nasa.gov_mission_artemis-iii_2026-11-02.json`.
5. **Dry run the morning of the recording** (the page is live and changes).
   Check 5.A and 9.A still FAIL. If either does not, say what you see, and
   do not show the tester comparison as agreement.

## The script

Times are for the edited video. **On screen** is what to show; **Say** is
the voice-over.

### 0:00–0:25 What this is

**On screen:** the split screen, Claude Code empty, the live log empty.

**Say:** "Scanners read a page's code. They can't tell you whether a
keyboard user can actually get through it: a trap, focus you can't see, no
way to skip the menu. The Trusted Tester process tests that by hand, and
there aren't enough testers. TOBI is an MCP server that follows that
process in a real Chrome browser, so the clear failures surface early and
certified testers spend their time on the hard calls. Its results are
agent-assisted, never a certified Trusted Tester result."

### 0:25–0:50 Ask in plain words

**Type in Claude Code:**

> Use TOBI to run the Trusted Tester tests it can on
> https://www.nasa.gov/mission/artemis-iii/. Compare it with
> https://www.nasa.gov/careers/ and https://www.nasa.gov/gallery/ksc-history/
> for the site-wide tests.

**On screen:** the live log's **→ request** row for `tobi_run_tt_tests`:
the URL and `other_pages`. Then, at 45 s, the first **← response**:
`status: running`, and Claude Code saying the progress line.

**Say:** "That's the whole request: a URL and two other pages of the same
site. The server only goes to .gov and .mil addresses, checked on every
redirect. It records the page once, and every key press after that goes to
the recording, not the live site, so a run can be repeated."

### 0:50–1:20 Fast forward (about 11 minutes, sped up)

**On screen:** speed up. Caption: "11 minutes, sped up". Let the progress
lines scroll on the right: "Walking the page with Tab and Shift+Tab",
"Opening menus and expandable sections", "Checking which hidden fields can
ever be shown", "Checking 9.A", "Checking 19.A". Show **Run steps** on for
a few seconds (`walk`: 82 presses each way, ending where it started).

**Say:** "It presses Tab and Shift+Tab through the whole page, the way a
tester does, and reads where focus is from Chrome itself, so a page can't
fake it. It opens menus and tabs, watches for moving and flashing content,
and compares the page with the other two. Each test's outcome comes from a
rules file, one per Trusted Tester test, written from the DHS procedure."

### 1:20–2:10 The result, and the questions only judgment can answer

**On screen:** the long **← response** in the live log. Point at the
outcome chips (5.A FAIL, 9.A FAIL, and many NEEDS_REVIEW), then scroll to
the pictures attached for the open questions. Stop on the 4.D pair: the
"Hide player controls" button without and with focus. Then Claude Code
answering the open questions (`tobi_answer_questions` in the log).

**Say:** "Two clear failures, both ones a certified tester found on this
page: the search box's only label is grey text that disappears when you
type, and there's no way to skip the navigation. Most rows say needs
review. That's on purpose: when a rule can't decide, it says so; it never
guesses a pass."

"Some rules ask a question only judgment can answer, like 'can a sighted
user see where focus is?' The agent gets the pictures and a rubric. This is
the YouTube player's hide-controls button: with focus, a thin navy ring
on black. Our tester confirmed it fails. The rubric says a faint ring
is 'unsure', so it goes to a person instead of being decided by a model.
And the server refuses an answer to a picture question unless the agent
says what it saw."

*If the agent answers "no" on 4.D in your recording, 4.D becomes FAIL:
say "it agrees with the tester", not that the tool proved it.*

### 2:10–3:10 Explain the results and the limits

**Type:**

> Explain what failed and how to fix it, what's left for a person and why,
> and what TOBI can't check on this page.

**On screen:** `tobi_explain` with the `run_id` in the live log; Claude
Code's answer. Keep the part on limits on screen.

**Say:** "Every result is explained in plain language from the rules, with
where to find it on the page and how to fix it. The limits matter as much:
TOBI runs 22 of the 61 Trusted Tester tests; the other 39 come back as
'this test could not be performed'. On this page it couldn't fully check
the embedded video for flashing or every image for movement, so those go
to a person, and some menus it opened held controls the Tab key didn't
reach."

### 3:10–4:20 The file a tester can use, beside the tester's own

**Type:**

> Save the pre-SCRT file and the full report into this folder.

**On screen:** the `resources/read` rows in the live log, the two files in
Claude Code. Switch to the viewer tab (served by TOBI at `/viewer`): load the
pre-SCRT file Claude Code saved. Show the
banner (agent-assisted, not a Trusted Tester's record), the counts, then
**Only needs review**. Then **Compare with** the tester's SCRT file and
**Only tests whose results differ**.

**Say:** "The pre-SCRT file has the same rows as DHS's report tool, and
says where each result came from and which rows need a person. It is not a
Trusted Tester's record and SCRT won't open it, by design. Here it is
beside our certified tester's blind file for the same page, from November:
the two failures match, and most differences
are rows TOBI hands to a person. The tester's file says 4.D passes: that
is the one the tester missed and later confirmed as a failure."

*In the dry run, 12 of 63 rows differed: 5.A and 9.A showed "Same
result"; the rest were mostly NEEDS REVIEW against the tester's Pass.*

### 4:20–5:00 Close

**On screen:** the evaluation numbers (slide 11, or the README status
table), then the disclaimer.

**Say:** "We score every change against certified testers' blind answers.
On our latest development rerun of 19 NASA pages, TOBI gave no pass and no
'does not apply' where the tester found a failure (the blind round before
those fixes had three). When it is wrong, it fails pages a tester passes or
leaves them for a person, which costs time, not access. Next: the page where a person
answers its questions, and more of the 61 tests. Agent-assisted findings,
never a certified Trusted Tester result."

## Dry run, 2026-11-18

The live page, the script's first call made in-process (not through
Claude Code, not on VAST), headless Chromium in a cloud container, the
client judge.
Agent-assisted findings, not a certified Trusted Tester result.

- **Time:** 10 min 31 s to the result; then 10 open questions and 1 more.
- **Before answers:** FAIL 5.A, 9.A; PASS 4.B, 9.B, 19.A; DOES NOT APPLY
  2.A, 5.H; NEEDS REVIEW the rest (4.A, 4.D, 4.F, 5.B and 9.C waiting on
  answers; 3.A could not play the embedded video, 2.B could not check one
  of 40 images, 2.C and 2.D could not be performed; 4.C, 4.E and 5.D did
  not reach every control in the menus it opened; 5.F and 5.G found 4
  fields hidden until something opens them).
- **Open questions:** Claude Code answers them in the recording, from the
  pictures and rubrics in the result. 4.D's pictures show a near-black ring
  on black: expect "unsure", so it stays for a person.
- **The 9.A summary has a lowercase sentence start** ("…skip past it. the
  "Explore" button did not…"): a wording fix after the freeze, not for the
  demo.
- **The viewer** (checked): this run's pre-SCRT file beside the tester's
  file: 5.A and 9.A "Same result", 12 of 63 rows differ.
- **Not checked:** through Claude Code against VAST with sign-in; the live
  log on VAST (checked on loopback HTTP with a local test
  page: requests, responses with pictures, progress and steps).
