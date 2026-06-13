# Compose-Like Services

Compose-like requests should be decomposed into service plans where possible. Full Docker Compose parity is not guaranteed.

Example request:

```text
Run a web app with redis and postgres like compose.
```

Agent response shape:

1. Identify services: `web`, `redis`, `postgres`.
2. Capture image/build context, ports, env vars, mounts, dependencies, and commands.
3. Verify Apple container support for each required flag.
4. Warn about stateful services and persistent data.
5. Produce an ordered plan:

```text
1. Pull redis image.
2. Pull postgres image and plan persistence.
3. Build or pull web image if supported.
4. Run postgres with verified env and port settings.
5. Run redis.
6. Run web with verified env and port settings.
```

If networks, volumes, build options, or dependency semantics do not map directly, document the limitation and suggest a manual workaround.
