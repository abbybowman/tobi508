"""Set up a Keycloak realm for the hosted smoke test, and report what its
access tokens carry (roadmap step 12a; docs/how-to/deploy-on-vast.md).

    uv run python scripts/smoke_keycloak.py https://keycloak.example:8443 \
        --redirect https://tobi.example/auth/callback --out kc.json

Against a Keycloak in dev mode (admin/admin unless --admin says otherwise),
it creates one realm with what VAST provisions for an app: a confidential
client (Authorization Code, redirect {PUBLIC_BASE_URL}/auth/callback), a
group named as VAMS names them, and two users in it. Then it answers the
plan's open question 4 for this Keycloak: whether an access token carries
`sub`, the groups claim and the audience the server checks. It reads one
token as the client stands when created (Keycloak's defaults), adds what
was missing (a group membership mapper on GROUP_CLAIM, an audience mapper
for the client), reads another, and fails unless the second has all three.

`--out` writes the settings the server and the smoke test need (realm
discovery URL, client id and secret, group, users and passwords) as JSON.
Every value is made up for a throwaway Keycloak; never point this at a real
realm.
"""

from __future__ import annotations

import argparse
import base64
import json
import secrets
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

REALM = "tobi-smoke"
CLIENT = "tobi508"
GROUP = "VAST--tobi508--smoke"
GROUP_CLAIM = "claim_groups"
USERS = ("alice", "bob")


class Admin:
    """Just enough of Keycloak's admin REST API."""

    def __init__(self, base: str, user: str, password: str, ctx: ssl.SSLContext):
        self.base, self.ctx = base.rstrip("/"), ctx
        tok = self.form(
            "/realms/master/protocol/openid-connect/token",
            {
                "grant_type": "password",
                "client_id": "admin-cli",
                "username": user,
                "password": password,
            },
        )
        self.token = tok["access_token"]

    def _send(self, req: urllib.request.Request):
        try:
            with urllib.request.urlopen(req, context=self.ctx, timeout=30) as r:
                body = r.read().decode()
                return r.status, r.headers, (json.loads(body) if body else None)
        except urllib.error.HTTPError as e:
            raise SystemExit(
                f"{req.get_method()} {req.full_url}: {e.code} {e.read()[:300]!r}"
            ) from None

    def form(self, path: str, data: dict) -> dict:
        req = urllib.request.Request(
            self.base + path, data=urllib.parse.urlencode(data).encode()
        )
        return self._send(req)[2]

    def call(self, method: str, path: str, body=None):
        req = urllib.request.Request(
            self.base + "/admin/realms" + path,
            method=method,
            data=None if body is None else json.dumps(body).encode(),
            headers={
                "authorization": "Bearer " + self.token,
                "content-type": "application/json",
            },
        )
        status, headers, doc = self._send(req)
        return doc if doc is not None else headers.get("location", "")


def claims_of(jwt: str) -> dict:
    payload = jwt.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))


def password_token(base: str, ctx, client_secret: str, user: str, pw: str) -> dict:
    """An access token for `user` through the client, by the password grant
    (switched on only while this script reads tokens). The server never
    sees this token; it is read only to show what Keycloak puts in one."""
    req = urllib.request.Request(
        f"{base}/realms/{REALM}/protocol/openid-connect/token",
        data=urllib.parse.urlencode(
            {
                "grant_type": "password",
                "client_id": CLIENT,
                "client_secret": client_secret,
                "username": user,
                "password": pw,
                "scope": "openid email profile",
            }
        ).encode(),
    )
    with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
        return claims_of(json.loads(r.read())["access_token"])


def what_it_carries(claims: dict) -> dict:
    aud = claims.get("aud")
    auds = [aud] if isinstance(aud, str) else list(aud or [])
    return {
        "sub": bool(claims.get("sub")),
        GROUP_CLAIM: claims.get(GROUP_CLAIM),
        "aud": auds,
        "audience_is_client": CLIENT in auds,
        "name_claims": {
            k: claims[k]
            for k in ("email", "preferred_username", "nasaPrimaryEmail")
            if k in claims
        },
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("keycloak", help="Keycloak's base URL, https://host:port")
    ap.add_argument("--redirect", required=True, help="{PUBLIC_BASE_URL}/auth/callback")
    ap.add_argument("--admin", default="admin:admin", help="user:password")
    ap.add_argument("--cacert", help="CA file for Keycloak's certificate")
    ap.add_argument("--out", help="write the settings as JSON here")
    a = ap.parse_args(argv)

    ctx = ssl.create_default_context(cafile=a.cacert)
    base = a.keycloak.rstrip("/")
    user, _, pw = a.admin.partition(":")
    kc = Admin(base, user, pw, ctx)

    kc.call("POST", "", {"realm": REALM, "enabled": True})
    kc.call(
        "POST",
        f"/{REALM}/clients",
        {
            "clientId": CLIENT,
            "protocol": "openid-connect",
            "publicClient": False,
            "standardFlowEnabled": True,
            "directAccessGrantsEnabled": True,  # off again below
            "redirectUris": [a.redirect],
            "attributes": {"pkce.code.challenge.method": "S256"},
        },
    )
    [client] = kc.call("GET", f"/{REALM}/clients?clientId={CLIENT}")
    cid = client["id"]
    secret = kc.call("GET", f"/{REALM}/clients/{cid}/client-secret")["value"]

    kc.call("POST", f"/{REALM}/groups", {"name": GROUP})
    [group] = [g for g in kc.call("GET", f"/{REALM}/groups") if g["name"] == GROUP]
    passwords = {}
    for name in USERS:
        passwords[name] = secrets.token_urlsafe(12)
        kc.call(
            "POST",
            f"/{REALM}/users",
            {
                "username": name,
                "email": f"{name}@smoke.test",
                "emailVerified": True,
                "firstName": name.title(),
                "lastName": "Smoke",
                "enabled": True,
                "credentials": [
                    {"type": "password", "value": passwords[name], "temporary": False}
                ],
            },
        )
        [u] = kc.call("GET", f"/{REALM}/users?username={name}&exact=true")
        kc.call("PUT", f"/{REALM}/users/{u['id']}/groups/{group['id']}")

    before = what_it_carries(
        password_token(base, ctx, secret, "alice", passwords["alice"])
    )
    print("keycloak defaults:", json.dumps(before))

    # What VAST's realm would need for this server (plan, open question 4).
    kc.call(
        "POST",
        f"/{REALM}/clients/{cid}/protocol-mappers/models",
        {
            "name": "groups",
            "protocol": "openid-connect",
            "protocolMapper": "oidc-group-membership-mapper",
            "config": {
                "claim.name": GROUP_CLAIM,
                "full.path": "false",
                "access.token.claim": "true",
                "id.token.claim": "true",
                "userinfo.token.claim": "true",
            },
        },
    )
    kc.call(
        "POST",
        f"/{REALM}/clients/{cid}/protocol-mappers/models",
        {
            "name": "audience",
            "protocol": "openid-connect",
            "protocolMapper": "oidc-audience-mapper",
            "config": {
                "included.client.audience": CLIENT,
                "access.token.claim": "true",
                "id.token.claim": "false",
            },
        },
    )
    after = what_it_carries(
        password_token(base, ctx, secret, "alice", passwords["alice"])
    )
    print("with the two mappers:", json.dumps(after))

    client["directAccessGrantsEnabled"] = False
    kc.call("PUT", f"/{REALM}/clients/{cid}", client)

    problems = [
        what
        for what, ok in (
            ("sub", after["sub"]),
            (GROUP_CLAIM, GROUP in (after[GROUP_CLAIM] or [])),
            ("aud", after["audience_is_client"]),
        )
        if not ok
    ]
    if problems:
        print("access token still lacks:", ", ".join(problems))
        return 1

    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "OIDC_CONFIG_URL": (
                        f"{base}/realms/{REALM}/.well-known/openid-configuration"
                    ),
                    "OIDC_CLIENT_ID": CLIENT,
                    "OIDC_CLIENT_SECRET": secret,
                    "OIDC_AUDIENCE": CLIENT,
                    "REQUIRED_GROUPS": [GROUP],
                    "GROUP_CLAIM": GROUP_CLAIM,
                    "users": passwords,
                    "defaults": before,
                    "configured": after,
                },
                f,
                indent=1,
            )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
