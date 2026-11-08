I tested both pages with the Trusted Tester tools. These are agent-assisted findings, not a certified result. I left many criteria as NEEDS_REVIEW where the automated checks were incomplete or I had doubts about their result.

**https://svs.gsfc.nasa.gov/cilab/**
- **Passes:** 2.1.1, 2.1.2, 2.4.3, 2.4.7 and 3.2.1 all pass. Tabbing reached all 4 focusable elements in a sensible order, each showed focus, and nothing trapped focus or changed context on focus.
- **Does not apply:** The page has no form fields, so 1.3.1, 2.4.6, 3.2.2, 3.3.1, 3.3.2, 3.3.3, 3.3.4 and 4.1.2 are DNA. 2.4.1 is also DNA because the tool found no repeated content block to bypass.
- **Needs review:**
  - **1.4.2:** The page has audio the tool could not play or measure.
  - **2.2.2:** The tool saw a timer longer than it watched, so a person should check for auto-updating content.
  - **2.3.1:** The audio file was too large to record, so the page's media could not be checked for flashing.
  - **2.4.5:** The tool found no second way to reach this page, and its search did not find the page. I did not trust this result enough to call a fail.
  - **3.2.3 and 3.2.4:** The tool found nothing in common with the other pages, which seems unlikely for one site.

**https://svs.gsfc.nasa.gov/14592/**
- **Passes:** 2.1.1 and 3.2.1 pass. 2.1.2 also passes, but the tool could not open 15 collapsed controls or see all the lazily loaded content, so that pass is limited.
- **Fail:** 3.3.2 fails because the "Search" text field's only label is placeholder text, which disappears when you type.
- **Does not apply:** 3.3.4 is DNA because the only form is a search.
- **Needs review:**
  - **1.3.1 and 4.1.2:** The tool flagged an unnamed button, but that is not a form field. The search box's name comes only from its placeholder.
  - **2.4.6:** The search field has no visible label to judge.
  - **1.4.2 and 2.2.2:** The page has audio the tool could not measure, and it saw a long timer.
  - **2.3.1:** The flare videos did not play in the recording, so flashing could not be checked.
  - **2.4.1, 3.2.3 and 3.2.4:** The tool reported nothing in common with the other pages, which seems unlikely for one site.
  - **2.4.3:** Shift+Tab does not mirror the Tab order, and focus jumps between each Download button and its "Copy a link" button.
  - **2.4.5:** The tool found no second way to reach the page, but the page has previous/next links, a Galleries link and search.
  - **2.4.7:** The tool flagged the whole check as a fail, but it could not confirm most elements. These are the "Copy a link to this media item" buttons, the volume slider, the video elements and the "Lars Leonhard" and "Scientific Visualization Studio" links.
  - **3.2.2, 3.3.1 and 3.3.3:** The tool could not finish these on the search form.

RESULT: {"https://svs.gsfc.nasa.gov/cilab/": {"1.3.1": {"result": "DNA", "elements": []}, "1.4.2": {"result": "NEEDS_REVIEW", "elements": ["page audio"]}, "2.1.1": {"result": "PASS", "elements": []}, "2.1.2": {"result": "PASS", "elements": []}, "2.2.2": {"result": "NEEDS_REVIEW", "elements": []}, "2.3.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.1": {"result": "DNA", "elements": []}, "2.4.3": {"result": "PASS", "elements": []}, "2.4.5": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.6": {"result": "DNA", "elements": []}, "2.4.7": {"result": "PASS", "elements": []}, "3.2.1": {"result": "PASS", "elements": []}, "3.2.2": {"result": "DNA", "elements": []}, "3.2.3": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.4": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.1": {"result": "DNA", "elements": []}, "3.3.2": {"result": "DNA", "elements": []}, "3.3.3": {"result": "DNA", "elements": []}, "3.3.4": {"result": "DNA", "elements": []}, "4.1.2": {"result": "DNA", "elements": []}}, "https://svs.gsfc.nasa.gov/14592/": {"1.3.1": {"result": "NEEDS_REVIEW", "elements": ["Search... text field", "unnamed button"]}, "1.4.2": {"result": "NEEDS_REVIEW", "elements": ["video"]}, "2.1.1": {"result": "PASS", "elements": []}, "2.1.2": {"result": "PASS", "elements": []}, "2.2.2": {"result": "NEEDS_REVIEW", "elements": []}, "2.3.1": {"result": "NEEDS_REVIEW", "elements": ["flare videos"]}, "2.4.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.3": {"result": "NEEDS_REVIEW", "elements": ["Copy a link / Download buttons"]}, "2.4.5": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.6": {"result": "NEEDS_REVIEW", "elements": ["Search... text field"]}, "2.4.7": {"result": "NEEDS_REVIEW", "elements": ["Copy a link to this media item buttons", "volume slider", "Unable to play media video elements", "Lars Leonhard link", "Scientific Visualization Studio link"]}, "3.2.1": {"result": "PASS", "elements": []}, "3.2.2": {"result": "NEEDS_REVIEW", "elements": ["Search... text field"]}, "3.2.3": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.4": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.1": {"result": "NEEDS_REVIEW", "elements": ["Search... text field"]}, "3.3.2": {"result": "FAIL", "elements": ["Search... text field (placeholder-only label)"]}, "3.3.3": {"result": "NEEDS_REVIEW", "elements": ["Search... text field"]}, "3.3.4": {"result": "DNA", "elements": []}, "4.1.2": {"result": "NEEDS_REVIEW", "elements": ["Search... text field"]}}}
