# The egress proxy: what the browser and Playwright actually do

`egress.py` gives Chrome one way out, a local proxy that checks every
connection's address. Three things were not obvious.

**Playwright's `route.fetch` uses the browser's launch proxy, and tunnels even
plain `http://` with CONNECT, loopback included.** So the navigation guard's
own top-level fetch is checked too. Playwright also adds `<-loopback>` to
Chrome's proxy bypass list, so loopback pages go through the proxy rather than
around it. (Verified with a logging proxy; `tests/test_egress.py` would show a
hit on the 127.0.0.2 sentinel otherwise.)

**A CONNECT refusal comes back from `route.fetch` as an ordinary 403
response**, not an exception. The guard served it as the page, so a refused or
unreachable page was "tested" as an empty 403. Now the proxy records every
refusal (`policy: True` for an address or port rule, `False` for a failed
connection), and the guard compares the list before and after its fetch:
policy refusals raise `NavigationBlocked`, failed connections raise
`PageUnreachable`. For plain-HTTP refusals the proxy sends no response at all,
because a 403 body would render as the page.

**HAR replay hangs on requests that failed while recording.** The HAR stores
them with status -1, and `route_from_har` waits on them forever (a
`page.goto` timeout of 30 s). This applies to any failed subresource, not only
refused ones. `capture.replay_context` aborts exactly those URLs, as they
failed live.

How we know: `tests/test_egress.py` (removing the proxy from the launch fails 9
tests), `tests/test_leakage.py::test_secrets_stay_out_of_a_load_failure` (found
the 403 case), and the iframe test (found the HAR hang).

## A page blank in its replay: the silent sign-in check (round 3, 2026-11-16)

**What happened.** Round 3's two Data Governance pages (an Angular app on
keycloak-js) replayed as a blank white page while the live page showed
about 125 lines. The app draws nothing until a hidden frame asks the sign-in
server whether the visitor is signed in (`prompt=none`, "check-sso"). That
request carries a `state` value made on each load, so the replay asked an
address the recording never saw, the frame was aborted and the app waited
forever.

**What did not work.** Serving the recorded redirect as it is: its `state`
is the recording's own, keycloak-js rejects the mismatch and still draws
nothing. Answering with a fulfilled 302: Chromium followed the redirect
outside the replay's routes, to the network (a leak in a frozen run).

**What we do now** (`capture._serve_signin_answers`, Abby 2026-11-16).
When the recording holds the check answered "not signed in"
(`error=login_required`), a replay gives a new load the same answer: a
small page that sends the frame to the recorded redirect address, served
from the recording, with only `state` replaced by the request's own. Only
a frame's navigation, only to an address the recording holds; nothing
live. It is the one place a replay makes up part of a response, and each
one is logged (`replay_signin_answer` in steps.jsonl).

**How we know.** `tests/test_replay_signin.py` (the fixture page draws
only when the answer carries its own state; without a recorded answer
nothing is made up). On the real forum page the replay drew 130 lines,
live 123. A page can still draw incompletely when its recording lacks
what the app loads after the check (the home page: 27 lines of about 126,
its recording missing a script, images and data requests): compare a
replay with the live page after freezing.
