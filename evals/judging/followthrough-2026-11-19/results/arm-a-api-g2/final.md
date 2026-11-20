I ran the Trusted Tester checks on https://www.nasa.gov/careers/. The run was agent-assisted and is not a certified Trusted Tester result.

- **Fail:** 3.3.2 fails because the "Search" text field has no visible label. Its only label is gray placeholder text that disappears when you type. Six more textboxes could not be judged: "Science and Research", "Data, IT, and Cyber", "Engineering", "Business Services", "Internships" and "Aspiring Astronauts". A person should look at them.
- **Pass:** 2.4.3 passes because focus moves through the page in reading order, forward and backward. The check for key-press timing, which is part of 2.1.1, also found nothing timed. 2.1.1 itself is still needs review, because the keyboard-access check could not finish.
- **Does not apply:**
  - 1.4.2: no audio played by itself for more than 3 seconds.
  - 3.3.4: the form has no legal or financial consequences.
- **Needs review:**
  - 2.4.1, 3.2.3, 3.2.4 and 2.4.5 compare pages, and you gave me only one page. I did not choose other pages myself, so these need a rerun with other pages from the site.
  - For 1.3.1, 2.4.6 and 4.1.2 the label checks could not finish, and 6 of the 7 form fields were not reached by keyboard.
  - For 2.1.1, 2.1.2 and 2.4.7 the keyboard checks could not finish.
  - 3.2.1 and 3.2.2 need a person: the keyboard did not reach every control in some expandable sections ("Featured Careers", "NASA Force", "Veterans and Military Spouses" and 2 more).
  - 3.3.1 and 3.3.3 could not be checked on the 6 unreached fields.
  - 2.2.2 and 2.3.1 could not be checked fully: of 39 images, 1 could not be checked for animation, and the check for content that keeps changing by itself could not finish.

The server also has one judgment question it was unsure about, and it waits for a person.

I did not save the report files. They are at run://20261119T235738Z-a636c7/report.json and run://20261119T235738Z-a636c7/pre-scrt.json, and expire on 2026-12-20.

RESULT: {"https://www.nasa.gov/careers/": {"1.3.1": {"result": "NEEDS_REVIEW", "elements": []}, "1.4.2": {"result": "DNA", "elements": []}, "2.1.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.1.2": {"result": "NEEDS_REVIEW", "elements": []}, "2.2.2": {"result": "NEEDS_REVIEW", "elements": []}, "2.3.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.3": {"result": "PASS", "elements": []}, "2.4.5": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.6": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.7": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.1": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.2": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.3": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.4": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.1": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.2": {"result": "FAIL", "elements": ["Search (text field) - only label is placeholder text"]}, "3.3.3": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.4": {"result": "DNA", "elements": []}, "4.1.2": {"result": "NEEDS_REVIEW", "elements": []}}}
