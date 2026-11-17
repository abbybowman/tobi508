"""deploy/vast/tobi508.yaml: the settings it sets are ones the server reads
(an unknown name is ignored silently, so a typo would turn a setting off),
and the deployment stays fail-closed and single."""

from __future__ import annotations

from pathlib import Path

import yaml

from tobi508.config import Settings

MANIFEST = Path(__file__).resolve().parents[1] / "deploy" / "vast" / "tobi508.yaml"
# Read by uvicorn, not by Settings.
NOT_SETTINGS = {"FORWARDED_ALLOW_IPS"}


def _docs() -> dict[str, dict]:
    return {d["kind"]: d for d in yaml.safe_load_all(MANIFEST.read_text()) if d}


def test_every_config_key_is_a_setting():
    fields = {name.upper() for name in Settings.model_fields}
    config = _docs()["ConfigMap"]["data"]
    unknown = sorted(set(config) - fields - NOT_SETTINGS)
    assert not unknown, f"not settings the server reads: {unknown}"


def test_sign_in_on_dev_mode_off():
    config = _docs()["ConfigMap"]["data"]
    assert config["AUTH"] == "oidc"
    assert config["DEV_MODE"] == "false"
    assert config["PUBLIC_BASE_URL"].startswith("https://")
    assert config["OIDC_CONFIG_URL"].startswith("https://")


def test_one_replica_one_known_image_secrets_not_inline():
    deployment = _docs()["Deployment"]
    assert deployment["spec"]["replicas"] == 1
    assert deployment["spec"]["strategy"]["type"] == "Recreate"
    (container,) = deployment["spec"]["template"]["spec"]["containers"]
    assert not container["image"].endswith(":latest")
    assert "Secret" not in _docs()
    assert {"secretRef": {"name": "tobi508-secrets"}} in container["envFrom"]
