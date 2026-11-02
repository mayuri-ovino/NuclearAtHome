#!/usr/bin/env bash
# Build the Windows x86_64 LAMMPS binaries shipped to volunteers (serial, static), cross-compiled with MinGW-w64 inside a Debian container, so the build host needs only Docker.
# Same LAMMPS release and packages as client/build_lammps.sh (MANYBODY, EXTRA-FIX, VORONOI);
# LAMMPS's CMake build, because the traditional make build has no Windows cross target.
# LAMMPS is GPL-2: publish this script and the exact source tarball with every release.
#
#   cpu (default): core 0xa1
#   gpu:           GPU package over OpenCL, full double precision, core 0xa2. LAMMPS's own static
#                  OpenCL loader is linked in; the OpenCL driver itself comes with the GPU driver.
#
# Usage: bash client/build_lammps_windows.sh [work_dir] [cpu|gpu]
set -euo pipefail

VERSION="29Aug2024"
URL="https://download.lammps.org/tars/lammps-${VERSION}.tar.gz"
# Matches https://download.lammps.org/tars/SHA256SUMS (checked 2026-11-01).
SHA256="7d39c788ab808494c334a07e6b3fe2f3e01359f5741bf8e4b48842f262e1687c"
IMAGE="debian:bookworm-20241016"

repo="$(cd "$(dirname "$0")/.." && pwd)"
work="${1:-$(mktemp -d)}"
variant="${2:-cpu}"
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
# voro++'s own Makefile calls plain ar/ranlib: point them at the MinGW tools (container only).
ln -sf /usr/bin/x86_64-w64-mingw32-ar /usr/local/bin/ar && ln -sf /usr/bin/x86_64-w64-mingw32-ranlib /usr/local/bin/ranlib
cd /work && rm -rf src "build_$VARIANT" && mkdir src "build_$VARIANT" && tar -xzf lammps.tar.gz -C src --strip-components=1
cd "build_$VARIANT"
# Double precision like the Linux GPU build: the GPU must pass the same energy check as the CPU.
# The OpenCL loader source is downloaded by LAMMPS's own CMake, which checks its checksum.
gpu_flags=""
[ "$VARIANT" = gpu ] && gpu_flags="-DPKG_GPU=on -DGPU_API=opencl -DGPU_PREC=double -DUSE_STATIC_OPENCL_LOADER=yes"
# Serial (no MPI, no OpenMP), static runtime: the .exe needs no DLLs on the volunteer's machine.
# voro++ is downloaded by LAMMPS's own CMake, which checks its checksum.
cmake ../src/cmake -DCMAKE_TOOLCHAIN_FILE=/work/mingw.cmake -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_MPI=off -DBUILD_OMP=off -DBUILD_SHARED_LIBS=off -DLAMMPS_EXCEPTIONS=on \
  -DPKG_MANYBODY=on -DPKG_EXTRA-FIX=on -DPKG_VORONOI=on -DDOWNLOAD_VORO=on $gpu_flags \
  -DCMAKE_EXE_LINKER_FLAGS="-static -static-libgcc -static-libstdc++" >/dev/null
make -j "$(nproc)" lmp
x86_64-w64-mingw32-strip lmp.exe
BUILD

# Build tools are installed once into a local image (apt with timeouts and retries: a stalled
# mirror connection once hung a build), so later builds skip the download.
builder="nah-lammps-mingw:${IMAGE#debian:}"
docker image inspect "$builder" >/dev/null 2>&1 || docker build -q -t "$builder" - <<DOCKER
FROM $IMAGE
RUN apt-get -o Acquire::http::Timeout=30 -o Acquire::Retries=5 update -qq \\
 && apt-get -o Acquire::http::Timeout=30 -o Acquire::Retries=5 install -y -qq --no-install-recommends \\
    mingw-w64 cmake make patch python3 curl ca-certificates \\
 && rm -rf /var/lib/apt/lists/*
DOCKER
docker run --rm -e VARIANT="$variant" -v "$work:/work" "$builder" bash /work/build.sh
if [ "$variant" = gpu ]; then
  out="$repo/client/app_version/lmp_nah_stable_${VERSION}_windows_opencl.exe"
else
  out="$repo/client/app_version/lmp_nah_stable_${VERSION}_windows.exe"
fi
install -m 0755 "$work/build_$variant/lmp.exe" "$out"
sha256sum "$out"
