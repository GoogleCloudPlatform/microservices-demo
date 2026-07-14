#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# quality-gate.sh — quality gate hook (Stop / SubagentStop)
#
# Enforces the "Goal-Driven Execution — loop until verified" rule: before any
# agent is allowed to finish, the project must BUILD and all TESTS pass. On
# failure it blocks (exit 2) and feeds the output back so the agent keeps
# fixing until green.
#
# ── TWO MODES ──────────────────────────────────────────────────────────────
# 1. SINGLE-SERVICE (default): one global build/test pair, read from the env.
# 2. ROUTED (monorepo): a per-service routing table. The gate looks at WHICH
#    files changed and runs ONLY the build/test commands of the services that
#    actually changed. A change under src/cart/ runs the cart commands; a change
#    under src/checkout/ runs the checkout commands — never all of them. This is
#    what makes the gate usable AND meaningful in a polyglot monorepo: fast
#    (only the touched service is built) and honest (green covers the code that
#    changed). Single-service is just the one-route degenerate case.
#
# ── CONFIGURE ME (per repo, NOT here) ──────────────────────────────────────
# SINGLE-SERVICE — set the commands ONCE per repo in .claude/settings.json
# (init-dev-kit writes this for you):
#
#   "env": { "QG_BUILD_CMD": "...", "QG_TEST_CMD": "..." }
#
# Examples:
#   .NET:    QG_BUILD_CMD="dotnet build"             QG_TEST_CMD="dotnet test"
#   Node:    QG_BUILD_CMD="npm run build"            QG_TEST_CMD="npm test"
#   Python:  QG_BUILD_CMD="uv run ruff check . && uv run mypy src"  QG_TEST_CMD="uv run pytest"
#   Go:      QG_BUILD_CMD="go build ./..."           QG_TEST_CMD="go test ./..."
#   Rust:    QG_BUILD_CMD="cargo build"              QG_TEST_CMD="cargo test"
# Leave QG_BUILD_CMD empty to skip the build phase; leave QG_TEST_CMD empty to skip tests.
#
# ROUTED — create .claude/quality-gate.routes (committed). One route per line,
# three `::`-separated fields, leading/trailing space trimmed:
#
#   <path-prefix> :: <build_cmd> :: <test_cmd>
#
#   src/cart/           :: dotnet build src/cart       :: dotnet test src/cart
#   src/checkout/       :: go build ./src/checkout/... :: go test ./src/checkout/...
#   src/recommendation/ ::                             :: pytest src/recommendation
#   protos/             :: <build the consumers, `&&`-chained> ::
#
# A path-prefix matches a changed file when the file path STARTS WITH it (so it
# works for a directory `src/cart/` or a file `go.mod`). Leave a command field
# empty to skip that phase for that service. A SHARED dir (proto/IDL contracts,
# OpenAPI specs, a shared lib) is routed the same way — point its prefix at a
# COMPOSITE command that builds/tests its consumers (see
# quality-gate.routes.example, Shape E). Lines that are blank or start with
# `#` are ignored. When this file has at least one active route it takes over;
# QG_BUILD_CMD/QG_TEST_CMD are then the fallback for changed files that match
# NO route (so a repo-wide lint can still run) — leave them empty for none.
#
# Leave BOTH the env pair empty AND ship no routes (e.g. a multi-language repo
# you couldn't unify) and the gate no-ops — verification then falls to each
# task's own acceptance check.
#
# IMPORTANT: a gate only verifies what its commands actually exercise. In routed
# mode each service's green covers that service; a changed file matching no route
# is NOT verified by the gate — the gate WARNS about it (see below) so the gap is
# visible, and the pipeline then relies on that task's own executed acceptance check.
#
# WATCH_PATHS (single-service mode only) limits when the gate runs: it only fires
# if the working tree has pending changes under these paths. Tune it via
# QG_WATCH_PATHS. In routed mode the route prefixes ARE the watch filter.
# ---------------------------------------------------------------------------
set -uo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$PROJECT_DIR" || exit 0

# Read the hook payload from stdin (used to detect re-entrancy).
payload="$(cat 2>/dev/null || true)"

BUILD_CMD="${QG_BUILD_CMD:-}"     # e.g. "dotnet build" / "npm run build" / "go build ./..."
TEST_CMD="${QG_TEST_CMD:-}"       # e.g. "dotnet test"  / "npm test"      / "pytest -q"
ROUTES_FILE="${QG_ROUTES_FILE:-.claude/quality-gate.routes}"

# Space-separated override; otherwise a broad cross-stack default.
if [ -n "${QG_WATCH_PATHS:-}" ]; then
  # shellcheck disable=SC2206
  WATCH_PATHS=(${QG_WATCH_PATHS})
else
  WATCH_PATHS=(src/ tests/ test/ lib/ app/ pkg/ cmd/ internal/ services/ '*.sln' '*.slnx' package.json go.mod Cargo.toml pyproject.toml pom.xml build.gradle)
fi

phase=""
fail_out=""

# Is the executable a command needs present on this machine?
tool_present() {
  local tool="$1"
  case "$tool" in
    "") return 0 ;;                         # empty command → nothing to check
    ./*|/*) [ -x "$tool" ] ;;               # explicit path, e.g. ./gradlew
    *) command -v "$tool" >/dev/null 2>&1 ;;
  esac
}

# A missing toolchain is a SETUP problem, not a code failure — block with an
# actionable message (install it / comment the route) instead of a raw 127.
missing_tool_msg() {
  local cmd="$1" tool="$2"
  printf '%s\n' \
    "This route needs '$tool', which is not installed on this machine." \
    "The dev-kit premise is you have the toolchains for the services you touch." \
    "Fix: install '$tool' (see the repo's dev setup / docs/test/README.md prerequisites)," \
    "or — if you don't work on this service — comment its route out in .claude/quality-gate.routes." \
    "Command was: $cmd"
}

# Run one build/test pair. Sets $phase/$fail_out and returns 1 on the first
# failing phase; returns 0 when both phases pass (or are empty/skipped).
run_pair() {
  local label="$1" b="$2" t="$3" out st tool
  if [ -n "$b" ]; then
    tool="${b%% *}"
    if ! tool_present "$tool"; then
      phase="build${label:+ [$label]} — toolchain '$tool' not installed"
      fail_out="$(missing_tool_msg "$b" "$tool")"; return 1
    fi
    out="$(eval "$b" 2>&1)"; st=$?
    if [ $st -ne 0 ]; then phase="build${label:+ [$label]} ($b)"; fail_out="$out"; return 1; fi
  fi
  if [ -n "$t" ]; then
    tool="${t%% *}"
    if ! tool_present "$tool"; then
      phase="test${label:+ [$label]} — toolchain '$tool' not installed"
      fail_out="$(missing_tool_msg "$t" "$tool")"; return 1
    fi
    out="$(eval "$t" 2>&1)"; st=$?
    if [ $st -ne 0 ]; then phase="test${label:+ [$label]} ($t)"; fail_out="$out"; return 1; fi
  fi
  return 0
}

# Emit the block (exit 2) or, on a repeated failure (stop_hook_active true),
# allow the stop but surface the still-RED tree LOUDLY — a stderr WARNING plus a
# user-visible {"systemMessage": …} on stdout — so red is never silent. Blocking
# once then allowing keeps the gate from grinding (Claude Code force-overrides a
# Stop hook after 8 blocks anyway) while a human is handed the intervention.
block_or_allow() {
  if printf '%s' "$payload" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
    {
      echo "WARNING: ${phase} still failing after a retry — allowing the stop so you can intervene."
      echo "Do NOT commit; the tree is not green."
    } >&2
    # Fixed message → the JSON is always valid (no interpolation to escape). The
    # failing phase is in the stderr WARNING above for logs/transcript.
    printf '%s\n' '{"systemMessage": "quality gate: still RED after a retry — allowed to stop so you can intervene. Do NOT commit; the tree is not green."}'
    exit 0
  fi
  {
    echo "QUALITY GATE FAILED: ${phase} did not pass. Do not finish — fix and re-run."
    echo "----------------------------------------------------------------------"
    printf '%s\n' "$fail_out" | tail -60
  } >&2
  exit 2
}

# Parse active routes (prefix<TAB>build<TAB>test) once, if the file exists.
routes_tsv=""
if [ -f "$ROUTES_FILE" ]; then
  routes_tsv="$(awk -F'::' '
    /^[[:space:]]*#/ { next }
    /^[[:space:]]*$/ { next }
    {
      p=$1; b=$2; t=$3
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", p)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", b)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", t)
      if (p == "") next
      printf "%s\t%s\t%s\n", p, b, t
    }' "$ROUTES_FILE")"
fi

# =========================================================================
# ROUTED MODE — at least one active route is configured.
# =========================================================================
if [ -n "$routes_tsv" ]; then
  # Which files changed (tracked modifications + untracked). Without git we
  # can't route, so fall back to running every route (with a warning).
  changed=""
  have_git=0
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    have_git=1
    changed="$(git status --porcelain 2>/dev/null | sed -e 's/^...//' -e 's/.* -> //')"
    [ -z "$changed" ] && exit 0   # nothing changed → nothing to gate
  fi

  matched_files=""
  ran_pairs=""   # dedup key list: one "build\ttest" per line already run

  while IFS=$'\t' read -r prefix b t; do
    [ -z "$prefix" ] && continue

    # Does any changed file fall under this route's prefix?
    hit=0
    if [ "$have_git" -eq 1 ]; then
      while IFS= read -r f; do
        [ -z "$f" ] && continue
        case "$f" in
          "$prefix"*) hit=1; matched_files="${matched_files}${f}"$'\n' ;;
        esac
      done <<< "$changed"
    else
      hit=1   # no git → run every route
    fi
    [ "$hit" -eq 0 ] && continue

    # Dedup: skip if an identical (build,test) pair already ran this invocation.
    key="${b}"$'\t'"${t}"
    case $'\n'"$ran_pairs" in
      *$'\n'"$key"$'\n'*) continue ;;
    esac
    ran_pairs="${ran_pairs}${key}"$'\n'

    if ! run_pair "$prefix" "$b" "$t"; then
      block_or_allow
    fi
  done <<< "$routes_tsv"

  # Changed files that matched NO route are not covered by the gate. Surface
  # them (non-blocking) so the gap is visible rather than silent.
  if [ "$have_git" -eq 1 ]; then
    unmatched=""
    while IFS= read -r f; do
      [ -z "$f" ] && continue
      case $'\n'"$matched_files" in
        *$'\n'"$f"$'\n'*) : ;;                 # covered by a route
        *) unmatched="${unmatched}  ${f}"$'\n' ;;
      esac
    done <<< "$changed"

    # Fallback global pair (if configured) covers unmatched changes; else warn.
    if [ -n "$unmatched" ]; then
      if [ -n "$BUILD_CMD" ] || [ -n "$TEST_CMD" ]; then
        if ! run_pair "unrouted" "$BUILD_CMD" "$TEST_CMD"; then
          block_or_allow
        fi
      else
        {
          echo "NOTE: changed files matched no quality-gate route and are NOT verified by the gate:"
          printf '%s' "$unmatched"
          echo "      (Add a route in $ROUTES_FILE, or rely on the task's own acceptance check.)"
        } >&2
      fi
    fi
  fi

  exit 0
fi

# =========================================================================
# SINGLE-SERVICE MODE — no routes file; use the global build/test pair.
# =========================================================================

# Nothing configured → nothing to gate.
if [ -z "$BUILD_CMD" ] && [ -z "$TEST_CMD" ]; then
  exit 0
fi

# Only gate when build-relevant files actually changed. If git isn't available,
# fall through and gate anyway.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  changes="$(git status --porcelain -- "${WATCH_PATHS[@]}" 2>/dev/null || true)"
  if [ -z "$changes" ]; then
    exit 0
  fi
fi

if ! run_pair "" "$BUILD_CMD" "$TEST_CMD"; then
  block_or_allow
fi

exit 0
