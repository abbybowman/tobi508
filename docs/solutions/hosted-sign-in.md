# Hosted sign-in: what a real provider and a real proxy showed

Found while building the hosted smoke test (roadmap step 12a,
2026-11-15). The deployment steps are in
[how-to/deploy-on-vast.md](../how-to/deploy-on-vast.md).

## A logger with no handler drops INFO, and caplog hides it

**Problem.** Every audit line (`access.audit`, INFO on `tobi508.audit`)
was lost in a running server. Nothing gave that logger a handler, so its
records fell to Python's last-resort handler, which prints WARNING and
above only. The tests passed because pytest's `caplog` collects records
at the root, whatever the server would have printed.

**What we do.** `access.send_audit_to_stderr` gives the logger its own
stderr handler at startup with sign-in, and `tests/test_access.py` reads
stderr (`capsys`), not records. Any logger whose lines must reach the
platform needs a test of what is printed, not of what is logged.

## Behind TLS termination the server sees http

**Problem.** Behind a proxy that terminates TLS, uvicorn's request scheme
is `http` unless it trusts the proxy's `X-Forwarded-Proto`, and by default
it trusts only `127.0.0.1,::1` (`FORWARDED_ALLOW_IPS`). FastMCP's Origin
check compares the browser's `Origin` (`https://host`) with the request's
own origin (`http://host:80`) and refuses the consent page's POST with 403
Forbidden Origin, so nobody can sign in. The stand-in sign-in test missed
it: it runs plain http with the consent page off.

**What we do.** Deployment sets `FORWARDED_ALLOW_IPS` to the proxy's
address and the proxy sends `X-Forwarded-Proto: https`; the Origin check
stays on. `scripts/smoke_hosted_ci.sh` checks both ways in CI. The smoke
test submits the consent form with the Origin header a browser sends, so
it fails where a browser would.

## What Keycloak puts in an access token

Keycloak 26.8.2 gives `sub` (its `basic` scope), `email` and
`preferred_username`, no groups claim, and `aud: ["account"]`. The group
gate needs a Group Membership mapper (claim `claim_groups`, full path off)
and `OIDC_AUDIENCE` an Audience mapper for the client's ID.
`scripts/smoke_keycloak.py` prints the token's contents before and after.

## A page inside CI with DEV_MODE off

The egress proxy refuses private addresses unless `DEV_MODE` is on, so a
page served inside a CI job never reaches a server under test that keeps
it off. A recorder container with `DEV_MODE` on records it once
(`scripts/smoke_record_page.py`), and the server replays the recording
(`FROZEN_PAGES_MODE=replay`). Live egress is then not tested; that needs a
real public page.
