# Conservative Command Map

Apple container evolves. Verify exact syntax with local help before using flags not already proven by this repository.

## Help And Version

- `container --help` - safe first check.
- `container <subcommand> --help` - safe subcommand check.
- `container --version` - use if available; otherwise verify version support through `container --help`.

## System

- `container system start` - start the system service when supported.
- `container system stop` - stop the system service; confirm if this affects running work.
- `container system status` - use if available. If not available, run `container system --help` and use the documented status or diagnostic command.

## Images

- Pull image: `container image pull IMAGE` or nearest documented pull command. Verify with `container image --help` and `container image pull --help`.
- List images: `container image list` or nearest documented list command. Verify with help.
- Delete image: `container image delete IMAGE` or nearest documented delete/remove command. Requires confirmation.

## Containers

- Run: `container run ... IMAGE [COMMAND...]`. Verify each flag with `container run --help`.
- List: `container list` or nearest documented list command. Verify whether stopped containers need an extra flag.
- Logs: `container logs NAME`. Verify follow/tail flags before use.
- Exec: `container exec NAME COMMAND...`. Verify interactive/TTY flags before use.
- Stop: `container stop NAME`. Use only for explicit targets unless confirmed.
- Restart: `container restart NAME` if available; otherwise plan stop/start with help-verified commands.
- Delete: `container delete NAME` or nearest documented remove command. Requires confirmation.

## Uncertain Flags

Mark ports, env vars, volumes, names, working directory, entrypoint, platform, resources, detach/background, and restart policy flags as "verify with help before use" until tests or local docs prove exact support.
