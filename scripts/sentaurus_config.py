#!/usr/bin/env python3
"""Shared configuration helpers for the public Sentaurus Codex skill."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SentaurusConfig:
    ssh_host: str | None
    stdb_root: str | None
    tcad_root: str | None
    bin_dir: str | None


def from_env() -> SentaurusConfig:
    return SentaurusConfig(
        ssh_host=os.getenv("SENTAURUS_SSH_HOST") or None,
        stdb_root=os.getenv("SENTAURUS_STDB_ROOT") or None,
        tcad_root=os.getenv("SENTAURUS_TCAD_ROOT") or None,
        bin_dir=os.getenv("SENTAURUS_BIN_DIR") or None,
    )


def add_connection_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--host", default=None, help="SSH target; defaults to SENTAURUS_SSH_HOST.")
    parser.add_argument("--stdb-root", default=None, help="Remote STDB root; defaults to SENTAURUS_STDB_ROOT.")
    parser.add_argument("--tcad-root", default=None, help="Remote TCAD root; defaults to SENTAURUS_TCAD_ROOT.")
    parser.add_argument("--bin-dir", default=None, help="Remote Sentaurus bin dir; defaults to SENTAURUS_BIN_DIR.")


def merge_args(args: argparse.Namespace) -> SentaurusConfig:
    env = from_env()
    return SentaurusConfig(
        ssh_host=args.host or env.ssh_host,
        stdb_root=args.stdb_root or env.stdb_root,
        tcad_root=args.tcad_root or env.tcad_root,
        bin_dir=args.bin_dir or env.bin_dir,
    )


def require(value: str | None, label: str, env_name: str) -> str:
    if value:
        return value
    raise SystemExit(f"Missing {label}. Pass the option or set {env_name}.")


def remote_join(*parts: str) -> str:
    cleaned = [part.strip("/") for part in parts if part]
    if not cleaned:
        return ""
    prefix = "/" if parts[0].startswith("/") else ""
    return prefix + "/".join(cleaned)

