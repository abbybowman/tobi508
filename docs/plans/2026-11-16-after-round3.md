# Plan: what round 3 showed, and what to do about it (step 10c)

Round 3 was a blind judging round on science.data.nasa.gov (10 pages,
keyed by Abby 2026-11-14, frozen 2026-11-16, locked at `eb45b07`,
scored 2026-11-16: [`score.md`](../../evals/judging/round3/score.md)).
The tool had never been developed on this site. Pages p01 to p06 are a
Drupal site drawn by the server; p07 and p08 (the Data Governance
Community) and p09 and p10 (the Science Discovery Engine) are
applications built with a script framework (Angular: `app-root`,
custom element tags), drawn in the browser after load.

**Round 3's pages are development pages from now on.** A later run on
them is a rerun that shows what a change did. It never replaces this
score, which stays the blind result.

What is scheduled when is in [the roadmap](../ROADMAP.md): two threads
before the cut ("Now", A and B) and five bundles after the demo
("Next", R1 to R5), holding steps 21 to 35. Each thread's prompt is in
[the handoff file](../reviews/2026-11-11-code-review-fixing.md).

**Names.** `docs/ROADMAP.md` names the work by step number only. Where
this plan says "thread A", "thread B" or "bundles R1 to R5", read the
rows of the roadmap's "Order of work" and "Next" tables: A is steps 21,
36, 22 and 23; B is steps 31 and 29's small part; R1 to R5 are the
rows Applications, 4.D and 5.D on what opens, 4.A and 4.F, Forms, and
Site tests. Cause numbers are this plan's own.

## Questions for Abby

1. **Native validation in 5.F (and 5.G).** The contact form has no
   error messages of its own; the browser's bubble is the only one, it
   shows one field at a time and its words differ by browser. TT does
   not ask a tester to tell the browser's message from the page's.
   Should TT 5.F (and 5.G) FAIL such a form, PASS it, or leave it to a
   person? Until you decide, step 21 makes it NEEDS REVIEW (cause 1).
2. **MySearchStory 5.A, 5.B, 5.D (key Pass).** The tool found only
   buttons there. If the page has no data-entry field, your 2026-11-04
   decision ("buttons alone are not a form") makes 5.A and 5.D DOES NOT
   APPLY. Which field did you judge? (cause 16)
3. **The search page's 19.A (key Pass by "content links").** The home
   page's topic tags lead to other queries of the results page, not to
   `?rendered_item=test&sort_by=rel`. Is a results page one page
   whatever its query? (cause 13)
4. **The home page's and blog's 19.A (key Pass by "breadcrumbs").** The
   spec counts a breadcrumb as a navigation link, the same kind as the
   menus. Is a breadcrumb on a child page a way of its own? (cause 13)

## How the work is cut (Abby, 2026-11-16)

The ranking below stands; the work is cut into seven threads.

- **Before the cut (Nov 17), two threads, at once:**
  - **Thread A:** step 21, then step 22, then a time-boxed step 23
    (wait for the page to draw), which starts with a probe and no code
    and stops at midday on Nov 17 if not merged; 21 and 22 never wait
    on it.
  - **Thread B:** step 31 (9.B), then only the small part of step 29
    (5.B is NEEDS REVIEW, not DOES NOT APPLY, when 5.A could not
    decide).
  - Each reruns its tests on all three rounds' frozen pages and shows
    every moved cell beside the key.
- **After the demo, five bundles, one thread at a time each; no two
  share a test.** Inside a bundle, a wrong outcome or a cell one step
  from unsafe comes before turning NEEDS REVIEW into answers.
  - **R1, applications:** step 23 if thread A did not finish it, 24,
    25, 26, 35a (controls with no `<form>`) and 35e (4.C: a search
    button that shows results at another address, on SDE home; your
    list left 35e out, and R1 is the bundle that already touches 4.C's
    walk).
  - **R2, 4.D and 5.D on what opens:** 27, then step 15's 4.D and 5.D
    part.
  - **R3, 4.A and 4.F:** 28, 32, 33.
  - **R4, forms:** the rest of 29, 30, and 35b to 35d (5.D, 5.C, 5.B).
  - **R5, site tests:** 34 (with CILab), and 9.C by function (roadmap
    19b).
  - **Two overlaps to keep apart by order:** R1's step 26 changes A2
    of 9.A to 9.C and 19.A, which R5 also changes, so R5 starts after
    R1 has merged 26; R4's 35b changes 5.D, which R2 also changes, so
    R4 starts after R2 has merged.

## What it showed, in short

- **149 of 220 cells decided, 118 agree; 3 unsafe cells.** Two PASS
  where the key fails (5.F and 5.G on the contact page: the browser's
  own error messages) and one DOES NOT APPLY where it fails (4.F on the
  forum page: the tool read the page before the application drew it).
- **The applications (p07 to p10) are where the tool was not built.**
  They hold 41 of the 102 wrong or undecided cells. Four things about
  them the tool did not expect: the page draws itself a second or more
  after load, so the keyboard walk and the readers saw an almost empty
  page (cause 2); every address serves the same document, so another
  page's recording is byte for byte the tested page's and 9.A to 9.C
  and 19.A were not performed (cause 5); the address changes on its own
  while the app starts, which 4.E read as caused by focus (cause 14);
  and there is no `<form>` element, so header buttons were grouped with
  the search field (cause 15). The sign-in check (an OpenID Connect
  frame whose address changes on every load) and two code chunks were
  not in the recording (causes 2 and 17).
- **One rule gave 6 of the 18 false FAILs:** 9.B pairs links of the
  same name and address in order, and the home page has one "Home"
  fewer (no breadcrumb), so the pairs cross (cause 10).
- **Two PASS results hide inside cells held at NEEDS REVIEW** where the
  key fails: 4.D passed the blog page's image links on a faint change
  (guard RC held the cell; cause 3), and 4.A on MySearchStory is one
  judge answer away from a PASS the key fails (cause 4).
- **Most of the 71 undecided cells are known limits** seen in rounds 1
  and 2 as well: guard RC (opened content 4.D and 5.D do not walk yet),
  2.C's timers, 4.A's undecidable signals, forms that cannot be sent
  from a recording, 19.A's site search.

## Verified and assumed

- **Verified by reading the reports:** every cell's outcome, rows,
  sentence and the key's comment (the table at the end, generated from
  the reports and keys with the scorer's own comparison, `evals.scoring`
  on `tobi508.compare`, 102 cells: 31 wrong, 71 left for a person).
  The judge's questions and answers quoted below are from the reports'
  `questions` and `answers`.
- **Verified by a run (2026-11-16, scratch pages, not committed):**
  - a page that draws its controls 1.2 s after load gives 4.F DOES NOT
    APPLY (A3, "only one element"), 5.A and 5.D DOES NOT APPLY ("no
    form fields"), and 4.A and 4.C PASS on the one link there at
    first (cause 2);
  - two pages whose repeated links sit in no landmark, one with an
    extra breadcrumb "Home", give 9.B FAIL (N3) on the social links;
    with the same links in distinct landmarks it gives PASS (cause 10);
  - fixture `5f/f01-native-validation` gives 5.F PASS (M2) and 5.G
    PASS (J1 "guides" on Chrome's message), as its test expects
    (`tests/test_fixtures_5f.py -k f01`, passed) (cause 1).
- **Read from the reports, not run:** the walk's press cap of 50 on
  p07 and p08 means the inventory held no focusable element when the
  walk began (`traverse.py`: cap = 3 x inventory + 50); 4.E counted 76
  and 90 elements later. That the sign-in frame is what moves the
  app's address is **assumed**: the reports do not record where the
  address went, and the frozen archive's `steps.jsonl` would show it.
- **Not shown by the reports:** what sits beside the forum's search
  combobox (5.A on p07, p08; the pictures are in the run folders, not
  in `results/`), whether MySearchStory has a data-entry field (cause
  16), which element 4.A's execute row x1 on p10 pressed, and why
  19.A on CILab FAILed in step 6g's rerun.

## The causes, ranked

Unsafe first: a PASS or DOES NOT APPLY where the key fails. Causes 3
and 4 come next although no scored cell is wrong yet: each holds a key
Fail cell that only a guard or one judge answer keeps from a PASS, and
the PASS is already in the instance rows. The rest by cells.

| Rank | Cause | Cells (unsafe) | Kind | Rounds 1 and 2 | Smallest fix, size | Needs approval | Step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | The browser's own error messages: 5.F reads Chrome's message for every field as shown; 5.G judges Chrome's wording | 2 (2 PASS) | rule, browser | not decided before (5.F and 5.G were DNA or NR there) | 5.F M2 and 5.G J1 on a native message become NEEDS REVIEW; S | no (PASS to NR); FAIL instead is Abby's call | 21, before the cut |
| 2 | The walk and readers read an application before it drew itself | 12 (1 DNA) | reading (recording assumed) | new | a reading whose page grew after it is incomplete: no DNA, no PASS, no FAIL from "not reached"; S-M. Then wait for the page to draw; M | no (DNA and FAIL to NR) | 22 before the cut; 23 |
| 3 | 4.D passes a faint mark on a large linked image (12 px² is absolute) | 1 (key Fail held by guard RC) | rule | not in the gate rows | M6 also needs the change to be a share of the element's size, else J1; M | no (PASS to J1) | 27, before step 15's 4.D part |
| 4 | 4.A: J1 "alternative" while its reasons say "not certain"; Enter's effect not compared with the click's | 1 (key Fail, one answer from PASS) | judge, rule | not in the gate rows | an "alternative" whose reasons hedge is unsure; M8 needs the key's effect to match the click's; M | no | 28 |
| 5 | One document for every address read as the same page (K-01) | 16 | rule/reading | new | the byte test only for the same path apart from the query; S, after step 23 | yes (NR to outcomes) | 26 |
| 6 | The site search sits in a panel the magnifier opens; 5.B says DNA when 5.A could not decide | 10 | reading, rule | partly: round 1's keys and round 2's fix 8b | 5.B A2 only when 5.A found no label (S); open the panel before the picture (with step 15); M | the icon as a label: yes | 29 |
| 7 | Guard RC: 4.D and 5.D do not walk what opens; 4.E on an arrow-key dropdown | 10 | reading (known) | same in both | step 15 as planned | as step 15 | 15 |
| 8 | 2.C and 2.D: timers longer than the watch | 8 | reading (known) | same (round 2: all 10) | part J, as planned | | Later |
| 9 | 5.F to 5.H on forms the tool cannot send (filters, a GET search, a file field) | 7 | rule question | same in both | a spec decision first: a form with nothing to get wrong; M | yes (NR to DNA) | 30 |
| 10 | 9.B pairs equal links in order; one page has one "Home" fewer | 6 | rule | new (both 9/9 and 9/10 agree) | pair equal links by an order-keeping alignment; S | no | 31 |
| 11 | 4.A's three undecided signals on every Drupal page | 6 | reading | likely the same (NR on 8 of 9 and 7 of 10) | hidden frames and page-level listeners are not U; calibrate the hover cap; M | yes (NR to PASS) | 32 |
| 12 | 4.F: J1 over-strict; footer columns and dropdowns raise signals; the order list misses what the signals name | 4 | judge, rule, reading | same (round 2's two 4.F false FAILs) | rubric and judge eval; S3 and S6 exceptions; M | S3/S6: yes | 33 |
| 13 | 19.A: search results not loading; breadcrumbs counted as navigation; a results page's address | 4 | reading (known), rule question | search and menus the same | questions for Abby first; CILab's FAIL found | yes | 34 |
| 14 | 4.E: the app's own address change read as caused by focus | 3 | reading | new | the control replay waits as long after load as the original step; S-M | no | 24 |
| 15 | No `<form>` in an app: header buttons join the search field; "SDESDE" against "SDE" | 3 | reading | new | form "none" leaves banner and navigation buttons out; M5 compares without spaces too; S | yes (NR to PASS) | 35 |
| 16 | MySearchStory: no data-entry field found; the key passes 5.A, 5.B, 5.D | 3 | key or reading: not shown | | a question for Abby | | none |
| 17 | Two code chunks not in the frozen recording (guard GU) | 2 | recording | round 2's 5340 had GU | the freeze saves the chunk store; S | no | 25 |
| 18 | 5.D: the filter's request not recorded; focus to the field's own label read as a move | 1 | recording, reading | round 1 p01 5.D false FAIL, cause not in the gate rows | focus onto the field's own label or wrapper is not a move; an action the recording cannot answer is NR; S | no | 35 |
| 19 | 5.C: an event card's own words read as a missing cue | 1 | judge | no | rubric and judge eval; S | no | 35 |
| 20 | 5.B: a checkbox's label not read; J1 answered without seeing it | 1 | reading, judge | no | read a visually hidden checkbox's `label[for]`; "not visible" means unsure; S | no | 35 |
| 21 | 4.C: a search button that shows results counts as an unfinished error state | 1 | rule | no | a press that navigates leaves no error state; S | yes (NR to PASS) | 35 |

**Before the Nov 17 cut:** steps 21 and 22 are small and only move
PASS, DOES NOT APPLY and FAIL to NEEDS REVIEW, so neither needs
approval and neither can add a wrong PASS. Step 31 (9.B) is small too
and removes six false FAILs no key confirms. Abby's cut (above): 21,
22 and a time-boxed 23 in thread A; 31 and 29's small part in thread
B. Everything else is after the demo, in five bundles.

## The causes

### 1. The browser's own error messages (5.F and 5.G, contact page)

**Cells:** 5.F and 5.G on p03, PASS where the key fails.

**What the tool did.** The contact form uses the browser's own
validation (`required`, `type=email`). In Chromium the tool left the
four fields empty and sent the form, then read each field's
`validationMessage` ("Please fill out this field.") and counted all
four as errors the page identified and explained (5.F row M2: "the
browser identifies the field by focusing it and describes the error in
text", from Understanding 3.3.1). It typed `test@` into the email
field and Chromium's message was "Please enter a part following '@'.
'test@' is incomplete."; J1 called that guidance (5.G N4).

**What the tester did.** In Firefox 147, sending the form shows one
bubble, under the first field in error only, saying "Please fill out
this field", which does not name the field in text; a short string
without `@` gives "Please enter an email address", which says nothing
about how to fix it.

**Kind.** The rule and the browser. 5.F's M2 follows Understanding
3.3.1, which says native validation "meets the requirements"; the key
reads the TT text ("the item in error is identified ... in text") and
counts that the user sees one error at a time. The tool also reads
messages the user does not see: the browser shows only the first
invalid field's bubble, and the tool counted every field's. 5.G's
outcome depends on the browser: Chromium's message guides, Firefox's
does not, and the page's author controls neither.

**Is the key wrong?** No. 5.G is right for the browser it was tested
in. 5.F is a defensible TT reading that differs from the W3C
Understanding text; that is a decision for Abby, and until she makes
it the tool should not PASS what a Trusted Tester fails.

**Rounds 1 and 2.** Not decided before: in the latest reruns their
5.F and 5.G cells are DOES NOT APPLY or NEEDS REVIEW. Round 2's 5340
(key Pass: "an error popup appears beneath the field") is NEEDS
REVIEW. Round 1's NSSC form (key Pass for 5.G: "guidance on proper
email formatting") is NEEDS REVIEW; whether its message was the
browser's is not recorded. Fixture `5f/f01` has asserted PASS since
5.F 1.0.0.

**Smallest fix (step 21).** 5.F M2 and 5.G N4 on a native message:
NEEDS REVIEW, with a sentence that the message is the browser's,
differs by browser and shows one field at a time. Fixture `5f/f01`
moves from PASS to NEEDS REVIEW; `f15` (the page cancels the browser's
message: M3 FAIL) and the custom-message fixtures (f03, f04) keep
their outcomes. Size S: two spec rows, two MINOR versions, the
fixture's expectation, the hackathon evaluation line. PASS to NEEDS
REVIEW: no approval needed. If Abby decides native validation fails
TT 5.F (or 5.G), that is a later MINOR change to FAIL.

### 2. The walk and readers read an application before it drew itself

**Cells (12):** 4.F on p08, DOES NOT APPLY where the key fails; 4.F on
p07 and 5.D on p07 and p08, DOES NOT APPLY where the key passes; 4.A
on p07 and p08, FAIL where it passes; 4.C, 4.D and 5.H on p07 and p08,
left for a person. Also agreeing by luck: 5.F and 5.G on p07 and p08
are DOES NOT APPLY by row A1, "no form fields", on pages with search
boxes (the key says DOES NOT APPLY for another reason).

**What the tool did.** The forward Tab walk (P1) reached one element,
the "Data Governance Knowledge Hub" home link, and ended. The
backward walk stopped at its press cap of 50; the cap is 3 x the
inventory + 50, so the inventory held no focusable element when the
walk began. Later readers counted 76 (home) and 90 (forum) focusable
elements. From the one stop, 4.F said there is only one element (A3,
DOES NOT APPLY); 5.D said there are no form fields (A1); 4.A asked
J1 about 20 controls "the keyboard never reaches", and J1, shown one
reached stop, answered "no other keyboard way" (M6, FAIL: "Only
reached stop is a home link"); 5.H says the keyboard reached 0 of 1
and 0 of 2 fields.

**What the tester did.** Tabbed through the drawn page: the header,
the cards, the posts, the forum's tag word cloud. On the forum the
word cloud's order "seems random", so 4.F fails.

**Kind.** Reading: nothing checks that the page the walk reads is the
page a person sees, and the tests decide DOES NOT APPLY and FAIL from
a walk that covered 1 of 76 elements. The recording may add to it:
the freeze could not record the app's sign-in frame
(`auth.sciencecloud.nasa.gov/.../openid-connect/auth`, "differs
between two loads", `frozen/freeze.json`), and the address change
cause 14 describes happened on the first key presses; that the frame
is what delays or moves the app is assumed, not shown.

**Rounds 1 and 2.** New. Their pages are drawn by the server.

**Smallest fix, in two steps.**
- **Step 22 (before the cut):** a test decides from the walk only when
  the walk covered the inventory taken after it, the count 4.E and
  4.A already print ("reached 51 of 76"). 4.F's A3 needs one element
  in that inventory, not one stop; 5.D's A1 (and 5.A, 5.F to 5.H's
  "no form fields") read the late inventory; 4.A's unreached
  candidates are C? (NEEDS REVIEW) while the walk is incomplete; 4.C
  does not PASS on it. Rows: 4.F A3, 5.D A1, 4.A K rows (M4), 4.C's
  coverage guard. Fixture: a page whose controls are drawn 1.2 s after
  load (the scratch page above); nearest pages that must keep their
  outcomes: `4f/f07-one-link` (DOES NOT APPLY) and 5.D on
  `4d/f01-background-change` (no fields: DOES NOT APPLY). Size S-M. Moves DNA and FAIL to NEEDS REVIEW:
  no approval.
- **Step 23 (after the demo):** wait for the page to draw before the
  walk, pass L and the site read (the inventory unchanged over a short
  window, with a ceiling), and take P2's press cap from the inventory
  when P2 starts. This turns the NEEDS REVIEW of step 22 back into
  outcomes on these pages; measured on the frozen pages, it needs no
  approval for a rule but each cell that moves to PASS is shown to
  Abby. Size M.

### 3. 4.D passes a faint mark on a large linked image

**Cells:** 4.D on p02 (key Fail; NEEDS REVIEW only through guard RC)
and on p01 (key Pass; NEEDS REVIEW).

**What the tool did.** On the blog page each post has a title link, an
image link named "Image" and a link on the image's alt text. 4.D found
about 50 strongly changed pixels on each "Image" link with a style
signal, which passes row M6 (`MIN_CHANGED_PX` is 12 CSS px², whatever
the element's size). The cell is NEEDS REVIEW only because guard RC
holds it (opened menus not walked). On p01, ten image links are M4: an
outline style changed but the pictures did not show it.

**What the tester did.** "The keyboard focuses on the linked image as
a whole, but there is no visual indication of that focus."

**Kind.** Rule: an absolute pixel count passes a change too small to
see on a large element.

**Rounds 1 and 2.** Not in the gate rows (they keep page rows only).
New evidence.

**Smallest fix (step 27).** M6 also needs the strongly changed pixels
to be a share of the element's size (its perimeter, for example);
below it, J1 looks (M7). Fixture: a large image link whose focus
shows only a small mark; nearest pages that must keep their outcomes:
`4d/f18-small-icon-clear-ring` (PASS) and `4d/f19-small-icon-faint-ring`
(NEEDS REVIEW). Size M,
with a rerun of rounds 1 to 3's 4.D cells. PASS to J1: no approval.
It must come before step 15's 4.D part, which lifts guard RC and
would turn p02's cell into a PASS the key fails.

### 4. 4.A on MySearchStory: a hedged "alternative" and Enter's effect

**Cell:** 4.A on p10 (key Fail; NEEDS REVIEW).

**What the tool did.** Three instance rows: k1, a header `div` that a
click takes to the SDE home page, PASS by M5 because J1 answered
"alternative" naming the NASA logo link, while its reasons say "The
reached NASA link goes to nasa.gov, not the SDE home, so it is not the
same ... Not certain."; k2, the breadcrumb "Home", unsure (M7); x1, a
custom control where Enter or Space "has an effect", PASS by M8. The
cell is NEEDS REVIEW because of k2 alone.

**What the tester did.** Could not reach "Search Stories" in the top
navigation or the breadcrumb links; "Submit Your Story" and "SEARCH"
can be reached but Enter and Space only advance the carousel.

**Kind.** Judge (an answer that contradicts its own reasons) and rule
(M8 passes any effect of a key, even one that is not what the click
does; native buttons are never executed). "Search Stories" is not
among the candidates at all; the report does not say why, nor which
element x1 is.

**Smallest fix (step 28).** J1's rubric and the answer check: an
"alternative" whose reasons say it is not the same or not certain is
unsure (M7). M8 needs the key's effect to be the click's (same
navigation, same region changed), else NEEDS REVIEW. Judge eval for
J1. Fixture: a button whose Enter is taken by a carousel; nearest page
that must keep PASS: 4.A's custom-control fixtures that work by
keyboard. Size M. No approval (PASS to NEEDS REVIEW).

### 5. One document for every address read as the same page

**Cells (16):** 9.A, 9.B, 9.C and 19.A on p07 to p10, not performed.

**What the tool did.** The forum's recorded document is byte for byte
the community home page's, and MySearchStory's is SDE home's: the
application serves one HTML shell at every address and draws the page
in the browser. Review K-01 (Abby, 2026-11-12) treats an other page
whose document is the tested page's as the tested page again, so all
four tests stopped: "other page 7 has the same content as the tested
page". The spec's A2 says "under another address (a query string)";
the code applies it to any address.

**What the tester did.** Compared the microsites' pages: 9.A fails
(no skip link), 9.B and 9.C pass, 19.A passes on three and fails on
MySearchStory.

**Kind.** Rule as built (the byte test was meant for a query string).
New with the applications.

**Smallest fix (step 26).** The byte test counts only when host and
path are the same apart from the query string, as `site.near_copy`
already requires; pages at different paths are compared. Rows: A2 of
9.A, 9.B, 9.C and 19.A, and 19.A's alias and suggested-page checks
("document byte for byte the same"). It must follow step 23: compared
before the app draws, 9.A could find no repeated block and say DOES
NOT APPLY where the key fails. Fixture: two pages at different paths
with one shell document whose script draws different content; nearest
page that must keep NEEDS REVIEW: K-01's query-string copy. Size S.
Turns NEEDS REVIEW into outcomes: **needs approval**. Also a limit to
record now: on such a site 19.A's alias check would verify
`/index.html` as the tested page because the shell is the same.

### 6. The search box in a closed panel, and 5.B's DOES NOT APPLY

**Cells (10):** 5.B on p01, p06, p07 and p08, DOES NOT APPLY where the
key passes; 5.A on p07 and p08, FAIL where it passes; 5.A on p01, p04,
p05 and p06, left for a person.

**What the tool did.** On the Drupal pages the search box sits in a
panel that the magnifier button in the header opens. Pass L focused
the field without opening the panel, so J1's picture showed "a nav bar
with a magnifier icon, but no visible search field" and J1 was unsure
(5.A M6). 5.B then said no field has a label people can see (A2, DOES
NOT APPLY), although 5.A could not decide that. On the forum, 5.A
found the comboboxes' only label to be their placeholder (M3, FAIL);
what is beside them is not in the report.

**What the tester did.** Counted the magnifier as the search box's
visible label (5.A and 5.B Pass), and the forum's icon buttons the
same. Round 1's keys say the same from the other side: nasa.gov's
search fails because there is "no magnifier glass icon etc.".

**Kind.** Reading (the field pictured inside a closed panel) and rule
(5.B's A2 fires while 5.A is undecided; an icon labels a field only
when it is a button in the field's own input group or search form, fix
8b). For p07 and p08, the frozen archive's 5.A pictures would show
which.

**Rounds 1 and 2.** Partly: fix 8b (round 2's svs search box) built
the icon-button case; the closed panel is new.

**Smallest fix (step 29).** (a) 5.B A2 only when 5.A found every field
unlabelled by a rule or by J1 = not_labeled; a field 5.A left unsure
makes 5.B NEEDS REVIEW, and J1 = graphic makes it an item. S, no
approval (DNA to NEEDS REVIEW). (b) Pass L opens the panel that holds
a hidden field before its picture: with step 15's phase 3, M. (c)
Abby's decision whether a panel's opener showing a magnifier labels
the field it opens: **needs approval** (NEEDS REVIEW to PASS).
Fixtures: a search box in a panel opened by a magnifier button; the
nearest page that must keep 5.A FAIL and 5.B DOES NOT APPLY is a
placeholder-only search box with no icon (round 1's nasa.gov).

### 7. Guard RC: what opens is not walked by 4.D and 5.D

**Cells (10):** 4.D on p02 to p05; 5.D on p01, p03, p05, p06 and p09;
4.E on p09 (the "All" dropdown's options were not reached by Tab).

The guard did its job: each cell's instances all PASS and the guard
holds the outcome. Known and planned (roadmap step 15, phase 2 for
4.D, phase 3 for 5.D; the combobox list for 4.E). Same in rounds 1 and
2. **One condition added:** step 27 (cause 3) before 4.D reads opened
content, or p02's 4.D becomes a PASS the key fails.

### 8. 2.C and 2.D: timers longer than the watch

**Cells (8):** 2.C and 2.D on p01, p07, p08 and p10, key DOES NOT
APPLY. A day-long timer that asks the server (p01, p10), and a 10 s
timer on the community app after which its content, text and images
changed (37 to 47 requests: the app still starting). Known
([KNOWN-LIMITS](../KNOWN-LIMITS.md), 2.C's clock check), same on all
ten of round 2's pages. No new step: part J (one watch on a paused
clock).

### 9. 5.F to 5.H on forms the tool cannot send

**Cells (7):** 5.F and 5.G on p02 (filter checkboxes, no button), p04
(a GET search sent to its server) and p05 (a file field with no
button); 5.H on p04 ("Published Date" may not be the submit control).
Keys: DOES NOT APPLY on p02 and p04, Pass on p05.

A careful tester sees that filter checkboxes and a search box with
nothing required cannot be filled in wrong; the tool tries to send
them and cannot. p05 needs a file: NEEDS REVIEW is right there
(proportionate to the PDF). Rounds 1 and 2: the same, most of their
5.F and 5.G cells are NEEDS REVIEW where the key says DOES NOT APPLY.
**Step 30:** a spec decision first (Abby): a form whose fields are
only a search box, checkboxes, radio buttons and selects, none
required and none with a format, has no input error to identify (DOES
NOT APPLY), with fixtures for a filter form and a required search box
(`5f/f19`, which must keep its outcome). Size M. NEEDS REVIEW to DOES
NOT APPLY: **needs approval**.

### 10. 9.B pairs equal links in order

**Cells (6):** 9.B on p01 to p06, FAIL where the key passes, each
against the first other page.

**What the tool did.** The site has a "Home" link in the top bar, one
in the footer's logo block and one in the footer list; every page but
the home page has a fourth, the breadcrumb's. Equal links (same name
and address) "pair in order" (9.B Terms), so the home page's second
"Home" pairs with the others' breadcrumb, its third with their logo
block's, and the social links between them read as reversed (N3).
Reproduced on a scratch page.

**What the tester did.** Saw the same navigation in the same order;
the breadcrumb is simply missing on the home page (TT p. 43 allows
insertions and removals).

**Kind.** Rule. New: rounds 1 and 2 agree on 9 of 9 and 9 of 10.

**Smallest fix (step 31).** Pair equal components by an alignment that
keeps their order where it can (the longest common subsequence of the
two pages' component lists), so an extra copy on one page is an
insertion, not a swap. Row: 9.B Terms ("several equal ones pair in
order") and N3. Fixture: the two scratch pages (an extra breadcrumb
"Home" in the same region); nearest page that must keep FAIL:
`9x/a3-nav-reordered` (two different links swapped). Size S. Removes
FAILs no key confirms; no approval.

### 11. 4.A's undecided signals on every Drupal page

**Cells (6):** 4.A on p01 to p06, key Pass. Each has the same three:
the AddToAny share frame (`#addtoany`, a hidden helper frame) as "an
embedded frame we could not read" (U, M16); a wheel or touch listener
on "an element" with no selector, probably the document (U, M16); and
the hover check stopped at its cap of 40 elements. Reading. Rounds 1
and 2: 4.A is NEEDS REVIEW on 8 of 9 and 7 of 10 pages; the gate files
keep page rows only (round 1's home page shows a frame, WK), so the
same signals are likely but not shown. **Step 32:** a frame with no
visible area and a listener on the window, document or body are not
U; calibrate `HOVER_MAX` on the three rounds' pages (KNOWN-LIMITS
already lists it). Size M. Turns NEEDS REVIEW into PASS: **needs
approval**.

### 12. 4.F: the judge, the footer's columns and dropdowns

**Cells (4):** 4.F FAIL on p04 and p09 (judge-decided; key Pass); 4.F
on p02 and p06, left for a person (J1 unsure).

- Every Drupal page raises the same three S3 signals ("focus jumps
  back up the page from 'Contact' to 'DATA SEARCH'" and two more): the
  footer's link lists sit in columns and Tab goes down one column and
  up to the next. On p02 and p06 J1 was unsure because those signals
  name footer links that are not in its order list or picture.
- On p04, J1 called the search page's order (the search button after
  the sort menu, the filters after the results) "does not preserve";
  Abby: "a little odd ... but the meaning and operability is
  preserved".
- On p09, after opening the "All" dropdown, Tab skips its options to
  the search box (S6); J1 said "does not preserve". The options take
  arrow keys, as a listbox's do.

Kind: judge (p04, p09), rule (S3 on columns, S6 on an arrow-key
popup) and reading (the order list misses what the signals name).
Rounds 1 and 2: round 2's two 4.F false FAILs (search, 5340) were
judge answers; round 1's 4.F is NEEDS REVIEW by J1 on 5 pages. Same
family. **Step 33:** the order list and picture include every element
a signal names (S); S3 not raised for a jump to the top of the next
column of one list (M); S6 not raised when the trigger's popup is a
listbox or menu reached by arrows (S); J1's rubric: an order that is
odd but keeps meaning and operation preserves it, with a judge eval.
The S3 and S6 exceptions can turn NEEDS REVIEW into PASS: **need
approval**.

### 13. 19.A on the Drupal pages

**Cells (4):** 19.A on p01 to p04, key Pass.

- p01 to p03: one kind found (navigation); the site search ran but its
  results page did not load one of its scripts (W4). Known
  (KNOWN-LIMITS: "19.A's site search depends on where the tool runs").
- p04 (a search results page, `?rendered_item=test&sort_by=rel`): one
  kind (search, W5); 486 links in closed menus on 9 pages (W9).
- The key's second ways: "navigation and breadcrumbs on child pages"
  (p01, p02) and "content links" (p03, p04). The spec counts a
  breadcrumb as a navigation link, the same kind as the menus; the key
  counts it apart. TT p. 75 lists "navigation menus or dropdowns",
  "navigation trees" and "links between pages" separately. A rule
  question for Abby.
- p04's "content links": the home page's topic tags lead to
  `/search?rendered_item=astrophysics` and others, not to this query.
  The spec says a link that differs only by its query string is not
  the page. Whether a results page is one page whatever its query is
  also Abby's call.

**Step 34:** Abby's two answers, then the spec change they need
(**approval**: NEEDS REVIEW to PASS), and the CILab question below.

### 14. 4.E: the app's own address change read as caused by focus

**Cells (3):** 4.E on p07, p08 and p10, FAIL where the key passes.

Every 4.E address change on the application pages came on the first
key press of a fresh load: Tab on p07 and p08 ("an element": the page
was gone before the element could be named), Shift+Tab on p07's event
card and on p10's "next-icon", Tab on p10's NASA logo. On p08 the
Shift+Tab one did not happen again on a second try (M3). 4.E's control
replay, which should tell time from focus (M2), waits only as long as
the step itself took after its own load, and the reports do not record
how long after load the original key came; a change the app makes
while it starts is missed by the control that way. That is the likely
reading, not shown. These were loads of another document, not
`history.pushState` (4.E ignores that: fixture `4e/f12-pushstate-on-focus`
is PASS); on p07 and p08 the app's sign-in redirect would fit (cause 2),
on p10 the reports do not say. **Step 24:** the control replay waits
until the same time after load as the original step ended (section 2,
b; row M2). Fixture: a page that goes to another address by itself
1.5 s after load, with the walk's first key near then; nearest page
that must keep FAIL: `4e/f02-navigate-on-focus`. Size S-M. Removes
FAILs no key confirms; no approval. New with the applications.

### 15. Applications with no `<form>` element

**Cells (3):** 5.B on p09 and 5.C on p09 and p10, left for a person.
With no `<form>`, every control's form is "none", so the header's
"SDE" button (a product menu) joined the search field's form as a
button that acts on its data, and J1 was unsure what "SDE" means. 5.C
compared "SDESDE" (the name ANDI reports: icon text and label run
together) with the visible "SDE" word by word, found no match (M5 not
met) and asked J1, which was unsure. Reading; new. **Step 35 (part
a):** form "none" leaves out buttons in banner and navigation regions;
M5 also matches with spaces removed. S. NEEDS REVIEW to PASS:
**needs approval**.

### 16. MySearchStory: fields the tool did not find

**Cells (3):** 5.A, 5.B and 5.D on p10, DOES NOT APPLY where the key
passes ("All input fields have icons and/or text labels"). The tool
found only buttons (5.A A2: "only buttons, which carry their own
text"; 5.H: no form). The report does not show whether the page has a
data-entry field. If its only controls are the carousel's buttons,
Abby's decision of 2026-11-04 ("buttons alone are not a form", post
round 1 fix 14) makes 5.A and 5.D DOES NOT APPLY and the key cells
wrong; 5.B's ER 2 covers button labels, so 5.B may apply either way.
**A question for Abby**, no step until it is answered (or the frozen
archive shows a field).

### 17. Two code chunks not in the frozen recording

**Cells (2):** 4.B on p07 and p08: guard GU, two chunks the app loads
when used (`chunk-HH7OQO3D.js`, `chunk-GCKNKALH.js`) are not in the
recording. The guard did its job. The chunk store fetches them during
a live recording; a frozen replay fetches nothing, and the freeze did
not run the chunk store. Recording. Round 2's 5340 had the same guard.
**Step 25:** the freeze runs the chunk store and saves the chunks in
the frozen recording. S. No approval.

### 18. 5.D on the blog's filters

**Cell:** 5.D on p02, FAIL where the key passes. Pressing Space on a
filter checkbox sent a request the recording does not hold: J2's
reasons note "an error message banner appeared" on each one (the
site's error for a failed filter request). After "Earth Science (8)",
focus went to an element of the same name, the checkbox's own label or
wrapper, which 5.D read as focus moving on its own (M9). Recording and
reading. Round 1 has a 5.D false FAIL on its home page (judge-decided);
the gate rows do not show why. **Step 35 (part b):** focus that lands
on the field's own label or wrapper, or on the same field drawn again,
is not a move; an action whose request the recording cannot answer is
NEEDS REVIEW. S. Nearest page that must keep FAIL:
`5d/f19-rerender-on-change` (the form drawn again, focus put on
another field).

### 19. 5.C on an event card

**Cell:** 5.C on p07, FAIL where the key passes. J1 found "GMT" (the
time zone printed on an event card that is a button) missing from its
name and answered "missing" (M7). The card's own words are its
content, not an instruction or cue for using it. Judge. **Step 35
(part c):** the rubric says so; judge eval. S.

### 20. 5.B on the FITS verifier

**Cell:** 5.B on p05, FAIL where the key passes. Pass L read the
"Print Header Contents" checkbox's visible label as empty, and its
picture shows the file button, not the checkbox (the checkbox is
drawn by the page's own style). J1 answered "some not descriptive"
while its `seen` says "no checkbox visible". Reading and judge. **Step
35 (part d):** read a visually hidden checkbox's `label[for]` as its
visible label; an answer whose `seen` says the item is not visible is
unsure. S.

### 21. 4.C on SDE home

**Cell:** 4.C on p09, left for a person: "Tabbing from an error state
(after pressing the button in form1) did not finish (navigation)".
The search button shows results at another address; there is no error
state to walk. Rule. **Step 35 (part e):** a press that navigates
leaves no error state, so that walk is not owed. S. NEEDS REVIEW to
PASS: **needs approval**.

## 19.A on round 2's CILab page

- **Step 6h's rerun** (19.A 1.14.0, 2026-11-15, tested pages frozen and
  other pages live, `tested_frozen`): **PASS**, from two kinds: the
  svs home page's card link to `/cilab/index.html`, which the alias
  check loaded and found to be the same document (W6, a content link),
  and the subpages' row of icon links, repeated on CILab's home (the
  1.14.0 link-group rule: navigation)
  ([plan](2026-11-15-19a-finds-ways.md), "Rerun with 19.A 1.14.0").
- **Step 6g's rerun** (19.A 1.15.0, the same day, the same mode; and
  `main`'s 1.14.0 run beside it): **FAIL** where the key passes. The
  README's status line records only the outcome; the run's reports are
  out of git and no file in this repository says which rows decided it.
- **Which is right: the PASS.** Both of the key's ways are on the live
  site (checked 2026-11-15), and they are exactly the two 6h found.
- **What the FAIL means.** 19.A FAILs only when the live search ran,
  its results did not lead to the page, every suggested page was
  checked and no alias was left unverified. So in 6g's run neither
  the alias nor the icon row was read as a way and neither was counted
  as unverified: the two runs read different other pages. Both loaded
  the other pages live, so what the live svs pages served that day
  (or what the page cache held) differed; which is not recorded.
- **What to do (step 34).** Run 19.A alone on CILab twice in each mode
  and compare W1 and W6 with the 6g run folder (Abby holds a copy).
  Whatever the cause, development reruns of 9.A to 9.C and 19.A should
  serve the other pages from the freeze too, as round 3's were (every
  other page `frozen: true` in its reports): a rerun that loads them
  live depends on what the live pages show that day and is not
  repeatable.

## Key cells

- **p03 5.F (Fail):** not wrong. It is a TT reading that differs from
  Understanding 3.3.1 on native validation; a decision for Abby (cause
  1). **p03 5.G (Fail):** right for Firefox; Chromium's message would
  pass. Browser-dependent.
- **p10 5.A, 5.B, 5.D (Pass):** possibly wrong, if the page's only
  controls are buttons (cause 16). A question.
- **p04 19.A (Pass) by "content links":** the links lead to other
  queries of the same results page; right only if a results page is
  one page whatever its query (cause 13). A question.
- **p01, p02 19.A (Pass) by "breadcrumbs":** right if a breadcrumb is a
  way of its own; the spec says it is navigation (cause 13). A
  question.
- No other key cell looks wrong to me. The 9.B, 4.E, 4.A (p07, p08),
  5.A to 5.D cells the tool got wrong are the tool's errors.

## New limits recorded today

In [KNOWN-LIMITS.md](../KNOWN-LIMITS.md): applications that draw
themselves after load; one document at every address (and 19.A's
alias check on such a site); 4.E's control replay and an app's own
address change; 9.B's pairing of equal links; the browser's own error
messages in 5.F and 5.G; 4.D's absolute pixel count; 4.A's hedged J1
answer and its execute check; 4.F's columns and arrow-key popups;
controls with no `<form>`; 5.D's filters on a recording; the freeze
and the chunk store; breadcrumbs in 19.A. The wrong PASS and DOES NOT
APPLY results that reproduce are in the README's "Known wrong
outcomes" table.

## Every wrong cell and every cell left for a person

Worst first, then by page. "Cause" is the number above. Sentences are
the report's, shortened; the full text is in each page's
`results/pNN/report.json`.

| Page | Test | Key, and its comment | Tool: outcome, rows | Tool's sentence (shortened) | Verdict | Cause |
| --- | --- | --- | --- | --- | --- | --- |
| p03 | 5.F | Fail: When you submit (or preview) on a form with errors, a pop up message under only the first field to error (not all), and only says "Please f… | PASS, A5 G4 (M2×5) | We left required fields empty and typed a wrong value (such as a bad email address or a year out of range) into fields that expect a format and dates… | **PASS, key Fails** | 1: Chrome's own messages read for every field as shown, and Chrome's "test@" message guides; the key read Firefox's bubble (first field only, "Please enter an email address") |
| p03 | 5.G | Fail: Entering a short string in the Email field without @ shows an error of just "Please enter an email address" (there is an email entered, jus… | PASS, A5 G5 (N4×5) | Each form error we caused came with a hint on how to fix it. | **PASS, key Fails** | 1: Chrome's own messages read for every field as shown, and Chrome's "test@" message guides; the key read Firefox's bubble (first field only, "Please enter an email address") |
| p08 | 4.F | Fail: The focus order for the tag word cloud seems random and I'm not able to navigate in a logical way to the tag I want to select. | DNA, A3 G1 | The page has only one element that takes keyboard focus, so there is no order to check. | **DNA, key Fails** | 2: forward walk read the app before it drew: P1 one stop, P2 cap 50 (inventory empty at start) on a page of 76-90 focusable elements |
| p01 | 9.B | Pass | FAIL, A4 G2 (N3×5) | Some navigation appears in a different order on another page: "Home" comes before "Home" here but after it on other page 1. "NASA Science on Facebook… | FAIL, key Passes | 10: three or four links named "Home" to one address; the home page has no breadcrumb "Home", so pairing them in order crosses them |
| p02 | 5.D | Pass: Filter checkboxes do immediately update the blog listings but do not reload the page, change focus, or otherwise act unexpectedly. | FAIL, A3 G2 (M11×8, M13, M9) | Filling in some form fields changes what the user is doing without warning, which can disorient keyboard and screen reader users. Filling in "Earth S… | FAIL, key Passes | 18: after Space on a filter, focus went to an element of the field's own name; the replay showed the site's error banner (the filter's request is not in the recording) |
| p02 | 9.B | Pass | FAIL, A4 G2 (N3, N6×4) | Some navigation appears in a different order on another page: "Home" comes before "Home" here but after it on other page 1. "Home" comes before "NASA… | FAIL, key Passes | 10: three or four links named "Home" to one address; the home page has no breadcrumb "Home", so pairing them in order crosses them |
| p03 | 9.B | Pass | FAIL, A4 G2 (N3, N6×4) | Some navigation appears in a different order on another page: "Home" comes before "Home" here but after it on other page 1. "Home" comes before "NASA… | FAIL, key Passes | 10: three or four links named "Home" to one address; the home page has no breadcrumb "Home", so pairing them in order crosses them |
| p04 | 4.F | Pass: A little odd for the search filters (first column) to come after the search results (second column) but the meaning and operability is pres… | FAIL, A4 G2 (M6[S3,S3,S3,S3,S3], M9[S6]) | Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus ord… | FAIL, key Passes | 12: J1 said "does not preserve" |
| p04 | 9.B | Pass | FAIL, A4 G2 (N3, N6×4) | Some navigation appears in a different order on another page: "Home" comes before "Home" here but after it on other page 1. "Home" comes before "NASA… | FAIL, key Passes | 10: three or four links named "Home" to one address; the home page has no breadcrumb "Home", so pairing them in order crosses them |
| p05 | 5.B | Pass: Visual labels for site search box, file upload field and show header checkbox are all descriptive. | FAIL, A4 G2 (M3, M2) | Some labels do not say what to enter or what the button does: the field next to "Select a FITS file to verify it directly in your browser.". | FAIL, key Passes | 20: pass L read the checkbox's label as empty; J1 said "not descriptive" though its picture showed no checkbox |
| p05 | 9.B | Pass | FAIL, A4 G2 (N3, N6×4) | Some navigation appears in a different order on another page: "Home" comes before "Home" here but after it on other page 1. "Home" comes before "NASA… | FAIL, key Passes | 10: three or four links named "Home" to one address; the home page has no breadcrumb "Home", so pairing them in order crosses them |
| p06 | 9.B | Pass | FAIL, A4 G2 (N3, N6×4) | Some navigation appears in a different order on another page: "Home" comes before "Home" here but after it on other page 1. "Home" comes before "NASA… | FAIL, key Passes | 10: three or four links named "Home" to one address; the home page has no breadcrumb "Home", so pairing them in order crosses them |
| p07 | 4.A | Pass | FAIL, A3 G2 (M16×48, M6×17, M5×2, M1, C?×5) | Some things on this page work with a mouse but not with the keyboard, so keyboard users cannot use them. "Search" works with a mouse but can't be rea… | FAIL, key Passes | 2: forward walk read the app before it drew: P1 one stop, P2 cap 50 (inventory empty at start) on a page of 76-90 focusable elements |
| p07 | 4.E | Pass | FAIL, A3 G2 (M4×2, M11×2, M12) | Moving keyboard focus onto some elements changes what the user is doing without their asking, which can disorient keyboard and screen reader users. W… | FAIL, key Passes | 14: address changed at the first key press of a fresh load (Tab or Shift+Tab), read as caused by focus; p08's second one did not repeat |
| p07 | 5.A | Pass: Site search and forum post buttons all have descriptive icon buttons at least, and sometimes text labels too. | FAIL, A4 G2 (M3) | Some form fields have no label or instructions people can see, so a person may not know what to enter. "Global search across forum, events, and annou… | FAIL, key Passes | 6: "only label is the placeholder" (M3); the key counts the search icon |
| p07 | 5.C | Pass: Site search and forum post buttons all have programmatic descriptions | FAIL, A3 G2 (M5×38, M7) | Some form fields or buttons do not tell screen reader users what they are for, or leave out instructions that other users can see. "Data Governance C… | FAIL, key Passes | 19: J1 called "GMT" on an event card button a missing cue (M7) |
| p08 | 4.A | Pass | FAIL, A3 G2 (M16×42, M6×18, M3×2, M1, C?×20) | Some things on this page work with a mouse but not with the keyboard, so keyboard users cannot use them. "Search" works with a mouse but can't be rea… | FAIL, key Passes | 2: forward walk read the app before it drew: P1 one stop, P2 cap 50 (inventory empty at start) on a page of 76-90 focusable elements |
| p08 | 4.E | Pass | FAIL, A3 G2 (M4, M11×2, M3, M12) | Moving keyboard focus onto some elements changes what the user is doing without their asking, which can disorient keyboard and screen reader users. W… | FAIL, key Passes | 14: address changed at the first key press of a fresh load (Tab or Shift+Tab), read as caused by focus; p08's second one did not repeat |
| p08 | 5.A | Pass: Site search and forum post buttons all have descriptive icon buttons at least, and sometimes text labels too. | FAIL, A4 G2 (M3×2) | Some form fields have no label or instructions people can see, so a person may not know what to enter. "Global search across forum, events, and annou… | FAIL, key Passes | 6: "only label is the placeholder" (M3); the key counts the search icon |
| p09 | 4.F | Pass | FAIL, A4 G2 (M4, M6[S6]) | Keyboard focus moves through parts of the page in an order that doesn't make sense, which can confuse keyboard and screen reader users. The focus ord… | FAIL, key Passes | 12: J1 said "does not preserve" |
| p10 | 4.E | Pass | FAIL, A3 G2 (M4×2) | Moving keyboard focus onto some elements changes what the user is doing without their asking, which can disorient keyboard and screen reader users. W… | FAIL, key Passes | 14: address changed at the first key press of a fresh load (Tab or Shift+Tab), read as caused by focus; p08's second one did not repeat |
| p01 | 5.B | Pass: Only form element on page is site search box, which passes with a visual magnifying glass icon. | DNA, A2 G1 | No form field on this page has a label people can see, so there is no label to judge here (a missing label is reported by the label test). | DNA, key Passes | 6: 5.A found no label it could see (the search box sits in a panel the magnifier opens, or only its placeholder); 5.B then said no label to judge |
| p06 | 5.B | Pass: Only form element on page is site search box, which passes with a visual magnifying glass icon. | DNA, A2 G1 | No form field on this page has a label people can see, so there is no label to judge here (a missing label is reported by the label test). | DNA, key Passes | 6: 5.A found no label it could see (the search box sits in a panel the magnifier opens, or only its placeholder); 5.B then said no label to judge |
| p07 | 4.F | Pass | DNA, A3 G1 | The page has only one element that takes keyboard focus, so there is no order to check. | DNA, key Passes | 2: the walk read the app before it drew: P1 found one element (also 4.A's J1: "only reached stop is a home link") |
| p07 | 5.B | Pass: Site search and forum post buttons all have descriptive icon buttons at least, and sometimes text labels too. | DNA, A2 G1 | No form field on this page has a label people can see, so there is no label to judge here (a missing label is reported by the label test). | DNA, key Passes | 6: 5.A found no label it could see (the search box sits in a panel the magnifier opens, or only its placeholder); 5.B then said no label to judge |
| p07 | 5.D | Pass | DNA, A1 G1 | This page has no form fields, so this test does not apply. | DNA, key Passes | 2: forward walk read the app before it drew: P1 one stop, P2 cap 50 (inventory empty at start) on a page of 76-90 focusable elements |
| p08 | 5.B | Pass: Site search and forum post buttons all have descriptive icon buttons at least, and sometimes text labels too. | DNA, A2 G1 | No form field on this page has a label people can see, so there is no label to judge here (a missing label is reported by the label test). | DNA, key Passes | 6: 5.A found no label it could see (the search box sits in a panel the magnifier opens, or only its placeholder); 5.B then said no label to judge |
| p08 | 5.D | Pass | DNA, A1 G1 | This page has no form fields, so this test does not apply. | DNA, key Passes | 2: forward walk read the app before it drew: P1 one stop, P2 cap 50 (inventory empty at start) on a page of 76-90 focusable elements |
| p10 | 5.A | Pass: All input fields have icons and/or text labels. | DNA, A2 G1 | This page's only form controls are buttons, which carry their own text, so this test does not apply. | DNA, key Passes | 16: the tool found only buttons on the page (no field); the report does not show a field the key could mean |
| p10 | 5.B | Pass | DNA, A2 G1 | No form field on this page has a label people can see, so there is no label to judge here (a missing label is reported by the label test). | DNA, key Passes | 16: the tool found only buttons on the page (no field); the report does not show a field the key could mean |
| p10 | 5.D | Pass | DNA, A1 G1 | This page has no form fields, so this test does not apply. | DNA, key Passes | 16: the tool found only buttons on the page (no field); the report does not show a field the key could mean |
| p01 | 19.A | Pass: Navigation and breadcrumbs on child pages (e.g. https://science.data.nasa.gov/blog/omni-spotlight) | NEEDS_REVIEW, A5 W1 W4 G3 | We found 1 way to reach this page (the site navigation). The site search could not be checked: its results page did not finish loading (1 of its scri… | left for a person | 13: one kind found (navigation); the site search's results page did not finish loading (a script missing) |
| p01 | 2.C | Does Not Apply | NEEDS_REVIEW, A2 G1 | We watched this page for 6.5 seconds without touching it, looking for content that is still changing by itself after 5 seconds, like a carousel, tick… | left for a person | 8: a timer longer than the watch: a day-long one that asks the server (p01, p10), or a 10 s one after which the app's content changed (p07, p08) |
| p01 | 2.D | Does Not Apply | NEEDS_REVIEW, A1 2.C-A2 G1 | We watched this page for 6.5 seconds without touching it, looking for content that is still changing by itself after 5 seconds, like a carousel, tick… | left for a person | 8: a timer longer than the watch: a day-long one that asks the server (p01, p10), or a 10 s one after which the app's content changed (p07, p08) |
| p01 | 4.A | Pass | NEEDS_REVIEW, A3 G3 (M16×2, M11×9) | The page has an embedded frame we could not read that we cannot check automatically; please check it works with the keyboard. The page has something… | left for a person | 11: three undecided signals on every page: AddToAny's hidden frame (U), a wheel or touch listener on "an element" (U), hover check capped at 40 |
| p01 | 4.D | Pass | NEEDS_REVIEW, A3 G3 (M6×101, M5, M4×10) | We could not get a clear before-and-after view of "Galaxies" (link) (its focus style draws an outline or a shadow that our pictures did not show wher… | left for a person | 3: image links: their focus style draws an outline the pictures did not show (M4) |
| p01 | 5.A | Pass: Only form element on page is site search box, which passes with a visual magnifying glass icon. | NEEDS_REVIEW, A4 G3 (M6) | We could not tell whether "Search NASA science data" (text field) has a label people can see. Please look at it. | left for a person | 6: J1 unsure: the picture shows the magnifier, not the field (it is in a closed panel) |
| p01 | 5.D | Pass | NEEDS_REVIEW, A3 G4 RC | The page has menus or sections that open to show more controls, and this test has not checked inside them yet, so a person needs to check what they h… | left for a person | 7: guard RC: menus and sections that open hold controls this test does not walk yet |
| p02 | 19.A | Pass: Navigation and breadcrumbs on child pages (e.g. https://science.data.nasa.gov/blog/omni-spotlight) | NEEDS_REVIEW, A5 W1 W4 G3 | We found 1 way to reach this page (the site navigation). The site search could not be checked: its results page did not finish loading (1 of its scri… | left for a person | 13: one kind found (navigation); the site search's results page did not finish loading (a script missing) |
| p02 | 4.A | Pass | NEEDS_REVIEW, A3 G3 (M16×2, M11×8, M13×2) | The page has an embedded frame we could not read that we cannot check automatically; please check it works with the keyboard. The page has something… | left for a person | 11: three undecided signals on every page: AddToAny's hidden frame (U), a wheel or touch listener on "an element" (U), hover check capped at 40 |
| p02 | 4.D | Fail: In the list of blog results, between a blog's title and its image alt text (which shows as a faint dashed outline of a long horizontal rect… | NEEDS_REVIEW, A3 G4 RC (M6×81, M5) | The page has menus or sections that open to show more controls, and this test has not checked inside them yet, so a person needs to check what they h… | left for a person | 7: guard RC: menus and sections that open hold controls this test does not walk yet |
| p02 | 4.F | Pass | NEEDS_REVIEW, A4 G3 (M9[S3,S3,S3,S3]) | The focus order departs from the reading order (focus jumps back up the page from "Planetary Science (5)" (checkbox) to "INDUS-SDE: A Language Model… | left for a person | 12: J1 unsure: the footer's column jumps (S3) name elements its order list and picture leave out |
| p02 | 5.F | Does Not Apply | NEEDS_REVIEW, A5 G3 | We pressed the form's last field, but it may not be the control that sends this form, so we could not tell whether the page checks it for errors. Ple… | left for a person | 9: no attempt could be completed: a filter form with no button and no text field |
| p02 | 5.G | Does Not Apply | NEEDS_REVIEW, A5 G3 | We pressed the form's last field, but it may not be the control that sends this form, so we could not tell whether the page checks it for errors. Ple… | left for a person | 9: no attempt could be completed: a filter form with no button and no text field |
| p03 | 19.A | Pass: Navigation and content links on pages (e.g. https://science.data.nasa.gov/science-discovery-engine). | NEEDS_REVIEW, A5 W1 W4 G3 | We found 1 way to reach this page (the site navigation). The site search could not be checked: its results page did not finish loading (1 of its scri… | left for a person | 13: one kind found (navigation); the site search's results page did not finish loading (a script missing) |
| p03 | 4.A | Pass | NEEDS_REVIEW, A3 G3 (M16×2, M11×8, M13) | The page has an embedded frame we could not read that we cannot check automatically; please check it works with the keyboard. The page has something… | left for a person | 11: three undecided signals on every page: AddToAny's hidden frame (U), a wheel or touch listener on "an element" (U), hover check capped at 40 |
| p03 | 4.D | Pass | NEEDS_REVIEW, A3 G4 RC (M6×42, M5×5) | The page has menus or sections that open to show more controls, and this test has not checked inside them yet, so a person needs to check what they h… | left for a person | 7: guard RC: menus and sections that open hold controls this test does not walk yet |
| p03 | 5.D | Pass | NEEDS_REVIEW, A3 G4 RC | The page has menus or sections that open to show more controls, and this test has not checked inside them yet, so a person needs to check what they h… | left for a person | 7: guard RC: menus and sections that open hold controls this test does not walk yet |
| p04 | 19.A | Pass: Navigation and content links (e.g. on homepage when you click on a topic tag, it takes you to the search results page for that topic) | NEEDS_REVIEW, A5 W1 W5 W9 G3 | We found 1 way to reach this page (the site search). Some pages we read have closed menus (486 links inside them on 9 pages) that we did not open, so… | left for a person | 13: one kind found (search); 486 links in closed menus not opened |
| p04 | 4.A | Pass | NEEDS_REVIEW, A3 G3 (M16×2, M11×8, M13×3) | The page has an embedded frame we could not read that we cannot check automatically; please check it works with the keyboard. The page has something… | left for a person | 11: three undecided signals on every page: AddToAny's hidden frame (U), a wheel or touch listener on "an element" (U), hover check capped at 40 |
| p04 | 4.D | Pass | NEEDS_REVIEW, A3 G4 RC (M6×100, M5×2) | The page has menus or sections that open to show more controls, and this test has not checked inside them yet, so a person needs to check what they h… | left for a person | 7: guard RC: menus and sections that open hold controls this test does not walk yet |
| p04 | 5.A | Pass | NEEDS_REVIEW, A4 G3 (M6, M4, M2×5) | We could not tell whether "Search NASA science data" (text field) has a label people can see. Please look at it. | left for a person | 6: J1 unsure: the picture shows the magnifier, not the field (it is in a closed panel) |
| p04 | 5.F | Does Not Apply | NEEDS_REVIEW, A4 G1 | The form was sent to its server, and our copy of the page cannot show what the server answers. Please submit it with mistakes on the live site and ch… | left for a person | 9: a GET search sent to its server, which the recording cannot answer |
| p04 | 5.G | Does Not Apply | NEEDS_REVIEW, A4 G1 | The form was sent to its server, and our copy of the page cannot show what the server answers. Please submit it with mistakes on the live site and ch… | left for a person | 9: a GET search sent to its server, which the recording cannot answer |
| p04 | 5.H | Does Not Apply | NEEDS_REVIEW, A2 G1 | We pressed "Published Date", but it may not be the control that sends this form, so we could not tell whether the page checks it for errors. Please c… | left for a person | 9: the press may not be the form's submit control ("Published Date") |
| p05 | 4.A | Pass | NEEDS_REVIEW, A3 G3 (M16×2, M11×8, M13) | The page has an embedded frame we could not read that we cannot check automatically; please check it works with the keyboard. The page has something… | left for a person | 11: three undecided signals on every page: AddToAny's hidden frame (U), a wheel or touch listener on "an element" (U), hover check capped at 40 |
| p05 | 4.D | Pass | NEEDS_REVIEW, A3 G4 RC (M6×60, M5) | The page has menus or sections that open to show more controls, and this test has not checked inside them yet, so a person needs to check what they h… | left for a person | 7: guard RC: menus and sections that open hold controls this test does not walk yet |
| p05 | 5.A | Pass: Site search box, file upload field and show header checkbox all have visual labels. | NEEDS_REVIEW, A4 G3 (M6×2, M4) | We could not tell whether "Search NASA science data" (text field) has a label people can see. Please look at it. We could not tell whether "Print Hea… | left for a person | 6: J1 unsure on the search box (closed panel) and on the checkbox (the picture shows the file button) |
| p05 | 5.D | Pass | NEEDS_REVIEW, A3 G4 RC | The page has menus or sections that open to show more controls, and this test has not checked inside them yet, so a person needs to check what they h… | left for a person | 7: guard RC: menus and sections that open hold controls this test does not walk yet |
| p05 | 5.F | Pass: Errors in uploaded FITS files are explained in detail in the results box, and uploading a file of an incorrect format also explains why and… | NEEDS_REVIEW, A5 G3 | One attempt to send a form could not be completed (no button and no text field to press Enter in). | left for a person | 9: a file field with no button: the form is never sent |
| p05 | 5.G | Pass: Errors in uploaded FITS files are explained in detail in the results box, and uploading a file of an incorrect format also explains why and… | NEEDS_REVIEW, A5 G3 | One attempt to send a form could not be completed (no button and no text field to press Enter in). | left for a person | 9: a file field with no button: the form is never sent |
| p06 | 4.A | Pass | NEEDS_REVIEW, A3 G3 (M16×2, M11×8, M13) | The page has an embedded frame we could not read that we cannot check automatically; please check it works with the keyboard. The page has something… | left for a person | 11: three undecided signals on every page: AddToAny's hidden frame (U), a wheel or touch listener on "an element" (U), hover check capped at 40 |
| p06 | 4.F | Pass | NEEDS_REVIEW, A4 G3 (M9[S3,S3,S3,S3], M4) | The focus order departs from the reading order (focus jumps back up the page from "Test Data Sets" (link) to "FITS File Verifier" (link); focus jumps… | left for a person | 12: J1 unsure: the footer's column jumps (S3) name elements its order list and picture leave out |
| p06 | 5.A | Pass: Only form element on page is site search box, which passes with a visual magnifying glass icon. | NEEDS_REVIEW, A4 G3 (M6) | We could not tell whether "Search NASA science data" (text field) has a label people can see. Please look at it. | left for a person | 6: J1 unsure: the picture shows the magnifier, not the field (it is in a closed panel) |
| p06 | 5.D | Pass | NEEDS_REVIEW, A3 G4 RC | The page has menus or sections that open to show more controls, and this test has not checked inside them yet, so a person needs to check what they h… | left for a person | 7: guard RC: menus and sections that open hold controls this test does not walk yet |
| p07 | 19.A | Pass: Navigation and content links on other pages (e.g. https://science.data.nasa.gov/) | NEEDS_REVIEW, A2 G1 | other page 7 has the same content as the tested page, so comparing them would compare the page with itself | left for a person | 5: the app serves one document for every address: another page's recording is byte for byte the tested page's, read as the same page (K-01) |
| p07 | 2.C | Does Not Apply | NEEDS_REVIEW, A2 G1 | We watched this page for 6.5 seconds without touching it, looking for content that is still changing by itself after 5 seconds, like a carousel, tick… | left for a person | 8: a timer longer than the watch: a day-long one that asks the server (p01, p10), or a 10 s one after which the app's content changed (p07, p08) |
| p07 | 2.D | Does Not Apply | NEEDS_REVIEW, A1 2.C-A2 G1 | We watched this page for 6.5 seconds without touching it, looking for content that is still changing by itself after 5 seconds, like a carousel, tick… | left for a person | 8: a timer longer than the watch: a day-long one that asks the server (p01, p10), or a 10 s one after which the app's content changed (p07, p08) |
| p07 | 4.B | Pass | NEEDS_REVIEW, A3 G4 GU (M1) | The page loads more code when it is used, for example when you type in a field, and the recording of the page does not have that code, so what happen… | left for a person | 17: guard GU: two code chunks the app loads when used are not in the recording |
| p07 | 4.C | Pass | NEEDS_REVIEW, A3 G3 | The Shift+Tab walk hit its press limit before reaching the end of the page. The page seems to load more content as you scroll, and the recording coul… | left for a person | 2: forward walk read the app before it drew: P1 one stop, P2 cap 50 (inventory empty at start) on a page of 76-90 focusable elements |
| p07 | 4.D | Pass: The dashed focus outlines are sometimes extremely faint (esp on the links within the hero, against the background image) but they are techn… | NEEDS_REVIEW, A3 WK G3 (M4×10, M6×41) | We could not get a clear before-and-after view of "Data Governance Knowledge Hub" (link) (focus never moved on (the walk ended on it)), so a person n… | left for a person | 2: forward walk read the app before it drew: P1 one stop, P2 cap 50 (inventory empty at start) on a page of 76-90 focusable elements |
| p07 | 5.H | Does Not Apply | NEEDS_REVIEW, A2 G1 | The keyboard reached 0 of the 1 form fields on this page, so 1 was not checked. | left for a person | 2: forward walk read the app before it drew: P1 one stop, P2 cap 50 (inventory empty at start) on a page of 76-90 focusable elements |
| p07 | 9.A | Fail: No skip link to bypass header | NEEDS_REVIEW, A2 G1 | other page 7 has the same content as the tested page, so comparing them would compare the page with itself | left for a person | 5: the app serves one document for every address: another page's recording is byte for byte the tested page's, read as the same page (K-01) |
| p07 | 9.B | Pass: Consistent with other pages within the Data Governance Community's microsite | NEEDS_REVIEW, A2 G1 | other page 7 has the same content as the tested page, so comparing them would compare the page with itself | left for a person | 5: the app serves one document for every address: another page's recording is byte for byte the tested page's, read as the same page (K-01) |
| p07 | 9.C | Pass: Consistent with other pages within the Data Governance Community's microsite | NEEDS_REVIEW, A2 G1 | other page 7: it has the same content as the tested page, so comparing them would compare the page with itself | left for a person | 5: the app serves one document for every address: another page's recording is byte for byte the tested page's, read as the same page (K-01) |
| p08 | 19.A | Pass: Navigation and breadcrumbs on individual forum posts (e.g. https://science.data.nasa.gov/data-governance-community/forum/post-details/242) | NEEDS_REVIEW, A2 G1 | other page 7 has the same content as the tested page, so comparing them would compare the page with itself | left for a person | 5: the app serves one document for every address: another page's recording is byte for byte the tested page's, read as the same page (K-01) |
| p08 | 2.C | Does Not Apply | NEEDS_REVIEW, A2 G1 | We watched this page for 6.5 seconds without touching it, looking for content that is still changing by itself after 5 seconds, like a carousel, tick… | left for a person | 8: a timer longer than the watch: a day-long one that asks the server (p01, p10), or a 10 s one after which the app's content changed (p07, p08) |
| p08 | 2.D | Does Not Apply | NEEDS_REVIEW, A1 2.C-A2 G1 | We watched this page for 6.5 seconds without touching it, looking for content that is still changing by itself after 5 seconds, like a carousel, tick… | left for a person | 8: a timer longer than the watch: a day-long one that asks the server (p01, p10), or a 10 s one after which the app's content changed (p07, p08) |
| p08 | 4.B | Pass | NEEDS_REVIEW, A3 G4 GU (M1) | The page loads more code when it is used, for example when you type in a field, and the recording of the page does not have that code, so what happen… | left for a person | 17: guard GU: two code chunks the app loads when used are not in the recording |
| p08 | 4.C | Pass | NEEDS_REVIEW, A3 G3 | The Shift+Tab walk hit its press limit before reaching the end of the page. The page seems to load more content as you scroll, and the recording coul… | left for a person | 2: forward walk read the app before it drew: P1 one stop, P2 cap 50 (inventory empty at start) on a page of 76-90 focusable elements |
| p08 | 4.D | Pass | NEEDS_REVIEW, A3 WK G3 (M4×7, M6×44) | We could not get a clear before-and-after view of "Data Governance Knowledge Hub" (link) (focus never moved on (the walk ended on it)), so a person n… | left for a person | 2: forward walk read the app before it drew: P1 one stop, P2 cap 50 (inventory empty at start) on a page of 76-90 focusable elements |
| p08 | 5.H | Does Not Apply | NEEDS_REVIEW, A2 G1 | The keyboard reached 0 of the 2 form fields on this page, so 2 were not checked. | left for a person | 2: forward walk read the app before it drew: P1 one stop, P2 cap 50 (inventory empty at start) on a page of 76-90 focusable elements |
| p08 | 9.A | Fail: No skip link to bypass header | NEEDS_REVIEW, A2 G1 | other page 7 has the same content as the tested page, so comparing them would compare the page with itself | left for a person | 5: the app serves one document for every address: another page's recording is byte for byte the tested page's, read as the same page (K-01) |
| p08 | 9.B | Pass: Consistent with other pages within the Data Governance Community's microsite | NEEDS_REVIEW, A2 G1 | other page 7 has the same content as the tested page, so comparing them would compare the page with itself | left for a person | 5: the app serves one document for every address: another page's recording is byte for byte the tested page's, read as the same page (K-01) |
| p08 | 9.C | Pass: Consistent with other pages within the Data Governance Community's microsite | NEEDS_REVIEW, A2 G1 | other page 7: it has the same content as the tested page, so comparing them would compare the page with itself | left for a person | 5: the app serves one document for every address: another page's recording is byte for byte the tested page's, read as the same page (K-01) |
| p09 | 19.A | Pass: Navigation and breadcrumbs on search results (e.g. https://science.data.nasa.gov/science-discovery-engine/search/sde/search?query=%7B%22sea… | NEEDS_REVIEW, A2 G1 | other page 9 has the same content as the tested page, so comparing them would compare the page with itself | left for a person | 5: the app serves one document for every address: another page's recording is byte for byte the tested page's, read as the same page (K-01) |
| p09 | 4.C | Pass: The popup menu when you select "?" has an "X" close icon that can be focused via keyboard but not activated. However, pressing Esc exited t… | NEEDS_REVIEW, A3 G3 | Tabbing from an error state (after pressing the button in form1) did not finish (navigation). The page seems to load more content as you scroll, and… | left for a person | 21: pressing the search button navigates (the app shows results), so the error-state walk did not finish |
| p09 | 4.E | Pass | NEEDS_REVIEW, A3 G4 RC | The page has menus or sections that open to show more controls, and the Tab key did not reach every control inside some of them ("All All"), so a per… | left for a person | 7: guard RC: menus and sections that open hold controls this test does not walk yet |
| p09 | 5.B | Pass: The "All" category dropdown is an edge case (weird non-common icon, not "All Categories") but landed on the side of pass as there's only on… | NEEDS_REVIEW, A4 G3 (M4×3) | We could not finish this test, so a person needs to check it. | left for a person | 15: no <form> in the app: the header's "SDE" button joins the search field's form; "SDESDE" does not match "SDE" word for word, so J1 was asked and unsure |
| p09 | 5.C | Pass | NEEDS_REVIEW, A3 G3 (M9, M5×5, M6) | We could not tell whether what screen readers announce for "SDESDE" (button) includes everything shown next to it. Please check it with a screen read… | left for a person | 15: no <form> in the app: the header's "SDE" button joins the search field's form; "SDESDE" does not match "SDE" word for word, so J1 was asked and unsure |
| p09 | 5.D | Pass | NEEDS_REVIEW, A3 G4 RC | The page has menus or sections that open to show more controls, and this test has not checked inside them yet, so a person needs to check what they h… | left for a person | 7: guard RC: menus and sections that open hold controls this test does not walk yet |
| p09 | 9.A | Fail: No skip link to bypass header | NEEDS_REVIEW, A2 G1 | other page 9 has the same content as the tested page, so comparing them would compare the page with itself | left for a person | 5: the app serves one document for every address: another page's recording is byte for byte the tested page's, read as the same page (K-01) |
| p09 | 9.B | Pass: Consistent with other pages within the Science Discovery Engine microsite | NEEDS_REVIEW, A2 G1 | other page 9 has the same content as the tested page, so comparing them would compare the page with itself | left for a person | 5: the app serves one document for every address: another page's recording is byte for byte the tested page's, read as the same page (K-01) |
| p09 | 9.C | Pass: Consistent with other pages within the Science Discovery Engine microsite | NEEDS_REVIEW, A2 G1 | other page 9: it has the same content as the tested page, so comparing them would compare the page with itself | left for a person | 5: the app serves one document for every address: another page's recording is byte for byte the tested page's, read as the same page (K-01) |
| p10 | 19.A | Fail: Navigation only, could not find any other links or search results for this page. | NEEDS_REVIEW, A2 G1 | other page 9 has the same content as the tested page, so comparing them would compare the page with itself | left for a person | 5: the app serves one document for every address: another page's recording is byte for byte the tested page's, read as the same page (K-01) |
| p10 | 2.C | Does Not Apply | NEEDS_REVIEW, A2 G1 | We watched this page for 6.5 seconds without touching it, looking for content that is still changing by itself after 5 seconds, like a carousel, tick… | left for a person | 8: a timer longer than the watch: a day-long one that asks the server (p01, p10), or a 10 s one after which the app's content changed (p07, p08) |
| p10 | 2.D | Does Not Apply | NEEDS_REVIEW, A1 2.C-A2 G1 | We watched this page for 6.5 seconds without touching it, looking for content that is still changing by itself after 5 seconds, like a carousel, tick… | left for a person | 8: a timer longer than the watch: a day-long one that asks the server (p01, p10), or a 10 s one after which the app's content changed (p07, p08) |
| p10 | 4.A | Fail: Could not reach or select the "Search Stories" link in top nav. Could not reach or select the breadcrumb links Could reach the "Submit Your… | NEEDS_REVIEW, A3 G3 (M5, M7, M8) | "Home" (link) works with a mouse but can't be reached with the keyboard; please check whether something else on the page does the same thing. "html >… | left for a person | 4: J1 unsure on the breadcrumb "Home"; J1 said "alternative" for the header div while its reasons say "Not certain"; the key fails on controls the tool passed or never listed |
| p10 | 5.C | Pass | NEEDS_REVIEW, A3 G3 (M9, M5×3, M6) | We could not tell whether what screen readers announce for "SDESDE" (button) includes everything shown next to it. Please check it with a screen read… | left for a person | 15: no <form> in the app: the header's "SDE" button joins the search field's form; "SDESDE" does not match "SDE" word for word, so J1 was asked and unsure |
| p10 | 9.A | Fail: No skip link to bypass header | NEEDS_REVIEW, A2 G1 | other page 9 has the same content as the tested page, so comparing them would compare the page with itself | left for a person | 5: the app serves one document for every address: another page's recording is byte for byte the tested page's, read as the same page (K-01) |
| p10 | 9.B | Pass: Consistent with other pages within the Science Discovery Engine microsite | NEEDS_REVIEW, A2 G1 | other page 9 has the same content as the tested page, so comparing them would compare the page with itself | left for a person | 5: the app serves one document for every address: another page's recording is byte for byte the tested page's, read as the same page (K-01) |
| p10 | 9.C | Pass: Consistent with other pages within the Science Discovery Engine microsite | NEEDS_REVIEW, A2 G1 | other page 9: it has the same content as the tested page, so comparing them would compare the page with itself | left for a person | 5: the app serves one document for every address: another page's recording is byte for byte the tested page's, read as the same page (K-01) |
