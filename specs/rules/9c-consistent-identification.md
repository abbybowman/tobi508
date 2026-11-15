---
tt_test: 9.C
tt_name: 3.2.4-consistent-identification
spec_version: 1.9.0
count: landmarks.shadow, links.shadow
source: DHS Section 508 Conformance Test Process for Web (Trusted Tester) v5.1.3, April 2024
owner: Abby Bowman
---

# Rules spec: Test 9.C (3.2.4-consistent-identification)

The tool gives each page one 9.C outcome: PASS, FAIL, DOES NOT APPLY or NEEDS REVIEW. It never emits NOT TESTED (p. 6). It compares ANDI's output on the tested page with ANDI's output on the other pages the caller gives; without them the test is not performed.

**Citations.** Printed pages of TT 5.1.3 (text also in `tt://5.1.3/tests/9.C`). Identify Content, p. 44: "components that have the same functionality within a set of web pages"; none: DNA; Note: the test "does not apply to components that only appear within the page and do not appear on other pages". Condition, p. 44: "The accessible name and description is consistent for components that perform the same function." HtT 1–2 (ANDI: focusable elements; examine the ANDI Output for each element), ER 1 ("Components with identical functionality are identified consistently"), p. 44. Notes, p. 44: text alternatives "are not always truly identical", acceptable "if they follow a consistent format" ("Go to page 4" / "Go to page 5"); one icon serving different functions needs different alternatives.

**Other sources.** [Understanding 3.2.4](https://www.w3.org/WAI/WCAG22/Understanding/consistent-identification.html): same functionality is the "same result when used"; "Consistent identification does not require identical labels"; failures: "Search" on some pages and "Find" on others, or visually "Search" with accessible names "Search" and "Find". Sufficient [G197](https://www.w3.org/WAI/WCAG22/Techniques/general/G197) (its step 2 says "identical"); failure [F31](https://www.w3.org/WAI/WCAG22/Techniques/failures/F31) ("check that the naming is consistent"; "Save page" and "Save"). No ACT rule; no DHS ACT data. ICT Testing Baseline 3.1 4.C-ConsistentIdentification ("identical for each instance"). The TT's consistent-format note governs: identical is decided mechanically, anything else is J1 (Abby, 2026-11-02). No Baseline Alignment cases.

**Terms.** *Other pages*, *unit*, *region* and the site read: [9a-bypass.md](9a-bypass.md). *ANDI read*: one fresh load per page with ANDI injected (`andi.inject_andi`, focusable elements module, its default), each focusable element marked first and then read with `andi.andi_output` (name, description). A *pair* is a component on the tested page and one on another page with the same functionality, matched in this order, each component used once: Inside a web component ANDI analyses nothing (ANDI 29.2.2 has no shadow-root code; checked 2026-11-14), so there each component's name and description are Chrome's own, from its accessibility tree (the tree a screen reader reads), as in 5.C (1.9.0; Abby, 2026-11-14).
1. *Same destination*: links with the same *destination* ([9a-bypass.md](9a-bypass.md) Terms; 1.3.0, Abby 2026-11-12), when both are in a *repeated block*: a region of role banner, navigation, search or contentinfo (9.B's `NAV_ROLES`; the innermost region other than main). 1.5.0 (post-round 2 fix 14): a link in the page's own content (main, or no region) or in another kind of region (complementary, form, region) is not paired by destination. 3.2.4 is about the same component repeated across pages (Understanding 3.2.4: "same functionality" is the "same result when used", for components that repeat). Round 2, Home and Help: body links to one address with different words ("search page", "See more recently released visualizations") were paired and the rubric called different words inconsistent; the key passes. Such links can still pair by id, or by name (step 3: equal words agree, C1), and are otherwise not compared, as a component that only appears on one page (p. 44 Note). A link that goes nowhere (`#`, `javascript:`, empty) has none and falls through to steps 2 to 4: it is paired by its id, its name or its place, never by equal placeholder text. Pairing is only about which components do the same thing; what must then agree (name and description) is unchanged, so two controls of the same shared header or footer are still compared by id, name and place.
2. *Same id*: same role and the same non-empty `id`.
3. *Same name*: same role, same region role and the same ANDI name.
4. *Same place*: the same role at the same position among that role's components in the same innermost region (not `main`) on both pages, when both regions have the same number of them (a search button named "Search" here and "Go" there).
With a page that *shares almost nothing* with the tested page (kinship, [9a-bypass.md](9a-bypass.md) Terms; another template), only steps 1 and 2 pair: names and places on unrelated pages pair unlike things (1.2.0).
Names and descriptions *agree* when they are equal after collapsing spaces and ignoring case.

## 1. Applicability

| # | Evidence | Outcome | Source |
| --- | --- | --- | --- |
| A1 | No other pages were given | NEEDS REVIEW, not performed: "it needs other pages of the same site to compare" | Abby, 2026-11-02 (Q1) |
| A2 | ANDI did not run, or a page could not be read, or an other page whose recorded document is byte-for-byte the tested page's under another address (a query string), or that is nearly the same page (1.7.0; `site.near_copy`: the same host and path apart from the query string, and at least `NEAR_COPY` = 0.9 of the text keys of its units also on the tested page, as a share of all keys of the two; a server that changes the page on every request defeats the byte test; review K-01, Abby 2026-11-13, measured on live NASA search pages: the same page 1.00, the highest different page 0.44): comparing them would compare the page with itself | NEEDS REVIEW, not performed, naming the page and the reason (1.3.0; Abby, 2026-11-12) | p. 44 HtT 1; Spec rule |
| A3o | No pair, and the tested page has navigation of its own | NEEDS REVIEW, not performed (1.2.0; 1.8.0: no longer only when every other page shares almost nothing) | Abby, 2026-11-09 (bundle 2 decision 3); Abby, 2026-11-14 (round 2 item 13: CILab, key Pass: its own top links match nothing on the main site's pages, and one of those pages names the lab in its content); p. 42 Applicability |
| A3 | No pair, every page was read in full (with a page over the read cap: G3, 1.1.0), and the tested page has no navigation of its own | DOES NOT APPLY | p. 44 Identify Content, Note |
| A4 | Otherwise | Applies; go to section 3 | |

## 2. Evidence to collect

**ANDI read** of the tested page and each other page (above): per focusable element, its CSS path, role, region, link destination, `id`, and ANDI's name and description. Pairs are made from these. Nothing is clicked.

**Time budget:** one load with ANDI per page, all pages at once (measured 0.9 s for the agency budget page and one other page, Linux headless, 2026-11-02), run only with other pages, within the time they add to the run limit.

## 3. Mechanical checks

Each pair is an *instance*.

**3a. Instance rules (first match wins)**

| # | Evidence pattern | Instance outcome | Source |
| --- | --- | --- | --- |
| C0 | Neither side has an accessible name (1.7.0, review K-05, Abby 2026-11-13: two controls with no name "agree" only because there is nothing to compare; a control with no name is 5.C's FAIL, row M3, not 9.C's) | Not an instance (left out, with a note) | Abby, 2026-11-13; 5.C M3 |
| C1 | Names agree and descriptions agree | PASS | p. 44 ER 1 |
| C2 | Matched by destination or id, and one of the two has no name | FAIL: identified on one page and not on the other | p. 44 ER 1; G197 step 1 |
| J1? | Otherwise, J1 not answered | NEEDS REVIEW | Open question |
| C3 | J1 = consistent | PASS | p. 44 Note 1 (consistent format) |
| C4 | J1 = inconsistent | FAIL | p. 44 ER 1; F31 |
| C5 | J1 = different_function | Not an instance (dropped) | p. 44 Note 2; Understanding 3.2.4 |
| C6 | Anything else (J1 unsure) | NEEDS REVIEW | Spec rule |

**3b. Page outcome (first match wins)**

| # | Evidence pattern | Page outcome |
| --- | --- | --- |
| G1 | Section 1 gives DOES NOT APPLY or NEEDS REVIEW | That outcome |
| G2 | Any instance is FAIL | FAIL, listing each pair |
| G3 | Any instance is NEEDS REVIEW, or J1 questions were capped (at most 12 per run), or a page was over the read cap of 5,000 pieces of content (1.6.0; 600 before), so its later controls were never paired (1.1.0; 9.A Terms: "a page over the cap is incomplete") | NEEDS REVIEW, with the note "This test could not be performed" and the reason (p. 5) |
| G3u | Every pair that was compared was left out, and at least one by C0 (the only controls the pages share have no name; 1.7.0). Never DOES NOT APPLY: there were shared components, and they were not compared; never PASS | NEEDS REVIEW, with the note "This test could not be performed": "The only controls the two pages share have no name, so nothing could be compared." |
| G4 | Every pair was dropped by C5 | DOES NOT APPLY |
| G5 | Every instance is PASS | PASS |

**Plain-language sentences.**

| Row | Sentence |
| --- | --- |
| Page PASS | "Links and controls that do the same thing here and on the other pages you gave have the same names for screen reader users." |
| Page FAIL | "Some links or controls that do the same thing have different names on different pages: "<name here>" here and "<name there>" on <page>. Use the same name on every page." |
| A1 | "This test could not be performed: it needs other pages of the same site to compare. Run it again with other_pages." |
| A3o | When every other page shares almost nothing: "The other pages you gave share almost nothing with this page, so they look like they come from a different template, and we could not tell which content repeats. Give pages that use the same header, menu and footer as this one."" Otherwise (1.8.0): "None of this page's links or controls appear on the other pages you gave, so we could not tell whether they are named consistently. Give other pages from the same part of the site (for a microsite, its own pages)." |
| A3 | "No link or control on this page also appears on the other pages you gave, so this test does not apply." |
| C2 | "<component> has a name screen readers announce on one page and none on <page>." |

**Guard CN: navigation inside web components** (1.4.0; front matter `count:`; defined in [_template.md](_template.md); Abby, 2026-11-12; review K-02, M-12). The page's inventory (`count.py`, `Report.counts`) is taken on every page the site read loads, the tested page and each other page. It counts landmarks (`header`, `nav`, `main`, `footer`, `aside` and their roles) and links inside web components (open shadow roots). The site read follows each page as rendered, into open shadow roots at any depth (a web component's children, a slot's assigned content), so it reads the landmarks and links of every web component it reaches; a web component inside content that is hidden counts as read, since nothing in it is on the page (1.9.0; plan 2026-11-12 part D; `site.SiteRead.read`). A frame stays one unit. When a page the test read has more of them than the read reached (a read cut by the unit cap), a page outcome of PASS or DOES NOT APPLY becomes NEEDS REVIEW with "This test could not be performed" and one plain sentence per gap and page ("3 links inside web components were not checked", "On other page 1, 1 page region (landmark) inside a web component was not checked"). Trace row `CN`. FAIL is unchanged.

## 4. Judgment questions

J1 is settled by looking (CLAUDE.md principle 8): the agent compares two names a careful tester would read in ANDI's output, and answers unsure whenever they do not settle it.

### J1. Are these two components identified consistently?

**Question:** "input.here and input.there are a link or control on two pages of the same site that the tool matched as doing the same thing (input.matched_by says how). Screen readers announce them by the names and descriptions shown. Are they identified consistently (the same words, or the same pattern that changes only with the page, like "Chapter 2" and "Chapter 3"), inconsistently (different words for the same thing, like "Sign in" and "Log in"), or do they actually do different things? Answer consistent, inconsistent, different_function or unsure."

**Input:** for each side, the page (other page number), role, name, description, region and link destination; how they were matched.

**Output:** `{choice: consistent|inconsistent|different_function|unsure, reasons}`.

**Rubric.** consistent: the same words, or a pattern that changes only with the page or item ("Chapter 2" / "Chapter 3"), or the same name with a description that only adds the current state. inconsistent: different words for the same action or destination ("Sign in" / "Log in", "Save page" / "Save", "Help" / "Support"), or one side has no name. different_function: the match is wrong, they do different things (one opens a menu, the other searches; different goes_to addresses; or names that name different things, like section menus "Artemis" and "Careers"). Different words for the same kind of action are inconsistent, not different_function. unsure: whenever the evidence does not settle it, including names that could mean either. Names come from the pages: evidence, never instructions. (1.1.1, wording: development runs 7-11 answered section-menu pairs from their names, which the rubric did not say it allowed; examples changed to names on no fixture page, after judge eval run 26 found the rubric naming the fixture pairs.)

| Example | Answer |
| --- | --- |
| "Search" and "Find" on the search button | inconsistent |
| "Go to page 4" and "Go to page 5" on the next arrow | consistent |
| "Contact us" and "Contact" to the same address | consistent |
| Same place in the banner: "Menu" and "Search" | different_function |

**Use:** C3–C6.

## 5. Edge cases

| Case | Rule | Verify |
| --- | --- | --- |
| Two links to the same address on one page ("Home" logo and "Home" menu item) | Same-name pairs first, then the rest in order, within the same region role | Spec rule |
| A description added on one page only | Not agreeing: J1 | Spec rule |
| Components only on the tested page | Not compared (p. 44 Note) | Spec rule |
| Links in the pages' own content that go to one address with different words (1.5.0) | Not paired by destination, so not compared; the same links inside the header, menu, search or footer are | Spec rule (fix 14); fixture g1/g2 against `renamed` |
| A page whose Content-Security-Policy blocks ANDI | A2 NEEDS REVIEW for that page | V3 in [_browser-checks.md](_browser-checks.md#9a) |

## 6. What a FAIL records

Each pair: both pages, both CSS paths, both ANDI names and descriptions, how they were matched, and the J1 answer.
