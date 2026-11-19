Both pages are tested. The search page fails three criteria, and several criteria on both pages still need a person to check them. These are agent-assisted findings, not a certified Trusted Tester result.

**Contact page** (https://science.data.nasa.gov/contact)
- **PASS:**
  - 1.3.1, 2.1.2, 2.4.1, 2.4.3, 2.4.6, 3.2.1, 3.2.3, 3.2.4 and 4.1.2 pass.
  - On 1.3.1, 2.4.6 and 4.1.2, all four form fields have visible labels that are programmatically associated and descriptive.
- **DNA:** 1.4.2, 2.2.2, 2.3.1 and 3.3.4 do not apply. The 3.3.4 reason is that the contact form is not a legal, financial or data-change form.
- **NEEDS_REVIEW:**
  - 2.1.1: the tool's check of tooltip-only text and keyboard access was not finished.
  - 2.4.5: the site search results page did not finish loading, so only one way to reach the page (site navigation) was confirmed.
  - 2.4.7, 3.2.2, 3.3.1 and 3.3.3: the tool could not finish these, and nothing was checked inside the page's menus.
  - 3.3.2: the form fields are visibly labelled, but the header search field shows only a magnifier icon, so I could not tell if it has a visible label.

**Search page** (https://science.data.nasa.gov/search?rendered_item=test&sort_by=rel)
- **FAIL:**
  - 1.3.1 and 4.1.2: the results search text box (reached with 11 Tabs) and its unnamed magnifier button (13 Tabs) have no accessible name. Their visible text and icon are not connected to them in the code.
  - 3.2.2: changing the "Sort:" select, or any of the Type checkboxes (Page, News, Blog, Event), loads a new page with no warning.
- **PASS:** 2.1.2, 2.4.1, 2.4.6, 3.2.1, 3.2.3 and 3.2.4 pass.
- **DNA:** 1.4.2, 2.2.2 and 2.3.1 do not apply.
- **NEEDS_REVIEW:**
  - 2.1.1: not finished.
  - 2.4.3: the Sort drop-down sits between the search box and its button in the tab order, and the filters come after the results. I couldn't settle whether that breaks a sensible order.
  - 2.4.5: only one way to reach the page (site search) was confirmed.
  - 2.4.7: not finished, because nothing was checked inside the menus and filter sections.
  - 3.3.1, 3.3.3 and 3.3.4: the tool could not see the server's responses, so the error messages need a person to check them on the live site.
  - 3.3.2: I could not confirm a visible label for the header search field.

RESULT: {"https://science.data.nasa.gov/contact": {"1.3.1": {"result": "PASS", "elements": []}, "1.4.2": {"result": "DNA", "elements": []}, "2.1.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.1.2": {"result": "PASS", "elements": []}, "2.2.2": {"result": "DNA", "elements": []}, "2.3.1": {"result": "DNA", "elements": []}, "2.4.1": {"result": "PASS", "elements": []}, "2.4.3": {"result": "PASS", "elements": []}, "2.4.5": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.6": {"result": "PASS", "elements": []}, "2.4.7": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.1": {"result": "PASS", "elements": []}, "3.2.2": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.3": {"result": "PASS", "elements": []}, "3.2.4": {"result": "PASS", "elements": []}, "3.3.1": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.2": {"result": "NEEDS_REVIEW", "elements": ["Search NASA science data (header search field)"]}, "3.3.3": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.4": {"result": "DNA", "elements": []}, "4.1.2": {"result": "PASS", "elements": []}}, "https://science.data.nasa.gov/search?rendered_item=test&sort_by=rel": {"1.3.1": {"result": "FAIL", "elements": ["search results text field (Tab 11, no accessible name)", "unnamed magnifier search button (Tab 13)"]}, "1.4.2": {"result": "DNA", "elements": []}, "2.1.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.1.2": {"result": "PASS", "elements": []}, "2.2.2": {"result": "DNA", "elements": []}, "2.3.1": {"result": "DNA", "elements": []}, "2.4.1": {"result": "PASS", "elements": []}, "2.4.3": {"result": "NEEDS_REVIEW", "elements": ["SORT: combobox between search text field and search button", "Type filter button"]}, "2.4.5": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.6": {"result": "PASS", "elements": []}, "2.4.7": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.1": {"result": "PASS", "elements": []}, "3.2.2": {"result": "FAIL", "elements": ["Sort: select", "Page (20) checkbox", "News (15) checkbox", "Blog (12) checkbox", "Event (3) checkbox"]}, "3.2.3": {"result": "PASS", "elements": []}, "3.2.4": {"result": "PASS", "elements": []}, "3.3.1": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.2": {"result": "NEEDS_REVIEW", "elements": ["Search NASA science data (header search field)"]}, "3.3.3": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.4": {"result": "NEEDS_REVIEW", "elements": []}, "4.1.2": {"result": "FAIL", "elements": ["search results text field (Tab 11, no accessible name)", "unnamed magnifier search button (Tab 13)"]}}}
