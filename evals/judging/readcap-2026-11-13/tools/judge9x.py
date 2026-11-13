"""Answer the saved 9.A/9.C questions with the server judge (CLI route),
then rescore. Usage: judge9x.py RUNS_PARENT [--dry]"""

import asyncio
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))
from tobi508 import apijudge  # noqa: E402
from tobi508.config import Settings  # noqa: E402

out = Path(sys.argv[1])
s = Settings(
    runs_dir=out / "runs",
    run_ttl_hours=720,
    judge_backend="api",
    judge_route="cli",
    judge_types="9.A,9.C",
    judge_cap_s=900,
)
ids = sorted(p.name for p in (out / "runs").iterdir() if (p / "report.json").is_file())
if "--dry" in sys.argv:
    got = apijudge.dry(s, ids, {"9.A", "9.C"})
    print(json.dumps(got["total"]), got["rough_input_tokens"])
else:

    async def main():
        for i in ids:
            st = await apijudge.judge_run(s, i)
            print(i, st, flush=True)

    asyncio.run(main())
