---
description: Install the bundled Preflight plugin into this project's .claude/ tree.
---

Run the bundled installer to extract the Preflight plugin from `tools/preflight.tar.gz`
into `.claude/plugins/preflight/` and register it in `.claude/settings.json`.

Steps:

1. Run from the repo root:

   ```
   bash tools/install-preflight.sh
   ```

   The script:
   - extracts the plugin tree into `.claude/plugins/preflight/`
   - merges an `enabledPlugins.preflight` entry into `.claude/settings.json`
   - leaves `~/.claude/` untouched (project-local install)

2. Surface the script's stdout to the user verbatim — it lists what landed where
   and how to invoke the plugin's commands.

3. Tell the user to **restart Claude Code** so the plugin loads. Without a
   restart, the new slash commands and hooks will not be available in the
   current session.

4. After restart the user can run:
   - `/preflight:preflight` — gate the current branch (the `/preflight:` prefix
     comes from the plugin name; if there's no naming collision Claude may
     also accept `/preflight`)
   - `/preflight:install-preflight-hook` — drop the native git pre-push hook
   - `/preflight:preflight-pr` — generate a PR description from the last
     preflight report

If `tools/preflight.tar.gz` is missing or `jq` is not installed, the script
prints an actionable error and exits non-zero — relay it to the user as-is.

To remove Preflight afterwards: delete `.claude/plugins/preflight/` and remove
the `preflight` key from `.claude/settings.json`.
