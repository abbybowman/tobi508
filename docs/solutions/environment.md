# The development environment: container, parallel tests, editing

Tooling notes, not rules about TT tests.

## The Linux container image (built in GitHub Actions, run on VAST)

**Problem.** A hosted deployment needs Chromium and its system libraries on
a Linux host. NASA's VAST (internal Forgejo plus Kubernetes dev
environments) runs in FIPS mode (`/proc/sys/crypto/fips_enabled` = 1):
Ubuntu images, Playwright's official ones among them, can't start OpenSSL
there, and apt fails inside VAST's nested rootless podman. So the image
can't be built on VAST.

**What we do.** `Dockerfile` builds from Debian (`python:3.11-slim-bookworm`)
with uv, the dev group, and `playwright install --with-deps chromium`
(Chromium, the headless shell and ffmpeg), running as uid 1000; about
2.2 GB unpacked. `.github/workflows/container.yml` builds it and pushes
`ghcr.io/abbybowman/tobi508:latest` and `:<sha>`; VAST only pulls and
runs it. `.dockerignore` keeps `.env`, `.venv`, `.git` and `runs/` out. It
was first committed as `dockerignore`, without the dot, so Docker ignored it
and the published image held `.git` (no secret was in it: CI checks out a
clean tree with no `.env`). The workflow's path filter does not include
`tests/`, so a change only to tests does not rebuild the image; run the
workflow by hand.

**Running the suite in the image, with progress.** Under `-q` the suite
prints a dot only as each test finishes, so a slow start looks like a hang.
Run it detached, so a dropped ssh connection doesn't end it, and read the
progress file:

```bash
podman run -d --name tt ghcr.io/abbybowman/tobi508:latest uv run --no-sync pytest -n 4 -v -p no:cacheprovider
podman exec tt cat /app/runs/test-progress.txt
podman logs tt 2>&1 | tail -30
podman rm tt
```

`-n auto` caps workers at the container's CPU limit (below). The suite
takes about 15 minutes at 4 workers.

**Serving from the image.** Its command serves HTTP on `0.0.0.0:8000` with
Chromium, headless, and runs and sign-in registrations under `/data`
(`RUNS_DIR`, `FASTMCP_HOME`). Without `AUTH=oidc` and its settings it
refuses to start: set them from the platform's secrets. To try it without
sign-in, keep it on the container's loopback and run the smoke test inside
(what the image workflow does on every build):

```bash
podman run -d --name tobi -e MCP_HOST=127.0.0.1 -e DEV_MODE=true ghcr.io/abbybowman/tobi508:latest
podman exec tobi uv run --no-sync python tests/container_smoke.py
podman rm -f tobi
```

### Working on a VAST dev environment

- **Each session:** `vastdev login`, then `vastdev up`, then
  `ssh <you>-dev`. `vastdev up` requests a fresh SSH certificate; without
  it, ssh fails with `Permission denied (publickey)` once yesterday's
  certificate has expired. The access token lasts 5 minutes and the
  refresh token 30, so after about 30 idle minutes `vastdev` logs in again.
- **Use PowerShell or Windows Terminal for ssh,** not Git Bash. vastdev
  writes Win32-OpenSSH's config, and Win32 ssh inside Git Bash's mintty
  window shows no prompt or output, so it looks hung while it is in fact
  logged in. Commands typed then run on VAST: `C:\...` paths fail there and
  ssh asks about VAST's own host key. If you must use Git Bash, put
  `winpty` in front of `/c/Windows/System32/OpenSSH/ssh.exe`.
- **Knowing where you are:** the dev container is a minimal RHEL 8.10
  with no `hostname` command (use `uname -n` or
  `cat /etc/redhat-release`), and its login shell does not read
  `~/.bashrc`. Add `[ -f ~/.bashrc ] && . ~/.bashrc` to `~/.bash_profile`
  and set a prompt such as `PS1="[vast \w]\$ "` in `~/.bashrc`.
- **Storage:** home is a 20 GB volume and persists across container
  restarts (an image pulled two days earlier was still there after a
  restart). Rootless podman keeps its images there
  (`~/.local/share/containers/storage`), so pulls count against it.
- **Dropped connections:** on 2026-11-06 opening a second ssh session
  closed the first and reset the second while the container stayed up
  (`stat -c %y /proc/1` showed it had started hours earlier, and
  `oom_kill` was 0). Cause unknown; until it is, use one session and run
  long jobs detached.

**How we know.** 2026-11-06: the `:latest` image in Docker on a 4-CPU Linux
host: the default 64 MB `/dev/shm` is enough (Playwright launches Chromium
with `--disable-dev-shm-usage`), and the full suite ran with 4 workers: 930
passed, 3 skipped, 1 xfailed, no failures, in 14 min 52 s. On VAST, the same
day: Chromium in the image loaded https://www.nasa.gov, and the suite (an
older `:latest` with 793 tests) ran detached with `-n 4` on the 4-CPU dev
container: 789 passed, 3 skipped, 1 xfailed, no failures, in 9 min 52 s. Its
ACT agreement lines matched the Docker run's case for case.

## The suite runs in parallel; shared files must be per worker

**Problem.** The full suite took 20 minutes serially. Tests mostly wait
(settle windows, timers, a 3 s key hold), so CPUs sat idle.

**What we do.** pytest-xdist, `-n auto` by default (one worker per CPU):
5.5 min on 4 CPUs; `-n 8` measured 3.5–3.9 min twice with no flakes. Every
test already had its own run folder, servers on ephemeral ports and browser
context. The one shared thing was the ACT scoreboard: each worker now writes
`tests/.act_scores/<worker>.json`, and only the controller (no `workerinput`)
clears them at session start. Anything new that writes a shared file from
tests needs the same treatment. Use `-n0` to run one test on its own.

**Known load-sensitive test.** `test_f29_feed_grows_live_and_footer_is_reachable_backward`
presses keys 20 ms apart on a live infinite feed; under `-n 8` it failed
once (2026-11-01) and passed alone and on the rerun. It checks the fixture,
not a rule; if it fails again, rerun it alone before looking further.

**In a container, `auto` counts the pod's CPU limit (2026-11-06).** xdist
counts the CPUs the scheduler shows (`sched_getaffinity`, the same number
`nproc` prints), which in a Kubernetes pod is every core of the node, not
the pod's limit. On VAST (4-CPU limit) a run under `-q` printed nothing and
seemed to hang; the likely cause is one worker, and so one Chromium, per
node core (with `-n 4` the full suite passed there in under 10 minutes;
`nproc` against the limit would confirm).
`tests/conftest.py` now implements `pytest_xdist_auto_num_workers` and caps
`auto` at the cgroup quota (v2 `cpu.max`, or v1 `cpu.cfs_quota_us`).
`PYTEST_XDIST_AUTO_NUM_WORKERS` or an explicit `-n` still wins. Verified:
`docker run --cpus=2` on a 4-CPU host started 2 workers, and a faked
`cpu.max` of 4 CPUs with 64 visible returned 4.

### A test that fails only on a busy machine: look for chance in the page first (2026-11-07)

`test_act_color_cycle_with_stop` (2.B on ACT efbfc7 inapplicable 3) failed about 1 run in 3 under `-n 8` on 4 CPUs and never alone, which looked like CPU starvation. The page picks one of four colours at random every second (`Math.random()`), so about one tick in four changes nothing. Pass T's watch is 6.5 s, and 2.B needs a change seen after 5 s: when the ticks near 5 s and 6 s both repeat (1 in 16), nothing moves late and 2.B is DOES NOT APPLY. On a busy machine the page starts its timer later, so fewer ticks fall in the window and it happens more often. Proof without load: with `Math.random` fixed so the colours repeat from the fifth tick, 2.B was DOES NOT APPLY every time; with every tick changing, NEEDS REVIEW.

What we do: the test fixes the page's `Math.random` with an init script (the page itself is not edited), so it tests the rules, not the dice. A test that checks an input on the page's run reads `run_check(...)["asked"]` (or `run_tests(..., asked=[])`) instead of running the page again; folding five such tests into the outcome tests removed seven pipeline runs (about 60-80 CPU s).

Where a run's CPU goes (4 CPUs, idle machine): 4-17 CPU s per test against 6-52 s of wall time; the Playwright driver and two browser launches are about 0.65 CPU s of that; pass T about 1.2 CPU s on a static page. The rest is Chromium doing the work (presses, settle polling, screenshots), which the outcomes need.

## Editing code that the formatter reflows

**Problem (for agents editing this repo).** `ruff format` rewraps long calls
and dicts. A later exact-string edit written against the pre-format text then
fails to match, and a script that asserts on the match aborts *before
writing*, so none of its edits land. This happened several times.

**What to do.** Run `uv run ruff format` right after each edit, then edit
against the formatted text. For larger changes, replace a block between two
stable marker lines (a comment or a `def`) instead of matching a long
expression. Check `git diff` after scripted edits.

## Working beside a running suite, and probing recordings

- **Never edit files while a background pytest runs.** The workers read
  the tree; an edit mid-run meant killing the suite and running it again,
  twice. Probe one page at a time beside a running suite.
- **The test server serves only `.html` and `.js` files** inside
  `tests/fixtures/`, from a map scanned at start: a new fixture of another
  type needs the map, not a path.
- **To probe a frozen recording,** use Playwright's `route_from_har` on
  its `pages/NNN.har.zip`. Frozen pages are not in git: restore them as the
  round's `results/ARCHIVE.md` says and check the manifest.
- **A second browser for comparisons** (TOBI itself is Chromium-only):
  `PLAYWRIGHT_BROWSERS_PATH=<scratch> uv run playwright install firefox`
  puts Firefox in a scratch folder with no system packages.
- **Model calls cost real tokens.** Use the Claude Code CLI route only;
  run the judge eval only for the question types a change touched; count
  requests with dry mode first and record measured tokens.

## A cloud container: make the browser trust its connections

**Problem.** In a Claude Code cloud container, a direct connection from
the egress proxy (`egress.py`) gets a certificate from the container's
gateway, which Chromium does not trust (`net::ERR_CERT_AUTHORITY_INVALID`).
The top-level page still loads (the navigation guard fetches it another
way), so the failure is silent: CSS, fonts and scripts fail (status -1 in
the recording). Step 6 (2026-11-13) lost six 19.A cells to it: the live
site search's results page never ran its scripts, so no search showed
results.

**What we do.** Tunnel through the container's own proxy, which hands the
browser the site's real certificate (checked: `cdn.jsdelivr.net` arrives
signed by Sectigo, verified against the system store). The egress proxy
still checks every address first; the upstream resolves the name again
(weaker against DNS rebinding, so it is off by default):

```bash
printf 'UPSTREAM_PROXY=%s\n' "$HTTPS_PROXY" >> .env
```

`.env` is git-ignored and the proxy's port changes with the container, so
set it in each new container. The test suite builds its settings without
`.env` (`_env_file=None`) and never needs it; the eval scripts (freeze,
`judging.py`, the gate) read it. Check: 19.A on round 2's 14194 in
`tested_frozen` mode found the page through the live search with no
script failed (without it: 13 scripts refused, W4). A recording made in a
new environment must have its CSS and scripts at status 200; the freeze
calls a page whose CSS, fonts and scripts mostly failed suspect.
