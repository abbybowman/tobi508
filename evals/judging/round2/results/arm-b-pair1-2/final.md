I tested both pages with a DOM inspection and a single Tab press. I did not do a full keyboard walkthrough or a visual check of focus indicators. Those criteria are marked NEEDS_REVIEW, along with the filter behaviour in 3.2.2 on the home page.

**Home page (https://svs.gsfc.nasa.gov/)**
- **2.2.2 FAIL.** The home page carousel (`#home_page_carousel`) starts by itself and advances every 7.5 seconds with fade transitions. It has no pause or stop control. Its only buttons are the slide indicators.
- **2.4.1 PASS, with a caveat.** There is no skip link, since the first Tab stop is the NASA logo link. The page does have `header`, `nav` and `main` landmarks and a heading structure. Those are accepted bypass techniques, but a person may want to confirm.
- **Form fields (1.3.1, 2.4.6, 3.3.2, 4.1.2) PASS.**
  - The search box has both a `label for` and an `aria-label`, so its accessible name matches its label.
  - The filter checkboxes each have a `label for`.
- **Other criteria.**
  - 1.4.2 is DNA because the page has no audio or video.
  - 3.3.1, 3.3.3 and 3.3.4 are DNA because the page has no form that validates input or submits legal or financial data.

**Help page (https://svs.gsfc.nasa.gov/help/)**
- **Form fields.** The only field is the search box, labelled the same way as on the home page.
- **Carousel and media.** The page has no carousel, no audio and no video, so 1.4.2 is DNA and 2.2.2 passes.
- **2.4.1.** It has the same landmarks, so the same caveat applies.
- **Navigation.** The header and footer links match the home page, and the help sidebar is specific to this section.

**Both pages**
- **2.4.5 PASS.** Navigation links and site search give two ways to find pages.
- **3.2.3 and 3.2.4 PASS.** The header and footer navigation and the search box are the same on both pages.

RESULT: {"https://svs.gsfc.nasa.gov/": {"1.3.1": {"result": "PASS", "elements": []}, "1.4.2": {"result": "DNA", "elements": []}, "2.1.1": {"result": "NEEDS_REVIEW", "elements": ["carousel indicator buttons", "filter checkbox labels"]}, "2.1.2": {"result": "PASS", "elements": []}, "2.2.2": {"result": "FAIL", "elements": ["#home_page_carousel (auto-advancing every 7.5s, no pause/stop control)"]}, "2.3.1": {"result": "PASS", "elements": []}, "2.4.1": {"result": "PASS", "elements": []}, "2.4.3": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.5": {"result": "PASS", "elements": []}, "2.4.6": {"result": "PASS", "elements": []}, "2.4.7": {"result": "NEEDS_REVIEW", "elements": ["links, buttons, filter checkbox labels"]}, "3.2.1": {"result": "PASS", "elements": []}, "3.2.2": {"result": "NEEDS_REVIEW", "elements": ["filter checkboxes in Recently released/updated/Currently popular forms update results on change"]}, "3.2.3": {"result": "PASS", "elements": []}, "3.2.4": {"result": "PASS", "elements": []}, "3.3.1": {"result": "DNA", "elements": []}, "3.3.2": {"result": "PASS", "elements": []}, "3.3.3": {"result": "DNA", "elements": []}, "3.3.4": {"result": "DNA", "elements": []}, "4.1.2": {"result": "PASS", "elements": []}}, "https://svs.gsfc.nasa.gov/help/": {"1.3.1": {"result": "PASS", "elements": []}, "1.4.2": {"result": "DNA", "elements": []}, "2.1.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.1.2": {"result": "PASS", "elements": []}, "2.2.2": {"result": "PASS", "elements": []}, "2.3.1": {"result": "PASS", "elements": []}, "2.4.1": {"result": "PASS", "elements": []}, "2.4.3": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.5": {"result": "PASS", "elements": []}, "2.4.6": {"result": "PASS", "elements": []}, "2.4.7": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.1": {"result": "PASS", "elements": []}, "3.2.2": {"result": "PASS", "elements": []}, "3.2.3": {"result": "PASS", "elements": []}, "3.2.4": {"result": "PASS", "elements": []}, "3.3.1": {"result": "DNA", "elements": []}, "3.3.2": {"result": "PASS", "elements": []}, "3.3.3": {"result": "DNA", "elements": []}, "3.3.4": {"result": "DNA", "elements": []}, "4.1.2": {"result": "PASS", "elements": []}}}
