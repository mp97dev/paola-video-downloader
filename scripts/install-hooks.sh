#!/usr/bin/env bash
#
# Points git at the tracked hooks in scripts/git-hooks.
# Run once per clone: ./scripts/install-hooks.sh
set -euo pipefail

# Resolve the repo from this script's own location, so it works from any cwd.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(git -C "$script_dir" rev-parse --show-toplevel)"

chmod +x "$repo_root/scripts/git-hooks/"*
git -C "$repo_root" config core.hooksPath scripts/git-hooks

echo "[II] git hooks installed (core.hooksPath = scripts/git-hooks)"
