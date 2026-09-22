#!/usr/bin/env python3
"""Discover running lab nodes and save each one's configuration to disk."""

import os
import subprocess
from datetime import datetime
from pathlib import Path

from netmiko import ConnectHandler

LAB_PREFIX = "clab-first-lab-"
BACKUP_DIR = Path("backups")

CREDENTIALS = {
    "device_type": "nokia_srl",
    "username": "admin",
    "password": os.environ.get("SRL_PASSWORD", "NokiaSrl1!"),
}


def docker(*args):
    """Run a docker command and return its stdout, stripped."""
    result = subprocess.run(
        ["docker", *args], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def discover_nodes():
    """Return {container_name: ip_address} for every running lab node."""
    names = docker(
        "ps", "--filter", f"name={LAB_PREFIX}", "--format", "{{.Names}}"
    ).split()

    nodes = {}
    for name in names:
        ip = docker(
            "inspect", "-f",
            "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}",
            name,
        )
        if ip:
            nodes[name] = ip
    return nodes


def fetch_config(ip):
    conn = ConnectHandler(host=ip, **CREDENTIALS)
    config = conn.send_command("info")
    conn.disconnect()
    return config


def main():
    nodes = discover_nodes()

    if not nodes:
        print(f"No running containers matching '{LAB_PREFIX}'. Is the lab deployed?")
        return

    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")

    for name, ip in nodes.items():
        print(f"connecting to {name} ({ip}) ...")
        try:
            config = fetch_config(ip)
        except Exception as error:
            print(f"  FAILED: {error}")
            continue

        path = BACKUP_DIR / f"{name}_{stamp}.cfg"
        path.write_text(config)
        print(f"  saved {len(config)} bytes to {path}")


if __name__ == "__main__":
    main()
