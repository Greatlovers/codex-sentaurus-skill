#!/usr/bin/env python3
"""Remote-side helper for indexing a user's licensed Sentaurus tree."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def iter_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    result: list[Path] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            result.append(Path(dirpath) / name)
    return sorted(result)


def rel(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def emit_paths(root: Path) -> None:
    for path in iter_files(root):
        print(path)


def emit_examples(root: Path, base: Path) -> None:
    for dirpath, _dirnames, filenames in os.walk(root):
        if "gtree.dat" not in filenames:
            continue
        project = Path(dirpath)
        record = {
            "type": "official_example_project",
            "path": str(project),
            "relpath": rel(project, base),
            "files": sorted(filenames),
        }
        print(json.dumps(record, ensure_ascii=False, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["applications-paths", "training-paths", "manuals-paths", "calibration-paths", "examples"])
    parser.add_argument("--tcad-root", required=True, help="Remote TCAD root.")
    args = parser.parse_args()

    base = Path(args.tcad_root)
    roots = {
        "applications-paths": base / "Applications_Library",
        "training-paths": base / "Sentaurus_Training",
        "manuals-paths": base / "manuals",
        "calibration-paths": base / "Calibration_Library",
        "examples": base / "Applications_Library",
    }
    root = roots[args.mode]
    if args.mode == "examples":
        emit_examples(root, base)
    else:
        emit_paths(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

