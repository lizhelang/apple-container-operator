#!/bin/sh
set -u

echo "Apple container detection"
echo "architecture: $(uname -m 2>/dev/null || echo unknown)"

if command -v sw_vers >/dev/null 2>&1; then
  echo "macos: $(sw_vers -productVersion 2>/dev/null || echo unknown)"
else
  echo "macos: sw_vers unavailable"
fi

if ! command -v container >/dev/null 2>&1; then
  echo "container: missing from PATH" >&2
  exit 1
fi

CONTAINER_PATH=$(command -v container)
echo "container_path: $CONTAINER_PATH"

if container --version >/dev/null 2>&1; then
  echo "container_version: $(container --version 2>&1 | head -n 1)"
else
  echo "container_version: unavailable; check container --help"
fi

if container system status >/dev/null 2>&1; then
  echo "container_system_status:"
  container system status 2>&1
else
  echo "container_system_status: unavailable; check container system --help"
fi
