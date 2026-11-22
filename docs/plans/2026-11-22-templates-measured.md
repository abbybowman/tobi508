# Templates for 9.A to 9.C, measured (#138, 2026-11-22)

Agent-assisted results, not certified Trusted Tester results.

**Method.** 9.B alone on every page of rounds 1 to 3 (29 pages), replay,
from the verified freezes, each page with its round's other pages (252
pairs). For each pair: the named regions they share, and 9.B's matched
components (links and controls outside `main` with the same role, name
and, for links, destination). Scratch runs, not kept.

**Named regions do not separate templates.** nasa.gov's search page
(round 1 p02) and naca-at-110 (p07) have 2 named regions; same-template
pages share 1 of them (50%), as low as a microsite pair.

**Shared navigation items do.**

| Pairs | Shared items |
| --- | --- |
| Round 1, all 72 (one template) | 9 to 43 |
| Round 2, svs pages with each other (72) | 6 or more (all N6) |
| Round 2, CILab with any svs page (18) | 0 |
| Round 3, main-site pages with each other | 46 to 48 |
| Round 3, community home with forum | 19 |
| Round 3, SDE home with MySearchStory | 4 |
| Round 3, a microsite page with a main-site page, or the two microsites | 0 or 1 |

### Draft G: another part of the site (9.A, 9.B, 9.C)

In 9a-bypass.md section 1 ("Which other pages are compared"), shared by
9.B and 9.C:

> An other page is *another part of the site* when it shares fewer than 2
> navigation items with the tested page: links and controls outside the
> `main` landmark with the same role, the same name and, for links, the
> same destination (9.B's match). It is left out of the comparison and
> named, as a page that could not be read is ("Left out:
> /data-governance-community/home is another part of the site"); the test
> is decided on the pages of the tested page's own part. With none left,
> A3o (NEEDS REVIEW: "Give other pages from the same part of the site (for
> a microsite, its own pages)"). (#138, Abby 2026-11-22: a page of a
> smaller grouping, a microsite, is not an other page for the main site's
> template, and the reverse.)

Supersedes draft F.

**Built (Abby approved G, 2026-11-22), with two refinements the fixtures
required.** 9.A's ACT cases and four 9.x fixtures are pages with no
navigation of their own, or with one other page given; G as drafted left
those out too. So: (1) only when both pages have navigation of their own
(9.A Terms); (2) only while a page of the tested page's own part is left
to compare with (none is left out otherwise, so no outcome appears where
there was none). Components counted as 9.B counts them (links, controls
and regions outside main), as measured. No existing fixture's expected
outcome changed. Round 3 p01 from the freeze: 9.B PASS (key Pass), the
four microsite pages named as left out.

## Draft H: navigation inside `main` (9.B)

In 9b-consistent-navigation.md Terms, replacing "A component inside the
`main` landmark of either page is content, not navigation, and is left
out.":

> A component inside the `main` landmark of either page is content, not
> navigation, and is left out, except a navigation region (`nav`, role
> navigation) or a breadcrumb trail (19.A Terms) inside `main`: its links
> and controls are navigation components (9.B 1.11.0; #138, Abby
> 2026-11-22; Baseline 4.B: navigational mechanisms "may or may not be
> contained within a block of content"; TT p. 43: "groupings of
> components").

Fixtures (`test_fixtures_9x.py`): a section menu inside `main`, the same
order on the other page (PASS) and two items swapped (FAIL; PASS today,
since it is left out). No round's cell is known to depend on it.

## 19b measured (2026-11-22): 9.C pairing by function

**Method.** 9.C alone (judge off; the controls only) on every page of
rounds 2 and 3 from the verified freezes, each page with its round's other
pages. For each pair of pages, the controls 9.C left unpaired in the pages'
own content (not banner, navigation, search or footer), counted by each
candidate rule (scratch script, not kept).

| Candidate | Pairs found (rounds 2 and 3) | What they are |
| --- | --- | --- |
| Buttons and fields, the same first word, different names | 0 | |
| Buttons and fields at the same place (same CSS path), different names | 0 | |
| Links at the same place, different names | 83 | all different functions: topic tags ("Sun" / "Universe", "Heliophysics" / "Astrophysics"), people ("Tom Bridgman" / "Claire Andreoli") on round 2's leaf pages |
| The same picture | not measured: ANDI's read keeps no image address | |

So no candidate rule moves a cell on these rounds, and pairing links by
place would send the judge 83 pairs that are all "different function" (and
risk false FAILs). Round 3 p07 to p10's 9.C cells (the issue's target) are
not about pairing: on the original freeze p07 to p09 are A3o and p10 is
DOES NOT APPLY (A3, also on `main`): without #134's added code files
MySearchStory does not draw its navigation. Gate 2026-11-20-134 ran round 3
from its copy with those files (A3o there).
