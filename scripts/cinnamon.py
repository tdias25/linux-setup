#!/usr/bin/env python3
"""Change Cinnamon settings only when needed, without replacing existing shortcuts.

  cinnamon.py set SCHEMA KEY VALUE [--dry-run]
  cinnamon.py shortcut NAME BINDING COMMAND [--dry-run]

Prints CHANGED, OK or WARN.
"""
import ast
import subprocess
import sys

BASE = "org.cinnamon.desktop.keybindings"
PATH = "/org/cinnamon/desktop/keybindings/custom-keybindings"


def get(schema, key):
    return subprocess.run(["gsettings", "get", schema, key], check=True,
                          capture_output=True, text=True).stdout.strip()


def put(schema, key, value):
    subprocess.run(["gsettings", "set", schema, key, value], check=True)


def quote(text):
    return "'" + text.replace("\\", "\\\\").replace("'", "\\'") + "'"


def parse(value):
    return ast.literal_eval(value.removeprefix("@as ").strip())


def entry_schema(name):
    return f"{BASE}.custom-keybinding:{PATH}/{name}/"


def set_value(schema, key, value, dry_run):
    if get(schema, key) == value:
        print("OK")
        return
    if not dry_run:
        put(schema, key, value)
    print("CHANGED")


def set_shortcut(label, binding, command, dry_run):
    names = parse(get(BASE, "custom-list"))
    entries = {name: {
        "name": parse(get(entry_schema(name), "name")),
        "command": parse(get(entry_schema(name), "command")),
        "binding": parse(get(entry_schema(name), "binding")),
    } for name in names}

    for name, entry in entries.items():
        if binding in entry["binding"] and entry["name"] != label:
            print(f"WARN: {binding} is already used by '{entry['name']}'. Left unchanged.")
            return

    target = next((name for name, entry in entries.items() if entry["name"] == label), None)
    if target and entries[target]["command"] == command and entries[target]["binding"] == [binding]:
        print("OK")
        return
    if dry_run:
        print("CHANGED")
        return

    if target is None:
        number = 0
        while f"custom{number}" in names:
            number += 1
        target = f"custom{number}"

    schema = entry_schema(target)
    put(schema, "name", quote(label))
    put(schema, "command", quote(command))
    put(schema, "binding", "[" + quote(binding) + "]")
    if target not in names:
        put(BASE, "custom-list", "[" + ", ".join(quote(name) for name in names + [target]) + "]")
    print("CHANGED")


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [arg for arg in args if arg != "--dry-run"]
    if len(args) == 4 and args[0] == "set":
        set_value(args[1], args[2], args[3], dry_run)
    elif len(args) == 4 and args[0] == "shortcut":
        set_shortcut(args[1], args[2], args[3], dry_run)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
