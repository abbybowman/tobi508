Neither page got a FAIL on a clear-cut basis except one on the blog page. The tools could not finish 2.1.1 and 2.4.7 on either page, and 2.4.5 stayed open on both. Results come from an agent-assisted run, not a certified Trusted Tester result.

**Home page (https://science.data.nasa.gov/)**
- **NEEDS_REVIEW**
  - 2.1.1: the tool could not finish the keyboard-access check.
  - 2.2.2: the auto-updating check could not be performed.
  - 2.4.5: only one way to reach the page was found (site navigation). The site search results page did not load, so it could not be checked.
  - 2.4.7: the focus-visible check could not be finished.
  - 3.2.2: menus and expandable sections were not checked.
- **DNA:** 1.4.2, 2.3.1, 3.3.1, 3.3.3, 3.3.4.
  - 3.3.1 and 3.3.3 are DNA because the only form is a site search that accepts anything.
- **PASS:** 1.3.1, 2.1.2, 2.4.1, 2.4.3, 2.4.6, 3.2.1, 3.2.3, 3.2.4, 3.3.2, 4.1.2.
  - The search field's visible label is a magnifier icon, which I judged to be enough for 3.3.2 and 2.4.6.

**Blog page (https://science.data.nasa.gov/blog)**
- **FAIL: 3.2.2.** The tool confirmed that checking the "Earth Science (8)" filter checkbox moves keyboard focus on its own, with no warning.
  - The other filter checkboxes also change part of the page, and error banners ("Oops, something went wrong") appeared when I checked them.
  - I could not tell from the screenshots whether those other changes alter the page's purpose, so they are unconfirmed.
  - The other checkboxes are Data Spotlights (10), Training (1), My Search Stories (9), Program Highlights (2), Technology Updates (9), Astrophysics (3), Biological and Physical Sciences (3), Heliophysics (4) and Planetary Science (5).
  - Nothing on the page says the filters update the list or move focus.
- **NEEDS_REVIEW**
  - 2.1.1: the keyboard-access check could not be finished.
  - 2.4.5: only one way to reach the page was found; search results could not be checked.
  - 2.4.7: the focus-visible check could not be finished.
  - 3.3.1 and 3.3.3: the tool could not tell whether the page validates the form, so a person should check how the filters report errors.
- **DNA:** 1.4.2, 2.2.2, 2.3.1, 3.3.4.
- **PASS:** 1.3.1, 2.1.2, 2.4.1, 2.4.3, 2.4.6, 3.2.1, 3.2.3, 3.2.4, 3.3.2, 4.1.2.

RESULT: {"https://science.data.nasa.gov/": {"1.3.1": {"result": "PASS", "elements": []}, "1.4.2": {"result": "DNA", "elements": []}, "2.1.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.1.2": {"result": "PASS", "elements": []}, "2.2.2": {"result": "NEEDS_REVIEW", "elements": []}, "2.3.1": {"result": "DNA", "elements": []}, "2.4.1": {"result": "PASS", "elements": []}, "2.4.3": {"result": "PASS", "elements": []}, "2.4.5": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.6": {"result": "PASS", "elements": []}, "2.4.7": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.1": {"result": "PASS", "elements": []}, "3.2.2": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.3": {"result": "PASS", "elements": []}, "3.2.4": {"result": "PASS", "elements": []}, "3.3.1": {"result": "DNA", "elements": []}, "3.3.2": {"result": "PASS", "elements": []}, "3.3.3": {"result": "DNA", "elements": []}, "3.3.4": {"result": "DNA", "elements": []}, "4.1.2": {"result": "PASS", "elements": []}}, "https://science.data.nasa.gov/blog": {"1.3.1": {"result": "PASS", "elements": []}, "1.4.2": {"result": "DNA", "elements": []}, "2.1.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.1.2": {"result": "PASS", "elements": []}, "2.2.2": {"result": "DNA", "elements": []}, "2.3.1": {"result": "DNA", "elements": []}, "2.4.1": {"result": "PASS", "elements": []}, "2.4.3": {"result": "PASS", "elements": []}, "2.4.5": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.6": {"result": "PASS", "elements": []}, "2.4.7": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.1": {"result": "PASS", "elements": []}, "3.2.2": {"result": "FAIL", "elements": ["Earth Science (8) filter checkbox (focus moves on its own); other filter checkboxes unconfirmed: Data Spotlights (10), Training (1), My Search Stories (9), Program Highlights (2), Technology Updates (9), Astrophysics (3), Biological and Physical Sciences (3), Heliophysics (4), Planetary Science (5)"]}, "3.2.3": {"result": "PASS", "elements": []}, "3.2.4": {"result": "PASS", "elements": []}, "3.3.1": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.2": {"result": "PASS", "elements": []}, "3.3.3": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.4": {"result": "DNA", "elements": []}, "4.1.2": {"result": "PASS", "elements": []}}}
