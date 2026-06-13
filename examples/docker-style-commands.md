# Docker-Style Command Examples

Docker-style input is translated as intent for Apple container.

## `docker ps`

Intent: `list_containers`.

Tentative Apple workflow:

```sh
container list
```

Verify exact list support with `container --help`.

## `docker logs -f app`

Intent: `view_logs`.

Tentative Apple workflow:

```sh
container logs --help
container logs app
```

Use follow mode only if documented by local help.

## `docker exec -it app sh`

Intent: `exec_shell`.

Tentative Apple workflow:

```sh
container exec --help
container exec app sh
```

TTY flags must be verified before use.

## `docker run --name redis -p 6379:6379 redis`

Intent: `run_container`.

Tentative Apple workflow:

```sh
container run --help
container run --name redis -p 6379:6379 redis
```

Name and port flags must be verified before use.

## `docker compose up`

Intent: `compose_like_service`.

Ask for the compose file or service definitions, then decompose into explicit service plans. Do not claim full Compose parity.
