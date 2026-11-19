1. Where I struggled or felt unsure

- **Keyboard-dependent criteria (2.1.1, 2.1.2, 2.4.3, 2.4.7, 3.2.1).** I never pressed Tab or interacted with either page. I only read the accessibility snapshot and ran a few DOM queries. So these are NEEDS_REVIEW by necessity, not because I found something ambiguous.
- **Main-nav dropdowns.** The "Data Sites", "Data Services" and "Data Search" links point to "/" and have hidden submenus. I couldn't tell whether they work from the keyboard.
- **Verifier tool behavior.** The tool says it runs locally. I didn't upload a file, so I don't know whether it runs on selection (3.2.2) or how it reports errors (3.3.1, 3.3.3).
- **Sample-files accordions.** The markup is odd: `role=tab` on a div wrapping an h4 and a button, inside a `tablist` that holds tabpanels. I saw that, but I did not test keyboard operation or the ARIA behavior.
- **Some results are weakly supported.** I marked these without real verification:
  - 2.3.1 PASS and the 1.4.2/2.2.2 DNA results rest on finding no media elements, not on watching the page. I did not check for CSS animations or carousels.
  - 3.2.4, 3.2.3, 2.4.1 and 2.4.5 PASS are based on one snapshot per page. I did not compare navigation order precisely or look at the dropdown contents.
  - Sample-files 3.2.2 PASS and 4.1.2 PASS are thinly supported. 3.2.2 is shaky because I never interacted with the search form, and 4.1.2 only covers the search box, which I checked by its label.
- **Sample-files 1.3.1 and 2.4.6 PASS.** I did not inspect the search-box label on that page directly. I assumed it matches the verifier page, since it is the same site header.

2. What I left undone

- No keyboard testing, no focus-visibility check, and no upload test of the verifier. I stopped after DOM inspection, and my summary didn't say clearly enough that this was a choice to cut scope, not a technical limit.
- I did not look at the console errors (5 on the verifier, 1 on sample-files). I didn't check whether they point to script failures that affect accessibility.
- I did not run the DOM form check on the sample-files page. I assumed it from the snapshot.

3. What would have helped

- Keyboard tools, such as a way to press Tab and report the focused element and its visible indicator.
- A way to upload a test file to the verifier.
- A cleaner way to read computed accessible names and a page's full interaction states.
- A clearer budget or expectation for how deep testing should go.
