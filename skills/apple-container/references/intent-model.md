# Intent Model

Use this model before producing commands. Confirmation means the agent should ask unless the user already gave a narrow, explicit instruction.

| Intent | Natural language examples | Docker-style examples | Required information | Safe default | Confirmation |
| --- | --- | --- | --- | --- | --- |
| `install_container` | "install Apple container", "set up container CLI" | n/a | user explicitly requested install | run installation checks, official signed package install, then verify | no extra confirmation if explicit; ask before upgrade/reinstall |
| `system_status` | "is container running?", "check Apple container" | n/a | none | run help/status checks | no |
| `run_container` | "run redis", "start postgres with password pass" | `docker run redis` | image, optional name/env/ports/mounts/command | verify `container run --help`, then run only supported flags | no, unless replacing existing state |
| `list_containers` | "show containers" | `docker ps`, `docker ps -a` | include stopped? | list containers with supported command | no |
| `list_images` | "show images" | `docker images` | none | list images | no |
| `pull_image` | "pull redis" | `docker pull redis` | image tag | pull exact image | usually no |
| `view_logs` | "show app logs", "follow logs" | `docker logs app`, `docker logs -f app` | container name/id | show logs; verify follow support before follow flag | no |
| `exec_command` | "run ls in app" | `docker exec app ls` | container, command | exec exact command | usually no |
| `exec_shell` | "enter redis" | `docker exec -it redis sh` | container, shell | exec shell if available | usually no |
| `stop_container` | "stop app" | `docker stop app` | container name/id | stop the named container | no if target is explicit; yes for broad targets |
| `restart_container` | "restart app" | `docker restart app` | container name/id | stop/start or restart if supported | no if target is explicit |
| `delete_container` | "remove app" | `docker rm app` | container name/id | explain data risk, ask if ambiguous | yes |
| `delete_image` | "remove redis image" | `docker rmi redis` | image tag/id | ask before delete | yes |
| `cleanup` | "clean unused containers" | `docker system prune` | scope | produce plan first | yes |
| `configuration_change` | "change app port to 8080" | recreate-style Docker commands | target, change, current config | inspect and produce recreate plan | yes if destructive/stateful |
| `debug_failure` | "app will not start" | n/a | target or failing command | read-only diagnostics first | no |
| `docker_translation` | "translate docker run ..." | any Docker command | input command | output intent and tentative workflow | no |
| `compose_like_service` | "run app and db like compose" | `docker compose up` | service definitions | decompose into service plan | yes before creating multiple services |

## Missing Information

If required information is missing and cannot be inferred safely, ask one concise question. Prefer safe inspection before asking when the target can be discovered without side effects.
