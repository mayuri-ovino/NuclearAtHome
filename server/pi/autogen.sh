#!/usr/bin/env bash
# Switch the automatic work generator on or off on a native install (Pi). Usage: autogen.sh on|off
set -euo pipefail
case "${1:-}" in on) want=0 ;; off) want=1 ;; *) echo "usage: $0 on|off" >&2; exit 2 ;; esac
runuser -u boincadm -- sed -i \
  "/<cmd>nah_generate<\/cmd>/,/<\/task>/ s|<disabled>[01]</disabled>|<disabled>$want</disabled>|" \
  /home/boincadm/projects/nuclear/config.xml
echo "work generator $1 (takes effect at the next 5-minute cron run)"
