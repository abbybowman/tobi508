# pre-SCRT demo viewer

A view-only page that shows a pre-SCRT file (TOBI's agent-assisted record)
or an SCRT file (the record a person saves in DHS's SCRT), optionally beside
a second file for the same page. It is a demo, not part of the MCP server.

**Open `viewer.html` by double-click** (it works from `file://`). It is one
self-contained file: no network requests (a Content-Security-Policy blocks
them), no editing, no saving.

## What it shows

- A banner that stays at the top: for a pre-SCRT file, the file's own
  disclaimer and that it is an agent-assisted record, not a Trusted Tester's;
  for an SCRT file, that it is a person's SCRT record as loaded.
- Product, Testing Information and Test Environment, as SCRT's view page
  does (pre-SCRT's `System` is `{os, browsers}`; SCRT's is its `S_*` fields).
- For pre-SCRT: record details (`origin`, `site`, `runs` with versions).
- The Criteria table with child issue rows under their parent. A blank
  pre-SCRT result reads "Needs review: a person must decide"; a test the tool
  did not perform says "This test could not be performed". Each row shows
  its `source` and `review`.
- Counts per result (counting only, no score), a result filter and "only
  rows needing a person".
- "Compare with": a second file's result and comment beside each test,
  matched by test ID, with rows whose results differ marked "Differs".

Every value from a file is shown as text, never as HTML: file text can come
from tested web pages. An image is shown only for a
`data:image/(png|jpeg|gif);base64,` value; anything else is shown as text.

## Building

`viewer.html` is built from `src/` and SCRT's stylesheet
(`third_party/scrt/CSS/acrt_styles.css`, read, never changed):

```bash
uv run python demo/prescrt-viewer/build.py          # write viewer.html
uv run python demo/prescrt-viewer/build.py --check  # used by the test
uv run pytest -n0 tests/test_prescrt_viewer.py
```

## Licence

The layout and stylesheet come from DHS's Section 508 Compliance Reporting
Tool (SCRT), MIT licence: see `LICENSE`. This viewer is TOBI's, not DHS's
tool. The page logic is plain JavaScript (SCRT's view page uses AngularJS).
