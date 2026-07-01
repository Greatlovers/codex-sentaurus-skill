#!/usr/bin/env python3
"""Search local generated Sentaurus indexes or a configured remote source tree."""

from __future__ import annotations

import argparse
import pathlib
import shlex
import subprocess
import sys

from sentaurus_config import add_connection_args, merge_args, remote_join, require


INDEX_FILES = {
    "applications": "official_paths_applications.txt",
    "calibration": "official_paths_calibration.txt",
    "training": "official_paths_training.txt",
    "manuals": "official_paths_manuals.txt",
}

ROOTS = {
    "applications": "Applications_Library",
    "calibration": "Calibration_Library",
    "training": "Sentaurus_Training",
    "manuals": "manuals",
}

TEXT_INCLUDES = (
    "*.cmd",
    "*.tcl",
    "*.prf",
    "*.dat",
    "*.txt",
    "*.html",
    "*.htm",
    "*.py",
    "*.md",
)


def skill_dir() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def selected_scopes(scope: str) -> list[str]:
    if scope == "all":
        return ["applications", "training", "manuals", "calibration"]
    return [scope]


def search_index(query: str, scope: str, limit: int) -> int:
    refs = skill_dir() / "references"
    query_lower = query.lower()
    shown = 0
    for name in selected_scopes(scope):
        index_path = refs / INDEX_FILES[name]
        if not index_path.exists():
            continue
        for line in index_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if query_lower in line.lower():
                print(line)
                shown += 1
                if shown >= limit:
                    return shown
    return shown


def remote_grep(query: str, scope: str, limit: int, host: str, tcad_root: str) -> int:
    roots = [remote_join(tcad_root, ROOTS[name]) for name in selected_scopes(scope)]
    include_args = " ".join(f"--include={shlex.quote(pattern)}" for pattern in TEXT_INCLUDES)
    root_args = " ".join(shlex.quote(root) for root in roots)
    remote = (
        f"grep -RInI {include_args} -m 3 -- {shlex.quote(query)} {root_args} 2>/dev/null "
        f"| head -{int(limit)}"
    )
    return subprocess.call(["ssh", host, remote])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", help="Search query.")
    parser.add_argument(
        "--scope",
        choices=["applications", "training", "manuals", "calibration", "all"],
        default="all",
        help="Source group to search.",
    )
    parser.add_argument("--limit", type=int, default=50, help="Maximum results.")
    parser.add_argument("--content", action="store_true", help="Search remote file content via SSH.")
    add_connection_args(parser)
    args = parser.parse_args()

    if not args.query:
        parser.print_help()
        return 0

    config = merge_args(args)
    shown = search_index(args.query, args.scope, args.limit)
    if shown or not args.content:
        return 0

    host = require(config.ssh_host, "SSH host", "SENTAURUS_SSH_HOST")
    tcad_root = require(config.tcad_root, "TCAD root", "SENTAURUS_TCAD_ROOT")
    return remote_grep(args.query, args.scope, args.limit, host, tcad_root)


if __name__ == "__main__":
    raise SystemExit(main())

