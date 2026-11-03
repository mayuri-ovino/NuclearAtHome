#!/usr/bin/env bash
# Runs INSIDE the official makeproject container (which holds the staging signing key):
# copies our app version, templates and script wrappers into the shared project volume,
# registers the app and daemons, then signs the app files with BOINC's update_versions.
set -euo pipefail
src=/opt/nuclear-at-home
# Like the official makeproject-step2.sh: make $PROJECT_ROOT the shared volume, or BOINC's tools
# write download/ files into this throwaway container instead of the project.
rm -rf "$PROJECT_ROOT" && ln -s "$PROJECT_ROOT.dst" "$PROJECT_ROOT"
cd "$PROJECT_ROOT"
# App versions. 1.03: stripped Linux builds and gzipped downloads; 1.04 (GPU): NVIDIA device chosen
# explicitly, not Intel's integrated GPU. Earlier versions stay in the database for tasks already
# sent. Each is installed if its binary has been built.
a="$src/client/app_version"
install_version() {  # <app version> <dir> <version.xml> <job.xml> <job physical name> <files...>
  local dir=apps/nuclear_cascade/$1/$2 version=$3 job=$4 job_name=$5; shift 5
  for f in "$@"; do [ -f "$a/$f" ] || return 0; done
  mkdir -p "$dir" && for f in "$@"; do cp "$a/$f" "$dir/"; done
  cp "$a/$version" "$dir/version.xml" && cp "$src/client/$job" "$dir/$job_name"
}
# CPU: bash client/build_lammps.sh <dir>; GPU (OpenCL, core 0xa2): ... <dir> gpu; Windows: build_lammps_windows.sh
install_version 1.03 x86_64-pc-linux-gnu version.xml job.xml job_nah_cascade_1.xml \
  wrapper_26018_x86_64-pc-linux-gnu lmp_nah_stable_29Aug2024_r2
install_version 1.04 x86_64-pc-linux-gnu__opencl_nvidia_101 version_opencl.xml job_opencl.xml job_nah_cascade_opencl_4.xml \
  wrapper_26018_x86_64-pc-linux-gnu lmp_nah_stable_29Aug2024_opencl_r2
install_version 1.03 windows_x86_64 version_windows.xml job.xml job_nah_cascade_1.xml \
  wrapper_26019_windows_x86_64.exe lmp_nah_stable_29Aug2024_windows.exe
install_version 1.04 windows_x86_64__opencl_nvidia_101 version_windows_opencl.xml job_opencl.xml job_nah_cascade_opencl_4.xml \
  wrapper_26019_windows_x86_64.exe lmp_nah_stable_29Aug2024_windows_opencl.exe
cp "$src/server/boinc/nah_cascade_in" "$src/server/boinc/nah_cascade_out" templates/
cp "$src/server/boinc/bin/"nah_* bin/
python3 "$src/server/staging/add_app.py" .
bin/xadd
bin/update_versions < <(yes)  # plain "yes |" fails under pipefail (SIGPIPE)
