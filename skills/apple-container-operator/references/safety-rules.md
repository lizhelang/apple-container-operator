# Safety Rules

## Directly Allowed Without Confirmation

- Help.
- Version.
- List.
- Status.
- Logs.
- Inspect, if available.

## Usually Allowed

- Pull an explicitly named image.
- Run a new container when it does not replace existing state.
- Exec into an explicitly named container.
- Install Apple container when the user explicitly requested installation or setup.

## Require Confirmation

- Delete container.
- Delete image.
- Prune or cleanup.
- Stop all containers.
- Delete data.
- Recreate a stateful service.
- Any operation affecting multiple targets.

## Strong Confirmation

Require especially clear confirmation for:

- Deleting volumes or persistent data.
- Removing persistent database state.
- Uninstalling Apple container.
- System-wide cleanup.

## Installation Safety

Installing Apple container uses the macOS package installer and may ask for an administrator password. Use only the official `apple/container` release package unless the user explicitly chooses another source. Ask before reinstalling, downgrading, or upgrading an existing installation.

## Confirmation Content

State the exact target, expected effect, likely data impact, and a safe alternative when available.
