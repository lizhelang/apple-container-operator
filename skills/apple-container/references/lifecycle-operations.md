# Lifecycle Operations

## First-Time Environment Check

1. Run `scripts/detect-container.sh`.
2. If missing and the user asked to install, run `scripts/install-container.sh`; otherwise explain that Apple container must be installed before runtime operations.
3. Check architecture and macOS version.
4. Run `container --help` and relevant subcommand help.

## Start Container System Service

1. Check `container system --help`.
2. If `start` exists, use `container system start`.
3. Check status only with documented status or safe diagnostics.

## Pull And Run Image

1. Verify image pull syntax.
2. Pull the exact image tag when supplied.
3. Verify `container run --help`.
4. Include only supported options for name, env, ports, mounts, workdir, and command.

## List Containers

Use the documented list command. Verify whether stopped containers require an additional flag.

## View Logs

Use the documented logs command for an explicit container. Verify follow, tail, and timestamp flags before use.

## Exec Into Container

Use exec only for an explicitly named running container. Verify interactive/TTY support before using shell-style `-it`.

## Stop, Restart, Delete

Stop and restart are acceptable for explicit targets. Delete requires confirmation, especially if the container may hold local state.

## Clean Up Safely

Produce a cleanup plan before running any prune/delete command. State the target scope, what will be removed, and what will not be touched.

## Update Image And Recreate Container

1. Inspect or reconstruct current configuration.
2. Pull the new image tag.
3. Warn if the service is stateful.
4. Stop the old container only after confirmation when needed.
5. Recreate with preserved name, ports, env, mounts, command, and workdir.
