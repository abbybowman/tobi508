# A recording misses scripts a page loads only after interaction

**What cost time.** 5340's year popup and 5.D focus jump (Abby's key) could
not be reproduced in replay, in Chromium or Firefox. I first suspected the
browser.

**Why.** The page's input handler starts with `import("./chunk.js")` (code
splitting). The chunk loads on first use, so the HAR (made from a load and a
scroll pass) lacks it; in replay the import fails and the handler silently
does nothing. Interactions (typing, Tab, Enter) then look harmless.

**Check.** Search recorded scripts for `import("./...")` and compare with the
HAR's URLs. To prove a cause, route the missing file over the recording in a
scratch Playwright context (fetched live, never into the frozen archive) and
repeat the steps.

**Do.** A replay result for a page with an unrecorded chunk is not a PASS for
tests that interact (plan `2026-11-08-rules-principle3-build.md`, step 1
finding 6). Do not blame the browser first.
