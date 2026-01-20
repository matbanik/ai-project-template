#!/usr/bin/env python3
"""
Template sanity checks.

Keeps the docs honest by verifying that the files they reference exist and that
the repo has the expected structure.
"""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent

    required_paths = [
        repo_root / "AGENTS.md",
        repo_root / "README.md",
        repo_root / "HOWTO.md",
        repo_root / "tools" / "web_search.py",
        repo_root / "tools" / "setup_mcp.py",
        repo_root / "tools" / "sync_rules.py",
        repo_root / "api-keys.sample.json",
        repo_root / "mcp_settings.sample.json",
        repo_root / ".agent" / "workflows",
    ]

    optional_paths = [
        repo_root / "api-keys.local.json",
        repo_root / "LICENSE",
    ]

    errors: list[str] = []
    warnings: list[str] = []

    for path in required_paths:
        if not path.exists():
            errors.append(f"Missing required path: {path.relative_to(repo_root)}")

    for path in optional_paths:
        if not path.exists():
            warnings.append(f"Missing optional path: {path.relative_to(repo_root)}")

    if errors:
        print("[FAIL] Validation errors:")
        for error in errors:
            print(f"- {error}")
    else:
        print("[OK] Required files present.")

    if warnings:
        print("\n[WARN] Optional checks:")
        for warning in warnings:
            print(f"- {warning}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
