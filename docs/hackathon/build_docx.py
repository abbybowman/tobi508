"""Build the evaluation document in GSA's Word template from its Markdown source.

    python3 docs/hackathon/build_docx.py SOURCE.md OUT.docx

(docs/hackathon/README.md gives the exact command.)

Needs python-docx (not a project dependency: it builds a submission file,
not the server). The template is GSA's sample, vendored byte for byte in
docs/hackathon/templates/; its body is replaced and its styles, numbering and
table borders are kept. Handles the Markdown this folder uses: front-matter
title and subtitle, ## and ### headings, paragraphs, - and 1. lists, pipe
tables, **bold**, *italic*, `code` and [links](url). Blockquotes are drafting
notes and are left out.
"""

from __future__ import annotations

import copy
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

TEMPLATE = Path(__file__).parent / "templates" / "gsa-sample-evaluation-document.docx"
TABLE_W = 9360  # dxa, the sample's table width (6.5 in)
INLINE = re.compile(
    r"(\*\*(?P<b>.+?)\*\*|\*(?P<i>[^*]+?)\*|`(?P<c>[^`]+)`|\[(?P<lt>[^\]]+)\]\((?P<lu>[^)]+)\))"
)


def add_runs(par, text: str, bold=False, italic=False) -> None:
    pos = 0
    for m in INLINE.finditer(text):
        if m.start() > pos:
            _run(par, text[pos : m.start()], bold, italic)
        if m.group("b") is not None:
            add_runs(par, m.group("b"), True, italic)
        elif m.group("i") is not None:
            add_runs(par, m.group("i"), bold, True)
        elif m.group("c") is not None:
            r = _run(par, m.group("c"), bold, italic)
            r.font.name = "Courier New"
        else:
            _link(par, m.group("lt"), m.group("lu"), bold, italic)
        pos = m.end()
    if pos < len(text):
        _run(par, text[pos:], bold, italic)


def _run(par, text, bold, italic):
    r = par.add_run(text)
    r.bold = bold or None
    r.italic = italic or None
    return r


def _link(par, text, url, bold, italic) -> None:
    rid = par.part.relate_to(url, RT.HYPERLINK, is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), rid)
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "1155CC")
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rpr.append(color)
    rpr.append(u)
    if bold:
        rpr.append(OxmlElement("w:b"))
    if italic:
        rpr.append(OxmlElement("w:i"))
    r.append(rpr)
    t = OxmlElement("w:t")
    t.text = text
    t.set(qn("xml:space"), "preserve")
    r.append(t)
    h.append(r)
    par._p.append(h)


class Lists:
    """Bullets use the sample's bullet list; each numbered list restarts at 1."""

    def __init__(self, doc):
        self.numbering = doc.part.numbering_part.element
        nums = self.numbering.findall(qn("w:num"))
        self.next_id = max(int(n.get(qn("w:numId"))) for n in nums) + 1
        self.bullet = self._abstract_for("bullet")
        self.decimal = self._abstract_for("decimal")
        self.bullet_num = self._new(self.bullet, restart=False)

    def _abstract_for(self, fmt: str) -> str:
        for a in self.numbering.findall(qn("w:abstractNum")):
            lvl = a.find(qn("w:lvl"))
            if lvl.find(qn("w:numFmt")).get(qn("w:val")) == fmt:
                return a.get(qn("w:abstractNumId"))
        raise SystemExit(f"template has no {fmt} list")

    def _new(self, abstract: str, restart: bool) -> int:
        n = OxmlElement("w:num")
        n.set(qn("w:numId"), str(self.next_id))
        a = OxmlElement("w:abstractNumId")
        a.set(qn("w:val"), abstract)
        n.append(a)
        if restart:
            o = OxmlElement("w:lvlOverride")
            o.set(qn("w:ilvl"), "0")
            s = OxmlElement("w:startOverride")
            s.set(qn("w:val"), "1")
            o.append(s)
            n.append(o)
        self.numbering.append(n)
        self.next_id += 1
        return self.next_id - 1

    def numbered(self) -> int:
        return self._new(self.decimal, restart=True)


def set_num(par, num_id: int) -> None:
    ppr = par._p.get_or_add_pPr()
    numpr = OxmlElement("w:numPr")
    ilvl = OxmlElement("w:ilvl")
    ilvl.set(qn("w:val"), "0")
    nid = OxmlElement("w:numId")
    nid.set(qn("w:val"), str(num_id))
    numpr.append(ilvl)
    numpr.append(nid)
    ppr.append(numpr)


def spacing(par, before=0, after=0) -> None:
    par.paragraph_format.space_before = Pt(before)
    par.paragraph_format.space_after = Pt(after)


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def add_table(doc, rows: list[list[str]], header: bool) -> None:
    ncol = len(rows[0])

    # Column widths in proportion to their longest cell, within limits.
    def col(i):
        return [re.sub(r"[*`]", "", r[i]) if i < len(r) else "" for r in rows]

    # Each column at least fits its longest word (about 105 dxa a character
    # at 9.5 pt, plus cell margins); the rest is shared by longest cell.
    floor = [
        max((len(w) for c in col(i) for w in c.split()), default=1) * 105 + 200
        for i in range(ncol)
    ]
    weights = [min(max(max(len(c) for c in col(i)), 8), 60) for i in range(ncol)]
    widths = [max(f, int(TABLE_W * w / sum(weights))) for f, w in zip(floor, weights)]
    over = sum(widths) - TABLE_W
    if over > 0:  # take the excess from columns wider than their floor
        slack = [w - f for w, f in zip(widths, floor)]
        widths = [w - int(over * sl / sum(slack)) for w, sl in zip(widths, slack)]
    widths[-1] = TABLE_W - sum(widths[:-1])
    t = doc.add_table(rows=len(rows), cols=ncol)
    tpr = t._tbl.tblPr
    for tag, val in (("w:tblW", str(TABLE_W)),):
        el = OxmlElement(tag)
        el.set(qn("w:w"), val)
        el.set(qn("w:type"), "dxa")
        tpr.append(el)
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "8")
        b.set(qn("w:space"), "0")
        b.set(qn("w:color"), "000000")
        borders.append(b)
    tpr.append(borders)
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tpr.append(layout)
    grid = t._tbl.tblGrid
    for gc, w in zip(grid.findall(qn("w:gridCol")), widths):
        gc.set(qn("w:w"), str(w))
    for ri, row in enumerate(rows):
        tr = t.rows[ri]
        if header and ri == 0:
            trpr = tr._tr.get_or_add_trPr()
            h = OxmlElement("w:tblHeader")
            trpr.append(h)
        for ci in range(ncol):
            cell = tr.cells[ci]
            tcpr = cell._tc.get_or_add_tcPr()
            tcw = OxmlElement("w:tcW")
            tcw.set(qn("w:w"), str(widths[ci]))
            tcw.set(qn("w:type"), "dxa")
            tcpr.append(tcw)
            mar = OxmlElement("w:tcMar")
            for side in ("top", "left", "bottom", "right"):
                m = OxmlElement(f"w:{side}")
                m.set(qn("w:w"), "80")
                m.set(qn("w:type"), "dxa")
                mar.append(m)
            tcpr.append(mar)
            if header and ri == 0:
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:fill"), "EDEDED")
                tcpr.append(shd)
            text = row[ci] if ci < len(row) else ""
            par = cell.paragraphs[0]
            spacing(par)
            par.paragraph_format.line_spacing = 1.0
            bold = (header and ri == 0) or (not header and ci == 0)
            add_runs(par, text, bold=bold)
            for r in par.runs:
                r.font.size = Pt(9.5)
            for h in par._p.findall(qn("w:hyperlink")):
                for rpr in h.iter(qn("w:rPr")):
                    sz = OxmlElement("w:sz")
                    sz.set(qn("w:val"), "19")
                    rpr.append(sz)
    gap = doc.add_paragraph()
    spacing(gap, 0, 0)


def build(src: Path, out: Path) -> None:
    text = src.read_text()
    meta = {}
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if fm:
        for line in fm.group(1).splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"').replace('\\"', '"')
        text = text[fm.end() :]

    doc = Document(str(TEMPLATE))
    body = doc.element.body
    sect = copy.deepcopy(body.find(qn("w:sectPr")))
    for child in list(body):
        body.remove(child)
    body.append(sect)
    lists = Lists(doc)

    if "title" in meta:
        doc.add_paragraph(meta["title"], style="Title")
    if "subtitle" in meta:
        p = doc.add_paragraph(meta["subtitle"].replace('\\"', '"'), style="Subtitle")
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    lines = text.splitlines()
    i = 0
    para: list[str] = []
    num_id = None

    def flush():
        nonlocal para
        if para:
            p = doc.add_paragraph()
            add_runs(p, " ".join(para))
            spacing(p, 0, 8)
            para = []

    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            flush()
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if not re.match(r"\d+\. ", nxt):
                num_id = None  # a numbered list ends; the next one restarts at 1
            i += 1
            continue
        if s.startswith(">"):
            flush()
            i += 1
            continue
        if s.startswith("## ") or s.startswith("### "):
            flush()
            level = "Heading3" if s.startswith("## ") else "Heading4"
            doc.add_paragraph(s.lstrip("#").strip(), style=level)
            i += 1
            continue
        if s.startswith("|"):
            flush()
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(cells(lines[i]))
                i += 1
            rule = re.compile(r":?-{3,}:?")
            rows = [r for r in block if not all(rule.fullmatch(c) for c in r)]
            header = any(c for c in rows[0])
            if not header:
                rows = rows[1:]
            add_table(doc, rows, header)
            continue
        m = re.match(r"(- |\d+\. )(.*)", s)
        if m and not line.startswith("  "):
            flush()
            item = [m.group(2)]
            i += 1
            while (
                i < len(lines)
                and lines[i].startswith("  ")
                and lines[i].strip()
                and not re.match(r"\s+- ", lines[i])
            ):
                item.append(lines[i].strip())
                i += 1
            p = doc.add_paragraph()
            add_runs(p, " ".join(item))
            spacing(p, 0, 3)
            if m.group(1) == "- ":
                set_num(p, lists.bullet_num)
            else:
                if num_id is None:
                    num_id = lists.numbered()
                set_num(p, num_id)
            # Nested bullets ("  - ") become indented bullets of the same list.
            while i < len(lines) and re.match(r"\s+- ", lines[i]):
                sub = doc.add_paragraph()
                add_runs(sub, lines[i].strip()[2:])
                spacing(sub, 0, 2)
                set_num(sub, lists.bullet_num)
                sub.paragraph_format.left_indent = Pt(54)
                i += 1
            continue
        para.append(s)
        i += 1
    flush()
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    build(Path(sys.argv[1]), Path(sys.argv[2]))
