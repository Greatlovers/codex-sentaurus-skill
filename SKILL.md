---
name: sentaurus
description: >-
  Use when Codex needs to operate Synopsys Sentaurus through a configurable SSH
  and Workbench-first workflow: inspect STDB projects, preserve Workbench nodes
  and dependencies, look up local licensed documentation or examples, diagnose
  convergence issues, submit runs through Workbench, and monitor node status
  with low-token terminal-state checks.
---

# Sentaurus

Use this skill to help Codex work with a user's own licensed Synopsys Sentaurus
installation. The skill is intentionally configuration-driven. It does not ship
Sentaurus software, official manuals, official examples, material databases, or
generated indexes derived from those sources.

## Required Configuration

Set these values in the local environment, Codex project config, or command-line
arguments before using the scripts:

- `SENTAURUS_SSH_HOST`: SSH target for the machine that can run Sentaurus.
- `SENTAURUS_STDB_ROOT`: remote STDB root.
- `SENTAURUS_TCAD_ROOT`: remote Sentaurus TCAD root that contains
  `Applications_Library`, `manuals`, and related local licensed sources.
- `SENTAURUS_BIN_DIR`: optional directory containing `swb`, `gsub`, `sdevice`,
  `sde`, `snmesh`, `svisual`, `inspect`, `tdx`, and related tools.

Use SSH keys or another local credential manager. Do not place credentials in
this skill, checked-in files, command examples, generated indexes, or reports.

## Workbench-First Rule

Treat Sentaurus Workbench as the project control plane.

- Preserve `gtree.dat`, scenarios, variables, tool nodes, dependencies, node IDs,
  generated results, and GUI-visible project state.
- Edit durable Workbench source decks such as `*_des.cmd`, `sde_dvs.cmd`, or
  visualization scripts. Avoid durable fixes in generated `pp*_des.cmd` files.
- Submit production runs through Workbench, normally `gsub -nodes "<ids>"
  <project>`, then verify `.sta`, `.err`, `.out`, `gsummary.txt`, and output
  artifacts.
- Use direct tool commands only for read-only inspection, syntax checks,
  postprocessing, or isolated experiments. If an experiment produces a real fix,
  apply it to the Workbench source and rerun through Workbench.
- Back up each Workbench source file before editing it.

## Low-Token Monitoring Rule

When this skill submits or resumes a real Workbench simulation, avoid keeping
Codex active just to wait.

1. After submission, do one short confirmation: captured submit log or process
   metadata, relevant `.sta` status, and whether the target node is queued,
   running, done, failed, or aborted.
2. If a node is queued or running, stop Codex-side work and use
   `scripts/watch_sta.ps1` or an equivalent external watcher for terminal-state
   detection.
3. Only inspect logs or update monitoring metadata after a node reaches a
   terminal state.
4. For explicit status requests, use `scripts/swb_status_summary.py` for compact
   JSON and avoid broad project scans.
5. Do not diagnose a node that is merely running.

## Bounded Convergence Repair

Automatic repair is limited to numerical convergence classes such as initial
solve failure, step-size below minimum, or repeated Newton iteration-limit
failure.

Before editing, inspect the decisive error region, `CNormPrint`, and available
minimal-state or NewtonPlot evidence. Change one repair class per cycle:
official-example-guided mesh alignment, initial-state staging, sweep-path
adjustment, or solver settings. Require explicit user approval before changing
geometry, dimensions, doping, materials, contacts, physical models, electrode
resistance, thermal boundaries, circuit topology, target bias, or simulation
endpoints.

## Official-Source Routing

Only use local official sources that the user is licensed to access. Generated
reference indexes are optional local artifacts and are ignored by this public
repository.

- Use `scripts/sentaurus_search.py <query>` for generated local path indexes
  when they exist.
- Use `scripts/sentaurus_search.py <query> --content` only when path indexes are
  insufficient and the configured SSH target can access the licensed source
  tree.
- For solver or convergence changes, start from the closest local official
  example and local failure evidence.
- For SDevice, SDE, mesh, visualization, and postprocessing edits, inspect the
  relevant local deck or manual page before changing a user project.
- Do not paste long manual passages or official source files into skill files,
  reports, issues, or pull requests.

## STDB Project Exploration

For an established Workbench project, start read-only and stay scoped to the
requested project:

```powershell
python scripts/swb_status_summary.py --project "<remote-project-path>" --nodes 1,2
python scripts/sentaurus_search.py "NewtonPlot convergence"
```

Use `gtree.dat` and `gexec.cmd` to map flow, variables, scenarios, and node IDs.
Avoid broad full-project scans during monitoring; inspect only the in-scope
nodes.

