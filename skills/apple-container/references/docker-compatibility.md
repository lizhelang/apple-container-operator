# Docker Compatibility Notes

Docker-style commands are intent language. They are not proof that Apple container accepts the same flags.

| Docker input | Intent | Apple container workflow | Unsupported or uncertain | Fallback guidance |
| --- | --- | --- | --- | --- |
| `docker ps` | `list_containers` | list containers with documented Apple command | `-a`, filters, format | verify list help |
| `docker images` | `list_images` | list images with documented Apple image command | filters, format | verify image list help |
| `docker pull IMAGE` | `pull_image` | pull image | registry auth details | verify image pull help |
| `docker run IMAGE` | `run_container` | run image | detach, platform, resources | verify run help |
| `docker run --name redis -p 6379:6379 redis` | `run_container` | run named container with port mapping if supported | exact name and port flags | if unsupported, document manual alternative |
| `docker run -e KEY=VALUE IMAGE` | `run_container` | run with env if supported | env flag syntax | verify run help |
| `docker logs NAME` | `view_logs` | read logs | tail/since formatting | verify logs help |
| `docker logs -f NAME` | `view_logs` | follow logs if supported | follow flag | otherwise repeat logs manually |
| `docker exec -it NAME sh` | `exec_shell` | exec shell if supported | TTY/interactive flags | run non-interactive shell command if TTY unsupported |
| `docker stop NAME` | `stop_container` | stop named container | timeout flag | use default stop |
| `docker rm NAME` | `delete_container` | delete named container | force flag, volumes | confirm and warn on data |
| `docker rmi IMAGE` | `delete_image` | delete image | force/no-prune | confirm first |
| `docker build -t NAME .` | `docker_translation` | build if Apple container supports build | build context, Dockerfile flags | otherwise use compatible external build tool and load/pull OCI image |
| `docker compose up` | `compose_like_service` | decompose into per-service pull/run/recreate plan | full Compose parity | ask for compose file and produce conservative plan |

## Rule

When a Docker flag is not mapped with confidence, preserve it in `unsupported_or_uncertain` and do not silently drop it from the explanation.
