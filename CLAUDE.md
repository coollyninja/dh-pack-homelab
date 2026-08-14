# dh-pack-homelab

Inherit `../CLAUDE.md` and the vault standards. This repository is a declarative, topology-neutral solution pack; it does not contain executable integration code.

- Keep `pack.yaml`, the canonical solution-pack schema, plugin activation, exact lock, profiles, and policy examples mutually consistent.
- Use only logical domains, placeholder identities, and `.invalid` endpoints.
- Never include real topology, targets, credentials, certificate names, or mutation allowlists.
- A pack may request compatible plugins but cannot grant authority; the private site policy remains decisive.
