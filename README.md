# dh-pack-homelab

`dh-pack-homelab` is a topology-neutral Deckhand solution pack. It composes `dh-http-status` into a useful three-key observability profile while keeping actual endpoints, identities, devices, and allowlists outside the public artifact.

This repository is deliberately declarative. It does not contain integration code or grant mutation authority. Copy the examples into a private `deckhand-site-<site>` repository, replace `.invalid` placeholders there, and deliver secrets by file-backed credential mechanisms.

## Contents

- `pack.yaml`: pack identity, compatibility, and referenced artifacts.
- `config/`: example plugin activation and exact lock.
- `profiles/`: logical Stream Deck control composition.
- `policy/`: deny-by-default example inventory with no mutation targets.
- `schema/` and `scripts/`: local and CI validation.

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
