#!/usr/bin/env python3
"""Build local Sentaurus reference indexes from a configured licensed install."""

from __future__ import annotations

import argparse
import pathlib
import shlex
import subprocess
import sys

from sentaurus_config import add_connection_args, merge_args, require


REMOTE_HELPER = "/tmp/codex_sentaurus_official_index.py"

OUTPUTS = {
    "applications-paths": "official_paths_applications.txt",
    "training-paths": "official_paths_training.txt",
    "manuals-paths": "official_paths_manuals.txt",
    "calibration-paths": "official_paths_calibration.txt",
    "examples": "official_examples_index.jsonl",
}


def skill_dir() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, encoding="utf-8", errors="replace", check=True, **kwargs)


def upload_helper(host: str, remote_helper: str) -> None:
    local = skill_dir() / "scripts" / "_remote_official_index.py"
    run(["scp", str(local), f"{host}:{remote_helper}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def build_mode(mode: str, refs: pathlib.Path, host: str, tcad_root: str, remote_helper: str) -> int:
    proc = subprocess.run(
        ["ssh", host, f"python3 {shlex.quote(remote_helper)} {mode} --tcad-root {shlex.quote(tcad_root)}"],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        return -1
    out_path = refs / OUTPUTS[mode]
    out_path.write_text(proc.stdout, encoding="utf-8")
    return sum(1 for line in proc.stdout.splitlines() if line.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=[*OUTPUTS.keys(), "all"], default="all")
    parser.add_argument("--remote-helper", default=REMOTE_HELPER)
    add_connection_args(parser)
    args = parser.parse_args()

    config = merge_args(args)
    host = require(config.ssh_host, "SSH host", "SENTAURUS_SSH_HOST")
    tcad_root = require(config.tcad_root, "TCAD root", "SENTAURUS_TCAD_ROOT")

    refs = skill_dir() / "references"
    refs.mkdir(exist_ok=True)
    upload_helper(host, args.remote_helper)

    modes = list(OUTPUTS) if args.mode == "all" else [args.mode]
    failed = False
    for mode in modes:
        count = build_mode(mode, refs, host, tcad_root, args.remote_helper)
        if count < 0:
            failed = True
            continue
        print(f"{OUTPUTS[mode]}: {count} records")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

