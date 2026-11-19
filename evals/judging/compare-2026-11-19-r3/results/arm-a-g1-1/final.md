I tested both pages with the Trusted Tester tools. These are agent-assisted results, not a certified Trusted Tester result.

**Home page (https://science.data.nasa.gov/)**
- Passes: 1.3.1, 2.1.2, 2.4.1, 2.4.3, 2.4.6, 3.2.1, 3.2.3, 3.2.4, 3.3.2 and 4.1.2. The only form field is the header search box, and its visible label is a magnifier icon.
- Does not apply: 1.4.2, 2.3.1, 3.3.1, 3.3.3 and 3.3.4. The only form is a site search that accepts any input.
- Needs review:
  - 2.1.1: the keyboard check did not finish.
  - 2.2.2: the check for auto-updating content did not finish.
  - 2.4.5: only one way to reach the page (the navigation) was confirmed. The search results page did not load, so site search could not be checked.
  - 2.4.7: the focus-visibility check did not finish.
  - 3.2.2: the check did not finish inside the menus and expandable sections.

**Blog page (https://science.data.nasa.gov/blog)**
- Passes: 1.3.1, 2.1.2, 2.4.1, 2.4.3, 2.4.6, 3.2.1, 3.2.3, 3.2.4, 3.3.2 and 4.1.2. The blog page also has Category and Topic checkboxes, each with visible text labels.
- Does not apply: 1.4.2, 2.2.2, 2.3.1 and 3.3.4. The forms are search and filters.
- Needs review:
  - 2.1.1: the keyboard check did not finish.
  - 2.4.5: same site search problem as the home page.
  - 2.4.7: the check did not finish inside the menus.
  - 3.2.2: the filter checkboxes update the page as soon as you check them, with no instruction saying so. In my test, each check added "Oops, something went wrong" error banners above the filters. I judged most of these changes as content only, but I couldn't settle the check, so a person should look.
  - 3.3.1 and 3.3.3: the tool could not tell which control submits the filter form, so it could not check error handling.

RESULT: {"https://science.data.nasa.gov/": {"1.3.1": {"result": "PASS", "elements": []}, "1.4.2": {"result": "DNA", "elements": []}, "2.1.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.1.2": {"result": "PASS", "elements": []}, "2.2.2": {"result": "NEEDS_REVIEW", "elements": []}, "2.3.1": {"result": "DNA", "elements": []}, "2.4.1": {"result": "PASS", "elements": []}, "2.4.3": {"result": "PASS", "elements": []}, "2.4.5": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.6": {"result": "PASS", "elements": []}, "2.4.7": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.1": {"result": "PASS", "elements": []}, "3.2.2": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.3": {"result": "PASS", "elements": []}, "3.2.4": {"result": "PASS", "elements": []}, "3.3.1": {"result": "DNA", "elements": []}, "3.3.2": {"result": "PASS", "elements": []}, "3.3.3": {"result": "DNA", "elements": []}, "3.3.4": {"result": "DNA", "elements": []}, "4.1.2": {"result": "PASS", "elements": []}}, "https://science.data.nasa.gov/blog": {"1.3.1": {"result": "PASS", "elements": []}, "1.4.2": {"result": "DNA", "elements": []}, "2.1.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.1.2": {"result": "PASS", "elements": []}, "2.2.2": {"result": "DNA", "elements": []}, "2.3.1": {"result": "DNA", "elements": []}, "2.4.1": {"result": "PASS", "elements": []}, "2.4.3": {"result": "PASS", "elements": []}, "2.4.5": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.6": {"result": "PASS", "elements": []}, "2.4.7": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.1": {"result": "PASS", "elements": []}, "3.2.2": {"result": "NEEDS_REVIEW", "elements": ["Category and Topic filter checkboxes"]}, "3.2.3": {"result": "PASS", "elements": []}, "3.2.4": {"result": "PASS", "elements": []}, "3.3.1": {"result": "NEEDS_REVIEW", "elements": ["Category and Topic filter form"]}, "3.3.2": {"result": "PASS", "elements": []}, "3.3.3": {"result": "NEEDS_REVIEW", "elements": ["Category and Topic filter form"]}, "3.3.4": {"result": "DNA", "elements": []}, "4.1.2": {"result": "PASS", "elements": []}}}
