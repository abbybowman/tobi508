---
tt_test: 19.A
tt_name: 2.4.5-multiple-ways
spec_version: 1.11.0
count: landmarks.shadow, links.shadow
source: DHS Section 508 Conformance Test Process for Web (Trusted Tester) v5.1.3, April 2024
owner: Abby Bowman
---

# Rules spec: Test 19.A (2.4.5-multiple-ways)

The tool gives each page one 19.A outcome: PASS, FAIL, DOES NOT APPLY or NEEDS REVIEW. It never emits NOT TESTED (p. 6). It needs other pages of the same site; without them the test is not performed. With them, it looks further itself, as a tester does: a link to the page under another address, the site map, the page's parent, child pages and the home page (1.10.0, 1.11.0).

**Citations.** Printed page 75 of TT 5.1.3 (text also in `tt://5.1.3/tests/19.A`). Identify Content: "All web pages within a set of related web pages"; EXCLUDE pages that are "the result of, or a step in, a process, such as an order confirmation form". Applicability: DNA if the page is not within a set of related pages OR is a result of, or a step in, a process. HtT 1: two or more ways to locate the page, such as site maps, site search, tables of contents, navigation menus or dropdowns, navigation trees, links between pages (not limited to these). HtT 2: "Verify that the identified techniques correctly function and lead to the web page" (2.a links and menus lead to the pages; 2.b "The search form leads to the page(s) which contains the search term"). ER 1: "At least two techniques exist"; ER 2: they "function correctly such that they lead to the correct web page".

**Other sources.** [Understanding 2.4.5](https://www.w3.org/WAI/WCAG22/Understanding/multiple-ways.html): a *process* is a "series of user actions where each action is required in order to complete an activity" (a multi-step order, a funds-transfer confirmation, search engine results); a *set of web pages* shares a purpose and author (a checkout template without the site navigation is not part of the product pages' set). Sufficient: two or more of G125 (related links), G64 (table of contents), G63 (site map: its links lead to the pages), G161 (search: a term that occurs in the set leads to a page containing it or a list of links to such pages), G126 (a list of links to all pages), G185 (the home page links to every page). No failure technique; no ACT rule; no DHS ACT data. ICT Testing Baseline 3.1 [23.A-MultipleWays](https://ictbaseline.access-board.gov/web-baselines/23MultipleWays/): the same list, the process exception, "Additional techniques ... may be available". No Baseline Alignment cases.

**Terms.**
- *Other pages*, the site read, *units*, *regions*: [9a-bypass.md](9a-bypass.md) Terms and section 2. Other pages come from the caller (CLAUDE.md principle 5); the exceptions are the live search, the alias check and the suggested pages below.
- *T*: the tested page's final URL. A link *leads to T* when its destination equals T or a verified alias of T (absolute, fragment dropped, trailing slash ignored; the alias 1.10.0).
- *Suspected alias* (1.10.0; Abby, 2026-11-14 and 2026-11-15: a tester treats `/cilab/index.html` as `/cilab/`; round 2 p05, svs.gsfc.nasa.gov/cilab/, key Pass): the destination of a link on another page the test read (a caller's page or a suggested page, 1.11.0) that is not T but differs from T only in one or more of these ways: its last path segment is a file named `index.*` or `default.*` where T's path ends in `/`, or the reverse; its scheme (`http`, `https`); a leading `www.` on the host. Any other difference (another directory, file name, host or query string) is not an alias: a link that differs from T only by its query string is another page, and not a way (Abby, 2026-11-15). A link on T itself is not counted: a link from T to T is no way to reach it.
- *Alias check* (1.10.0): only while the links to T and W5 give fewer than two kinds and a suspected alias exists. At most 3 a run, in the order their links are read (other pages in order, each in reading order). Each is loaded exactly as a caller's other page is loaded, by the same code (`pipeline.capture_other`): the allowlist on every redirect hop, the page cache, its own HAR, the 20 s share a caller-named page gets; asked for on T's host with or without its leading `www.` and ending on T's host after redirects. It is *the same page as T* (a *verified alias*) when its final address equals T's (fragment and trailing slash aside), or its recorded document is byte for byte T's (`document_sha`, K-01; Abby, 2026-11-15: no text comparison, which two thin pages under one template could pass). It is *not verified* in every other case: loaded with other bytes (another page, or a server that changes its page on every load), not loaded (not allowed, another host after redirects, no recording in replay mode, an error, out of time) or past the 3 checked. Its own links are never read or followed.
- *Kinds of way* (Abby, 2026-11-02: two ways means two different kinds, from the TT's list). A link inside a navigation, banner or contentinfo region is navigation on every page, a site map page and a search results page included: those regions are the site's shared template, not the site map's list or the search's results (1.1.0, Abby 2026-11-02):
  - *navigation*: a link to T on another page, inside a navigation, banner or contentinfo region (menus, dropdowns, trees, header and footer link lists; breadcrumbs);
  - *table of contents*: a link to T inside a region or list labelled "contents" or "on this page";
  - *site map*: a link to T, outside those regions, on another page that is a site map: a page people can see and reach from a visible link (its title or first heading says "site map" or "sitemap", or a link named so leads to it). An XML sitemap for search engines is not a way for people (1.1.0);
  - *links between pages*: a link to T anywhere else on another page (its content);
  - *search*: the site search leads to T (below), or T is the site search's own page: a search form on T or on another page submits to T (W5, 1.4.0).
- *Search form*: a form with role search, a search field, or a field named `q`, `query`, `search`, `s`, `k`, `keyword`, `keywords`, `searchterm` or `term` (the last three 1.1.0), on T or on another page.
- *Live search* (Abby, 2026-11-02: exhaust the pages first, then run the search on the live site): only when the caller's pages show fewer than two kinds and a search form exists. At most two searches per run, with the same form: the term, then, only when its results do not link to T, the term in quotation marks (1.5.0; Abby, 2026-11-08, post-round 2 fix 11: svs.gsfc.nasa.gov answered "No results for:" the plain heading of 14592, and the tester found the page searching with quotation marks). The form must submit by GET; its action URL must pass the allowlist and be on T's host (the allowlist is checked on every redirect hop, the host at the end); the term is T's first `h1`, else its title; the request carries the form's own hidden fields and the term, nothing else. Each results page is recorded as its own HAR and read like another page, whole: after its scripts have fetched what they fetch (network idle, at most 5 s), since results often arrive by script after load, and up to 2,000 units (1.5.0, fix 11). Search counts as a way when the results page links to T (HtT 2.b; G161 step 5).
- *Suggested pages* (1.11.0; Abby, 2026-11-14 and 2026-11-15: a tester goes down to a child page for a breadcrumb or a link back, up to the parent, and to the home page; replaces the pages proposed for a follow-up call, 1.1.1, which the eval runners never made and which carried no suggested page when 5 or more were given): pages of T's host that could show more ways, in this order, at most 5:
  1. *the site map*: the first link on the pages read (T and the caller's pages) named "site map", "sitemap" or "A-Z index", on T's host;
  2. *T's parent*: the address one level up from T's own path, on T's host (`/a/b/c/` and `/a/b/c.html` give `/a/b/`; `/a/b/index.html` gives `/a/`; T at the root has none). It comes from T's address, not from page content;
  3. and 4. *child pages*: the first 2 links on T, in reading order, on T's host, whose path is under T's own directory (T's path when it ends in `/`, else its path up to the last `/`) and is not T, that directory or a suspected alias of T; links to files that are not pages (an extension other than none, `html`, `htm`, `shtml`, `php`, `asp`, `aspx`, `jsp`, `cfm`) are left out. A T whose directory is the site root has no child pages (every page of the site is under it; Abby, 2026-11-15);
  5. *the home page*: the root of T's host.

  A page already given, T, a suspected alias of T and the same address twice are left out. Breadcrumbs are not suggested on their own: they are read on the pages that are checked, as any link to T is (Abby, 2026-11-15).
- *Checking the suggested pages* (1.11.0; Abby, 2026-11-15): only while fewer than two kinds are found after the caller's pages and the alias check. In the order above, one at a time; each is loaded exactly as a caller's other page is loaded (the same code and limits as the alias check, `pipeline.capture_other`) and read as another page: its links to T or a verified alias count (W1), its suspected aliases join the alias check (at most 3 a run in all). The test stops as soon as two kinds are found. A suggested page whose final address is T's, or whose document is T's byte for byte, is T itself: not a way, and not missing. A suggested page that cannot be loaded or read is *not checked*. The tool never follows any other link it reads. In all, at most 5 suggested pages, 3 aliases and 2 searches a run.
- *Process hint*: T's text has "step N of M", "review your", "confirm", "confirmation", "order summary" or "thank you for", and T has a form with a submit button.

## 1. Applicability

| # | Evidence | Outcome | Source |
| --- | --- | --- | --- |
| A1 | No other pages were given | NEEDS REVIEW, not performed: "it needs other pages of the same site; give the home page and, if the site has one, its site map" | p. 75 Identify Content; Abby, 2026-11-02 |
| A2 | A page could not be read, or an other page whose recorded document is byte-for-byte the tested page's under another address (a query string), or that is nearly the same page (1.8.0; `site.near_copy`: the same host and path apart from the query string, and at least `NEAR_COPY` = 0.9 of the text keys of its units also on the tested page, as a share of all keys of the two; a server that changes the page on every request defeats the byte test; review K-01, Abby 2026-11-13, measured on live NASA search pages: the same page 1.00, the highest different page 0.44): comparing them would compare the page with itself | NEEDS REVIEW, not performed, naming the page and the reason (1.2.0; Abby, 2026-11-12) | Spec rule |
| J1? | A process hint, J1 not answered | NEEDS REVIEW | Open question |
| A3 | J1 = process | DOES NOT APPLY | p. 75 Applicability; Understanding 2.4.5 (process) |
| A4 | J1 = unsure | NEEDS REVIEW | Spec rule |
| A5 | Otherwise | Applies; go to section 3 | |

## 2. Evidence to collect

**Site read** (shared with 9.A–9.C; each page up to 9.A's read cap, 5,000 units since 1.6.0, 600 before, so links to T further down a long page now count): adds each page's title and its search forms (action, method, the field to fill, hidden fields). **Alias check**, **suggested pages** and **live search**, only as in Terms, in that order. Nothing is pressed on the recorded pages.

**Time budget:** 240 s (1.11.0; 120 s before): at most 10 loads of up to 20 s each (5 suggested pages, 3 aliases, 2 searches) and their reads. The site read is shared with 9.A–9.C. Past its budget the test is NEEDS REVIEW (G3), never FAIL.

## 3. Mechanical checks

The instance is the page: the kinds of way found.

**3a. Way rules**

Order (1.10.0, 1.11.0): W1 and W5, then the alias check (W6, W7) while fewer than two kinds, then the suggested pages one by one (W1 and the alias check on each; W8) while still fewer than two, then the live search (W2 to W4) while still fewer than two.

| # | Evidence pattern | Result | Source |
| --- | --- | --- | --- |
| W1 | Links to T on the other pages, each classified by kind (Terms) | Kinds found | p. 75 HtT 1, 2.a |
| W2 | Fewer than two kinds, a search form, the live search allowed and run, its results link to T (outside navigation, banner and contentinfo regions, 1.1.0) | Adds search | p. 75 HtT 2.b; G161 |
| W3 | The live search ran, its results page loaded every script it asked for (1.7.0), and its results do not link to T, plain or quoted (1.5.0) | Search does not lead to T (not a way) | p. 75 ER 2 |
| W5 | A search form (Terms) on T or on another page submits by GET to T: its own `action` attribute names T's address, the query and a trailing slash aside (a form with no `action` submits to the page it is on and does not count). Submitting any search lands on T | Adds search, without the live search (1.4.0) | p. 75 HtT 1 (site search), 2.b; Abby, 2026-11-08 (post-round 2 fix 10: svs.gsfc.nasa.gov/search/, reached from the top-nav search box and a content link on the home page; key Pass) |
| W6 | The alias check found a verified alias | Its links count as links to T: W1 again with it, and W2 and W3 read the search results for it too (1.10.0) | p. 75 HtT 2.a ("lead to the web page"); Abby, 2026-11-14 (round 2 p05, CILab: one way is a link to `/cilab/index.html`; key Pass) |
| W7 | A suspected alias was not verified | Alias not verified: a way may be missed (1.10.0) | Spec rule; Abby, 2026-11-14: "never FAIL and never a match" |
| W8 | A suggested page could not be loaded or read, or no time was left to load it | Page not checked: a way may be missed (1.11.0) | Spec rule (principle 3); Abby, 2026-11-15: FAIL only when the set was checked |
| W9 | No navigation link to T was found, and a page read (a caller's page or a suggested page) has links in a navigation, banner or contentinfo region that were not shown on load (a closed menu, dropdown or mega menu; `site.PageRead.hidden_nav`) | The site navigation was not read in full: a navigation way may be missed (1.11.0). The links' addresses are in the markup, but a link counts only when the read shows it, so until the menus are opened (roadmap 6g) none of them counts as a way, and those that lead to T are named | p. 75 HtT 1 ("navigation menus or dropdowns"); Abby, 2026-11-15: "we can't say we've checked for nav links as a way if we haven't read the nav"; round 1's nasa.gov pages hide 25 to 44 of 60 to 83 links there on load |
| W4 | The search form cannot be run (POST, script only, off host, blocked, time, or longer than a caller-named page's 20 s share), or its results page was over the read cap and did not link to T (1.1.0), or its results page did not link to T and a script it asked for did not load (no response, or an error status, in its recording; 1.7.0) | Search not verified | Spec rule; roadmap step 6c (Abby, 2026-11-13): in step 6 the browser refused the results page's scripts from cdn.jsdelivr.net and the site's `/static/` (its proxy certificate was not trusted), so no search showed results and W3 gave six false FAILs. A results page drawn by script shows nothing when its scripts fail, so finding nothing there says nothing |

**3b. Page outcome (first match wins)**

| # | Evidence pattern | Page outcome |
| --- | --- | --- |
| G1 | Section 1 gives DOES NOT APPLY or NEEDS REVIEW | That outcome |
| G2 | Two or more kinds | PASS, naming them |
| G3 | Fewer than two kinds, and something was not checked: a suggested page (W8), an alias (W7), the search (W4) or closed menus (W9) (1.11.0) | NEEDS REVIEW, naming the ways found and what was not checked ("This test could not be performed" note) |
| G4 | Fewer than two kinds, every suggested page checked, no alias left unverified, no closed menu left unread (W9), and no search form or the search does not lead to T (W3) | FAIL, naming what was checked (Abby, 2026-11-02 and 2026-11-15) |
| G5 | Anything else | NEEDS REVIEW |

**Plain-language sentences.**

| Row | Sentence |
| --- | --- |
| G2 | "This page can be found in more than one way: <kinds>." |
| G3 | "We found <n> way(s) to reach this page (<kinds>) / no way to reach this page. (W9:) A link to this page is inside a closed menu on <url> that we did not open, so the site navigation may lead here. / Some pages we read have closed menus (<n> links inside them on <k> pages) that we did not open, so we cannot say the site navigation does not lead here. We could not check <the site map, the page above this one, a page below this one, the home page> (<url>): <reason>. We could not check whether <url> is this page under another address: <reason>. <the search note>. Run this test again later (tests: 19.A) and replace this result in the saved report; the other tests need not run again. A person can also search the web for pages that link to <T>." (1.11.0) |
| G4 | "We found only <kinds or 'no way'> to reach this page. We checked <the n other pages you gave, the site map, the page above this one, the home page, n pages below it and the site search (n searches)>. <the search note>. Add a second way, such as a link in the site navigation, a site map or a site search that finds it. A person can also search the web for pages that link to <T>, which may show a way we could not see." (1.11.0) |
| A1 | "This test could not be performed: it needs other pages of the same site. Run it again with other_pages (the home page and, if there is one, the site map)." |
| A3 | "This page is a step in a process (or its result), so this test does not apply." |

**Guard CN: navigation inside web components** (1.3.0; front matter `count:`; defined in [_template.md](_template.md); Abby, 2026-11-12; review K-02, M-12). The page's inventory (`count.py`, `Report.counts`) is taken on every page the site read loads, the tested page and each other page. It counts landmarks (`header`, `nav`, `main`, `footer`, `aside` and their roles) and links inside web components (open shadow roots). The site read follows each page as rendered, into open shadow roots at any depth (a web component's children, a slot's assigned content), so it reads the landmarks and links of every web component it reaches; a web component inside content that is hidden counts as read, since nothing in it is on the page (1.9.0; plan 2026-11-12 part D; `site.SiteRead.read`). A frame stays one unit. When a page the test read has more of them than the read reached (a read cut by the unit cap), a page outcome of PASS or DOES NOT APPLY becomes NEEDS REVIEW with "This test could not be performed" and one plain sentence per gap and page ("3 links inside web components were not checked", "On other page 1, 1 page region (landmark) inside a web component was not checked"). Trace row `CN`. FAIL is unchanged.

## 4. Judgment questions

J1 is settled by looking (CLAUDE.md principle 8); the agent answers unsure whenever the text does not settle it.

### J1. Is this page a step in, or the result of, a process?

**Question:** "input.text is the tested page's visible text, in order. Is this page a step in a process that must be completed in order (a checkout step, a form wizard step, a review-and-submit page) or the result of one (an order or payment confirmation, a search results page)? Answer process, not_process or unsure."

**Output:** `{choice: process|not_process|unsure, reasons}`.

**Rubric.** process: "Step 2 of 4", a review page before submitting, a confirmation number after submitting, search results. not_process: a page anyone can reach directly that only contains a form (a contact form, a newsletter sign-up, a start page for an application). unsure: whenever the text does not settle it.

**Use:** A3, A4.

## 5. Edge cases

| Case | Rule | Verify |
| --- | --- | --- |
| T is the home page | Links to it (logo, "Home") are navigation as any other | Spec rule |
| T reached only through a redirect | T is the final URL; links to the requested URL also count | Spec rule |
| A search that runs in script only (no form submission) | W4: not verified | Spec rule |
| T is the site search's results page, reached with no query | W5: search is a way; a page about searching that the form does not submit to is not | Spec rule |
| A results page that is itself a step in a process | Read only for links to T | Spec rule |

## 6. What a FAIL records

Every link to T found (page, region, name), the kinds, the search form and the live search (URL, term, whether its results link to T), each suspected alias (address, the page whose link named it, and how it was settled: the same page by address or by document, or not verified and why; 1.10.0), each suggested page in order with what came of it (checked, T itself, not needed, or not checked and why; 1.11.0), and the pages given.
