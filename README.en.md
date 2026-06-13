# Apple Container Operator

<p align="center">
  English | <a href="./README.md">简体中文</a>
</p>

Apple Container Operator is a vendor-neutral AI agent skill pack for operating Apple's native `container` runtime from natural language, Docker-style workflows, and runtime configuration requests.

It helps agents identify container intent, check local `container` capabilities, translate conservative Docker-style commands, plan lifecycle operations, and apply safety rules before destructive actions.

## What It Supports

- Natural language operations such as running, stopping, inspecting, and debugging containers.
- Docker-style command translation as an intent language.
- Local container and image lifecycle management.
- Guided Apple container installation from the official signed installer package.
- Configuration change planning for ports, env vars, volumes, commands, names, working directories, and image tags.
- Troubleshooting workflows for common runtime, image, command, network, and mount issues.
- Safety rules for destructive or multi-target operations.

## Setup

### Install This Skill Pack

Send this prompt to your AI coding agent:

```text
Install the Apple Container Operator skill pack from https://github.com/lizhelang/apple-container-operator.

Clone the repository, inspect its README and skills/apple-container/SKILL.md, then install or reference the apple-container skill in your local agent skill/rules system so future requests about Apple container use this skill automatically. Keep it vendor-neutral and do not convert it into an OpenAI-only plugin.
```

### Install Apple Container

Send this prompt after the skill pack is available:

```text
Use the apple-container skill to install Apple's native container runtime on this Mac.

Follow the skill's installation workflow: verify this is an Apple silicon Mac, check the macOS version, download the latest official signed installer package from apple/container GitHub Releases, install it with the macOS installer, run container --version, start the system service with container system start, and verify the result. Do not install Docker Desktop as a substitute.
```

### Install Skill Pack And Apple Container Together

Send this prompt to do both in one pass:

```text
Set up Apple Container Operator end to end.

First install the Apple Container Operator skill pack from https://github.com/lizhelang/apple-container-operator into your local agent skill/rules system. Then use that skill to install Apple's native container runtime on this Mac from the official apple/container GitHub Releases signed installer package. Verify Apple silicon and macOS support, install the package, run container --version, start container system service, and report the final status. Keep the workflow vendor-neutral and do not install Docker Desktop as a substitute.
```

### Migrate Docker Services To Apple Container

Send this prompt to migrate existing Docker-based services:

```text
Use Apple Container Operator to inspect my Docker-based service setup, identify images, ports, env vars, volumes, commands, dependencies, and stateful data, then create and execute a safe migration plan to Apple's native container runtime without assuming full Docker or Compose parity.
```

## Installation And Usage

### Generic AI Agents

Copy or reference `skills/apple-container/SKILL.md` in your agent's skill, rule, or instruction system. The skill routes detailed behavior to `skills/apple-container/references/` and deterministic helpers in `skills/apple-container/scripts/`.

Agents should run:

```sh
skills/apple-container/scripts/detect-container.sh
skills/apple-container/scripts/install-container.sh
skills/apple-container/scripts/inspect-state.sh
```

before assuming local support for commands or flags.

### Codex Via AGENTS.md

Use the root `AGENTS.md` as repository guidance. When operating Apple container for a user, load `skills/apple-container/SKILL.md`, consult the relevant reference file, and verify local CLI support with `container --help` or subcommand help before using uncertain flags.

### Claude Via CLAUDE.md

Point Claude Code at `agents/CLAUDE.md`. It summarizes the portable behavior and directs Claude to the skill and references without relying on Codex-specific APIs.

### Cursor Via Rules File

Use `agents/cursor-rules.md` as Cursor project rules. Keep command mappings conservative and test any changes to Docker-style translation.

## Examples

User: "run postgres with password pass and expose it locally"

Agent behavior: identify `run_container`, check `container run --help`, plan env and port settings, warn about database persistence, then produce a conservative `container run` command only with verified flags.

User: `docker ps`

Agent behavior: treat this as `list_containers`, translate to the nearest Apple container list command, and verify exact list syntax with help if uncertain.

User: `docker logs -f app`

Agent behavior: treat this as `view_logs`, use Apple container logs if available, and verify whether follow mode is supported before adding a follow flag.

User: "change app port from 3000 to 8080"

Agent behavior: treat this as `configuration_change`, inspect current settings if possible, then generate a stop/recreate plan that preserves the image, env, mounts, command, and name as much as possible.

User: "this container will not start, debug it"

Agent behavior: follow the troubleshooting sequence: check system, image, container status, logs, command/configuration, ports, mounts, then suggest a minimal reproduction.

User: "install Apple container for me"

Agent behavior: verify Apple silicon and macOS support, download the latest signed installer package from the official `apple/container` GitHub release, run the macOS installer, then start and verify the system service.

## Compatibility Disclaimer

Apple container is not Docker. Docker-style commands are interpreted as intent, not as proof of flag or workflow parity. Agents and maintainers should check the local `container` CLI help and version before assuming flag support.
