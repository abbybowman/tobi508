"""Draw docs/diagrams/tobi-runs.svg: every run TOBI makes on a recording,
what each produces, and which Trusted Tester tests read it.

The facts come from the rules specs' section 2 (Evidence to collect) and
`pipeline.py`. When a run changes, edit RUNS below and rerun:

    uv run python scripts/draw_runs_diagram.py
"""

from __future__ import annotations

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "diagrams" / "tobi-runs.svg"

# Test columns, grouped as the Trusted Tester process groups them.
FAMILIES = [
    ("Motion and sound", ["2.A", "2.B", "2.C", "2.D", "3.A"], "#8a4b00", "#fdf1e3"),
    ("Keyboard", ["4.A", "4.B", "4.C", "4.D", "4.E", "4.F"], "#1f5fa8", "#e7f0fb"),
    ("Forms", ["5.A", "5.B", "5.C", "5.D", "5.F", "5.G", "5.H"], "#1e7a35", "#e6f4ea"),
    ("Across pages", ["9.A", "9.B", "9.C", "19.A"], "#6a3fb5", "#f1eafb"),
]
TESTS = [t for _, ts, _, _ in FAMILIES for t in ts]

# Each run: (letter chip or "", name, what it does (lines), evidence (lines),
#            tests it decides from, tests it only checks against).
GROUPS = [
    (
        "Read the page: nothing pressed",
        [
            (
                "",
                "Inventory",
                [
                    "Counts what is on the page, including inside",
                    "web components, frames and hidden parts",
                ],
                [
                    "Counts of focusable elements, form fields,",
                    "media, images, landmarks and links",
                ],
                [],
                [
                    "2.A",
                    "2.B",
                    "3.A",
                    "4.A",
                    "4.D",
                    "4.F",
                    "5.A",
                    "5.B",
                    "5.C",
                    "5.D",
                    "5.F",
                    "5.G",
                    "5.H",
                    "9.A",
                    "9.B",
                    "9.C",
                    "19.A",
                ],
            ),
            (
                "T",
                "Watch",
                [
                    "Loads the page and watches it for 6.5 s",
                    "with no input, beside the keyboard walk",
                ],
                [
                    "A picture every 0.5 s; every change, timer, sound,",
                    "animation, video, focus move and dialog",
                ],
                ["2.A", "2.B", "2.C", "2.D", "3.A"],
                [],
            ),
            (
                "",
                "Flash capture",
                [
                    "Only when the watch saw something fast:",
                    "replays it frame by frame",
                ],
                ["Frames at 60 a second, and the", "brightness changes between them"],
                ["3.A"],
                [],
            ),
            (
                "L",
                "Labels",
                [
                    "Loads the page with ANDI and focuses each",
                    "form field; opens each frame as its own page",
                ],
                [
                    "Per field: its label, name in code, the text",
                    "around it, a picture of it focused",
                ],
                ["5.A", "5.B", "5.C"],
                [],
            ),
        ],
    ),
    (
        "Use the keyboard",
        [
            (
                "P1 P2",
                "Keyboard walk",
                ["Tab through the whole page (P1), then", "Shift+Tab back (P2)"],
                [
                    "Every stop: what it is, its name, where it is,",
                    "focus events, page changes, how each pass ended",
                ],
                ["4.A", "4.B", "4.C", "4.D", "4.E", "4.F", "5.D", "5.F", "9.A"],
                ["2.C", "5.A", "5.B", "5.C"],
            ),
            (
                "",
                "Opening menus",
                [
                    "Opens each menu, tab, accordion and filter",
                    "the walk found (up to 20), each on a fresh load",
                ],
                [
                    "What each one opened, read like the page;",
                    "a list of those that would not open",
                ],
                ["5.A", "5.B", "5.C"],
                ["4.A", "4.C", "4.D", "4.E", "4.F", "5.D"],
            ),
            (
                "P3 P4 P6 P7 P8",
                "Trap follow-ups",
                [
                    "P3 tries keys to leave a trap; P4 arrows into",
                    "widgets; P6 skips past a trap; P7 tabs through",
                    "error states; P8 tabs through what menus opened",
                ],
                ["Whether focus can always move on,", "and the keys that free it"],
                ["4.C", "4.E"],
                [],
            ),
            (
                "W",
                "Widgets",
                [
                    "Arrow keys inside each menu bar, tab list,",
                    "grid or list the walk reached",
                ],
                ["A picture of each item with and", "without focus"],
                ["4.D"],
                [],
            ),
            (
                "R",
                "Reveal order",
                [
                    "Presses Enter on up to 6 controls that show",
                    "content (4.F's own, not Opening menus)",
                ],
                ["Where what appeared sits in", "the focus order"],
                ["4.F"],
                ["4.A"],
            ),
            (
                "",
                "Each test's own presses",
                [
                    "4.A mouse, hover and Enter/Space; 4.B a held",
                    "or repeated key; 4.E a step replayed; 9.A skip links",
                ],
                ["What each press did, from a", "fresh load each time"],
                ["4.A", "4.B", "4.E", "9.A"],
                [],
            ),
        ],
    ),
    (
        "Fill in forms",
        [
            (
                "F",
                "Fill",
                ["Types into every field in Tab order", "and tabs out of it"],
                ["What changed when a field was", "filled or left"],
                ["5.D"],
                [],
            ),
            (
                "E",
                "Errors",
                ["Submits each form empty, then with", "wrong values"],
                [
                    "The page before and after: messages,",
                    "where they are, focus, dialogs",
                ],
                ["4.C", "5.F", "5.G", "5.H"],
                [],
            ),
        ],
    ),
    (
        "Other pages you give",
        [
            (
                "",
                "Site read",
                ["Loads each other page's own recording", "(9.C with ANDI)"],
                [
                    "Links, menus, regions, titles, search",
                    "forms and names, matched across pages",
                ],
                ["9.A", "9.B", "9.C", "19.A"],
                [],
            ),
            (
                "",
                "Live site checks",
                [
                    "The only live visits: the site's own search,",
                    "suggested pages, other addresses for the page",
                ],
                ["Whether a second way to find", "the page exists"],
                ["19.A"],
                [],
            ),
        ],
    ),
]

STEPS = [
    ("Rules", ["Each test's spec: the first", "row that matches decides"]),
    (
        "Open questions",
        ["A model looks at the pictures", "and answers; a person overrides"],
    ),
    ("Guards", ["Anything not read turns PASS", "or DNA into NEEDS REVIEW"]),
    ("Report", ["One outcome per test, and", "a draft SCRT file"]),
]

# Geometry.
W = 1480
PAD = 24
NAME_X = PAD + 22  # left of run names (a group bar sits left of it)
NAME_W = 400
EVID_X = NAME_X + NAME_W + 12
EVID_W = 330
GRID_X = EVID_X + EVID_W + 12
COL = (W - PAD - GRID_X) / len(TESTS)
LINE = 15
INK = "#1b1f24"
MUTED = "#57606a"
RULE = "#d0d7de"


def text(x, y, s, size=12, weight=400, fill=INK, anchor="start", family=None):
    fam = f' font-family="{family}"' if family else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}" text-anchor="{anchor}"{fam}>{escape(s)}</text>'
    )


def chip(x, y, label):
    """A pill with the run's letters, so P1 or L can be found at a glance."""
    w = 9 + 7.6 * len(label)
    return (
        f'<rect x="{x:.1f}" y="{y - 12:.1f}" width="{w:.1f}" height="17" rx="8.5" '
        f'fill="{INK}"/>'
        + text(
            x + w / 2,
            y + 0.5,
            label,
            11,
            700,
            "#ffffff",
            "middle",
            "ui-monospace, SFMono-Regular, Menlo, monospace",
        ),
        w,
    )


def col_x(test):
    return GRID_X + COL * TESTS.index(test) + COL / 2


def draw() -> str:
    out: list[str] = []
    y = PAD + 18
    out.append(
        text(
            PAD,
            y,
            "How TOBI reads a page: the runs, what each records, and the tests that use it",
            20,
            700,
        )
    )
    y += 22
    out.append(
        text(
            PAD,
            y,
            "Agent-assisted findings, not a certified Trusted Tester result. Sources: each rules spec's section 2 and pipeline.py.",
            12,
            400,
            MUTED,
        )
    )

    # Step 1: the recording.
    y += 20
    h = 50
    out.append(
        f'<rect x="{PAD}" y="{y}" width="{W - 2 * PAD}" height="{h}" rx="8" fill="#f6f8fa" stroke="{INK}" stroke-width="1.5"/>'
    )
    out.append(text(PAD + 16, y + 21, "1  Record once", 15, 700))
    out.append(
        text(
            PAD + 140,
            y + 21,
            "Chrome loads the page once and saves it with all its network traffic. Other pages you give are recorded the same way.",
            13,
        )
    )
    out.append(
        text(
            PAD + 140,
            y + 39,
            "Every run below starts from a fresh load of a recording, never the live site, so a rerun reads the same page. The one exception is marked.",
            13,
            400,
            MUTED,
        )
    )
    y += h + 26

    # Step 2 header.
    out.append(text(PAD, y, "2  Runs on the recording", 15, 700))
    out.append(
        text(
            NAME_X + 175,
            y,
            "Letters are the names used in the specs and the evidence trace.",
            12,
            400,
            MUTED,
        )
    )
    # Column headers: families, then test IDs.
    fy = y - 8
    for fam, ts, ink, tint in FAMILIES:
        x0 = col_x(ts[0]) - COL / 2
        out.append(
            f'<rect x="{x0 + 1:.1f}" y="{fy - 16}" width="{COL * len(ts) - 2:.1f}" height="22" rx="4" fill="{tint}"/>'
        )
        out.append(text(x0 + COL * len(ts) / 2, fy, fam, 12, 700, ink, "middle"))
    y += 22
    out.append(text(NAME_X, y, "Run", 12, 700, MUTED))
    out.append(text(EVID_X, y, "Evidence it records", 12, 700, MUTED))
    for fam, ts, ink, _ in FAMILIES:
        for t in ts:
            out.append(text(col_x(t), y, t, 12, 700, ink, "middle"))
    y += 8
    grid_top = y
    y += 10

    # Column tints behind the rows.
    body: list[str] = []
    for gname, runs in GROUPS:
        gy0 = y
        y += 10
        for letters, name, does, evid, main, check in runs:
            n = max(len(does), len(evid))
            rh = 22 + LINE * n
            ty = y + 17
            x = NAME_X
            if letters:
                svg, cw = chip(x, ty, letters)
                body.append(svg)
                x += cw + 7
            body.append(text(x, ty + 0.5, name, 13, 700))
            for i, line in enumerate(does):
                body.append(text(NAME_X, ty + LINE * (i + 1), line, 12, 400, MUTED))
            for i, line in enumerate(evid):
                body.append(text(EVID_X, ty + LINE * i, line, 12))
            cy = y + rh / 2
            for t in main:
                body.append(
                    f'<circle cx="{col_x(t):.1f}" cy="{cy:.1f}" r="6.5" fill="{INK}"/>'
                )
            for t in check:
                body.append(
                    f'<circle cx="{col_x(t):.1f}" cy="{cy:.1f}" r="5.5" fill="#ffffff" stroke="{INK}" stroke-width="1.6"/>'
                )
            if name == "Live site checks":
                body.append(
                    f'<rect x="{NAME_X - 6}" y="{y + 2}" width="{GRID_X + COL * len(TESTS) - NAME_X + 4:.1f}" height="{rh - 4}" rx="5" fill="none" stroke="#b3261e" stroke-width="1.5" stroke-dasharray="5 3"/>'
                )
                body.append(
                    text(
                        NAME_X + 125,
                        ty + 0.5,
                        "the exception: the live site",
                        11,
                        700,
                        "#b3261e",
                    )
                )
            y += rh
            body.append(
                f'<line x1="{NAME_X}" y1="{y}" x2="{W - PAD}" y2="{y}" stroke="#eaeef2"/>'
            )
        # Group label: a bar down the left with the name above the rows.
        body.insert(
            0,
            f'<rect x="{PAD}" y="{gy0 + 6}" width="5" height="{y - gy0 - 10}" rx="2.5" fill="{MUTED}"/>',
        )
        body.insert(1, text(NAME_X, gy0 + 4, gname.upper(), 10.5, 700, MUTED))
        y += 18
    grid_bottom = y - 18

    for fam, ts, ink, tint in FAMILIES:
        x0 = col_x(ts[0]) - COL / 2
        out.append(
            f'<rect x="{x0 + 1:.1f}" y="{grid_top}" width="{COL * len(ts) - 2:.1f}" height="{grid_bottom - grid_top:.1f}" fill="{tint}" opacity="0.55"/>'
        )
    out.extend(body)

    # Legend.
    ly = y + 2
    out.append(f'<circle cx="{NAME_X + 6}" cy="{ly - 4}" r="6.5" fill="{INK}"/>')
    out.append(text(NAME_X + 18, ly, "The test decides from this evidence", 12))
    lx = NAME_X + 270
    out.append(
        f'<circle cx="{lx + 6}" cy="{ly - 4}" r="5.5" fill="#fff" stroke="{INK}" stroke-width="1.6"/>'
    )
    out.append(
        text(
            lx + 18,
            ly,
            "Used only to check nothing was missed or changing: it can turn a PASS into NEEDS REVIEW, never the other way",
            12,
        )
    )
    y = ly + 30

    # Step 3: from evidence to outcome.
    out.append(text(PAD, y, "3  From evidence to outcome", 15, 700))
    y += 14
    bw = (W - 2 * PAD - 3 * 34) / 4
    bh = 62
    for i, (name, lines) in enumerate(STEPS):
        bx = PAD + i * (bw + 34)
        out.append(
            f'<rect x="{bx:.1f}" y="{y}" width="{bw:.1f}" height="{bh}" rx="8" fill="#ffffff" stroke="{INK}" stroke-width="1.5"/>'
        )
        out.append(text(bx + 14, y + 22, name, 14, 700))
        for j, line in enumerate(lines):
            out.append(text(bx + 14, y + 40 + j * LINE, line, 12, 400, MUTED))
        if i < len(STEPS) - 1:
            ax = bx + bw + 6
            ay = y + bh / 2
            out.append(
                f'<path d="M{ax:.1f},{ay} h20 m-7,-6 l7,6 l-7,6" fill="none" stroke="{INK}" stroke-width="1.8"/>'
            )
    y += bh + PAD

    head = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{y:.0f}" '
        f'viewBox="0 0 {W} {y:.0f}" role="img" aria-labelledby="t d" '
        f'font-family="system-ui, -apple-system, Segoe UI, Helvetica, Arial, sans-serif">'
        f'<title id="t">How TOBI reads a page</title>'
        f'<desc id="d">The page is recorded once. Fourteen runs read the recording; '
        f"a table in docs/diagrams/tobi-runs.md lists each run, its evidence and the "
        f"tests that use it. Evidence then goes through the rules, open questions, "
        f"guards and the report.</desc>"
        f'<rect width="100%" height="100%" fill="#ffffff"/>'
    )
    return head + "".join(out) + "</svg>\n"


def table() -> str:
    """The same facts as a Markdown table, the diagram's text equivalent."""
    rows = [
        "| Run | What it does | Evidence it records | Tests that decide from it | Tests that check against it |",
        "| --- | --- | --- | --- | --- |",
    ]
    for gname, runs in GROUPS:
        rows.append(f"| **{gname}** | | | | |")
        for letters, name, does, evid, main, check in runs:
            label = f"{name} ({letters})" if letters else name
            rows.append(
                f"| {label} | {' '.join(does)} | {' '.join(evid)} | {', '.join(main) or '–'} | {', '.join(check) or '–'} |"
            )
    return "\n".join(rows) + "\n"


if __name__ == "__main__":
    OUT.write_text(draw())
    print(table())
