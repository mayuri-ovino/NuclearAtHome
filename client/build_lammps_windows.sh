#!/usr/bin/env bash
# Build the Windows x86_64 LAMMPS binary shipped to volunteers (serial, static, core 0xa1),
# cross-compiled with MinGW-w64 inside a Debian container, so the build host needs only Docker.
# Same LAMMPS release and packages as client/build_lammps.sh (MANYBODY, EXTRA-FIX, VORONOI);
# LAMMPS's CMake build, because the traditional make build has no Windows cross target.
# LAMMPS is GPL-2: publish this script and the exact source tarball with every release.
#
# Usage: bash client/build_lammps_windows.sh [work_dir]
set -euo pipefail

VERSION="29Aug2024"
URL="https://download.lammps.org/tars/lammps-${VERSION}.tar.gz"
# Matches https://download.lammps.org/tars/SHA256SUMS (checked 2026-11-01).
SHA256="7d39c788ab808494c334a07e6b3fe2f3e01359f5741bf8e4b48842f262e1687c"
IMAGE="debian:bookworm-20241016"

repo="$(cd "$(dirname "$0")/.." && pwd)"
work="${1:-$(mktemp -d)}"
mkdir -p "$work" && work="$(cd "$work" && pwd)"
[ -f "$work/lammps.tar.gz" ] || curl -fsSL "$URL" -o "$work/lammps.tar.gz"
echo "${SHA256}  $work/lammps.tar.gz" | sha256sum -c -

cat > "$work/mingw.cmake" <<'CMAKE'
set(CMAKE_SYSTEM_NAME Windows)
set(CMAKE_SYSTEM_PROCESSOR x86_64)
set(CMAKE_C_COMPILER x86_64-w64-mingw32-gcc-posix)
set(CMAKE_CXX_COMPILER x86_64-w64-mingw32-g++-posix)
set(CMAKE_RC_COMPILER x86_64-w64-mingw32-windres)
set(CMAKE_FIND_ROOT_PATH /usr/x86_64-w64-mingw32)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
CMAKE

cat > "$work/build.sh" <<'BUILD'
set -euo pipefail
apt-get update -qq && apt-get install -y -qq --no-install-recommends mingw-w64 cmake make patch python3 curl ca-certificates >/dev/null
# voro++'s own Makefile calls plain ar/ranlib: point them at the MinGW tools (container only).
ln -sf /usr/bin/x86_64-w64-mingw32-ar /usr/local/bin/ar && ln -sf /usr/bin/x86_64-w64-mingw32-ranlib /usr/local/bin/ranlib
cd /work && rm -rf src build && mkdir src build && tar -xzf lammps.tar.gz -C src --strip-components=1
cd build
# Serial (no MPI, no OpenMP), static runtime: the .exe needs no DLLs on the volunteer's machine.
# voro++ is downloaded by LAMMPS's own CMake, which checks its checksum.
cmake ../src/cmake -DCMAKE_TOOLCHAIN_FILE=/work/mingw.cmake -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_MPI=off -DBUILD_OMP=off -DBUILD_SHARED_LIBS=off -DLAMMPS_EXCEPTIONS=on \
  -DPKG_MANYBODY=on -DPKG_EXTRA-FIX=on -DPKG_VORONOI=on -DDOWNLOAD_VORO=on \
  -DCMAKE_EXE_LINKER_FLAGS="-static -static-libgcc -static-libstdc++" >/dev/null
make -j "$(nproc)" lmp
x86_64-w64-mingw32-strip lmp.exe
BUILD

docker run --rm -v "$work:/work" "$IMAGE" bash /work/build.sh
out="$repo/client/app_version/lmp_nah_stable_${VERSION}_windows.exe"
install -m 0755 "$work/build/lmp.exe" "$out"
sha256sum "$out"
