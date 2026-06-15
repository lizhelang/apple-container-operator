#!/bin/sh
set -u

run_safe() {
  echo
  echo "$ $*"
  "$@" 2>&1 || echo "command unavailable or failed: $*"
}

echo "Apple container read-only state inspection"
echo "architecture: $(uname -m 2>/dev/null || echo unknown)"

if command -v sw_vers >/dev/null 2>&1; then
  echo "macos: $(sw_vers -productVersion 2>/dev/null || echo unknown)"
fi

if ! command -v container >/dev/null 2>&1; then
  echo "container: missing from PATH" >&2
  exit 1
fi

echo "container_path: $(command -v container)"

run_safe container --help
run_safe container system --help
run_safe container image --help

if container --version >/dev/null 2>&1; then
  run_safe container --version
fi

if container system status >/dev/null 2>&1; then
  run_safe container system status
fi

if container list >/dev/null 2>&1; then
  run_safe container list
fi

if container image list >/dev/null 2>&1; then
  run_safe container image list
fi
