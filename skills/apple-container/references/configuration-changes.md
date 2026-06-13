# Configuration Changes

Runtime configuration changes are state transition plans, not blind command rewrites.

## Common Workflow

1. Identify target container and requested change.
2. Inspect current state if possible.
3. Determine whether Apple container supports an in-place change.
4. If not, generate a recreate plan.
5. Preserve existing image, env, ports, mounts, command, workdir, and name as much as possible.
6. Warn before delete/recreate for stateful containers such as databases.

## Port Mappings

Changing ports usually requires recreate. Preserve all non-port settings and explain old-to-new mapping.

## Environment Variables

Changing env vars usually requires recreate. Preserve existing env vars unless the user asks to replace them.

## Volume Mounts

Changing mounts usually requires recreate. Verify host paths and warn before touching persistent data.

## Container Name

Renaming may require recreate unless a rename command exists. Verify help before assuming either path.

## Image Tag

Pull the new tag, then recreate using existing configuration. Warn if the tag is mutable such as `latest`.

## Command Or Entrypoint

Changing the command usually requires recreate. Preserve image and runtime configuration.

## Working Directory

Verify whether run supports a workdir flag. If not, document the limitation or adjust command only when safe.

## Resource Limits

Verify current support before using CPU, memory, or platform flags. If unsupported, document the limitation.

## Restart Or Background Behavior

Verify detach/background and restart-policy support before using them. If unsupported, explain how the user can manually start the service.
