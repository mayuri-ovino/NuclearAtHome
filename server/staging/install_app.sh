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
v=apps/nuclear_cascade/1.0/x86_64-pc-linux-gnu
mkdir -p "$v"
cp "$src/client/app_version/wrapper_26018_x86_64-pc-linux-gnu" "$src/client/app_version/lmp_nah_stable_29Aug2024" \
   "$src/client/app_version/version.xml" "$v/"
cp "$src/client/job.xml" "$v/job_nah_cascade_1.xml"
# GPU version (OpenCL, core 0xa2), if it has been built: bash client/build_lammps.sh <dir> gpu
g=apps/nuclear_cascade/1.01/x86_64-pc-linux-gnu__opencl_nvidia_101  # 1.01: neigh no (1.0 crashed)
if [ -f "$src/client/app_version/lmp_nah_stable_29Aug2024_opencl" ]; then
  mkdir -p "$g"
  cp "$src/client/app_version/wrapper_26018_x86_64-pc-linux-gnu" "$src/client/app_version/lmp_nah_stable_29Aug2024_opencl" "$g/"
  cp "$src/client/app_version/version_opencl.xml" "$g/version.xml"
  cp "$src/client/job_opencl.xml" "$g/job_nah_cascade_opencl_2.xml"
fi
cp "$src/server/boinc/nah_cascade_in" "$src/server/boinc/nah_cascade_out" templates/
cp "$src/server/boinc/bin/"nah_* bin/
python3 "$src/server/staging/add_app.py" .
bin/xadd
bin/update_versions < <(yes)  # plain "yes |" fails under pipefail (SIGPIPE)
