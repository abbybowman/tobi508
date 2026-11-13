import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))
from evals import judging  # noqa: E402
from evals.apijudge_gate import KEYS  # noqa: E402
from evals.scoring import adjudications, decided_tests  # noqa: E402
from evals.scoring import score as score_page  # noqa: E402
from tobi508 import scrt  # noqa: E402
from tobi508.compare import compare, page_key  # noqa: E402
from tobi508.models import Report  # noqa: E402

out = Path(sys.argv[1])
listed = judging.parse_pages((KEYS / "pages.txt").read_text("utf-8"))
keys = judging.read_keys(KEYS, listed)
adj = adjudications(KEYS)
pid = {u: f"p{n:02d}" for n, (u, _) in enumerate(listed, 1)}
rows = []
for rd in sorted((out / "runs").iterdir()):
    if not (rd / "report.json").is_file():
        continue
    rep = Report.model_validate_json((rd / "report.json").read_text())
    url = rep.target if hasattr(rep, "target") else rep.url
    pre = scrt.write_for_run(rd, rd / "report.json", rep)
    sc = score_page(
        compare(keys[url][1], scrt.parse(Path(pre).read_text("utf-8"))),
        adj.get(page_key(url)),
    )
    dec = decided_tests(rep)
    by = {f.test_id.value: f for f in rep.findings}
    for t in sc.tests:
        tid = t.test.test_id
        if tid not in ("9.A", "9.B", "9.C"):
            continue
        f = by[tid]
        rows.append(
            dict(
                page=pid[url],
                url=url[25:] or "/",
                test=tid,
                key=t.test.first.result.value if t.test.first.result else None,
                tool=t.test.second.result.value
                if t.test.second.result
                else "NEEDS REVIEW",
                verdict=t.verdict.value,
                judge=bool(dec.get(tid)),
                rows=[r for r in f.rows if ":" not in r],
            )
        )
rows.sort(key=lambda r: (r["test"], r["page"]))
(out / "cells.json").write_text(json.dumps(rows, indent=1))
for r in rows:
    print(
        r["test"],
        r["page"],
        r["url"],
        "key:",
        r["key"],
        "tool:",
        r["tool"],
        r["verdict"],
        "judge" if r["judge"] else "rule",
        r["rows"],
    )
