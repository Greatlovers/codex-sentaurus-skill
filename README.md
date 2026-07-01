# Codex Sentaurus Skill

This repository contains a sanitized Codex skill for operating a user's own
licensed Synopsys Sentaurus environment through SSH and Sentaurus Workbench.

The public repository includes only the reusable skill text and helper scripts.
It does not include Synopsys Sentaurus, official manuals, official examples,
material databases, project result payloads, or generated indexes derived from
licensed sources.

## Install

Copy this folder into your Codex skills directory:

```powershell
Copy-Item -Recurse . "$env:USERPROFILE\.codex\skills\sentaurus"
```

Then configure your own environment:

```powershell
$env:SENTAURUS_SSH_HOST = "user@your-sentaurus-host"
$env:SENTAURUS_STDB_ROOT = "/path/to/STDB"
$env:SENTAURUS_TCAD_ROOT = "/path/to/sentaurus/tcad/version"
$env:SENTAURUS_BIN_DIR = "/path/to/sentaurus/bin"
```

Use SSH keys or another local credential manager. Do not commit credentials,
machine-specific paths, generated result payloads, or generated official-source
indexes.

## Included Tools

- `scripts/sentaurus_search.py`: searches generated local index files and can
  optionally run a remote content search against a configured licensed source
  tree.
- `scripts/swb_status_summary.py`: reads compact Workbench node status from
  configured remote projects.
- `scripts/watch_sta.ps1`: external watcher for `.sta` files that reports a
  terminal state without keeping Codex active.
- `scripts/build_official_indexes.py` and `scripts/_remote_official_index.py`:
  optional local index builders for users with access to their own licensed
  Sentaurus installation.
- `scripts/audit_public_release.py`: validates that this public repository has
  not picked up private machine details or excluded artifact types.

## Rebuilding Local Indexes

Generated index files are intended for local use only and are ignored by git.
After configuring your environment, run:

```powershell
python scripts/build_official_indexes.py --mode all
```

The generated files are written under `references/` and should remain local.
They summarize local licensed content for routing and search; they are not part
of this open-source release.

## Safety Policy

- Keep Workbench as the source of truth for project nodes, dependencies, and
  generated state.
- Prefer read-only inspection before edits.
- Back up source decks before changing a project.
- Use external watchers for queued or running simulations.
- Do not redistribute official Sentaurus manuals, examples, material files, or
  generated result payloads.

