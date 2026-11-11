# K review: site.py, checks/t9b.py, checks/t9c.py, checks/t19a.py

## Overview

The three checks follow their specs closely. The row tables in t9b.py and t9c.py match the spec tables in id and first-match order. 19.A's evaluate() matches A1-A5, G1-G5 and W1-W4, with one gap noted in K-06. No P0 found: I did not find a way for the code, as the spec reads, to PASS a page that no spec row passes. The worst risks are the following.

- Pages the tool cannot see are treated as "nothing found". Shadow DOM, iframes and controls ANDI skipped all lead to DNA or FAIL.
- A caller-named "other page" that is really the tested page is not refused. The tool then compares the page with itself.
- 9.C pairs `javascript:` links as "same destination".
- 19.A's live search constraints hold in the main case, but they rest on one caller (t19a.py) rather than on the recorder. Scheme and port are not compared.

Verified by running small Python snippets on make_pairs and evaluate. Everything else was verified by reading and grepping callers.

## 19.A live search and suggested pages: constraint audit

| Stated constraint | Enforced where | Verdict |
| --- | --- | --- |
| Allowlist on the search URL and on every redirect hop | pipeline.py:329 `check_url` before the load. Hops are checked by `obtain` / `record` (NavigationGuard, not re-read in full by me). | Holds. |
| Same host before and after redirects | pipeline.py:330 and 342 via `_same_site`. The final host is checked after the load. | Holds for the hostname only. `_same_site` ignores scheme and port (K-07). The HAR of an off-host landing is already recorded on disk when the check fails (harmless; it is not read). |
| GET only | By construction: `search_url` (t19a.py:154) requires `method == "get"` and `record_live` just navigates. | Holds. Gap: the submit button's `formmethod` is ignored (K-14). |
| Query is only the form's hidden fields plus the term | t19a.py:161-163. | Holds. |
| One search per run | Only because t19a.py calls `record_live` once. `record_live` itself has no counter (`n = len(report.live_pages)+1`). | Convention, not enforcement (K-07). |
| Term is T's first h1, else its title | t19a.py:166-168. h1 is `kind == "heading" and level == 1` in reading order. Cut at 80 characters. | Holds. |
| At most 5 suggested pages | `suggestions()` returns `out[:5]`. `follow_up` caps the whole `other_pages` list at 5 (`[:5]`). | Holds. The cap on total pages makes "5 suggestions" smaller when pages were already given (the call returns None at 5). |
| Suggested pages are allowlisted, same host before and after redirects, each its own HAR | Suggestions are only proposed. They come back as `other_pages` and go through `check_other_pages` and the post-record `_same_site` (pipeline.py:289-321, 1000). | Holds. |
| `other_pages` never grow from page content | `check_other_pages` takes only the caller's list. Page content only reaches the agent as text. | Holds, but see K-15 (page-controlled URLs in agent-facing text). |
| `other_pages` cannot be the tested page | pipeline.py:319 compares raw strings only. | Does not hold for equivalent URLs (K-01). |

## Findings

### K-01 Other page that is the tested page under another spelling is not refused
- Severity: P1
- Kind: false-pass-risk
- Where: /home/user/tobi508/src/tobi508/pipeline.py:319 (check); pipeline.py:1000 (post-record check); consumed by site.py:285, t9b.py:140, t9c.py:270, t19a.py:212
- What: `check_other_pages` refuses an other page only when `u.split("#")[0] == url.split("#")[0]` as strings. A trailing slash, `http` vs `https`, `index.html`, a harmless query string, or a URL that redirects to T all pass. After recording, only the host is compared (`_same_site(oc.final_url, cap.final_url)`); `final_url` equality is never checked. The tested page is then compared with its own copy. 9.B finds every component matched and in the same order, so N6 gives PASS. 9.C pairs every component by destination with identical names, so C1 gives PASS. 19.A counts the copy's menu entry for itself as a "navigation" link to T. An agent that passes "T/" as the second page gets a PASS built on nothing.
- Evidence: read of pipeline.py:289-321 and 939-1005. No `final_url ==` comparison exists anywhere in the loop (grep). No test (grep of tests for "itself").
- Fix: Normalise (scheme-insensitive, host lowercase, fragment dropped, trailing slash dropped) before the equality check, and after recording refuse an other page whose `final_url` equals the tested page's `final_url`. Also drop duplicates among the other pages by `final_url`.
- Confidence: likely (the path is plain in the code; I did not run a full run with it)

### K-02 Content in shadow DOM or iframes is invisible to 9.B, 9.C and 19.A, giving DNA or FAIL
- Severity: P1
- Kind: gap
- Where: /home/user/tobi508/src/tobi508/site.py:124-162 (`walk` uses `el.children`, never `shadowRoot`; frames are pushed as one `frame` unit and not entered); t9b.py:200-214, t9c.py:471-477, t19a.py:422-438
- What: A menu or footer built as a web component (shadow DOM) or placed in an iframe yields no units. For 9.B this gives "No navigation ... appears on the other pages", DNA (A3). For 9.C it gives "no pair", DNA. For 19.A the links to T are not found, so the page FAILs ("nothing else to check"). 9.A has a frame guard (t9a.py:286); the other three tests have none, and the report does not say content was skipped. DNA and FAIL claims then rest on a page that was only partly read.
- Evidence: read of UNITS_FN; grep for `shadow` and `'frame'` in site.py and the three checks shows nothing except kinship ignoring frame units (site.py:421-422).
- Fix: Count shadow roots and frames while reading (`PageRead.unread_scopes`), and make A3/DNA and G4/FAIL NEEDS_REVIEW when a page has any (like the cap rule N1). Walking open shadow roots in `walk` is the second step.
- Confidence: confirmed for the code path; how often real pages hit it is unknown

### K-03 9.C: if ANDI analyses few or no elements, the result is DNA; skipped controls vanish silently
- Severity: P1
- Kind: false-pass-risk (wrong DNA)
- Where: /home/user/tobi508/src/tobi508/checks/t9c.py:144-153 (`andi_output`, marks), 173-174 (`andi_name is not None` filter), 471-477 (A3 DNA)
- What: `andi_output` returns `[]`, not None, when ANDI is running but no element carries `data-andi508-index` (the "focusable elements" module analyses focusable elements only). `ran` is then True with every `andi_name` None. All components are dropped from `a` and `b`, there are no pairs, and A3 says "No link or control on this page also appears on the other pages". MARK_JS also marks elements that are not focusable (`[role=menuitem]` without tabindex, `[role=option]`, links with a role and no tabindex). ANDI never names these, so they are dropped one by one with no count and no note.
- Evidence: read of `ANDI_OUTPUT_JS` (andi.py:93-127) and `make_pairs` lines 173-174; no test of "marked but not analysed".
- Fix: Count marked components with `andi_name is None`. If every marked component of a page is unanalysed, or the share is above a small threshold, return the A2 "ANDI did not run" NEEDS_REVIEW. Mention the number of controls left out in the summary otherwise.
- Confidence: likely

### K-04 9.C: `javascript:` and similar destinations pair unrelated controls and can FAIL (verified)
- Severity: P1
- Kind: bug (wrong FAIL)
- Where: /home/user/tobi508/src/tobi508/checks/t9c.py:131 and 203 (destination key); site.py:314-323 (`norm_href` keeps the string)
- What: Links with `href="javascript:void(0)"`, `javascript:;` or any identical non-page string on two pages get the same destination key. They pair "by destination" whatever they do. Then C2 fires when one side has no name. I ran this: an unnamed `javascript:void(0)` link on T and "Close alert" on another page gives FAIL "has a name screen readers announce on one page and none on other page 1". The two are different controls. With names on both sides the pair goes to J1 and costs a question each (up to 12).
- Evidence: `make_pairs` + `evaluate` run in `uv run python -c` with two hand-built AndiPage objects.
- Fix: Give a link a destination key only when its scheme is http, https or file (and `mailto:`/`tel:` if wanted). `javascript:`, `data:` and empty fragment-only links get none, so they fall through to id, name and place.
- Confidence: confirmed

### K-05 9.C: two unnamed controls "agree" and PASS (verified)
- Severity: P2
- Kind: false-pass-risk (spec level)
- Where: /home/user/tobi508/src/tobi508/checks/t9c.py:285-289 (`_agree`), 298 (C1 before C2); spec 9c 3a C1/C2
- What: C1 is "names agree and descriptions agree", and C1 comes before C2, so a pair where both sides have no ANDI name and no description is PASS. This happens for pairs made by destination and id (C2 is meant to catch "one side has no name", but "both sides" falls into C1), and always for pairs made by place. I ran two empty-named buttons in the same banner: PASS. The PASS says "Links and controls ... have the same names for screen reader users" when there are no names. A page full of nameless icon buttons can therefore PASS 9.C on the strength of those pairs.
- Evidence: Python run of `make_pairs` + `evaluate` with two unnamed buttons; result `Outcome.PASS`.
- Fix: This is a spec decision (principle 3: PASS only on evidence). Suggest a row before C1: "both names empty" is NEEDS_REVIEW (or not an instance, with a note). Needs Abby.
- Confidence: confirmed (behaviour); the spec choice is arguable

### K-06 9.C: code differs from spec text in two places
- Severity: P2
- Kind: gap
- Where: /home/user/tobi508/src/tobi508/checks/t9c.py:203-222 (step 1 groups by href only); 316-321 (`_row` handles C5 before the table)
- What: (a) The spec edge case says same-address pairs are made "within the same region role"; step 1 ignores region role. The first pass pairs equal names anywhere. The second pass pairs the remaining in order regardless of region, so the "Home" logo in the banner can pair with a footer "Home" link or an unnamed icon link elsewhere, and then C2 or J1 follows. (b) `_row` returns C5 (dropped) when J1 = different_function and the names disagree, before `first_match`. In the spec C2 comes before C5. The branch is also redundant: the table already ends in a C5 row and C1 is first. It can only differ from the spec by letting C5 win over C2.
- Evidence: read; spec 9c section 5 first edge case, section 3a order.
- Fix: Add `region_role` to the destination group key (spec text), and delete the pre-check in `_row` (let `first_match` pick C5).
- Confidence: confirmed (text vs code); impact on real runs likely small

### K-07 19.A: `_same_site` compares host only, and "one search per run" is not enforced by the recorder
- Severity: P2
- Kind: security
- Where: /home/user/tobi508/src/tobi508/pipeline.py:281-287 (`_same_site`), 328-368 (`record_live`); t19a.py:230-243
- What: The page's own form `action` chooses the URL. `_same_site` ignores scheme and port, and `check_url` has no port rule. A form on a tested (or other) page can therefore send the tool to `http://host:8443/...` on the same hostname, or downgrade to http, and the redirect-end check passes too. `record_live` has no limit on its own: `n = len(report.live_pages) + 1` has no cap, and "one per run" is only true because t19a.py calls it once. Any future caller, or a re-entry (a second `collect`), would get more page-chosen loads. `file://` URLs also pass `_same_site` when dev mode is on (any file path), but that is dev only.
- Evidence: read of `_same_site`, `record_live`, `check_url`; grep shows `record_live` is used only in t19a.py.
- Fix: In `record_live` compare scheme and effective port with the tested page's final URL (https stays https; same port), and refuse a second call (`if report.live_pages: raise ValueError`). Add a test for an off-port action and one for a redirect off host (none found in tests/test_fixtures_19a.py).
- Confidence: confirmed for the code; impact is limited to the same hostname

### K-08 19.A repeats the live search on the follow-up run
- Severity: P2
- Kind: time
- Where: /home/user/tobi508/src/tobi508/checks/t19a.py:217-218; follow_up t19a.py:483-493
- What: The follow-up call (the same URL plus suggested pages) is a new run, so `collect` loads the live search again (up to `other_page_s`, 20 s) and reads its results again. Its earlier result (`not_found`, `cannot_run`, or even a `found` that still left fewer than two kinds) is not passed in, and the page cache does not hold live pages. Every 19.A that ends in G3 therefore pays for the search twice, plus once more for each later follow-up.
- Evidence: read of collect/follow_up; pagecache.py caches only `other_pages` recordings.
- Fix: Carry the earlier search result in the follow-up input (or key a cache on the search URL's recording), and skip the load when the same URL was already searched this session.
- Confidence: likely

### K-09 9.C loads and reads every page twice
- Severity: P2
- Kind: time
- Where: /home/user/tobi508/src/tobi508/checks/t9c.py:262-269 (`andi_page` load, then `site_read` load only for kinship); site.py:285-293
- What: `andi_page` already runs `units()` (via MARK_JS) on a fresh load of each page. When 9.A or 9.B is not in the same call, `site_read` then loads and reads the tested page again (the other pages are covered by the pagecache after the first call). It is a serial step after the ANDI gather. A `wait_for_timeout(500)` per page is also fixed.
- Evidence: read; `MARK_JS` returns only the controls and throws the rest of `units()` away.
- Fix: Return `units` and `regions` from MARK_JS too and build the `PageRead` for kinship from them (cache it under `ctx.cache["site"]`), so 9.C alone costs one load per page.
- Confidence: confirmed

### K-10 The site read has no settle step
- Severity: P2
- Kind: gap
- Where: /home/user/tobi508/src/tobi508/site.py:248-256; t9c.py:123-124; pipeline.py:134-150 (`new_page` returns at load)
- What: `read_page` reads the DOM straight after the `load` event. A menu that a script renders just after load (a framework app, or a fetch that the HAR replay answers a moment later) may not exist yet. The units are then missing, and the effects are DNA (9.B, 9.C) or FAIL (19.A), not NEEDS_REVIEW. The keyboard walk uses the settle rule; this read does not.
- Evidence: read; no fixture of a late-rendered menu found in tests (grep shows no such site read test).
- Fix: Reuse the settle helper from traverse.py (quiet window) before `READ_JS` and before MARK_JS.
- Confidence: speculative (depends on the pages)

### K-11 9.B stores every inverted pair; 9.C lists every FAIL pair
- Severity: P2
- Kind: time / tokens
- Where: /home/user/tobi508/src/tobi508/checks/t9b.py:115-126 (`c.source`, `c.visual` appended without a cap); t9b.py:226 (shown capped to 5); t9c.py:490-498 (one sentence per FAIL pair, uncapped), 500-505 (instance per non-PASS pair)
- What: For a page whose menu is reversed (right-to-left variant, a different template order) `source` and `visual` get about n^2/2 pairs. With 300 matched components that is about 45,000 two-string lists in the state, the evidence file and the run state, with a double loop in Python on the event loop for each other page (up to 50 pages with `no_time_limit`). The finding text only shows 5. 9.C's summary adds one sentence per FAIL pair, with no cap, and the same for instances; the report says it shortens long summaries, but the finding itself holds all of them.
- Evidence: read; no cap constant except `SHOWN_MAX`.
- Fix: Keep a count plus the first 20 pairs in `Cmp`; cap 9.C's sentences and instances (say "and N more").
- Confidence: confirmed (code); likelihood depends on the page

### K-12 9.B counts regions known only by position as matched components
- Severity: P2
- Kind: false-pass-risk
- Where: /home/user/tobi508/src/tobi508/checks/t9b.py:92-99 (all non-main regions become items, including keys with `|@n`); t9b.py:149 (N5 only at exactly one match); spec 9b section 5 ("regions are known by place only, so they do not match")
- What: A plain `<header>` and `<footer>` on two pages become keys `banner|@1` and `contentinfo|@1` and match. Two pairs matched is enough to skip N5 (NEEDS_REVIEW) and reach N6 PASS, as long as the regions appear in the same order, which they nearly always do. Kinship's N2o removes only the case where the other page shares almost nothing and no unit text matches. A page pair that shares two or three unit texts with different templates can still PASS on the strength of positional regions. The spec's own edge-case text says such regions "do not match".
- Evidence: read of `items` vs `kinship._named_regions` (which does drop `|@` keys); no test for this mix.
- Fix: Leave out `|@n` region keys in `items()` (same as `_named_regions`), and count `matched` from controls plus named regions.
- Confidence: likely

### K-13 Duplicated code between the checks
- Severity: P3
- Kind: design
- Where: t9b.py:154-168, t9c.py:409-423, t19a.py:323-336 (`_finding`: same body, three copies); site.py:272-282 `_cached_read` vs t9c.py:100-112 `_cached_andi` (same cache-or-read pattern); page labels built by hand in t9c.py:439 and 450 though `site.page_label` exists; the "A1 not performed" block (t9b.py:177-186, t9c.py:428-437, t19a.py:345-355)
- What: Each new multi-page test copies these. A change to the principle-2 note rule has to be made three times.
- Fix: One `site.finding(test_id, ...)` helper and one `site.not_performed(test_id, reason, rows)`; one generic `cached_read(kind, ref, reader)`.
- Confidence: confirmed

### K-14 Small gaps and dead code
- Severity: P3
- Kind: gap / dead-code
- Where and what:
  - site.py:165-176 and t19a.py:154: the submit button's `formmethod` (and `formaction`) is ignored. The method comes from the `method` attribute only, so a form whose button posts is still treated as GET.
  - t19a.py:231: `next(...)` takes the first usable form's URL; if that one is off host, `record_live` raises and the search is `cannot_run` even though a later form is on host. Filter on host before choosing.
  - t19a.py:119: the table of contents is detected only as a landmark region whose key says "contents"/"on this page"; the spec says "a region or list labelled". A labelled `<ul>` counts as "links". A region id such as `#contents` (also on `main|#contents`) matches too.
  - t19a.py:214: `search_forms` counts forms of all pages, so the same header form on 6 pages counts 6. Only zero or non-zero is used.
  - pagecache.py `_READS` grows without limit for the life of the server (each entry holds up to 600 units); `Cmp.url`, `Kin.shared_controls`, `Kinship.fingerprints` are recorded but no check reads them (the fingerprints are "for the later site-wide store").
  - t9b.py `__all__` and t19a.py `__all__` re-export `page_label`, only so the import is used.
  - t9c.py:486 `p in capped` is O(pairs x capped) list membership using pydantic equality; use a set of ids.
- Confidence: confirmed (reading)

### K-15 19.A puts page-chosen URLs and an instruction into agent text
- Severity: P2
- Kind: security / tokens
- Where: /home/user/tobi508/src/tobi508/checks/t19a.py:171-193 (`suggestions` takes `u.href` verbatim, query included), 403-413 (inserted into the finding summary with "You need not ask the user first"); follow_up t19a.py:483-493
- What: The suggested URLs come from page content (links named "home", "site map", any link to the root, breadcrumbs) and are placed unchanged in the summary the agent reads, including the query string and any text in it. A page can put an instruction into a same-host URL (`/?ignore-previous-instructions...`) and the tool then tells the agent to call again with it and not to ask the user. The agent's call is still validated (allowlist, same host), so no new URL access, but the text reaches the agent's context. The fixed sentence "You need not ask the user first" is long and repeated in every G3 result (about 60 tokens) and in the spec, so it is expected by Abby.
- Evidence: read; `suggestions` does not strip `parts.query`.
- Fix: Suggest only scheme + host + path (no query, no fragment), limit each to about 120 characters, and keep only URLs with plain URL characters. A user who cares can add a query by hand.
- Confidence: confirmed

## Unverified leads

- site.py:134: a `frame` unit's `name` comes from `el.title`, which is page text, and `kin()` ignores frames; not checked whether 9.A shows them to an agent.
- t9b.py:109: `compare` runs synchronously inside the event loop; not timed on a 50-page run.
- pipeline.py:338-341: when `wait_for_timeout` in record_live cancels `obtain`, whether the Playwright context of the half-done recording is closed was not traced.
- t9c.py:243-250 step 4 uses `c.regions[-1]`, which may be a `main|...` key for a control inside main nested in a landmark; spec says "innermost region (not main)". Not traced with a fixture.
- 9.C `J1` outcomes are only exercised with scripted answers in tests; the judge eval covers them (not run here).
- tests: no test found for an off-host or off-port live search action, a live search that redirects off host, or two live searches in one run.
