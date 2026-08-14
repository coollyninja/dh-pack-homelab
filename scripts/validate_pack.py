from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path) -> dict[str, Any]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a mapping")
    return document


def resolve_inside(path_text: str) -> Path:
    resolved = (ROOT / path_text).resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError(f"pack path escapes repository: {path_text}")
    if not resolved.is_file():
        raise ValueError(f"pack path does not exist: {path_text}")
    return resolved


def validate_pack() -> None:
    pack = load_yaml(ROOT / "pack.yaml")
    schema = json.loads((ROOT / "schema/pack.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(pack)

    for profile in pack["profiles"]:
        load_yaml(resolve_inside(profile["path"]))
    for path_text in pack["configuration"].values():
        resolve_inside(path_text)

    config = load_yaml(resolve_inside(pack["configuration"]["plugin_config"]))
    lock = load_yaml(resolve_inside(pack["configuration"]["plugin_lock"]))
    enabled = {name for name, activation in config["plugins"].items() if activation["enabled"]}
    locked = {entry["id"]: entry["version"] for entry in lock["plugins"]}
    required = {entry["plugin"]: entry["version"] for entry in pack["requires"]}
    if not enabled <= locked.keys():
        raise ValueError("every enabled plugin must be present in the example lock")
    if any(locked.get(plugin) != version for plugin, version in required.items()):
        raise ValueError("pack requirements must exactly match the example lock")


if __name__ == "__main__":
    validate_pack()
    print("solution-pack validation passed")
