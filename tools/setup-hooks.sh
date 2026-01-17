#!/bin/bash
# setup-hooks.sh - Cross-platform pre-commit hook setup for Linux and macOS
# Usage: ./tools/setup-hooks.sh
#
# This script installs Gitleaks and pre-commit hooks for secret scanning.
# See .agent/docs/secret-scanning-setup.md for full documentation.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

GITLEAKS_VERSION="8.21.2"

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Darwin*) echo "macos" ;;
        Linux*)  echo "linux" ;;
        *)       echo "unknown" ;;
    esac
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Gitleaks on macOS
install_gitleaks_macos() {
    if command_exists brew; then
        print_status "Installing Gitleaks via Homebrew..."
        brew install gitleaks
    else
        print_error "Homebrew not found. Please install Homebrew first:"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
}

# Install Gitleaks on Linux
install_gitleaks_linux() {
    print_status "Downloading Gitleaks v${GITLEAKS_VERSION}..."

    local ARCH
    case "$(uname -m)" in
        x86_64) ARCH="x64" ;;
        aarch64|arm64) ARCH="arm64" ;;
        *) print_error "Unsupported architecture: $(uname -m)"; exit 1 ;;
    esac

    local TARBALL="gitleaks_${GITLEAKS_VERSION}_linux_${ARCH}.tar.gz"
    local URL="https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/${TARBALL}"

    curl -sSL "$URL" -o "/tmp/${TARBALL}"
    tar -xzf "/tmp/${TARBALL}" -C /tmp

    if [ -w /usr/local/bin ]; then
        mv /tmp/gitleaks /usr/local/bin/
    else
        print_status "Requires sudo to install to /usr/local/bin..."
        sudo mv /tmp/gitleaks /usr/local/bin/
    fi

    rm -f "/tmp/${TARBALL}"
    print_success "Gitleaks installed to /usr/local/bin/gitleaks"
}

# Install pre-commit
install_precommit() {
    print_status "Installing pre-commit via pip..."

    if command_exists pip3; then
        pip3 install --user pre-commit
    elif command_exists pip; then
        pip install --user pre-commit
    else
        print_error "pip not found. Please install Python and pip first."
        exit 1
    fi
}

# Main installation
main() {
    echo ""
    echo "=================================================="
    echo "  Pre-commit Hook Setup Script"
    echo "  Secret Scanning with Gitleaks"
    echo "=================================================="
    echo ""

    local OS
    OS=$(detect_os)
    print_status "Detected OS: ${OS}"

    if [ "$OS" = "unknown" ]; then
        print_error "Unsupported operating system. Please install manually."
        exit 1
    fi

    # Check/Install Gitleaks
    if command_exists gitleaks; then
        print_success "Gitleaks already installed: $(gitleaks version)"
    else
        print_warning "Gitleaks not found. Installing..."
        if [ "$OS" = "macos" ]; then
            install_gitleaks_macos
        else
            install_gitleaks_linux
        fi
    fi

    # Check/Install pre-commit
    if command_exists pre-commit; then
        print_success "pre-commit already installed: $(pre-commit --version)"
    else
        print_warning "pre-commit not found. Installing..."
        install_precommit
    fi

    # Ensure we're in the git repository root
    if [ ! -f ".pre-commit-config.yaml" ]; then
        print_error "Cannot find .pre-commit-config.yaml"
        print_error "Please run this script from the project root directory."
        exit 1
    fi

    # Install pre-commit hooks
    print_status "Installing pre-commit hooks..."
    pre-commit install

    # Run initial scan
    print_status "Running initial scan (this may take a moment)..."
    if pre-commit run --all-files; then
        print_success "All checks passed!"
    else
        print_warning "Some checks failed or fixed files. Review the output above."
    fi

    echo ""
    echo "=================================================="
    print_success "Setup complete!"
    echo ""
    echo "Your commits will now be automatically scanned for:"
    echo "  🔐 Secrets and credentials (Gitleaks)"
    echo "  🐘 Large files (>5MB)"
    echo "  ✅ JSON/YAML syntax errors"
    echo "  🔑 Private keys"
    echo ""
    echo "To manually scan: pre-commit run --all-files"
    echo "To bypass (emergency only): git commit --no-verify"
    echo "=================================================="
}

main
