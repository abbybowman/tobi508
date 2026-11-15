#!/usr/bin/env bash
# The hosted smoke test against a built image and a real Keycloak, as CI runs
# it (.github/workflows/container.yml) and as anyone with Docker can:
#
#   scripts/smoke_hosted_ci.sh tobi508:test
#
# On one Docker network, with names the runner maps to 127.0.0.1:
#   keycloak.smoke.test  Keycloak in dev mode, over HTTPS (a throwaway CA);
#                        scripts/smoke_keycloak.py makes the realm, client,
#                        group and two users, and reports token contents.
#   page.tobi508-smoke.gov  nginx serving tests/fixtures/no_trap.html.
#   tobi                 the image under test: AUTH=oidc, DEV_MODE off, the
#                        default allowlist; the page replayed from a
#                        recording (FROZEN_PAGES_MODE=replay), made first by
#                        a separate recorder container with DEV_MODE on
#                        (scripts/smoke_record_page.py says why).
#   tobi.smoke.test      nginx terminating TLS in front of tobi, as VAST's
#                        ingress does, sending X-Forwarded-Proto; the server
#                        trusts it from that address only (FORWARDED_ALLOW_IPS).
# Then scripts/smoke_hosted.py signs alice and bob in through Keycloak's own
# form, and one more run shows what happens when the server does not trust
# the proxy's headers: its Origin check refuses the consent page.
#
# Needs: docker, curl, openssl, python3, uv; writes /etc/hosts (sudo on a
# runner). Leaves nothing running unless KEEP=1.
set -euo pipefail

IMAGE=${1:?usage: smoke_hosted_ci.sh IMAGE}
KEYCLOAK=quay.io/keycloak/keycloak:26.8.2@sha256:c68e286cacd87b942ac1939a0a1481461109d6acd3a57dc496969a319a76bbf0
NGINX=nginx:1.27.4-alpine@sha256:4ff102c5d78d254a6f0da062b3cf39eaf07f01eec0927fd21e219d0af8bc0591
NET=tobi-smoke
SUBNET=172.30.0.0/24
IP_KC=172.30.0.2 IP_PROXY=172.30.0.3 IP_TOBI=172.30.0.4 IP_PAGE=172.30.0.10
PAGE=http://page.tobi508-smoke.gov/
BASE=https://tobi.smoke.test
ROOT=$(cd "$(dirname "$0")/.." && pwd)
WORK=$(mktemp -d)
chmod 755 "$WORK"

cleanup() {  # keeps the script's own exit status: a cleanup error never decides it
  rc=$?
  if [ "${KEEP:-0}" != 1 ]; then
    docker rm -f tobi-kc tobi-page tobi-proxy tobi >/dev/null 2>&1 || true
    docker network rm "$NET" >/dev/null 2>&1 || true
    # The recorder wrote the frozen page as the image's uid 1000.
    rm -rf "$WORK" 2>/dev/null || sudo rm -rf "$WORK" || true
  fi
  exit "$rc"
}
trap cleanup EXIT

step() { echo "::group::$*" 2>/dev/null || true; echo "== $*"; }
end() { echo "::endgroup::" 2>/dev/null || true; }

step "certificates (a throwaway CA)"
mkdir -p "$WORK/certs" "$WORK/frozen" "$WORK/page"
cd "$WORK/certs"
# Extensions a strict verifier needs (Python 3.13+ sets VERIFY_X509_STRICT:
# the CA needs keyUsage, the server certificate its key identifiers).
openssl req -x509 -newkey rsa:2048 -nodes -days 1 -subj "/CN=tobi508 smoke CA" \
  -addext "basicConstraints=critical,CA:TRUE" \
  -addext "keyUsage=critical,keyCertSign,cRLSign" \
  -addext "subjectKeyIdentifier=hash" \
  -keyout ca.key -out ca.crt 2>/dev/null
openssl req -newkey rsa:2048 -nodes -subj "/CN=smoke.test" \
  -keyout server.key -out server.csr 2>/dev/null
cat > ext <<'EXT'
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid
subjectAltName=DNS:keycloak.smoke.test,DNS:tobi.smoke.test
EXT
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -days 1 -extfile ext -out server.crt 2>/dev/null
chmod 644 ./*
cd "$ROOT"
grep -q "tobi.smoke.test" /etc/hosts \
  || echo "127.0.0.1 keycloak.smoke.test tobi.smoke.test" | sudo tee -a /etc/hosts >/dev/null
end

step "network and Keycloak"
docker network create --subnet "$SUBNET" "$NET" >/dev/null
docker run -d --name tobi-kc --network "$NET" --ip "$IP_KC" \
  --network-alias keycloak.smoke.test -p 8443:8443 \
  -v "$WORK/certs:/certs:ro" \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
  "$KEYCLOAK" start-dev --https-port=8443 \
  --https-certificate-file=/certs/server.crt \
  --https-certificate-key-file=/certs/server.key \
  --hostname=https://keycloak.smoke.test:8443 >/dev/null
for _ in $(seq 1 90); do
  curl -sf --cacert "$WORK/certs/ca.crt" -o /dev/null \
    https://keycloak.smoke.test:8443/realms/master/.well-known/openid-configuration && break
  sleep 2
done
python3 scripts/smoke_keycloak.py https://keycloak.smoke.test:8443 \
  --redirect "$BASE/auth/callback" --cacert "$WORK/certs/ca.crt" --out "$WORK/kc.json" \
  || { docker logs tobi-kc | tail -50; exit 1; }
end

step "the page, recorded once (recorder: DEV_MODE on; server under test: off)"
cp tests/fixtures/no_trap.html "$WORK/page/index.html"
chmod 644 "$WORK/page/index.html"
docker run -d --name tobi-page --network "$NET" --ip "$IP_PAGE" \
  --network-alias page.tobi508-smoke.gov \
  -v "$WORK/page:/usr/share/nginx/html:ro" "$NGINX" >/dev/null
chmod 777 "$WORK/frozen"
docker run --rm --network "$NET" -v "$WORK/frozen:/frozen" \
  -e DEV_MODE=true -e DEV_ALLOWED_ADDRESSES="[\"$IP_PAGE/32\"]" \
  "$IMAGE" uv run --no-sync python scripts/smoke_record_page.py "$PAGE" /frozen
end

server() {  # $1: FORWARDED_ALLOW_IPS for the server (the proxy's address, or none)
  docker rm -f tobi >/dev/null 2>&1 || true
  python3 - "$WORK/kc.json" "$WORK/tobi.env" "$BASE" "$1" <<'EOF'
import json, secrets, sys
kc, out, base, fwd = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3], sys.argv[4]
env = {
    "AUTH": "oidc",
    "PUBLIC_BASE_URL": base,
    "OIDC_CONFIG_URL": kc["OIDC_CONFIG_URL"],
    "OIDC_CLIENT_ID": kc["OIDC_CLIENT_ID"],
    "OIDC_CLIENT_SECRET": kc["OIDC_CLIENT_SECRET"],
    "OIDC_AUDIENCE": kc["OIDC_AUDIENCE"],
    "REQUIRED_GROUPS": json.dumps(kc["REQUIRED_GROUPS"]),
    "GROUP_CLAIM": kc["GROUP_CLAIM"],
    "OIDC_JWT_SIGNING_KEY": secrets.token_urlsafe(32),
    # The page comes from its recording; nothing is fetched live.
    "FROZEN_PAGES_DIR": "/frozen",
    "FROZEN_PAGES_MODE": "replay",
    # The run outlives one call, so tobi_run_status and its owner check run too.
    "CALL_WAIT_S": "1",
    # Python's HTTPS (the discovery document, JWKS, token endpoint) trusts the test CA.
    "SSL_CERT_FILE": "/certs/ca.crt",
    "FORWARDED_ALLOW_IPS": fwd,
}
open(out, "w").write("".join(f"{k}={v}\n" for k, v in env.items()))
EOF
  docker run -d --name tobi --network "$NET" --ip "$IP_TOBI" \
    -v "$WORK/certs:/certs:ro" -v "$WORK/frozen:/frozen:ro" \
    --env-file "$WORK/tobi.env" "$IMAGE" >/dev/null
  for _ in $(seq 1 60); do
    curl -sf --cacert "$WORK/certs/ca.crt" -o /dev/null "$BASE/health" && return 0
    sleep 1
  done
  docker logs tobi | tail -50
  return 1
}

step "TLS in front of the server, as an ingress"
cat > "$WORK/proxy.conf" <<EOF
server {
  listen 443 ssl;
  server_name tobi.smoke.test;
  ssl_certificate /certs/server.crt;
  ssl_certificate_key /certs/server.key;
  location / {
    proxy_pass http://$IP_TOBI:8000;
    proxy_http_version 1.1;
    proxy_set_header Host \$host;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_buffering off;
    proxy_read_timeout 600s;
  }
}
EOF
chmod 644 "$WORK/proxy.conf"
docker run -d --name tobi-proxy --network "$NET" --ip "$IP_PROXY" -p 443:443 \
  -v "$WORK/certs:/certs:ro" -v "$WORK/proxy.conf:/etc/nginx/conf.d/default.conf:ro" \
  "$NGINX" >/dev/null
end

step "smoke test: the server trusts the proxy's headers"
server "$IP_PROXY"
docker exec tobi sh -c 'echo "DEV_MODE=${DEV_MODE:-unset}"'
users=$(python3 -c "import json,sys; u=json.load(open(sys.argv[1]))['users']; print('alice:'+u['alice'], 'bob:'+u['bob'])" "$WORK/kc.json")
read -r ALICE BOB <<<"$users"
uv run --frozen python scripts/smoke_hosted.py "$BASE" --page "$PAGE" \
  --login form --user "$ALICE" --second-user "$BOB" \
  --cacert "$WORK/certs/ca.crt" --audit-cmd "docker logs tobi" \
  || { docker logs tobi 2>&1 | tail -80; exit 1; }
end

step "without FORWARDED_ALLOW_IPS the Origin check refuses the consent page"
server ""
set +e
out=$(uv run --frozen python scripts/smoke_hosted.py "$BASE" --page "$PAGE" \
  --login form --user "$ALICE" --second-user "$BOB" \
  --cacert "$WORK/certs/ca.crt" --skip-audit 2>&1)
set -e
echo "$out"
echo "$out" | grep -q "FAIL  sign-in: the consent page refused" \
  || { echo "expected the consent page to be refused"; exit 1; }
end
echo "hosted smoke test passed"
