#!/usr/bin/env bash
# Preview or apply this Linux Mint setup.
#
#   ./setup.sh preview [profile] [ansible options]
#   ./setup.sh apply   [profile] [ansible options]
#
# Examples:
#   ./setup.sh preview generic
#   ./setup.sh apply legion-5
#   ./setup.sh apply legion-5 --tags memory,bluetooth
set -euo pipefail

cd "$(dirname "$(readlink -f "$0")")"
export LC_ALL=C.UTF-8 PYTHONDONTWRITEBYTECODE=1

usage() {
  sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
  echo "Profiles: $(basename -s .yml profiles/*.yml | tr '\n' ' ')"
  exit "${1:-0}"
}

[ "$(id -u)" -ne 0 ] || { echo "Run as your normal user, not with sudo. It asks for your password when needed."; exit 1; }

MODE="${1:-}"
case "$MODE" in
  preview|apply) shift ;;
  -h|--help|help) usage 0 ;;
  *) usage 1 ;;
esac

PROFILE="generic"
if [ $# -gt 0 ] && [[ "$1" != -* ]]; then
  PROFILE="$1"
  shift
fi
[[ "$PROFILE" =~ ^[a-zA-Z0-9_-]+$ ]] && [ -f "profiles/$PROFILE.yml" ] || { echo "Unknown profile: $PROFILE"; usage 1; }

. /etc/os-release
[ "${ID:-}" = "linuxmint" ] || { echo "This setup only supports Linux Mint."; exit 1; }

if ! command -v ansible-playbook >/dev/null; then
  echo "Ansible is required. Installing it from the Ubuntu repositories."
  sudo apt-get update
  sudo apt-get install -y ansible-core
fi

ARGS=(playbook.yml -i localhost, -c local -e "@profiles/$PROFILE.yml" --ask-become-pass)

if [ "$MODE" = "preview" ]; then
  exec ansible-playbook "${ARGS[@]}" --check --diff "$@"
fi

echo "This will change the system using profile: $PROFILE"
echo "A Timeshift restore point is created first. Bluetooth devices may drop briefly."
read -r -p "Type yes to continue: " answer
[ "$answer" = "yes" ] || { echo "Cancelled."; exit 0; }
exec ansible-playbook "${ARGS[@]}" "$@"
