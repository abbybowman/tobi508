# How to deploy on VAST

For whoever puts the server on VAST (roadmap step 12) and the VAST admin
who answers its questions. Follow it top to bottom; the checklist at the
end is what to confirm on the first deployment.

**Status:** no deployment on VAST yet. Every value here is taken from the
code (`src/tobi508/config.py`, `app.py`, `access.py`, `routes.py`,
`runlog.py`), the `Dockerfile` and `.env.example`, not from memory. The
sign-in is tested against a stand-in provider (`tests/test_access_signin.py`),
not yet against a real Keycloak, VAST's or another, nor NASA Launchpad
(step 12b). Design and
reasons: [the hosted sign-in plan](../plans/2026-11-06-hosted-auth.md).

Results are agent-assisted, never a certified Trusted Tester result, on
VAST as anywhere else.

## 1. The Containerfile

The image is built by GitHub Actions (`.github/workflows/container.yml`),
not on VAST: VAST hosts run in FIPS mode and apt fails inside its nested
containers ([environment notes](../solutions/environment.md)). Every push
to `main` that changes what goes into the image publishes
`ghcr.io/abbybowman/tobi508:latest` and `ghcr.io/abbybowman/tobi508:<commit
sha>`. VAST's Containerfile is one line; pin the commit, so a deployment
is one known image:

```dockerfile
FROM ghcr.io/abbybowman/tobi508:<commit sha>
```

What the image already does (`Dockerfile`):

- Python 3.11 on Debian bookworm, Playwright's Chromium and the libraries
  it needs; runs as uid 1000 (`app`).
- `BROWSER_CHANNEL=chromium`, `HEADLESS=true`, `RUNS_DIR=/data/runs`,
  `FASTMCP_HOME=/data/fastmcp`.
- Its command serves MCP over streamable HTTP on `0.0.0.0:8000` (MCP
  endpoint `/mcp`). Without `AUTH=oidc` and every sign-in setting below it
  refuses to start ("set AUTH=oidc to listen beyond loopback", or
  "AUTH=oidc: ... must be set"), so a deployment missing its secrets fails
  closed.

## 2. Settings

Set them in the app's environment; the secrets from the platform's secret
store (a Kubernetes Secret), never in the Containerfile or git. Names are
case-insensitive; lists are JSON.

### Sign-in (required)

| Setting | Secret | What it does |
| --- | --- | --- |
| `AUTH` | no | `oidc`. Every MCP request needs a token; only then may the server listen beyond loopback. The default `none` refuses `0.0.0.0`. |
| `PUBLIC_BASE_URL` | no | The app's public URL, `https://<app host>` (https is required). The server's issuer and resource URLs are built from it; Keycloak sends people back to `{PUBLIC_BASE_URL}/auth/callback`; and its host is the only one besides `localhost` that passes the Host check. |
| `OIDC_CONFIG_URL` | no | `https://<keycloak host>/realms/<realm>/.well-known/openid-configuration` (https is required). Fetched at startup: if Keycloak cannot be reached, the server does not start. |
| `OIDC_CLIENT_ID` | no | The confidential client VAST provisions for the app. |
| `OIDC_CLIENT_SECRET` | **yes** | That client's secret. |
| `OIDC_JWT_SIGNING_KEY` | **yes** | Signs the tokens this server gives MCP clients and encrypts its stored client registrations. A long random string; keep it the same across restarts, or every client registers and signs in again. |

### Sign-in (optional, but set the first two before a second person signs in)

| Setting | Default | What it does |
| --- | --- | --- |
| `OIDC_AUDIENCE` | unset | The `aud` Keycloak's access tokens must carry. Unset skips the audience check. Keycloak puts only `account` there unless the client has an audience mapper (below). |
| `REQUIRED_GROUPS` | `[]` | The caller needs one of these values in `GROUP_CLAIM`, for example `["VAST--<client>--<slug>"]`. Empty: any person Keycloak signs in. A person outside the groups gets 401 after signing in, and an `authz.denied` audit line. |
| `GROUP_CLAIM` | `claim_groups` | The access-token claim holding groups (VAST's boilerplate's name). |
| `OIDC_CLIENT_REDIRECT_URIS` | `["http://localhost:*", "http://127.0.0.1:*"]` | Where MCP clients may be sent back after sign-in. Claude Code uses a localhost port, so the default serves it. |

### Behind VAST's HTTPS

| Setting | Default | What it does |
| --- | --- | --- |
| `FORWARDED_ALLOW_IPS` | `127.0.0.1,::1` | Uvicorn's (`uvicorn/config.py`), not the server's own. The addresses whose `X-Forwarded-Proto` and `X-Forwarded-For` headers the server believes. Set it to the address (or range) of VAST's ingress, which must send `X-Forwarded-Proto: https`. Without it the server takes requests for plain http, and its Origin check refuses a browser's "Allow Access" on the consent page (403 Forbidden Origin): nobody can sign in. Never `*` unless the ingress is the only way to reach the pod. |
| `MCP_PORT` | `8000` | The port the container listens on. |
| `MCP_TRANSPORT`, `MCP_HOST` | `streamable-http`, `0.0.0.0` | Set by the image's command; leave them. |

### Storage

| Setting | Default in the image | What it does |
| --- | --- | --- |
| `RUNS_DIR` | `/data/runs` | Run folders: each run's report, pre-SCRT file, evidence, screenshots, recordings (`page.har.zip`) and `owner` (the `sub` of the person who made it). |
| `FASTMCP_HOME` | `/data/fastmcp` | The sign-in proxy's store, under `oauth-proxy/<key fingerprint>/`: registered MCP clients, sign-ins in progress, and the map from this server's tokens to Keycloak's. On a fresh volume every client registers and signs in again. |
| `RUN_TTL_HOURS` | `24` | How long a run is kept after its last change. |

### The browser's way out

| Setting | Default | What it does |
| --- | --- | --- |
| `ALLOWED_DOMAINS` | `[".gov", ".mil"]` | The pages that may be tested, on every navigation and redirect hop. |
| `DEV_MODE` | `false` | Must stay `false` on VAST: `true` allows `file://` pages and `DEV_ALLOWED_ADDRESSES`. |
| `EGRESS_PORTS` | `[80, 443]` | Ports the browser may connect to. Every connection goes through the server's own egress proxy, which refuses any host that resolves to a private, loopback, link-local or metadata address. |
| `UPSTREAM_PROXY` | unset | Only if the pod's outbound HTTPS passes through a gateway that re-signs certificates with a CA Chromium does not trust: an `http://` proxy URL. The egress proxy checks each address as usual, then tunnels by name through it (weaker against DNS rebinding, since the gateway resolves the name again). Leave unset if pods reach public sites directly. |

### Open questions (the judge)

| Setting | Default | What it does |
| --- | --- | --- |
| `JUDGE_BACKEND` | `client` | `client`: every open question goes back to the calling agent (in Claude Code, Claude answers it by rubric; the user can override with `tobi_answer_questions`). Nothing else to set, and no model key on the server. `api`: the server answers the question types in `JUDGE_TYPES` itself. |
| `JUDGE_ROUTE` | `cli` | With `api`: `cli` runs `claude -p`, which is **not in the image**, so never use it on VAST; `anthropic-messages` calls a Messages API gateway. |
| `JUDGE_BASE_URL`, `JUDGE_API_KEY` (**secret**) | unset | The gateway and its key. With `api` and `anthropic-messages`, the server refuses to start without both. |
| `JUDGE_AUTH_HEADER` | `x-api-key` | The header the key goes in. |
| `JUDGE_MODEL` | `claude-sonnet-5-5` | The gateway's model name. |
| `JUDGE_TYPES` | empty | Test IDs whose questions the server answers, e.g. `4.B`. Empty: none, even with `api`. |
| `JUDGE_CONCURRENCY`, `JUDGE_CALL_TIMEOUT_S`, `JUDGE_CAP_S` | `3`, `300`, `900` | Requests at once, one request's limit, a run's whole judging phase. |
| `JUDGING_MODEL` | `none` | Recorded in every report; with `api`, set from the model and prompt. |

**With no gateway** (today: Luna or another is not settled; roadmap,
"Decisions waiting for Abby"), keep `JUDGE_BACKEND=client`. Runs work the
same; open questions are answered by the connecting agent.

### Capacity

| Setting | Default | What it does |
| --- | --- | --- |
| `MAX_CONCURRENT_RUNS` | `2` | Runs using a browser at once; others queue. |
| `CALL_WAIT_S` | `45` | How long one tool call waits before it returns a job id; `tobi_run_status` waits again. Keep it under the ingress's read timeout. |
| `MAX_RUN_S` | `1800` | The longest any run may take. |

The dev container was 4 CPU and 16 GB; a run with `MAX_CONCURRENT_RUNS=2`
can use two Chromiums at once, each with a page and its replays.

## 3. Where runs live, and for how long

- A run's folder is `RUNS_DIR/<run id>/`. It is deleted once it is older
  than `RUN_TTL_HOURS` (24 h) since its last change, when the next run
  starts (`runlog.prune_runs`); no timer deletes it otherwise. Every result
  says when (`expires_at`). Results belong in the user's own files: the
  agent reads `report_uri` and `pre_scrt_uri` (run:// links) and saves them
  before then.
- A run belongs to the person who made it: another signed-in person's
  `run://` read, `tobi_explain`, `tobi_answer_questions` or
  `tobi_run_status` sees it as missing.
- Jobs (runs still going, and the record of finished ones for
  `tobi_run_status`) and the other-pages cache live in the server's memory:
  a restart loses running jobs. Run **one replica**: a second would not see
  the first one's jobs, and its sign-in store would be separate.
- `/data` must be on storage that survives a restart, or point `RUNS_DIR`
  and `FASTMCP_HOME` at a path that does. The admin answered that the app's
  storage survives restarts unless `vastdev down` is run (plan, question
  1); which path that is, is still to confirm.
- There is no other retention rule yet, and no store that outlives the
  volume (SECURITY.md, "Before a hosted deployment").

## 4. The health route

`GET /health` answers `200 {"status": "healthy", "service": "tobi508"}`
without sign-in; `GET /version` gives the package version. Use `/health`
for the platform's liveness and readiness checks. It shows that the
process serves HTTP, not that Keycloak or Chromium work: the server
fetches Keycloak's discovery document at startup and does not start
without it, and the checklist (section 7) is what shows a run works.

## 5. Connecting from Claude Code

On the user's own machine (Claude's custom connectors on claude.ai and
Claude Desktop connect from Anthropic's cloud and cannot reach VAST unless
NASA admits Anthropic's addresses; plan, question 5):

```bash
claude mcp add --transport http tobi508 https://<app host>/mcp
```

Then, in Claude Code, `/mcp`, choose `tobi508` and authenticate. A browser
opens on this server's consent page ("Allow Access"), then NASA's sign-in,
then returns to Claude Code on a localhost port. The server's tools then
appear (`tobi_run_tt_tests` and the rest). Every call is made as the
person who signed in.

What differs from a local (stdio) server:

- `tobi_read_report` takes a report's text or a `run://` link; a path to a
  file on the user's computer works only on a local server in `DEV_MODE`.
- Reports and evidence come as `run://` links the agent reads through MCP;
  nothing is written to the user's computer unless the agent saves it.
- A run that outlives one call goes on in the server; a server restart
  loses it (section 3).

## 6. Before the first deployment: questions for the VAST admin

From the plan (questions 1 to 3 are answered there):

2. ~~Can VAST pull `ghcr.io/abbybowman/tobi508`?~~ Answered (Abby,
   2026-11-15): yes. The package is public (no pull credential), and the
   image has been pulled from GitHub and installed in a personal VAST
   sandbox.
3. ~~Is a service that drives Chromium acceptable?~~ Answered (Abby,
   2026-11-15): yes. A Chromium container has been run on VAST as a test.
4. Can the app's access tokens include `sub` and the groups claim, and an
   audience mapper for this server?
5. Can Anthropic's outbound IP ranges reach the app, for Claude Desktop
   custom connectors? If not, Claude Code is the demo client.

Not confirmed from the code or VAST's documentation:

6. Does the ingress terminate TLS and send `X-Forwarded-Proto: https`, and
   from which addresses does it reach the pod (`FORWARDED_ALLOW_IPS`)? Does
   it pass the `Host` header through unchanged? Without both, nobody can
   sign in.
7. What is the app's host name (`PUBLIC_BASE_URL`), and can the client's
   redirect URI be `https://<app host>/auth/callback`?
8. Can the pod reach public `.gov` and `.mil` sites on ports 80 and 443?
   Directly, or through a proxy (`UPSTREAM_PROXY`), and does that proxy
   re-sign certificates?
9. Which path survives restarts for `/data`, and how large may it be? A
   run with recordings and screenshots is tens of MB; a page with video
   more.
10. How do secrets reach the pod (a Kubernetes Secret as environment
    variables?), and how is one rotated?
11. Does the platform collect the container's stderr into the consolidated
    audit trail, and how long is it kept?
12. Is exactly one replica guaranteed?
13. What read timeout does the ingress have for a request that streams
    (a tool call holds its response up to `CALL_WAIT_S`, 45 s)?
14. Is `/dev/shm` the default 64 MB? Chromium uses it; a larger one (or the
    host's) avoids crashes on large pages.

## 7. Checklist for the first deployment

1. The Containerfile names the image by commit, and the build pulled it.
2. The server started: its log shows `Uvicorn running on
   http://0.0.0.0:8000` and no `AUTH=oidc:` error.
3. `curl https://<app host>/health` answers `healthy`.
4. `curl -i -X POST https://<app host>/mcp` answers 401 with
   `WWW-Authenticate: Bearer resource_metadata="https://<app host>/.well-known/oauth-protected-resource/mcp"`
   (the host is the public one, https).
5. A person signs in from Claude Code (section 5). A 403 on the consent
   page means `FORWARDED_ALLOW_IPS` or the ingress's `X-Forwarded-Proto`
   (question 6). A 401 after signing in means the token lacks `sub`, the
   group or the audience: look for `authn.no_subject` or `authz.denied` in
   the log.
6. Claude Code runs one page through the server, and saves its report.
7. The audit lines name each caller: one JSON line per tool call,
   resource read and prompt, with `sub`, `who`, `action`, `tool`, the URL
   without its query, `outcome` and `seconds`; no token, answer or page
   text.
8. The second person cannot open the first person's run.
9. After a restart: the run folder is still there, and Claude Code still
   connects without registering again (`FASTMCP_HOME` survived).
10. Then step 12b is done: the [PENDING] markers in
    `docs/hackathon/evaluation.md` and `deck.md` can go, and the plan's
    "Verified and not" says so.
