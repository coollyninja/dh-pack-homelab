import re
from pathlib import Path

import yaml

from scripts.validate_pack import validate_pack


def test_pack_is_internally_consistent() -> None:
    validate_pack()


def test_pack_composes_only_read_only_plugins() -> None:
    config = yaml.safe_load(Path("config/plugins.example.yaml").read_text(encoding="utf-8"))
    assert set(config["plugins"]) == {
        "dh-core",
        "dh-http-status",
        "dh-proxmox",
        "dh-prometheus",
        "dh-tailscale",
    }
    assert config["plugins"]["dh-proxmox"]["config"]["targets"] == {
        "virtualization_cluster": {"kind": "cluster", "stale_after_seconds": 30}
    }
    prometheus = config["plugins"]["dh-prometheus"]
    assert set(prometheus["config"]["checks"]) == {
        "monitoring_availability",
        "critical_alerts",
        "scrape_targets",
    }
    assert prometheus["runtime"]["max_concurrency"] == 4
    tailscale = config["plugins"]["dh-tailscale"]
    assert set(tailscale["config"]["checks"]) == {
        "tailnet_fleet",
        "stale_devices",
        "key_expiry",
    }
    assert "endpoint" not in tailscale["config"]


def test_profile_contains_ten_unique_logical_controls() -> None:
    profile = yaml.safe_load(
        Path("profiles/homelab-observability.yaml").read_text(encoding="utf-8")
    )
    assert len(profile["controls"]) == 10
    assert len({control["position"] for control in profile["controls"]}) == 10
    assert len({control["domain"] for control in profile["controls"]}) == 10


def test_ecosystem_requirements_use_immutable_public_commits() -> None:
    requirements = Path("tests/ecosystem-requirements.txt").read_text(encoding="utf-8").splitlines()
    assert len(requirements) == 5
    assert {line.split(" @ ", 1)[0] for line in requirements} == {
        "deckhand-control-plane",
        "dh-http-status",
        "dh-proxmox",
        "dh-prometheus",
        "dh-tailscale",
    }
    assert all(
        re.fullmatch(
            r"[a-z0-9-]+ @ git\+https://github\.com/coollyninja/[a-z0-9-]+\.git@[a-f0-9]{40}",
            line,
        )
        for line in requirements
    )
