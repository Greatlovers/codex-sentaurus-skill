#!/usr/bin/env python3
"""Audit the public repository for private machine details and excluded files."""

from __future__ import annotations

import argparse
import fnmatch
import pathlib
import subprocess
import sys


def joined(*parts: str) -> str:
    return "".join(parts)


BLOCKED_CONTENT = [
    ".".join(["192", "168", "136", "130"]),
    joined("d", "@"),
    joined("/home", "/d"),
    joined("/usr", "/synopsys"),
    joined("Yuehang", "Wang"),
    joined("yuehang", "wang860"),
    joined("gho", "_"),
    joined("github", "_pat", "_"),
    joined("pass", "word"),
    joined("sec", "ret"),
    " ".join(["BEGIN", "OPENSSH", "PRIVATE", "KEY"]),
]

BLOCKED_PATH_GLOBS = [
    "*/__pycache__/*",
    "*.pyc",
    "*.tdr",
    "*.sav",
    "*.par",
    "*.log",
    "*.job",
    "references/official_*.json",
    "references/official_*.jsonl",
    "references/official_*.txt",
    "backup_codex_*",
]

TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".ps1",
    ".yaml",
    ".yml",
    ".txt",
    ".toml",
    ".json",
    ".gitignore",
    "",
}


def iter_files(root: pathlib.Path) -> list[pathlib.Path]:
    if (root / ".git").exists():
        proc = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=root,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode == 0:
            return [root / line for line in proc.stdout.splitlines() if line.strip()]

    files: list[pathlib.Path] = []
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        if "__pycache__" in path.parts:
            continue
        if path.is_file():
            files.append(path)
    return files


def path_matches(rel: str) -> bool:
    normalized = rel.replace("\\", "/")
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in BLOCKED_PATH_GLOBS)


def scan_text(path: pathlib.Path) -> list[str]:
    suffix = path.suffix.lower()
    if suffix not in TEXT_SUFFIXES and path.name != ".gitignore":
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for idx, token in enumerate(BLOCKED_CONTENT, 1):
        if token in text:
            hits.append(f"blocked-content-{idx}")
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    failures: list[str] = []
    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        if path_matches(rel):
            failures.append(f"excluded file path: {rel}")
        for hit in scan_text(path):
            failures.append(f"{hit}: {rel}")

    if failures:
        print("Public release audit failed:", file=sys.stderr)
        for item in failures:
            print(f"- {item}", file=sys.stderr)
        return 1
    print("Public release audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
