#!/usr/bin/env bash
# Switch the automatic work generator (BOINC task "nah_generate", every 10 minutes) on or off.
# On: it keeps campaign.max_in_flight work units queued, so connected computers start working.
# Usage: bash server/staging/autogen.sh on|off [path to boinc-server-docker checkout]
set -euo pipefail
case "${1:-}" in on) want=0 ;; off) want=1 ;; *) echo "usage: $0 on|off" >&2; exit 2 ;; esac
cd "${2:-$HOME/nah-staging/boinc-server-docker}"
docker compose exec -T -u boincadm apache sed -i \
  "/<cmd>nah_generate<\/cmd>/,/<\/task>/ s|<disabled>[01]</disabled>|<disabled>$want</disabled>|" \
  /home/boincadm/project/config.xml
echo "work generator $1 (takes effect at the next 5-minute BOINC cron run)"
