I tested both pages with the Trusted Tester tools. These are agent-assisted findings, not a certified Trusted Tester result. Where a check couldn't be finished, I marked it NEEDS_REVIEW.

**Contact page (`/contact`)**
- **Passes:**
  - 1.3.1, 4.1.2 and 2.4.6: the four fields (name, email, subject, message) have visible labels that are connected to them and describe what to enter.
  - 2.1.2 and 3.2.1: focus never got trapped, and moving focus caused no change of context.
  - 2.4.1, 3.2.3 and 3.2.4: the "Skip to main content" link works, navigation order was the same on both pages, and shared links had the same names.
  - 2.4.3: focus order follows the reading order.
- **Does not apply:** 1.4.2, 2.2.2 and 2.3.1 (no audio, no moving or auto-updating content, and no flashing). I also marked 3.3.4 as DNA, because the tool found no payment, legal or data-changing form.
- **Needs review:**
  - 2.1.1: the tool couldn't finish the keyboard check.
  - 2.4.7: the tool didn't check inside the open-on-demand header menus.
  - 3.2.2, 3.3.1 and 3.3.3: not finished. The header menus weren't checked for 3.2.2, and the tool couldn't show the error messages for the other two.
  - 3.3.2: I couldn't confirm a visible label for the header search box.
  - 2.4.5: only one way to reach the page (the site navigation) could be confirmed. The search-results check hadn't loaded.

**Search page (`/search?rendered_item=test&sort_by=rel`)**
- **Fails:**
  - 1.3.1 and 4.1.2: the search-results text field and the magnifier button beside it have no accessible name. Their visible context isn't connected to them in the code.
  - 3.2.2: the "Sort:" dropdown and the four Type checkboxes (Page, News, Blog, Event) send the user to another page when changed, with no warning beforehand.
- **Passes:**
  - 2.4.6: labels describe the fields.
  - 2.1.2, 3.2.1, 2.4.1, 3.2.3 and 3.2.4: same findings as the contact page.
- **Does not apply:** 1.4.2, 2.2.2 and 2.3.1.
- **Needs review:**
  - 2.1.1 and 2.4.7: not finished.
  - 2.4.3: the Type filter's open state sent the next Tab to the page body, so I couldn't judge the order.
  - 3.3.1 and 3.3.3: error messages couldn't be shown.
  - 3.3.2: I couldn't confirm a visible label for the header search box.
  - 3.3.4: the tool couldn't tell which control submits the form.
  - 2.4.5: only one way to reach the page (the site search) could be confirmed.

RESULT: {"https://science.data.nasa.gov/contact": {"1.3.1": {"result": "PASS", "elements": []}, "1.4.2": {"result": "DNA", "elements": []}, "2.1.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.1.2": {"result": "PASS", "elements": []}, "2.2.2": {"result": "DNA", "elements": []}, "2.3.1": {"result": "DNA", "elements": []}, "2.4.1": {"result": "PASS", "elements": []}, "2.4.3": {"result": "PASS", "elements": []}, "2.4.5": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.6": {"result": "PASS", "elements": []}, "2.4.7": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.1": {"result": "PASS", "elements": []}, "3.2.2": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.3": {"result": "PASS", "elements": []}, "3.2.4": {"result": "PASS", "elements": []}, "3.3.1": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.2": {"result": "NEEDS_REVIEW", "elements": ["Search NASA science data (header search field)"]}, "3.3.3": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.4": {"result": "DNA", "elements": []}, "4.1.2": {"result": "PASS", "elements": []}}, "https://science.data.nasa.gov/search?rendered_item=test&sort_by=rel": {"1.3.1": {"result": "FAIL", "elements": ["search results text field (unnamed, Tab 11)", "magnifier search button (unnamed, Tab 13)"]}, "1.4.2": {"result": "DNA", "elements": []}, "2.1.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.1.2": {"result": "PASS", "elements": []}, "2.2.2": {"result": "DNA", "elements": []}, "2.3.1": {"result": "DNA", "elements": []}, "2.4.1": {"result": "PASS", "elements": []}, "2.4.3": {"result": "NEEDS_REVIEW", "elements": ["Type filter button and its checkboxes"]}, "2.4.5": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.6": {"result": "PASS", "elements": []}, "2.4.7": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.1": {"result": "PASS", "elements": []}, "3.2.2": {"result": "FAIL", "elements": ["Sort: select", "Page (20) checkbox", "News (15) checkbox", "Blog (12) checkbox", "Event (3) checkbox"]}, "3.2.3": {"result": "PASS", "elements": []}, "3.2.4": {"result": "PASS", "elements": []}, "3.3.1": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.2": {"result": "NEEDS_REVIEW", "elements": ["Search NASA science data (header search field)"]}, "3.3.3": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.4": {"result": "NEEDS_REVIEW", "elements": []}, "4.1.2": {"result": "FAIL", "elements": ["search results text field (unnamed, Tab 11)", "magnifier search button (unnamed, Tab 13)"]}}}
