#!/usr/bin/env bash
# Convert a list of attendee emails (one per line, # for comments) into the
# CSV format provision.sh expects. Bugs are assigned round-robin across
# the catalog under training/bugs/, so each attendee's neighbour gets a
# different bug.
#
#   ./emails-to-csv.sh emails.txt > attendees.csv
#
# Stdout: name,bug
# Stderr: a "lookup" table mapping email -> handle, so you know who's who.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUGS_DIR="$REPO_ROOT/training/bugs"

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <emails.txt>" >&2
  exit 2
fi

bugs=()
while IFS= read -r b; do bugs+=("$b"); done < <(
  cd "$BUGS_DIR" && for d in */; do echo "${d%/}"; done | sort
)
[[ ${#bugs[@]} -gt 0 ]] || { echo "no bugs found in $BUGS_DIR" >&2; exit 1; }

used=" "
i=0
echo "name,bug"
echo "email -> handle mapping:" >&2
echo "------------------------" >&2

while IFS= read -r line || [[ -n "$line" ]]; do
  # Skip blanks and comments
  line="${line%%#*}"
  line="$(echo "$line" | xargs)"
  [[ -z "$line" ]] && continue

  local_part="${line%%@*}"
  # Lowercase, replace . _ + with -, strip anything that's not [a-z0-9-]
  handle="$(echo "$local_part" | tr '[:upper:]' '[:lower:]' | tr '._+' '-' | sed 's/[^a-z0-9-]//g')"
  # Trim leading non-alpha (RFC 1123: must start with a letter)
  handle="$(echo "$handle" | sed 's/^[^a-z]*//')"
  # Cap length
  handle="${handle:0:25}"
  [[ -z "$handle" ]] && { echo "could not derive handle from: $line" >&2; exit 1; }

  # De-duplicate
  base="$handle"
  n=2
  while [[ "$used" == *" $handle "* ]]; do
    handle="${base}-$n"
    n=$((n+1))
  done
  used="$used$handle "

  bug="${bugs[i % ${#bugs[@]}]}"
  i=$((i+1))

  echo "$handle,$bug"
  printf '  %-40s -> %s (%s)\n' "$line" "$handle" "$bug" >&2
done < "$1"
