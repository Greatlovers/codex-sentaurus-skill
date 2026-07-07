# Technical Notes

## Workbench-first control plane

The skill treats Sentaurus Workbench as authoritative. Durable edits are applied to Workbench source decks and tree metadata, while generated node decks such as `pp*_des.cmd` are treated as outputs. Production reruns go through `gsub -nodes ... <project>` so node dependencies, scenarios, variables, and GUI-visible state remain consistent.

## SSH as transport

SSH is only the transport layer for file inspection, deck edits, status checks, and background submissions. The project model still comes from `gtree.dat`, `gexec.cmd`, node directories, `.sta` status files, and Workbench dependency order.

## Low-token monitoring

Long-running simulations are not polled inside Codex. The skill uses a lightweight STA watcher outside Codex and a heartbeat that checks only a tiny terminal marker. If the marker is absent or stale, the heartbeat exits without SSH, log reading, or analysis.

## Mesh-first convergence repair

For numerical SDevice failures, the default first repair pass is mesh-first. The evidence path is intentionally small: inspect the failed `*_des_min.tdr` state and the upstream durable SDE source, map the hotspot to geometry and refinement definitions, then adjust existing SDE mesh definitions where justified.

## Official-example-guided decisions

The skill routes mesh and solver questions toward the closest local Sentaurus device family. Official examples and manuals are read only from the user's own licensed installation and are not redistributed in this public package.

## Generated references

`official_*` reference files in this public package are stubs. They document expected filenames without republishing generated content from a licensed installation. Use the builder scripts locally to regenerate them when allowed.
