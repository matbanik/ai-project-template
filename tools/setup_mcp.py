#!/usr/bin/env python3
"""
MCP Server Setup Guide - Detect IDE and provide setup instructions.

Usage:
    python setup_mcp.py              # Auto-detect IDE and show instructions
    python setup_mcp.py --ide cursor # Show instructions for specific IDE
    python setup_mcp.py --list       # List supported IDEs
    python setup_mcp.py --check      # Check if MCP servers are installed
    python setup_mcp.py --install    # Install missing MCP servers
    python setup_mcp.py --install --force  # Reinstall all MCP servers
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


# Default MCP tools directory
DEFAULT_MCP_TOOLS_DIR = Path.home() / "mcp-tools"

# NPM global modules directory (for pomera)
NPM_GLOBAL_DIR = Path.home() / "AppData" / "Roaming" / "npm" / "node_modules"


# MCP Server definitions with installation instructions
MCP_SERVERS = {
    "pomera": {
        "name": "Pomera AI Commander",
        "type": "npm-global",
        "check_file": None,
        "install_cmd": "npm install -g pomera-ai-commander",
        "check_cmd": ["python", str(NPM_GLOBAL_DIR / "pomera-ai-commander" / "pomera_mcp_server.py"), "--version"],
        "config_template": {
            "command": "python",
            "args": ["{npm_global_dir}/pomera-ai-commander/pomera_mcp_server.py"]
        }
    },
    "sequential-thinking": {
        "name": "Sequential Thinking",
        "type": "npx",
        "check_file": None,
        "install_cmd": None,  # Uses npx -y
        "check_cmd": None,  # npx handles this
        "config": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
        }
    },
    "text-editor": {
        "name": "MCP Text Editor",
        "type": "uvx",
        "check_file": None,
        "install_cmd": "pip install uv",
        "check_cmd": ["uvx", "--version"],
        "config": {
            "command": "uvx",
            "args": ["mcp-text-editor"]
        }
    },
    "backup": {
        "name": "MCP Backup Server",
        "type": "git-node",
        "repo_url": "https://github.com/hexitex/MCP-Backup-Server.git",
        "dir_name": "MCP-Backup-Server",
        "check_file": "dist/index.js",
        "build_cmds": [
            "npm install",
            "npm install zod-to-json-schema@3.23.3 --save",  # Fix TS compatibility
            "npm run build"
        ],
        "config_template": {
            "command": "node",
            "args": ["{mcp_tools_dir}/MCP-Backup-Server/dist/index.js"],
            "env": {
                "BACKUP_DIR": "./.code_backups",
                "EMERGENCY_BACKUP_DIR": "./.code_emergency_backups",
                "MAX_VERSIONS": "50"
            }
        }
    },

    "markdownify": {
        "name": "Markdownify MCP",
        "type": "git-node",
        "repo_url": "https://github.com/zcaceres/markdownify-mcp.git",
        "dir_name": "markdownify-mcp",
        "check_file": "dist/index.js",
        "build_cmds": [
            "pnpm install",
            "pnpm run build"
        ],
        "config_template": {
            "command": "node",
            "args": ["{mcp_tools_dir}/markdownify-mcp/dist/index.js"]
        }
    },
}


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
- Command: `npx`
- Args: `-y`, `pomera-ai-commander`, `--mcp-server`

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
    "antigravity": {
        "name": "Antigravity (Gemini)",
        "process_names": [],
        "env_markers": [],
        "config_paths": {
            "Windows": Path.home() / ".gemini" / "antigravity" / "mcp_config.json",
            "Darwin": Path.home() / ".gemini" / "antigravity" / "mcp_config.json",
            "Linux": Path.home() / ".gemini" / "antigravity" / "mcp_config.json",
        },
        "instructions": """
## Antigravity (Gemini) MCP Setup

1. Edit the configuration file at:
   {config_path}

2. Paste the following configuration:

```json
{config_json}
```

3. Restart Antigravity to load the MCP servers
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


def run_command(cmd: str, cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return result."""
    print(f"  → Running: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    if check and result.returncode != 0:
        print(f"    ✗ Failed: {result.stderr[:200]}")
    return result


def check_server_installed(server_key: str, mcp_tools_dir: Path) -> tuple[bool, str]:
    """Check if a specific MCP server is installed."""
    server = MCP_SERVERS.get(server_key)
    if not server:
        return False, f"Unknown server: {server_key}"

    server_type = server.get("type", "")

    if server_type == "http":
        return True, "HTTP endpoint (no installation needed)"

    if server_type == "npx":
        return True, "Uses npx (auto-downloaded on first use)"

    if server_type == "npm-global":
        check_cmd = server.get("check_cmd")
        if check_cmd:
            try:
                result = subprocess.run(check_cmd, capture_output=True, timeout=10)
                if result.returncode == 0:
                    return True, "Installed (npm global)"
            except Exception:
                pass
        return False, "Not installed"

    if server_type == "uvx":
        try:
            result = subprocess.run(["uvx", "--version"], capture_output=True, timeout=10)
            if result.returncode == 0:
                return True, "Installed (uv/uvx)"
        except FileNotFoundError:
            return False, "uv not installed - run: pip install uv"
        except Exception:
            pass
        return False, "Not installed"

    if server_type in ("git-node", "git-python"):
        dir_name = server.get("dir_name")
        check_file = server.get("check_file")
        if dir_name and check_file:
            full_path = mcp_tools_dir / dir_name / check_file
            if full_path.exists():
                return True, f"Installed at {mcp_tools_dir / dir_name}"
        return False, f"Not found in {mcp_tools_dir}"

    return False, "Unknown installation type"


def install_server(server_key: str, mcp_tools_dir: Path, force: bool = False) -> bool:
    """Install a specific MCP server."""
    server = MCP_SERVERS.get(server_key)
    if not server:
        print(f"  ✗ Unknown server: {server_key}")
        return False

    server_type = server.get("type", "")
    server_name = server.get("name", server_key)

    print(f"\n📦 Installing {server_name}...")

    if server_type in ("http", "npx"):
        print(f"  ✓ No installation needed for {server_type} servers")
        return True

    if server_type == "npm-global":
        install_cmd = server.get("install_cmd")
        if install_cmd:
            result = run_command(install_cmd)
            return result.returncode == 0
        return True

    if server_type == "uvx":
        install_cmd = server.get("install_cmd")
        if install_cmd:
            result = run_command(install_cmd)
            return result.returncode == 0
        return True

    if server_type in ("git-node", "git-python"):
        dir_name = server.get("dir_name")
        repo_url = server.get("repo_url")
        build_cmds = server.get("build_cmds", [])
        check_file = server.get("check_file")

        if not dir_name or not repo_url:
            print(f"  ✗ Missing dir_name or repo_url for {server_key}")
            return False

        server_dir = mcp_tools_dir / dir_name

        # Check if already installed
        if server_dir.exists() and not force:
            if check_file and (server_dir / check_file).exists():
                print(f"  ✓ Already installed at {server_dir}")
                return True
            else:
                print(f"  → Directory exists but build incomplete, rebuilding...")

        # Create mcp-tools dir if needed
        mcp_tools_dir.mkdir(parents=True, exist_ok=True)

        # Clone if needed
        if not server_dir.exists():
            result = run_command(f"git clone {repo_url}", cwd=mcp_tools_dir)
            if result.returncode != 0:
                return False
        elif force:
            print(f"  → Force reinstall: removing and re-cloning...")
            shutil.rmtree(server_dir)
            result = run_command(f"git clone {repo_url}", cwd=mcp_tools_dir)
            if result.returncode != 0:
                return False

        # Run build commands
        for cmd in build_cmds:
            result = run_command(cmd, cwd=server_dir)
            if result.returncode != 0:
                print(f"  ✗ Build command failed: {cmd}")
                return False

        # Verify installation
        if check_file:
            if (server_dir / check_file).exists():
                print(f"  ✓ Successfully installed {server_name}")
                return True
            else:
                print(f"  ✗ Build completed but {check_file} not found")
                return False

        return True

    print(f"  ✗ Unknown server type: {server_type}")
    return False


def check_mcp_servers_installed(mcp_tools_dir: Path) -> dict:
    """Check installation status of all MCP servers."""
    results = {}
    for server_key in MCP_SERVERS:
        installed, status = check_server_installed(server_key, mcp_tools_dir)
        results[server_key] = {
            "name": MCP_SERVERS[server_key].get("name", server_key),
            "installed": installed,
            "status": status
        }
    return results


def install_missing_servers(mcp_tools_dir: Path, force: bool = False, servers: Optional[list] = None) -> dict:
    """Install missing MCP servers."""
    results = {}

    # Determine which servers to check
    server_list = servers if servers else list(MCP_SERVERS.keys())

    for server_key in server_list:
        if server_key not in MCP_SERVERS:
            print(f"  ⚠ Unknown server: {server_key}")
            continue

        installed, status = check_server_installed(server_key, mcp_tools_dir)

        if installed and not force:
            results[server_key] = {"installed": True, "action": "skipped", "status": status}
            continue

        success = install_server(server_key, mcp_tools_dir, force=force)
        results[server_key] = {
            "installed": success,
            "action": "installed" if success else "failed",
            "status": "Installed" if success else "Installation failed"
        }

    return results


def generate_mcp_config(mcp_tools_dir: Path, servers: Optional[list] = None) -> dict:
    """Generate MCP configuration for all installed servers."""
    config = {"mcpServers": {}}
    mcp_tools_str = str(mcp_tools_dir).replace("\\", "/")
    npm_global_str = str(NPM_GLOBAL_DIR).replace("\\", "/")

    server_list = servers if servers else list(MCP_SERVERS.keys())

    for server_key in server_list:
        server = MCP_SERVERS.get(server_key)
        if not server:
            continue

        installed, _ = check_server_installed(server_key, mcp_tools_dir)
        if not installed:
            continue

        # Get config (use template if available, otherwise static config)
        if "config_template" in server:
            config_json = json.dumps(server["config_template"])
            config_json = config_json.replace("{mcp_tools_dir}", mcp_tools_str)
            config_json = config_json.replace("{npm_global_dir}", npm_global_str)
            server_config = json.loads(config_json)
        else:
            server_config = server.get("config", {})

        if server_config:
            config["mcpServers"][server_key] = server_config

    return config


def check_mcp_tools_installed() -> dict:
    """Check if basic MCP tools (npm, uvx, etc.) are installed."""
    tools = {
        "node": {
            "installed": False,
            "install": "Install Node.js from https://nodejs.org/",
        },
        "npm": {
            "installed": False,
            "install": "Comes with Node.js",
        },
        "npx": {
            "installed": False,
            "install": "Comes with Node.js",
        },
        "pnpm": {
            "installed": False,
            "install": "npm install -g pnpm",
        },
        "uvx": {
            "installed": False,
            "install": "pip install uv",
        },
        "git": {
            "installed": False,
            "install": "Install Git from https://git-scm.com/",
        },
        "python": {
            "installed": False,
            "install": "Install Python from https://python.org/",
        },
    }

    for tool_name, tool_info in tools.items():
        # Use shutil.which as primary check (most reliable)
        tool_info["installed"] = shutil.which(tool_name) is not None

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
        help="Check if MCP tools and servers are installed"
    )
    parser.add_argument(
        "--detect", "-d",
        action="store_true",
        help="Detect running IDEs"
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install missing MCP servers"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force reinstallation of servers"
    )
    parser.add_argument(
        "--servers", "-s",
        type=str,
        nargs="+",
        help="Specific servers to install/check (default: all)"
    )
    parser.add_argument(
        "--mcp-dir",
        type=str,
        default=str(DEFAULT_MCP_TOOLS_DIR),
        help=f"MCP tools directory (default: {DEFAULT_MCP_TOOLS_DIR})"
    )
    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Generate MCP config JSON for installed servers"
    )

    args = parser.parse_args()
    mcp_tools_dir = Path(args.mcp_dir)

    # Find project root and load settings
    project_root = find_project_root()
    mcp_settings = load_mcp_settings(project_root)

    if args.list:
        print("\n📋 Supported IDEs:\n")
        for key, config in IDE_MCP_CONFIGS.items():
            print(f"  • {key:15s} - {config['name']}")

        print("\n📦 Available MCP Servers:\n")
        for key, server in MCP_SERVERS.items():
            print(f"  • {key:20s} - {server['name']}")
            if "note" in server:
                print(f"    Note: {server['note']}")

        print(f"\nUsage: python setup_mcp.py --ide <name>")
        print(f"       python setup_mcp.py --install [--servers <names>]")
        return 0

    if args.check:
        print("\n🔍 Checking MCP tool installation:\n")
        tools = check_mcp_tools_installed()

        for tool_name, tool_info in tools.items():
            status = "✓" if tool_info["installed"] else "✗"
            print(f"  {status} {tool_name}")
            if not tool_info["installed"]:
                print(f"     Install: {tool_info['install']}")

        print(f"\n🔍 Checking MCP servers (dir: {mcp_tools_dir}):\n")
        servers = check_mcp_servers_installed(mcp_tools_dir)

        for server_key, info in servers.items():
            status = "✓" if info["installed"] else "✗"
            print(f"  {status} {info['name']:25s} - {info['status']}")

        return 0

    if args.detect:
        print("\n🔍 Detecting running IDEs...\n")
        detected = detect_running_ide()

        if detected:
            print(f"Found: {', '.join(detected)}")
        else:
            print("No supported IDEs detected running.")
        return 0

    if args.install:
        print(f"\n🔧 Installing MCP servers to: {mcp_tools_dir}\n")

        # First check prerequisites
        tools = check_mcp_tools_installed()
        missing_tools = [k for k, v in tools.items() if not v["installed"] and k in ("node", "npm", "git", "python")]

        if missing_tools:
            print("⚠️  Missing required tools:")
            for tool in missing_tools:
                print(f"   • {tool}: {tools[tool]['install']}")
            print("\nInstall these tools first, then re-run this script.")
            return 1

        # Install servers
        results = install_missing_servers(
            mcp_tools_dir,
            force=args.force,
            servers=args.servers
        )

        print("\n📊 Installation Summary:\n")
        for server_key, result in results.items():
            status = "✓" if result["installed"] else "✗"
            action = result.get("action", "unknown")
            print(f"  {status} {server_key:20s} - {action}")

        # Generate config
        if any(r["installed"] for r in results.values()):
            print("\n📝 Generated MCP config:\n")
            config = generate_mcp_config(mcp_tools_dir, servers=args.servers)
            print(json.dumps(config, indent=2))

        return 0

    if args.generate_config:
        config = generate_mcp_config(mcp_tools_dir, servers=args.servers)
        print(json.dumps(config, indent=2))
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

    # Use project settings or generate from installed servers
    if not mcp_settings:
        mcp_settings = generate_mcp_config(mcp_tools_dir)

    show_setup_instructions(target_ide, mcp_settings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
