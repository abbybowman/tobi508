# Gate 2026-11-22-136d, #136: 4.A 1.19.0 on the pages it can move

Agent-assisted results, not certified Trusted Tester results. A development
rerun on the rounds' frozen pages; it never replaces any round's blind score.

## What ran

4.A 1.19.0 (Abby, 2026-11-22): a feed link's spelled-out title is not
essential (F42), and native radio buttons that share a name are probed with
the arrow keys (F40, F41). `evals/apijudge_gate.py run --date
2026-11-22-136d --round 1 --pages "search=artemis"` and `--round 2 --pages
"search,14592,14194,4914"`, `--tests 4.A --types 4.A --frozen-mode replay`,
the server judge (CLI route, `claude-sonnet-5-5`), Playwright's Chrome
153.0.8010.12. Both exited 0; every page from the freeze.

Which pages: every page of gate 2026-11-22-136b whose 4.A left an `input`
unreached (searched in its evidence), plus round 2's search page for its
RSS and Atom titles. Round 2's 5340 was left out (its one unreached input is
a search box). Compared with gate 2026-11-22-136b by each round's own key and
scorer.

## What moved

No PASS against a FAIL key.

| Round | Page | Key | 136b | Now | Why |
| --- | --- | --- | --- | --- | --- |
| 1 | p02 search | Pass | FAIL (`k1:M6`, "Last Month") | NEEDS REVIEW (`G4 RC`, no instance) | The arrow probe from "Last Year" lands on "Last Month": reached, no question. Held only by guard RC (content that opens is not checked yet, step 15) |
| 2 | p03 search | Pass | FAIL (`t18`, `t19`: M14) | NEEDS REVIEW (`G3`) | "(RSS)" and "(Atom)": "title spells out RSS format already named by the link" (M13); sort button M13 as in 136b |

Round 2 p06, p07 and p10 did not move: their unreached input is the video
player's "show more media controls", not a radio button.

## Still open on round 2's search page

Five date radio buttons ("Past week" to "This fiscal year") are still asked
as J1 and answered unsure (`k7`-`k11`: M7). Their group's stop ("All time")
was probed, but the page submits its form when a date radio changes
(`class="... submitonchange"`; the page's script triggers `#search_form`'s
submit on `change`), so ArrowDown selects "Past week" and the page reloads:
focus never rests on it and the probe cannot count it. A keyboard user can
choose them (the arrow selects and applies the filter). Counting that needs
the probe to record which radio an arrow press checked before the page
leaves; not built (asked on #136).

## Later (2026-11-22)

Abby chose option 1 (4.A 1.20.0): one ArrowDown and one ArrowUp from the
group's stop, each recording the radio it selects as the page leaves; when
both land on another radio of the group, the whole group is reached. On the
search page the five date radios are no longer asked
(`../gate-2026-11-22-136e/README.md`).
