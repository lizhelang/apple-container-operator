#!/bin/sh
set -u

REPO="lizhelang/apple-container-operator"
BRANCH="main"
TARGET=""
CHECK_ONLY=0
DRY_RUN=0
REFRESH=0

usage() {
  cat <<'EOF'
Usage: update-skill.sh [--check] [--refresh] [--dry-run] [--target DIR] [--branch NAME]

Update the apple-container skill from the upstream GitHub repository.

Default behavior:
  - If this skill is inside a git clone of apple-container-operator, run a
    fast-forward-only git update.
  - Otherwise, download the latest repository archive and replace the target
    apple-container skill directory.

Options:
  --check        Check remote revision and local state without changing files.
  --refresh      Ignore cached freshness results and check the remote now.
  --dry-run      Show what would be updated without changing files.
  --target DIR   Update this apple-container skill directory instead of the
                 directory that contains this script.
  --branch NAME  Update from a branch other than main.
  -h, --help     Show this help.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --check)
      CHECK_ONLY=1
      ;;
    --refresh)
      REFRESH=1
      ;;
    --dry-run)
      DRY_RUN=1
      ;;
    --target)
      if [ "$#" -lt 2 ]; then
        echo "missing value for --target" >&2
        exit 2
      fi
      TARGET="$2"
      shift
      ;;
    --branch)
      if [ "$#" -lt 2 ]; then
        echo "missing value for --branch" >&2
        exit 2
      fi
      BRANCH="$2"
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

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SKILL_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
if [ -n "$TARGET" ]; then
  SKILL_DIR=$(CDPATH= cd -- "$TARGET" && pwd)
fi

if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
  echo "target is not an apple-container skill directory: $SKILL_DIR" >&2
  exit 1
fi

REPO_ROOT=$(CDPATH= cd -- "$SKILL_DIR/../.." && pwd)

echo "Apple Container Operator skill updater"
echo "target: $SKILL_DIR"
echo "branch: $BRANCH"

ttl_seconds() {
  value=${APPLE_CONTAINER_CHECK_TTL_SECONDS:-86400}
  case "$value" in
    ''|*[!0-9]*)
      echo 86400
      ;;
    *)
      echo "$value"
      ;;
  esac
}

cache_dir() {
  if [ -n "${APPLE_CONTAINER_CHECK_CACHE_DIR:-}" ]; then
    printf '%s\n' "$APPLE_CONTAINER_CHECK_CACHE_DIR"
  elif [ -n "${XDG_CACHE_HOME:-}" ]; then
    printf '%s\n' "$XDG_CACHE_HOME/apple-container-operator"
  else
    printf '%s\n' "$HOME/.cache/apple-container-operator"
  fi
}

cache_key() {
  printf '%s\n' "$1" | sed 's/[^A-Za-z0-9._-]/_/g'
}

file_mtime() {
  if stat -f %m "$1" >/dev/null 2>&1; then
    stat -f %m "$1"
  else
    stat -c %Y "$1" 2>/dev/null || echo 0
  fi
}

cache_is_fresh() {
  file=$1
  ttl=$(ttl_seconds)
  if [ "$REFRESH" -eq 1 ] || [ "$ttl" -eq 0 ] || [ ! -f "$file" ]; then
    return 1
  fi
  now=$(date +%s)
  mtime=$(file_mtime "$file")
  age=$((now - mtime))
  [ "$age" -ge 0 ] && [ "$age" -lt "$ttl" ]
}

remote_cache_file() {
  dir=$(cache_dir)
  key=$(cache_key "$REPO-$BRANCH-remote-revision")
  printf '%s/%s\n' "$dir" "$key"
}

remote_revision() {
  cache_file=$(remote_cache_file)
  if { [ "$CHECK_ONLY" -eq 1 ] || [ "$DRY_RUN" -eq 1 ]; } && cache_is_fresh "$cache_file"; then
    echo "freshness_cache: hit"
    cat "$cache_file"
    return 0
  fi

  need_cmd curl
  remote=$(curl -fsSL "https://api.github.com/repos/$REPO/commits/$BRANCH" \
    | sed -n 's/.*"sha": "\([0-9a-f][0-9a-f]*\)".*/\1/p' \
    | head -n 1)
  if [ -n "$remote" ]; then
    mkdir -p "$(dirname "$cache_file")" 2>/dev/null || true
    printf '%s\n' "$remote" > "$cache_file" 2>/dev/null || true
  fi
  if [ "$CHECK_ONLY" -eq 1 ] || [ "$DRY_RUN" -eq 1 ]; then
    echo "freshness_cache: miss"
  fi
  printf '%s\n' "$remote"
}

if [ -d "$REPO_ROOT/.git" ] && [ -f "$REPO_ROOT/skills/apple-container/SKILL.md" ]; then
  need_cmd git
  echo "mode: git clone"
  (
    cd "$REPO_ROOT" || exit 1
    current=$(git rev-parse HEAD 2>/dev/null || echo unknown)
    echo "current_revision: $current"
    if [ "$CHECK_ONLY" -eq 1 ] || [ "$DRY_RUN" -eq 1 ]; then
      remote_output=$(remote_revision)
      printf '%s\n' "$remote_output" | sed -n '/^freshness_cache:/p'
      remote=$(printf '%s\n' "$remote_output" | sed -n '/^freshness_cache:/!p' | tail -n 1)
      echo "remote_revision: $remote"
      if [ "$current" = "$remote" ]; then
        echo "status: up to date"
      else
        echo "status: update available"
      fi
      exit 0
    fi
    git pull --ff-only origin "$BRANCH"
  )
  exit $?
fi

echo "mode: copied skill directory"
MARKER="$SKILL_DIR/.apple-container-source-revision"
if [ -f "$MARKER" ]; then
  echo "current_revision: $(cat "$MARKER")"
else
  echo "current_revision: unknown"
fi

REMOTE_OUTPUT=$(remote_revision)
printf '%s\n' "$REMOTE_OUTPUT" | sed -n '/^freshness_cache:/p'
REMOTE_REVISION=$(printf '%s\n' "$REMOTE_OUTPUT" | sed -n '/^freshness_cache:/!p' | tail -n 1)
if [ -z "$REMOTE_REVISION" ]; then
  echo "could not resolve remote revision" >&2
  exit 1
fi
echo "remote_revision: $REMOTE_REVISION"

if [ "$CHECK_ONLY" -eq 1 ]; then
  if [ -f "$MARKER" ] && [ "$(cat "$MARKER")" = "$REMOTE_REVISION" ]; then
    echo "status: up to date"
  else
    echo "status: update available"
  fi
  exit 0
fi

if [ "$DRY_RUN" -eq 1 ]; then
  echo "dry_run: would download and replace $SKILL_DIR from $REPO@$BRANCH"
  exit 0
fi

need_cmd tar
need_cmd rsync
need_cmd mktemp

TMPDIR=$(mktemp -d "${TMPDIR:-/tmp}/apple-container-skill-update.XXXXXX")
cleanup() {
  rm -rf "$TMPDIR"
}
trap cleanup EXIT INT TERM

ARCHIVE="$TMPDIR/source.tar.gz"
URL="https://github.com/$REPO/archive/refs/heads/$BRANCH.tar.gz"
echo "downloading: $URL"
curl -fL "$URL" -o "$ARCHIVE"
tar -xzf "$ARCHIVE" -C "$TMPDIR"

SOURCE_DIR=$(find "$TMPDIR" -maxdepth 2 -type d -path "*/skills/apple-container" | head -n 1)
if [ -z "$SOURCE_DIR" ] || [ ! -f "$SOURCE_DIR/SKILL.md" ]; then
  echo "downloaded archive does not contain skills/apple-container" >&2
  exit 1
fi

rsync -a --delete "$SOURCE_DIR/" "$SKILL_DIR/"
printf '%s\n' "$REMOTE_REVISION" > "$MARKER"
echo "status: updated"
