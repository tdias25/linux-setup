#!/usr/bin/env python3
"""Print read-only facts about this machine as JSON."""
import glob
import json
import os
import shutil
import subprocess


def run(*cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def read(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as handle:
            return handle.read().strip()
    except OSError:
        return ""


def os_release():
    values = {}
    for line in read("/etc/os-release").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value.strip('"')
    return values


def has_nvidia_gpu():
    for device in glob.glob("/sys/bus/pci/devices/*"):
        if read(f"{device}/vendor") == "0x10de" and read(f"{device}/class").startswith("0x03"):
            return True
    return False


release = os_release()
conservation = glob.glob("/sys/bus/platform/devices/VPC2004:*/conservation_mode")

print(json.dumps({
    "distro": release.get("ID", ""),
    "ubuntu_codename": release.get("UBUNTU_CODENAME", ""),
    "nvidia_gpu": has_nvidia_gpu(),
    "secure_boot": "enabled" in run("mokutil", "--sb-state").lower(),
    "root_fstype": run("findmnt", "-no", "FSTYPE", "/"),
    "root_source": run("findmnt", "-no", "SOURCE", "/"),
    "bluetooth": bool(glob.glob("/sys/class/bluetooth/hci*")),
    "conservation_path": conservation[0] if conservation else "",
    "brave": shutil.which("brave-browser") is not None,
    "cinnamon": "cinnamon" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower(),
}))
