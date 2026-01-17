#!/usr/bin/env python3
"""
MCP Server Setup Guide - Detect IDE and provide setup instructions.

Usage:
    python setup_mcp.py              # Auto-detect IDE and show instructions
    python setup_mcp.py --ide cursor # Show instructions for specific IDE
    python setup_mcp.py --list       # List supported IDEs
    python setup_mcp.py --check      # Check if MCP servers are installed
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path


# IDE detection and configuration paths
IDE_MCP_CONFIGS = {
    "cursor": {
        "name": "Cursor",
        "process_names": ["Cursor.exe", "Cursor"],
        "env_markers": ["CURSOR_"],
        "config_paths": {
            "Windows": Path.home() / ".cursor" / "mcp.json",
            "Darwin": Path.home() / ".cursor" / "mcp.json",
            "Linux": Path.home() / ".cursor" / "mcp.json",
        },
        "instructions": """
## Cursor MCP Setup

1. Open Cursor Settings (Ctrl/Cmd + ,)
2. Search for "MCP" or navigate to Features > MCP Servers
3. Click "Edit in mcp.json" or create the file at:
   {config_path}

4. Paste the following configuration:

```json
{config_json}
```

5. Restart Cursor to load the MCP servers
""",
    },
    "vscode-cline": {
        "name": "VS Code with Cline",
        "process_names": ["Code.exe", "code", "Code - Insiders"],
        "env_markers": ["VSCODE_"],
        "config_paths": {
            "Windows": Path.home() / "AppData" / "Roaming" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json",
            "Darwin": Path.home() / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json",
            "Linux": Path.home() / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json",
        },
        "instructions": """
## VS Code + Cline MCP Setup

### Option A: Use Cline's MCP Settings UI (Recommended)

1. Open VS Code
2. Click the Cline icon in the sidebar (or Ctrl/Cmd + Shift + P → "Cline: Open Settings")
3. Navigate to the "MCP Servers" tab
4. Click "Add Server" for each server below and configure:

**Pomera Server:**
- Command: `pomera`
- Args: `--mcp-server`

**Text Editor Server:**
- Command: `uvx`
- Args: `mcp-text-editor`

**Sequential Thinking Server:**
- Command: `npx`
- Args: `-y`, `@modelcontextprotocol/server-sequential-thinking`

### Option B: Edit Configuration File Directly

1. Create/edit the file at:
   {config_path}

2. Paste the following configuration:

```json
{config_json}
```

3. Restart VS Code or reload the Cline extension
""",
    },
    "windsurf": {
        "name": "Windsurf",
        "process_names": ["Windsurf.exe", "windsurf"],
        "env_markers": ["WINDSURF_"],
        "config_paths": {
            "Windows": Path.home() / ".windsurf" / "mcp.json",
            "Darwin": Path.home() / ".windsurf" / "mcp.json",
            "Linux": Path.home() / ".windsurf" / "mcp.json",
        },
        "instructions": """
## Windsurf MCP Setup

1. Open Windsurf Settings
2. Navigate to AI Features > MCP Configuration
3. Click "Edit Configuration" or create the file at:
   {config_path}

4. Paste the following configuration:

```json
{config_json}
```

5. Restart Windsurf to load the MCP servers
""",
    },
    "claude-desktop": {
        "name": "Claude Desktop",
        "process_names": ["Claude.exe", "Claude"],
        "env_markers": [],
        "config_paths": {
            "Windows": Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json",
            "Darwin": Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
            "Linux": Path.home() / ".config" / "Claude" / "claude_desktop_config.json",
        },
        "instructions": """
## Claude Desktop MCP Setup

1. Open Claude Desktop
2. Go to Settings (gear icon) > Developer > Edit Config
3. Or manually edit the file at:
   {config_path}

4. Paste the following configuration:

```json
{config_json}
```

5. Restart Claude Desktop to load the MCP servers
""",
    },
    "zed": {
        "name": "Zed",
        "process_names": ["Zed.exe", "zed"],
        "env_markers": ["ZED_"],
        "config_paths": {
            "Windows": Path.home() / ".config" / "zed" / "settings.json",
            "Darwin": Path.home() / ".config" / "zed" / "settings.json",
            "Linux": Path.home() / ".config" / "zed" / "settings.json",
        },
        "instructions": """
## Zed MCP Setup

1. Open Zed Settings (Cmd + ,)
2. Edit settings.json and add the MCP configuration under "assistant":
3. Config file location:
   {config_path}

4. Add this to your settings.json under the "assistant" key:

```json
{{
  "assistant": {{
    "mcp_servers": {config_json_inner}
  }}
}}
```

5. Restart Zed to load the MCP servers
""",
    },
}


def find_project_root() -> Path:
    """Find project root by looking for mcp_settings.json or .git."""
    current = Path.cwd()

    for parent in [current] + list(current.parents):
        if (parent / "mcp_settings.json").exists():
            return parent
        if (parent / ".git").exists():
            return parent

    return current


def load_mcp_settings(project_root: Path) -> dict:
    """Load MCP settings from project configuration."""
    settings_file = project_root / "mcp_settings.json"

    if not settings_file.exists():
        return {}

    with open(settings_file, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_running_ide() -> list[str]:
    """Detect which IDEs are currently running."""
    detected = []
    system = platform.system()

    try:
        if system == "Windows":
            # Use tasklist on Windows
            result = subprocess.run(
                ["tasklist", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                timeout=10
            )
            running_processes = result.stdout.lower()
        else:
            # Use ps on Unix-like systems
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=10
            )
            running_processes = result.stdout.lower()

        for ide_key, config in IDE_MCP_CONFIGS.items():
            for process_name in config["process_names"]:
                if process_name.lower() in running_processes:
                    detected.append(ide_key)
                    break

    except Exception as e:
        print(f"Warning: Could not detect running processes: {e}")

    # Also check environment variables
    env_vars = " ".join(os.environ.keys())
    for ide_key, config in IDE_MCP_CONFIGS.items():
        if ide_key in detected:
            continue
        for marker in config.get("env_markers", []):
            if marker in env_vars:
                detected.append(ide_key)
                break

    return detected


def check_mcp_tools_installed() -> dict:
    """Check if MCP server tools are installed."""
    tools = {
        "pomera": {
            "check_cmd": ["pomera", "--version"],
            "installed": False,
            "install": "npm install -g pomera-ai-commander",
        },
        "uvx": {
            "check_cmd": ["uvx", "--version"],
            "installed": False,
            "install": "pip install uv",
        },
        "npx": {
            "check_cmd": ["npx", "--version"],
            "installed": False,
            "install": "npm install -g npm (comes with Node.js)",
        },
    }

    for tool_name, tool_info in tools.items():
        try:
            result = subprocess.run(
                tool_info["check_cmd"],
                capture_output=True,
                timeout=10
            )
            tool_info["installed"] = result.returncode == 0
        except FileNotFoundError:
            tool_info["installed"] = False
        except Exception:
            # Try which/where as fallback
            try:
                cmd = "where" if platform.system() == "Windows" else "which"
                result = subprocess.run(
                    [cmd, tool_name],
                    capture_output=True,
                    timeout=5
                )
                tool_info["installed"] = result.returncode == 0
            except Exception:
                tool_info["installed"] = False

    return tools


def format_config_for_ide(mcp_settings: dict, ide_key: str) -> str:
    """Format MCP settings for a specific IDE's configuration format."""
    servers = mcp_settings.get("mcpServers", {})

    # Most IDEs use this format
    config = {"mcpServers": {}}

    for server_name, server_config in servers.items():
        # Remove internal fields
        clean_config = {
            k: v for k, v in server_config.items()
            if not k.startswith("_")
        }
        config["mcpServers"][server_name] = clean_config

    return json.dumps(config, indent=2)


def show_setup_instructions(ide_key: str, mcp_settings: dict):
    """Show setup instructions for a specific IDE."""
    if ide_key not in IDE_MCP_CONFIGS:
        print(f"Error: Unknown IDE '{ide_key}'")
        print(f"Supported IDEs: {', '.join(IDE_MCP_CONFIGS.keys())}")
        return

    config = IDE_MCP_CONFIGS[ide_key]
    system = platform.system()
    config_path = config["config_paths"].get(system, "~/.config/mcp.json")

    # Format the configuration JSON
    config_json = format_config_for_ide(mcp_settings, ide_key)

    # For Zed, we need the inner mcpServers object only
    servers_only = mcp_settings.get("mcpServers", {})
    clean_servers = {}
    for name, srv in servers_only.items():
        clean_servers[name] = {k: v for k, v in srv.items() if not k.startswith("_")}
    config_json_inner = json.dumps(clean_servers, indent=4)

    # Print header
    print("\n" + "=" * 60)
    print(f"🔧 MCP Setup for {config['name']}")
    print("=" * 60)

    # Print prerequisites
    print("\n## Prerequisites\n")
    print("Before configuring your IDE, install the required tools:\n")

    tools = check_mcp_tools_installed()
    all_installed = True

    for tool_name, tool_info in tools.items():
        status = "✓" if tool_info["installed"] else "✗"
        print(f"  {status} {tool_name}: ", end="")
        if tool_info["installed"]:
            print("Installed")
        else:
            print(f"NOT FOUND - Run: {tool_info['install']}")
            all_installed = False

    if not all_installed:
        print("\n⚠️  Some tools are missing. Install them before proceeding.\n")

    # Print IDE-specific instructions
    instructions = config["instructions"].format(
        config_path=config_path,
        config_json=config_json,
        config_json_inner=config_json_inner,
    )
    print(instructions)

    # Print config file location
    print(f"\n📁 Configuration file: {config_path}")

    if config_path.exists():
        print("   ⚠️  File exists - back it up before modifying!")
    else:
        print("   📝 File does not exist - it will be created")


def main():
    parser = argparse.ArgumentParser(
        description="MCP Server Setup Guide - Detect IDE and provide instructions"
    )
    parser.add_argument(
        "--ide", "-i",
        type=str,
        help="Target specific IDE (cursor, vscode-cline, windsurf, etc.)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List supported IDEs"
    )
    parser.add_argument(
        "--check", "-c",
        action="store_true",
        help="Check if MCP tools are installed"
    )
    parser.add_argument(
        "--detect", "-d",
        action="store_true",
        help="Detect running IDEs"
    )

    args = parser.parse_args()

    # Find project root and load settings
    project_root = find_project_root()
    mcp_settings = load_mcp_settings(project_root)

    if not mcp_settings:
        print("Error: mcp_settings.json not found in project root")
        print(f"Looked in: {project_root}")
        return 1

    if args.list:
        print("\n📋 Supported IDEs:\n")
        for key, config in IDE_MCP_CONFIGS.items():
            print(f"  • {key:15s} - {config['name']}")
        print(f"\nUsage: python setup_mcp.py --ide <name>")
        return 0

    if args.check:
        print("\n🔍 Checking MCP tool installation:\n")
        tools = check_mcp_tools_installed()

        for tool_name, tool_info in tools.items():
            status = "✓" if tool_info["installed"] else "✗"
            print(f"  {status} {tool_name}")
            if not tool_info["installed"]:
                print(f"     Install: {tool_info['install']}")
        return 0

    if args.detect:
        print("\n🔍 Detecting running IDEs...\n")
        detected = detect_running_ide()

        if detected:
            print(f"Found: {', '.join(detected)}")
        else:
            print("No supported IDEs detected running.")
        return 0

    # Determine which IDE to show instructions for
    if args.ide:
        target_ide = args.ide
    else:
        # Auto-detect
        detected = detect_running_ide()

        if not detected:
            print("\n🔍 No IDE detected automatically.\n")
            print("Please specify an IDE with --ide <name>\n")
            print("Supported IDEs:")
            for key, config in IDE_MCP_CONFIGS.items():
                print(f"  • {key:15s} - {config['name']}")
            return 1

        if len(detected) > 1:
            print(f"\n🔍 Multiple IDEs detected: {', '.join(detected)}")
            print(f"Using first detected: {detected[0]}\n")

        target_ide = detected[0]

    show_setup_instructions(target_ide, mcp_settings)
    return 0


if __name__ == "__main__":
    exit(main())
