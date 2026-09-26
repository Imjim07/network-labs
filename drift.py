#!/usr/bin/env python3
"""Compare the two most recent backups for each device and report what changed."""

import difflib
import string
import sys
from collections import defaultdict
from pathlib import Path

BACKUP_DIR = Path("backups")
B64_CHARS = set(string.ascii_letters + string.digits + "+/=")


def is_noise(line):
    """True for encrypted values and certificate blobs that differ on every rebuild."""
    stripped = line.strip()
    if "$aes1$" in line:
        return True
    if len(stripped) > 60 and set(stripped) <= B64_CHARS:
        return True
    return False


def clean(path):
    """Read a backup, dropping lines that are noise rather than configuration."""
    return [line for line in path.read_text().splitlines() if not is_noise(line)]


def group_by_device():
    """Return {device: [paths, oldest first]}."""
    groups = defaultdict(list)
    for path in BACKUP_DIR.glob("*.cfg"):
        device = path.stem.rsplit("_", 2)[0]
        groups[device].append(path)
    for paths in groups.values():
        paths.sort()
    return groups


def main():
    groups = group_by_device()
    if not groups:
        print(f"No backups found in {BACKUP_DIR}/")
        return 0

    changed = 0

    for device, paths in sorted(groups.items()):
        if len(paths) < 2:
            print(f"{device}: only one backup, nothing to compare")
            continue

        old, new = paths[-2], paths[-1]
        diff = list(difflib.unified_diff(
            clean(old), clean(new),
            fromfile=old.name, tofile=new.name, lineterm="", n=1,
        ))

        if not diff:
            print(f"{device}: no change")
            continue

        changed += 1
        print(f"\n{device}: DRIFT DETECTED")
        for line in diff:
            print(f"  {line}")

    print(f"\n{changed} device(s) changed.")
    return 1 if changed else 0


if __name__ == "__main__":
    sys.exit(main())
