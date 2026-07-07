# Codex Sentaurus Skill

A public-safe Codex skill for operating a user's own licensed Synopsys Sentaurus environment through a **Workbench-first** workflow.

The skill helps Codex inspect Sentaurus Workbench projects, follow node dependencies, submit simulations, monitor node status with low token cost, and diagnose bounded convergence failures. It does **not** replace Sentaurus Workbench and does **not** redistribute Synopsys software, manuals, official examples, material databases, calibration payloads, project results, or generated indexes derived from licensed sources.

## Highlights

### Workbench-first

Workbench remains the source of truth. Project status, `gtree.dat`, `gexec.cmd`, `.sta` files, node dependencies, result directories, scenarios, variables, and generated artifacts stay inside the Workbench project model. Codex acts as an automation assistant instead of bypassing Workbench with hard edits to generated files.

### Low-token monitoring

Long-running simulations are not monitored by repeatedly reading large logs. After a Workbench submission, an external watcher tracks compact `.sta` state, while Codex only checks a small terminal marker. If no terminal state is available, Codex exits without log reading, SSH polling, or analysis.

### Mesh-first convergence repair

For SDevice numerical convergence failures, the first repair path is evidence-driven and mesh-first: inspect the failed `*_des_min.tdr` state and upstream durable SDE source, map the hotspot to geometry and refinement definitions, then adjust local mesh or structure where justified. The skill avoids blindly shrinking `MinStep`, loosening convergence, or adding iteration count without physical or numerical evidence.

### Official-example-guided routing

When syntax, mesh strategy, or solver workflow is uncertain, the skill routes the task toward similar local Sentaurus examples such as trench, IGBT, LDMOS, power diode, HFET/HEMT, SDE, SDevice, SMesh, SVisual, and Workbench workflows. Official source decks are read only from the user's own licensed installation and are not included here.

### Optional GitHub handoff

An optional external GPT handoff flow can use a private GitHub repository as file transport for failed-node diagnostic bundles and complete replacement `.cmd` files. This feature is disabled by default and requires explicit private configuration.

## Included

- `SKILL.md`: sanitized Codex skill instructions.
- `agents/openai.yaml`: Codex skill metadata.
- `scripts/`: helper scripts for Workbench status inspection, `.sta` watching, public-release auditing, and local official-index generation.
- `templates/external_gpt_prompt.md`: optional handoff prompt template.
- `references/`: public-safe references and stubs for locally generated official reference files.
- `TECHNICAL_NOTES.md`: architecture and implementation notes.
- `BILIBILI_TECH_NOTES.md`: Chinese technical notes suitable for a public column or repository post.

## Install

Copy this folder into your Codex skills directory:

```powershell
Copy-Item -Recurse . "$env:USERPROFILE\.codex\skills\sentaurus"
```

Then configure your own environment:

```powershell
$env:SENTAURUS_SSH_USER = "<linux-user>"
$env:SENTAURUS_SSH_HOST = "<vm-or-server-host>"
$env:SENTAURUS_SSH_TARGET = "$env:SENTAURUS_SSH_USER@$env:SENTAURUS_SSH_HOST"
$env:SENTAURUS_STROOT = "/path/to/Sentaurus"
$env:SENTAURUS_TCAD_ROOT = "/path/to/Sentaurus/tcad/<release>"
$env:SENTAURUS_BIN_DIR = "$env:SENTAURUS_STROOT/bin"
$env:SENTAURUS_STDB_ROOT = "/path/to/STDB"
```

Use SSH keys or another local credential manager. Do not commit credentials, private machine paths, generated result payloads, licensed official-source files, or generated official-source indexes.

## Optional external handoff configuration

```powershell
$env:SENTAURUS_GITHUB_HANDOFF_REPO = "<owner>/<private-repo>"
$env:SENTAURUS_GITHUB_HANDOFF_REMOTE = "https://github.com/<owner>/<private-repo>.git"
$env:SENTAURUS_HANDOFF_ARCHIVE = "/path/to/local/handoff/archive"
$env:SENTAURUS_HANDOFF_CHECKOUT = "/path/to/local/handoff/checkout"
```

Keep this handoff repository private if diagnostic bundles may contain local project files, unpublished structures, or proprietary simulation context.

## Rebuilding local indexes

Generated index files are intended for local use only and are ignored by git. After configuring your environment, run:

```powershell
python scripts/build_official_indexes.py --mode all
```

The generated files are written under `references/` and should remain local unless you have independently verified redistribution rights.

## Public release policy

This repository is designed to be public-safe. It excludes:

- Synopsys Sentaurus binaries, licenses, manuals, official examples, and calibration payloads.
- Local Workbench projects, `.tdr`, `.plt`, `.out`, `.sta`, `.log`, `.sav`, and result directories.
- Private VM IPs, hostnames, usernames, local absolute paths, SSH credentials, tokens, and handoff state.
- Generated official JSON/JSONL/TXT indexes derived from a licensed Sentaurus installation.

Run the audit before publishing manual edits:

```powershell
python scripts/audit_public_release.py .
```

## License

This repository is released under the MIT License. The license only applies to the independently authored skill text and helper scripts in this repository. It does not grant rights to Synopsys Sentaurus or any licensed Synopsys content.
