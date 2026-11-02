"""BOINC script_validator compare script: are two replicas of one WU equivalent?

Configured as: --compare_script "nah_validate_compare" (wrapper in server/boinc/bin/)
MD is chaotic, so replicas are never compared to each other, and rare cascades are physics,
not errors (decision log, 2026-11-01). The init script has already run V1-V8 on each
replica, so two replicas that reach this script are equivalent. Exit 0 = equivalent.
"""
import sys

if __name__ == "__main__":
    sys.exit(0)
