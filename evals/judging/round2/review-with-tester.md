# Round 2: the rule results to review with the tester

Working notes for Abby's review after the reveal (2026-11-08). Every cell
here is one where the tool's result differs from the key and **a rule
decided it alone**: no agent's or judge's answer was involved, and it is
the same in every Agent A and Agent C run. Cells a judge's answer decided
are listed apart (part 4). Nothing here changes a rule or the key: each
item ends in a decision for Abby, and a rule change goes through its spec
(principle 2) with a fixture, and the full suite and judge eval after it.

Source of each "TOBI" line: Agent C repeat 1's tool reports
(`round2-armc/results/arm-c-1/runs/`); Agent A's runs say the same.
Agent-assisted results, not certified Trusted Tester results.

## 1. The tool passed or set aside a failure (principle 3: first)

| # | Page, test | Key | TOBI | My read | Decision for Abby |
| --- | --- | --- | --- | --- | --- |
| 1 | CILab, 4.A | Fail: the video plays with a mouse click, not with the keyboard | PASS (A3, G4): no pointer-only element found | The pointer scan did not see a click-to-play video as something a mouse can use. Check how the player is built (a `<video>` with a click handler on it or a cover, no focusable control) | Confirm the failing element; then a 4.A rule and fixture for a clickable video or cover with no keyboard way |
| 2 | 5340, 4.C | Fail: the embedded app (iframe) is a trap; also the "year before 1900" error popup traps | PASS: a Tab loop inside the frame (i1) ended by "pressing Enter on View timeline lets focus move on" (M4); a backward stick on OVERVIEW (M2) | M4 took activating a button inside the app as an exit, but it only moves within the app, not out of it. The popup trap needs an invalid year, which 4.C never types | Should an exit count only if focus leaves the looping set (the frame), not just moves? The popup: a 4.C step that fills fields, or left to a person? |
| 3 | 5340, 5.D | Fail: after editing name or year, Tab sends focus back to the start of the frame | PASS: none of 15 fields "moved focus on its own" | The fill pass checks where focus is right after input, not where the next Tab goes. A change of context on Tab-away would show as focus jumping back | Is "Tab after editing goes to the frame's start" a 5.D change of context (focus moved unexpectedly)? If so, compare the next stop after the edit with the walk's next stop |
| 4 | 5144, 5.D | Fail, but the comment reads as a pass: "doesn't reload the page or change where focus is, and the instructions say 'Click to select' so it's expected" | PASS | Possibly a slip in the key (Fail chosen, pass reasoning) | Is the key right? If it is a Fail, what is the change of context? |
| 5 | CILab, 9.A | Fail: no skip link for the top nav | DNA (A4): "only a link or a few words repeat on the other pages you gave" | **Caused by our pairing, not the rule:** in run 2 and in C's fresh run, CILab's other page was 14592 and 14592's was CILab, a different template, so little repeats. In run 1 (CILab with four other pages) this cell was not a missed fail | Keep A4 as is? Or a tool note when the other pages share almost nothing ("other pages may be another part of the site: needs review" instead of DNA)? |
| 6 | 14592, 9.A | Fail: no skip link for the top nav | DNA (A4) | Same as 5 | Same as 5. The same pairing also gave 9.B and 9.C DNA where the key passes (part 3) |

## 2. The tool failed what the key passes (possible catches first)

| # | Page, test | Key | TOBI | My read | Decision for Abby |
| --- | --- | --- | --- | --- | --- |
| 7 | 5340, 4.D | Pass (no comment) | FAIL (M8): "OVERVIEW" (tab) changes 0 px with focus; "Scroll down" never in view (M4, needs review) | **Possible catch.** Its off and on pictures are identical (the underline marks the selected tab, in both). Same kind as round 1's validated 4.D catch | Does OVERVIEW show focus? If not, record it in `round2/adjudications.json` |
| 8 | 14592, 14194, Galleries, 5.C | Pass: "the site search box is the only input field" | FAIL (M3): carousel scroll buttons (`…_scroll_right`) have no name | Scope: TOBI counts buttons as form components for 5.C; the key counts input fields. The unnamed buttons are real (4.1.2), whichever test owns them | Do carousel scroll buttons belong to 5.C, or to another TT test (or none of the built ones)? A scope change goes in 5.C's spec |
| 9 | Home, Help, Search, Galleries, 14194, 14592, 5144, 5340, 4914 (7 in each run), 5.A | Pass: "site search box has visual labels/instructions" | FAIL (M3): the field's only label is its placeholder | The field has a magnifier icon button and a clear button beside the "Search..." placeholder. M3 fails a placeholder-only field without asking; judge eval run 19 found a magnifier icon can label a field. Round 1's key failed nasa.gov's placeholder-only search | Does an adjacent magnifier icon button make a visible label? If yes, M3 should ask J1 (the graphic case) when an icon button sits beside the field, not fail |
| 10 | Search, 19.A | Pass: reached from the top-nav search box, and a content link on the home page | FAIL (W1, W3): only links found, and the site search for its heading did not find it | The search page is the search form's own target: submitting any search lands there. TOBI only counts search when it finds the page by its heading | Count "this page is the site search's result page" as a way? |
| 11 | 14592, 19.A | Pass: prev/next links on neighbour pages, and site search finds it | FAIL: no way found, and the search for its heading did not find it | TOBI's live search used the page's heading; check the recorded search reply (is the result list rendered by script after load?) | Look at the recorded search reply with me before any rule change |

## 3. Other differences

| # | Page, test | Key | TOBI | My read |
| --- | --- | --- | --- | --- |
| 12 | Help, Galleries, 14194, 14592, 5.B | Pass | DNA | 5.B only covers fields that have a visible label; with item 9's search field set as unlabeled, nothing is left. Follows item 9 |
| 13 | CILab, 14592, 9.B and 9.C | Pass | DNA | Same pairing as items 5-6 |
| 14 | 14592, 3.A | Not Tested | DNA | The key's Not Tested (flashing found) against TOBI finding nothing to check; worth a look at what flashes |

## 4. Cells a judge's answer decided (Agent C), for the judge eval

C's model answered every question; these false FAILs came from its
answers, in most of its three repeats. They may also hold catches:
- **4.F J1 "does not preserve"** on Home, Help, Galleries, 14194, 5144,
  5340 (5-6 per repeat): the focus-order picture questions. To check:
  whether any order is in fact confusing (a catch), or the model reads
  normal layout jumps as wrong (the judge eval with these pictures).
- **9.C J1 "inconsistent"** on Home and Help (2).
- 4.A on Home and Search, 4.D on 14592, 5.A and 5.B on Search (1-2 each).

## 5. What any agent found that the key does not have

- Item 7 (4.D OVERVIEW) and item 8 (unnamed carousel buttons) above.
- Agent B reported no FAIL the key lacks.
- Agent A's FAILs the key lacks are the tool's (items 7-11), relayed.
- Agent C's are the judge cells in part 4.
