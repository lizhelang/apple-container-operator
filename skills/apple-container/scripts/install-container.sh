#!/bin/sh
set -u

REPO="apple/container"
START_SERVICE=1
FORCE=0
VERSION=""

usage() {
  cat <<'EOF'
Usage: install-container.sh [--force] [--no-start] [--version VERSION]

Install Apple's native container CLI from the official apple/container GitHub
release signed installer package.

Options:
  --force            Reinstall even when container already exists.
  --no-start         Do not run "container system start" after installation.
  --version VERSION  Install a specific release tag, for example 0.11.0.
  -h, --help         Show this help.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --force)
      FORCE=1
      ;;
    --no-start)
      START_SERVICE=0
      ;;
    --version)
      if [ "$#" -lt 2 ]; then
        echo "missing value for --version" >&2
        exit 2
      fi
      VERSION="$2"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "required command missing: $1" >&2
    exit 1
  fi
}

echo "Apple container installer"

ARCH=$(uname -m 2>/dev/null || echo unknown)
echo "architecture: $ARCH"
if [ "$ARCH" != "arm64" ]; then
  echo "Apple container requires an Apple silicon Mac; refusing to install on $ARCH." >&2
  exit 1
fi

if command -v sw_vers >/dev/null 2>&1; then
  MACOS_VERSION=$(sw_vers -productVersion 2>/dev/null || echo unknown)
  echo "macos: $MACOS_VERSION"
  MACOS_MAJOR=$(printf '%s\n' "$MACOS_VERSION" | sed 's/\..*//')
  case "$MACOS_MAJOR" in
    ''|*[!0-9]*)
      echo "warning: could not parse macOS major version; continuing with official installer checks"
      ;;
    *)
      if [ "$MACOS_MAJOR" -lt 26 ]; then
        echo "warning: official apple/container documentation currently calls out macOS 26 support; this host is $MACOS_VERSION"
      fi
      ;;
  esac
else
  echo "warning: sw_vers unavailable; cannot verify macOS version"
fi

if command -v container >/dev/null 2>&1 && [ "$FORCE" -ne 1 ]; then
  echo "container is already installed: $(command -v container)"
  if container --version >/dev/null 2>&1; then
    container --version
  fi
  echo "Use --force to reinstall."
  exit 0
fi

need_cmd curl
need_cmd grep
need_cmd sed
need_cmd head
need_cmd mktemp
need_cmd sudo

if [ -n "$VERSION" ]; then
  API_URL="https://api.github.com/repos/$REPO/releases/tags/$VERSION"
else
  API_URL="https://api.github.com/repos/$REPO/releases/latest"
fi

echo "fetching release metadata: $API_URL"
PKG_URL=$(curl -fsSL "$API_URL" \
  | grep '"browser_download_url":' \
  | sed -n 's/.*"browser_download_url": "\(.*installer-signed\.pkg\)".*/\1/p' \
  | head -n 1)

if [ -z "$PKG_URL" ]; then
  echo "could not find a signed installer package in release metadata" >&2
  echo "open https://github.com/$REPO/releases/latest and install the signed .pkg manually" >&2
  exit 1
fi

TMPDIR=$(mktemp -d "${TMPDIR:-/tmp}/apple-container-install.XXXXXX")
PKG_PATH="$TMPDIR/container-installer-signed.pkg"

cleanup() {
  rm -rf "$TMPDIR"
}
trap cleanup EXIT INT TERM

echo "downloading: $PKG_URL"
curl -fL "$PKG_URL" -o "$PKG_PATH"

echo "installing package with macOS installer"
sudo /usr/sbin/installer -pkg "$PKG_PATH" -target /

if ! command -v container >/dev/null 2>&1; then
  echo "installation finished but container is not in PATH; check /usr/local/bin/container" >&2
  exit 1
fi

echo "installed: $(command -v container)"
if container --version >/dev/null 2>&1; then
  container --version
fi

if [ "$START_SERVICE" -eq 1 ]; then
  echo "starting container system service"
  container system start
  if container system status >/dev/null 2>&1; then
    container system status
  else
    echo "container system status unavailable; verify with container system --help"
  fi
else
  echo "skipped service start because --no-start was supplied"
fi
