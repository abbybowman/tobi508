# Opening menus and sections: what cost time

`reveal.py` opens what the Tab walk finds that announces it opens something
(fix 9b phase 1; specs' guards `reveal` and `reveal-content`).

- **`aria-controls` is not a trigger by itself.** A selected tab names its
  visible panel, a spinbutton names the total it updates and a combobox names
  its list. The first full run turned 15 expectations into reviews for these.
  A trigger is collapsed, has `aria-haspopup`, names a *hidden* region, or is an
  unselected tab; form fields and the parts of a native date input (they open
  the browser's picker, not page content) are never triggers.
- **Choose a set's options together, read once.** ANDI changes the page, so each
  read ends a session. Home's remove buttons only appear together (one per
  choice), so two options of a set are chosen on one fresh load and the page is
  read after both. Reading after each, on separate loads, found one remove
  button each and never the set.
- **The same control has a new path after the page changes.** A list that grew
  above a checkbox moved its `nth-of-type` path, so Home's filter checkboxes
  came back as new controls in every opened state (about 40 questions). Merge
  revealed controls by kind, text, group, heading and row, against earlier reads
  only (`labels_pass`).
- **A set's answer carries one quote.** The agent quoted the rows of two
  buttons ("Earth; Sun"); a per-button quote check sent both to review. Check each
  piece of the quote against the rows of the whole set (`t5c._quote_ok`).
- **4.F has no `reveal-content`:** its pass R already Tabs through what the first
  six triggers open.
- **Probe a page's triggers in one process at a time**: several browsers beside
  a running test suite got the probe killed (exit 137).
