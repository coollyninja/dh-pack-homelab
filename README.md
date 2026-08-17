# dh-pack-homelab

`dh-pack-homelab` is a topology-neutral Deckhand solution pack. It composes `dh-http-status`, `dh-proxmox`, `dh-prometheus`, and `dh-tailscale` into a useful ten-key observability profile while keeping actual endpoints, identities, queries, devices, resource IDs, and allowlists outside the public artifact.

This repository is deliberately declarative. It does not contain integration code or grant mutation authority. Copy the examples into a private `deckhand-site-<site>` repository, replace `.invalid` placeholders and example target bindings there, and deliver secrets by file-backed credential mechanisms.

## Contents

- `pack.yaml`: pack identity, compatibility, and referenced artifacts.
- `config/`: example plugin activation and exact lock.
- `profiles/`: logical Stream Deck control composition.
- `policy/`: deny-by-default example inventory with no mutation targets.
- `schema/` and `scripts/`: local and CI validation.
- `tests/ecosystem-requirements.txt`: immutable public source pins used only by lifecycle tests.

The hosted ecosystem test creates a fresh environment from those pins, loads every plugin together, disables each external plugin independently while leaving it installed and locked, then creates one clean environment per plugin, uninstalls it, removes it from configuration and lock, and proves the remaining system still starts. It never calls an upstream service.

## Verify

```bash
uv sync --locked --all-groups
uv run ruff check .
uv run ruff format --check .
uv run python scripts/validate_pack.py
uv run python scripts/check_public_surface.py
uv run pytest
```

The pack is MIT licensed.
