"""Build the hackathon deck in GSA's PowerPoint template.

    python3 docs/hackathon/build_pptx.py OUT.pptx

(docs/hackathon/README.md gives the exact command.) Needs python-pptx (not a
project dependency). The template is GSA's sample deck, vendored byte for
byte in docs/hackathon/templates/: its slides are removed and its master,
layouts, theme and black title bar are kept. Every figure here is copied from
evaluation.md; change both together. The deck is read, not presented: no
speaker notes; sources and caveats are footnotes on the slides.

Accessibility: every slide has a real title; text is real text; tables are
real tables with a header row; the diagram has alt text; reading order is
the order shapes are added (title first); no meaning is carried by colour
alone; text contrast is at least 4.5:1.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).parent
TEMPLATE = HERE / "templates" / "gsa-sample-deck.pptx"
DIAGRAM = HERE / "diagrams" / "tobi-flow.png"

NAVY = RGBColor(0x0B, 0x33, 0x64)
INK = RGBColor(0x1F, 0x1F, 0x1F)
MUTED = RGBColor(0x4A, 0x4A, 0x4A)
CARD = RGBColor(0xF3, 0xF3, 0xF3)
TINT = RGBColor(0xE8, 0xEE, 0xF6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0, 0, 0)

FILL = "**[FILL]**"


# --- helpers ----------------------------------------------------------------


def runs(par, text: str, size: float, color=INK, bold=False) -> None:
    """Add text with **bold** spans to a paragraph."""
    for i, part in enumerate(re.split(r"\*\*", text)):
        if not part:
            continue
        r = par.add_run()
        r.text = part
        r.font.size = Pt(size)
        r.font.color.rgb = color
        r.font.bold = bold or (i % 2 == 1)


def bullet(par, level: int = 0) -> None:
    ppr = par._p.get_or_add_pPr()
    ppr.set("marL", str(Emu(Inches(0.22 + 0.22 * level))))
    ppr.set("indent", str(-Emu(Inches(0.18))))
    bu = ppr.makeelement(qn("a:buChar"), {"char": "•"})
    ppr.append(bu)


def text(
    slide,
    x,
    y,
    w,
    h,
    paras,
    size=14,
    color=INK,
    anchor=MSO_ANCHOR.TOP,
    align=PP_ALIGN.LEFT,
    space=6,
    name=None,
):
    """paras: list of str, or (str, {size, color, bold, bullet}) tuples."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, Inches(0.04))
    for i, p in enumerate(paras):
        t, o = (p, {}) if isinstance(p, str) else p
        par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        par.alignment = align
        par.space_after = Pt(o.get("space", space))
        if o.get("bullet") is not None:
            bullet(par, o["bullet"])
        runs(par, t, o.get("size", size), o.get("color", color), o.get("bold", False))
    return tb


def box(slide, x, y, w, h, fill=CARD, name=None):
    s = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    s.adjustments[0] = 0.06
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    s.line.fill.background()
    s.shadow.inherit = False
    if name:
        s.name = name
    s.text_frame.text = ""
    return s


def card(
    slide, x, y, w, h, head, body, fill=CARD, size=13, head_size=14, bullets=False
):
    box(slide, x, y, w, h, fill, name=f"Card: {head[:30]}")
    paras = [(head, {"size": head_size, "bold": True, "color": NAVY, "space": 4})]
    items = [body] if isinstance(body, str) else body
    paras += [(b, {"size": size, "bullet": 0 if bullets else None}) for b in items]
    text(slide, x + 0.12, y + 0.08, w - 0.24, h - 0.16, paras, space=3)


def stat(slide, x, y, w, big, label, color=NAVY, big_size=34, label_size=12):
    text(
        slide,
        x,
        y,
        w,
        0.62,
        [(big, {"size": big_size, "bold": True, "color": color})],
        space=0,
    )
    text(
        slide,
        x,
        y + 0.62,
        w,
        1.1,
        [(label, {"size": label_size, "color": MUTED})],
        space=0,
    )


def table(slide, x, y, w, rows, widths, size=11, row_h=0.3):
    shape = slide.shapes.add_table(
        len(rows),
        len(rows[0]),
        Inches(x),
        Inches(y),
        Inches(w),
        Inches(row_h * len(rows)),
    )
    t = shape.table
    tot = sum(widths)
    for i, cw in enumerate(widths):
        t.columns[i].width = Inches(w * cw / tot)
    for ri, row in enumerate(rows):
        t.rows[ri].height = Inches(row_h)
        for ci, val in enumerate(row):
            c = t.cell(ri, ci)
            c.fill.solid()
            c.fill.fore_color.rgb = NAVY if ri == 0 else (WHITE if ri % 2 else CARD)
            c.margin_left = c.margin_right = Inches(0.06)
            c.margin_top = c.margin_bottom = Inches(0.03)
            tf = c.text_frame
            tf.word_wrap = True
            par = tf.paragraphs[0]
            runs(par, val, size, WHITE if ri == 0 else INK, bold=ri == 0)
    return shape


def slide_with_title(prs, title: str):
    s = prs.slides.add_slide(prs.slide_layouts[4])  # TITLE_ONLY
    t = s.shapes.title
    t.left, t.top, t.width, t.height = 0, 0, prs.slide_width, Emu(572700)
    t.fill.solid()
    t.fill.fore_color.rgb = BLACK
    tf = t.text_frame
    tf.margin_left = Inches(0.25)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.text = ""
    runs(tf.paragraphs[0], title, 20, WHITE)
    tf.paragraphs[0].alignment = PP_ALIGN.LEFT
    return s


def foot(slide, body: str) -> None:
    """A source or caveat line at the foot of a slide (no speaker notes:
    the deck is read, not presented)."""
    text(
        slide,
        0.4,
        5.05,
        9.2,
        0.5,
        [(body, {"size": 10, "color": MUTED})],
        space=0,
        anchor=MSO_ANCHOR.BOTTOM,
        name="Footnote",
    )


# --- slides -----------------------------------------------------------------


def build(out: Path) -> None:
    prs = Presentation(str(TEMPLATE))
    ids = prs.slides._sldIdLst
    for sid in list(ids):
        prs.part.drop_rel(sid.rId)
        ids.remove(sid)

    # 1. Title
    s = prs.slides.add_slide(prs.slide_layouts[0])
    s.shapes.title.text = "Section 508 TOBI"
    sub = s.placeholders[1].text_frame
    sub.text = ""
    runs(
        sub.paragraphs[0],
        "An MCP server that runs the DHS Trusted Tester process in a real browser",
        18,
        MUTED,
    )
    p = sub.add_paragraph()
    runs(
        p,
        'GSA MCP and AI Agent Hackathon · Service "Read" Integration · Abby Bowman',
        14,
        MUTED,
    )
    p = sub.add_paragraph()
    runs(p, "Agent-assisted results, not certified Trusted Tester results", 12, MUTED)

    foot(
        s,
        "Code: github.com/abbybowman/tobi508. The evaluation document gives "
        "every figure in this deck with its source.",
    )

    # 2. The challenge
    s = slide_with_title(prs, "The challenge: a precise test, too few people to run it")
    stat(
        s,
        0.4,
        0.85,
        2.9,
        "2.00 / 5",
        "Testing and remediation: the weakest area of federal Section 508 "
        "programs (GSA, FY 2025)",
    )
    stat(
        s,
        3.55,
        0.85,
        2.9,
        "~70 hours",
        "of training plus an exam to become a certified Trusted Tester; in 2024 "
        "DHS lowered the pass mark from 90% to 85% to make it more attainable",
    )
    stat(
        s,
        6.7,
        0.85,
        2.9,
        "36 of 60",
        "Trusted Tester test conditions that automated scanners do not cover at "
        "all, including every keyboard trap",
    )
    box(s, 0.4, 3.35, 9.2, 1.75, TINT)
    text(
        s,
        0.6,
        3.45,
        8.8,
        1.6,
        [
            (
                "The DHS Trusted Tester process is the government's consistent, "
                "objective "
                "accessibility test: it says which keys to press and what counts as a "
                "failure.",
                {"size": 14},
            ),
            (
                "Scanners read a page's code; they cannot press Tab. Certified "
                "people can, "
                "and agencies do not have enough of them.",
                {"size": 14},
            ),
        ],
        anchor=MSO_ANCHOR.MIDDLE,
    )

    foot(
        s,
        "Sources: GSA FY 2024 and FY 2025 governmentwide Section 508 "
        'assessments; ONRR, "Trusted Tester"; Section508.gov, April 2024. '
        "Scanner coverage: our map of 60 Trusted Tester test conditions "
        "against axe-core 4.14 and pa11y 10.",
    )

    # 3. Hypothesis
    s = slide_with_title(prs, "Our hypothesis")
    rows = [
        (
            "FOR",
            "agencies with only a few certified Trusted Testers and no capacity "
            "to test pages at scale,",
        ),
        (
            "GIVEN",
            "that the Trusted Tester process is built to be mechanical and "
            "consistent, with only a few judgment calls,",
        ),
        (
            "IF",
            "we combine scripted steps in a real browser with narrow, rubric-based "
            "model judgments,",
        ),
        (
            "THEN",
            "we can find clear failures accurately and consistently, including "
            "ones scanners cannot see, and leave the unclear cases for a person,",
        ),
        (
            "THUS",
            "certified testers can cover far more pages, and site owners can fix "
            "obvious problems without waiting for a full manual test.",
        ),
    ]
    for i, (k, v) in enumerate(rows):
        y = 0.8 + i * 0.82
        box(s, 0.4, y, 1.3, 0.72, NAVY, name=f"Label {k}")
        text(
            s,
            0.4,
            y,
            1.3,
            0.72,
            [(k, {"size": 16, "bold": True, "color": WHITE})],
            anchor=MSO_ANCHOR.MIDDLE,
            align=PP_ALIGN.CENTER,
        )
        text(s, 1.9, y, 7.7, 0.72, [(v, {"size": 15})], anchor=MSO_ANCHOR.MIDDLE)

    foot(
        s,
        "In the spirit of SSA's ANDI, the free inspector Trusted Testers "
        "already use: TOBI supports certified testers; it does not replace "
        "them.",
    )

    # 4. Why not just give an agent a browser?
    s = slide_with_title(prs, "Why not just give an AI agent a browser?")
    text(
        s,
        0.4,
        0.8,
        9.2,
        0.6,
        [
            (
                "Same model, same instructions, same pages, scored blind against a "
                "certified Trusted Tester. Unsafe error: a PASS where the tester "
                "found a "
                "failure.",
                {"size": 13, "color": MUTED},
            )
        ],
    )
    card(
        s,
        0.4,
        1.45,
        4.4,
        2.3,
        "Agent with a general browser tool",
        [
            "Unsafe errors per run:",
            "**20, 16** (round 1)   **20, 17** (round 2)",
            "In round 1 it reported no failure on any page. It passed every "
            "unlabeled search field and took page landmarks for a way to skip "
            "repeated content.",
        ],
    )
    card(
        s,
        5.2,
        1.45,
        4.4,
        2.3,
        "Agent with TOBI",
        [
            "Unsafe errors per run:",
            "**0, 0, 0** (round 1)   **3, 5** (round 2)",
            "Every round 2 unsafe error came from a rule deciding alone, the same "
            "cells each run; those rules are fixed. None came from a model's answer.",
        ],
        fill=TINT,
    )
    text(
        s,
        0.4,
        3.95,
        9.2,
        1.2,
        [
            (
                "**The procedure has to be encoded, not prompted.** A capable agent "
                "knows "
                "what WCAG says; it does not follow a 90-page test procedure step by "
                "step.",
                {"size": 15},
            )
        ],
    )

    foot(
        s,
        "Round 1: 9 www.nasa.gov pages (Nov 4). Round 2: 10 svs.gsfc.nasa.gov "
        "pages (Nov 8). Both agents: Claude Sonnet 5.5; the baseline had "
        "Playwright MCP and web access instead of TOBI. Scored per WCAG "
        "criterion.",
    )

    # 5. The solution
    s = slide_with_title(prs, "The solution: an MCP server that follows the procedure")
    steps = [
        "**Record** the page once in real Chrome; replay it for every check",
        "**Walk** it with the keyboard, fill in forms, watch for motion, compare pages",
        "**Decide** what the procedure decides mechanically, from versioned rules",
        "**Ask** a pinned model narrow questions with evidence and a rubric; "
        '"unsure" goes to a person',
        "**Report** by Trusted Tester test ID, in plain language, with screenshots, "
        "and a draft in DHS's own report format",
    ]
    for i, st in enumerate(steps):
        y = 0.85 + i * 0.8
        box(s, 0.4, y + 0.1, 0.5, 0.5, NAVY, name=f"Step {i + 1}")
        text(
            s,
            0.4,
            y + 0.1,
            0.5,
            0.5,
            [(str(i + 1), {"size": 16, "bold": True, "color": WHITE})],
            anchor=MSO_ANCHOR.MIDDLE,
            align=PP_ALIGN.CENTER,
        )
        text(s, 1.05, y, 4.6, 0.72, [(st, {"size": 13})], anchor=MSO_ANCHOR.MIDDLE)
    card(
        s,
        6.0,
        0.95,
        3.6,
        3.9,
        "Five tools, each a whole task",
        [
            "tobi_run_tt_tests: test a page",
            "tobi_run_status: wait for a long run",
            "tobi_answer_questions: record answers",
            "tobi_explain: a result in plain words",
            "tobi_read_report: read or compare report files",
            "Resources: the TT text (tt://) and a run's evidence (run://)",
            "**22 of 61 tests:** keyboard, focus, forms, moving and flashing content, "
            "consistency across a site's pages",
        ],
        fill=TINT,
        size=13,
        bullets=True,
    )

    foot(
        s,
        "Python, FastMCP, Pydantic and Playwright, from GSA's template. stdio "
        "by default; hosted over HTTP only behind the agency's sign-in. Any MCP "
        "client is the front end.",
    )

    # 6. Architecture
    s = slide_with_title(prs, "Server design: how a page gets tested")
    pic = s.shapes.add_picture(
        str(DIAGRAM), Inches(1.25), Inches(0.68), height=Inches(4.25)
    )
    pic.name = "Flow diagram"
    pic._element.nvPicPr.cNvPr.set(
        "descr",
        (
            "Flow diagram, How TOBI tests a page. Solid lines are built and running "
            "today; dashed lines are planned. 1: the developer's AI agent, any MCP "
            "client, asks TOBI to test a page with tobi_run_tt_tests. Inside the "
            "TOBI MCP server: 2, record the page once in real Chrome, and every "
            "check runs on the replay, not the live site; 3, walk and collect: Tab "
            "through the page, fill in forms, watch for motion, compare other "
            "pages; 4, rules decide, one rules spec per Trusted Tester test with "
            "each step citing the DHS PDF, giving an outcome of PASS, FAIL, DOES "
            "NOT APPLY or NEEDS REVIEW with evidence. Held back when unsure: a rule "
            "that cannot decide says NEEDS REVIEW, and a PASS or DOES NOT APPLY "
            "becomes NEEDS REVIEW when a test did not read everything. When a rule "
            "needs a judgment it asks an open question; 5, the server judge, TOBI's "
            "own pinned model given evidence, pictures and a rubric, answers yes, "
            "no or unsure. A sure answer goes back to the rule. Unsure, or a failed "
            "call, goes to 7, a person on a signed-in review page whose answer "
            "overrides the model's (planned). Outcomes go to 6, a draft report "
            "(pre-SCRT) marked not certified, recording who answered what, and "
            "later to 8, the Trusted Tester's own SCRT record once they certify "
            "every row (planned). Results and a link to the full report go back to "
            "the agent."
        ),
    )

    foot(
        s,
        "One module per Trusted Tester test, one rules spec per module, one "
        "tool per file: adding a test changes no tool. The server judge "
        "answers every question type whenever the server has a model.",
    )

    # 7. Key decision: the procedure is the code
    s = slide_with_title(prs, "Key decision: the DHS procedure is the code")
    card(
        s,
        0.4,
        0.85,
        2.95,
        2.25,
        "One rules file per test",
        [
            "Every step cites the Trusted Tester PDF's page.",
            "No outcome is decided anywhere else: not in evidence collection, the "
            "judge or the tools.",
        ],
    )
    card(
        s,
        3.525,
        0.85,
        2.95,
        2.25,
        "Versioned and locked",
        [
            "Every report records each rule's version.",
            "CI refuses a rule change without a new version number: what kept "
            "parallel AI coding sessions from overwriting each other.",
        ],
    )
    card(
        s,
        6.65,
        0.85,
        2.95,
        2.25,
        "Proportionate to the PDF",
        [
            "A step must match something the PDF asks a person to do.",
            "Anything past that goes to a person. The aim: a careful tester, not more.",
        ],
    )
    stat(s, 0.4, 3.4, 3.0, "1,557", "tests run on every change", big_size=26)
    stat(
        s,
        3.5,
        3.4,
        3.0,
        "149",
        "published answer-key pages (W3C, DHS, Section 508 Baseline)",
        big_size=26,
    )
    stat(
        s,
        6.6,
        3.4,
        3.0,
        "~560",
        "test pages of our own: frames, dialogs, trick text, late-drawing pages",
        big_size=26,
    )

    foot(
        s,
        "Built Oct 30 to Nov 18, 2026 by one person with Claude Code: about 990 "
        "commits, 137 merged pull requests. The developer reviewed rules and "
        "results, not each line of AI-written code; the tests made that safe.",
    )

    # 8. Key decision: record once
    s = slide_with_title(prs, "Key decision: record once, replay every check")
    text(
        s,
        0.4,
        0.85,
        4.4,
        3.9,
        [
            (
                "Every key press, form entry and screenshot happens on one recording "
                "of "
                "the page.",
                {"size": 15, "bold": True, "color": NAVY},
            ),
            (
                "Testing never touches the live site: no form is really submitted.",
                {"size": 14, "bullet": 0},
            ),
            (
                "Same recording, same evidence: run-to-run variation can only come "
                "from "
                "judgment, where it can be measured.",
                {"size": 14, "bullet": 0},
            ),
            (
                "Browser, ANDI, Playwright, rules, judge model and prompt hash are "
                "recorded in every report.",
                {"size": 14, "bullet": 0},
            ),
        ],
        space=10,
    )
    card(
        s,
        5.2,
        0.85,
        4.4,
        1.55,
        "Pages can lie; the browser cannot",
        [
            "Focus is read through Chrome's DevTools protocol, outside the page's "
            "reach. A test page whose script fakes focus still fails."
        ],
        fill=TINT,
    )
    card(
        s,
        5.2,
        2.6,
        4.4,
        1.75,
        "What a recording missed",
        [
            "A NASA page loaded a script only when used, so a keyboard trap did "
            "nothing on replay. Such scripts are now saved, and a test cannot PASS "
            "without them."
        ],
        fill=TINT,
    )

    # 9. Key decision: false PASS
    s = slide_with_title(prs, "Key decision: a false PASS is the worst error")
    ladder = [
        (
            "A rule decides",
            "PASS, FAIL or DOES NOT APPLY, with the PDF step it rests on",
        ),
        ("A rule cannot decide", "NEEDS REVIEW, never PASS"),
        ("The test did not read everything", "PASS and DOES NOT APPLY are held back"),
        (
            "A model gives an opinion",
            "PASS only when a key press or measurement confirms it",
        ),
    ]
    for i, (k, v) in enumerate(ladder):
        y = 0.85 + i * 0.72
        box(s, 0.4, y, 2.9, 0.6, NAVY, name=f"When: {k}")
        text(
            s,
            0.45,
            y,
            2.8,
            0.6,
            [(k, {"size": 13, "bold": True, "color": WHITE})],
            anchor=MSO_ANCHOR.MIDDLE,
        )
        text(s, 3.45, y, 2.6, 0.6, [(v, {"size": 13})], anchor=MSO_ANCHOR.MIDDLE)
    card(
        s,
        6.2,
        0.85,
        3.4,
        2.75,
        "Example: keyboard trap",
        [
            "TOBI presses Shift+Tab, arrows, Escape and Enter to get out.",
            "The model only reads the page for a documented escape key.",
            "**TOBI then presses that key.** Only if focus leaves is it a PASS.",
        ],
        fill=TINT,
    )
    text(
        s,
        0.4,
        3.85,
        9.2,
        1.3,
        [
            (
                "A false PASS hides a barrier from someone who cannot use a mouse; a "
                "false "
                "FAIL costs a developer time. **Our score weights an unsafe error "
                "-3, any "
                "other error -1, agreement +1, and a result left for a person 0.**",
                {"size": 14},
            )
        ],
    )

    # 10. Key decision: the judge moves into the server
    s = slide_with_title(prs, "Key decision: the judge moved into the server")
    cols = [
        (
            "Round 1: the calling agent judges",
            [
                "No agent answered TOBI's questions unless told to.",
                "Told to, the score rose from 44-47 to 82.",
                'Asked to say what each picture showed, one wrote it "as if I had '
                'looked, but I never opened those images".',
            ],
        ),
        (
            "Round 2: a server judge, on trial",
            [
                "Answered all 194 questions in each of 3 repeats; repeats agreed on "
                "194 "
                "of 200 results.",
                "But **not more accurate**: more false FAILs, most from one question "
                "whose evidence was faulty.",
            ],
        ),
        (
            "Now: the server judges",
            [
                "One pinned model and prompt, recorded in every report.",
                "Unsure goes to a person.",
                "The calling agent explains results in the user's project and helps "
                "fix them.",
            ],
        ),
    ]
    for i, (h, b) in enumerate(cols):
        card(s, 0.4 + i * 3.125, 0.85, 2.95, 2.95, h, b, fill=TINT if i == 2 else CARD)
    text(
        s,
        0.4,
        4.0,
        9.2,
        1.2,
        [
            (
                "**Why:** repeatable, auditable and measurable, not smarter. Fixing "
                "the "
                "evidence fixed most wrong answers.",
                {"size": 14},
            ),
            (
                f"Re-measured Nov 19 on round 3's pages, 3 runs each: {FILL}",
                {"size": 13, "color": MUTED},
            ),
        ],
    )

    foot(
        s,
        "Round 2's server judge erred only toward FAIL, mostly because elements "
        "were placed while the page was still scrolling. Fixing that evidence, "
        "not the prompt, fixed the answers.",
    )

    # 11. Demo
    s = slide_with_title(prs, "Demo: NASA's Artemis III page, in plain words")
    beats = [
        ("0:00", "What TOBI is, and why scanners cannot do this"),
        ("0:25", "Sign-in: only NASA people reach the hosted server"),
        ("0:55", "Ask in plain words: test a page and two others from its site"),
        ("1:20", "The keyboard walk, sped up (about 11 minutes)"),
        ("1:50", "Results, and the questions only judgment can answer"),
        ("2:40", "Explain the results and the tool's limits"),
        ("3:25", "The draft report beside the certified tester's own"),
        ("4:25", "Every call audited; not certified"),
    ]
    for i, (t, b) in enumerate(beats):
        y = 0.85 + i * 0.5
        text(
            s,
            0.4,
            y,
            0.8,
            0.45,
            [(t, {"size": 14, "bold": True, "color": NAVY})],
            anchor=MSO_ANCHOR.MIDDLE,
        )
        text(s, 1.25, y, 4.6, 0.45, [(b, {"size": 13})], anchor=MSO_ANCHOR.MIDDLE)
    card(
        s,
        6.2,
        0.95,
        3.4,
        1.2,
        "The 5-minute video",
        ["Uploaded with this deck.", f"Link: {FILL}"],
        fill=TINT,
    )

    # 12. Evaluation setup
    s = slide_with_title(prs, "Evaluation: three comparisons, scored by exact match")
    card(
        s,
        0.4,
        0.85,
        2.95,
        2.35,
        "vs. published answer keys",
        [
            "114 W3C test cases with DHS's Trusted Tester verdicts; 35 Section 508 "
            "Baseline Alignment pages.",
            "A development set: the rules were written with them in view.",
        ],
    )
    card(
        s,
        3.525,
        0.85,
        2.95,
        2.35,
        "vs. a certified Trusted Tester",
        [
            "29 NASA pages on 3 sites, each tested by hand in DHS's own report tool.",
            "Commit and reveal: TOBI's results are locked before the answers go in.",
        ],
        fill=TINT,
    )
    card(
        s,
        6.65,
        0.85,
        2.95,
        2.35,
        "vs. a general-purpose agent",
        [
            "The same model and instructions with Playwright MCP and the web instead "
            "of TOBI.",
            "Harder than a no-tool baseline.",
        ],
    )
    text(
        s,
        0.4,
        3.45,
        9.2,
        1.5,
        [
            (
                "No LLM grades the results: outcomes are categories, compared in code.",
                {"size": 14, "bullet": 0},
            ),
            (
                "Results a rule decided are scored apart from results a model's answer "
                "decided.",
                {"size": 14, "bullet": 0},
            ),
            (
                "After any change to a question, a fresh agent answers it from TOBI's "
                "output alone (37 runs).",
                {"size": 14, "bullet": 0},
            ),
        ],
    )

    # 13. Results
    s = slide_with_title(prs, "Results: no unsafe errors after the fixes")
    stat(
        s,
        0.4,
        0.8,
        3.0,
        "0 of 593",
        "unsafe errors on all 29 pages, rerun Nov 18 after the fixes",
    )
    stat(
        s,
        3.5,
        0.8,
        3.0,
        "93%",
        "agreement with the certified tester where TOBI decided (331 of 355)",
    )
    stat(
        s, 6.6, 0.8, 3.0, "40%", "left for a person (238 of 593): the price of caution"
    )
    table(
        s,
        0.4,
        2.6,
        9.2,
        [
            ["Evidence", "Agree", "Unsafe errors", "Left for a person"],
            [
                "Round 3, blind: a site never used before (10 pages)",
                "118 of 149 (79%)",
                "3 (both causes fixed)",
                "32%",
            ],
            ["Same pages, general agent with a browser", FILL, FILL, FILL],
            ["DHS's published verdicts (49 W3C cases)", "43 of 49", "0", "5 of 49"],
        ],
        [4.2, 1.6, 1.8, 1.6],
        size=12,
        row_h=0.42,
    )
    text(
        s,
        0.4,
        4.32,
        9.2,
        0.5,
        [
            (
                "The rerun used sites the tool was then fixed on: development "
                "evidence, not "
                "a blind result. Too few true failures per test to prove a miss rate: "
                "promising, not proven.",
                {"size": 11, "color": MUTED},
            )
        ],
    )

    foot(
        s,
        "Per site after the fixes: www.nasa.gov 79 of 82 agree, "
        "svs.gsfc.nasa.gov 131 of 141, science.data.nasa.gov 121 of 132; 0 "
        "unsafe on each. Round 3's 3 unsafe errors: Chrome's own form messages "
        "read as the page's, and a page that drew itself late.",
    )

    # 14. Cost and time
    s = slide_with_title(prs, "What it costs: cents per page, minutes per page")
    table(
        s,
        0.4,
        0.85,
        9.2,
        [
            ["Per page", "Model spend (list price)", "Clock time"],
            [
                "TOBI's browser work",
                "none",
                "1-6 min; 6-8 min with other pages of the site",
            ],
            ["TOBI's server judge", "$0.13 cached, $0.67 uncached", "about 1 min"],
            ["Calling agent driving TOBI", "$0.07-0.26", "mostly TOBI's browser time"],
            ["General agent with a browser", "$0.02-0.05", "10-20 s, and wrong"],
            ["Certified tester, by hand", "staff time", f"about 10-15 min {FILL}"],
        ],
        [3.0, 3.0, 3.2],
        size=12,
        row_h=0.42,
    )
    text(
        s,
        0.4,
        3.6,
        9.2,
        1.5,
        [
            (
                "**Model spend is small; browser time is the cost.** Every shortcut we "
                "measured (fewer images, not waiting for late pages) gave wrong "
                "results.",
                {"size": 14},
            ),
            (
                "Per page, TOBI is not faster than an experienced tester. It runs "
                "unattended and in parallel, needs no certified tester for what it "
                "decides, and gives the same evidence every time.",
                {"size": 14},
            ),
        ],
    )

    foot(
        s,
        "Model spend: Claude Sonnet 5.5 list prices as Claude Code reports "
        "them; an agency's own route will differ. Prompt caching cut the "
        "judge's cost about five times.",
    )

    # 15. Security
    s = slide_with_title(
        prs, "Security: public pages, untrusted content, signed-in hosting"
    )
    sec = [
        (
            "Internal networks",
            "Every browser connection is checked when it "
            "connects; private and cloud-metadata addresses refused (56 tests).",
        ),
        (
            "Prompt injection",
            "Page text reaches the model only inside an escaped, "
            "untrusted block; it never picks a URL, tool or outcome.",
        ),
        ("The live site", "Key presses and form entries go only to the recording."),
        (
            "An agent posing as a person",
            "Every answer through MCP is recorded as the agent's; it outranks no one.",
        ),
        (
            "Secrets in logs",
            "No query strings, cookies, headers or page text in "
            "errors and logs (seeded-secret tests).",
        ),
        (
            "Hosted access",
            "Agency sign-in (OIDC); runs visible only to their "
            "owner; one audit line per call.",
        ),
    ]
    for i, (h, b) in enumerate(sec):
        x = 0.4 + (i % 3) * 3.125
        y = 0.85 + (i // 3) * 1.85
        card(s, x, y, 2.95, 1.7, h, b)
    text(
        s,
        0.4,
        4.45,
        9.2,
        0.45,
        [
            (
                'Every result says "not a certified Trusted Tester result"; a report '
                "cannot be marked certified.",
                {"size": 13, "bold": True, "color": NAVY},
            )
        ],
    )

    foot(
        s,
        "Known gap: no network-level egress rules on the host yet, as a second "
        "layer. Page content may shape a request only in a few capped, approved "
        "cases, all on the tested page's own host.",
    )

    # 16. MCP lessons
    s = slide_with_title(prs, "Six lessons for building MCP servers")
    lessons = [
        (
            "1. Don't depend on the agent's diligence",
            "Agents skipped questions and pictures, and filled proof fields without "
            "looking. Put correctness-critical steps in the server.",
        ),
        (
            "2. Put the next step in the data",
            "Wording lost to the agent's idea of done. One finish=true call and a "
            "to-do list at the end worked.",
        ),
        (
            "3. In practice, only tools count",
            "Agents seldom read resources and cannot start prompts. Attach what they "
            "must see to tool results.",
        ),
        (
            "4. Design for the client's limits",
            "Timeouts, result size, unseen progress: return in 45 s and keep the run "
            "going; one page's 96 questions became 4.",
        ),
        (
            "5. The server owns the verdict",
            "Pin the model that decides; let the client agent explain and fix. "
            "Sampling would borrow the user's model.",
        ),
        (
            "6. Encode the expertise as rules",
            "Versioned rules a domain expert can review; narrow rubric questions; "
            "tests every change must pass.",
        ),
    ]
    for i, (h, b) in enumerate(lessons):
        x = 0.4 + (i % 3) * 3.125
        y = 0.8 + (i // 3) * 2.2
        card(
            s, x, y, 2.95, 2.05, h, b, fill=TINT if i in (0, 4) else CARD, head_size=13
        )

    # 17. Limits and next
    s = slide_with_title(prs, "Limits, and what comes next")
    card(
        s,
        0.4,
        0.85,
        4.4,
        3.9,
        "Limits",
        [
            "22 of 61 Trusted Tester tests",
            "29 pages, 3 NASA sites, one certified tester, who is also the developer",
            "Every site is now a development site",
            "One browser, one window size, from a recording",
            "About a third of results go to a person",
        ],
        size=14,
        bullets=True,
    )
    card(
        s,
        5.2,
        0.85,
        4.4,
        3.9,
        "Next",
        [
            "A blind round on a new site, with a second certified tester",
            "A signed-in page where a person answers what the model was unsure of",
            "More tests where scanners and people disagree most: images, contrast, "
            "headings",
            "Another agency can fork it and host it with its own sign-in",
            "Elicitation, so the server can ask the user directly",
        ],
        fill=TINT,
        size=14,
        bullets=True,
    )

    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    build(Path(sys.argv[1]))
