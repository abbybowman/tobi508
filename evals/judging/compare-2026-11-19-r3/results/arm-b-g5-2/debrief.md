**1. Where I struggled or felt unsure**
- **Keyboard and focus criteria (both pages):** I never pressed Tab or Enter, so 2.1.1, 2.1.2, 2.4.3, 2.4.7, 3.2.1 and 3.2.2 rest on markup clues only. That is why they are NEEDS_REVIEW. The tools gave me no keyboard or focus-ring evidence, only DOM and accessibility-tree snapshots.
- **Some PASS results are weaker than they look:**
  - 2.3.1 on both pages is PASS only because I saw no flashing content, and I did not watch the pages for flashing.
  - 2.2.2 on the home page is PASS with no real test.
  - 2.2.2 on the stories page rests on one 12-second wait, and I checked only slide 1 of 6.
  - These should probably have been NEEDS_REVIEW.
- **Unverified DNA results:**
  - On the stories page I never clicked "Submit Your Story", which may open a form. That makes the DNA results for 1.3.1, 2.4.6, 3.3.x and 4.1.2 unverified.
  - On the home page I never opened the "All" dropdown, the SDE menu, "Read More" or the help button. They may contain form controls, so the DNA results for 3.3.1, 3.3.3 and 3.3.4 are unverified.
- **Skip-link check:** It was crude. I looked only for `a[href^="#"]`, so a skip link built another way would be missed.

**2. What I left undone**
- I did not read the console logs, which showed 5 errors. I did not notice that they might matter.
- I did not check the other five story slides or the carousel buttons.
- I did not compare the navigation across pages for 3.2.3 and 3.2.4, or look for a site map or other ways to find pages for 2.4.5. I cut this short to save time and effort, and I did not say so clearly.
- I did not look at the pages visually, for example with a screenshot.

**3. What would have helped**
- Tools for keyboard testing, such as tab-order recording and a screenshot of the focused element.
- A way to interact with the page, open the dropdowns and dialogs, and re-snapshot.
- An instruction that said which criteria needed hands-on testing.
- A rule that a PASS needs evidence, so I would default to NEEDS_REVIEW instead of PASS when I had none.
