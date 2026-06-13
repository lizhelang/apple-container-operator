# Installation

Use this file when the user asks to install, set up, upgrade, or repair Apple container.

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

1. Check whether `container` already exists.
2. If installed, print path and version. Ask before reinstalling, downgrading, or upgrading.
3. Check architecture and macOS version.
4. Download the latest signed installer package from `https://github.com/apple/container/releases/latest`.
5. Install the package with `/usr/sbin/installer`.
6. Run `container --version`.
7. Start the system service with `container system start` unless the user requested otherwise.
8. Verify with `container system status` if available.

## Script

Use:

```sh
skills/apple-container/scripts/install-container.sh
```

Options:

- `--force` - reinstall even when `container` already exists.
- `--no-start` - install but do not start the system service.
- `--version VERSION` - install a specific GitHub release tag such as `0.11.0`.

## Fallbacks

If download, installation, or service start fails, report the exact failing command and recommend manual installation from the official release page. Do not install Docker Desktop as a substitute.
