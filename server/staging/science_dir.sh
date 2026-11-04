#!/usr/bin/env bash
# Print the results folder from config/staging.conf, or the default given as $1 when none is set.
# A configured folder must already exist and be writable: this refuses to start on a missing USB drive.
set -euo pipefail
conf="$(cd "$(dirname "$0")/../.." && pwd)/config/staging.conf"
dir=$(sed -n 's/^science_dir=//p' "$conf" | sed 's/[[:space:]]*$//')
if [ -z "$dir" ]; then echo "$1"; exit 0; fi
for sub in results wu; do
  [ -d "$dir/$sub" ] && [ -w "$dir/$sub" ] || { echo "$dir/$sub is missing or not writable: is the USB drive plugged in? (config/staging.conf)" >&2; exit 1; }
done
echo "$dir"
