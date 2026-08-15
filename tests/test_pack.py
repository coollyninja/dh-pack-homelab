from pathlib import Path

import yaml

from scripts.validate_pack import validate_pack


def test_pack_is_internally_consistent() -> None:
    validate_pack()


def test_pack_composes_only_read_only_plugins() -> None:
    config = yaml.safe_load(Path("config/plugins.example.yaml").read_text(encoding="utf-8"))
    assert set(config["plugins"]) == {"dh-core", "dh-http-status", "dh-proxmox"}
    assert config["plugins"]["dh-proxmox"]["config"]["targets"] == {
        "virtualization_cluster": {"kind": "cluster", "stale_after_seconds": 30}
    }
