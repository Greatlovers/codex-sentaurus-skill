#!/usr/bin/env python3
"""Emit compact JSON status for Sentaurus Workbench nodes."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shlex
import subprocess
from datetime import datetime, timezone

from sentaurus_config import add_connection_args, merge_args, require


def parse_nodes(value: str) -> list[str]:
    return [item.strip().lstrip("n") for item in value.split(",") if item.strip()]


def status_from_sta(text: str) -> str:
    for line in text.splitlines():
        if "|" not in line:
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) >= 3 and parts[2]:
            return parts[2].lower()
    lowered = text.lower()
    for word in ["queued", "running", "done", "failed", "aborted"]:
        if re.search(rf"\b{word}\b", lowered):
            return word
    return "unknown"


def read_remote_file(host: str, project: str, relpath: str) -> str:
    remote = f"cd {shlex.quote(project)} && cat {shlex.quote(relpath)} 2>/dev/null || true"
    proc = subprocess.run(
        ["ssh", host, remote],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=None, help="Remote Workbench project path.")
    parser.add_argument("--nodes", default="", help="Comma-separated node IDs, for example 1,2,12.")
    parser.add_argument("--include-tail", action="store_true", help="Include short .out and .err tails.")
    add_connection_args(parser)
    args = parser.parse_args()

    config = merge_args(args)
    host = require(config.ssh_host, "SSH host", "SENTAURUS_SSH_HOST")
    project = require(args.project, "remote project path", "no environment fallback")
    nodes = parse_nodes(args.nodes)
    if not nodes:
        raise SystemExit("Missing --nodes.")

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": project,
        "nodes": [],
    }
    for node in nodes:
        sta_name = f"n{node}_des.sta"
        sta_text = read_remote_file(host, project, sta_name)
        item = {
            "node": node,
            "sta_file": sta_name,
            "status": status_from_sta(sta_text),
        }
        if args.include_tail:
            for suffix in ["out", "err"]:
                text = read_remote_file(host, project, f"n{node}_des.{suffix}")
                item[f"{suffix}_tail"] = "\n".join(text.splitlines()[-20:])
        result["nodes"].append(item)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

