# How to deploy on VAST

For whoever puts the server on VAST (roadmap step 12) and the VAST admin
who answers its questions. Follow it top to bottom; the checklist at the
end is what to confirm on the first deployment.

**Status:** hosted with sign-in at a VAST dev URL (2026-11-18, section
6b): Claude Code signed in through VAST's Keycloak and NASA's sign-in
and ran a live page, and the smoke test passed there. No deployment of
its own yet (section 9). Every value here is taken from the
code (`src/tobi508/config.py`, `app.py`, `access.py`, `routes.py`,
`runlog.py`), the `Dockerfile` and `.env.example`, not from memory. The
sign-in is tested against a stand-in provider (`tests/test_access_signin.py`);
`scripts/smoke_hosted.py` checks a deployed server end to end, and CI runs
it on every image build against a real Keycloak (section 8), and it
passed against VAST's Keycloak and NASA's sign-in at the dev URL with
one person (section 6b). Design and
reasons: [the hosted sign-in plan](../plans/2026-11-06-hosted-auth.md).

Results are agent-assisted, never a certified Trusted Tester result, on
VAST as anywhere else.

## 1. The Containerfile

The image is built by GitHub Actions (`.github/workflows/container.yml`),
not on VAST: VAST hosts run in FIPS mode and apt fails inside its nested
containers ([environment notes](../solutions/environment.md)). Every push
to `main` that changes what goes into the image publishes
`ghcr.io/abbybowman/tobi508:latest` and `ghcr.io/abbybowman/tobi508:<commit
sha>` (the merge commit's). While TOBI is a prototype, VAST runs
`:latest`, so it gets each new build at its next restart (Abby,
2026-11-17; section 9, "Updating"). Pin a commit's tag instead when a
deployment must be one known image:

```dockerfile
FROM ghcr.io/abbybowman/tobi508:latest
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
| `UPSTREAM_PROXY` | unset | Only if the pod's outbound HTTPS passes through a gateway that re-signs certificates with a CA Chromium does not trust: an `http://` proxy URL. The egress proxy checks each address as usual, then tunnels by name through it (weaker against DNS rebinding, since the gateway resolves the name again). Leave unset if pods reach public sites directly, as a VAST sandbox does (question 8). |

### Open questions (the judge)

| Setting | Default | What it does |
| --- | --- | --- |
| `JUDGE_BACKEND` | `auto` | `auto`: `api` when `JUDGE_BASE_URL` and `JUDGE_API_KEY` are both set, else `client` (Abby, 2026-11-18: the server judge answers whenever it has a model). `api`: the server answers the question types in `JUDGE_TYPES` itself. `client`: every open question goes back to the calling agent (in Claude Code, Claude answers it by rubric). Either way a person can override with `tobi_answer_questions`. |
| `JUDGE_ROUTE` | `anthropic-messages` | `anthropic-messages` calls a Messages API gateway; `cli` runs `claude -p`, which is **not in the image**, so never use it on VAST. |
| `JUDGE_BASE_URL`, `JUDGE_API_KEY` (**secret**) | unset | The gateway (without `/v1`) and its key. Both set: the judge is on. With an explicit `api`, the server refuses to start without both. |
| `JUDGE_AUTH_HEADER` | `x-api-key` | The header the key goes in. |
| `JUDGE_MODEL` | `claude-sonnet-5-5` | The gateway's model name. |
| `JUDGE_TYPES` | `all` | Test IDs whose questions the server answers: `all` (every implemented test), a list such as `4.B,5.H`, or empty for none. |
| `JUDGE_CONCURRENCY`, `JUDGE_CALL_TIMEOUT_S`, `JUDGE_CAP_S` | `3`, `300`, `900` | Requests at once, one request's limit, a run's whole judging phase. |
| `JUDGING_MODEL` | `none` | Recorded in every report; with `api`, set from the model and prompt. |

**With no gateway,** leave `JUDGE_BASE_URL` and `JUDGE_API_KEY` unset:
runs work the same, and open questions are answered by the connecting
agent.

### Capacity

| Setting | Default | What it does |
| --- | --- | --- |
| `MAX_CONCURRENT_RUNS` | `2` | Runs using a browser at once; others queue. |
| `CALL_WAIT_S` | `45` | How long one tool call waits before it returns a job id; `tobi_run_status` waits again. Keep it under the ingress's read timeout. |
| `MAX_RUN_S` | `1800` | The longest any run may take. |

The dev container was 4 CPU and 16 GB; a run with `MAX_CONCURRENT_RUNS=2`
can use two Chromiums at once, each with a page and its replays.

### Live log (a demo only)

| Setting | Default | What it does |
| --- | --- | --- |
| `LIVE_LOG` | `false` | Keeps the last 2,000 events in memory (never on disk): every MCP call with its full arguments and response, pictures included, and each run's steps and progress lines. |
| `LIVE_LOG_TOKEN` | unset | The secret that opens the page. Put it in `tobi508-secrets`, not the ConfigMap. Without it the page answers 404. |

Open `https://<app host>/live#token=<LIVE_LOG_TOKEN>` in a browser. The
token is in the address's fragment, which a browser never sends, so it stays
out of the gateway's logs; the page sends it in a header when it asks for
events. The page is not behind sign-in: anyone with the token sees **every
caller's** calls, including page text and answers, which the audit lines
never hold. Turn it on for the demo (ConfigMap `LIVE_LOG: "true"`, the token
in the secret, a restart), then off again (another restart clears it).

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
without it, and the smoke test (section 7) is what shows a run works.

`GET /viewer` serves the pre-SCRT viewer (`demo/prescrt-viewer/viewer.html`,
as built) without sign-in. It holds no data: the person picks a saved
pre-SCRT or SCRT file and it is read in their own browser, and the page
makes no request (its Content-Security-Policy, also sent as a header).

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
   audience mapper for this server? (What it takes in Keycloak: section 8.)
5. ~~Can Anthropic's outbound IP ranges reach the app, for Claude Desktop
   custom connectors?~~ Answered (Abby, 2026-11-18): no. VAST's host names
   exist only in NASA's internal DNS, so a client connecting from
   Anthropic's cloud (claude.ai, Claude Desktop's custom connectors)
   cannot reach them. The client is Claude Code on a NASA machine.

Not confirmed from the code or VAST's documentation:

6. Does the ingress terminate TLS and send `X-Forwarded-Proto: https`, and
   from which addresses does it reach the pod (`FORWARDED_ALLOW_IPS`)? Does
   it pass the `Host` header through unchanged? Without both, nobody can
   sign in. Answered for a dev environment's URL (2026-11-17, section 6a):
   yes, from 10.42.0.0, `Host` unchanged. Confirm for the app's own
   subdomain.
7. What is the app's host name (`PUBLIC_BASE_URL`), and can the client's
   redirect URI be `https://<app host>/auth/callback`?
8. Can the pod reach public `.gov` and `.mil` sites on ports 80 and 443?
   Answered for a personal VAST sandbox (Abby, 2026-11-15): yes, directly,
   with the sites' own certificates; leave `UPSTREAM_PROXY` unset. No proxy
   setting in the shell; `curl -v https://www.section508.gov/` connected
   straight to the site's public address, with or without `--noproxy`,
   and showed Let's Encrypt as issuer. The image (TOBI's egress proxy and
   Chromium, `DEV_MODE` off) recorded that page live: 42 requests, none
   failed, 4.C PASS. Confirm the same from the app's own environment once
   it exists (a re-signing gateway there would show as most requests
   failed; then set `UPSTREAM_PROXY`). From a dev environment, 2026-11-17:
   4.C on that page again, PASS (section 6a).
9. Which path survives restarts for `/data`, and how large may it be? A
   run with recordings and screenshots is tens of MB; a page with video
   more. Answered for a dev environment (a VAST admin, 2026-11-18):
   self-service up to 20 GB of storage and 4 GB of memory, beyond the
   NAMS approval. Its home volume survives restarts unless `vastdev down`
   is run; a Podman named volume lives there (section 6b).
10. How do secrets reach the pod (a Kubernetes Secret as environment
    variables?), and how is one rotated?
11. Does the platform collect the container's stderr into the consolidated
    audit trail, and how long is it kept?
12. Is exactly one replica guaranteed?
13. What read timeout does the ingress have for a request that streams
    (a tool call holds its response up to `CALL_WAIT_S`, 45 s)? At least
    50 s at a dev environment's URL (2026-11-17, section 6a).
14. Is `/dev/shm` the default 64 MB? Chromium uses it; a larger one (or the
    host's) avoids crashes on large pages.

## 6a. What a VAST dev environment showed (2026-11-17)

**How deployment works on VAST** (a VAST admin, 2026-11-17): a developer
can reach only their own dev namespace; there is no per-app namespace
with developer rights, and no process to grant one. An app gets its own
subdomain by configuring the gateway, without a namespace of its own.
The path is: run it in the dev environment, make it work at the dev
environment's URL (`https://<you>-dev.<VAST domain>/`), then write YAML
for the app's resources (its own storage, environment, and Kubernetes
Secrets for keys and tokens) and hand it to the cluster admins. A
separate namespace adds nothing but proof of a documented deployment.

**What ran.** The image (`:latest`) in the dev environment under Podman,
`--network host -e MCP_HOST=127.0.0.1` (way 3 of
[get-started.md](get-started.md)), reached from a laptop through
`ssh -L 8000:127.0.0.1:8000`, Claude Code connected over HTTP: 4.C on
https://www.section508.gov/ came back PASS (93 Tab and 94 Shift+Tab
presses, no open question). The first live run from a VAST dev
environment, by Claude Code through MCP.

**What the dev URL's gateway does,** found with a throwaway server that
echoes each request's headers, not TOBI (TOBI without sign-in stays on
loopback):

| Question | Found |
| --- | --- |
| Port the dev URL reaches | **8000** (`MCP_PORT`'s default). While TOBI listens on 127.0.0.1 only, the URL answers 502, as it should. |
| Does the gateway sign people in? | **No.** Traefik passes requests through with no user header, so TOBI's own sign-in (`AUTH=oidc`) is what protects it. Never serve it on this URL without that. |
| TLS and forwarded headers (question 6) | Traefik ends TLS and sends `X-Forwarded-Proto: https`, `X-Forwarded-Port: 443` and `X-Forwarded-Host`; `Host` arrives unchanged. Requests reach the pod from **10.42.0.0** (the cluster's pod network, not Traefik's own address): `FORWARDED_ALLOW_IPS=10.42.0.0`, or `10.42.0.0/16` if that address moves (uvicorn 0.54 takes ranges; any pod could then claim https, while sign-in is still required). `X-Forwarded-For` is 10.42.0.1, not the caller's address. |
| Read timeout (question 13) | A request held 50 s answered 200 after 50.3 s: `CALL_WAIT_S` (45 s) fits. |
| Settings given to the environment | No port, URL or OIDC variables (`env` names only). |

**The Keycloak client exists (2026-11-18):** the VAST admins minted its
client ID and secret (both kept out of git: the ID in the env file, the
secret only there or in a Kubernetes Secret). Signing in with it took
the realm, the Client ID, the redirect URI and NASA's certificates
right first (section 6b). Its access tokens carry `sub` and a name for
the audit line; whether they carry `claim_groups` and the client's own
audience is not yet checked (section 8).

**What the admins recommend (2026-11-18):**

- **Read VAST's `py_auth_boilerplate`** for setting up sign-in with that
  client. TOBI's sign-in is already built (FastMCP's OIDC proxy,
  `access.py`): the boilerplate signs browsers in with a session cookie,
  while MCP clients send a bearer token on every request, so its code is
  not reused ([the hosted sign-in plan](../plans/2026-11-06-hosted-auth.md)).
  Read it for what VAST's realm expects: the issuer and discovery URL,
  scopes, claim names, the group strings, and the redirect path.
- **Later, a namespace and a pod of TOBI's own,** with its own storage
  volume, from a Kubernetes file; the boilerplate has an example. That is
  section 9's YAML, compared with their example before it is handed over.
- **Mirror the repository on VAST's git (Forgejo),** whose workflows
  could release a new image when `main` moves. Images cannot be built on
  VAST (FIPS mode; apt fails in nested containers:
  [environment notes](../solutions/environment.md)), so a VAST workflow
  would take GitHub's built image (by its commit tag) and update or
  restart the deployment, not build it.

## 6b. Hosting from the dev environment (self-service)

A VAST admin (2026-11-18): every dev container gets
`https://<you>-dev.<VAST domain>`, TLS ended at the gateway; listen for
http on port 8000 inside the dev container. Within 20 GB of storage and
4 GB of memory this needs nothing from the admins beyond the NAMS
approval. (Code can also be pushed to VAST's Forgejo; signing in there
adds the smartcard's SSH key from Active Directory, and `vastdev login`
in a dev container reaches it.) So the dev URL is where TOBI is hosted
for now, and the YAML (section 9) is for a deployment beyond it.

Its settings go in one file only you can read, never in the command line
or git. In the dev container:

```bash
mkdir -p ~/.config/tobi508 && umask 077
cat > ~/.config/tobi508/env <<'END'
# Without sign-in: loopback only, reached through the ssh tunnel.
MCP_HOST=127.0.0.1
# Within the 4 GB: one Chromium at a time until memory is measured.
MAX_CONCURRENT_RUNS=1
# The server's own judge (Luna): with these two it answers every
# test's open questions (section 2 has every setting).
JUDGE_BASE_URL=https://<gateway, without /v1>
JUDGE_API_KEY=<key>
JUDGE_MODEL=<the gateway's name for the model>
# JUDGE_AUTH_HEADER=authorization   # if it wants "Bearer <key>" as the key
END
podman run -d --name tobi --network host --env-file ~/.config/tobi508/env \
  -v tobi-data:/data ghcr.io/abbybowman/tobi508:latest
```

`tobi-data` is a Podman named volume, under the home volume, owned
right for the image's user. To update: `podman pull` the image, then
`podman rm -f tobi` and the same `podman run`.

**Memory.** `podman stats` leaves out file cache, and Podman sets no
limit of its own (it shows the dev container's 16 GiB, not the 4 GB).
The kernel's own figures, from inside the container:

```bash
podman exec tobi cat /sys/fs/cgroup/memory.peak    # highest since start, cache included
podman exec tobi grep -E '^(anon|file) ' /sys/fs/cgroup/memory.stat   # programs, cache now
```

Measured 2026-11-18 (one 4.C run, then every test on
https://www.section508.gov/ with three other pages): the peak with
cache was 4.21 GB; afterwards programs held 259 MB and cache 2.9 GB.
The cache (recordings and browser files) is given back when memory is
short, so a 4 GB limit would shrink it before a run failed; the
programs' own peak during the run was not captured (1.07 GB a minute
in). Keep `MAX_CONCURRENT_RUNS=1` until it is.

### With sign-in, at the dev URL

First signed in on 2026-11-18. Before writing the file, check three
things with the admins or the commands here; each one cost a round trip.

- **Which realm, and which Client ID.** The client may be in VAST's
  shared cluster realm rather than a realm of the app's own (the
  boilerplate assumes one per app). A realm that exists answers its
  discovery URL (`curl -s -o /dev/null -w '%{http_code}\n'
  https://<keycloak host>/realms/<realm>/.well-known/openid-configuration`
  prints 200; a wrong name, or the wrong case, 404). Keycloak gives a
  client two identifiers: a Client ID (a name, which sign-in uses) and an
  internal UUID (admin console only). Given the UUID, Keycloak's sign-in
  page says "Client not found".
- **The redirect URI.** Keycloak sends people back only to the exact
  addresses registered on the client. Ask for
  `https://<you>-dev.<VAST domain>/auth/callback` by its full address,
  not a wildcard (a wildcard such as `https://<you>*` also matches
  addresses that are not yours). A client registered only for the app's
  own subdomain gives "Invalid parameter: redirect_uri"; that subdomain
  answers the gateway's 404 until the gateway routes it.
- **Keycloak's certificate.** VAST's Keycloak (and the dev URL) use
  NASA's internal certificate authority, which the image does not trust:
  with `AUTH=oidc` the server stops at startup with
  `CERTIFICATE_VERIFY_FAILED`. The dev container already trusts it, so
  mount its bundle read-only and point `SSL_CERT_FILE` at it (below).
  The bundle also holds the public authorities, so the judge gateway
  still works. The browser that tests pages keeps its own trust store
  and is not affected. NASA's certificates are never added to the image
  or to git: this repository is public.

Write the file without the secret reaching the screen, shell history or
a chat. The prompts ask for the dev URL (with `https://`), the realm, the
Client ID and the secret (hidden as you type):

```bash
umask 077 && mkdir -p ~/.config/tobi508
read -r -p 'Dev URL (https://...): ' URL; read -r -p 'Realm: ' REALM; read -r -p 'Client ID: ' CID; read -rs -p 'Client secret (hidden): ' CSECRET; echo
cat > ~/.config/tobi508/env <<END
AUTH=oidc
PUBLIC_BASE_URL=$URL
OIDC_CONFIG_URL=https://<keycloak host>/realms/$REALM/.well-known/openid-configuration
OIDC_CLIENT_ID=$CID
OIDC_CLIENT_SECRET=$CSECRET
OIDC_JWT_SIGNING_KEY=$(openssl rand -base64 48)
FORWARDED_ALLOW_IPS=10.42.0.0/16
SSL_CERT_FILE=/etc/ssl/vast-ca.pem
MAX_CONCURRENT_RUNS=1
END
unset CSECRET CID
chmod 600 ~/.config/tobi508/env && cut -d= -f1 ~/.config/tobi508/env
```

The last line lists the setting names only. `PUBLIC_BASE_URL` must start
with `https://`, or the server refuses to start. Add the judge settings
above the same way if there is a gateway. Then start it with the dev
container's certificate bundle mounted:

```bash
podman rm -f tobi; podman run -d --name tobi --network host \
  --env-file ~/.config/tobi508/env \
  -v /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem:/etc/ssl/vast-ca.pem:ro \
  -v tobi-data:/data ghcr.io/abbybowman/tobi508:latest
```

The container reads the file only when it starts: after any change to
it, run both lines again. The image's command listens on `0.0.0.0:8000`,
which the gateway reaches; section 7's checklist applies.

**Left out on purpose until the first sign-in shows the token:**
`OIDC_AUDIENCE` (it refuses every token unless the client has an
audience mapper) and `REQUIRED_GROUPS` (it refuses everyone unless the
client has a group mapper writing `claim_groups`; section 8). Without
the group gate, anyone the realm signs in can use the server, and a
shared realm is every VAST user: set a group before the URL is shared.

**The smoke test runs on your own computer,** not in the dev container
(the repository is there, and so is the browser that signs in). Give it
a file holding NASA's two CA certificates for the dev URL and Keycloak
(`--cacert`, kept outside the repository), and read the audit lines
over ssh:

```bash
uv run python scripts/smoke_hosted.py https://<you>-dev.<VAST domain> --page https://www.section508.gov/ --login browser --cacert <NASA CA file> --audit-cmd "ssh <dev container host> podman logs tobi"
```

It passed on 2026-11-18: health, no token, sign-in, a live 4.C run,
its report, and the audit line naming the person with no token in the
log. With `--login browser` it skips the second person, which needs a
second NASA identity at the same computer; CI's run checks that on every
image build (section 8).

**Found on the way:**

- **Claude Code had to sign in again** after its token was refused: the
  sign-in proxy logged "Refresh token not found ... already rotated,
  expired, or revoked". Not the restart (the store on `tobi-data`
  survived it). Unconfirmed: two Claude Code processes sharing one saved
  sign-in (refresh tokens are single use), or a short token lifetime in
  VAST's realm. If it recurs, checklist item 9 fails.

**Fixed since:** uvicorn's access log kept each request's whole address,
including the one-time code in `/auth/callback?...code=...`. It now keeps
the path and status without the query string (`redact.py`,
`tests/test_leakage.py`).

## 7. Checklist for the first deployment

1. The Containerfile names the image by commit, and the build pulled it.
2. The server started: its log shows `Uvicorn running on
   http://0.0.0.0:8000` and no `AUTH=oidc:` error.
3. `curl https://<app host>/health` answers `healthy`.
4. `curl -i -X POST https://<app host>/mcp` answers 401 with
   `WWW-Authenticate: Bearer resource_metadata="https://<app host>/.well-known/oauth-protected-resource/mcp"`
   (the host is the public one, https).
5. The smoke test passes. One person signs in by hand; save the
   server's log to a file first, or give `--audit-cmd` a command that
   prints it (section 6b has the dev URL's form, with `--cacert`):

   ```bash
   uv run python scripts/smoke_hosted.py https://<app host> --page https://www.section508.gov/ --login browser --audit-file tobi.log
   ```

   It prints one line per check (health, no token, sign-in, run, report,
   second person, audit) and stops at the first failure; with
   `--login browser` the second person is skipped and says so. A 403 at the
   consent page means `FORWARDED_ALLOW_IPS` or the ingress's
   `X-Forwarded-Proto` (question 6). A 401 after signing in means the
   token lacks `sub`, the group or the audience: look for
   `authn.no_subject` or `authz.denied` in the log.
6. Claude Code connects (section 5), runs one page, and saves its report.
7. The audit lines name each caller: one JSON line per tool call,
   resource read and prompt, with `sub`, `who`, `action`, `tool`, the URL
   without its query, `outcome` and `seconds`; no token, answer or page
   text.
8. The second person cannot open the first person's run: checked in CI
   against a real Keycloak with two users (section 8). On VAST it needs
   two people.
9. After a restart: the run folder is still there, and Claude Code still
   connects without registering again (`FASTMCP_HOME` survived).
10. Then step 12b's sign-in is done (2026-11-18 at the dev URL: items 2
    to 5 and 7 passed; 6 ran a page, its saved report not checked; 8 in
    CI; 9 not yet seen to hold).

## 8. What a real Keycloak showed

CI runs the smoke test on every image build
(`.github/workflows/container.yml`, `scripts/smoke_hosted_ci.sh`; anyone
with Docker can run the script): the image under test, signed in through
Keycloak 26.8.2 in dev mode, behind nginx terminating TLS as VAST's
ingress does. `scripts/smoke_keycloak.py` makes what VAST provisions for an
app (a confidential client with redirect `{PUBLIC_BASE_URL}/auth/callback`,
a group named `VAST--tobi508--smoke`, two users in it) and reads an access
token before and after configuring the client.

**How the page is allowed with DEV_MODE off.** The page is served inside
the job, at a private address; the server's egress proxy refuses private
addresses unless `DEV_MODE` is on, and nothing about that is changed. So a
separate recorder container of the same image, with `DEV_MODE` on and that
one address let through, records the page first
(`scripts/smoke_record_page.py`, which records as a live run does). The
server under test keeps `DEV_MODE` off and the default allowlist; its URL
is under `.gov` (`page.tobi508-smoke.gov`, a name that exists only inside
the job) and it replays the recording (`FROZEN_PAGES_DIR`,
`FROZEN_PAGES_MODE=replay`: a URL with no recording is a tool error and
nothing is fetched live). The report records `frozen_pages: replay`. So CI
proves sign-in, a run, the report and ownership, not the server's live
egress: that was checked on a VAST sandbox with a real `.gov` page
(question 8), and is checked again in the app's own environment.

**What an access token carries** (Keycloak 26.8.2, scopes
`openid email profile`):

| Claim | As the client is created | What to configure |
| --- | --- | --- |
| `sub` | present (Keycloak's `basic` client scope) | Nothing, unless the client uses lightweight access tokens or lacks the `basic` scope: then every token is refused (`authn.no_subject` in the log). |
| `claim_groups` | absent | A **Group Membership** mapper on the client: token claim name `claim_groups` (`GROUP_CLAIM`), "Full group path" off, "Add to access token" on. Without it `REQUIRED_GROUPS` refuses everyone (`authz.denied`). |
| `aud` | `["account"]` only | An **Audience** mapper: included client audience = the client's ID, "Add to access token" on; then `OIDC_AUDIENCE` = the client's ID. Without it, setting `OIDC_AUDIENCE` refuses every token. |
| `email`, `preferred_username` | present | Nothing; the audit line's `who` is the first of `nasaPrimaryEmail`, `email`, `preferred_username`, `AgencyUID`. |

VAST's realm may differ (its Launchpad claims, its own mappers); question 4
asks. On VAST, the smoke test's sign-in answers it: a 401 after signing in,
with `authn.no_subject` or `authz.denied` in the log, names what is
missing.

**Behind TLS, the server must know the scheme.** Without
`FORWARDED_ALLOW_IPS` naming the proxy, the consent page's "Allow Access"
gets 403 Forbidden Origin: the server sees `http://<host>`, the browser's
Origin is `https://<host>`, and FastMCP's Origin check (on, and left on)
calls them different. With the proxy's address in `FORWARDED_ALLOW_IPS`
and `X-Forwarded-Proto: https` from the proxy, sign-in works. CI checks
both: the full smoke test with the setting, and the 403 without it.

**The audit lines were not reaching the log** until 2026-11-15 (no
handler on the audit logger); the smoke test found it, and the fix is
tested (`tests/test_access.py`).


## 9. The YAML for the cluster admins

On VAST a developer cannot apply resources outside their own dev
namespace (section 6a), so the deployment is a file the cluster admins
apply: [`deploy/vast/tobi508.yaml`](../../deploy/vast/tobi508.yaml). It
holds a ConfigMap (the settings of section 2), a PersistentVolumeClaim
for `/data` (20 Gi), a Deployment (one replica, `Recreate`, `:latest`
pulled on every start, uid 1000, all capabilities dropped, a 1 Gi `/dev/shm`,
`/health` probes), a Service on port 8000 and an Ingress for the app's
host. Replace every `<...>` first. `tests/test_deploy_manifest.py` checks
that every setting it names is one the server reads (an unknown name is
ignored silently), that sign-in is on and `DEV_MODE` off, that it stays
one replica, and that `:latest` is always pulled (a cached `:latest`
would never update).

**Updating.** Kubernetes pulls `:latest` only when the pod starts: a new
build on `main` does nothing until a restart. Someone with rights in the
namespace (today, a cluster admin) restarts it:

```bash
kubectl -n <namespace> rollout restart deployment/tobi508
```

A restart ends runs in progress (jobs live in memory); run folders on
`/data` stay. The YAML does not change for an update, so a deployment
from git (VAST's Forgejo) would not restart it either. Ways to need no
one, not built yet: a job in the namespace allowed to restart only this
deployment, nightly; or, with a deployment from git, CI writing each
new build's commit into the YAML (pinned and automatic). Reports do not
yet record which image build ran.

**The secrets** are not in the file. Whoever applies it creates them,
from a file only they can read, deleted afterwards (not on the command
line, where shell history keeps them):

```bash
umask 077
cat > tobi508-secrets.env <<'END'
OIDC_CLIENT_SECRET=<the Keycloak client's secret>
OIDC_JWT_SIGNING_KEY=<a long random string, e.g. from: openssl rand -base64 48>
JUDGE_API_KEY=<the judge gateway's key>
END
kubectl create secret generic tobi508-secrets -n <namespace> --from-env-file=tobi508-secrets.env
rm tobi508-secrets.env
kubectl apply -f tobi508.yaml
```

Keep `OIDC_JWT_SIGNING_KEY` the same across updates: a new one makes
every client register and sign in again.

**The server's own judge** (Luna or another Messages API gateway; on for
every test once both are set, section 2). In the ConfigMap:

```yaml
  JUDGE_BACKEND: api                     # explicit: no key, no start
  JUDGE_BASE_URL: https://<gateway>      # without /v1: the server adds /v1/messages
  JUDGE_MODEL: <the gateway's model name>
  # JUDGE_AUTH_HEADER: authorization     # if the gateway wants a bearer token, not x-api-key
```

and `JUDGE_API_KEY=<key>` in the secrets file (with `authorization` as the
header, the key's value is `Bearer <key>`). With `api` set, the server
refuses to start with no URL or key. The gateway must be reachable from the pod.
Locally the same names go in `.env`; with Podman, in a file passed with
`--env-file` (mode 600).

**Verified (2026-11-17):** the manifest's test; the image's smoke test
(`tests/container_smoke.py`, 4.C PASS) under Docker with the manifest's
security settings (`--user 1000:1000 --cap-drop ALL --security-opt
no-new-privileges --shm-size 1g`). **Not verified:** applying it on a
cluster (no access from where it was written, and no schema check run);
whether VAST's gateway takes a standard Ingress; the gateway's reach to
Luna.
