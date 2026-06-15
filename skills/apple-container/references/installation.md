# Installation

Use this file when the skill checks, installs, sets up, upgrades, or repairs Apple container.

## Official Source

Prefer the official `apple/container` GitHub releases. The documented initial install path is to download the latest signed installer package, install it with the macOS installer, then start the system service with:

```sh
container system start
```

## Requirements

- Apple silicon Mac. Check with `uname -m`; expected value is `arm64`.
- macOS support must be verified against current Apple container documentation and release notes. The official project currently documents macOS 26 support.
- Administrator privileges may be required by the package installer.

## Agent Workflow

1. Run `scripts/install-container.sh --check` before Apple `container` runtime operations.
2. Check whether `container` already exists.
3. If installed, print path and version, then compare with the latest official GitHub release when possible. Remote release metadata is cached for 24 hours by default; use `--refresh` only when the user explicitly asks for a latest-version check now.
4. Check architecture and macOS version.
5. If missing, or if the user asked for setup/update and a newer official release appears available, download the latest signed installer package from `https://github.com/apple/container/releases/latest`.
6. Install the package with `/usr/sbin/installer`.
7. Run `container --version`.
8. Start the system service with `container system start` unless the user requested otherwise.
9. Verify with `container system status` if available.

## Script

Use:

```sh
skills/apple-container/scripts/install-container.sh
```

Options:

- `--check` - check local installation and latest official release without installing.
- `--refresh` - ignore cached release metadata and check GitHub now.
- `--force` - reinstall even when `container` already exists.
- `--no-start` - install but do not start the system service.
- `--version VERSION` - install a specific GitHub release tag such as `0.11.0`.

## Fallbacks

If download, installation, or service start fails, report the exact failing command and recommend manual installation from the official release page. Do not install Docker Desktop as a substitute.
