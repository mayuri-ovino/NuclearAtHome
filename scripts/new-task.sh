#!/usr/bin/env bash
# Create the next numbered task card from the template.
# Usage: bash scripts/new-task.sh "Short task title"
set -euo pipefail

cd "$(dirname "$0")/.."

title="${1:-Untitled task}"
tasks_dir="docs/tasks"

last=$(ls "$tasks_dir" 2>/dev/null | grep -oE '^T-[0-9]{3}' | sed 's/T-//' | sort -n | tail -1 || true)
next=$(printf "%03d" $(( 10#${last:-0} + 1 )))
id="T-$next"
file="$tasks_dir/$id.md"

sed -e "s/{{ID}}/$id/g" -e "s/{{TITLE}}/$title/g" "$tasks_dir/TEMPLATE.md" > "$file"
printf '| %s | %s | - | - | todo | - | no |\n' "$id" "$title" >> "$tasks_dir/TRACKER.md"

echo "Created $file and added it to TRACKER.md"
