#!/usr/bin/env python3
"""
Sync AI rules from AGENTS.md and .agent/ to IDE-native formats.

Usage:
    python sync_rules.py              # Detect and sync to all found IDEs
    python sync_rules.py --dry-run    # Preview changes without applying
    python sync_rules.py --ide cursor # Sync to specific IDE only
    python sync_rules.py --list       # List detected IDEs
"""

import argparse
import os
import shutil
from pathlib import Path
from datetime import datetime


# IDE configurations: name -> (detection_markers, target_paths, is_directory)
IDE_CONFIGS = {
    "cursor": {
        "markers": [".cursor/", ".cursorrules"],
        "targets": [".cursorrules"],  # Legacy format for broad compatibility
        "alt_targets": [".cursor/rules/project.mdc"],  # Modern format
        "is_dir": False,
    },
    "windsurf": {
        "markers": [".windsurf/"],
        "targets": [".windsurf/rules/project.md"],
        "is_dir": True,
    },
    "cline": {
        "markers": [".clinerules", ".clinerules/"],
        "targets": [".clinerules"],
        "is_dir": False,
    },
    "claude_code": {
        "markers": [".claude/", "CLAUDE.md"],
        "targets": ["CLAUDE.md"],
        "is_dir": False,
    },
    "copilot": {
        "markers": [".github/copilot-instructions.md"],
        "targets": [".github/copilot-instructions.md"],
        "is_dir": True,
    },
    "intellij": {
        "markers": [".idea/", ".aiassistant/"],
        "targets": [".aiassistant/rules/project.md"],
        "is_dir": True,
    },
    "zed": {
        "markers": [".zed/", ".rules"],
        "targets": [".rules"],
        "is_dir": False,
    },
    "warp": {
        "markers": ["WARP.md"],
        "targets": ["WARP.md"],
        "is_dir": False,
    },
    "kiro": {
        "markers": [".kiro/"],
        "targets": [".kiro/steering/project.md"],
        "is_dir": True,
    },
    "trae": {
        "markers": ["project_rules.md"],
        "targets": ["project_rules.md"],
        "is_dir": False,
    },
    "void": {
        "markers": [".voidrules"],
        "targets": [".voidrules"],
        "is_dir": False,
    },
    "gemini": {
        "markers": ["GEMINI.md", ".gemini/"],
        "targets": ["GEMINI.md"],
        "is_dir": False,
    },
}


def find_project_root() -> Path:
    """Find project root by looking for .git or AGENTS.md."""
    current = Path.cwd()

    for parent in [current] + list(current.parents):
        if (parent / ".git").exists() or (parent / "AGENTS.md").exists():
            return parent

    return current


def detect_ides(project_root: Path) -> list[str]:
    """Detect which IDEs are configured in the project."""
    detected = []

    for ide_name, config in IDE_CONFIGS.items():
        for marker in config["markers"]:
            marker_path = project_root / marker
            if marker_path.exists():
                detected.append(ide_name)
                break

    return detected


def load_source_content(project_root: Path) -> str:
    """Load and combine source content from AGENTS.md and .agent/."""
    content_parts = []

    # Load AGENTS.md
    agents_file = project_root / "AGENTS.md"
    if agents_file.exists():
        content_parts.append(f"# Project AI Guidelines\n\n")
        content_parts.append(agents_file.read_text(encoding="utf-8"))

    # Add sync metadata
    content_parts.append(f"\n\n---\n\n")
    content_parts.append(f"<!-- Auto-synced from AGENTS.md on {datetime.now().isoformat()} -->\n")
    content_parts.append(f"<!-- Source: {project_root / 'AGENTS.md'} -->\n")

    return "".join(content_parts)


def get_file_mtime(path: Path) -> datetime:
    """Get file modification time."""
    if path.exists():
        return datetime.fromtimestamp(path.stat().st_mtime)
    return datetime.min


def check_sync_status(project_root: Path) -> dict:
    """
    Check if AGENTS.md and synced rule files are in sync.

    Returns dict with status info for each IDE.
    """
    agents_file = project_root / "AGENTS.md"
    agents_mtime = get_file_mtime(agents_file)

    status = {
        "source": {
            "file": agents_file,
            "mtime": agents_mtime,
            "exists": agents_file.exists()
        },
        "targets": {}
    }

    for ide_name, config in IDE_CONFIGS.items():
        target_path = project_root / config["targets"][0]
        target_mtime = get_file_mtime(target_path)

        if not target_path.exists():
            sync_status = "missing"
        elif target_mtime < agents_mtime:
            sync_status = "outdated"  # Target is older than source
        elif target_mtime > agents_mtime:
            sync_status = "newer"  # Target was modified after source (potential manual edits)
        else:
            sync_status = "synced"

        status["targets"][ide_name] = {
            "file": target_path,
            "mtime": target_mtime if target_path.exists() else None,
            "exists": target_path.exists(),
            "status": sync_status
        }

    return status


def print_sync_status(project_root: Path):
    """Print sync status between AGENTS.md and IDE rule files."""
    status = check_sync_status(project_root)

    print("\n" + "=" * 60)
    print("📊 Sync Status Check")
    print("=" * 60)

    # Source info
    source = status["source"]
    if source["exists"]:
        print(f"\n📄 Source: AGENTS.md")
        print(f"   Modified: {source['mtime'].strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n❌ Source: AGENTS.md (NOT FOUND)")
        return

    # Target status
    print(f"\n📋 IDE Rule Files:\n")

    has_issues = False
    for ide_name, info in status["targets"].items():
        if not info["exists"]:
            continue  # Skip non-existent files (not synced yet)

        if info["status"] == "synced":
            icon = "✓"
            msg = "In sync"
        elif info["status"] == "outdated":
            icon = "⚠️"
            msg = "OUTDATED - Run sync to update"
            has_issues = True
        elif info["status"] == "newer":
            icon = "🔄"
            msg = f"NEWER than source - Manual edits detected!"
            has_issues = True
        else:
            icon = "?"
            msg = info["status"]

        target_time = info['mtime'].strftime('%Y-%m-%d %H:%M:%S') if info['mtime'] else "N/A"
        print(f"   {icon} {ide_name:15s} ({target_time}) - {msg}")

    # Recommendations
    if has_issues:
        print("\n" + "-" * 60)
        print("💡 Recommendations:\n")

        for ide_name, info in status["targets"].items():
            if info["status"] == "outdated":
                print(f"   • Run: python tools/sync_rules.py --ide {ide_name}")
            elif info["status"] == "newer":
                print(f"   • {ide_name}: Rule file was edited manually.")
                print(f"     → If changes should be kept: Update AGENTS.md first")
                print(f"     → If changes should be discarded: Run sync to overwrite")
                print(f"     → Run: python tools/sync_rules.py --ide {ide_name}")

        print("\n   To sync all: python tools/sync_rules.py --all")
    else:
        print("\n✅ All synced rule files are up to date!")


def sync_to_ide(
    ide_name: str,
    content: str,
    project_root: Path,
    dry_run: bool = False
) -> tuple[bool, str]:
    """Sync content to a specific IDE's rule format."""
    config = IDE_CONFIGS.get(ide_name)
    if not config:
        return False, f"Unknown IDE: {ide_name}"

    target_path = project_root / config["targets"][0]

    # Create parent directories if needed
    if config.get("is_dir") and not dry_run:
        target_path.parent.mkdir(parents=True, exist_ok=True)

    if dry_run:
        return True, f"Would write {len(content)} chars to {target_path}"

    # Backup existing file if it exists
    if target_path.exists():
        backup_path = target_path.with_suffix(target_path.suffix + ".bak")
        shutil.copy2(target_path, backup_path)

    # Write new content
    if config.get("is_dir"):
        target_path.parent.mkdir(parents=True, exist_ok=True)

    target_path.write_text(content, encoding="utf-8")
    return True, f"Synced to {target_path}"


def main():
    parser = argparse.ArgumentParser(
        description="Sync AI rules from AGENTS.md to IDE-native formats"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview changes without applying"
    )
    parser.add_argument(
        "--ide", "-i",
        type=str,
        help="Target specific IDE (cursor, windsurf, cline, etc.)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List detected IDEs and exit"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Sync to ALL supported IDEs (not just detected ones)"
    )
    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="Check sync status between AGENTS.md and IDE rule files"
    )

    args = parser.parse_args()

    project_root = find_project_root()
    print(f"Project root: {project_root}")

    # Check for AGENTS.md
    if not (project_root / "AGENTS.md").exists():
        print("Error: AGENTS.md not found in project root")
        print("Create AGENTS.md first, or run from project directory")
        return 1

    detected = detect_ides(project_root)

    if args.list:
        print(f"\nDetected IDEs: {', '.join(detected) if detected else 'None'}")
        print(f"\nSupported IDEs: {', '.join(IDE_CONFIGS.keys())}")
        return 0

    if args.status:
        print_sync_status(project_root)
        return 0

    # Determine which IDEs to sync
    if args.ide:
        target_ides = [args.ide]
    elif args.all:
        target_ides = list(IDE_CONFIGS.keys())
    else:
        target_ides = detected if detected else []

    if not target_ides:
        print("\nNo IDEs detected. Use --all to sync to all supported formats,")
        print("or --ide <name> to target a specific IDE.")
        print(f"\nSupported: {', '.join(IDE_CONFIGS.keys())}")
        return 0

    # Load source content
    content = load_source_content(project_root)
    print(f"\nSource content: {len(content)} characters")

    # Sync to each target
    print(f"\n{'DRY RUN - ' if args.dry_run else ''}Syncing to: {', '.join(target_ides)}\n")

    for ide_name in target_ides:
        success, message = sync_to_ide(ide_name, content, project_root, args.dry_run)
        status = "✓" if success else "✗"
        print(f"  {status} {ide_name}: {message}")

    if not args.dry_run:
        print("\nSync complete! Backup files created with .bak extension.")

    return 0


if __name__ == "__main__":
    exit(main())
