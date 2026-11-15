"""Smoke test for a hosted, signed-in server (roadmap step 12a;
docs/how-to/deploy-on-vast.md).

    uv run python scripts/smoke_hosted.py https://<app host> --page <URL> \
        --login browser --audit-file audit.log

It checks, in order, and stops at the first failure (exit 1):

  1. health      GET /health answers.
  2. no token    POST /mcp without a token is 401, and the WWW-Authenticate
                 header links the protected-resource metadata, which names
                 an authorization server.
  3. sign-in     The MCP authorization flow a client such as Claude Code
                 runs (register, authorize with PKCE, this server's consent
                 page, the identity provider's sign-in, callback, token)
                 gives a token, and /mcp accepts it.
  4. run         tobi_run_tt_tests on --page runs to done, through
                 tobi_run_status when it outlives one call; the result
                 carries the disclaimer and a finding for each test asked.
  5. report      The report is read through its run:// link.
  6. second      A second person signs in and can open neither that run's
     person      report nor its job.
  7. audit       The audit lines name the caller: the run's tool call with
                 the first person's subject (and, with --login form, their
                 name), the second person's refused read with another
                 subject, and no token anywhere in the log.

Sign-in, two ways:
  --login form     Fill the identity provider's own username and password
                   form (a Keycloak realm: CI). --user and --second-user are
                   NAME:PASSWORD.
  --login browser  Print a link for a person to open (NASA Launchpad on
                   VAST); this script listens on a localhost port for the
                   redirect, as Claude Code does. Sign the second person in
                   from a private window, or the provider's session signs
                   the first person in again.

Audit lines come from the server's log, which this script cannot reach
through the server: --audit-cmd runs a command that prints it (for example
`docker logs tobi`), --audit-file reads a file of it. --skip-audit leaves
the check out and says so; without one of the three the check fails.

--cacert trusts a private CA (CI's). The page must be on the server's
allowlist; nothing here changes a server setting.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import html.parser
import http.cookiejar
import http.server
import json
import os
import secrets
import ssl
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit

TIMEOUT_S = 60
RUN_TIMEOUT_S = 900


def ok(name: str, detail: str = "") -> None:
    print(f"ok    {name}" + (f": {detail}" if detail else ""), flush=True)


def fail(name: str, detail: str) -> None:
    print(f"FAIL  {name}: {detail}", flush=True)
    sys.exit(1)


# ── HTTP ──────────────────────────────────────────────────────────────────────


class Response:
    def __init__(self, status: int, url: str, headers, body: bytes):
        self.status_code, self.url, self.headers = status, url, headers
        self.text = body.decode("utf-8", "replace")
        self.is_redirect = status in (301, 302, 303, 307, 308) and "location" in headers

    def json(self):
        return json.loads(self.text)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **kw):
        return None


class Http:
    """A browser's part of the flow: cookies kept, redirects not followed
    (the caller follows them, so it sees the callback), standard library
    only. Proxies come from the environment, as for any client."""

    def __init__(self, cacert: str | None):
        ctx = ssl.create_default_context(cafile=cacert)
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ctx),
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
            _NoRedirect,
        )

    def _send(self, method, url, body=None, headers=None) -> Response:
        req = urllib.request.Request(
            url, data=body, method=method, headers=headers or {}
        )
        try:
            with self.opener.open(req, timeout=TIMEOUT_S) as r:
                return Response(r.status, r.url, _lower(r.headers), r.read())
        except urllib.error.HTTPError as e:
            return Response(e.code, url, _lower(e.headers), e.read())

    def get(self, url, headers=None) -> Response:
        return self._send("GET", url, headers=headers)

    def post(self, url, json_body=None, form=None, raw=None, headers=None) -> Response:
        headers = dict(headers or {})
        if json_body is not None:
            raw, headers["content-type"] = json.dumps(json_body), "application/json"
        if form is not None:
            raw = urlencode(form)
            headers["content-type"] = "application/x-www-form-urlencoded"
        return self._send("POST", url, (raw or "").encode(), headers)


def _lower(headers) -> dict:
    return {k.lower(): v for k, v in headers.items()}


def http_client(cacert: str | None) -> Http:
    return Http(cacert)


class _Forms(html.parser.HTMLParser):
    """Every <form> on a page: its action and its inputs' names and values."""

    def __init__(self):
        super().__init__()
        self.forms: list[dict] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form":
            self.forms.append({"action": a.get("action") or "", "fields": {}})
        elif tag in ("input", "button") and self.forms and a.get("name"):
            if tag == "button" and a.get("type", "submit") != "submit":
                return
            # A form's first submit button of each name stands for a click.
            self.forms[-1]["fields"].setdefault(a["name"], a.get("value") or "")


def forms_in(page: str) -> list[dict]:
    p = _Forms()
    p.feed(page)
    return p.forms


# ── Sign-in ───────────────────────────────────────────────────────────────────


def _pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(48)
    digest = hashlib.sha256(verifier.encode()).digest()
    return verifier, base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def _register(h, base: str, redirect_uri: str) -> str:
    r = h.post(
        base + "/register",
        json_body={
            "redirect_uris": [redirect_uri],
            "token_endpoint_auth_method": "none",
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "client_name": "tobi508 smoke test",
        },
    )
    if r.status_code != 201:
        fail("sign-in", f"client registration answered {r.status_code}: {r.text[:200]}")
    return r.json()["client_id"]


def _authorize_url(
    base: str, client_id: str, redirect_uri: str, challenge: str, state: str
) -> str:
    return (
        base
        + "/authorize?"
        + urlencode(
            {
                "response_type": "code",
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "state": state,
                "resource": base + "/mcp",
            }
        )
    )


def _token(
    h, base: str, client_id: str, redirect_uri: str, code: str, verifier: str
) -> str:
    r = h.post(
        base + "/token",
        form={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "code_verifier": verifier,
        },
    )
    if r.status_code != 200:
        fail("sign-in", f"token exchange answered {r.status_code}: {r.text[:200]}")
    return r.json()["access_token"]


def sign_in_form(base: str, cacert: str | None, user: str, password: str) -> str:
    """The flow a browser makes, with the provider's sign-in form filled in.
    The consent page is submitted as a browser submits it (Origin header
    and cookies), so a deployment that refuses a real browser's consent
    fails here too."""
    redirect_uri = "http://localhost:9/callback"  # never contacted
    origin = "{0.scheme}://{0.netloc}".format(urlsplit(base))
    h = http_client(cacert)
    client_id = _register(h, base, redirect_uri)
    verifier, challenge = _pkce()
    state = secrets.token_urlsafe(8)
    url = _authorize_url(base, client_id, redirect_uri, challenge, state)
    r = h.get(url)
    for _ in range(20):
        if r.is_redirect:
            nxt = urljoin(str(r.url), r.headers["location"])
            if nxt.startswith(redirect_uri):
                back = parse_qs(urlsplit(nxt).query)
                if back.get("state") != [state] or "code" not in back:
                    fail("sign-in", f"the callback carried no code: {sorted(back)}")
                return _token(
                    h, base, client_id, redirect_uri, back["code"][0], verifier
                )
            r = h.get(nxt)
            continue
        if r.status_code != 200:
            fail(
                "sign-in",
                f"{urlsplit(str(r.url)).path} answered {r.status_code}: {r.text[:200]}",
            )
        page_forms = forms_in(r.text)
        consent = [f for f in page_forms if "csrf_token" in f["fields"]]
        login = [f for f in page_forms if "password" in f["fields"]]
        if consent:
            fields = {**consent[0]["fields"], "action": "approve"}
            target = urljoin(str(r.url), consent[0]["action"] or str(r.url))
            r = h.post(target, form=fields, headers={"origin": origin})
            if r.status_code == 403:
                fail(
                    "sign-in",
                    "the consent page refused a browser's approval "
                    f"(403 {r.text[:60]!r}); "
                    "behind a TLS proxy the server may see http, not https, and call "
                    "the browser's Origin foreign",
                )
        elif login:
            fields = {**login[0]["fields"], "username": user, "password": password}
            target = urljoin(str(r.url), login[0]["action"])
            r = h.post(target, form=fields)
        else:
            fail(
                "sign-in", f"no consent or sign-in form at {urlsplit(str(r.url)).path}"
            )
    fail("sign-in", "more than 20 steps without reaching the callback")
    raise AssertionError


def sign_in_browser(base: str, cacert: str | None, who: str) -> str:
    """Print the link; a person signs in in their browser; the redirect
    comes back to a localhost port, as it does for Claude Code."""
    got: dict = {}
    done = threading.Event()

    class Back(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            got.update(parse_qs(urlsplit(self.path).query))
            self.send_response(200)
            self.send_header("content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Signed in. You can close this window.")
            done.set()

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), Back)
    redirect_uri = f"http://localhost:{srv.server_address[1]}/callback"
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    h = http_client(cacert)
    client_id = _register(h, base, redirect_uri)
    verifier, challenge = _pkce()
    state = secrets.token_urlsafe(8)
    print(
        f"\nSign in as the {who} person (a private window for the second), "
        "then come back here:\n  "
        + _authorize_url(base, client_id, redirect_uri, challenge, state)
        + "\n",
        flush=True,
    )
    if not done.wait(600):
        fail("sign-in", "no sign-in within 10 minutes")
    srv.shutdown()
    if got.get("state") != [state] or "code" not in got:
        fail(
            "sign-in",
            f"the callback carried no code: {got.get('error') or sorted(got)}",
        )
    return _token(h, base, client_id, redirect_uri, got["code"][0], verifier)


# ── MCP ───────────────────────────────────────────────────────────────────────


def unwrap(content: dict | None) -> dict:
    """A tool whose result is one of several models wraps it in "result"."""
    content = content or {}
    return content.get("result", content)


async def run_page(base: str, token: str, page: str, tests: list[str]) -> dict:
    from fastmcp import Client

    async with Client(base + "/mcp", auth=token, timeout=300) as c:
        names = {t.name for t in await c.list_tools()}
        if "tobi_run_tt_tests" not in names:
            fail("run", f"tobi_run_tt_tests is not offered: {sorted(names)}")
        r = await c.call_tool(
            "tobi_run_tt_tests", {"url": page, "tests": tests}, raise_on_error=False
        )
        if r.is_error:
            fail(
                "run", f"tobi_run_tt_tests refused the page: {r.content[0].text[:300]}"
            )
        data = unwrap(r.structured_content)
        job_id = data.get("job_id")
        end = time.monotonic() + RUN_TIMEOUT_S
        while data.get("status") in ("queued", "running"):
            if time.monotonic() > end:
                fail("run", f"not done after {RUN_TIMEOUT_S} s: {data.get('progress')}")
            r = await c.call_tool("tobi_run_status", {"job_id": data["job_id"]})
            data = unwrap(r.structured_content)
        data["_job_id"] = job_id
        return data


async def read_report(base: str, token: str, uri: str) -> dict:
    from fastmcp import Client

    async with Client(base + "/mcp", auth=token, timeout=120) as c:
        contents = await c.read_resource(uri)
        return json.loads(contents[0].text)


async def second_person_reaches(base: str, token: str, uri: str, job_id: str | None):
    """What the second person reaches of the first person's run: a list of
    what they could open (empty when they could open nothing)."""
    from fastmcp import Client
    from mcp.shared.exceptions import MCPError

    opened = []
    async with Client(base + "/mcp", auth=token, timeout=120) as c:
        await c.list_tools()  # signed in and served, so a refusal below means it
        try:
            contents = await c.read_resource(uri)
            if contents and getattr(contents[0], "text", ""):
                opened.append("the report")
        except MCPError:  # the server's refusal; a network error stops the test
            pass
        if job_id:
            r = await c.call_tool(
                "tobi_run_status", {"job_id": job_id}, raise_on_error=False
            )
            if not r.is_error and unwrap(r.structured_content).get("run_id"):
                opened.append("the job")
    return opened


# ── Audit ─────────────────────────────────────────────────────────────────────


def audit_lines(text: str) -> list[dict]:
    """The JSON audit entries in a log, whatever prefix a log line carries."""
    out = []
    for line in text.splitlines():
        i = line.find('{"ts"')
        if i < 0:
            continue
        try:
            entry = json.loads(line[i:])
        except ValueError:
            continue
        if isinstance(entry, dict) and "action" in entry:
            out.append(entry)
    return out


def read_log(a) -> str:
    if a.audit_file:
        with open(a.audit_file, encoding="utf-8", errors="replace") as f:
            return f.read()
    p = subprocess.run(
        a.audit_cmd, shell=True, capture_output=True, text=True, timeout=60
    )
    return p.stdout + p.stderr


# ── Main ──────────────────────────────────────────────────────────────────────


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Smoke test for a hosted, signed-in tobi508 server.",
        epilog="Checks and options are described at the top of this file.",
    )
    ap.add_argument(
        "base", help="the server's public URL, e.g. https://tobi.example.gov"
    )
    ap.add_argument("--page", required=True, help="a page on the server's allowlist")
    ap.add_argument("--tests", default="4.C", help="comma separated (default 4.C)")
    ap.add_argument("--login", choices=("form", "browser"), default="browser")
    ap.add_argument("--user", help="NAME:PASSWORD (--login form)")
    ap.add_argument("--second-user", help="NAME:PASSWORD (--login form)")
    ap.add_argument("--cacert", help="CA file to trust for the server and the provider")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--audit-cmd", help="a command that prints the server's log")
    g.add_argument("--audit-file", help="a file holding the server's log")
    g.add_argument(
        "--skip-audit", action="store_true", help="leave the audit check out"
    )
    a = ap.parse_args(argv)

    base = a.base.rstrip("/")
    tests = [t.strip() for t in a.tests.split(",") if t.strip()]
    if a.cacert:
        os.environ["SSL_CERT_FILE"] = a.cacert  # the MCP client's httpx reads it
    if a.login == "form" and not (a.user and a.second_user):
        ap.error("--login form needs --user and --second-user")
    started = time.time()
    h = http_client(a.cacert)

    # 1. health
    try:
        r = h.get(base + "/health")
        body = r.json() if r.status_code == 200 else {}
    except Exception as exc:
        fail("health", f"{type(exc).__name__}: {exc}")
    if body.get("status") != "healthy":
        fail("health", f"answered {r.status_code}: {r.text[:200]}")
    ok("health", f"{r.status_code} {body}")

    # 2. no token
    r = h.post(
        base + "/mcp",
        raw="{}",
        headers={
            "content-type": "application/json",
            "accept": "application/json, text/event-stream",
        },
    )
    challenge = r.headers.get("www-authenticate", "")
    if r.status_code != 401 or "resource_metadata=" not in challenge:
        fail("no token", f"answered {r.status_code}, WWW-Authenticate {challenge!r}")
    meta_url = challenge.split('resource_metadata="', 1)[1].split('"', 1)[0]
    if urlsplit(meta_url).netloc != urlsplit(base).netloc:
        fail("no token", f"the metadata link points elsewhere: {meta_url}")
    meta = h.get(meta_url)
    servers = (
        meta.json().get("authorization_servers") if meta.status_code == 200 else None
    )
    if not servers:
        fail(
            "no token",
            f"metadata at {meta_url} answered {meta.status_code}: {meta.text[:200]}",
        )
    ok(
        "no token",
        f"401, metadata {urlsplit(meta_url).path}, authorization server {servers[0]}",
    )

    # 3. sign-in
    def sign_in(which: str, cred: str | None) -> str:
        if a.login == "form":
            name, _, pw = (cred or "").partition(":")
            return sign_in_form(base, a.cacert, name, pw)
        return sign_in_browser(base, a.cacert, which)

    first = sign_in("first", a.user)
    r = h.post(
        base + "/mcp",
        json_body={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "smoke", "version": "0"},
            },
        },
        headers={
            "authorization": "Bearer " + first,
            "accept": "application/json, text/event-stream",
        },
    )
    if r.status_code != 200:
        fail("sign-in", f"/mcp refused the new token: {r.status_code} {r.text[:200]}")
    ok("sign-in", "token issued and accepted by /mcp")

    # 4. run
    data = asyncio.run(run_page(base, first, a.page, tests))
    if data.get("status") != "done":
        fail("run", f"ended as {data.get('status')!r}: {str(data)[:300]}")
    findings = {f["test_id"]: f["outcome"] for f in data.get("findings", [])}
    missing = [t for t in tests if t not in findings]
    if missing or "NOT a certified" not in data.get("disclaimer", ""):
        fail(
            "run",
            f"findings {findings}, missing {missing}, "
            f"disclaimer {data.get('disclaimer')!r}",
        )
    uri = data.get("report_uri", "")
    if not uri.startswith("run://"):
        fail("run", f"report_uri is not a run:// link: {uri!r}")
    via = "through tobi_run_status" if data.get("_job_id") else "in one call"
    ok("run", f"{data['run_id']} done {via}: {findings}")

    # 5. report
    try:
        report = asyncio.run(read_report(base, first, uri))
    except Exception as exc:
        fail(
            "report", f"{uri} could not be read: {type(exc).__name__}: {str(exc)[:200]}"
        )
    v = report.get("versions", {})
    if report.get("certified") is not False or not v.get("browser"):
        fail(
            "report",
            f"unexpected report: certified={report.get('certified')!r}, versions {v}",
        )
    ok(
        "report",
        f"{uri} read: browser {v.get('browser')}, "
        f"frozen pages {report.get('frozen_pages')}",
    )

    # 6. second person
    second = sign_in("second", a.second_user)
    opened = asyncio.run(second_person_reaches(base, second, uri, data.get("_job_id")))
    if opened:
        fail("second person", f"opened the first person's {' and '.join(opened)}")
    asked = "report" + (" and job" if data.get("_job_id") else "")
    ok("second person", f"signed in; could not open the first person's {asked}")

    # 7. audit
    if a.skip_audit:
        print("skip  audit: --skip-audit; the audit lines were not checked", flush=True)
        return 0
    if not (a.audit_cmd or a.audit_file):
        fail(
            "audit",
            "give --audit-cmd or --audit-file (or --skip-audit to leave it out)",
        )
    text = read_log(a)
    if first in text or second in text:
        fail("audit", "a sign-in token appears in the server's log")
    lines = [e for e in audit_lines(text) if e.get("ts", 0) >= started - 5]
    runs = [
        e
        for e in lines
        if e.get("action") == "tool.call"
        and e.get("tool") == "tobi_run_tt_tests"
        and e.get("url") == a.page.split("?", 1)[0]
    ]
    if not runs:
        fail(
            "audit",
            "no audit line for the run's tool call "
            f"({len(lines)} audit lines since start)",
        )
    sub1, who1 = runs[-1].get("sub"), runs[-1].get("who")
    if not sub1 or not who1:
        fail("audit", f"the run's audit line names nobody: {runs[-1]}")
    if a.login == "form":
        name1 = (a.user or "").split(":", 1)[0].lower()
        if name1 not in str(who1).lower():
            fail("audit", f"the run's audit line names {who1!r}, not {name1!r}")
    reads = [
        e
        for e in lines
        if e.get("action") == "resource.read"
        and e.get("uri") == uri
        and e.get("sub") != sub1
    ]
    if not reads:
        fail("audit", "no audit line for the second person's read of the run")
    if reads[-1].get("outcome") != "error" or not reads[-1].get("sub"):
        fail("audit", f"the second person's read is logged as {reads[-1]}")
    ok(
        "audit",
        f"run by {who1} ({len(lines)} lines; tool.call ok), "
        f"refused read by {reads[-1].get('who')}; no token in the log",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
