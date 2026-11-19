**1. Where I struggled or felt unsure**
- **Verifier file input:** I called `input#fileInput` a FAIL for 1.3.1 and 4.1.2. I checked `labels` and `aria-label`, but I never checked `aria-labelledby`, `title`, or the computed accessible name. My summary said there was no `aria-labelledby`, and I had not verified that. The FAIL is probably right, but the evidence is thinner than I stated.
- **Keyboard and focus criteria (2.1.1, 2.1.2, 2.4.3, 2.4.7, 3.2.1, 3.2.2):** the tools gave me a DOM and accessibility snapshot, and I did no real keyboard testing. The header dropdowns, which link to `/`, and the tab buttons on the sample-files page were never exercised. Those are marked NEEDS_REVIEW, which is honest but leaves a lot undone.

**2. What I left undone or overstated**
- **Verifier navigation:** I only read the accessibility snapshot of the sample-files page. The verifier snapshot file was never opened. My claim that the header, sub-navigation and footer match on both pages, and that the verifier has search and breadcrumbs, was inferred rather than checked. The 3.2.3, 3.2.4 and 2.4.5 PASSes for the verifier are therefore weaker than I presented. I should have compared the two pages or marked them NEEDS_REVIEW.
- **Console errors:** the logs showed 5 errors on the verifier and 1 on the sample-files page. I never read them, and they might have explained broken scripts.
- **Media and motion:** the check for audio, video, marquee and autoplay elements ran only on the verifier. For the sample-files page I assumed there was nothing. I also did not look for carousels or animation in the "Featured content" region. The DNA results for 1.4.2, 2.2.2 and 2.3.1 are unverified on that page.
- **Sample-files PASSes:** I marked 2.4.6, 3.3.2 and 4.1.2 PASS from only the search box. Those are lightly supported, and DNA or NEEDS_REVIEW might have been more accurate.
- **Verifier behavior:** I never uploaded a file or triggered the verifier. Error handling (3.3.1, 3.3.3) and the report region's live behavior are untested.
- **Why:** mostly I stopped early and did not notice these gaps. I took the first sufficient-looking evidence instead of checking each claim.

**3. What would have helped**
- Keyboard-driven tools that tab through the page and report focus order, visible focus and traps.
- An accessible-name computation tool, so I would not have to piece it together from attributes.
- Console and snapshot output inline instead of as file paths I had to open separately.
- A clearer prompt on how much interaction testing is expected, such as uploading a sample file.
