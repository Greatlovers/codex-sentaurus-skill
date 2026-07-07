# Publication Notes

Generated as a public-safe package from a private live Codex skill.

Excluded by design:

- `state/` and private external-GPT thread mappings.
- `__pycache__/` and compiled Python bytecode.
- Live backup files such as `SKILL.md.codex_backup_*`.
- Generated official `*.json`, `*.jsonl`, and `official_paths_*.txt` indexes.
- Any Sentaurus installation, official manual/example source, license files, project results, `.tdr`, `.plt`, `.out`, `.sta`, `.log`, `.sav`, or Workbench result directories.

Sanitization replaces private host/path/repo defaults with placeholders. Run `scripts/audit_public_release.py .` before publishing after any manual edits.
