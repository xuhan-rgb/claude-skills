#!/usr/bin/env bash
# Configure both clients; install dependencies in an isolated environment.
set -euo pipefail
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    python3 "$repo_dir/scripts/install.py" --help
    exit 0
fi
installer_venv="${XDG_DATA_HOME:-$HOME/.local/share}/claude-skills-installer"
if [[ ! -x "$installer_venv/bin/python" ]]; then
    if command -v uv >/dev/null 2>&1; then
        uv venv "$installer_venv" --python python3
    else
        python3 -m venv "$installer_venv" || {
            echo 'Install Python venv support (Debian/Ubuntu: sudo apt install python3-venv), or install uv, then retry.' >&2
            exit 1
        }
    fi
fi
if ! "$installer_venv/bin/python" -c 'import tomlkit' 2>/dev/null; then
    if command -v uv >/dev/null 2>&1; then
        uv pip install --python "$installer_venv/bin/python" 'tomlkit==0.13.3'
    else
        "$installer_venv/bin/python" -m ensurepip --upgrade
        "$installer_venv/bin/python" -m pip install 'tomlkit==0.13.3'
    fi
fi
exec "$installer_venv/bin/python" "$repo_dir/scripts/install.py" "$@"
