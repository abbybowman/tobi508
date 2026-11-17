# Get started

TOBI is an MCP server. Your agent (Claude Code here) starts it, or connects
to it, and calls its tools. There are three ways to run it; none of them
needs Keycloak or any sign-in. Sign-in (`AUTH=oidc`) is only for a server
other people reach over the network: [deploy-on-vast.md](deploy-on-vast.md).

| Way | You need | Use it when |
| --- | --- | --- |
| [1. From a clone, over stdio](#1-from-a-clone-over-stdio) | uv, git, Chrome or Chromium | You work on the code, or want a visible browser |
| [2. The image, over stdio](#2-the-image-over-stdio) | Docker or Podman | You only want to use it |
| [3. The image over HTTP, no sign-in](#3-the-image-over-http-no-sign-in) | Docker or Podman on Linux | Trying the server on a remote host (a VAST dev environment) before it is hosted |

Results are agent-assisted findings, never a certified Trusted Tester
result.

## 1. From a clone, over stdio

Works on Windows, macOS and Linux. Install
[uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```bash
git clone https://github.com/abbybowman/tobi508.git
cd tobi508
cp .env.example .env
uv sync
```

The browser. `.env` starts with installed Google Chrome, in a window
(`BROWSER_CHANNEL=chrome`, `HEADLESS=false`). With no Chrome, or no
display (a server, WSL, a container), use Playwright's Chromium instead:

```bash
uv run playwright install chromium   # Linux: add --with-deps for its system libraries (uses sudo)
```

and set `BROWSER_CHANNEL=chromium` and `HEADLESS=true` in `.env`.

Connect Claude Code (use the clone's full path):

```bash
claude mcp add tobi508 -- uv --directory /full/path/to/tobi508 run tobi508
```

or the same in a project's `.mcp.json`:

```json
{"mcpServers": {"tobi508": {"command": "uv", "args": ["--directory", "/full/path/to/tobi508", "run", "tobi508"]}}}
```

## 2. The image, over stdio

No clone and no Python: the image has the server, Chromium (headless) and
everything they need. The first pull downloads about 1.2 GB (2.8 GB on
disk), mostly Chromium and its libraries.

```bash
docker pull ghcr.io/abbybowman/tobi508:latest
claude mcp add tobi508 -- docker run -i --rm -e MCP_TRANSPORT=stdio ghcr.io/abbybowman/tobi508:latest
```

Podman works the same (`podman` for `docker`). `-e MCP_TRANSPORT=stdio`
is what matters: without it the image starts the hosted server, which
stops with `MCP_HOST must be one of 127.0.0.1, ::1 without sign-in: set
AUTH=oidc ...`. That message means "you started hosted mode", not "you
need Keycloak".

Run folders live inside the container and go when it stops; the agent
saves reports through MCP (`report_uri`) before then. Add more settings
with more `-e` flags (for example `-e ALLOWED_DOMAINS='[".gov",".mil",".edu"]'`).

## 3. The image over HTTP, no sign-in

The same server over HTTP, as it will be hosted, without sign-in. Without
sign-in it only listens on loopback (127.0.0.1), by design: it drives a
real browser, so it is never open on the network unauthenticated. So run
it on the host's network and reach it through that host's loopback.

On the host (Linux; `--network host` shares the host's loopback):

```bash
docker run -d --name tobi --network host -e MCP_HOST=127.0.0.1 ghcr.io/abbybowman/tobi508:latest
curl http://127.0.0.1:8000/health          # {"status":"healthy","service":"tobi508"}
```

If the host is remote (a VAST dev environment), forward the port from your
own machine, then connect Claude Code there:

```bash
ssh -L 8000:127.0.0.1:8000 <you>-dev       # keep this open
claude mcp add --transport http tobi508 http://127.0.0.1:8000/mcp
```

`-p 8000:8000` does not work here: the server listens on the container's
own loopback, which a published port cannot reach. Stop it with
`docker rm -f tobi`.

Open questions go to your agent by default. To have the server answer
some itself through a Messages API gateway (Luna or another), set the
`JUDGE_*` settings in `.env`, or with the image in a file passed with
`--env-file`: [deploy-on-vast.md, section 9](deploy-on-vast.md#9-the-yaml-for-the-cluster-admins).

## Check it works

Restart Claude Code, run `/mcp` and check `tobi508` is connected, then ask:

> Run TT test 4.C on https://www.section508.gov/

You get a result for 4.C (keyboard trap) in a minute or two, often with
one open question that Claude answers. Pages must be on the allowlist
(`ALLOWED_DOMAINS`, default `.gov` and `.mil`); any other address is
refused.

No internet from where the server runs? Test a page that ships with it,
with `DEV_MODE=true` (local files; never for real audits). In the image add
`-e DEV_MODE=true` and ask for
`file:///app/tests/fixtures/4c/f06-script-loop.html`; from a clone, set it
in `.env` and use that file's full path in your clone. 4.C comes back
NEEDS REVIEW with an open question (are there instructions to get out of
three looping links?).

## When it doesn't work

| You see | Why | Do |
| --- | --- | --- |
| `MCP_HOST must be one of 127.0.0.1, ::1 without sign-in` | The image's default command: hosted mode | Way 2 (`-e MCP_TRANSPORT=stdio`) or way 3 (`-e MCP_HOST=127.0.0.1 --network host`) |
| `AUTH=oidc: ... must be set` | `AUTH=oidc` is set without its Keycloak settings | Unset `AUTH` unless you are deploying: [deploy-on-vast.md](deploy-on-vast.md) |
| Chrome not found, or the browser fails to launch | No installed Chrome, or no display | `BROWSER_CHANNEL=chromium`, `HEADLESS=true`, `uv run playwright install chromium` |
| `421 Misdirected Request` over HTTP | The Host header is not a loopback name | Connect to `http://127.0.0.1:8000/mcp` through the tunnel, not the host's name |
| "not allowed" for a URL | The allowlist | Test a `.gov`/`.mil` page, or add the domain to `ALLOWED_DOMAINS` |
| `/mcp` shows tobi508 failed | The command did not start | Run the same command in a terminal and read its error |

**How we know.** 2026-11-16, Linux container: way 1 (Chromium, headless)
and way 2 (`ghcr.io/abbybowman/tobi508:latest`, Docker 29.9.2) each ran 4.C
on the fixture above through an MCP client over stdio; way 3 answered
`/health`, ran the same test over HTTP, refused a foreign Host header
(421), and the default command printed the `MCP_HOST` message. Not yet
checked: the Claude Code commands themselves, Windows and macOS, Podman,
and the ssh tunnel from a VAST dev environment.
