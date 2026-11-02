#!/usr/bin/env bash
# Build the static LAMMPS binary shipped to volunteers (Linux x86_64, serial).
# Packages: MANYBODY (EAM/FS), EXTRA-FIX (electron/stopping, dt/reset), VORONOI
# (Wigner-Seitz occupation). Add packages here only when an approved potential needs them.
# LAMMPS is GPL-2: publish this script and the exact source tarball with every release.
#
# Usage: LAMMPS_SHA256=<pinned hash> bash client/build_lammps.sh
set -euo pipefail

TAG="stable_29Aug2024"
URL="https://github.com/lammps/lammps/archive/refs/tags/${TAG}.tar.gz"
: "${LAMMPS_SHA256:?set LAMMPS_SHA256 to the hash recorded for ${TAG} (TODO-DECIDE: record it after the first verified download)}"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
curl -fsSL "$URL" -o "$work/lammps.tar.gz"
echo "${LAMMPS_SHA256}  $work/lammps.tar.gz" | sha256sum -c -
tar -xzf "$work/lammps.tar.gz" -C "$work"

cmake -S "$work/lammps-${TAG}/cmake" -B "$work/build" \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_MPI=no -DBUILD_OMP=no -DBUILD_SHARED_LIBS=no \
  -DCMAKE_EXE_LINKER_FLAGS="-static" \
  -DPKG_MANYBODY=yes -DPKG_EXTRA-FIX=yes -DPKG_VORONOI=yes -DDOWNLOAD_VORO=yes
cmake --build "$work/build" -j "$(nproc)"
install -m 0755 "$work/build/lmp" "client/app_version/lmp_nah_${TAG}"
echo "Built client/app_version/lmp_nah_${TAG}"
