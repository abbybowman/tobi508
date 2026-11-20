I ran the Trusted Tester checks on the page, answered the judgment questions they left open, and re-ran the multi-page checks with three other pages from the site. Five criteria still need a person to check them.

- **2.1.1 Keyboard:** The keyboard-access check could not finish. The check for key timing passed.
- **2.2.2 Pause, Stop, Hide:** Nothing moved or blinked, but the check for content that updates by itself could not be performed.
- **2.4.1 Bypass Blocks:** This check could not finish even with the other pages supplied. The page does have a "Skip to main content" link, but I did not confirm that it works.
- **2.4.5 Multiple Ways:** The tool found one way to reach the page, the site navigation. It could not run the site search check.
- **2.4.7 Focus Visible:** 91 elements showed focus clearly. The "˄ Top" button scrolled out of view before the tool could check it, so a person needs to look at it.

I reported 1.4.2 and 2.3.1 as DNA because the tool did. Nothing played audio or flashed.

The error and form criteria (3.3.1, 3.3.3, 3.3.4) are DNA because the only form is the site search, which accepts any input and has no consequences.

RESULT: {"https://www.section508.gov/": {"1.3.1": {"result": "PASS", "elements": []}, "1.4.2": {"result": "DNA", "elements": []}, "2.1.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.1.2": {"result": "PASS", "elements": []}, "2.2.2": {"result": "NEEDS_REVIEW", "elements": []}, "2.3.1": {"result": "DNA", "elements": []}, "2.4.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.3": {"result": "PASS", "elements": []}, "2.4.5": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.6": {"result": "PASS", "elements": []}, "2.4.7": {"result": "NEEDS_REVIEW", "elements": ["˄ Top button"]}, "3.2.1": {"result": "PASS", "elements": []}, "3.2.2": {"result": "PASS", "elements": []}, "3.2.3": {"result": "PASS", "elements": []}, "3.2.4": {"result": "PASS", "elements": []}, "3.3.1": {"result": "DNA", "elements": []}, "3.3.2": {"result": "PASS", "elements": []}, "3.3.3": {"result": "DNA", "elements": []}, "3.3.4": {"result": "DNA", "elements": []}, "4.1.2": {"result": "PASS", "elements": []}}}
