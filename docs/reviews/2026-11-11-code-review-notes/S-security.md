# S-security: security and safety review

Files: browser.py, capture.py, egress.py, policy.py, redact.py, access.py, frozen.py, andi.py, scrt.py, compare.py (plus resources/runs.py, resources/tt.py, tools/read_report.py, runlog.py, pagecache.py as callers).

## Overview

- The core controls are sound. The allowlist is enforced on every top-level navigation and every redirect hop, and a second check on Chrome's own normalized URL (the route) backstops Python's URL parsing. The egress proxy resolves once, checks every answer and connects to the checked address. Every browser connection goes through it, and Playwright's own API requests do too (I confirmed this). Run ownership is enforced for tools (RunRecorder.open) and resources (run_file) alike.
- No hole in the allowlist or egress was found. The weak spots are the newer "page content chooses a fetch" paths in capture.py: the media store and the chunk store (CLAUDE.md principle 5, exception 4).
- Chunk store: redirects are followed with no allowlist or same-host check (S-02). The 40 s cap is checked only before fetching starts and "a script" is not checked (S-03). Scanning is quadratic, so a 3 MB script can stall the event loop for minutes (S-01).
- Media store: URLs come straight from the page's DOM, with no allowlist, redirects followed, and no size or time limit once caps are lifted (S-04).
- `tobi_read_report` returns unclipped page/product strings from an untrusted file and has no row cap (S-06, S-07). Tool errors can echo page-chosen text from a redirect Location (S-08).
- One fail-open in access.py: a signed-in token with no `sub` makes every run readable (S-05).
- Counts: P0 0, P1 1, P2 6, P3 4.

## Findings

### S-01 Chunk store scans are quadratic and run on the event loop, so a script can stall the server
- Severity: P1
- Kind: security
- Where: src/tobi508/capture.py:331-339 (`script_refs`, `ref not in out` on a list), capture.py:386-409 (`sum(1 for e in out if e.get("size"))` per ref), capture.py:515-518 (`unrecorded_code`, same list scan on every replay)
- What: A script the page loads can name any number of distinct `import"/cN.js"` strings. Every one is kept as an entry in `out` (as "missing" if past the limit), so nothing caps the count of refs. Each ref costs a linear scan of a list, so a script of a few MB makes the scan quadratic. All of it is synchronous code on the asyncio loop, so every other run and the egress proxy stop while it runs. The same list scan runs again in `unrecorded_code` on every replay of that recording.
- Evidence: I timed `script_refs` on 5k, 10k and 20k distinct refs: 0.12 s, 0.48 s, 1.48 s (quadratic). A 3 MB script holds about 170k refs, so about 100 s here. The per-ref `sum(...)` over `out` in `_fetch_chunks` adds a second quadratic term, probably a few times worse. No script size cap applies to scripts that are only scanned (`scripts` holds every ok response and `r.text()` is read whole).
- Fix: Use a set plus an ordered list in `script_refs`, keep a running counter of fetched entries, stop adding entries after `MAX_CHUNKS` (log "N more not listed"), and cap the text scanned per script.
- Confidence: confirmed (script_refs timing); likely (the loop in `_fetch_chunks`)

### S-02 Chunk fetch follows redirects with no allowlist or same-host check on the hops
- Severity: P2
- Kind: security
- Where: src/tobi508/capture.py:349 (`ctx.request.get(ref, timeout=10_000)`), 398-403 (the checks apply to the first URL only)
- What: CLAUDE.md says a chunk must be on the same host as the script that names it and allowlisted. The code checks that for the named URL only. `ctx.request.get` follows up to 20 redirects on its own, outside the NavigationGuard, so an allowlisted same-host `/x.js` can answer 302 to any host. The body is then saved as the chunk (stored under the original URL) and replayed as that script. Egress still limits it to public addresses, but the host rule of the exception is not what runs.
- Evidence: With a browser-level proxy as in `launch_browser` and a counting proxy, `ctx.request.get("http://x.gov/a.js")` against a server answering `302 Location: http://evil.example/z.js` made the proxy see `CONNECT x.gov:80` and then 20 times `CONNECT evil.example:80`, until "Max redirect count exceeded". tests/test_lazy_chunks.py has no redirect case (grep).
- Fix: Pass `max_redirects=0` for chunk fetches (code-split chunks are plain files); a 3xx becomes `missing = "redirected"`. Same for media (S-04).
- Confidence: confirmed

### S-03 Several stated chunk limits are not enforced as written
- Severity: P2
- Kind: gap
- Where: src/tobi508/capture.py:269 and 342-364 (40 s), 359 (3 MB), 326-328 (a script), 398 (same host)
- What: (a) The 40 s limit is compared with the clock only while building the round's `todo`. `_fetch_chunk` never checks it, and each fetch may take 10 s, 8 at a time. A round of 150 files can take about 190 s, and three rounds more. (b) The 3 MB limit is tested after `got.body()` has read the whole response, so memory and time are bounded only by the 10 s timeout. (c) `_is_script(ref, ctype)` cannot fail: `ref` always ends in .js/.mjs because the regex requires it, so "a script" is not checked. An HTML soft-404 at `/x.js` is stored and later served with its own content type. (d) "Same host" compares `hostname` only, so `//a.gov:8443/x.js` passes (egress ports then decide). The "150 files" and "12 MB" limits and the 3 levels hold (read).
- Evidence: read; no test covers a slow or oversized chunk.
- Fix: Check `deadline` inside `_fetch_chunk` (and give the gather a `wait_for` of the time left); check Content-Length or stream with a cap; require a JavaScript content type or a successful `ok` and a non-HTML type; compare scheme and port as well as host.
- Confidence: confirmed (read)

### S-04 Media store fetches URLs the page names, with no allowlist, redirects followed, and no size or time bound when caps are lifted
- Severity: P2
- Kind: security
- Where: src/tobi508/capture.py:118-121 (URL list from the DOM, only `^https?:`), 124-149, 152-208
- What: `_fetch_media` takes up to 20 URLs from `<video>/<audio>` `currentSrc`/`src`/`<source>`, from every frame, and fetches each again with `ctx.request.head/get` (follows redirects, shares cookies). None is checked against the allowlist or the tested host; the page decides what the server downloads. This is not one of the four approved exceptions in principle 5. When the caller passes `no_time_limit=true`, `media_cap_mb` and `media_cap_s` become None: `left` and `deadline` are None, the GET gets `timeout=0` (none) and `got.body()` loads the whole file into memory, then `_add_media` writes it into the HAR zip. A page can name 20 huge public files.
- Evidence: read; pipeline.py:836-841 lifts the caps for an explicit `no_time_limit=true`. Egress blocks private addresses (tests cover it), so this is exposure of the server's bandwidth, memory and disk, and of cookies in the context's jar to non-allowlisted hosts, not an SSRF into the network.
- Fix: Apply `check_url` (and the same-host rule, or the redirect-free rule from S-02) to each media URL; always keep a hard ceiling (for example 500 MB total) even when the caller lifts the caps.
- Confidence: confirmed (read); likely (unbounded download when lifted)

### S-05 A signed-in token without `sub` makes every run readable
- Severity: P2
- Kind: security
- Where: src/tobi508/access.py:44-55 (`caller` returns None without `sub`), 76-86 (`may_open` returns True when `caller()` is None)
- What: Without sign-in `may_open` is open to every run, which is right for stdio. But `caller()` also returns None for an authenticated token whose claims lack `sub` (or are empty), so under AUTH=oidc such a caller reads and changes all users' runs, and `claim_run` records no owner for runs it starts (they are then closed to everyone with a `sub`). Keycloak always sets `sub`, so this needs a misconfigured or different issuer, but nothing in `build_auth` requires the claim.
- Evidence: read; callers are only runlog.py and resources/runs.py. tests/test_access_signin.py was not checked for a sub-less token.
- Fix: In AUTH=oidc mode, treat "token present but no `sub`" as denied (raise in `caller`/`may_open`), and keep None only for "no token at all" in non-auth mode.
- Confidence: likely

### S-06 `tobi_read_report` returns unclipped text from an untrusted file
- Severity: P2
- Kind: tokens
- Where: src/tobi508/tools/read_report.py:122-130 (`page`, `product`), 188-195 (`content_page`, `compare_to_page`); clipping exists only for comments and locations (`_clip`, 400 chars)
- What: `Product.P_Location` and `P_Name` of the file go into the result as they are. The file may be up to 40M characters, so one field can fill the agent's context, and it is also a free channel for instructions (the result carries an untrusted notice, but the size is unbounded). `Row.location` is clipped but `ReadResult.page` is not.
- Evidence: read; `from_scrt` copies `_text(p.get(k))` with no limit.
- Fix: Clip `page`, `product`, `content_page` and `compare_to_page` with `_clip`, or to about 200 characters.
- Confidence: confirmed

### S-07 `tobi_read_report`: no row cap, and malformed files raise non-`NotAReport` errors
- Severity: P2
- Kind: gap
- Where: src/tobi508/scrt.py:222-268 (`from_scrt`), 271-290 (`parse`); src/tobi508/tools/read_report.py:27 (`MAX_FILE_CHARS = 40_000_000`), 163-170
- What: A 40 MB JSON array of `{"TestID":"1.A"}` is about 2 million rows, each a pydantic `Row` with a `Source`; this takes gigabytes and CPU in one tool call (the tool is a plain `def`). Separately, `[{"Criteria":[1]}]` raises AttributeError, `{"TestID":5}` TypeError, `"Product":"x"` AttributeError, and a pre-SCRT file with a missing field a pydantic ValidationError, none of them `NotAReport`. `mask_error_details=True` hides the text, so the agent sees a generic error instead of "not an SCRT file".
- Evidence: ran `scrt.parse` on those four inputs: AttributeError, TypeError, AttributeError, ValidationError (the pydantic text quotes input values).
- Fix: Reject more than about 5,000 `Criteria` rows (SCRT has 61 tests plus child issues); wrap `parse` so any `AttributeError`, `TypeError` or `ValidationError` becomes `NotAReport("malformed file")`.
- Confidence: confirmed (exceptions); likely (memory)

### S-08 Page-chosen text reaches tool errors; `redact` misses some URL forms
- Severity: P2
- Kind: security
- Where: src/tobi508/redact.py:23-36 (`_URL`, `safe_url`), src/tobi508/browser.py:244-269 (`goto` messages), pipeline.py:927-930 and 995-998
- What: `safe_url` keeps the path, so for a non-http target it keeps the whole payload. A tested page's server can answer `Location: data:text/plain,IGNORE PREVIOUS INSTRUCTIONS ...` (or `https://other/<text>`); `goto` blocks it and raises `NavigationBlocked("Navigation to <that> blocked")`, which `safe_error` cuts to 200 characters and returns to the agent as the page's load error. That is page content steering text in tool output, short but unmarked. Smaller leaks in `scrub`: the regex covers only http(s)/ws(s)/file, so `ftp://user:pass@host` is left whole; and the match stops at `)`, `]`, `}`, so `?token=abc)def` leaves `def` behind.
- Evidence: ran `safe_url("data:text/plain,IGNORE PREVIOUS ...")` which returned the text; `scrub("... https://a.gov/p?token=abc)def and ftp://u:p@h/x")` gave `https://a.gov/p)def and ftp://u:p@h/x`. The run's `blocked` list keeps the raw URL too (report.json).
- Fix: In `NavigationBlocked`/`PageUnreachable` messages print only scheme and host (for non-http schemes only the scheme), never the path of a redirect target; extend `_URL` to any `scheme://` and drop userinfo generally.
- Confidence: confirmed (safe_url, scrub); likely (reaches the agent via pipeline.py:927)

### S-09 `check_url` parses some hostnames differently from Chrome; only the route re-check saves it
- Severity: P3
- Kind: security
- Where: src/tobi508/policy.py:30-52; used raw at pipeline.py:311, 329, 843, browser.py:247 (`goto`), capture.py:400
- What: `check_url("https://evil.com\\.gov/")`, `"https://evil.com%2f.gov/"`, `"https://evil.com;.gov/"` and `"http://a.gov:99999/"` are all ALLOWED by Python's `urlsplit`; Chrome would read the first as host `evil.com`. The browser is safe because `NavigationGuard._handle` runs `check_url` again on `route.request.url`, which is Chrome's normalized form (I checked: `page.goto("https://evil.com\\.gov/")` in a guarded context was recorded as blocked with URL `https://evil.com/.gov/`). So the early checks are only an early refusal, but a future use of `check_url` on a URL that never goes through a Chrome route (like the chunk fetch) would inherit the gap.
- Evidence: ran `check_url` on 23 trick URLs: userinfo, trailing dot, uppercase, `.gov.evil.com`, IP literals, `data:`, `javascript:`, `blob:`, `file://` (non-dev) are all handled correctly; the four above are the ones that differ.
- Fix: In `check_url`, require the host to match `^[a-z0-9.-]+$` (after IDNA) and reject `\`, `%`, `;` in the netloc; cheap and makes the pure function match what a browser does.
- Confidence: confirmed

### S-10 No cap on what a recording stores or on page-driven logging
- Severity: P3
- Kind: gap
- Where: src/tobi508/capture.py:60-62 (`record_har_mode="full"`), 522-553 (`_serve_media` keeps media in memory), egress.py:192-198 (a log line per refused connection), pagecache.py:61-82
- What: The HAR records every response body in full; nothing limits its total size (only the navigation and run time limits do). A page streaming gigabytes fills the runs folder, and the page cache keeps a second copy. Each refused connection (a page can issue thousands, such as `fetch('http://127.0.0.1:N')`) adds a `refused` entry and a steps.jsonl line.
- Evidence: read only; not run.
- Fix: Stop recording at a per-run byte ceiling (check the HAR size at the end and mark the run), and rate-limit or dedupe `egress_refused` log lines by host.
- Confidence: speculative

### S-11 ANDI route gaps
- Severity: P3
- Kind: gap
- Where: src/tobi508/andi.py:57-71
- What: (a) `SSA_ORIGIN + "**"` matches only `https://www.ssa.gov/`; `http://www.ssa.gov/...`, `https://www.ssa.gov:443/...` and `https://ssa.gov/` are not intercepted, so "any other www.ssa.gov request is aborted" holds only for the exact https origin. ANDI itself uses the https `host_url` (verified in tests/test_andi.py), so ANDI is never loaded from ssa.gov. (b) `serve_jquery` aborts every other `ajax.googleapis.com/ajax/libs/jquery/` request; a tested page that lazy-loads its own Google-hosted jQuery after ANDI routes are installed (labels.py:441, t9c.py:141) loses it. (c) On a tested `www.ssa.gov` page (an allowlisted `.gov`), all later requests to that origin are aborted or answered from ANDI files.
- Evidence: read.
- Fix: Route the three schemes/hosts, and for (b) and (c) fall back to the HAR route instead of aborting when the URL is not an ANDI file.
- Confidence: likely

### S-12 Egress proxy accepts any local process
- Severity: P3
- Kind: security
- Where: src/tobi508/egress.py:139-143
- What: The proxy listens on 127.0.0.1 on a random port with no credential. Any other process or container on the same host can use the server as a public-address proxy (its checks still apply). In dev mode with `dev_allowed_addresses`, it also reaches the fixture addresses.
- Evidence: read.
- Fix: Require a `Proxy-Authorization` token that the server passes to Chrome (Playwright `proxy.username/password`).
- Confidence: speculative

## Checked, holds

1. Allowlist on every top-level navigation and hop: holds. Read `NavigationGuard` (guard fetch with `max_redirects=0`, `_check` before each `goto` hop and again in `_handle` on Chrome's URL); ran `check_url` on userinfo, trailing dot, uppercase, `.gov.evil.com`, IPv6/IP literals, `data:`, `javascript:`, `blob:`, `file://` (non-dev) and observed refusals; ran a guarded context on `https://evil.com\.gov/` and saw it blocked (see S-09 for the pre-check gap). Popups and meta refresh are top-level navigation requests and take the same route; service workers are blocked (`new_context`). Iframes and subresources are not allowlist-checked, only egress-checked; this matches the docstring and the cross-site-frame support, but CLAUDE.md should say so.
2. Egress proxy: holds. Read all of egress.py; ran `address_problem` on metadata, IPv4-mapped, NAT64, 6to4, Teredo, IPv4-compatible, scoped, CGNAT, link-local and `0.0.0.0`: all refused (192.88.99.1 passes, deprecated and harmless). Resolve-once-then-connect-to-checked-address defeats rebinding; every error path in `_serve` closes the connection; `launch_browser` has no unproxied launch and sets WebRTC `disable_non_proxied_udp`. tests/test_egress.py covers rebinding, alternate IP forms, ports and redirects. The `upstream_proxy` mode re-resolves by name (documented, off by default).
3. HAR record/replay and stores: replay uses `route_from_har(not_found="abort")` plus abort routes for failed entries, so an unrecorded request never goes live. Names inside the HAR zip are `a11y-media-N.bin` and `a11y-chunk-N.js`, never page-chosen. Index JSON and HAR are parsed only from files the server wrote (frozen folder trusted). The chunk-store limits are covered in S-01 to S-03 (relative to the script, 150 files, 12 MB, 3 levels hold; redirects, 40 s, 3 MB-before-download, "a script" do not).
4. redact.py: holds for query strings, fragments and userinfo of http(s)/ws(s)/file URLs, and for the Playwright call log and multi-line messages (read, ran). Paths are kept by design, so a token in a path survives. Gaps are in S-08.
5. Run ownership: holds for tools and resources, both end in `may_open` (`RunRecorder.open`, `run_file`); another person's run reads as missing; `..` and symlinks are refused by `resolve()` plus `is_relative_to`. Run ids are 24 random bits plus a second-resolution timestamp (guessable in principle), but ownership is what protects them, so it only matters under S-05. `owner` is readable only through the owner's own `run://id/owner`. The page cache is keyed by URL and holds no per-user data (pages are fetched without credentials), so sharing it across users leaks nothing beyond stale pages (`_page_cache` has no owner file, so it is closed under sign-in).
6. scrt/compare/read_report: JSON only (no xlsx, XML or zip is parsed here, so no zip bomb or entity expansion); writing is JSON only (no formula injection). The file arrives as text, a `run://` link (ownership-checked, confined to the run folder) or, in DEV_MODE only, a local path; a hosted server never reads its own disk. Test results in a file are enum-checked and test IDs must be in the catalog. Gaps: S-06, S-07.
7. ANDI from ssa.gov: holds. `install_andi_routes` serves `third_party/andi` with a `resolve()`/`is_relative_to` check and aborts the rest of the https www.ssa.gov origin; jQuery is served from `third_party/` for one exact URL. Weak edges are in S-11.

## Unverified leads

- `RUN_ID` regex uses `$`, which accepts a trailing newline (`"abc\n"`): no escape found, only a malformed folder name.
- `GatedOIDCProxy` passes `audience=s.oidc_audience` (default None) and `required_groups` defaults to empty: with defaults any user of the realm can sign in and tokens are not audience-checked; confirm the deployment sets both.
- `_serve_media` and `_serve_chunks` register `ctx.route(lambda ...)`; whether a media URL with a query string is found by `url in stored` (exact match) was not tested.
- `frozen.load` trusts `index.json` paths (`folder / hit.har` with `..` would escape); only reachable by someone who can write the frozen folder.
- `file:` subresources are passed on with `route.continue_()` even in replay (browser.py:189-194); Chrome should refuse them from http pages, not tested.
- `read_report` runs as a sync function; whether FastMCP runs it in a thread (a 40 MB parse would otherwise stall the loop) was not checked.
- `NavigationGuard._pending_redirect` can be set by a navigation that is not the one `goto` is awaiting (meta refresh during load); result would be a wrong hop, not an allowlist bypass.
- AuditMiddleware logs the caller's email (`who`) on every call; intended, but confirm it matches the retention policy.
