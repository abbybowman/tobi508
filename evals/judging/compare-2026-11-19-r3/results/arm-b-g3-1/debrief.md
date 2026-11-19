**1. Where I struggled or felt unsure**
- **Keyboard behaviour (2.1.1, 2.1.2, 2.4.3, 3.2.1, 3.2.2).** I never pressed Tab or Enter on either page. I called `.focus()` from a script and read computed styles, which says nothing about real tab order, traps, or whether the dropdown menus and accordion tabs work from the keyboard. I marked some of these NEEDS_REVIEW but gave PASS to others that I had not really tested, such as 3.2.1 and 3.2.2 on sample-files. Those PASSes are weaker than they look.
- **2.4.7 on the header search box.** I called it a FAIL because the computed outline, border and shadow did not change on focus. I did not take a screenshot, so I may have missed some other visible indicator.
- **2.4.7 on the other controls.** I did not check whether the 1px dashed white outline on the nav links has enough contrast against the header background.
- **PASS without evidence.** I gave 2.2.2, 2.3.1 and 2.4.5 a PASS on thin evidence.
  - The animation, media and marquee check ran on the Verifier page only, not on sample-files.
  - I did not look at images or auto-updating content.
  - I did not check how the "Multiple Ways" requirement is met beyond seeing search and navigation.
- **Sample-files form fields.** My script ran only in the Verifier tab. The sample-files result for the search box rests on the accessibility snapshot alone.

**2. What I left undone**
- I did not run a FITS file through the verifier, so error handling and the 3.3.x criteria are unassessed. That needed a test file and the tool lacked file upload to try it. I should have said so more plainly.
- I did not read the 5 console errors on the Verifier page or the 1 on sample-files, and I did not check whether they matter. I did not notice they might be relevant.
- I did not open the accordion tabs on sample-files or the nav dropdowns. I skipped this to save time.
- I did not check that the "Ready" status message is announced to assistive technology, or that the skip link lands correctly. I did not notice these in time.

**3. What would have helped**
- Real keyboard-driving tools, such as a Tab-press sequence with a focus log and a screenshot per stop.
- A way to supply a test file to the upload control.
- An explicit way to run the same DOM script on each page.
- Clearer guidance that PASS should be reserved for things I actually exercised, with NEEDS_REVIEW as the default otherwise.
