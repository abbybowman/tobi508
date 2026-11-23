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
- **4.D reads the walk too (1.13.0, #135):** each trigger's load needs its own
  pass name (`O<n>`), or the pictures of every trigger's walk overwrite each
  other; pictures only when 4.D runs, so 4.E's evidence on those loads is
  unchanged. Its before pictures come from Shift+Tab back through the opened
  content after the walk (`after_walk`, raw key presses, not walk steps). A
  dropdown that closes when focus leaves is shut by then, so the first
  Shift+Tab lands on its button: stop at the first landing that is not the
  stop expected, never picture the wrong element.
- **5.D fills what the walk reached (1.13.0, #135):** pass FO is pass F
  on a load opened as reveal.py opened the trigger (`reveal.reopen`),
  arriving by Tab from where the opening left focus, with the next P8
  stop as where Tab is expected. Before building, list what each
  trigger opened on the round's pages (`evidence/reveal.json`:
  `new_fields`, `walked.reached`): round 3's held 5.D cells had no field
  inside any menu, so only the guard moved them, and a fill pass alone
  would have moved nothing.
- **4.A and 4.F read the walk too (4.A 1.21.0, 4.F 1.16.0, #135):** a menu
  the walk leaves at once may still be reached later: round 3's SDE "All"
  list stays open, and Tab reaches its options after four other stops.
  The *onward Tabs* (a load of their own, kept apart from P8's steps) find
  that, so 4.C, 4.D, 4.E and 5.D read P8 unchanged. Probe a held cell on
  its replay with a short Playwright script (`capture.replay_context` on
  the run's `page.har.zip`) before designing: it showed the options were
  reachable, that Enter and Space did nothing, and that Space's "effect"
  was the open list re-setting its class on each scroll step. Pages can
  reuse ids (two `#button-basic` there): select by more than the id.
- **Name what a person sees:** sentences name an element by its visible
  text, with what a screen reader hears when that differs (`reveal.named`;
  the "All" button is heard as "All All", its icon's alt beside the word).
- **4.F has no `reveal-content`:** its pass R already Tabs through what the first
  six triggers open.
- **Probe a page's triggers in one process at a time**: several browsers beside
  a running test suite got the probe killed (exit 137).
