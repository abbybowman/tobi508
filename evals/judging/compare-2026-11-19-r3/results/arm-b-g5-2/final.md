I only checked these pages with a DOM and accessibility-tree inspection plus one 12-second wait. I did not test keyboard behavior or focus styling by hand. Because of that, most keyboard and focus results below are NEEDS_REVIEW rather than PASS.

**Home page**
- **1.3.1 – FAIL:** The search textbox has no `<label>`, no `aria-label` and no `aria-labelledby`. It has only a placeholder, "Type to search...".
- **4.1.2 – NEEDS_REVIEW:** The textbox gets an accessible name only from the placeholder fallback. There is no visible label for the name to match.
- **2.4.6 and 3.3.2 – NEEDS_REVIEW:** The placeholder does describe the field's purpose, but there is no persistent visible label or instruction.
- **2.4.1 – NEEDS_REVIEW:** There is no skip link and no `main` landmark. The header has only a handful of controls before the content, so a person should decide whether that is a failure.
- **2.4.7 – NEEDS_REVIEW:** The search input has `focus:outline-none`, and the buttons have `focus:ring-0 focus:outline-none`. Focus may be invisible, which needs a visual check.
- **1.4.2 – DNA:** There is no audio or video.
- **2.2.2 – PASS:** I saw no moving or auto-updating content.
- **2.3.1 – PASS:** I saw no flashing content.
- **2.1.1, 2.1.2, 2.4.3, 3.2.1, 3.2.2 – NEEDS_REVIEW:** These need hands-on keyboard testing of the "All" dropdown, the SDE menu, the microphone button and the search button.
- **3.2.3 and 3.2.4 – NEEDS_REVIEW:** Needs a cross-page comparison. The site is a single-page app and the header appears to be consistent.
- **3.3.1, 3.3.3, 3.3.4 – DNA:** There is no input validation, and nothing legal, financial or data-submitting.
- **2.4.5 – NEEDS_REVIEW:** I found no site map, and no navigation beyond the Search Stories link and search.

**My Search Stories page**
- **1.3.1, 2.4.6, 3.3.2, 4.1.2 – DNA:** There are no form fields.
- **2.1.1 – NEEDS_REVIEW:** Each story card ("How Cities and Suburbs Affect Chesapeake Bay", "Moon Trees" and others) is a clickable `div` with `cursor:pointer` and no tabindex. A SEARCH button sits inside each card and may give keyboard users the same action. A person should check this.
- **2.2.2 – PASS:** The story carousel (1 / 6) did not advance over 12 seconds, and it has previous and next buttons.
- **2.4.1 – NEEDS_REVIEW:** There is no skip link and no `main` landmark.
- **2.4.7 – NEEDS_REVIEW:** The buttons have `focus:outline-none`, so focus may be invisible.
- **1.4.2 – DNA:** There is no audio or video.
- **2.3.1 – PASS:** I saw no flashing content.
- **2.1.2, 2.4.3, 3.2.1, 3.2.2 – NEEDS_REVIEW:** These need hands-on keyboard testing of the carousel and the "Submit Your Story" button.
- **3.2.3 and 3.2.4 – NEEDS_REVIEW:** Needs a cross-page comparison. The header matches the home page.
- **2.4.5 – NEEDS_REVIEW:** There is a breadcrumb, but whether the site offers multiple ways to find pages needs review.
- **3.3.1, 3.3.3, 3.3.4 – DNA:** There is no input validation, and nothing legal, financial or data-submitting.

RESULT: {"https://science.data.nasa.gov/science-discovery-engine/search/sde/home": {"1.3.1": {"result": "FAIL", "elements": ["input[type=text] placeholder 'Type to search...' (no label, aria-label or labelledby)"]}, "1.4.2": {"result": "DNA", "elements": []}, "2.1.1": {"result": "NEEDS_REVIEW", "elements": ["All dropdown", "SDE menu", "Microphone button"]}, "2.1.2": {"result": "NEEDS_REVIEW", "elements": []}, "2.2.2": {"result": "PASS", "elements": []}, "2.3.1": {"result": "PASS", "elements": []}, "2.4.1": {"result": "NEEDS_REVIEW", "elements": ["no skip link, no main landmark"]}, "2.4.3": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.5": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.6": {"result": "NEEDS_REVIEW", "elements": ["search input (placeholder only)"]}, "2.4.7": {"result": "NEEDS_REVIEW", "elements": ["search input and buttons with focus:outline-none"]}, "3.2.1": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.2": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.3": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.4": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.1": {"result": "DNA", "elements": []}, "3.3.2": {"result": "NEEDS_REVIEW", "elements": ["search input (placeholder only, no visible label)"]}, "3.3.3": {"result": "DNA", "elements": []}, "3.3.4": {"result": "DNA", "elements": []}, "4.1.2": {"result": "NEEDS_REVIEW", "elements": ["search input (name only from placeholder)"]}}, "https://science.data.nasa.gov/science-discovery-engine/search/sde/MySearchStory": {"1.3.1": {"result": "DNA", "elements": []}, "1.4.2": {"result": "DNA", "elements": []}, "2.1.1": {"result": "NEEDS_REVIEW", "elements": ["story card divs with cursor:pointer and no tabindex"]}, "2.1.2": {"result": "NEEDS_REVIEW", "elements": []}, "2.2.2": {"result": "PASS", "elements": []}, "2.3.1": {"result": "PASS", "elements": []}, "2.4.1": {"result": "NEEDS_REVIEW", "elements": ["no skip link, no main landmark"]}, "2.4.3": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.5": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.6": {"result": "DNA", "elements": []}, "2.4.7": {"result": "NEEDS_REVIEW", "elements": ["buttons with focus:outline-none"]}, "3.2.1": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.2": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.3": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.4": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.1": {"result": "DNA", "elements": []}, "3.3.2": {"result": "DNA", "elements": []}, "3.3.3": {"result": "DNA", "elements": []}, "3.3.4": {"result": "DNA", "elements": []}, "4.1.2": {"result": "DNA", "elements": []}}}
