from __future__ import annotations

import argparse
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path

from deckhand.plugins import (
    PluginConfiguration,
    PluginLock,
    PluginManager,
    load_plugin_configuration,
    load_plugin_lock,
)

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_PLUGINS = {
    "dh-http-status",
    "dh-proxmox",
    "dh-prometheus",
    "dh-tailscale",
}
EXPECTED_MANIFESTS = {"dh-core", *EXTERNAL_PLUGINS}
PLUGIN_ADAPTERS = {
    "dh-http-status": set(),
    "dh-proxmox": {"dh-proxmox.read"},
    "dh-prometheus": {"dh-prometheus.read"},
    "dh-tailscale": {"dh-tailscale.read"},
}
PLUGIN_ACTIONS = {
    "dh-http-status": set(),
    "dh-proxmox": {"proxmox.target.observe"},
    "dh-prometheus": {"prometheus.check.observe"},
    "dh-tailscale": {"tailscale.check.observe"},
}
PLUGIN_STATUS = {
    "dh-http-status": {"automation", "metrics", "network"},
    "dh-proxmox": {"virtualization_cluster"},
    "dh-prometheus": {"monitoring_availability", "critical_alerts", "scrape_targets"},
    "dh-tailscale": {"tailnet_fleet", "stale_devices", "key_expiry"},
}
CORE_ADAPTERS = {"dh-core.fake", "dh-core.disabled"}


def require_equal(description: str, actual: set[str], expected: set[str]) -> None:
    if actual != expected:
        raise AssertionError(
            f"{description} differ: missing={sorted(expected - actual)}, "
            f"unexpected={sorted(actual - expected)}"
        )


def base_documents() -> tuple[PluginConfiguration, PluginLock]:
    return (
        load_plugin_configuration(ROOT / "config/plugins.example.yaml"),
        load_plugin_lock(ROOT / "config/plugins.lock.example.yaml"),
    )


def without_plugin(
    configuration: PluginConfiguration,
    lock: PluginLock,
    plugin_id: str,
) -> tuple[PluginConfiguration, PluginLock]:
    config_document = configuration.model_dump(mode="python")
    del config_document["plugins"][plugin_id]
    lock_document = lock.model_dump(mode="python")
    lock_document["plugins"] = [
        entry for entry in lock_document["plugins"] if entry["id"] != plugin_id
    ]
    return (
        PluginConfiguration.model_validate(config_document),
        PluginLock.model_validate(lock_document),
    )


def disabled_plugin(
    configuration: PluginConfiguration,
    plugin_id: str,
) -> PluginConfiguration:
    document = configuration.model_dump(mode="python")
    document["plugins"][plugin_id]["enabled"] = False
    return PluginConfiguration.model_validate(document)


def assert_loaded(
    configuration: PluginConfiguration,
    lock: PluginLock,
    *,
    omitted: set[str] | None = None,
) -> None:
    omitted = omitted or set()
    loaded = PluginManager().load(configuration, lock, allow_external=True)
    expected_plugins = EXPECTED_MANIFESTS - omitted
    expected_adapters = CORE_ADAPTERS | set().union(
        *(adapters for plugin, adapters in PLUGIN_ADAPTERS.items() if plugin not in omitted)
    )
    expected_actions = set().union(
        *(actions for plugin, actions in PLUGIN_ACTIONS.items() if plugin not in omitted)
    )
    expected_status = set().union(
        *(providers for plugin, providers in PLUGIN_STATUS.items() if plugin not in omitted)
    )
    require_equal(
        "loaded plugins", {manifest.id for manifest in loaded.manifests}, expected_plugins
    )
    require_equal(
        "loaded adapters", {name for name, _adapter in loaded.adapters.items()}, expected_adapters
    )
    require_equal("loaded actions", {action.id for action in loaded.actions}, expected_actions)
    require_equal("status providers", set(loaded.status.providers), expected_status)
    require_equal("resilience guards", set(loaded.resilience), expected_plugins)


def verify_installed_and_disabled() -> None:
    configuration, lock = base_documents()
    assert_loaded(configuration, lock)
    for plugin_id in sorted(EXTERNAL_PLUGINS):
        assert_loaded(disabled_plugin(configuration, plugin_id), lock, omitted={plugin_id})


def verify_removed(plugin_id: str) -> None:
    if plugin_id not in EXTERNAL_PLUGINS:
        raise ValueError(f"unsupported plugin: {plugin_id}")
    try:
        distribution(plugin_id)
    except PackageNotFoundError:
        pass
    else:
        raise AssertionError(f"{plugin_id} is still installed")
    configuration, lock = base_documents()
    reduced_configuration, reduced_lock = without_plugin(configuration, lock, plugin_id)
    assert_loaded(reduced_configuration, reduced_lock, omitted={plugin_id})


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("installed-and-disabled")
    removed = subparsers.add_parser("removed")
    removed.add_argument("plugin", choices=sorted(EXTERNAL_PLUGINS))
    arguments = parser.parse_args()
    if arguments.command == "installed-and-disabled":
        verify_installed_and_disabled()
        print("independent install and disable validation passed")
    else:
        verify_removed(arguments.plugin)
        print(f"independent removal validation passed for {arguments.plugin}")


if __name__ == "__main__":
    main()
