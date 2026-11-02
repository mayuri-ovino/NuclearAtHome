#!/usr/bin/env bash
# Build the static LAMMPS binary shipped to volunteers (Linux x86_64, serial).
# Uses LAMMPS's traditional make build (no cmake needed).
# Packages: MANYBODY (EAM/FS), EXTRA-FIX (electron/stopping, dt/reset), VORONOI
# (Wigner-Seitz occupation). Add packages here only when an approved potential needs them.
# LAMMPS is GPL-2: publish this script and the exact source tarball with every release.
#
# Usage: bash client/build_lammps.sh [work_dir]
set -euo pipefail

VERSION="29Aug2024"
URL="https://download.lammps.org/tars/lammps-${VERSION}.tar.gz"
# Matches https://download.lammps.org/tars/SHA256SUMS (checked 2026-11-01).
SHA256="7d39c788ab808494c334a07e6b3fe2f3e01359f5741bf8e4b48842f262e1687c"

repo="$(cd "$(dirname "$0")/.." && pwd)"
work="${1:-$(mktemp -d)}"
mkdir -p "$work"
cd "$work"
[ -f lammps.tar.gz ] || curl -fsSL "$URL" -o lammps.tar.gz
echo "${SHA256}  lammps.tar.gz" | sha256sum -c -
tar -xzf lammps.tar.gz
cd "lammps-${VERSION}"

# voro++ is fetched by LAMMPS's own installer, which checks its checksum.
(cd lib/voronoi && python3 Install.py -b)
cd src
make yes-manybody yes-extra-fix yes-voronoi
make -j "$(nproc)" serial LINKFLAGS="-O2 -static"
install -m 0755 lmp_serial "$repo/client/app_version/lmp_nah_stable_${VERSION}"
sha256sum "$repo/client/app_version/lmp_nah_stable_${VERSION}"
