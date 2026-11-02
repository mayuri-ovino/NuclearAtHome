#!/usr/bin/env bash
# Build the LAMMPS binaries shipped to volunteers (Linux x86_64, serial).
#   cpu (default): static binary, core 0xa1
#   gpu:           GPU package over OpenCL, full double precision, core 0xa2. Linked
#                  dynamically: the OpenCL loader (libOpenCL.so.1) comes with the GPU driver.
# Uses LAMMPS's traditional make build (no cmake needed).
# Packages: MANYBODY (EAM/FS), EXTRA-FIX (electron/stopping, dt/reset), VORONOI
# (Wigner-Seitz occupation). Add packages here only when an approved potential needs them.
# LAMMPS is GPL-2: publish this script and the exact source tarball with every release.
#
# Usage: bash client/build_lammps.sh [work_dir] [cpu|gpu]
set -euo pipefail

VERSION="29Aug2024"
URL="https://download.lammps.org/tars/lammps-${VERSION}.tar.gz"
# Matches https://download.lammps.org/tars/SHA256SUMS (checked 2026-11-01).
SHA256="7d39c788ab808494c334a07e6b3fe2f3e01359f5741bf8e4b48842f262e1687c"

repo="$(cd "$(dirname "$0")/.." && pwd)"
work="${1:-$(mktemp -d)}"
variant="${2:-cpu}"
mkdir -p "$work"
cd "$work"
[ -f lammps.tar.gz ] || curl -fsSL "$URL" -o lammps.tar.gz
echo "${SHA256}  lammps.tar.gz" | sha256sum -c -
tar -xzf lammps.tar.gz
cd "lammps-${VERSION}"

# voro++ is fetched by LAMMPS's own installer, which checks its checksum.
(cd lib/voronoi && python3 Install.py -b)
if [ "$variant" = gpu ]; then
  # Serial (MPI stubs), no OpenMP, double precision: the GPU must pass the same energy check as the CPU.
  (cd lib/gpu \
   && sed -e 's|^OCL_CPP = mpic++|OCL_CPP = g++ -I../../src/STUBS|' -e 's/-DMPI_GERYON //' -e 's/-fopenmp //' \
          -e 's/-D_SINGLE_DOUBLE/-D_DOUBLE_DOUBLE/' Makefile.linux_opencl > Makefile.nah_opencl \
   && make -f Makefile.nah_opencl -j "$(nproc)")
fi
cd src
make yes-manybody yes-extra-fix yes-voronoi
if [ "$variant" = gpu ]; then
  make yes-gpu
  make -j "$(nproc)" serial LINKFLAGS="-O2"
  out="$repo/client/app_version/lmp_nah_stable_${VERSION}_opencl_r2"
else
  make -j "$(nproc)" serial LINKFLAGS="-O2 -static"
  out="$repo/client/app_version/lmp_nah_stable_${VERSION}_r2"
fi
# -s strips debug symbols: 93 MB -> 11 MB, same code. r2 = first stripped build (BOINC files are
# immutable under one name, so a changed binary needs a new name).
install -s -m 0755 lmp_serial "$out"
sha256sum "$out"
