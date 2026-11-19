Neither page is fully done. On both pages, 2.4.1, 2.4.5, 3.2.3 and 3.2.4 are NEEDS_REVIEW. The tool treated the two pages as having the same content, so it could not compare them. Two focus-order questions (2.4.3) were also left unanswered. The pictures behind them did not settle them for me.

**Home page**
- **2.1.1 Keyboard: FAIL.** The "Search Stories" header item works with a mouse but keyboard focus never reaches it, and nothing else on the page does the same job.
- **2.4.7 Focus Visible: FAIL.** The "SDE SDE" button shows no change when it has focus. The "Help and Support" button needs a person to check, because the screenshots did not show where its focus style draws.
- **2.1.2 No Keyboard Trap: NEEDS_REVIEW.** The tabbing test did not finish.
- **2.4.3 Focus Order: NEEDS_REVIEW.** After the "All" dropdown opens, the next Tab skips its options and goes to the search box. I could not tell whether that matters.
- **3.2.1 On Focus: NEEDS_REVIEW.** The "Click to learn more about SciX" link changed the address once but not on a second try.
- **3.2.2 On Input: NEEDS_REVIEW.** The test did not check inside the dropdown that opens.
- **1.3.1 Info and Relationships: NEEDS_REVIEW.** The search box has no visible label, only a placeholder.
- **2.4.6 Headings and Labels: NEEDS_REVIEW.** The question on whether the search box's label is descriptive is unanswered.
- **4.1.2 Name, Role, Value: PASS.** The fields and buttons have accessible names that include their visible text.
- **3.3.2 Labels or Instructions: PASS.** The tool found a label or instructions for each field.
- **1.4.2, 2.2.2, 2.3.1: DNA.** There is no audio, nothing moving, and no flashing.
- **3.3.1, 3.3.3, 3.3.4: DNA.** The only form is a site search that accepts anything and shows no error, and it is not a consequential form.

**My Search Stories page**
- **2.1.1 Keyboard: FAIL.** The header logo (which goes to the home page) and the breadcrumb "Home" link work with a mouse but are not reachable by keyboard. No reached element goes to the SDE home page. The NASA logo link goes to nasa.gov instead.
- **2.4.7 Focus Visible: FAIL.** The "SDE SDE" button shows no focus indicator. The "Help and Support" button needs a person to check.
- **2.1.2 No Keyboard Trap: PASS.**
- **3.2.1 On Focus: PASS.**
- **2.2.2 Pause, Stop, Hide: NEEDS_REVIEW.** The page has a "1 / 6" story carousel. The automatic-change checks could not be completed.
- **2.4.3 Focus Order: NEEDS_REVIEW.** Focus jumps from "Help and Support" back up to the slide container, and then to buttons that have no visible box.
- **1.3.1 Info and Relationships and 4.1.2 Name, Role, Value: PASS.** These cover the page's buttons. The tool found no form fields on this page.
- **1.4.2, 2.3.1: DNA.** There is no audio and nothing flashes.
- **2.4.6, 3.2.2, 3.3.1, 3.3.2, 3.3.3, 3.3.4: DNA.** The tool found no form fields or forms on this page.

RESULT: {"https://science.data.nasa.gov/science-discovery-engine/search/sde/home": {"1.3.1": {"result": "NEEDS_REVIEW", "elements": ["Type to search... text field (placeholder only)"]}, "1.4.2": {"result": "DNA", "elements": []}, "2.1.1": {"result": "FAIL", "elements": ["Search Stories (header span, not keyboard reachable)"]}, "2.1.2": {"result": "NEEDS_REVIEW", "elements": []}, "2.2.2": {"result": "DNA", "elements": []}, "2.3.1": {"result": "DNA", "elements": []}, "2.4.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.3": {"result": "NEEDS_REVIEW", "elements": ["All dropdown options"]}, "2.4.5": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.6": {"result": "NEEDS_REVIEW", "elements": ["Type to search... text field"]}, "2.4.7": {"result": "FAIL", "elements": ["SDE SDE button"]}, "3.2.1": {"result": "NEEDS_REVIEW", "elements": ["Click to learn more about SciX link"]}, "3.2.2": {"result": "NEEDS_REVIEW", "elements": ["All dropdown"]}, "3.2.3": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.4": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.1": {"result": "DNA", "elements": []}, "3.3.2": {"result": "PASS", "elements": []}, "3.3.3": {"result": "DNA", "elements": []}, "3.3.4": {"result": "DNA", "elements": []}, "4.1.2": {"result": "PASS", "elements": []}}, "https://science.data.nasa.gov/science-discovery-engine/search/sde/MySearchStory": {"1.3.1": {"result": "PASS", "elements": []}, "1.4.2": {"result": "DNA", "elements": []}, "2.1.1": {"result": "FAIL", "elements": ["Header logo div linking to SDE home", "Home breadcrumb link"]}, "2.1.2": {"result": "PASS", "elements": []}, "2.2.2": {"result": "NEEDS_REVIEW", "elements": ["story carousel 1/6"]}, "2.3.1": {"result": "DNA", "elements": []}, "2.4.1": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.3": {"result": "NEEDS_REVIEW", "elements": ["image slide container", "Submit Your Story", "SEARCH", "next-icon"]}, "2.4.5": {"result": "NEEDS_REVIEW", "elements": []}, "2.4.6": {"result": "DNA", "elements": []}, "2.4.7": {"result": "FAIL", "elements": ["SDE SDE button"]}, "3.2.1": {"result": "PASS", "elements": []}, "3.2.2": {"result": "DNA", "elements": []}, "3.2.3": {"result": "NEEDS_REVIEW", "elements": []}, "3.2.4": {"result": "NEEDS_REVIEW", "elements": []}, "3.3.1": {"result": "DNA", "elements": []}, "3.3.2": {"result": "DNA", "elements": []}, "3.3.3": {"result": "DNA", "elements": []}, "3.3.4": {"result": "DNA", "elements": []}, "4.1.2": {"result": "PASS", "elements": []}}}
