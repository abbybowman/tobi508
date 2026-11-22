---
tt_test: 9.B
tt_name: 3.2.3-consistent-navigation
spec_version: 1.10.0
count: landmarks.shadow, links.shadow
source: DHS Section 508 Conformance Test Process for Web (Trusted Tester) v5.1.3, April 2024
owner: Abby Bowman
---

# Rules spec: Test 9.B (3.2.3-consistent-navigation)

The tool gives each page one 9.B outcome: PASS, FAIL, DOES NOT APPLY or NEEDS REVIEW. It never emits NOT TESTED (p. 6). It compares the tested page with the other pages the caller gives; without them the test is not performed. It asks no questions.

**Citations.** Printed pages of TT 5.1.3 (text also in `tt://5.1.3/tests/9.B`). Identify Content, p. 43: "all navigational elements that are repeated on multiple pages"; navigational elements "provide a user the ability to locate specific information or functionality across the website", "static or interactive", and "groupings of components"; none: DNA. Applicability, p. 43: DNA to a page that "does not contain components that are repeated on other web pages". HtT 1 ("Review multiple web pages ... Do not initiate changes to the content"), HtT 2 (compare the order with the other pages; ANDI's tab order and reading order may help), p. 43. ER 1, p. 43: "Each repeated component occurs in the same relative order with regard to other repeated components on each web page where it appears." Note, p. 44: same relative order is "same position relative to other items", even "if other items are inserted or removed" (expanded menus, a secondary navigation).

**Other sources.** [Understanding 3.2.3](https://www.w3.org/WAI/WCAG22/Understanding/consistent-navigation.html): consistent "visual layout and source order"; examples: a search field, a navigation menu, a skip link; insertions and removals allowed; a change "initiated by the user" (preferences, adaptive user agents) is excepted. Sufficient [G61](https://www.w3.org/WAI/WCAG22/Techniques/general/G61) (list the repeated components; check each is in the same relative order "with regard to other repeated components", and each navigational component's links "in the same relative order"). Failure [F66](https://www.w3.org/WAI/WCAG22/Techniques/failures/F66): "check the default presentation of the navigation mechanism on each page to see if the list of links are in the same relative order"; "secondary navigation items may be in between". No ACT rule; no DHS ACT data. ICT Testing Baseline 3.1 4.B-ConsistentNavigation: "Review multiple Web pages. Do not initiate changes to the content"; navigational mechanisms are "both interactive and non-interactive" and "may or may not be contained within a block of content". No Baseline Alignment cases.

**Terms.** *Other pages*, *unit*, *region*, the site read and *kinship* (a page that *shares almost nothing* with the tested page; *navigation of its own*): [9a-bypass.md](9a-bypass.md) Terms and section 2. A *component* is a control unit (link, button, field) or a region. Components *match* across two pages when they have the same kind, the same region role, the same name (lower case, spaces collapsed) and, for links, the same destination (absolute, without the fragment unless it is a same-page link); equal ones pair by an *alignment* that keeps their order where it can (1.7.0; step 31): the longest common subsequence of the two pages' lists of components (one found once on each page weighs more than any number of repeated ones), so an extra copy of a repeated link on one page is an insertion, not a swap; copies of one key the alignment leaves on both pages, as many on each, pair in order, so a real reorder still crosses. Lists too long to align (a table of more than 6 million cells, after equal ends are paired) pair in order as in 1.6.0. A component inside the `main` landmark of either page is content, not navigation, and is left out. Order is checked two ways: *source order* (reading order; controls are compared with controls and regions with regions) and *visual order* (controls only: a comes before b when a's box ends above b's box, or they share a line and a is to the left; pairs with neither relation are not compared).

## 1. Applicability

| # | Evidence | Outcome | Source |
| --- | --- | --- | --- |
| A1 | No other pages were given | NEEDS REVIEW, not performed: "it needs other pages of the same site to compare" | Abby, 2026-11-02 (Q1); p. 43 HtT 1 |
| A2 | The tested page could not be read, or no other page is left to compare with (below) | NEEDS REVIEW, not performed, naming the page and the reason | Spec rule (1.2.0; Abby, 2026-11-12); step 26 (1.8.0) |
| A3o | No component of the tested page matches one on any other page (pages that share almost nothing are not compared, N2o), and the tested page has navigation of its own | NEEDS REVIEW, not performed (1.1.0; 1.5.0: no longer only when every other page shares almost nothing) | Abby, 2026-11-09 (bundle 2 decision 3); Abby, 2026-11-14 (round 2 item 13: CILab, key Pass: its own top links match nothing on the main site's pages, and one of those pages names the lab in its content); p. 42 Applicability |
| A3 | No component of the tested page matches one on any other page, and the tested page has no navigation of its own | DOES NOT APPLY | p. 43 Applicability |
| A4 | Otherwise | Applies; go to section 3 | |

**Which other pages are compared** (step 26, #134). An other page is left out of the comparison, and named with the reason, when it could not be read in full (it did not load, its contents could not be read, or it draws itself after loading and two reads of it, each on a fresh load, share less than 90% of their texts (`NEAR_COPY`; when they agree, the fuller read is used) (1.9.0; Abby, 2026-11-20: round 3's gate read the community home page once without part of its header, and 9.A said DOES NOT APPLY on the forum where the key fails; the forum's tag cloud, two tags more on one load, still agrees)), or when it is the tested page again: its address is the tested page's except for the query string, and its saved document is identical to the tested page's, or at least 90% of its text is the tested page's (`site.near_copy`, `NEAR_COPY` = 0.9). 9.B is decided on the other pages that are left: one is enough, as one is when only one is given (A1). Every outcome says, in its summary (the pre-SCRT comment), how many of the other pages given were compared, and which were left out and why, each named by its path, the address without the site (`SiteRead.compared_sentence`; Abby, 2026-11-20). Pages at different paths are never the tested page again, even with an identical document: some applications send the same document for every address and draw each page in the browser (round 3's p07 to p10). Sources: review K-01 (Abby, 2026-11-13; measured on live NASA search pages: the same page 1.00, the highest different page 0.44); Abby, 2026-11-20 (one usable other page is enough; a page that does not load, or a copy, is left out rather than holding the test). **Another part of the site** (1.10.0; #138 draft G, Abby 2026-11-22: a page of a smaller grouping, a microsite, is not an other page for the main site's template, and the reverse). An other page is *another part of the site* when the tested page and it both have navigation of their own (Terms) and share fewer than 2 navigation components: links and controls outside the `main` landmark with the same role, name and, for links, destination, and regions other than main with the same role and label (9.B's components; `site.shared_nav_items`, `NAV_SHARED_MIN`). It is left out and named ("/data-governance-community/home is another part of the site"), but only while at least one other page of the tested page's own part is left to compare with; when every other page would be left out, none is, and the rows read them as before. A page read only in part (the read cap) is never left out this way. Measured on rounds 1 to 3 (252 pairs, 2026-11-22): pages of one template share 4 to 48 components, a microsite and the main site 0 or 1. Fixtures: `microsite-page-left-out-beside-the-site`, `microsite-page-alone-is-not-left-out` (test_fixtures_9x.py).

## 2. Evidence to collect

Nothing of its own: the site read (fresh loads, no interaction: HtT 1 "Do not initiate changes"). For each other page: the matched components (both CSS paths, boxes), the pairs out of source order, the pairs out of visual order, and the regions found on only one page.

**Time budget:** comparisons only (milliseconds); the site read is shared with 9.A and 9.C.

## 3. Mechanical checks

Each other page is an *instance* (the tested page compared with it).

**3a. Instance rules (first match wins)**

| # | Evidence pattern | Instance outcome | Source |
| --- | --- | --- | --- |
| N1 | That page's read is incomplete (cap), including a page with no match: a capped read is never DOES NOT APPLY (1.1.0, as 9.C 1.1.0) | NEEDS REVIEW | Spec rule |
| N2 | No component matches between the two pages | Not compared (no instance) | p. 43 Applicability ("where it appears") |
| N2o | That page shares almost nothing with the tested page (another template) | Not compared (no instance); with every page like this, A3o (1.1.0) | Abby, 2026-11-09; round 2 |
| N3 | Two matched components are in the opposite source order | FAIL | p. 43 ER 1; F66; Understanding 3.2.3 ("source order") |
| N4 | Two matched components are in the opposite visual order | FAIL | F66 ("default presentation"); Understanding 3.2.3 ("visual layout") |
| N5 | Only one component matches | NEEDS REVIEW: no order to compare, and repeated items whose names changed are not matched (9.C) | Spec rule |
| N6 | Otherwise | PASS | p. 43 ER 1, Note (insertions and removals allowed) |

**3b. Page outcome (first match wins)**

| # | Evidence pattern | Page outcome |
| --- | --- | --- |
| G1 | Section 1 gives DOES NOT APPLY or NEEDS REVIEW | That outcome |
| G2 | Any instance is FAIL | FAIL, listing each pair out of order and the page it differs on |
| G3 | Any instance is NEEDS REVIEW | NEEDS REVIEW, with the note "This test could not be performed" and the reason (p. 5) |
| G4 | Every instance is PASS | PASS |

**Notes (no outcome).** Regions on the tested page that no other page has, and the reverse (a person may want to look; insertions are allowed).

**Plain-language sentences.**

| Row | Sentence |
| --- | --- |
| Page PASS | "The navigation this page shares with the other pages you gave appears in the same order on each of them." |
| Page FAIL | "Some navigation appears in a different order on another page: "<a>" comes before "<b>" here but after it on <page>. Keep repeated navigation in the same order on every page." |
| A1 | "This test could not be performed: it needs other pages of the same site to compare. Run it again with other_pages." |
| A3o | When every other page shares almost nothing: "The other pages you gave share almost nothing with this page, so they look like they come from a different template, and we could not tell which content repeats. Give pages that use the same header, menu and footer as this one."" Otherwise (1.5.0): "None of this page's navigation appears on the other pages you gave, so we could not tell whether it is consistent with theirs. Give other pages from the same part of the site (for a microsite, its own pages)." |
| A3 | "No navigation on this page appears on the other pages you gave, so this test does not apply." |
| N5 | "Only one link or control is shared with <page>, so there is no order to compare. A person should check the navigation." |

**Guard CN: navigation inside web components** (1.3.0; front matter `count:`; defined in [_template.md](_template.md); Abby, 2026-11-12; review K-02, M-12). The page's inventory (`count.py`, `Report.counts`) is taken on every page the site read loads, the tested page and each other page. It counts landmarks (`header`, `nav`, `main`, `footer`, `aside` and their roles) and links inside web components (open shadow roots). The site read follows each page as rendered, into open shadow roots at any depth (a web component's children, a slot's assigned content), so it reads the landmarks and links of every web component it reaches; a web component inside content that is hidden counts as read, since nothing in it is on the page (1.6.0; plan 2026-11-12 part D; `site.SiteRead.read`). A frame stays one unit. When a page the test read has more of them than the read reached (a read cut by the unit cap), a page outcome of PASS or DOES NOT APPLY becomes NEEDS REVIEW with "This test could not be performed" and one plain sentence per gap and page ("3 links inside web components were not checked", "On other page 1, 1 page region (landmark) inside a web component was not checked"). Trace row `CN`. FAIL is unchanged.

## 4. Judgment questions

None. Which items are navigation is decided by matching and by leaving out the main content; order is mechanical.

## 5. Edge cases

| Case | Rule | Verify |
| --- | --- | --- |
| A secondary menu or an expanded submenu on one page only | Unmatched items are ignored: insertions are allowed | p. 44 Note |
| The same link in the header and the footer | Pairs within the same region role, so they are not mixed | Spec rule |
| A link repeated on every page has an extra copy on some pages (a breadcrumb "Home" beside the top bar's, the footer logo's and the footer list's; round 3's Drupal pages, key PASS on 6) | An insertion: the alignment pairs the copies both pages have, in order, so the links between them are not reversed. Two different links swapped, or repeated links whose copies change places with a link between them, still FAIL (N3) | p. 44 Note; Fixtures m1-m3, n1-n2 |
| Items reordered with CSS (`order`, `flex-direction: row-reverse`) | Visual order catches it (N4) | Fixture |
| A mobile and a desktop copy of the menu, one hidden | Hidden units are not read | Spec rule |
| Menus that open on hover or click | Not opened (HtT 1): their hidden items are not compared | p. 43 HtT 1 |
| Two unrelated pages that both have a plain header and footer | Their regions are known by place only, so they do not match: N2o, then A3o (before 1.1.0 they looked consistent) | Fixture e3 |
| No `main` landmark on a page | Nothing is left out as content on that page | Spec rule |

## 6. What a FAIL records

The other page; each pair out of order (names, CSS paths on both pages, source or visual); the matched components in order on both pages.
