# Troubleshooting

Use read-only diagnostics before modifying anything.

## Structured Sequence

1. Check system.
2. Check image.
3. Check container list/status.
4. Check logs.
5. Check command and configuration.
6. Check ports and mounts.
7. Suggest minimal reproduction.

## CLI Not Installed

Run `command -v container`. If missing, explain that Apple container is required and do not substitute Docker Desktop.

## Unsupported macOS Or Non-Apple-Silicon Environment

Report `uname -m` and `sw_vers` when available. Do not assume unsupported permanently; advise checking current Apple container requirements.

## System Service Not Started

Run `container system --help`, then use documented status/start commands.

## Image Pull Failure

Check image name, tag, registry authentication, network access, and registry availability.

## Container Exits Immediately

List containers including stopped containers if supported, then read logs and check command/entrypoint.

## Port Not Reachable

Verify port mapping support, host port conflicts, service bind address inside the container, and firewall/network settings.

## Env Var Missing

Inspect or reconstruct run configuration. Confirm env flag syntax and whether the app reads the expected variable name.

## Volume Or Path Issue

Check host path existence and permissions. Warn before creating or deleting data paths.

## Shell Or Exec Fails

Verify the container is running and the shell exists. Try `sh` if `bash` is unavailable.

## Command Or Entrypoint Issue

Compare intended command with image defaults. Recreate only after preserving configuration and confirming destructive steps.

## Networking Issue

Check ports, service bind address, DNS/registry access, and whether Docker network assumptions were carried over.

## Permissions Issue

Check host file permissions, mount paths, and runtime restrictions. Avoid broad `chmod` or ownership changes without explicit approval.
