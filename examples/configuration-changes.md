# Configuration Change Examples

## Change App Port From 3000 To 8080

Intent: `configuration_change`.

Plan:

1. Inspect current `app` configuration if supported.
2. Verify `container run --help` for port syntax.
3. Preserve image, name, env vars, mounts, command, and working directory.
4. Recreate only after confirming any stop/delete step.

Tentative plan:

```sh
container logs app
container stop app
container delete app
container run --name app -p 8080:3000 IMAGE COMMAND
```

The delete/recreate steps require confirmation and a state warning.

## Change Postgres Password

Environment changes usually require recreate. Warn that changing `POSTGRES_PASSWORD` may not update an existing database initialized with a previous password.

## Change Image Tag

Pull the new tag, preserve current settings, and recreate. Warn about mutable tags such as `latest`.
