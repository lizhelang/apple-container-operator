# Troubleshooting Example

User: "this container will not start, debug it"

Agent flow:

1. Check `container` exists:

```sh
command -v container
container --help
```

2. Check system service:

```sh
container system --help
container system status
```

3. Check image and container state:

```sh
container image list
container list
```

4. Read logs:

```sh
container logs NAME
```

5. Review command, env, ports, and mounts.
6. Suggest a minimal reproduction with the smallest image and command that demonstrates the failure.

Do not stop, delete, or recreate during diagnostics unless the user approves that specific action.
