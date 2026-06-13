# Natural Language Examples

## "帮我跑一个 postgres，密码设成 pass，端口暴露到本机"

Intent: `run_container`.

Agent response shape:

1. Explain that this is a stateful database and persistence should be planned before delete/recreate.
2. Run or suggest `container run --help` to verify env and port flags.
3. Produce a command only with verified flags, tentatively:

```sh
container run --name postgres -e POSTGRES_PASSWORD=pass -p 5432:5432 postgres
```

4. Mark `--name`, `-e`, and `-p` as help-verified requirements if not already checked.

## "帮我安装 Apple container"

Intent: `install_container`.

Agent response shape:

1. Check whether `container` already exists.
2. Verify Apple silicon and macOS version.
3. Run the official installer helper:

```sh
skills/apple-container/scripts/install-container.sh
```

4. Verify `container --version` and start/status output.

## "看一下 app 为什么挂了"

Intent: `debug_failure`.

Start with read-only checks: system status, list containers, logs for `app`, then command/configuration, ports, and mounts.

## "进入 redis 容器看一下"

Intent: `exec_shell`.

Verify exec and interactive support:

```sh
container exec --help
container exec redis sh
```

Use `sh` before assuming `bash` exists.

## "把 app 的端口从 3000 改成 8080"

Intent: `configuration_change`.

Inspect current state, decide whether in-place change is supported, otherwise produce a stop/recreate plan preserving image, env, mounts, command, and name.

## "清理不用的容器"

Intent: `cleanup`.

Do not immediately prune. List candidates, explain what would be removed, and ask for confirmation before deletion.
