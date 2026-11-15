# Fields hidden from everyone (draft rule, step 6e)

Status: **approved and built** (Abby, 2026-11-15: behaviour only; mobile-only fields out of scope at the tested window; the limits accepted). Built differences: step 1 also presses every opener the inventory counts, not only the reveal pass's triggers (the first build gave a wrong DOES NOT APPLY on a form behind a plain button, review H-08); step 2's fill-and-send is a value typed in each text box, nothing submitted. Agent-assisted
results, not certified Trusted Tester results.

## The question

Guard CN holds 5.A to 5.H when a form field is hidden on load and the page
has anything that could show it (`Count.openers`, page-wide; Abby,
2026-11-12). Anti-spam fields (honeypots) and reCAPTCHA's response box
are hidden on nearly every form and are never meant for a person, so on
real sites they would keep 5.F and 5.G at NEEDS REVIEW for ever (Abby,
2026-11-15). Fields that a person's action or the page's timing reveals
(conditional fields, popups, panels) stay in scope.

## What the sources say

- **TT 5.1.3** (p. 25, Identify Content for 5.A to 5.H): "Use ANDI to
  identify any form elements on the page." ANDI's form module (fANDI,
  vendored 29.2.2, `third_party/andi/fandi.js` line 24) loops over
  `TestPageData.allVisibleElements` only; ANDI's `:shown` is "visibility
  not hidden and displayed" (`andi.js` line 732). A field hidden from
  everyone is never in the tester's list. Hidden content has its own
  module (hANDI, which force-reveals it), not used by the form tests.
- **DHS Baseline Alignment** TC10.A-ic-dna-1 and -2 (vendored,
  `tests/fixtures/baseline/`): a page whose only field, unlabelled, is in
  a `visibility:hidden` or `display:none` block that nothing shows is
  DOES NOT APPLY for 5.A, 5.B and 5.C. Hidden from everyone is out of
  scope even when it would fail.
- **W3C ACT rule e086e5** (form field has a non-empty accessible name):
  applies only to elements "included in the accessibility tree";
  Inapplicable Example 1 is `<input style="display:none">`. The glossary:
  programmatically hidden elements (display none, visibility not visible,
  or `aria-hidden="true"` on it or an ancestor) "are considered not
  included in the accessibility tree". DHS's act-tt data has no verdicts
  for e086e5.
- **Gravity Forms' docs**: the honeypot "is a field real users never see
  or fill in". **Google's reCAPTCHA docs**: `g-recaptcha-response` is a
  token the widget fills. ANDI's help pages and Akismet's source refused
  automated fetches (403); Akismet's markup was read from round 1's
  recording instead.

## What the markup does not settle

Round 1's forms page (frozen recording, read 2026-11-15) holds three
anti-spam fields and one conditional field side by side:

| Field | Hidden by | Other signs |
| --- | --- | --- |
| Akismet trap `ak_hp_textarea` | parent inline `display: none !important` | label "Δ" |
| Gravity Forms honeypot `input_28` | parent class `gform_validation_container` (stylesheet) | label "Comments", `autocomplete="new-password"` |
| reCAPTCHA `g-recaptcha-response` | its own inline `display:none` | no label |
| "Other (Please Specify)*" `input_7` | parent inline `display: none;` | required; shown when "Other" is chosen |
| Feedback popup (form 117) | overlay `display:none` | opens by itself 5 s after load |
| Mobile search box | `visibility:hidden` panel | its only trigger is not shown at 1280 px |

No markup sign separates "kept from people" from "shown by a choice"
without naming a plugin, and a page could fake any such sign. So the rule
below decides by **behaviour**: what a careful tester does to a form, and
whether the field ever appears.

## Draft rule (shared, guard CN's hidden-field count)

A form field hidden when the page loads is **hidden from everyone**, and
not counted in `fields_hidden` (as a hidden field on a page with no opener
is not counted today), only when it was never shown while the tool did
all of these, each on a fresh load of the recording:

1. **Open:** every trigger the reveal pass opened (built, `reveal.py`).
2. **Fill and send:** pass E's two attempts on its form (built, 5.F).
3. **Choose (new, the *choice sweep*):** in the field's form, each option
   of each list box, each radio button and each checkbox, one at a time
   (at most 60 choices a form, 10 options a list), reading after each
   whether any hidden field of that form is now shown.
4. **Wait and scroll (new):** the page watched for 15 s with no input,
   then scrolled down as the image read does, reading whether any hidden
   field is shown.

A field any of these shows stays in scope (and stays counted, so the
guard holds the test until a reader reads it). In the TT's words, a
careful tester opens what can be opened, makes the form's choices and
waits for what appears (principle 7); a field none of that shows is one
fANDI would never list.

What it decides, said plainly:

- On round 1's forms page: the Akismet trap, the Gravity Forms honeypot
  and the reCAPTCHA box go out of scope; "Other (Please Specify)" stays
  (the choice sweep shows it); the feedback popup stays (it opens at
  5 s); the mobile search box goes out of scope at this window (its only
  trigger is not shown).
- **On step 9a's 19 pages it moves no cell on its own:** every round 1
  page also has the feedback popup, which stays in scope and holds 5.A
  to 5.G until a test reads it; round 2's hidden fields are in "Filters"
  and facet panels the reveal pass opens. Its value is for the many
  sites whose only hidden fields are anti-spam fields.

## Decisions for Abby

1. **Behaviour only** (above), or behaviour **and** a markup sign
   (`aria-hidden`, `!important`, `tabindex="-1"`)? A sign would add
   safety against a reveal the sweep does not try, but leaves the Gravity
   Forms honeypot and reCAPTCHA in, since they carry no common sign.
   Recommended: behaviour only, with the limits below stated.
2. **A field shown only at another window width** (the mobile search
   box): out of scope at the tested window, as above? TT tests at one
   window; the report records it (principle 4).
3. **The limits** (each keeps a wrong DOES NOT APPLY possible, rarely):
   a field shown only after typing a particular value, after hovering,
   after more than 15 s, or by leaving the page (exit-intent popups).
   Accept and state them in `docs/KNOWN-LIMITS.md`, or require more?

## If approved: the change

- Specs: `_template.md` guard CN (the hidden-field count), and a MINOR
  version of each spec that lists `fields_hidden`: 5.A, 5.B, 5.C, 5.D,
  5.F, 5.G, 5.H.
- Code: the choice sweep and the wait in `count.py` (or beside
  `reveal.py`), recorded on `Count` (which fields each step showed);
  guard CN reads it.
- Fixtures: a form with an Akismet-style trap, a Gravity Forms-style
  honeypot and a reCAPTCHA-style box (decides, 5.A to 5.H); the nearest
  that must stay: the same form with an "Other" field a list shows, and
  with a popup that opens at 5 s. The grid's hidden-form pages rerun.
- The frozen rerun of 5.A to 5.H on both rounds, each moved cell shown
  beside the key.
- Cost: one load per form with hidden fields, plus a 15 s watch once per
  page; measured against the budgets before it is merged.
