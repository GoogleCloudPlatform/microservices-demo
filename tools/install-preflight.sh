#!/usr/bin/env bash
# Extract the bundled Preflight plugin into the project's .claude/ tree
# and register it in .claude/settings.json so Claude Code loads it on
# the next session. Project-local install — does not touch ~/.claude/.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ARCHIVE="${REPO_ROOT}/tools/preflight.tar.gz"
PLUGIN_DIR="${REPO_ROOT}/.claude/plugins/preflight"
SETTINGS="${REPO_ROOT}/.claude/settings.json"

if [[ ! -f "$ARCHIVE" ]]; then
  echo "preflight install: archive not found at $ARCHIVE" >&2
  echo "Are you running this from the workshop repo root?" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "preflight install: jq is required (used by both this installer and the plugin's stamp checks)." >&2
  echo "Install it with: brew install jq   (macOS)   or   apt-get install jq   (Linux)" >&2
  exit 1
fi

if [[ -d "$PLUGIN_DIR" ]]; then
  echo "preflight install: $PLUGIN_DIR already exists. Re-running will overwrite plugin files but keep your settings.json registration."
  read -r -p "Continue? [y/N] " reply
  if [[ ! "$reply" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
  fi
  rm -rf "$PLUGIN_DIR"
fi

echo "Extracting Preflight plugin into $PLUGIN_DIR ..."
mkdir -p "$PLUGIN_DIR"
tar -xzf "$ARCHIVE" -C "$PLUGIN_DIR"

# Make sure all bundled shell scripts are executable on this checkout.
find "$PLUGIN_DIR/scripts" "$PLUGIN_DIR/hooks" -type f -name '*.sh' -exec chmod +x {} +
[[ -f "$PLUGIN_DIR/git-hooks/pre-push" ]] && chmod +x "$PLUGIN_DIR/git-hooks/pre-push"

# Register the plugin in .claude/settings.json. Merge with whatever is
# already there so we don't clobber existing settings.
mkdir -p "$(dirname "$SETTINGS")"
if [[ ! -f "$SETTINGS" ]]; then
  echo '{}' > "$SETTINGS"
fi

tmp="$(mktemp)"
jq '.enabledPlugins.preflight = {"source": {"source": "local-directory", "path": ".claude/plugins/preflight"}}' \
  "$SETTINGS" > "$tmp"
mv "$tmp" "$SETTINGS"

echo
echo "Preflight installed."
echo
echo "What landed:"
echo "  .claude/plugins/preflight/   plugin tree (manifest, agents, hooks, scripts)"
echo "  .claude/settings.json        enabledPlugins.preflight registered"
echo
echo "Next steps:"
echo "  1. Restart Claude Code so it picks up the new plugin."
echo "  2. Run  /preflight:preflight  to gate your branch (or  /preflight  if there's no naming collision)."
echo "  3. Run  /preflight:install-preflight-hook  to drop the native git pre-push hook."
echo
echo "To uninstall: delete .claude/plugins/preflight/ and remove the preflight key from .claude/settings.json."
